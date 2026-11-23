"""Preview workaround for named OneLake role membership without Graph."""

from __future__ import annotations

import json
from uuid import uuid4
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener
from uuid import UUID

from fabricops_kit.access_scanner.shared import (
    ACCESS_TABLE,
    FABRIC_API_ROOT,
    catalogue_tables,
    persist_access_rows,
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
    """Reconcile all identity sources before projecting any access surface."""
    identities = {}

    def observe(object_id, name=None, email=None, principal_type=None):
        if not isinstance(object_id, str) or not object_id.strip():
            coverage.append({"source": "IDENTITY", "status": "PRINCIPAL_ID_MISSING"})
            return
        key = object_id.casefold()
        identity = identities.setdefault(key, {"principal_object_id": object_id, "principal_type": "UNKNOWN"})
        for field, value in (("display_name", name), ("email", email)):
            if isinstance(value, str) and value.strip():
                identity[field] = value.strip()
        kind = normalise_principal_type(principal_type)
        prior = identity["principal_type"]
        if kind != "UNKNOWN":
            if prior not in {"UNKNOWN", kind}:
                identity["type_conflict"] = True
                coverage.append(
                    {"source": "IDENTITY", "status": "CONFLICTING_PRINCIPAL_TYPES", "principal_object_id": object_id}
                )
            identity["principal_type"] = "UNKNOWN" if identity.get("type_conflict") else kind

    for detail in item_access.get("detail", []):
        observe(detail.get("objectId"), detail.get("givenName"), detail.get("emailAddress"))
    for assignment in assignments:
        principal = assignment.get("principal")
        if not isinstance(principal, dict):
            coverage.append({"source": "WORKSPACE", "status": "INVALID_PRINCIPAL"})
            continue
        observe(
            principal.get("id"),
            principal.get("displayName"),
            (principal.get("userDetails") or {}).get("userPrincipalName"),
            principal.get("type"),
        )
    for role in roles:
        for member in (role.get("members") or {}).get("microsoftEntraMembers") or []:
            observe(
                member.get("objectId"),
                member.get("displayName"),
                member.get("userPrincipalName"),
                member.get("objectType"),
            )

    def identity(object_id):
        return identities.get(str(object_id or "").casefold(), {})

    item_rows = [
        {
            **identity(detail.get("objectId")),
            "permission_source": "ITEM_ACCESS",
            "permissions_raw": detail.get("permissions"),
            "artifact_permissions_raw": detail.get("artifactPermissions"),
            "access_source_json": json.dumps(detail.get("accessSource"), sort_keys=True),
        }
        for detail in item_access.get("detail", [])
        if identity(detail.get("objectId"))
    ]
    workspace_rows = [
        {
            **identity(assignment["principal"].get("id")),
            "permission_source": "WORKSPACE_ROLE",
            "role_name": assignment.get("role"),
        }
        for assignment in assignments
        if isinstance(assignment.get("principal"), dict) and identity(assignment["principal"].get("id"))
    ]
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
            if identity(member.get("objectId")):
                role_rows.append(
                    {
                        **common,
                        **identity(member.get("objectId")),
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
        if set(members) - {"microsoftEntraMembers", "fabricItemMembers"} or not explicit and not automatic:
            coverage.append({"source": "ONELAKE_ROLE", "status": "REVIEW_RAW_MEMBERS", "role_name": role.get("name")})

    name_ids = {}
    for key, value in identities.items():
        if value.get("display_name"):
            name_ids.setdefault(value["display_name"].casefold(), set()).add(key)
    users = []
    for row in workspace_rows + item_rows + role_rows:
        if row.get("membership_kind") == "AUTOMATIC":
            continue
        object_id = str(row.get("principal_object_id") or "").casefold()
        kind = row.get("principal_type", "UNKNOWN")
        if row.get("type_conflict"):
            continue
        if kind == "USER":
            users.append(
                {
                    **row,
                    "user_principal": row.get("email") or row["principal_object_id"],
                    "user_type": "USER",
                    "identity_source": "API",
                }
            )
            continue
        name = str(row.get("display_name") or "").casefold()
        key = object_id if object_id in supplied else None
        if key is None and name in supplied:
            if len(name_ids.get(name, set())) == 1:
                key = name
            else:
                coverage.append(
                    {"source": "IDENTITY", "status": "AMBIGUOUS_GROUP_NAME", "principal_object_id": object_id}
                )
        if key is not None and kind in {"GROUP", "UNKNOWN"}:
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
            status = (
                "GROUP_MEMBERSHIP_UNRESOLVED"
                if kind == "GROUP"
                else "PRINCIPAL_TYPE_UNRESOLVED"
                if kind == "UNKNOWN"
                else "NON_USER_PRINCIPAL"
            )
            coverage.append({"source": "IDENTITY", "status": status, "principal_object_id": object_id})
    return role_rows, workspace_rows, item_rows, users


def _permission_observations(rows):
    """Flatten observed permissions without interpreting undocumented bitmasks."""
    result = []
    for row in rows:
        automatic = row.get("membership_kind") == "AUTOMATIC"
        principal = (
            row.get("user_principal")
            or (row.get("email") if row.get("principal_type") == "USER" else None)
            or row.get("principal_object_id")
        )
        if automatic:
            principal = "fabric-item:" + row["member_json"]
        if not principal:
            continue
        supplied = row.get("identity_source") == "CALLER_SUPPLIED_GROUP_MEMBERSHIP"
        common = {
            "user_principal": principal,
            "user_type": row.get("user_type")
            or ("FABRIC_ITEM_MEMBERS" if automatic else row.get("principal_type", "UNKNOWN")),
            "principal_object_id": None if supplied or automatic else row.get("principal_object_id"),
            "role_name": row.get("role_name"),
            "permission_source": row["permission_source"],
            "access_verification_status": "UNVERIFIED",
            "permission_details_json": json.dumps({**row, "permission_path": "*"}, sort_keys=True),
        }
        if row["permission_source"] != "ONELAKE_ROLE":
            # Item Read is a prerequisite, not a OneLake table data grant.
            value = (
                str(row.get("role_name") or "UNKNOWN").upper()
                if row["permission_source"] == "WORKSPACE_ROLE"
                else "UNDECODED_ITEM_PERMISSION"
            )
            result.append(
                {
                    **common,
                    "path": "*",
                    "access_value": value,
                    "access_state": "OBSERVED",
                    "access_level": row["permission_source"],
                }
            )
            continue
        for rule in json.loads(row["decision_rules_json"]):
            paths, actions = [], []
            for permission in rule.get("permission") or []:
                attribute = str(permission.get("attributeName") or "").casefold()
                values = permission.get("attributeValueIncludedIn") or []
                if attribute == "path":
                    paths.extend(values)
                elif attribute == "action":
                    actions.extend(values)
            for path in paths or [""]:
                for action in actions or ["UNKNOWN"]:
                    result.append(
                        {
                            **common,
                            "path": str(path),
                            "permission_details_json": json.dumps(
                                {**row, "permission_path": str(path), "decision_rule": rule}, sort_keys=True
                            ),
                            "access_value": str(action),
                            "access_state": str(rule.get("effect") or "UNKNOWN"),
                            "access_level": "ONELAKE_PATH",
                        }
                    )
    return result


def _metadata_access(catalogue_df, rows, *, target, workspace_id, item_id, persist, snapshot_id, context):
    """Map observations to canonical physical Catalogue identities and save snapshots."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    from fabricops_kit.config.audit import build_runtime_audit_fields
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    from fabricops_kit.config.shared import get_store, resolve_fabric_context

    config, scope_workspace_id, runtime = resolve_fabric_context(context=context)
    store = get_store(config, scope_workspace_id, target)
    if (
        str(store.kind).lower() != "lakehouse"
        or str(store.workspace_id).lower() != workspace_id
        or str(store.item_id).lower() != item_id
    ):
        raise ValueError("target must identify the scanned physical Lakehouse in the configured context.")
    registered = catalogue_tables(
        catalogue_df, config=config, workspace_id=scope_workspace_id, target_store_kinds={target: "lakehouse"}
    )
    fields = [
        "user_principal",
        "user_type",
        "principal_object_id",
        "role_name",
        "permission_source",
        "access_verification_status",
        "permission_details_json",
        "path",
        "access_value",
        "access_state",
        "access_level",
    ]
    observations = catalogue_df.sparkSession.createDataFrame(
        [tuple(row.get(name) for name in fields) for row in _permission_observations(rows)],
        T.StructType([T.StructField(name, T.StringType(), True) for name in fields]),
    )
    path = F.lower(F.regexp_replace(F.col("path"), r"^/+|/+$", ""))
    schema = F.coalesce(F.col("_catalogue_schema_name"), F.lit(""))
    table_path = F.lower(
        F.when(
            F.length(schema) > 0, F.concat_ws("/", F.lit("Tables"), schema, F.col("_catalogue_table_name"))
        ).otherwise(F.concat_ws("/", F.lit("Tables"), F.col("_catalogue_table_name")))
    )
    schema_path = F.lower(F.concat_ws("/", F.lit("Tables"), schema))
    mapped = observations.join(
        registered,
        path.isin("*", "tables", "tables/*")
        | (path == table_path)
        | ((F.length(schema) > 0) & ((path == schema_path) | (path == F.concat(schema_path, F.lit("/*"))))),
        "left",
    )
    unmatched = (
        mapped.where(F.col("_catalogue_table_id").isNull())
        .select(*fields)
        .withColumn("unmatched_reason", F.lit("path_not_a_registered_table"))
    )
    audit = build_runtime_audit_fields(config=config, active_workspace_id=scope_workspace_id, runtime_context=runtime)
    access = mapped.where(F.col("_catalogue_table_id").isNotNull()).select(
        *[F.col(name) for name in fields if name != "path"],
        F.col("_catalogue_table_id").alias("table_id"),
        F.col("_catalogue_table_name").alias("table_name"),
        F.col("_catalogue_workspace_id").alias("asset_workspace_id"),
        F.lit("TABLE").alias("asset_type"),
        F.lit(snapshot_id).alias("access_snapshot_id"),
        F.lit(item_id).alias("database_name"),
        F.col("_catalogue_schema_name").alias("schema_name"),
        F.col("_catalogue_table_name").alias("object_name"),
        F.lit("ONELAKE_TABLE").alias("object_type"),
        F.col("path"),
    )
    identity_fields = [
        "asset_workspace_id",
        "table_id",
        "user_principal",
        "access_level",
        "access_value",
        "access_state",
        "permission_source",
        "permission_details_json",
        "path",
    ]
    access = (
        access.withColumn(
            "access_id",
            F.sha2(
                F.to_json(
                    F.struct(F.lit(snapshot_id).alias("snapshot_id"), *[F.col(name) for name in identity_fields])
                ),
                256,
            ),
        )
        .drop("path")
        .dropDuplicates(["access_id"])
    )
    for name, value in audit.items():
        access = access.withColumn(name, F.lit(value))
    access = access.select(*metadata_table_schema_registry()[ACCESS_TABLE].fieldNames())
    persist_access_rows(
        access,
        config=config,
        workspace_id=scope_workspace_id,
        context=runtime,
        persist=persist,
        transaction_id=f"onelake-access:{workspace_id}:{item_id}:{snapshot_id}",
    )
    return access, unmatched


def scan_onelake_role_members(
    workspace_id: str,
    item_id: str,
    *,
    portal_base_url: str,
    group_memberships: dict[str, list[str]] | None = None,
    access_token: str | None = None,
    catalogue_df=None,
    target: str | None = None,
    persist: bool = False,
    access_snapshot_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Inspect named OneLake role assignments using a Preview portal workaround.

    This is an unstable inventory workaround, not a supported Microsoft API
    integration or an effective-access verifier. It joins public OneLake roles
    and Workspace assignments to names returned by the undocumented Power BI
    portal item-access endpoint. No Graph or tenant-admin API is called.
    Inspection requires no FabricOps setup or Spark. Optional Catalogue mapping
    writes observed permission snapshots through the configured Metadata Lakehouse.

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

    catalogue_df : pyspark.sql.DataFrame, optional
        Active METADATA_DATA_CATALOGUE rows. Required for mapping or persistence.
    target : str, optional
        Configured Lakehouse store key. Must match workspace_id and item_id.
    persist : bool, default=False
        Write mapped observations to METADATA_DATA_ACCESS. Requires Catalogue,
        target, configured Metadata Lakehouse, metadata write permission, and
        setup_metadata_tables() after upgrading the package. Permissions remain unchanged.
    access_snapshot_id : str, optional
        Snapshot identity, generated when omitted. Reuse only to retry the same
        immutable observation set; writes use a transaction identity to avoid duplication.
    context : dict[str, Any], optional
        FabricOps configured metadata routing and notebook audit context.

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
        missing rows do not establish absence of access. With catalogue_df,
        access and unmatched are Spark DataFrames; otherwise both are None.
        access_snapshot_id identifies the scan. persist=True saves mapped rows
        including unresolved groups/selectors and supplied users, with original
        rules and assignment provenance in permission_details_json. Every saved
        row is UNVERIFIED effective access. Item bitmasks are stored as observations,
        never converted into table data grants. No permissions are changed.

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
    >>> saved = scan_onelake_role_members(
    ...     workspace_id, lakehouse_id, portal_base_url=portal_origin,
    ...     group_memberships={"Data Readers": ["alice@example.com"]},
    ...     catalogue_df=catalogue_df, target="Silver", persist=True,
    ... )
    >>> display(saved["access"])
    >>> display(saved["unmatched"])

    """
    try:
        workspace_id, item_id = str(UUID(workspace_id)), str(UUID(item_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("workspace_id and item_id must be UUID strings.") from exc
    if not isinstance(portal_base_url, str) or not re.fullmatch(
        r"https://wabi-[a-z0-9-]+\.analysis\.windows\.net/?", portal_base_url
    ):
        raise ValueError("portal_base_url must be an HTTPS wabi-*.analysis.windows.net origin only.")
    if not isinstance(persist, bool):
        raise ValueError("persist must be a boolean.")
    if (persist or catalogue_df is not None) and (
        catalogue_df is None or not isinstance(target, str) or not target.strip()
    ):
        raise ValueError("Catalogue mapping and persistence require catalogue_df and a configured target key.")
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
    access = unmatched = None
    snapshot_id = str(access_snapshot_id or uuid4())
    if catalogue_df is not None:
        observations = (
            workspace_rows
            + item_rows
            + role_rows
            + [row for row in users if row["identity_source"] == "CALLER_SUPPLIED_GROUP_MEMBERSHIP"]
        )
        access, unmatched = _metadata_access(
            catalogue_df,
            observations,
            target=target,
            workspace_id=workspace_id,
            item_id=item_id,
            persist=persist,
            snapshot_id=snapshot_id,
            context=context,
        )
    return {
        "access": access,
        "unmatched": unmatched,
        "access_snapshot_id": snapshot_id,
        "role_members": role_rows,
        "workspace_assignments": workspace_rows,
        "item_access": item_rows,
        "users": users,
        "coverage": coverage,
        "raw_roles": roles,
        "raw_workspace_assignments": assignments,
        "raw_item_access": item_access,
    }
