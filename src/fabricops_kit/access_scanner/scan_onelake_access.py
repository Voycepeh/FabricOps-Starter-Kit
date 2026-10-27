"""OneLake Security role scanner for governed Lakehouse tables."""

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
    onelake_role_observations,
    persist_access_rows,
    target_store_kinds,
)
from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.config.shared import get_store, resolve_fabric_context


def _list_data_access_roles(*, workspace_id: str, item_id: str, access_token: str) -> list[dict[str, Any]]:
    """Return all OneLake data access roles for one Fabric item."""
    return list_fabric_pages(
        f"{FABRIC_API_ROOT}/workspaces/{workspace_id}/items/{item_id}/dataAccessRoles",
        access_token=access_token,
    )


def _observations_df(spark, rows: list[dict[str, Any]]):
    """Create a stable Spark DataFrame for flattened OneLake observations."""
    from pyspark.sql import types as T

    fields = [
        "_target",
        "workspace_id",
        "item_id",
        "role_id",
        "role_name",
        "role_kind",
        "role_etag",
        "user_principal",
        "user_type",
        "permission_source",
        "membership_detail",
        "access_state",
        "access_value",
        "path",
        "constraints_json",
    ]
    schema = T.StructType([T.StructField(name, T.StringType(), True) for name in fields])
    return spark.createDataFrame([tuple(row.get(name) for name in fields) for row in rows], schema)


def _map_to_catalogue(observations, registered_tables):
    """Relate OneLake table paths to canonical FabricOps table identities."""
    from pyspark.sql import functions as F

    observed = observations.alias("observed")
    catalogue = registered_tables.alias("catalogue")
    schema_name = F.coalesce(F.col("catalogue._catalogue_schema_name"), F.lit(""))
    table_name = F.col("catalogue._catalogue_table_name")
    table_path = F.when(
        F.length(F.trim(schema_name)) > 0,
        F.concat_ws("/", F.lit("Tables"), schema_name, table_name),
    ).otherwise(F.concat_ws("/", F.lit("Tables"), table_name))
    normalized_path = F.lower(F.regexp_replace(F.col("observed.path"), r"^/+", ""))
    normalized_table_path = F.lower(table_path)
    normalized_schema_scope = F.lower(F.concat_ws("/", F.lit("Tables"), schema_name, F.lit("*")))
    path_match = (
        normalized_path.isin("*", "tables", "tables/*")
        | (normalized_path == normalized_table_path)
        | ((F.length(F.trim(schema_name)) > 0) & (normalized_path == normalized_schema_scope))
    )
    return observed.join(
        catalogue,
        (F.col("observed._target") == F.col("catalogue._catalogue_target")) & path_match,
        "left",
    )


def _access_rows(mapped, *, workspace_id: str, access_snapshot_id: str, audit_fields: dict[str, Any]):
    """Project matched OneLake observations into METADATA_DATA_ACCESS."""
    from pyspark.sql import functions as F

    access_id = F.sha2(
        F.concat_ws(
            "\u001f",
            F.lit(access_snapshot_id),
            F.col("_catalogue_table_id"),
            F.coalesce(F.col("user_principal"), F.lit("")),
            F.coalesce(F.col("role_name"), F.lit("")),
            F.coalesce(F.col("access_state"), F.lit("")),
            F.coalesce(F.col("access_value"), F.lit("")),
            F.coalesce(F.col("path"), F.lit("")),
            F.coalesce(F.col("_target"), F.lit("")),
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
            F.lit("ONELAKE_PATH").alias("access_level"),
            "access_value",
            "access_state",
            F.lit(access_snapshot_id).alias("access_snapshot_id"),
            "user_type",
            "role_name",
            "permission_source",
            F.col("item_id").alias("database_name"),
            F.col("_catalogue_schema_name").alias("schema_name"),
            F.col("_catalogue_table_name").alias("object_name"),
            F.lit("ONELAKE_TABLE").alias("object_type"),
        )
        .dropDuplicates()
    )
    for field_name, value in audit_fields.items():
        result = result.withColumn(field_name, F.lit(value))
    schema = metadata_table_schema_registry()[ACCESS_TABLE]
    return result.select(*[field.name for field in schema.fields])


