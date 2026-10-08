"""Owner file for the discovery-first effective Fabric access scanner."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any, Iterable

from fabricops_kit.access_scanner.scan_sql_access import SQL_ACCESS_QUERY
from fabricops_kit.access_scanner.shared import (
    FABRIC_API_ROOT,
    fabric_access_token,
    list_fabric_pages,
    normalise_principal_type,
    onelake_role_observations,
    read_discovered_sql_endpoint_query,
    search_fabric_catalog,
    workspace_role_observations,
)


SQL_TABLE_QUERY = """
SELECT
    s.name AS schema_name,
    o.name AS table_name,
    o.type_desc AS object_type
FROM sys.objects AS o
INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE o.type IN ('U', 'V')
""".strip()

IDENTITY_COLUMNS = {
    "object_id",
    "display_name",
    "user_principal_name",
    "principal_type",
    "group_type",
}
MEMBERSHIP_COLUMNS = {"group_object_id", "member_object_id"}
SUPPORTED_ITEM_TYPES = {"LAKEHOUSE", "WAREHOUSE"}
SECURITY_GROUP_TYPES = {"SECURITYGROUP", "SECURITY_GROUP", "SECURITY"}
ELEVATED_WORKSPACE_ROLES = {"ADMIN", "MEMBER", "CONTRIBUTOR"}
ACCESS_CONFIRMED = "CONFIRMED"
ACCESS_UNVERIFIED = "UNVERIFIED"
ACCESS_NOT_EFFECTIVE = "NOT_EFFECTIVE"
SQL_MODE_DELEGATED = "DELEGATED_IDENTITY"
SQL_MODE_USER = "USER_IDENTITY"
SQL_MODE_UNVERIFIED = "UNVERIFIED"


def _text(value: Any) -> str:
    """Return a stable stripped string for an optional source value."""
    return str(value or "").strip()


def _coverage(
    reason_code: str,
    detail: str,
    *,
    status: str = "INCOMPLETE",
    scope_type: str = "SCAN",
    access_surface: str = "",
    workspace_id: str = "",
    workspace_name: str = "",
    item_id: str = "",
    item_name: str = "",
    principal_object_id: str = "",
) -> dict[str, str]:
    """Build one normalized coverage row."""
    return {
        "status": status,
        "reason_code": reason_code,
        "scope_type": scope_type,
        "access_surface": access_surface,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "item_id": item_id,
        "item_name": item_name,
        "principal_object_id": principal_object_id,
        "detail": detail,
    }


def _table_identity(
    *, workspace_id: str, item_id: str, schema_name: str, table_name: str
) -> str:
    """Return a stable physical identity for a discovered Fabric table."""
    return "/".join((workspace_id, item_id, schema_name or "", table_name))


def _table_row(
    *,
    workspace: dict[str, Any],
    item: dict[str, Any],
    schema_name: str,
    table_name: str,
    table_path: str,
    object_type: str,
) -> dict[str, str]:
    """Build a normalized discovered table row."""
    workspace_id = _text(workspace.get("id"))
    item_id = _text(item.get("id"))
    return {
        "table_id": _table_identity(
            workspace_id=workspace_id,
            item_id=item_id,
            schema_name=schema_name,
            table_name=table_name,
        ),
        "workspace_id": workspace_id,
        "workspace_name": _text(workspace.get("displayName")),
        "item_id": item_id,
        "item_name": _text(item.get("displayName")),
        "item_type": _text(item.get("type")).upper(),
        "schema_name": schema_name,
        "table_name": table_name,
        "table_path": table_path,
        "object_type": object_type,
    }


def _lakehouse_tables(
    *,
    workspace: dict[str, Any],
    item: dict[str, Any],
    access_token: str,
) -> list[dict[str, str]]:
    """Discover non-schema Lakehouse tables through the existing Fabric pager."""
    workspace_id = _text(workspace.get("id"))
    item_id = _text(item.get("id"))
    values = list_fabric_pages(
        f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/lakehouses/{item_id}/tables",
        access_token=access_token,
        collection_key="data",
    )
    rows = []
    for value in values:
        name = _text(value.get("name"))
        location = _text(value.get("location"))
        if not name:
            continue
        relative = location.replace("\\", "/").split("/Tables/", 1)[-1]
        segments = [segment for segment in relative.split("/") if segment]
        schema_name = segments[-2] if len(segments) > 1 else ""
        rows.append(
            _table_row(
                workspace=workspace,
                item=item,
                schema_name=schema_name,
                table_name=name,
                table_path=(f"Tables/{schema_name}/{name}" if schema_name else f"Tables/{name}"),
                object_type=_text(value.get("type")) or "TABLE",
            )
        )
    return rows


def _sql_endpoint_rows(frame) -> list[dict[str, Any]]:
    """Materialize one small SQL catalogue result as dictionaries."""
    return [row.asDict(recursive=True) for row in frame.toLocalIterator()]


def _sql_tables(
    spark,
    *,
    workspace: dict[str, Any],
    item: dict[str, Any],
) -> list[dict[str, str]]:
    """Discover Warehouse or schema-enabled Lakehouse tables through SQL."""
    item_kind = _text(item.get("type")).lower()
    frame = read_discovered_sql_endpoint_query(
        spark,
        workspace_id=_text(workspace.get("id")),
        item_id=_text(item.get("id")),
        item_kind=item_kind,
        database_name=_text(item.get("displayName")),
        query=SQL_TABLE_QUERY,
    )
    rows = []
    for value in _sql_endpoint_rows(frame):
        schema_name = _text(value.get("schema_name"))
        table_name = _text(value.get("table_name"))
        if not table_name:
            continue
        rows.append(
            _table_row(
                workspace=workspace,
                item=item,
                schema_name=schema_name,
                table_name=table_name,
                table_path=(f"Tables/{schema_name}/{table_name}" if schema_name else f"Tables/{table_name}"),
                object_type=_text(value.get("object_type")) or "TABLE",
            )
        )
    return rows


def _permissions(value: str, *, surface: str) -> list[str]:
    """Map a source permission to normalized read/write capabilities."""
    normalized = _text(value).upper().replace(" ", "_")
    if surface == "SQL":
        result = []
        if normalized in {"SELECT", "CONTROL"}:
            result.append("READ")
        if normalized in {"INSERT", "UPDATE", "DELETE", "ALTER", "CONTROL"}:
            result.append("WRITE")
        return result
    if normalized in {"READWRITE", "READ_WRITE"}:
        return ["READ", "WRITE"]
    if normalized in {"READ", "READALL", "READ_DATA"}:
        return ["READ"]
    return []


def _grant_id(parts: Iterable[Any]) -> str:
    """Return a deterministic identifier for one observed grant."""
    source = "\u001f".join(_text(part) for part in parts)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _grant(
    table: dict[str, str],
    *,
    principal_id: str,
    principal_type: str,
    principal_name: str,
    access_surface: str,
    access_value: str,
    access_state: str,
    permission_source: str,
    role_name: str = "",
    scope_type: str = "",
    scope_value: str = "",
    restrictions_json: str = "{}",
    access_channels: list[str] | None = None,
    access_verification_status: str = ACCESS_UNVERIFIED,
    item_access_source: str = "",
    item_access_permissions: list[str] | None = None,
    data_access_source: str = "",
    sql_access_mode: str = "",
) -> dict[str, Any]:
    """Build one normalized table-level grant observation."""
    permissions = _permissions(access_value, surface=access_surface)
    row = {
        **table,
        "principal_object_id": principal_id,
        "principal_type": normalise_principal_type(principal_type),
        "principal_name": principal_name,
        "access_surface": access_surface,
        "access_channels": access_channels or [access_surface],
        "permissions": permissions,
        "access_state": _text(access_state).upper(),
        "permission_source": permission_source,
        "role_name": role_name,
        "scope_type": scope_type,
        "scope_value": scope_value,
        "restrictions_json": restrictions_json or "{}",
        "access_verification_status": access_verification_status,
        "item_access_source": item_access_source,
        "item_access_permissions": sorted(item_access_permissions or []),
        "data_access_source": data_access_source or permission_source,
        "sql_access_mode": sql_access_mode,
    }
    row["grant_id"] = _grant_id(
        (
            row["table_id"],
            principal_id,
            access_surface,
            permission_source,
            role_name,
            scope_type,
            scope_value,
            access_state,
            access_value,
            restrictions_json,
            access_verification_status,
            item_access_source,
            ",".join(sorted(item_access_permissions or [])),
            data_access_source or permission_source,
            sql_access_mode,
            ",".join(sorted(access_channels or [access_surface])),
        )
    )
    return row


def _workspace_item_permissions(role: str, item_type: str) -> list[str]:
    """Return the item permissions inherited from one supported Workspace role."""
    if role in ELEVATED_WORKSPACE_ROLES:
        return ["READ", "READALL", "READDATA", "WRITE"]
    if role == "VIEWER" and item_type == "LAKEHOUSE":
        return ["READ", "READALL"]
    if role == "VIEWER" and item_type == "WAREHOUSE":
        return ["READ", "READDATA"]
    return []


def _workspace_item_access(
    tables: list[dict[str, str]],
    observations: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Expand Workspace roles into item-level access evidence."""
    items = {(table["workspace_id"], table["item_id"]): table for table in tables}
    access = []
    for observation in observations:
        role = _text(observation.get("role_name")).upper()
        for (workspace_id, item_id), table in items.items():
            if workspace_id != _text(observation.get("workspace_id")):
                continue
            permissions = _workspace_item_permissions(role, table["item_type"])
            if not permissions:
                continue
            access.append(
                {
                    "workspace_id": workspace_id,
                    "item_id": item_id,
                    "item_type": table["item_type"],
                    "principal_object_id": _text(observation.get("principal_id")),
                    "principal_type": _text(observation.get("user_type")),
                    "principal_name": _text(observation.get("user_principal")),
                    "item_access_permissions": permissions,
                    "item_access_source": "WORKSPACE_ROLE",
                    "role_name": _text(observation.get("role_name")),
                    "access_verification_status": ACCESS_CONFIRMED,
                }
            )
    return access


