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
    normalise_principal_type,
    normalise_targets,
    persist_access_rows,
    target_store_kinds,
    workspace_role_observations,
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


def _target_workspaces_df(spark, *, config, workspace_id: str, targets: list[str]):
    """Return configured target-to-workspace mappings for the scan."""
    from pyspark.sql import types as T

    rows = [
        (target, get_store(config, workspace_id, target).workspace_id)
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


def _access_rows(mapped, *, workspace_id: str, access_snapshot_id: str, audit_fields: dict[str, Any]):
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
            F.col("_catalogue_table_name").alias("table_name"),
            F.lit(workspace_id).alias("workspace_id"),
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
    workspace_id: str | None = None,
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
    role_name. Users use the UPN exposed by Fabric; groups and other principal
    types remain separate records and are not expanded into members.

    Rows are appended to METADATA_DATA_ACCESS by default. Pass persist=False to
    inspect the result without writing metadata.

    Parameters
    ----------
    catalogue_df : pyspark.sql.DataFrame
        Active Data Catalogue rows for the configured workspace_id. Its Spark
        session is used for mapping and persistence.
    targets : str or list[str] or tuple[str, ...]
        Configured Fabric store keys whose permissions should be inventoried.
    workspace_id : str, optional
        Catalogue and configured-store workspace_id; defaults to the active workspace_id.
    access_snapshot_id : str, optional
        Shared scan identifier; a new UUID is generated when omitted.
    access_token : str, optional
        Fabric API token override; normally resolved from the notebook identity.
    persist : bool, default=True
        Append normalized rows to METADATA_DATA_ACCESS. Use False to inspect only.
    context : dict[str, Any], optional
        FabricOps configuration and runtime context established by 00_env_config.

    Returns
    -------
    dict[str, pyspark.sql.DataFrame]
        ``observations`` holds raw permission observations; ``access`` holds
        normalized METADATA_DATA_ACCESS rows; ``unmatched`` holds observations
        that could not be linked to registered tables. Review unmatched rows
        before interpreting missing access as absence of permission.

    Raises
    ------
    ValueError
        If targets are empty, invalid. Check configured store keys.
    RuntimeError
        If Fabric authentication, REST discovery, or safe pagination fails.
        Spark mapping and metadata write errors also propagate; check Catalogue
        columns and permissions on the configured metadata target.

    Examples
    --------
    >>> result = scan_workspace_access(catalogue_df, targets="Silver", persist=False)
    >>> display(result["access"])
    >>> display(result["unmatched"])

    """
    config, active_workspace_id, runtime_context = resolve_fabric_context(context=context)
    resolved_workspace_id = str(active_workspace_id if workspace_id is None else workspace_id)
    scan_context = {**runtime_context, "config": config, "scope_workspace_id": resolved_workspace_id}
    resolved_targets = normalise_targets(targets)
    resolved_store_kinds = target_store_kinds(config, resolved_workspace_id, resolved_targets)
    token = fabric_access_token(access_token)

    stores = {
        target: get_store(config, resolved_workspace_id, target)
        for target in resolved_targets
    }
    unique_workspace_ids = list(dict.fromkeys(store.workspace_id for store in stores.values()))
    rows: list[dict[str, str]] = []
    for workspace_id in unique_workspace_ids:
        rows.extend(
            workspace_role_observations(
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
        workspace_id=resolved_workspace_id,
        target_store_kinds=resolved_store_kinds,
    )
    target_workspaces = _target_workspaces_df(
        spark,
        config=config,
        workspace_id=resolved_workspace_id,
        targets=resolved_targets,
    )
    mapped = _map_to_catalogue(observations, registered_tables, target_workspaces)
    snapshot_id = str(access_snapshot_id or uuid4())
    audit_fields = build_runtime_audit_fields(
        config=config,
        active_workspace_id=resolved_workspace_id,
        runtime_context=scan_context,
    )
    access = _access_rows(
        mapped,
        workspace_id=resolved_workspace_id,
        access_snapshot_id=snapshot_id,
        audit_fields=audit_fields,
    )
    persist_access_rows(
        access,
        config=config,
        workspace_id=resolved_workspace_id,
        context=scan_context,
        persist=persist,
    )
    return {
        "observations": observations,
        "access": access,
        "unmatched": _unmatched_rows(mapped),
    }