def _unmatched_rows(mapped):
    """Keep role observations that do not map to a registered governed table."""
    from pyspark.sql import functions as F

    path = F.lower(F.regexp_replace(F.col("path"), r"^/+", ""))
    return (
        mapped.filter(F.col("_catalogue_table_id").isNull())
        .select(
            "user_principal",
            "user_type",
            "role_name",
            "permission_source",
            "access_state",
            "access_value",
            "path",
            "workspace_id",
            "item_id",
            "constraints_json",
            F.col("_target").alias("target"),
            F.when(path.startswith("files"), F.lit("files_path_not_table"))
            .otherwise(F.lit("not_registered_in_catalogue"))
            .alias("unmatched_reason"),
        )
        .dropDuplicates()
    )


def scan_onelake_access(
    catalogue_df,
    *,
    targets: str | list[str] | tuple[str, ...],
    workspace_id: str | None = None,
    access_snapshot_id: str | None = None,
    access_token: str | None = None,
    persist: bool = True,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Scan OneLake Security roles and map table access to FabricOps table IDs.

    The scanner reads the Fabric dataAccessRoles REST endpoint for each configured
    Lakehouse target. Explicit Entra members use a UPN or readable identity when
    the response provides one and otherwise retain the Entra object ID. Groups
    remain groups and are not expanded. Automatic Fabric item membership used by
    roles such as DefaultReader is preserved as a selector instead of being
    misrepresented as an individual user. No Microsoft Graph lookup is performed.

    Normalized access rows are appended to METADATA_DATA_ACCESS by default.
    Pass persist=False for an inspection-only scan. The scanner never changes
    OneLake permissions.

    Parameters
    ----------
    catalogue_df : pyspark.sql.DataFrame
        Active Data Catalogue rows for the configured workspace_id. Its Spark
        session is used for mapping and persistence.
    targets : str or list[str] or tuple[str, ...]
        Configured Lakehouse keys whose permissions should be inventoried.
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
        If targets are empty, invalid, or not Lakehouses. Check configured store keys.
    RuntimeError
        If Fabric authentication, REST discovery, or safe pagination fails.
        Spark mapping and metadata write errors also propagate; check Catalogue
        columns and permissions on the configured metadata target.

    Examples
    --------
    >>> result = scan_onelake_access(catalogue_df, targets="Silver", persist=False)
    >>> display(result["access"])
    >>> display(result["unmatched"])

    """
    config, active_workspace_id, runtime_context = resolve_fabric_context(context=context)
    resolved_workspace_id = str(active_workspace_id if workspace_id is None else workspace_id)
    scan_context = {**runtime_context, "config": config, "scope_workspace_id": resolved_workspace_id}
    resolved_targets = normalise_targets(targets)
    resolved_store_kinds = target_store_kinds(config, resolved_workspace_id, resolved_targets)
    unsupported = [target for target, kind in resolved_store_kinds.items() if kind != "lakehouse"]
    if unsupported:
        raise ValueError(
            "OneLake access scanning currently supports configured Lakehouse targets only: "
            + ", ".join(unsupported)
        )

    token = fabric_access_token(access_token)
    rows: list[dict[str, Any]] = []
    for target in resolved_targets:
        store = get_store(config, resolved_workspace_id, target)
        roles = _list_data_access_roles(
            workspace_id=store.workspace_id,
            item_id=store.item_id,
            access_token=token,
        )
        rows.extend(
            onelake_role_observations(
                target=target,
                workspace_id=store.workspace_id,
                item_id=store.item_id,
                roles=roles,
            )
        )

    observations = _observations_df(catalogue_df.sparkSession, rows)
    registered_tables = catalogue_tables(
        catalogue_df,
        workspace_id=resolved_workspace_id,
        target_store_kinds=resolved_store_kinds,
    )
    mapped = _map_to_catalogue(observations, registered_tables)
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