def _workspace_grants(
    tables: list[dict[str, str]],
    observations: list[dict[str, str]],
    *,
    default_reader_status: dict[str, str] | None = None,
    sql_modes: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Apply Workspace-derived item and data permissions to discovered tables."""
    default_reader_status = default_reader_status or {}
    sql_modes = sql_modes or {}
    grants = []
    for observation in observations:
        role = _text(observation.get("role_name")).upper()
        for table in tables:
            if table["workspace_id"] != _text(observation.get("workspace_id")):
                continue
            item_permissions = _workspace_item_permissions(role, table["item_type"])
            if not item_permissions:
                continue
            if role in ELEVATED_WORKSPACE_ROLES:
                if table["item_type"] == "LAKEHOUSE":
                    grant_specs = [
                        ("READWRITE", ["ONELAKE"], "WORKSPACE_ROLE"),
                        ("READ", ["SQL"], "WORKSPACE_ROLE"),
                    ]
                else:
                    grant_specs = [("READWRITE", ["SQL"], "WORKSPACE_ROLE")]
                status = ACCESS_CONFIRMED
            elif table["item_type"] == "WAREHOUSE":
                grant_specs = [("READ", ["SQL"], "WORKSPACE_READDATA")]
                status = ACCESS_CONFIRMED
            else:
                channels = ["ONELAKE"]
                if sql_modes.get(table["item_id"]) == SQL_MODE_USER:
                    channels.append("SQL")
                grant_specs = [("READ", channels, "ONELAKE_DEFAULT_READER")]
                status = default_reader_status.get(table["item_id"], ACCESS_UNVERIFIED)
            for value, channels, data_source in grant_specs:
                grants.append(
                    _grant(
                        table,
                        principal_id=_text(observation.get("principal_id")),
                        principal_type=_text(observation.get("user_type")),
                        principal_name=_text(observation.get("user_principal")),
                        access_surface="WORKSPACE",
                        access_value=value,
                        access_state="GRANT",
                        permission_source="WORKSPACE_ROLE",
                        role_name=_text(observation.get("role_name")),
                        scope_type="WORKSPACE",
                        scope_value=_text(observation.get("workspace_id")),
                        access_channels=channels,
                        access_verification_status=status,
                        item_access_source="WORKSPACE_ROLE",
                        item_access_permissions=item_permissions,
                        data_access_source=data_source,
                        sql_access_mode=sql_modes.get(table["item_id"], ""),
                    )
                )
    return grants


def _default_reader_status(
    *,
    workspace_id: str,
    item_id: str,
    item_name: str,
    roles: list[dict[str, Any]],
    coverage: list[dict[str, str]],
) -> str:
    """Validate the assumed unmodified Lakehouse DefaultReader role."""
    default_roles = [role for role in roles if _text(role.get("name")).casefold() == "defaultreader"]
    expected_paths = {"*", "tables", "tables/*"}
    selector_valid = False
    rule_valid = False
    for role in default_roles:
        members = role.get("members") or {}
        for member in members.get("fabricItemMembers") or []:
            permissions = {_text(value).upper() for value in member.get("itemAccess") or []}
            source_path = _text(member.get("sourcePath"))
            same_item = source_path in {
                "",
                f"{workspace_id}/{item_id}",
                "00000000-0000-0000-0000-000000000000/00000000-0000-0000-0000-000000000000",
            }
            selector_valid = selector_valid or (same_item and "READALL" in permissions)
        for rule in role.get("decisionRules") or []:
            paths: set[str] = set()
            actions: set[str] = set()
            for scope in rule.get("permission") or []:
                attribute = _text(scope.get("attributeName")).upper()
                values = {_text(value).lower() for value in scope.get("attributeValueIncludedIn") or []}
                if attribute == "PATH":
                    paths.update(values)
                elif attribute == "ACTION":
                    actions.update(value.upper() for value in values)
            constraints = rule.get("constraints") or {}
            rule_valid = rule_valid or (
                _text(rule.get("effect") or "Permit").upper() == "PERMIT"
                and "READ" in actions
                and bool(paths.intersection(expected_paths))
                and not constraints
            )
    if default_roles and selector_valid and rule_valid:
        return ACCESS_CONFIRMED
    coverage.append(
        _coverage(
            "DEFAULT_READER_BASELINE_CONTRADICTION",
            "The observed DefaultReader role does not match the assumed ReadAll-to-unrestricted-Read baseline; normal inherited Viewer access is not effective.",
            status=ACCESS_NOT_EFFECTIVE,
            scope_type="ITEM",
            access_surface="ONELAKE",
            workspace_id=workspace_id,
            item_id=item_id,
            item_name=item_name,
        )
    )
    return ACCESS_NOT_EFFECTIVE


def _sql_access_mode(item: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    """Only confirm modes established by an authoritative configuration signal."""
    if _text(item.get("type")).upper() == "WAREHOUSE":
        return SQL_MODE_DELEGATED
    # OLS database role names do not prove which Lakehouse SQL mode is active.
    return SQL_MODE_UNVERIFIED


def _selector_parts(grant: dict[str, Any]) -> tuple[str, str, set[str]]:
    """Return workspace, item, and required permissions from a virtual selector."""
    selector = _text(grant.get("principal_object_id"))
    payload = selector[len("fabric-item:") :] if selector.startswith("fabric-item:") else ""
    source_path, _, encoded_permissions = payload.rpartition(":")
    if not source_path:
        source_path = f"{grant['workspace_id']}/{grant['item_id']}"
    if source_path == "00000000-0000-0000-0000-000000000000/00000000-0000-0000-0000-000000000000":
        source_path = f"{grant['workspace_id']}/{grant['item_id']}"
    source_workspace_id, _, source_item_id = source_path.partition("/")
    required = {
        value.strip().upper()
        for value in encoded_permissions.replace(",", "+").split("+")
        if value.strip()
    }
    return source_workspace_id, source_item_id, required


def _item_permission_grants(
    tables: list[dict[str, str]],
    item_access: list[dict[str, Any]],
    sql_modes: dict[str, str],
) -> list[dict[str, Any]]:
    """Convert item-level ReadData into table data access where Fabric supports it."""
    grants = []
    for access in item_access:
        permissions = set(access["item_access_permissions"])
        item_id = access["item_id"]
        if not {"READ", "READDATA"}.issubset(permissions):
            continue
        mode = sql_modes.get(item_id, SQL_MODE_UNVERIFIED)
        for table in tables:
            if table["item_id"] != item_id:
                continue
            grants.append(
                _grant(
                    table,
                    principal_id=access["principal_object_id"],
                    principal_type=access["principal_type"],
                    principal_name=access["principal_name"],
                    access_surface="SQL",
                    access_value="SELECT",
                    access_state="GRANT",
                    permission_source="ITEM_READDATA",
                    role_name=access.get("role_name", ""),
                    scope_type="ITEM",
                    scope_value=item_id,
                    access_channels=["SQL"],
                    access_verification_status=(
                        ACCESS_CONFIRMED if mode == SQL_MODE_DELEGATED else ACCESS_UNVERIFIED
                    ),
                    item_access_source=access["item_access_source"],
                    item_access_permissions=access["item_access_permissions"],
                    data_access_source="ITEM_READDATA",
                    sql_access_mode=mode,
                )
            )
    return grants


def _path_matches(table: dict[str, str], path: str) -> bool:
    """Return whether a OneLake role path includes the discovered table."""
    normalized = _text(path).replace("\\", "/").lstrip("/").lower()
    table_path = table["table_path"].lower()
    schema_path = f"tables/{table['schema_name'].lower()}/*" if table["schema_name"] else ""
    return normalized in {"*", "tables", "tables/*", table_path, schema_path}


def _onelake_grants(
    tables: list[dict[str, str]],
    observations: list[dict[str, Any]],
    coverage: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Map OneLake role paths to table-level grant observations."""
    grants = []
    for observation in observations:
        action = _text(observation.get("access_value"))
        state = _text(observation.get("access_state")) or "Permit"
        if not _permissions(action, surface="ONELAKE"):
            coverage.append(
                _coverage(
                    "ONELAKE_PERMISSION_UNSUPPORTED",
                    f"OneLake action {action or 'UNKNOWN'} was not inferred as table access.",
                    status="UNSUPPORTED",
                    scope_type="PERMISSION",
                    access_surface="ONELAKE",
                    workspace_id=_text(observation.get("workspace_id")),
                    item_id=_text(observation.get("item_id")),
                    principal_object_id=_text(observation.get("principal_id")),
                )
            )
            continue
        if state.upper() != "PERMIT":
            coverage.append(
                _coverage(
                    "ONELAKE_EFFECT_UNSUPPORTED",
                    f"OneLake effect {state!r} was not inferred because OneLake roles support Permit semantics.",
                    status="UNSUPPORTED",
                    scope_type="PERMISSION",
                    access_surface="ONELAKE",
                    workspace_id=_text(observation.get("workspace_id")),
                    item_id=_text(observation.get("item_id")),
                    principal_object_id=_text(observation.get("principal_id")),
                )
            )
            continue
        item_tables = [table for table in tables if table["item_id"] == _text(observation.get("item_id"))]
        matched = [table for table in item_tables if _path_matches(table, _text(observation.get("path")))]
        if not matched:
            coverage.append(
                _coverage(
                    "ONELAKE_PATH_NOT_MAPPED",
                    f"OneLake path {_text(observation.get('path'))!r} did not map to a discovered table.",
                    status="UNSUPPORTED",
                    scope_type="PATH",
                    access_surface="ONELAKE",
                    workspace_id=_text(observation.get("workspace_id")),
                    item_id=_text(observation.get("item_id")),
                    principal_object_id=_text(observation.get("principal_id")),
                )
            )
            continue
        for table in matched:
            restrictions_json = _text(observation.get("constraints_json")) or "{}"
            if restrictions_json not in {"{}", "null"}:
                coverage.append(
                    _coverage(
                        "ONELAKE_RESTRICTION_PRESENT",
                        "OneLake row or column constraints restrict this table grant; inspect contributing_grants_json.",
                        status="RESTRICTED",
                        scope_type="TABLE",
                        access_surface="ONELAKE",
                        workspace_id=table["workspace_id"],
                        workspace_name=table["workspace_name"],
                        item_id=table["item_id"],
                        item_name=table["item_name"],
                        principal_object_id=_text(observation.get("principal_id")),
                    )
                )
            grants.append(
                _grant(
                    table,
                    principal_id=_text(observation.get("principal_id")),
                    principal_type=_text(observation.get("user_type")),
                    principal_name=_text(observation.get("user_principal")),
                    access_surface="ONELAKE",
                    access_value=action,
                    access_state=state,
                    permission_source=_text(observation.get("permission_source")),
                    role_name=_text(observation.get("role_name")),
                    scope_type="PATH",
                    scope_value=_text(observation.get("path")),
                    restrictions_json=restrictions_json,
                )
            )
    return grants


def _sql_grants(
    tables: list[dict[str, str]],
    item: dict[str, Any],
    rows: list[dict[str, Any]],
    coverage: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Map SQL database, schema, object, and column permissions to tables."""
    grants = []
    item_id = _text(item.get("id"))
    item_tables = [table for table in tables if table["item_id"] == item_id]
    for value in rows:
        scope_type = _text(value.get("class_desc")).upper()
        schema_name = _text(value.get("schema_name"))
        object_name = _text(value.get("object_name"))
        if scope_type == "DATABASE":
            matched = item_tables
        elif scope_type == "SCHEMA":
            matched = [table for table in item_tables if table["schema_name"].lower() == schema_name.lower()]
        elif scope_type == "OBJECT_OR_COLUMN":
            matched = [
                table
                for table in item_tables
                if table["schema_name"].lower() == schema_name.lower()
                and table["table_name"].lower() == object_name.lower()
            ]
        else:
            coverage.append(
                _coverage(
                    "SQL_PERMISSION_SCOPE_UNSUPPORTED",
                    f"SQL permission scope {scope_type or 'UNKNOWN'} was not inferred as table access.",
                    status="UNSUPPORTED",
                    scope_type="PERMISSION",
                    access_surface="SQL",
                    item_id=item_id,
                    item_name=_text(item.get("displayName")),
                    principal_object_id=_text(value.get("principal_id")),
                )
            )
            continue
        permission_name = _text(value.get("permission_name"))
        if not _permissions(permission_name, surface="SQL"):
            coverage.append(
                _coverage(
                    "SQL_PERMISSION_UNSUPPORTED",
                    f"SQL permission {permission_name or 'UNKNOWN'} was preserved as coverage only.",
                    status="UNSUPPORTED",
                    scope_type="PERMISSION",
                    access_surface="SQL",
                    item_id=item_id,
                    item_name=_text(item.get("displayName")),
                    principal_object_id=_text(value.get("principal_id")),
                )
            )
            continue
        if not matched:
            coverage.append(
                _coverage(
                    "SQL_PERMISSION_SCOPE_NOT_MAPPED",
                    "The SQL permission scope did not map to a discovered table.",
                    status="INCOMPLETE",
                    scope_type="PERMISSION",
                    access_surface="SQL",
                    item_id=item_id,
                    item_name=_text(item.get("displayName")),
                    principal_object_id=_text(value.get("principal_id")),
                )
            )
            continue
        column_name = _text(value.get("column_name"))
        restriction = json.dumps({"column": column_name}, sort_keys=True) if column_name else "{}"
        if column_name:
            coverage.append(
                _coverage(
                    "SQL_COLUMN_RESTRICTION_PRESENT",
                    "A column-scoped SQL permission restricts this table grant; inspect contributing_grants_json.",
                    status="RESTRICTED",
                    scope_type="TABLE",
                    access_surface="SQL",
                    item_id=item_id,
                    item_name=_text(item.get("displayName")),
                    principal_object_id=_text(value.get("principal_id")),
                )
            )
        for table in matched:
            grants.append(
                _grant(
                    table,
                    principal_id=_text(value.get("principal_id")) or _text(value.get("user_name")),
                    principal_type=_text(value.get("user_type")),
                    principal_name=_text(value.get("user_name")),
                    access_surface="SQL",
                    access_value=permission_name,
                    access_state=_text(value.get("state_desc")),
                    permission_source=_text(value.get("permission_source")),
                    role_name=_text(value.get("role_name")),
                    scope_type=scope_type,
                    scope_value=".".join(part for part in (schema_name, object_name, column_name) if part),
                    restrictions_json=restriction,
                )
            )
    return grants


def _discover_access_evidence(
    spark,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, str],
    bool,
    list[dict[str, Any]],
]:
    """Discover visible tables and grants, returning explicit coverage limitations."""
    coverage: list[dict[str, str]] = []
    try:
        token = fabric_access_token()
    except Exception as exc:
        return [], [], {}, False, [_coverage("FABRIC_TOKEN_UNAVAILABLE", str(exc), status="ERROR")]
    try:
        workspaces = list_fabric_pages(f"{FABRIC_API_ROOT}/workspaces", access_token=token)
    except Exception as exc:
        workspaces = []
        coverage.append(
            _coverage("WORKSPACE_DISCOVERY_FAILED", str(exc), status="ERROR", scope_type="TENANT")
        )

    catalog_items_by_workspace: dict[str, list[dict[str, Any]]] = defaultdict(list)
    try:
        for entry in search_fabric_catalog(access_token=token):
            item_type = _text(entry.get("type")).upper()
            workspace = (entry.get("hierarchy") or {}).get("workspace") or {}
            workspace_id = _text(workspace.get("id"))
            if item_type not in SUPPORTED_ITEM_TYPES or not workspace_id or not _text(entry.get("id")):
                continue
            catalog_items_by_workspace[workspace_id].append(
                {
                    "id": _text(entry.get("id")),
                    "displayName": _text(entry.get("displayName")),
                    "type": _text(entry.get("type")),
                    "workspaceId": workspace_id,
                }
            )
            if not any(_text(value.get("id")).casefold() == workspace_id.casefold() for value in workspaces):
                workspaces.append(
                    {
                        "id": workspace_id,
                        "displayName": _text(workspace.get("displayName")),
                        "type": "Workspace",
                    }
                )
    except Exception as exc:
        coverage.append(
            _coverage(
                "CATALOG_DISCOVERY_FAILED",
                str(exc),
                status="INCOMPLETE",
                scope_type="TENANT",
            )
        )

    tables: list[dict[str, str]] = []
    grants: list[dict[str, Any]] = []
    workspace_observations: list[dict[str, str]] = []
    onelake_observations: list[dict[str, Any]] = []
    sql_results: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    sql_modes: dict[str, str] = {}
    default_reader_status: dict[str, str] = {}

    for workspace in workspaces:
        workspace_id = _text(workspace.get("id"))
        workspace_name = _text(workspace.get("displayName"))
        try:
            assignments = list_fabric_pages(
                f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/roleAssignments",
                access_token=token,
            )
            observed_assignments = workspace_role_observations(
                workspace_id=workspace_id,
                assignments=assignments,
            )
            workspace_observations.extend(observed_assignments)
            for observation in observed_assignments:
                if _text(observation.get("role_name")).upper() not in {
                    "VIEWER",
                    *ELEVATED_WORKSPACE_ROLES,
                }:
                    coverage.append(
                        _coverage(
                            "WORKSPACE_ROLE_UNSUPPORTED",
                            f"Workspace role {_text(observation.get('role_name')) or 'UNKNOWN'} was not inferred as table access.",
                            status="UNSUPPORTED",
                            scope_type="PERMISSION",
                            access_surface="WORKSPACE",
                            workspace_id=workspace_id,
                            workspace_name=workspace_name,
                            principal_object_id=_text(observation.get("principal_id")),
                        )
                    )
        except Exception as exc:
            coverage.append(
                _coverage(
                    "WORKSPACE_ROLE_SCAN_FAILED",
                    str(exc),
                    status="ERROR",
                    scope_type="WORKSPACE",
                    access_surface="WORKSPACE",
                    workspace_id=workspace_id,
                    workspace_name=workspace_name,
                )
            )
        catalog_items = catalog_items_by_workspace.get(workspace_id, [])
        try:
            workspace_items = list_fabric_pages(
                f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/items",
                access_token=token,
            )
            items_by_id = {_text(item.get("id")): item for item in workspace_items}
            for item in catalog_items:
                items_by_id.setdefault(_text(item.get("id")), item)
            items = list(items_by_id.values())
        except Exception as exc:
            coverage.append(
                _coverage(
                    "ITEM_DISCOVERY_FAILED",
                    (
                        f"{exc} Catalog Search supplied {len(catalog_items)} caller-visible supported item(s)."
                        if catalog_items
                        else str(exc)
                    ),
                    status="INCOMPLETE" if catalog_items else "ERROR",
                    scope_type="WORKSPACE",
                    workspace_id=workspace_id,
                    workspace_name=workspace_name,
                )
            )
            items = catalog_items
            if not items:
                continue

        for item in items:
            item_type = _text(item.get("type")).upper()
            if item_type not in SUPPORTED_ITEM_TYPES:
                continue
            item_id = _text(item.get("id"))
            item_name = _text(item.get("displayName"))
            coverage.append(
                _coverage(
                    "ITEM_PERMISSION_ENUMERATION_UNAVAILABLE",
                    "Fabric does not expose a supported caller-accessible non-admin API that enumerates direct item permission assignments; absence of a visible assignment is not treated as denial.",
                    scope_type="ITEM",
                    workspace_id=workspace_id,
                    workspace_name=workspace_name,
                    item_id=item_id,
                    item_name=item_name,
                )
            )
            discovered_tables: list[dict[str, str]] = []
            if item_type == "LAKEHOUSE":
                try:
                    discovered_tables = _lakehouse_tables(workspace=workspace, item=item, access_token=token)
                except Exception as exc:
                    coverage.append(
                        _coverage(
                            "LAKEHOUSE_TABLE_REST_SCAN_FAILED",
                            str(exc),
                            status="INCOMPLETE",
                            scope_type="ITEM",
                            workspace_id=workspace_id,
                            workspace_name=workspace_name,
                            item_id=item_id,
                            item_name=item_name,
                        )
                    )
            if not discovered_tables:
                try:
                    discovered_tables = _sql_tables(spark, workspace=workspace, item=item)
                except Exception as exc:
                    coverage.append(
                        _coverage(
                            "TABLE_DISCOVERY_FAILED",
                            str(exc),
                            status="ERROR",
                            scope_type="ITEM",
                            workspace_id=workspace_id,
                            workspace_name=workspace_name,
                            item_id=item_id,
                            item_name=item_name,
                        )
                    )
            tables.extend(discovered_tables)

            try:
                permission_frame = read_discovered_sql_endpoint_query(
                    spark,
                    workspace_id=workspace_id,
                    item_id=item_id,
                    item_kind=item_type.lower(),
                    database_name=item_name,
                    query=SQL_ACCESS_QUERY,
                )
                sql_results.append((item, _sql_endpoint_rows(permission_frame)))
            except Exception as exc:
                coverage.append(
                    _coverage(
                        "SQL_PERMISSION_SCAN_FAILED",
                        str(exc),
                        status="ERROR",
                        scope_type="ITEM",
                        access_surface="SQL",
                        workspace_id=workspace_id,
                        workspace_name=workspace_name,
                        item_id=item_id,
                        item_name=item_name,
                    )
                )

            sql_modes[item_id] = _sql_access_mode(item, [])
            if item_type == "LAKEHOUSE":
                    coverage.append(
                        _coverage(
                            "SQL_ACCESS_MODE_UNVERIFIED",
                            "No supported read-only metadata established whether this Lakehouse SQL endpoint uses delegated identity or user identity mode; table SQL access remains unverified.",
                            scope_type="ITEM",
                            access_surface="SQL",
                            workspace_id=workspace_id,
                            workspace_name=workspace_name,
                            item_id=item_id,
                            item_name=item_name,
                        )
                    )

            if item_type == "LAKEHOUSE":
                try:
                    roles = list_fabric_pages(
                        f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/items/{item_id}/dataAccessRoles",
                        access_token=token,
                    )
                    onelake_observations.extend(
                        onelake_role_observations(
                            target=item_id,
                            workspace_id=workspace_id,
                            item_id=item_id,
                            roles=roles,
                        )
                    )
                    default_reader_status[item_id] = _default_reader_status(
                        workspace_id=workspace_id,
                        item_id=item_id,
                        item_name=item_name,
                        roles=roles,
                        coverage=coverage,
                    )
                except Exception as exc:
                    default_reader_status[item_id] = ACCESS_UNVERIFIED
                    coverage.append(
                        _coverage(
                            "ONELAKE_ROLE_SCAN_FAILED",
                            str(exc),
                            status="ERROR",
                            scope_type="ITEM",
                            access_surface="ONELAKE",
                            workspace_id=workspace_id,
                            workspace_name=workspace_name,
                            item_id=item_id,
                            item_name=item_name,
                        )
                    )

    unique_tables = {table["table_id"]: table for table in tables}
    tables = list(unique_tables.values())
    item_access = _workspace_item_access(tables, workspace_observations)
    grants.extend(
        _workspace_grants(
            tables,
            workspace_observations,
            default_reader_status=default_reader_status,
            sql_modes=sql_modes,
        )
    )
    grants.extend(_item_permission_grants(tables, item_access, sql_modes))
    grants.extend(_onelake_grants(tables, onelake_observations, coverage))
    for item, rows in sql_results:
        item_sql_grants = _sql_grants(tables, item, rows, coverage)
        grants.extend(item_sql_grants)
    return grants, item_access, sql_modes, False, coverage


def _validate_inputs(identity_map_df, group_membership_df) -> None:
    """Validate the two caller-owned mapping DataFrame contracts."""
    identity_missing = IDENTITY_COLUMNS.difference(identity_map_df.columns)
    membership_missing = MEMBERSHIP_COLUMNS.difference(group_membership_df.columns)
    if identity_missing:
        raise ValueError("identity_map_df is missing required columns: " + ", ".join(sorted(identity_missing)))
    if membership_missing:
        raise ValueError(
            "group_membership_df is missing required columns: " + ", ".join(sorted(membership_missing))
        )
    if identity_map_df.sparkSession is not group_membership_df.sparkSession:
        raise ValueError("identity_map_df and group_membership_df must use the same Spark session.")


def _mapping_rows(identity_map_df, group_membership_df):
    """Build normalized identity and group-edge mappings supplied by the caller."""
    identities: dict[str, dict[str, str]] = {}
    coverage: list[dict[str, str]] = []
    for row in identity_map_df.select(*sorted(IDENTITY_COLUMNS)).toLocalIterator():
        value = row.asDict(recursive=True)
        object_id = _text(value.get("object_id"))
        if not object_id:
            coverage.append(
                _coverage(
                    "IDENTITY_OBJECT_ID_MISSING",
                    "An identity mapping row had no object_id and was ignored.",
                    scope_type="IDENTITY",
                )
            )
            continue
        normalized = {
            "object_id": object_id,
            "display_name": _text(value.get("display_name")),
            "user_principal_name": _text(value.get("user_principal_name")),
            "principal_type": normalise_principal_type(value.get("principal_type")),
            "group_type": _text(value.get("group_type")).upper().replace(" ", "_").replace("-", "_"),
        }
        prior = identities.get(object_id)
        if prior is not None and prior != normalized:
            coverage.append(
                _coverage(
                    "DUPLICATE_IDENTITY_MAPPING",
                    "Conflicting identity rows share the same object_id; the first row was used.",
                    scope_type="IDENTITY",
                    principal_object_id=object_id,
                )
            )
            continue
        identities[object_id] = normalized

    memberships: dict[str, list[str]] = defaultdict(list)
    for row in group_membership_df.select(*sorted(MEMBERSHIP_COLUMNS)).toLocalIterator():
        value = row.asDict(recursive=True)
        group_id = _text(value.get("group_object_id"))
        member_id = _text(value.get("member_object_id"))
        if not group_id or not member_id:
            coverage.append(
                _coverage(
                    "GROUP_MEMBERSHIP_ID_MISSING",
                    "A group membership row lacked a group or member Object ID and was ignored.",
                    scope_type="GROUP_MEMBERSHIP",
                    principal_object_id=group_id or member_id,
                )
            )
            continue
        if member_id not in memberships[group_id]:
            memberships[group_id].append(member_id)
    return identities, memberships, coverage


def _expand_principal(
    principal_id: str,
    *,
    identities: dict[str, dict[str, str]],
    memberships: dict[str, list[str]],
    coverage: list[dict[str, str]],
    path: tuple[str, ...] = (),
) -> list[tuple[dict[str, str], tuple[str, ...]]]:
    """Expand one principal to users recursively while preserving every unique path."""
    if principal_id.casefold() in {value.casefold() for value in path}:
        coverage.append(
            _coverage(
                "GROUP_MEMBERSHIP_CYCLE",
                "A recursive group membership cycle was detected and stopped.",
                scope_type="GROUP_MEMBERSHIP",
                principal_object_id=principal_id,
            )
        )
        return []
    identity = identities.get(principal_id)
    if identity is None:
        identity = next(
            (
                value
                for object_id, value in identities.items()
                if object_id.casefold() == principal_id.casefold()
            ),
            None,
        )
    if identity is None:
        coverage.append(
            _coverage(
                "UNRESOLVED_IDENTITY",
                "The principal Object ID was not present in identity_map_df.",
                scope_type="IDENTITY",
                principal_object_id=principal_id,
            )
        )
        return []
    principal_type = identity["principal_type"]
    resolved_principal_id = identity["object_id"]
    next_path = (*path, resolved_principal_id)
    if principal_type == "USER":
        return [(identity, next_path)]
    if principal_type != "GROUP":
        coverage.append(
            _coverage(
                "NON_USER_PRINCIPAL",
                f"Principal type {principal_type or 'UNKNOWN'} is not an individual user.",
                status="UNSUPPORTED",
                scope_type="IDENTITY",
                principal_object_id=principal_id,
            )
        )
        return []
    group_type = identity["group_type"].replace("_", "")
    if group_type not in {value.replace("_", "") for value in SECURITY_GROUP_TYPES}:
        coverage.append(
            _coverage(
                "GROUP_TYPE_NOT_EXPANDED",
                f"Group type {identity['group_type'] or 'UNKNOWN'} was not treated as an access-bearing security group.",
                status="UNSUPPORTED",
                scope_type="GROUP_MEMBERSHIP",
                principal_object_id=principal_id,
            )
        )
        return []
    members = memberships.get(principal_id)
    if members is None:
        members = next(
            (
                value
                for group_id, value in memberships.items()
                if group_id.casefold() == principal_id.casefold()
            ),
            [],
        )
    if not members:
        coverage.append(
            _coverage(
                "GROUP_MEMBERSHIP_INCOMPLETE",
                "No supplied members were available for an access-bearing security group.",
                scope_type="GROUP_MEMBERSHIP",
                principal_object_id=principal_id,
            )
        )
        return []
    expanded = []
    seen: set[tuple[str, ...]] = set()
    for member_id in members:
        for person, member_path in _expand_principal(
            member_id,
            identities=identities,
            memberships=memberships,
            coverage=coverage,
            path=next_path,
        ):
            if member_path not in seen:
                seen.add(member_path)
                expanded.append((person, member_path))
    return expanded


def _resolve_item_access(
    item_access: list[dict[str, Any]],
    *,
    identities: dict[str, dict[str, str]],
    memberships: dict[str, list[str]],
    coverage: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Resolve item-access assignments to individual people."""
    resolved = []
    for access in item_access:
        for person, path in _expand_principal(
            access["principal_object_id"],
            identities=identities,
            memberships=memberships,
            coverage=coverage,
        ):
            resolved.append(
                {
                    **access,
                    "person_object_id": person["object_id"],
                    "person_display_name": person["display_name"],
                    "person_user_principal_name": person["user_principal_name"],
                    "person_principal_type": person["principal_type"],
                    "item_inheritance_path": list(path),
                }
            )
    return resolved


def _verification_for_grant(
    grant: dict[str, Any],
    item_match: dict[str, Any] | None,
    *,
    item_visibility_complete: bool,
    sql_modes: dict[str, str],
) -> str:
    """Combine one data grant with its required item-access prerequisite."""
    if grant["access_surface"] == "WORKSPACE":
        return grant["access_verification_status"]
    mode = sql_modes.get(grant["item_id"], SQL_MODE_UNVERIFIED)
    if grant["access_surface"] == "SQL":
        if mode == SQL_MODE_USER:
            return ACCESS_NOT_EFFECTIVE
        if item_match is None:
            return ACCESS_NOT_EFFECTIVE if item_visibility_complete else ACCESS_UNVERIFIED
        if mode != SQL_MODE_DELEGATED:
            return ACCESS_UNVERIFIED
        return item_match["access_verification_status"]
    if item_match is None:
        return ACCESS_NOT_EFFECTIVE if item_visibility_complete else ACCESS_UNVERIFIED
    return item_match["access_verification_status"]


def _resolve_grants(
    grants: list[dict[str, Any]],
    *,
    item_access: list[dict[str, Any]],
    sql_modes: dict[str, str],
    item_visibility_complete: bool,
    identities: dict[str, dict[str, str]],
    memberships: dict[str, list[str]],
    coverage: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Resolve grants to people and require applicable item-level access."""
    resolved = []
    resolved_item_access = _resolve_item_access(
        item_access,
        identities=identities,
        memberships=memberships,
        coverage=coverage,
    )
    used_item_access: set[tuple[str, str]] = set()
    for grant in grants:
        people: list[tuple[dict[str, str], tuple[str, ...]]] = []
        selector_matches: list[dict[str, Any]] = []
        if grant["principal_type"] == "FABRIC_ITEM_MEMBERS":
            source_workspace_id, source_item_id, required = _selector_parts(grant)
            selector_matches = [
                access
                for access in resolved_item_access
                if access["workspace_id"].casefold() == source_workspace_id.casefold()
                and access["item_id"].casefold() == source_item_id.casefold()
                and required.issubset(set(access["item_access_permissions"]))
            ]
            if not selector_matches:
                coverage.append(
                    _coverage(
                        "ITEM_PERMISSION_SELECTOR_UNRESOLVED",
                        "The OneLake virtual member selector could not be resolved to people from confirmed item-access evidence; direct item assignments may be outside caller visibility.",
                        scope_type="ITEM",
                        access_surface="ONELAKE",
                        workspace_id=grant["workspace_id"],
                        workspace_name=grant["workspace_name"],
                        item_id=grant["item_id"],
                        item_name=grant["item_name"],
                    )
                )
                continue
            people = [
                (
                    {
                        "object_id": access["person_object_id"],
                        "display_name": access["person_display_name"],
                        "user_principal_name": access["person_user_principal_name"],
                        "principal_type": access["person_principal_type"],
                    },
                    tuple(access["item_inheritance_path"]),
                )
                for access in selector_matches
            ]
        else:
            people = _expand_principal(
                grant["principal_object_id"],
                identities=identities,
                memberships=memberships,
                coverage=coverage,
            )
        for person, path in people:
            item_matches = [
                access
                for access in resolved_item_access
                if access["person_object_id"].casefold() == person["object_id"].casefold()
                and access["workspace_id"].casefold() == grant["workspace_id"].casefold()
                and access["item_id"].casefold() == grant["item_id"].casefold()
                and "READ" in access["item_access_permissions"]
            ]
            if grant["access_surface"] == "WORKSPACE":
                item_matches = [None]
            elif not item_matches:
                item_matches = [None]
            for item_match in item_matches:
                status = _verification_for_grant(
                    grant,
                    item_match,
                    item_visibility_complete=item_visibility_complete,
                    sql_modes=sql_modes,
                )
                if item_match is not None:
                    used_item_access.add((item_match["person_object_id"], item_match["item_id"]))
                if status == ACCESS_UNVERIFIED:
                    coverage.append(
                        _coverage(
                            "ITEM_ACCESS_UNVERIFIED",
                            "A data permission was observed, but required item access or the governing SQL access mode could not be established.",
                            scope_type="ITEM",
                            access_surface=grant["access_surface"],
                            workspace_id=grant["workspace_id"],
                            workspace_name=grant["workspace_name"],
                            item_id=grant["item_id"],
                            item_name=grant["item_name"],
                            principal_object_id=person["object_id"],
                        )
                    )
                elif status == ACCESS_NOT_EFFECTIVE:
                    reason = (
                        "SQL table grants are not effective in user identity mode; OneLake Security governs table access."
                        if grant["access_surface"] == "SQL"
                        and sql_modes.get(grant["item_id"]) == SQL_MODE_USER
                        else "The required item Read permission is known to be absent."
                    )
                    coverage.append(
                        _coverage(
                            "DATA_PERMISSION_NOT_EFFECTIVE",
                            reason,
                            status=ACCESS_NOT_EFFECTIVE,
                            scope_type="TABLE",
                            access_surface=grant["access_surface"],
                            workspace_id=grant["workspace_id"],
                            workspace_name=grant["workspace_name"],
                            item_id=grant["item_id"],
                            item_name=grant["item_name"],
                            principal_object_id=person["object_id"],
                        )
                    )
                mode = sql_modes.get(grant["item_id"], "")
                channels = list(grant["access_channels"])
                if grant["access_surface"] == "ONELAKE" and mode == SQL_MODE_USER:
                    channels = sorted({*channels, "SQL"})
                resolved.append(
                    {
                        **grant,
                        "person_object_id": person["object_id"],
                        "person_display_name": person["display_name"],
                        "person_user_principal_name": person["user_principal_name"],
                        "person_principal_type": person["principal_type"],
                        "inheritance_path": list(path),
                        "item_inheritance_path": (
                            list(item_match["item_inheritance_path"]) if item_match else []
                        ),
                        "item_access_source": (
                            item_match["item_access_source"]
                            if item_match
                            else grant["item_access_source"] or "UNOBSERVED"
                        ),
                        "item_access_permissions": (
                            item_match["item_access_permissions"]
                            if item_match
                            else grant["item_access_permissions"]
                        ),
                        "access_verification_status": status,
                        "sql_access_mode": mode or grant["sql_access_mode"],
                        "access_channels": channels,
                    }
                )
    for access in resolved_item_access:
        key = (access["person_object_id"], access["item_id"])
        if key not in used_item_access and access["item_access_source"] != "WORKSPACE_ROLE":
            coverage.append(
                _coverage(
                    "ITEM_ACCESS_WITHOUT_DATA_PERMISSION",
                    "Item access was observed, but no applicable table data permission was established.",
                    status=ACCESS_NOT_EFFECTIVE,
                    scope_type="ITEM",
                    workspace_id=access["workspace_id"],
                    item_id=access["item_id"],
                    principal_object_id=access["person_object_id"],
                )
            )
    return resolved


def _contribution(row: dict[str, Any]) -> dict[str, Any]:
    """Select stable auditable provenance fields for one contributing grant."""
    return {
        "grant_id": row["grant_id"],
        "principal_object_id": row["principal_object_id"],
        "principal_type": row["principal_type"],
        "principal_name": row["principal_name"],
        "permission_source": row["permission_source"],
        "role_name": row["role_name"],
        "scope_type": row["scope_type"],
        "scope_value": row["scope_value"],
        "access_state": row["access_state"],
        "permissions": row["permissions"],
        "access_channels": row["access_channels"],
        "access_verification_status": row["access_verification_status"],
        "item_access_source": row["item_access_source"],
        "item_access_permissions": row["item_access_permissions"],
        "item_inheritance_path": row["item_inheritance_path"],
        "data_access_source": row["data_access_source"],
        "sql_access_mode": row["sql_access_mode"],
        "restrictions": json.loads(row["restrictions_json"] or "{}"),
        "inheritance_path": row["inheritance_path"],
    }


def _consolidate(
    resolved: list[dict[str, Any]],
    coverage: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Consolidate effective permissions by person, table, and access surface."""
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in resolved:
        grouped[(row["person_object_id"], row["table_id"], row["access_surface"])].append(row)
    output = []
    for rows in grouped.values():
        sample = rows[0]
        grant_rows = [
            row
            for row in rows
            if row["access_state"] in {"GRANT", "GRANT_WITH_GRANT_OPTION", "PERMIT"}
        ]
        deny_rows = [row for row in rows if row["access_state"].startswith("DENY")]

        def survives_deny(grant_row: dict[str, Any], permission: str) -> bool:
            grant_restriction = grant_row["restrictions_json"] or "{}"
            return not any(
                permission in deny_row["permissions"]
                and (
                    (deny_row["restrictions_json"] or "{}") in {"{}", "null"}
                    or (deny_row["restrictions_json"] or "{}") == grant_restriction
                )
                for deny_row in deny_rows
            )

        observed = sorted(
            {
                permission
                for row in grant_rows
                for permission in row["permissions"]
                if survives_deny(row, permission)
            }
        )
        effective = sorted(
            {
                permission
                for row in grant_rows
                if row["access_verification_status"] == ACCESS_CONFIRMED
                for permission in row["permissions"]
                if survives_deny(row, permission)
            }
        )
        unverified = sorted(
            {
                permission
                for row in grant_rows
                if row["access_verification_status"] == ACCESS_UNVERIFIED
                for permission in row["permissions"]
                if survives_deny(row, permission)
            }
        )
        denied = {permission for row in deny_rows for permission in row["permissions"]}
        if denied:
            coverage.append(
                _coverage(
                    "PERMISSION_DENY_APPLIED",
                    "Observed deny permissions were removed from the effective result.",
                    status="RESTRICTED",
                    scope_type="TABLE",
                    access_surface=sample["access_surface"],
                    workspace_id=sample["workspace_id"],
                    workspace_name=sample["workspace_name"],
                    item_id=sample["item_id"],
                    item_name=sample["item_name"],
                    principal_object_id=sample["person_object_id"],
                )
            )
        contributions = sorted(
            (_contribution(row) for row in rows),
            key=lambda value: (value["grant_id"], value["inheritance_path"]),
        )
        inheritance_paths = sorted({" -> ".join(value["inheritance_path"]) for value in contributions})
        item_inheritance_paths = sorted(
            {
                " -> ".join(value["item_inheritance_path"])
                for value in contributions
                if value["item_inheritance_path"]
            }
        )
        restricted = bool(denied) or any(value["restrictions"] for value in contributions)
        access_channels = sorted(
            {
                channel
                for contribution in contributions
                for channel in contribution["access_channels"]
            }
        )
        if effective:
            verification_status = ACCESS_CONFIRMED
        elif unverified:
            verification_status = ACCESS_UNVERIFIED
        else:
            verification_status = ACCESS_NOT_EFFECTIVE
        item_access_sources = sorted(
            {value["item_access_source"] for value in contributions if value["item_access_source"]}
        )
        data_access_sources = sorted(
            {value["data_access_source"] for value in contributions if value["data_access_source"]}
        )
        item_access_permissions = sorted(
            {
                permission
                for contribution in contributions
                for permission in contribution["item_access_permissions"]
            }
        )
        channel_permissions: dict[str, set[str]] = defaultdict(set)
        for row in grant_rows:
            if row["access_verification_status"] != ACCESS_CONFIRMED:
                continue
            for permission in row["permissions"]:
                if survives_deny(row, permission):
                    for channel in row["access_channels"]:
                        channel_permissions[channel].add(permission)
        output.append(
            {
                "person_object_id": sample["person_object_id"],
                "person_display_name": sample["person_display_name"],
                "person_user_principal_name": sample["person_user_principal_name"],
                "person_principal_type": sample["person_principal_type"],
                "table_id": sample["table_id"],
                "workspace_id": sample["workspace_id"],
                "workspace_name": sample["workspace_name"],
                "item_id": sample["item_id"],
                "item_name": sample["item_name"],
                "item_type": sample["item_type"],
                "schema_name": sample["schema_name"],
                "table_name": sample["table_name"],
                "table_path": sample["table_path"],
                "access_surface": sample["access_surface"],
                "access_verification_status": verification_status,
                "access_channels": access_channels,
                "channel_permissions_json": json.dumps(
                    {channel: sorted(values) for channel, values in sorted(channel_permissions.items())},
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "item_access_source": ";".join(item_access_sources),
                "item_access_permissions": item_access_permissions,
                "data_access_source": ";".join(data_access_sources),
                "sql_access_mode": ";".join(
                    sorted({value["sql_access_mode"] for value in contributions if value["sql_access_mode"]})
                ),
                "observed_permissions": observed,
                "effective_permissions": effective,
                "is_restricted": restricted,
                "contributing_grant_count": len(contributions),
                "inheritance_paths": inheritance_paths,
                "item_inheritance_paths": item_inheritance_paths,
                "contributing_grants_json": json.dumps(contributions, sort_keys=True, separators=(",", ":")),
            }
        )
    return output


def _access_df(spark, rows: list[dict[str, Any]]):
    """Create a stable access result DataFrame, including when no access is visible."""
    from pyspark.sql import types as T

    schema = T.StructType(
        [
            T.StructField("person_object_id", T.StringType(), False),
            T.StructField("person_display_name", T.StringType(), True),
            T.StructField("person_user_principal_name", T.StringType(), True),
            T.StructField("person_principal_type", T.StringType(), False),
            T.StructField("table_id", T.StringType(), False),
            T.StructField("workspace_id", T.StringType(), False),
            T.StructField("workspace_name", T.StringType(), True),
            T.StructField("item_id", T.StringType(), False),
            T.StructField("item_name", T.StringType(), True),
            T.StructField("item_type", T.StringType(), False),
            T.StructField("schema_name", T.StringType(), True),
            T.StructField("table_name", T.StringType(), False),
            T.StructField("table_path", T.StringType(), True),
            T.StructField("access_surface", T.StringType(), False),
            T.StructField("access_verification_status", T.StringType(), False),
            T.StructField("access_channels", T.ArrayType(T.StringType(), False), False),
            T.StructField("channel_permissions_json", T.StringType(), False),
            T.StructField("item_access_source", T.StringType(), False),
            T.StructField("item_access_permissions", T.ArrayType(T.StringType(), False), False),
            T.StructField("data_access_source", T.StringType(), False),
            T.StructField("sql_access_mode", T.StringType(), False),
            T.StructField("observed_permissions", T.ArrayType(T.StringType(), False), False),
            T.StructField("effective_permissions", T.ArrayType(T.StringType(), False), False),
            T.StructField("is_restricted", T.BooleanType(), False),
            T.StructField("contributing_grant_count", T.IntegerType(), False),
            T.StructField("inheritance_paths", T.ArrayType(T.StringType(), False), False),
            T.StructField("item_inheritance_paths", T.ArrayType(T.StringType(), False), False),
            T.StructField("contributing_grants_json", T.StringType(), False),
        ]
    )
    return spark.createDataFrame(rows, schema=schema)


def _coverage_df(spark, rows: list[dict[str, str]]):
    """Create a stable coverage result DataFrame."""
    from pyspark.sql import types as T

    fields = [
        "status",
        "reason_code",
        "scope_type",
        "access_surface",
        "workspace_id",
        "workspace_name",
        "item_id",
        "item_name",
        "principal_object_id",
        "detail",
    ]
    schema = T.StructType([T.StructField(field, T.StringType(), False) for field in fields])
    unique = {tuple(row.get(field, "") for field in fields) for row in rows}
    return spark.createDataFrame(sorted(unique), schema=schema)


def scan_effective_access(*, identity_map_df, group_membership_df) -> dict[str, Any]:
    """Resolve visible Fabric table access to actual individual users.

    The scan uses caller-scoped Workspace and Catalog Search APIs to discover
    visible and directly shared Lakehouse and Warehouse items, then inventories
    tables and the Workspace, SQL, and OneLake permission surfaces that the
    caller can inspect. It uses the current Fabric notebook identity and does
    not require FabricOps metadata, persistence, Microsoft Graph, a separately
    supplied token, or Fabric Admin APIs.

    ``identity_map_df`` must contain ``object_id``, ``display_name``,
    ``user_principal_name``, ``principal_type``, and ``group_type``.
    ``group_membership_df`` must contain ``group_object_id`` and
    ``member_object_id``. Only groups whose ``group_type`` identifies a
    security group are recursively expanded. Cycles are stopped, duplicate
    edges are ignored, and every distinct inheritance path is retained.

    Effective table access requires both applicable item-level access and an
    applicable data permission. ``access`` therefore labels each person,
    table, and permission surface as ``CONFIRMED``, ``UNVERIFIED``, or
    ``NOT_EFFECTIVE`` in ``access_verification_status``. Only confirmed
    permissions appear in ``effective_permissions``; visible permissions that
    still lack a verified prerequisite remain in ``observed_permissions`` and
    provenance instead of being presented as effective.

    Workspace roles establish item access and can also establish data access.
    For Lakehouse Viewers, the scan preserves Fabric's normal DefaultReader
    assumption: an unmodified DefaultReader role maps item ``ReadAll`` to
    OneLake ``Read``. An observed conflicting configuration is reported in
    ``coverage`` and is not claimed as confirmed unrestricted access. The scan
    never modifies DefaultReader.

    SQL table permissions are effective only when item ``Read`` is established
    and the SQL analytics endpoint is in delegated identity mode. In user
    identity mode, OneLake Security governs table access and SQL table grants
    are retained as ``NOT_EFFECTIVE`` evidence. If a supported read-only
    mechanism cannot establish the mode, the SQL result remains
    ``UNVERIFIED``. SQL and OneLake permissions remain separate surfaces.

    ``contributing_grants_json`` retains all contributing item and data grants,
    modes, restrictions, and inheritance paths. ``channel_permissions_json``
    keeps SQL and OneLake capabilities distinct when one Workspace path
    contributes to both channels. ``coverage`` records
    inaccessible scopes, unresolved identities, incomplete group expansion,
    unsupported permission shapes, applied denies, restrictions, scan errors,
    and item-permission visibility gaps. A missing access row is therefore not
    evidence that access does not exist; inspect ``coverage`` with every
    result.

    The function only reads permission metadata. It does not grant access,
    modify DefaultReader, or persist results. OneLake row and column
    constraints and SQL column restrictions are retained and flagged as
    restricted instead of being presented as unrestricted table access.

    Parameters
    ----------
    identity_map_df : pyspark.sql.DataFrame
        Principal directory snapshot with ``object_id``, ``display_name``,
        ``user_principal_name``, ``principal_type``, and ``group_type``.
        Object IDs remain the stable join keys and readable fields are copied
        to the person-level result.
    group_membership_df : pyspark.sql.DataFrame
        Caller-supplied group edges with ``group_object_id`` and
        ``member_object_id``. Supply transitive source edges; FabricOps performs
        the recursive expansion and cycle detection.

    Returns
    -------
    dict[str, pyspark.sql.DataFrame]
        ``access`` contains consolidated person/table/surface observations,
        explicit verification status, confirmed effective permissions, and
        provenance. ``coverage`` contains visibility gaps, unsupported cases,
        restrictions, contradictions, and errors.

    Raises
    ------
    ValueError
        If either DataFrame lacks required columns or the DataFrames belong to
        different Spark sessions.

    Examples
    --------
    >>> result = scan_effective_access(
    ...     identity_map_df=identity_map_df,
    ...     group_membership_df=group_membership_df,
    ... )
    >>> display(result["access"])
    >>> display(result["coverage"])

    """
    _validate_inputs(identity_map_df, group_membership_df)
    spark = identity_map_df.sparkSession
    identities, memberships, coverage = _mapping_rows(identity_map_df, group_membership_df)
    grants, item_access, sql_modes, item_visibility_complete, discovery_coverage = (
        _discover_access_evidence(spark)
    )
    coverage.extend(discovery_coverage)
    resolved = _resolve_grants(
        grants,
        item_access=item_access,
        sql_modes=sql_modes,
        item_visibility_complete=item_visibility_complete,
        identities=identities,
        memberships=memberships,
        coverage=coverage,
    )
    access_rows = _consolidate(resolved, coverage)
    return {
        "access": _access_df(spark, access_rows),
        "coverage": _coverage_df(spark, coverage),
    }
