"""Owner file for the ``scan_workspace_access`` public access inventory function."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.config.shared import build_table_id, get_store, resolve_fabric_context
from fabricops_kit.io.shared import read_sql_endpoint_query_core


ACCESS_TABLE = "METADATA_DATA_ACCESS"

SQL_ACCESS_QUERY = r"""
WITH direct_permissions AS (
    SELECT
        u.name COLLATE Latin1_General_100_BIN2_UTF8 AS user_name,
        u.type_desc COLLATE Latin1_General_100_BIN2_UTF8 AS user_type,
        CAST(NULL AS VARCHAR(256)) COLLATE Latin1_General_100_BIN2_UTF8 AS role_name,
        'Direct Permission' COLLATE Latin1_General_100_BIN2_UTF8 AS permission_source,
        dp.state_desc COLLATE Latin1_General_100_BIN2_UTF8 AS state_desc,
        dp.permission_name COLLATE Latin1_General_100_BIN2_UTF8 AS permission_name,
        dp.class_desc COLLATE Latin1_General_100_BIN2_UTF8 AS class_desc,
        DB_NAME() COLLATE Latin1_General_100_BIN2_UTF8 AS database_name,
        CASE
            WHEN dp.class_desc = 'SCHEMA' THEN permission_schema.name
            WHEN dp.class_desc = 'OBJECT_OR_COLUMN' THEN object_schema.name
        END COLLATE Latin1_General_100_BIN2_UTF8 AS schema_name,
        CASE
            WHEN dp.class_desc = 'OBJECT_OR_COLUMN' THEN o.name
        END COLLATE Latin1_General_100_BIN2_UTF8 AS object_name,
        CASE
            WHEN dp.class_desc = 'OBJECT_OR_COLUMN' THEN o.type_desc
        END COLLATE Latin1_General_100_BIN2_UTF8 AS object_type
    FROM sys.database_principals u
    INNER JOIN sys.database_permissions dp
        ON dp.grantee_principal_id = u.principal_id
    LEFT JOIN sys.schemas permission_schema
        ON dp.class_desc = 'SCHEMA'
       AND dp.major_id = permission_schema.schema_id
    LEFT JOIN sys.objects o
        ON dp.class_desc = 'OBJECT_OR_COLUMN'
       AND dp.major_id = o.object_id
    LEFT JOIN sys.schemas object_schema
        ON o.schema_id = object_schema.schema_id
    WHERE u.type IN ('S','E','X','G')
),
role_permissions AS (
    SELECT
        u.name COLLATE Latin1_General_100_BIN2_UTF8 AS user_name,
        u.type_desc COLLATE Latin1_General_100_BIN2_UTF8 AS user_type,
        r.name COLLATE Latin1_General_100_BIN2_UTF8 AS role_name,
        'Via Role' COLLATE Latin1_General_100_BIN2_UTF8 AS permission_source,
        dp.state_desc COLLATE Latin1_General_100_BIN2_UTF8 AS state_desc,
        dp.permission_name COLLATE Latin1_General_100_BIN2_UTF8 AS permission_name,
        dp.class_desc COLLATE Latin1_General_100_BIN2_UTF8 AS class_desc,
        DB_NAME() COLLATE Latin1_General_100_BIN2_UTF8 AS database_name,
        CASE
            WHEN dp.class_desc = 'SCHEMA' THEN permission_schema.name
            WHEN dp.class_desc = 'OBJECT_OR_COLUMN' THEN object_schema.name
        END COLLATE Latin1_General_100_BIN2_UTF8 AS schema_name,
        CASE
            WHEN dp.class_desc = 'OBJECT_OR_COLUMN' THEN o.name
        END COLLATE Latin1_General_100_BIN2_UTF8 AS object_name,
        CASE
            WHEN dp.class_desc = 'OBJECT_OR_COLUMN' THEN o.type_desc
        END COLLATE Latin1_General_100_BIN2_UTF8 AS object_type
    FROM sys.database_role_members rm
    INNER JOIN sys.database_principals u
        ON u.principal_id = rm.member_principal_id
    INNER JOIN sys.database_principals r
        ON r.principal_id = rm.role_principal_id
    INNER JOIN sys.database_permissions dp
        ON dp.grantee_principal_id = r.principal_id
    LEFT JOIN sys.schemas permission_schema
        ON dp.class_desc = 'SCHEMA'
       AND dp.major_id = permission_schema.schema_id
    LEFT JOIN sys.objects o
        ON dp.class_desc = 'OBJECT_OR_COLUMN'
       AND dp.major_id = o.object_id
    LEFT JOIN sys.schemas object_schema
        ON o.schema_id = object_schema.schema_id
    WHERE u.type IN ('S','E','X','G')
)
SELECT * FROM direct_permissions
UNION ALL
SELECT * FROM role_permissions
""".strip()


def _normalise_targets(targets: str | list[str] | tuple[str, ...]) -> list[str]:
    values = [targets] if isinstance(targets, str) else list(targets)
    normalised = []
    for value in values:
        target = str(value or "").strip()
        if not target:
            raise ValueError("Workspace access scan targets must be non-empty strings.")
        if target not in normalised:
            normalised.append(target)
    if not normalised:
        raise ValueError("At least one configured physical data item target is required for access scanning.")
    return normalised


def _scan_targets(*, targets: list[str], spark_session, context: dict[str, Any]):
    from pyspark.sql import functions as F

    frames = []
    for target in targets:
        frame = read_sql_endpoint_query_core(
            SQL_ACCESS_QUERY,
            target=target,
            spark_session=spark_session,
            context=context,
        ).withColumn("_target", F.lit(target))
        frames.append(frame)

    result = frames[0]
    for frame in frames[1:]:
        result = result.unionByName(frame)
    return result


def _target_store_kinds(config, environment_name: str, targets: list[str]) -> dict[str, str]:
    """Resolve each configured physical data item target to its store kind."""
    return {
        target: str(get_store(config, environment_name, target).kind).strip().lower()
        for target in targets
    }


def _catalogue_tables(catalogue_df, *, environment_name: str, target_store_kinds: dict[str, str]):
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


def _map_to_catalogue(observations, catalogue_tables):
    from pyspark.sql import functions as F

    observed = observations.alias("observed")
    catalogue = catalogue_tables.alias("catalogue")

    target_match = F.col("observed._target") == F.col("catalogue._catalogue_target")
    object_match = (
        (F.col("observed.class_desc") == F.lit("OBJECT_OR_COLUMN"))
        & (F.lower(F.col("observed.schema_name")) == F.lower(F.col("catalogue._catalogue_schema_name")))
        & (F.lower(F.col("observed.object_name")) == F.lower(F.col("catalogue._catalogue_table_name")))
    )
    schema_match = (
        (F.col("observed.class_desc") == F.lit("SCHEMA"))
        & (F.lower(F.col("observed.schema_name")) == F.lower(F.col("catalogue._catalogue_schema_name")))
    )
    database_match = F.col("observed.class_desc") == F.lit("DATABASE")

    return observed.join(
        catalogue,
        target_match & (object_match | schema_match | database_match),
        "left",
    )


def _access_rows(
    mapped,
    *,
    environment_name: str,
    access_snapshot_id: str,
    audit_fields: dict[str, Any],
):
    from pyspark.sql import functions as F

    access_id = F.sha2(
        F.concat_ws(
            "\u001f",
            F.lit(access_snapshot_id),
            F.col("_catalogue_table_id"),
            F.coalesce(F.col("user_name"), F.lit("")),
            F.coalesce(F.col("role_name"), F.lit("")),
            F.coalesce(F.col("permission_source"), F.lit("")),
            F.coalesce(F.col("state_desc"), F.lit("")),
            F.coalesce(F.col("permission_name"), F.lit("")),
            F.coalesce(F.col("class_desc"), F.lit("")),
            F.coalesce(F.col("_target"), F.lit("")),
        ),
        256,
    )

    result = (
        mapped.filter(F.col("_catalogue_table_id").isNotNull())
        .select(
            access_id.alias("access_id"),
            F.col("user_name").alias("user_principal"),
            F.col("_catalogue_table_id").alias("table_id"),
            F.lit(environment_name).alias("environment_name"),
            F.col("class_desc").alias("access_level"),
            F.col("permission_name").alias("access_value"),
            F.col("state_desc").alias("access_state"),
            F.lit(access_snapshot_id).alias("access_snapshot_id"),
            F.col("user_type"),
            F.col("role_name"),
            F.col("permission_source"),
            F.col("database_name"),
            F.col("schema_name"),
            F.col("object_name"),
            F.col("object_type"),
        )
        .dropDuplicates()
    )

    for field_name, value in audit_fields.items():
        result = result.withColumn(field_name, F.lit(value))

    schema = metadata_table_schema_registry()[ACCESS_TABLE]
    return result.select(*[field.name for field in schema.fields])


def _unmatched_rows(mapped):
    from pyspark.sql import functions as F

    return (
        mapped.filter(F.col("_catalogue_table_id").isNull())
        .select(
            "user_name",
            "user_type",
            "role_name",
            "permission_source",
            "state_desc",
            "permission_name",
            "class_desc",
            "database_name",
            "schema_name",
            "object_name",
            "object_type",
            F.col("_target").alias("target"),
            F.lit("not_registered_in_catalogue").alias("unmatched_reason"),
        )
        .dropDuplicates()
    )


def scan_workspace_access(
    catalogue_df,
    *,
    targets: str | list[str] | tuple[str, ...] = "warehouse",
    environment_name: str | None = None,
    access_snapshot_id: str | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Scan observable SQL permissions for registered governed physical tables.

    The scanner reads SQL permission catalogue views through the existing
    read-only SQL endpoint connector. Each configured Warehouse or Lakehouse SQL
    analytics endpoint target is scanned separately, without dynamic
    ``DECLARE`` / ``EXEC`` SQL.

    Direct permissions and permissions inherited through explicit database
    role membership are returned separately. Object-level permissions map to
    one registered table. Schema-level and database-level permissions expand to
    every active registered physical table in that scope while preserving the
    original SQL permission class in ``access_level``.

    Configured target keys are related to catalogue rows by reconstructing the
    canonical ``table_id`` from the configured item kind, target key, schema,
    and table name. The catalogue ``layer`` classification is not used as a
    physical item identifier.

    Parameters
    ----------
    catalogue_df : pyspark.sql.DataFrame
        ``METADATA_DATA_CATALOGUE`` rows used to resolve observed SQL objects to
        canonical FabricOps ``table_id`` values.
    targets : str | list[str] | tuple[str, ...], default="warehouse"
        One or more configured Warehouse or Lakehouse target keys from
        ``00_env_config`` whose SQL endpoints expose the supported catalogue
        views.
    environment_name : str, optional
        Metadata environment to scan. Defaults to the active FabricOps
        environment.
    access_snapshot_id : str, optional
        Identifier shared by all rows in this scan. A UUID is generated when
        omitted.
    spark_session : object, optional
        Spark session override used by the Fabric SQL connector.
    context : dict[str, Any], optional
        Active FabricOps context override.

    Returns
    -------
    dict[str, pyspark.sql.DataFrame]
        ``access`` contains rows aligned to ``METADATA_DATA_ACCESS`` and ready
        for persistence. ``unmatched`` contains observed permissions that could
        not be linked to an active registered physical table, so observations
        are never silently discarded.

    Notes
    -----
    This scans observable SQL permissions only; it is not a complete workspace
    security inventory. Workspace roles, item sharing, OneLake Security, and
    Power BI security are outside this scanner's scope. The function returns
    DataFrames and never persists or changes permissions.

    Examples
    --------
    >>> result = scan_workspace_access(
    ...     catalogue_df,
    ...     targets=["warehouse", "curated_lakehouse"],
    ...     spark_session=spark,
    ... )
    >>> result["access"].display()
    >>> result["unmatched"].display()

    """
    config, active_env, resolved_context = resolve_fabric_context(context=context)
    resolved_environment = str(environment_name or active_env)
    resolved_targets = _normalise_targets(targets)
    target_store_kinds = _target_store_kinds(config, resolved_environment, resolved_targets)
    snapshot_id = str(access_snapshot_id or uuid4())

    observations = _scan_targets(
        targets=resolved_targets,
        spark_session=spark_session,
        context=resolved_context,
    )
    catalogue_tables = _catalogue_tables(
        catalogue_df,
        environment_name=resolved_environment,
        target_store_kinds=target_store_kinds,
    )
    mapped = _map_to_catalogue(observations, catalogue_tables)
    audit_fields = build_runtime_audit_fields(
        config=config,
        env=active_env,
        runtime_context=resolved_context,
    )

    return {
        "access": _access_rows(
            mapped,
            environment_name=resolved_environment,
            access_snapshot_id=snapshot_id,
            audit_fields=audit_fields,
        ),
        "unmatched": _unmatched_rows(mapped),
    }
