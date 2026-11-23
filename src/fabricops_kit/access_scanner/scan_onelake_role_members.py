"""Preview workaround for named OneLake role membership without Graph."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener
from uuid import UUID

from fabricops_kit.access_scanner.shared import (
    FABRIC_API_ROOT,
    PortalNoRedirect,
    fabric_access_token,
    normalise_principal_type,
    request_fabric_json,
)


def _portal_access(url: str, token: str) -> dict[str, Any]:
    """Read the observed portal resource without forwarding bearer redirects."""
    request = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with build_opener(PortalNoRedirect()).open(request, timeout=60) as response:
            data = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Portal item-access request failed with HTTP {exc.code}.") from None
    except URLError:
        raise RuntimeError("Portal item-access request failed; check network access.") from None
    if not isinstance(data, dict) or not isinstance(data.get("detail"), list):
        raise RuntimeError("Portal item-access response changed: expected a detail list.")
    if any(not isinstance(row, dict) for row in data["detail"]):
        raise RuntimeError("Portal item-access detail contains a non-object entry.")
    return data


def _collection(url: str, token: str) -> list[dict[str, Any]]:
    """Follow continuation tokens while retaining the original resource URL."""
    rows = []
    seen = set()
    next_url = url
    while True:
        payload = request_fabric_json(next_url, access_token=token)
        values = payload.get("value")
        if not isinstance(values, list) or any(not isinstance(row, dict) for row in values):
            raise RuntimeError("Fabric response changed: expected a list of objects in value.")
        rows.extend(values)
        continuation = payload.get("continuationToken")
        if not continuation:
            if payload.get("continuationUri"):
                raise RuntimeError("Pagination supplied a URI without a continuation token; scan is incomplete.")
            return rows
        if not isinstance(continuation, str) or continuation in seen:
            raise RuntimeError("Invalid or repeated Fabric continuation token.")
        seen.add(continuation)
        next_url = url + "?" + urlencode({"continuationToken": continuation})


def _memberships(value: dict[str, list[str]] | None) -> dict[str, list[str]]:
    """Validate an explicit caller-supplied group-to-user snapshot."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("group_memberships must be a dictionary of group names/IDs to lists of user UPNs.")
    result = {}
    for group, users in value.items():
        if not isinstance(group, str) or not group.strip() or group.strip().casefold() in result:
            raise ValueError("Group keys must be non-empty and unique ignoring case and whitespace.")
        if not isinstance(users, list) or any(not isinstance(user, str) or not user.strip() for user in users):
            raise ValueError("Each group must map to a list of non-empty user UPN strings.")
        result[group.strip().casefold()] = list(dict.fromkeys(user.strip().casefold() for user in users))
    return result


