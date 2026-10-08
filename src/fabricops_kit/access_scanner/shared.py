"""Shared foundations for Fabric access scanners."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import FabricStore, build_table_id, get_store
from fabricops_kit.io.shared import read_warehouse_synapsesql, validate_select_query
from fabricops_kit.io.write_lakehouse_table import write_lakehouse_table


ACCESS_TABLE = "METADATA_DATA_ACCESS"
FABRIC_API_ROOT = "https://api.fabric.microsoft.com/v1"


def normalise_principal_type(principal_type: Any) -> str:
    """Normalize known source principal types without treating other identities as users."""
    source_type = str(principal_type or "UNKNOWN").strip().upper().replace(" ", "_").replace("-", "_")
    aliases = {
        "EXTERNAL_USER": "USER",
        "SQL_USER": "USER",
        "WINDOWS_USER": "USER",
        "EXTERNAL_GROUP": "GROUP",
        "EXTERNAL_GROUPS": "GROUP",
        "WINDOWS_GROUP": "GROUP",
        "SERVICEPRINCIPAL": "SERVICE_PRINCIPAL",
    }
    return aliases.get(source_type, source_type or "UNKNOWN")


def normalise_targets(targets: str | list[str] | tuple[str, ...]) -> list[str]:
    """Return unique, validated configured target keys in input order."""
    values = [targets] if isinstance(targets, str) else list(targets)
    normalised = []
    for value in values:
        store = str(value or "").strip()
        if not store:
            raise ValueError("Access scan targets must be non-empty strings.")
        if store not in normalised:
            normalised.append(store)
    if not normalised:
        raise ValueError("At least one configured physical data item target is required for access scanning.")
    return normalised


def target_store_kinds(config, environment_name: str, targets: list[str]) -> dict[str, str]:
    """Resolve configured physical data item targets to normalized store kinds."""
    return {store: str(get_store(config, environment_name, store).kind).strip().lower() for store in targets}


def fabric_access_token(access_token: str | None = None) -> str:
    """Return an explicit token or acquire the current Fabric notebook token."""
    if access_token:
        return str(access_token).strip()
    try:
        import notebookutils  # type: ignore

        token = notebookutils.credentials.getToken("pbi")
    except Exception as exc:
        raise RuntimeError(
            "Access scanning requires a Fabric REST token. Run inside a Fabric notebook "
            "or pass access_token explicitly."
        ) from exc
    if not token:
        raise RuntimeError("NotebookUtils did not return a Fabric REST token.")
    return str(token)


def request_fabric_json(
    url: str,
    *,
    access_token: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Request one Fabric REST resource and return its JSON object."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "api.fabric.microsoft.com":
        raise RuntimeError("Refusing to send a Fabric bearer token to an unexpected host.")
    encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    if encoded_body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        url,
        data=encoded_body,
        headers=headers,
        method=method.upper(),
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Fabric REST request failed with HTTP {exc.code}: {detail or exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Fabric REST request failed: {exc.reason}") from exc
    data = json.loads(payload or "{}")
    if not isinstance(data, dict):
        raise RuntimeError("Fabric REST response was not a JSON object.")
    return data


def search_fabric_catalog(*, access_token: str) -> list[dict[str, Any]]:
    """Return caller-visible Lakehouse and Warehouse catalog entries."""
    url = f"{FABRIC_API_ROOT}/catalog/search"
    body: dict[str, Any] = {
        "search": "*",
        "filter": "Type eq 'Lakehouse' or Type eq 'Warehouse'",
        "pageSize": 1000,
    }
    rows: list[dict[str, Any]] = []
    seen_tokens: set[str] = set()
    while True:
        payload = request_fabric_json(
            url,
            access_token=access_token,
            method="POST",
            body=body,
        )
        values = payload.get("value") or []
        if not isinstance(values, list):
            raise RuntimeError("Fabric catalog response contains a non-list value.")
        rows.extend(value for value in values if isinstance(value, dict))
        continuation_token = str(payload.get("continuationToken") or "").strip()
        if not continuation_token:
            return rows
        if continuation_token in seen_tokens:
            raise RuntimeError("Fabric catalog pagination returned a repeated continuation token.")
        seen_tokens.add(continuation_token)
        body = {"continuationToken": continuation_token}


def list_fabric_pages(
    url: str,
    *,
    access_token: str,
    collection_key: str = "value",
) -> list[dict[str, Any]]:
    """Return every object from a paginated Fabric REST value response."""
    rows: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    while url:
        if url in seen_urls:
            raise RuntimeError("Fabric REST pagination returned a repeated continuation URI.")
        seen_urls.add(url)
        payload = request_fabric_json(url, access_token=access_token)
        values = payload.get(collection_key) or []
        if not isinstance(values, list):
            raise RuntimeError("Fabric REST response contains a non-list value.")
        rows.extend(value for value in values if isinstance(value, dict))
        next_url = payload.get("continuationUri")
        url = str(next_url).strip() if next_url else ""
    return rows


def workspace_role_observations(
    *,
    workspace_id: str,
    assignments: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Flatten Fabric workspace role assignments without expanding groups."""
    rows: list[dict[str, str]] = []
    for assignment in assignments:
        principal = assignment.get("principal") or {}
        if not isinstance(principal, dict):
            continue
        principal_id = str(principal.get("id") or "").strip()
        role = str(assignment.get("role") or "").strip()
        if not principal_id or not role:
            continue
        principal_type = normalise_principal_type(principal.get("type"))
        user_details = principal.get("userDetails") or {}
        identity_fields = (
            (user_details.get("userPrincipalName"), principal.get("displayName"), principal_id)
            if principal_type == "USER"
            else (principal.get("displayName"), principal_id)
        )
        principal_name = next(
            (str(value).strip() for value in identity_fields if str(value or "").strip()),
            principal_id,
        )
        normalized_role = role.lower()
        access_value = (
            "READ"
            if normalized_role == "viewer"
            else "READWRITE"
            if normalized_role in {"admin", "member", "contributor"}
            else role.upper()
        )
        rows.append(
            {
                "workspace_id": workspace_id,
                "role_assignment_id": str(assignment.get("id") or ""),
                "principal_id": principal_id,
                "user_principal": principal_name,
                "user_type": principal_type,
                "role_name": role,
                "access_value": access_value,
                "access_state": "GRANT",
                "permission_source": "WORKSPACE_ROLE",
            }
        )
    return rows


