"""Workspace-role access scanner for governed Fabric tables."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fabricops_kit.access_scanner.shared import (
    ACCESS_TABLE,
    FABRIC_API_ROOT,
    catalogue_tables,
    fabric_access_token,
    list_fabric_pages,
    normalise_targets,
    persist_access_rows,
    target_store_kinds,
)
from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.config.shared import get_store, resolve_fabric_context


def _list_workspace_role_assignments(*, workspace_id: str, access_token: str) -> list[dict[str, Any]]:
    """Return all role assignments for one Fabric workspace."""
    return list_fabric_pages(
        f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/roleAssignments",
        access_token=access_token,
    )


def _principal_name(principal: dict[str, Any]) -> str:
    """Return the most useful stable principal label exposed by the workspace API."""
    user_details = principal.get("userDetails") or {}
    return str(
        user_details.get("userPrincipalName")
        or principal.get("displayName")
        or principal.get("id")
        or ""
    ).strip()


def _role_access_value(role: str) -> str:
    """Normalize a workspace role to the table-data capability it implies."""
    normalized = str(role or "").strip().lower()
    if normalized == "viewer":
        return "READ"
    if normalized in {"admin", "member", "contributor"}:
        return "READWRITE"
    return str(role or "UNKNOWN").strip().upper() or "UNKNOWN"


def _workspace_observations(
    *,
    workspace_id: str,
    assignments: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Flatten workspace role assignments to normalized access observations."""
    rows: list[dict[str, str]] = []
    for assignment in assignments:
        principal = assignment.get("principal") or {}
        if not isinstance(principal, dict):
            continue
        principal_id = str(principal.get("id") or "").strip()
        role = str(assignment.get("role") or "").strip()
        if not principal_id or not role:
            continue
        rows.append(
            {
                "workspace_id": workspace_id,
                "role_assignment_id": str(assignment.get("id") or ""),
                "principal_id": principal_id,
                "user_principal": _principal_name(principal) or principal_id,
                "user_type": str(principal.get("type") or "UNKNOWN").upper(),
                "role_name": role,
                "access_value": _role_access_value(role),
                "access_state": "GRANT",
                "permission_source": "WORKSPACE_ROLE",
            }
        )
    return rows


def _observations_df(spark, rows: list[dict[str, str]]):
    """Create a stable Spark DataFrame for workspace role observations."""
    from pyspark.sql import types as T

    fields = [
        "workspace_id",
        "role_assignment_id",
        "principal_id",
        "user_principal",
        "user_type",
        "role_name",
        "access_value",
        "access_state",
        "permission_source",
    ]
    schema = T.StructType([T.StructField(name, T.StringType(), True) for name in fields])
    return spark.createDataFrame([tuple(row.get(name) for name in fields) for row in rows], schema)


def _target_workspaces_df(spark, *, config, environment_name: str, targets: list[str]):
    """Return configured target-to-workspace mappings for the scan."""
    from pyspark.sql import types as T

    rows = [
        (target, get_store(config, environment_name, target).workspace_id)
        for target in targets
    ]
    schema = T.StructType(
        [
            T.StructField("_catalogue_target", T.StringType(), False),
            T.StructField("_target_workspace_id", T.StringType(), False),
        ]
    )
    return spark.createDataFrame(rows, schema)


def _map_to_catalogue(observations, registered_tables, target_workspaces):
    """Expand workspace roles across registered tables in the same workspace."""
    tables = registered_tables.join(target_workspaces, "_catalogue_target", "inner").alias("tables")
    observed = observations.alias("observed")
    return observed.join(
        tables,
        observed["workspace_id"] == tables["_target_workspace_id"],
        "left",
    )