def _resolve_members(assignments, item_access, roles, supplied, coverage):
    """Join identity observations and expand only explicitly supplied memberships."""
    identities = {}
    for detail in item_access.get("detail", []):
        key = str(detail.get("objectId") or "").casefold()
        if key:
            identities[key] = {
                "principal_object_id": detail["objectId"],
                "display_name": detail.get("givenName"),
                "email": detail.get("emailAddress"),
                "principal_type": "UNKNOWN",
            }
    item_rows = []
    for detail in item_access.get("detail", []):
        identity = identities.get(str(detail.get("objectId") or "").casefold(), {})
        item_rows.append(
            {
                **identity,
                "permission_source": "ITEM_ACCESS",
                "permissions_raw": detail.get("permissions"),
                "artifact_permissions_raw": detail.get("artifactPermissions"),
                "access_source_json": json.dumps(detail.get("accessSource"), sort_keys=True),
            }
        )
    workspace_rows = []
    for assignment in assignments:
        principal = assignment.get("principal") or {}
        object_id = principal.get("id")
        if not object_id:
            coverage.append({"source": "WORKSPACE", "status": "PRINCIPAL_ID_MISSING"})
            continue
        key = str(object_id).casefold()
        prior = identities.get(key, {})
        identity = {
            "principal_object_id": object_id,
            "display_name": principal.get("displayName") or prior.get("display_name"),
            "email": (principal.get("userDetails") or {}).get("userPrincipalName") or prior.get("email"),
            "principal_type": normalise_principal_type(principal.get("type")),
        }
        identities[key] = identity
        workspace_rows.append({**identity, "permission_source": "WORKSPACE_ROLE", "role_name": assignment.get("role")})

    # Reconcile source types after Workspace identities have been read.
    item_rows = [
        {**row, **identities.get(str(row.get("principal_object_id") or "").casefold(), {})} for row in item_rows
    ]
    name_ids = {}
    for key, identity in identities.items():
        if identity.get("display_name"):
            name_ids.setdefault(identity["display_name"].casefold(), set()).add(key)

    role_rows = []
    for role in roles:
        common = {
            "permission_source": "ONELAKE_ROLE",
            "role_name": role.get("name"),
            "role_id": role.get("id"),
            "decision_rules_json": json.dumps(role.get("decisionRules") or [], sort_keys=True),
        }
        members = role.get("members") or {}
        explicit = members.get("microsoftEntraMembers") or []
        automatic = members.get("fabricItemMembers") or []
        for member in explicit:
            object_id = member.get("objectId")
            key = str(object_id or "").casefold()
            identity = identities.get(key, {})
            role_rows.append(
                {
                    **common,
                    "principal_object_id": object_id,
                    "display_name": identity.get("display_name") or member.get("displayName"),
                    "email": identity.get("email") or member.get("userPrincipalName"),
                    "principal_type": (
                        identity["principal_type"]
                        if identity.get("principal_type", "UNKNOWN") != "UNKNOWN"
                        else normalise_principal_type(member.get("objectType"))
                    ),
                    "membership_kind": "EXPLICIT",
                    "member_json": json.dumps(member, sort_keys=True),
                }
            )
        for selector in automatic:
            role_rows.append(
                {**common, "membership_kind": "AUTOMATIC", "member_json": json.dumps(selector, sort_keys=True)}
            )
            coverage.append(
                {"source": "ONELAKE_ROLE", "status": "AUTOMATIC_MEMBERSHIP_UNRESOLVED", "role_name": role.get("name")}
            )
        unknown_keys = set(members) - {"microsoftEntraMembers", "fabricItemMembers"}
        if unknown_keys or not explicit and not automatic:
            coverage.append({"source": "ONELAKE_ROLE", "status": "REVIEW_RAW_MEMBERS", "role_name": role.get("name")})

    for row in role_rows:
        if row.get("principal_object_id") and row.get("display_name"):
            name_ids.setdefault(row["display_name"].casefold(), set()).add(str(row["principal_object_id"]).casefold())

    users = []
    for row in workspace_rows + item_rows + role_rows:
        if row.get("membership_kind") == "AUTOMATIC":
            continue
        object_id = str(row.get("principal_object_id") or "").casefold()
        name = str(row.get("display_name") or "").casefold()
        principal_type = row.get("principal_type", "UNKNOWN")
        if principal_type == "USER":
            users.append(
                {
                    **row,
                    "user_principal": row.get("email") or row.get("principal_object_id"),
                    "user_type": "USER",
                    "identity_source": "API",
                }
            )
            continue
        key = object_id if object_id and object_id in supplied else None
        if key is None and name in supplied:
            if len(name_ids.get(name, set())) == 1:
                key = name
            else:
                coverage.append(
                    {"source": "IDENTITY", "status": "AMBIGUOUS_GROUP_NAME", "principal_object_id": object_id}
                )
        if key is not None and principal_type in {"GROUP", "UNKNOWN"}:
            for user in supplied[key]:
                users.append(
                    {
                        **row,
                        "user_principal": user,
                        "user_type": "USER",
                        "identity_source": "CALLER_SUPPLIED_GROUP_MEMBERSHIP",
                        "group_mapping_key": key,
                    }
                )
            coverage.append(
                {
                    "source": "IDENTITY",
                    "status": "CALLER_SUPPLIED_MEMBERSHIP_UNVERIFIED",
                    "principal_object_id": object_id,
                }
            )
        else:
            coverage.append(
                {
                    "source": "IDENTITY",
                    "status": "GROUP_MEMBERSHIP_UNRESOLVED"
                    if principal_type == "GROUP"
                    else "PRINCIPAL_TYPE_UNRESOLVED",
                    "principal_object_id": object_id,
                }
            )
    return role_rows, workspace_rows, item_rows, users