def onelake_role_observations(
    *,
    target: str,
    workspace_id: str,
    item_id: str,
    roles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Flatten OneLake roles while preserving explicit and virtual principals."""

    def member_rows(role: dict[str, Any]) -> list[dict[str, str]]:
        members = role.get("members") or {}
        member_result: list[dict[str, str]] = []
        for member in members.get("microsoftEntraMembers") or []:
            if not isinstance(member, dict):
                continue
            principal_type = normalise_principal_type(member.get("objectType"))
            principal_id = str(member.get("objectId") or "").strip()
            identity_fields = (
                ("userPrincipalName", "principalName", "displayName", "objectId")
                if principal_type == "USER"
                else ("displayName", "principalName", "objectId")
            )
            principal_name = next(
                (
                    str(member.get(field) or "").strip()
                    for field in identity_fields
                    if str(member.get(field) or "").strip()
                ),
                "",
            )
            if not principal_id and not principal_name:
                continue
            member_result.append(
                {
                    "principal_id": principal_id or principal_name,
                    "user_principal": principal_name or principal_id,
                    "user_type": principal_type,
                    "permission_source": "ONELAKE_ROLE",
                    "membership_detail": str(member.get("tenantId") or ""),
                }
            )
        for member in members.get("fabricItemMembers") or []:
            if not isinstance(member, dict):
                continue
            source_path = str(member.get("sourcePath") or "").strip()
            item_access = sorted(
                {
                    str(value or "").strip()
                    for value in member.get("itemAccess") or []
                    if str(value or "").strip()
                }
            )
            if source_path and item_access:
                permission_set = "+".join(item_access)
                selector = f"fabric-item:{source_path}:{permission_set}"
                member_result.append(
                    {
                        "principal_id": selector,
                        "user_principal": selector,
                        "user_type": "FABRIC_ITEM_MEMBERS",
                        "permission_source": "ONELAKE_ITEM_ACCESS_SELECTOR",
                        "membership_detail": permission_set,
                    }
                )
        return member_result

    observations: list[dict[str, Any]] = []
    for role in roles:
        role_name = str(role.get("name") or "").strip()
        members = member_rows(role)
        for rule in role.get("decisionRules") or []:
            if not isinstance(rule, dict):
                continue
            paths: list[str] = []
            actions: list[str] = []
            for scope in rule.get("permission") or []:
                if not isinstance(scope, dict):
                    continue
                attribute = str(scope.get("attributeName") or "").strip().lower()
                values = [
                    str(value).strip()
                    for value in (scope.get("attributeValueIncludedIn") or [])
                    if str(value).strip()
                ]
                if attribute == "path":
                    paths.extend(values)
                elif attribute == "action":
                    actions.extend(values)
            constraints_json = json.dumps(rule.get("constraints") or {}, sort_keys=True, separators=(",", ":"))
            for member in members:
                for path in paths or ["*"]:
                    for action in actions or ["UNKNOWN"]:
                        observations.append(
                            {
                                "_target": target,
                                "workspace_id": workspace_id,
                                "item_id": item_id,
                                "role_id": str(role.get("id") or ""),
                                "role_name": role_name,
                                "role_kind": str(role.get("kind") or ""),
                                "role_etag": str(role.get("eTag") or ""),
                                **member,
                                "access_state": str(rule.get("effect") or "Permit"),
                                "access_value": action,
                                "path": path,
                                "constraints_json": constraints_json,
                            }
                        )
    return observations


def read_discovered_sql_endpoint_query(
    spark,
    *,
    workspace_id: str,
    item_id: str,
    item_kind: str,
    database_name: str,
    query: str,
):
    """Read a discovered Warehouse or Lakehouse SQL endpoint."""
    store = FabricStore(
        env="discovered",
        workspace_id=workspace_id,
        item_id=item_id,
        kind=item_kind,
    )
    return read_warehouse_synapsesql(
        spark,
        store,
        validate_select_query(query),
        database_name=database_name,
    )


def persist_access_rows(
    access_df,
    *,
    config,
    environment_name: str,
    context: dict[str, Any],
    persist: bool,
) -> None:
    """Append one scanner's normalized observations to METADATA_DATA_ACCESS."""
    if not persist:
        return
    write_lakehouse_table(
        access_df,
        ACCESS_TABLE,
        store="Metadata",
        schema=metadata_table_physical_schema(config, ACCESS_TABLE),
        context={**context, "config": config, "env": environment_name},
        mode="append",
    )


def catalogue_tables(catalogue_df, *, environment_name: str, target_store_kinds: dict[str, str]):
    """Select active Catalogue tables belonging to configured scan targets."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    spark = catalogue_df.sparkSession
    targets = spark.createDataFrame(
        list(target_store_kinds.items()),
        T.StructType(
            [
                T.StructField("_catalogue_target", T.StringType(), False),
                T.StructField("_target_store_type", T.StringType(), False),
            ]
        ),
    )
    canonical_table_id = F.udf(
        lambda store_type, target, schema_name, table_name: build_table_id(
            store_type,
            target,
            None if schema_name is None or not str(schema_name).strip() else schema_name,
            table_name,
        ),
        T.StringType(),
    )

    return (
        catalogue_df.filter(
            (F.lower(F.col("metadata_level")) == F.lit("table"))
            & (F.col("environment_name") == F.lit(environment_name))
            & F.col("is_active")
        )
        .crossJoin(targets)
        .filter(
            (F.lower(F.col("store_type")) == F.col("_target_store_type"))
            & (
                F.col("table_id")
                == canonical_table_id(
                    F.col("store_type"),
                    F.col("_catalogue_target"),
                    F.col("schema_name"),
                    F.col("table_name"),
                )
            )
        )
        .select(
            F.col("table_id").alias("_catalogue_table_id"),
            F.col("_catalogue_target"),
            F.col("schema_name").alias("_catalogue_schema_name"),
            F.col("table_name").alias("_catalogue_table_name"),
        )
        .dropDuplicates(["_catalogue_table_id"])
    )