def _access_rows(mapped, *, environment_name: str, access_snapshot_id: str, audit_fields: dict[str, Any]):
    """Project workspace access observations into METADATA_DATA_ACCESS."""
    from pyspark.sql import functions as F

    access_id = F.sha2(
        F.concat_ws(
            "\u001f",
            F.lit(access_snapshot_id),
            F.col("_catalogue_table_id"),
            F.col("principal_id"),
            F.col("role_name"),
            F.col("workspace_id"),
        ),
        256,
    )
    result = (
        mapped.filter(F.col("_catalogue_table_id").isNotNull())
        .select(
            access_id.alias("access_id"),
            "user_principal",
            F.col("_catalogue_table_id").alias("table_id"),
            F.lit(environment_name).alias("environment_name"),
            F.lit("WORKSPACE").alias("access_level"),
            "access_value",
            "access_state",
            F.lit(access_snapshot_id).alias("access_snapshot_id"),
            "user_type",
            "role_name",
            "permission_source",
            F.col("workspace_id").alias("database_name"),
            F.col("_catalogue_schema_name").alias("schema_name"),
            F.col("_catalogue_table_name").alias("object_name"),
            F.lit("WORKSPACE_INHERITED_TABLE").alias("object_type"),
        )
        .dropDuplicates()
    )
    for field_name, value in audit_fields.items():
        result = result.withColumn(field_name, F.lit(value))
    schema = metadata_table_schema_registry()[ACCESS_TABLE]
    return result.select(*[field.name for field in schema.fields])


def _unmatched_rows(mapped):
    """Keep workspace assignments that did not map to a registered table."""
    from pyspark.sql import functions as F

    return (
        mapped.filter(F.col("_catalogue_table_id").isNull())
        .select(
            "workspace_id",
            "role_assignment_id",
            "principal_id",
            "user_principal",
            "user_type",
            "role_name",
            "access_value",
            "access_state",
            "permission_source",
            F.lit("no_registered_table_in_scanned_workspace").alias("unmatched_reason"),
        )
        .dropDuplicates()
    )


def scan_workspace_access(
    catalogue_df,
    *,
    targets: str | list[str] | tuple[str, ...],
    environment_name: str | None = None,
    access_snapshot_id: str | None = None,
    access_token: str | None = None,
    persist: bool = True,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Scan workspace roles and expand their data access across governed tables.

    The scanner reads Fabric workspace role assignments for the workspaces that
    contain the configured targets. Each unique workspace is scanned once.
    Viewer is normalized to READ, while Admin, Member, and Contributor are
    normalized to READWRITE. The original workspace role is retained in
    role_name.

    Rows are appended to METADATA_DATA_ACCESS by default. Pass persist=False to
    inspect the result without writing metadata.
    """
    config, active_env, runtime_context = resolve_fabric_context(context=context)
    resolved_environment = str(active_env if environment_name is None else environment_name)
    scan_context = {**runtime_context, "config": config, "env": resolved_environment}
    resolved_targets = normalise_targets(targets)
    resolved_store_kinds = target_store_kinds(config, resolved_environment, resolved_targets)
    token = fabric_access_token(access_token)

    stores = {
        target: get_store(config, resolved_environment, target)
        for target in resolved_targets
    }
    unique_workspace_ids = list(dict.fromkeys(store.workspace_id for store in stores.values()))
    rows: list[dict[str, str]] = []
    for workspace_id in unique_workspace_ids:
        rows.extend(
            _workspace_observations(
                workspace_id=workspace_id,
                assignments=_list_workspace_role_assignments(
                    workspace_id=workspace_id,
                    access_token=token,
                ),
            )
        )

    spark = catalogue_df.sparkSession
    observations = _observations_df(spark, rows)
    registered_tables = catalogue_tables(
        catalogue_df,
        environment_name=resolved_environment,
        target_store_kinds=resolved_store_kinds,
    )
    target_workspaces = _target_workspaces_df(
        spark,
        config=config,
        environment_name=resolved_environment,
        targets=resolved_targets,
    )
    mapped = _map_to_catalogue(observations, registered_tables, target_workspaces)
    snapshot_id = str(access_snapshot_id or uuid4())
    audit_fields = build_runtime_audit_fields(
        config=config,
        env=resolved_environment,
        runtime_context=scan_context,
    )
    access = _access_rows(
        mapped,
        environment_name=resolved_environment,
        access_snapshot_id=snapshot_id,
        audit_fields=audit_fields,
    )
    persist_access_rows(
        access,
        config=config,
        environment_name=resolved_environment,
        context=scan_context,
        persist=persist,
    )
    return {
        "observations": observations,
        "access": access,
        "unmatched": _unmatched_rows(mapped),
    }