def scan_onelake_role_members(
    workspace_id: str,
    item_id: str,
    *,
    portal_base_url: str,
    group_memberships: dict[str, list[str]] | None = None,
    access_token: str | None = None,
) -> dict[str, Any]:
    """Inspect named OneLake role assignments using a Preview portal workaround.

    This is an unstable, read-only workaround, not a supported Microsoft API
    integration or an effective-access verifier. It joins public OneLake roles
    and Workspace assignments to names returned by the undocumented Power BI
    portal item-access endpoint. No Graph or tenant-admin API is called.
    No FabricOps setup, Catalogue, Spark session, or metadata persistence is needed.

    Parameters
    ----------
    workspace_id : str
        Physical workspace UUID containing the Lakehouse.
    item_id : str
        Lakehouse item UUID, not its SQL endpoint UUID.
    portal_base_url : str
        HTTPS wabi-*.analysis.windows.net origin observed in the portal Network
        panel. No tenant-specific host is inferred or built into the package.
        Redirects are refused; obtain the current origin if the portal moves.
    group_memberships : dict[str, list[str]], optional
        Group object ID or exact display name mapped to user UPN strings, for
        example {"Data Readers": ["alice@example.com", "bob@example.com"]}.
        IDs take precedence over names. Ambiguous names are not expanded.
        Values are caller-supplied direct membership, not directory-verified.
        An UNKNOWN principal with a matching key is a caller-declared group.
        Nested groups are not expanded; provide their final user membership.
        An empty list means no users supplied, not a verified empty group.
    access_token : str, optional
        Current caller token; otherwise NotebookUtils getToken("pbi") is used.
        Never paste a browser bearer token into a shared notebook.

    Returns
    -------
    dict[str, Any]
        Python records: role_members, workspace_assignments, item_access, users, coverage,
        raw_roles, raw_workspace_assignments, and raw_item_access. The users
        records retain the originating principal fields; user_principal names
        the resolved user and identity_source distinguishes API users from
        supplied membership. Email and principal type can remain unknown.
        Rule JSON retains paths, actions, and restrictions unchanged. Automatic
        membership stays a selector, not a list of users. Portal permission
        bitmasks stay raw and are never interpreted. Always inspect coverage;
        missing rows do not establish absence of access. No tables are written,
        including METADATA_DATA_ACCESS, and no permissions are changed.

    Raises
    ------
    ValueError
        If UUIDs, the portal origin, or membership mappings are invalid.
    RuntimeError
        If authentication or the primary OneLake role read fails. Workspace
        and portal failures instead appear in coverage with available role
        observations retained; partial source pages are discarded on failure.

    Notes
    -----
    Workspace assignment listing requires Member or Admin plus Workspace API
    scope; Contributor is insufficient. OneLake role listing documents item
    Read permission plus OneLake API scope. The undocumented portal endpoint's
    minimum rights and stability are unverified: a successful caller test does
    not establish support for all Members. Notebook and Environment access are
    separate prerequisites. Scheduled/service-principal execution is untested.
    Public API permission references:
    https://learn.microsoft.com/rest/api/fabric/core/workspaces/list-workspace-role-assignments
    and https://learn.microsoft.com/rest/api/fabric/core/onelake-data-access-security/list-data-access-roles.
    Group expansion describes supplied assignments, not confirmed effective
    access. The current caller token never grants additional permissions.

    Examples
    --------
    >>> result = scan_onelake_role_members(
    ...     workspace_id, lakehouse_id, portal_base_url=portal_origin,
    ...     group_memberships={"Data Readers": ["alice@example.com"]},
    ... )
    >>> import pandas as pd
    >>> display(pd.DataFrame(result["role_members"]))
    >>> display(pd.DataFrame(result["users"]))
    >>> display(pd.DataFrame(result["coverage"]))

    """
    try:
        workspace_id, item_id = str(UUID(workspace_id)), str(UUID(item_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("workspace_id and item_id must be UUID strings.") from exc
    if not isinstance(portal_base_url, str) or not re.fullmatch(
        r"https://wabi-[a-z0-9-]+\.analysis\.windows\.net/?", portal_base_url
    ):
        raise ValueError("portal_base_url must be an HTTPS wabi-*.analysis.windows.net origin only.")
    supplied = _memberships(group_memberships)
    token = fabric_access_token(access_token)
    roles = _collection(f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/items/{item_id}/dataAccessRoles", token)
    for role in roles:
        members = role.get("members") or {}
        if not isinstance(members, dict):
            raise RuntimeError("OneLake role response changed: members must be an object.")
        for field in ("microsoftEntraMembers", "fabricItemMembers"):
            values = members.get(field) or []
            if not isinstance(values, list) or any(not isinstance(member, dict) for member in values):
                raise RuntimeError("OneLake role response changed: member collections must contain objects.")
    coverage = [{"source": "PORTAL_ITEM_ACCESS", "status": "UNDOCUMENTED_UNSTABLE_WORKAROUND"}]
    try:
        assignments = _collection(f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/roleAssignments", token)
        coverage.append({"source": "WORKSPACE", "status": "READ_SUCCEEDED"})
    except (RuntimeError, ValueError, OSError):
        assignments = []
        coverage.append(
            {
                "source": "WORKSPACE",
                "status": "UNAVAILABLE",
                "detail": "Check Member/Admin access and token scopes; workspace assignments were not read.",
            }
        )
    try:
        item_access = _portal_access(f"{portal_base_url.rstrip('/')}/metadata/access/artifacts/{item_id}", token)
        coverage.append({"source": "PORTAL_ITEM_ACCESS", "status": "READ_SUCCEEDED"})
    except (RuntimeError, ValueError, OSError):
        item_access = {}
        coverage.append(
            {
                "source": "PORTAL_ITEM_ACCESS",
                "status": "UNAVAILABLE",
                "detail": "Check caller permissions, portal origin, or response shape; names may remain unresolved.",
            }
        )
    role_rows, workspace_rows, item_rows, users = _resolve_members(assignments, item_access, roles, supplied, coverage)
    return {
        "role_members": role_rows,
        "workspace_assignments": workspace_rows,
        "item_access": item_rows,
        "users": users,
        "coverage": coverage,
        "raw_roles": roles,
        "raw_workspace_assignments": assignments,
        "raw_item_access": item_access,
    }
