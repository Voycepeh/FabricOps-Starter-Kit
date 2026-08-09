"""Public notebook-facing DataFrame profile registration callable."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Sequence

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import (
    build_metadata_column_key,
    build_metadata_table_key,
    get_store,
    resolve_fabric_context,
)
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    resolve_configured_lakehouse_table,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.shared import build_frequency_distribution_dataframe, build_profile_dataframe

PROFILED_TABLE = "METADATA_DATA_PROFILED"
PROFILED_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
PROFILED_COLUMNS = metadata_table_schema_registry()[PROFILED_TABLE].fieldNames()
PROFILED_FREQUENCY_COLUMNS = metadata_table_schema_registry()[PROFILED_FREQUENCY_TABLE].fieldNames()
CATALOGUE_COLUMNS = metadata_table_schema_registry()[CATALOGUE_TABLE].fieldNames()


def _require_non_empty_string(value: Any, name: str) -> str:
    """Return a stripped required string or raise a clear validation error."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _normalize_choice(value: Any, name: str, allowed: set[str]) -> str:
    """Return a normalized allowed choice or raise a clear validation error."""
    normalized = _require_non_empty_string(value, name).lower()
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {choices}.")
    return normalized


def _schema_fingerprint(df: Any) -> str:
    """Return an environment-independent fingerprint of ordered schema content."""
    fields = [
        {"name": str(field.name).strip(), "type": field.dataType.simpleString()}
        for field in getattr(getattr(df, "schema", None), "fields", [])
    ]
    payload = {"fields": fields}
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def _resolve_physical_identity(*, profile_role: Any, target: Any, schema: Any, table_name: Any):
    """Resolve and validate one configured physical table identity."""
    normalized_role = _normalize_choice(profile_role, "profile_role", {"source", "target"})
    normalized_target = _require_non_empty_string(target, "target").lower()
    normalized_table = _require_non_empty_string(table_name, "table_name")
    config, env, context = resolve_fabric_context()
    store = get_store(config, env, normalized_target)
    store_kind = str(getattr(store, "kind", "")).strip().lower()

    if store_kind == "lakehouse":
        if getattr(store, "schema_enabled", False) and schema is None and not getattr(store, "schema", None):
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
        normalized_table, normalized_schema, _path = resolve_lakehouse_table_location(store, normalized_table, schema)
        if getattr(store, "schema_enabled", False) and normalized_schema is None:
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
    elif store_kind == "warehouse":
        configured_schema = schema if schema is not None else getattr(store, "schema", None)
        if configured_schema is None or not str(configured_schema).strip():
            raise ValueError(
                f"schema is required for Warehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
        normalized_schema, normalized_table, _object_name = resolve_warehouse_table_location(
            store, configured_schema, normalized_table
        )
    else:
        raise ValueError(
            f"Target '{normalized_target}' has unsupported store kind {store_kind or '<blank>'!r}; "
            "supported kinds are: lakehouse, warehouse."
        )

    return normalized_role, normalized_target, normalized_table, normalized_schema, store_kind, config, env, context


def _lineage_event_id(*, activity_id: str, metadata_table_key: str, schema_fingerprint: str, profile_role: str) -> str:
    """Return the deterministic runtime lineage event identity."""
    payload = {
        "activity_id": _require_non_empty_string(activity_id, "activity_id"),
        "metadata_table_key": _require_non_empty_string(metadata_table_key, "metadata_table_key"),
        "schema_fingerprint": _require_non_empty_string(schema_fingerprint, "schema_fingerprint"),
        "profile_role": _normalize_choice(profile_role, "profile_role", {"source", "target"}),
    }
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def _validate_frequency_profile_dataframe(source_df, frequency_profile_df, selected_columns: Sequence[str]):
    """Return the frequency DataFrame after validating caller-provided scope."""
    if frequency_profile_df is None:
        return source_df, "full_source"

    source_session = getattr(source_df, "sparkSession", None)
    frequency_session = getattr(frequency_profile_df, "sparkSession", None)
    if source_session is not None and frequency_session is not None and source_session is not frequency_session:
        raise ValueError("frequency_profile_df must use the same Spark session as df.")

    fields = getattr(getattr(frequency_profile_df, "schema", None), "fields", None)
    if fields is None:
        raise ValueError("frequency_profile_df must be a Spark DataFrame-like object with a schema.")

    available_columns = {field.name for field in fields}
    missing_columns = [column for column in selected_columns if column not in available_columns]
    if missing_columns:
        raise ValueError(f"frequency_profile_df is missing selected frequency columns: {', '.join(missing_columns)}")

    return frequency_profile_df, "caller_provided"


def _scalar_frequency_columns(df, candidate_columns: Sequence[str]) -> list[str]:
    """Return candidate columns whose Spark types are scalar frequency types."""
    from pyspark.sql.types import ArrayType, BinaryType, MapType, StructType

    fields = {field.name: field for field in df.schema.fields}
    return [
        name
        for name in candidate_columns
        if name in fields and not isinstance(fields[name].dataType, ArrayType | MapType | StructType | BinaryType)
    ]


def _automatic_frequency_columns(
    profile_df, *, scalar_columns: Sequence[str], threshold_percent: float | None
) -> list[str]:
    """Return automatic scalar columns that pass the frequency cardinality guard."""
    from pyspark.sql import functions as F

    non_null_count = F.col("NON_NULL_COUNT").cast("double")
    distinct_count = F.col("DISTINCT_COUNT").cast("double")
    raw_cardinality_percent = (distinct_count / non_null_count) * 100
    eligible = profile_df.where(F.col("COLUMN_NAME").isin(list(scalar_columns))).where(
        F.col("NON_NULL_COUNT").cast("long") > 0
    )
    if threshold_percent is not None:
        eligible = eligible.where(raw_cardinality_percent <= F.lit(float(threshold_percent)))
    return [row.COLUMN_NAME for row in eligible.select("COLUMN_NAME").collect()]


def _selected_frequency_columns(
    source_df, profile_df, frequency_columns: Sequence[str] | None, threshold_percent: float | None
) -> list[str]:
    """Return explicitly requested or automatically eligible frequency columns."""
    if frequency_columns is not None:
        return list(frequency_columns)
    profiled_columns = [row.COLUMN_NAME for row in profile_df.select("COLUMN_NAME").collect()]
    scalar_columns = _scalar_frequency_columns(source_df, profiled_columns)
    return _automatic_frequency_columns(
        profile_df, scalar_columns=scalar_columns, threshold_percent=threshold_percent
    )


def _frequency_metadata_dataframe(
    frequency_df, *, profiled_df, config: Any, env: str, runtime_context: dict[str, Any]
):
    """Map authoritative flattened frequency output to its canonical child schema."""
    from pyspark.sql import functions as F

    identities = profiled_df.select(
        F.col("column_name").alias("_column_name"),
        F.col("data_type").alias("_data_type"),
        "metadata_column_key",
        "profiled_at",
    )
    audit_columns = _audit_literal_columns(config=config, env=env, runtime_context=runtime_context)
    joined = frequency_df.join(
        identities,
        (frequency_df.COLUMN_NAME == identities._column_name)
        & (frequency_df.DATA_TYPE == identities._data_type),
        "inner",
    )
    return joined.select(
        F.col("metadata_column_key").cast("string"),
        F.col("VALUE").cast("string").alias("value"),
        F.col("FREQUENCY_COUNT").cast("long").alias("frequency_count"),
        F.col("FREQUENCY_PERCENT").cast("double").alias("frequency_percent"),
        F.col("FREQUENCY_RANK").cast("integer").alias("frequency_rank"),
        F.col("PROFILED_ROW_COUNT").cast("long").alias("profiled_row_count"),
        F.col("PROFILED_NON_NULL_COUNT").cast("long").alias("profiled_non_null_count"),
        F.col("profiled_at").cast("timestamp"),
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_FREQUENCY_COLUMNS)


def _replace_frequency_rows(
    *, frequency_df: Any | None, profiled_df: Any, config: Any, env: str, spark_session: Any
) -> None:
    """Replace child rows only for the exact parent column snapshot identities."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake support is required for replacement METADATA_DATA_PROFILED_FREQUENCY writes."
        ) from exc

    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        PROFILED_FREQUENCY_TABLE,
        configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
    )
    snapshots = profiled_df.select("metadata_column_key", "profiled_at").dropDuplicates()
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(
            snapshots.alias("source"),
            "target.metadata_column_key = source.metadata_column_key "
            "AND target.profiled_at = source.profiled_at",
        )
        .whenMatchedDelete()
        .execute()
    )
    if frequency_df is None:
        return
    write_lakehouse_table_core(
        frequency_df,
        PROFILED_FREQUENCY_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )


def _audit_literal_columns(*, config: Any, env: str, runtime_context: dict[str, Any]) -> dict[str, Any]:
    """Return Spark literals for the canonical runtime audit field set."""
    from pyspark.sql import functions as F

    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
    return {
        "_committed_by": F.lit(audit["_committed_by"]).cast("string"),
        "_committed_at": F.lit(audit["_committed_at"]).cast("timestamp"),
        "_workspace_id": F.lit(audit["_workspace_id"]).cast("string"),
        "_workspace_name": F.lit(audit["_workspace_name"]).cast("string"),
        "_notebook_id": F.lit(audit["_notebook_id"]).cast("string"),
        "_notebook_name": F.lit(audit["_notebook_name"]).cast("string"),
        "_metadata_lakehouse_name": F.lit(audit["_metadata_lakehouse_name"]).cast("string"),
        "_activity_id": F.lit(audit["_activity_id"]).cast("string"),
    }


def _canonical_profiled_dataframe(
    profile_df,
    *,
    source_df,
    config: Any,
    env: str,
    runtime_context: dict[str, Any],
    environment_name: str,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
):
    """Return profile rows mapped to the detailed profiled schema."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    metadata_table_key = build_metadata_table_key(store_type, layer, schema_name, table_name)
    column_key_udf = F.udf(
        lambda column_name: build_metadata_column_key(metadata_table_key, column_name), T.StringType()
    )
    schema_fingerprint = _schema_fingerprint(source_df)
    audit_columns = _audit_literal_columns(config=config, env=env, runtime_context=runtime_context)

    profiled_df = profile_df.select(
        F.col("COLUMN_NAME").alias("column_name"),
        F.col("DATA_TYPE").alias("data_type"),
        F.col("ROW_COUNT").cast("long").alias("row_count"),
        F.col("NON_NULL_COUNT").cast("long").alias("non_null_count"),
        F.col("NULL_COUNT").cast("long").alias("null_count"),
        F.col("NULL_PERCENT").cast("double").alias("null_percent"),
        F.col("DISTINCT_COUNT").cast("long").alias("distinct_count"),
        F.col("DISTINCT_PERCENT").cast("double").alias("distinct_percent"),
        F.col("MEAN").cast("double").alias("mean_value"),
        F.col("STDDEV").cast("double").alias("stddev_value"),
        F.col("MIN_VALUE").cast("string").alias("min_value"),
        F.col("PERCENTILE_25").cast("double").alias("percentile_25_value"),
        F.col("MEDIAN").cast("double").alias("median_value"),
        F.col("PERCENTILE_75").cast("double").alias("percentile_75_value"),
        F.col("MAX_VALUE").cast("string").alias("max_value"),
    )

    return profiled_df.select(
        F.lit(metadata_table_key).cast("string").alias("metadata_table_key"),
        column_key_udf(F.col("column_name")).alias("metadata_column_key"),
        F.lit(environment_name).cast("string").alias("environment_name"),
        F.lit(store_type).cast("string").alias("store_type"),
        F.lit(layer).cast("string").alias("layer"),
        F.lit(schema_name).cast("string").alias("schema_name"),
        F.lit(table_name).cast("string").alias("table_name"),
        F.col("column_name").cast("string"),
        F.col("data_type").cast("string"),
        F.col("row_count"),
        F.col("non_null_count"),
        F.col("null_count"),
        F.col("null_percent"),
        F.col("distinct_count"),
        F.col("distinct_percent"),
        F.col("mean_value"),
        F.col("stddev_value"),
        F.col("min_value"),
        F.col("percentile_25_value"),
        F.col("median_value"),
        F.col("percentile_75_value"),
        F.col("max_value"),
        F.lit(schema_fingerprint).cast("string").alias("schema_fingerprint"),
        audit_columns["_committed_at"].alias("profiled_at"),
        audit_columns["_committed_by"].alias("_committed_by"),
        audit_columns["_committed_at"].alias("_committed_at"),
        audit_columns["_workspace_id"].alias("_workspace_id"),
        audit_columns["_workspace_name"].alias("_workspace_name"),
        audit_columns["_notebook_id"].alias("_notebook_id"),
        audit_columns["_notebook_name"].alias("_notebook_name"),
        audit_columns["_metadata_lakehouse_name"].alias("_metadata_lakehouse_name"),
        audit_columns["_activity_id"].alias("_activity_id"),
    ).select(*PROFILED_COLUMNS)


def _catalogue_dataframe_from_profiled(profiled_df):
    """Return distinct catalogue identity rows derived from detailed profiled rows."""
    from pyspark.sql import functions as F

    return (
        profiled_df.select(
            F.col("metadata_table_key").cast("string"),
            F.col("metadata_column_key").cast("string"),
            F.col("schema_fingerprint").cast("string"),
            F.col("environment_name").cast("string"),
            F.col("store_type").cast("string"),
            F.col("layer").cast("string"),
            F.col("schema_name").cast("string"),
            F.col("table_name").cast("string"),
            F.col("column_name").cast("string"),
            F.col("data_type").cast("string"),
            F.col("_committed_by").cast("string"),
            F.col("_committed_at").cast("timestamp"),
            F.col("_workspace_id").cast("string"),
            F.col("_workspace_name").cast("string"),
            F.col("_notebook_id").cast("string"),
            F.col("_notebook_name").cast("string"),
            F.col("_metadata_lakehouse_name").cast("string"),
            F.col("_activity_id").cast("string"),
        )
        .dropDuplicates(["environment_name", "metadata_table_key", "metadata_column_key", "schema_fingerprint"])
        .select(*CATALOGUE_COLUMNS)
    )


def _write_lineage_participation(
    *,
    metadata_table_key: str,
    schema_fingerprint: str,
    profile_role: str,
    profiled_at: Any,
    config: Any,
    env: str,
    context: dict[str, Any],
    spark_session: Any,
) -> None:
    """Write one idempotent runtime lineage event to metadata lineage."""
    normalized_key = _require_non_empty_string(metadata_table_key, "metadata_table_key")
    normalized_fingerprint = _require_non_empty_string(schema_fingerprint, "schema_fingerprint")
    normalized_role = _normalize_choice(profile_role, "profile_role", {"source", "target"})
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    activity_id = audit["_activity_id"]
    event_id = _lineage_event_id(
        activity_id=activity_id,
        metadata_table_key=normalized_key,
        schema_fingerprint=normalized_fingerprint,
        profile_role=normalized_role,
    )
    row = coerce_metadata_row_types(
        LINEAGE_TABLE,
        {
            "lineage_event_id": event_id,
            "metadata_table_key": normalized_key,
            "schema_fingerprint": normalized_fingerprint,
            "profile_role": normalized_role,
            "profiled_at": profiled_at,
            "environment_name": env,
            **audit,
        },
    )
    lineage_schema = metadata_table_schema_registry()[LINEAGE_TABLE]
    lineage_df = spark_session.createDataFrame([row], schema=lineage_schema)
    _upsert_lineage_event(lineage_df=lineage_df, config=config, env=env, spark_session=spark_session)


def _upsert_catalogue_identities(*, catalogue_df: Any, config: Any, env: str, spark_session: Any) -> None:
    """Upsert environment observations by logical table, column, and schema identity."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake merge support is required for idempotent METADATA_DATA_CATALOGUE writes."
        ) from exc

    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        CATALOGUE_TABLE,
        configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
    )
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(
            catalogue_df.alias("source"),
            "target.environment_name = source.environment_name AND target.metadata_table_key = source.metadata_table_key AND target.metadata_column_key = source.metadata_column_key AND target.schema_fingerprint = source.schema_fingerprint",
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def _upsert_lineage_event(*, lineage_df: Any, config: Any, env: str, spark_session: Any) -> None:
    """Upsert lineage rows by lineage_event_id without falling back to append."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError("Delta Lake merge support is required for idempotent METADATA_DATA_LINEAGE writes.") from exc

    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        LINEAGE_TABLE,
        configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
    )
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(
            lineage_df.alias("source"),
            "target.environment_name = source.environment_name AND target.lineage_event_id = source.lineage_event_id",
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def profile_and_register_table(
    df,
    *,
    profile_role,
    target,
    table_name,
    schema=None,
    frequency_columns=None,
    frequency_top_n: int | None = None,
    frequency_max_distinct_percent: float | None = 80.0,
    frequency_profile_df=None,
):
    """Profile a supplied Spark DataFrame and save its metadata records.

    The notebook supplies a Spark DataFrame and the table identity that the
    DataFrame represents. FabricOps calculates one profiling result row for
    each eligible column, saves a new profiling snapshot, creates stable table
    and column IDs, updates or adds catalogue records, records whether the
    table was used as an input or produced as an output, and returns the
    profiling result to the notebook.

    The original business DataFrame is not written, sampled, re-read, or
    changed by this function. All metadata writes go to the metadata lakehouse
    configured in ``00_env_config`` for the active environment.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to profile exactly as supplied by the caller. The
        helper does not sample, re-read, or mutate this DataFrame.
    profile_role : {"source", "target"}
        Records whether the profiled asset participated in the notebook
        activity as an input or an output: ``source`` for an activity input and
        ``target`` for an activity output. The value is stored in
        ``METADATA_DATA_LINEAGE`` rather than in ``METADATA_DATA_PROFILED`` or
        ``METADATA_DATA_CATALOGUE``.
    target : str
        Configured FabricStore target key. Its normalized key becomes the
        physical identity's layer and its store kind determines whether the
        asset is a Lakehouse or Warehouse table.
    table_name : str
        Physical table name of the business asset being profiled. This
        identifies the asset and does not redirect metadata writes.
    schema : str, optional
        Physical schema name, or ``None`` to use the configured store default.
        Classic or schema-disabled Lakehouses preserve ``None``.
    frequency_columns : sequence of str, optional
        Selected columns whose flattened frequency rows should be persisted.
        ``None`` profiles eligible non-technical scalar columns. An empty
        sequence skips frequency profiling entirely and writes no child rows.
        Requested columns should also be eligible for the main statistical
        profile.
    frequency_top_n : int or None, optional
        Optional number of ranked values to retain per selected frequency
        column. ``None`` retains every distinct value.
    frequency_max_distinct_percent : float or None, default=80.0
        Automatic frequency-profiling safeguard used only when
        ``frequency_columns=None``. Columns whose distinct-per-non-null
        percentage is greater than this threshold are skipped and produce no
        child frequency rows. Values must be between ``0.0`` and ``100.0``
        when supplied. ``None`` disables the high-cardinality threshold;
        all-null automatic columns remain skipped. Explicit
        ``frequency_columns`` selections override this threshold.
    frequency_profile_df : pyspark.sql.DataFrame, optional
        Optional caller-provided Spark DataFrame to use only for frequency
        distribution calculation. ``None`` preserves full-source frequency
        profiling. When supplied, it must contain every selected frequency
        column, may contain extra columns, and must use a compatible Spark
        session when this can be determined. The caller is responsible for
        preparing, persisting, refreshing, and governing this DataFrame; this
        function does not verify whether it is random, representative, sampled,
        persisted, or otherwise suitable for the caller's purpose.

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame containing one canonical profiling record for each
        eligible column in the supplied DataFrame. This is the same DataFrame
        appended to ``METADATA_DATA_PROFILED`` and includes physical asset
        identity, compact statistical metrics, schema identity, and runtime
        audit fields. Flattened child frequency rows, generated catalogue rows,
        and the lineage event are not returned.

    Raises
    ------
    ValueError
        If the role, target, configured store, schema, or table identity is invalid.
    RuntimeError
        If Delta replacement support is unavailable, or lineage registration
        fails after profile and catalogue registration succeed.

    Notes
    -----
    Processing flow:

    1. Build a statistical profile against the complete supplied DataFrame to
       produce one statistical profile row per eligible input column.
    2. Use that statistical profile to choose automatic frequency columns
       when ``frequency_columns=None``: eligible scalar columns at or below
       ``frequency_max_distinct_percent`` are profiled, high-cardinality
       columns and all-null columns produce no child frequency rows. Explicit non-empty
       ``frequency_columns`` bypass this threshold, while
       ``frequency_columns=[]`` skips frequency profiling entirely.
    3. Produce flattened frequency rows for the selected columns using the
       same calculation exposed by ``profile_frequency_distribution``.
    4. Resolve each frequency row to its parent ``metadata_column_key`` and
       prepare it with the same ``profiled_at`` snapshot timestamp.
    5. Save the compact profiling snapshot to ``METADATA_DATA_PROFILED``.
    6. Replace rows for the exact ``metadata_column_key + profiled_at`` child
       snapshot and write the normalized rows to
       ``METADATA_DATA_PROFILED_FREQUENCY``.
    7. Create stable table and column IDs, then update matching catalogue
       records or add new records in ``METADATA_DATA_CATALOGUE``.
    8. Record whether the table was used as an input or produced as an output
       in ``METADATA_DATA_LINEAGE``.
    9. Return only the compact parent Spark DataFrame written to
       ``METADATA_DATA_PROFILED``.

    User-facing workflow:

    Supplied DataFrame
        ↓
    Calculate column statistics and value frequencies
        ↓
    Save compact summary and flattened frequency snapshots
    ``METADATA_DATA_PROFILED`` + ``METADATA_DATA_PROFILED_FREQUENCY``
        ↓
    Create stable table and column IDs
        ↓
    Update existing catalogue records or add new ones
    ``METADATA_DATA_CATALOGUE``
        ↓
    Record whether the table was used as an input or output
        ↓
    ``METADATA_DATA_LINEAGE``
        ↓
    Return the profiling result to the notebook

    Frequency snapshot behavior:

    - Every eligible statistical profile row remains in the compact parent
      result whether or not that column produces child frequency rows.
    - ``frequency_columns=None`` automatically profiles eligible non-technical
      scalar columns whose distinct-per-non-null percentage is less than or
      equal to ``frequency_max_distinct_percent``. The default threshold is
      ``80.0`` percent.
    - Automatically selected columns above the threshold and all-null automatic
      columns produce no child frequency rows. No fake skipped values are stored.
    - ``frequency_max_distinct_percent=None`` disables the high-cardinality
      threshold for automatic columns.
    - Only columns listed in a non-empty ``frequency_columns`` sequence receive
      generated frequency evidence; explicit selections override the automatic
      threshold. Other profiled columns produce no child rows.
    - ``frequency_columns=[]`` skips frequency profiling entirely and writes no
      child rows for the current snapshot.
    - ``frequency_profile_df=None`` profiles frequencies against the complete
      supplied source DataFrame. When a caller supplies ``frequency_profile_df``,
      frequency counts, percentages, ranks, profiled row counts, and profiled
      non-null counts describe that caller-provided DataFrame. The compact
      parent statistics still describe the complete source DataFrame.
    - ``frequency_top_n`` restricts persisted child rows only when supplied. It
      limits output rows after grouped counts are calculated and does not
      reduce grouping cost.
    - Frequency values are ordered deterministically by rank.
    - Historical parent and child snapshots join on both
      ``metadata_column_key`` and ``profiled_at``. Rows are replaced only for
      that exact snapshot identity, so earlier snapshots remain intact.

    ``METADATA_DATA_PROFILED`` receives one appended row per eligible input
    DataFrame column. Repeated executions create additional profiling
    snapshots, and the returned DataFrame is the same compact DataFrame
    appended to this table. Its logical field groups are:

    - Identity fields: ``metadata_table_key``, ``metadata_column_key``,
      ``environment_name``, ``store_type``, ``layer``, ``schema_name``,
      ``table_name``, ``column_name``, ``data_type``.
    - Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
      ``null_percent``, ``distinct_count``, ``distinct_percent``,
      ``mean_value``, ``stddev_value``, ``min_value``,
      ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
      ``max_value``.
    - Runtime fields: ``schema_fingerprint``, ``profiled_at``.
    - Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
      ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
      ``_metadata_lakehouse_name``, ``_activity_id``.

    ``METADATA_DATA_PROFILED`` saves a new compact profiling snapshot. One row
    is saved for each eligible DataFrame column. ``METADATA_DATA_PROFILED_FREQUENCY``
    saves one flattened row per returned distinct value. Earlier parent and
    child snapshots are retained and join on ``metadata_column_key + profiled_at``.

    ``METADATA_DATA_CATALOGUE`` stores table and column records, not profiling
    measurements. FabricOps creates a stable ID for the table and each column,
    then checks whether the same table, column, and schema already exist. If a
    matching record exists, it is updated. Otherwise, a new record is added.
    Matching uses ``environment_name + metadata_table_key +
    metadata_column_key + schema_fingerprint``:

    - ``metadata_table_key``: stable logical table identity shared across
      environments.
    - ``metadata_column_key``: stable logical column identity shared across
      environments.
    - ``schema_fingerprint``: deterministic fingerprint of ordered schema
      content, independent of deployment environment. The current schema
      contract includes ordered column names and data types; nullability is
      not currently part of the fingerprint.
    - ``environment_name``: environment-specific catalogue observation.

    One logical Data Contract link can therefore govern the same dataset in
    Development and Production, while catalogue and execution observations
    remain separate and promotion checks can compare matching logical keys.
    Existing metadata created with environment-coupled identities must be
    recreated or explicitly migrated; FabricOps does not provide a legacy-key
    compatibility path.

    A changed ``schema_fingerprint`` represents a newly observed table
    structure and can create a new catalogue snapshot.

    ``METADATA_DATA_LINEAGE`` records whether the table was used as an input
    or produced as an output during the current notebook activity. A
    ``profile_role="source"`` value means the DataFrame was used as an input.
    A ``profile_role="target"`` value means the DataFrame was produced as an
    output. Lineage-specific fields are ``lineage_event_id``,
    ``metadata_table_key``, ``schema_fingerprint``, ``profile_role``,
    ``profiled_at``, and ``environment_name``. The standard eight underscore
    audit fields are the sole execution-context contract. ``profiled_at`` is
    the dataset profile snapshot time, while ``_committed_at`` is the metadata
    write time. ``lineage_event_id`` is deterministically derived from
    ``_activity_id``, ``metadata_table_key``, ``schema_fingerprint``, and
    ``profile_role``.

    What the notebook receives: a Spark DataFrame containing one profiling
    result row for each eligible column.

    What FabricOps saves:

    - ``METADATA_DATA_PROFILED``: a new compact profiling snapshot.
    - ``METADATA_DATA_PROFILED_FREQUENCY``: flattened frequency rows linked by
      ``metadata_column_key`` and ``profiled_at``.
    - ``METADATA_DATA_CATALOGUE``: updated or newly added table and column
      records.
    - ``METADATA_DATA_LINEAGE``: the current source or target activity.

    Statistical profiling records describe the complete DataFrame supplied
    during the notebook activity. If ``frequency_profile_df`` is supplied,
    only generated frequency evidence uses that DataFrame. The function does not claim or
    verify that the caller-provided DataFrame is sampled, random,
    representative, persisted, or governed; those responsibilities stay with
    the upstream ingestion or notebook workflow.

    The physical identity is the caller-selected configured table identity;
    an arbitrary DataFrame does not prove that table exists. Profile a source
    after a successful complete-table read, and profile a target only after
    its write has succeeded and the persisted target has been confirmed.

    Profile and catalogue registration occur before lineage registration. If
    lineage registration fails after those writes succeed, the function raises
    a ``RuntimeError`` explaining that profile and catalogue registration
    succeeded but lineage registration failed. Guardrail execution is a
    separate workflow.

    Removing ``frequency_json`` from ``METADATA_DATA_PROFILED`` and adding the
    normalized child table is a breaking physical-schema change. Existing
    metadata tables may need recreation through the established setup flow;
    no compatibility or automatic migration layer is provided.

    """
    (
        normalized_profile_role,
        normalized_target,
        normalized_table,
        normalized_schema,
        normalized_store_type,
        config,
        env,
        context,
    ) = _resolve_physical_identity(profile_role=profile_role, target=target, schema=schema, table_name=table_name)
    selected_frequency_columns = None if frequency_columns is None else list(frequency_columns)
    if frequency_max_distinct_percent is not None and (
        not math.isfinite(frequency_max_distinct_percent) or not 0.0 <= frequency_max_distinct_percent <= 100.0
    ):
        raise ValueError("frequency_max_distinct_percent must be finite and between 0.0 and 100.0 when supplied.")

    profile_df = build_profile_dataframe(df)
    schema_fingerprint = _schema_fingerprint(df)
    profiled_df = _canonical_profiled_dataframe(
        profile_df,
        source_df=df,
        config=config,
        env=env,
        runtime_context=context,
        environment_name=env,
        store_type=normalized_store_type,
        layer=normalized_target,
        schema_name=normalized_schema,
        table_name=normalized_table,
    )
    selected_columns = _selected_frequency_columns(
        df, profile_df, selected_frequency_columns, frequency_max_distinct_percent
    )
    frequency_metadata_df = None
    if selected_columns:
        frequency_source_df, _frequency_scope = _validate_frequency_profile_dataframe(
            df, frequency_profile_df, selected_columns
        )
        frequency_df = build_frequency_distribution_dataframe(
            frequency_source_df, columns=selected_columns, top_n=frequency_top_n
        )
        frequency_metadata_df = _frequency_metadata_dataframe(
            frequency_df,
            profiled_df=profiled_df,
            config=config,
            env=env,
            runtime_context=context,
        )
    write_lakehouse_table_core(
        profiled_df,
        PROFILED_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )
    _replace_frequency_rows(
        frequency_df=frequency_metadata_df,
        profiled_df=profiled_df,
        config=config,
        env=env,
        spark_session=df.sparkSession,
    )
    catalogue_df = _catalogue_dataframe_from_profiled(profiled_df)
    _upsert_catalogue_identities(catalogue_df=catalogue_df, config=config, env=env, spark_session=df.sparkSession)
    metadata_table_key = build_metadata_table_key(
        normalized_store_type, normalized_target, normalized_schema, normalized_table
    )
    try:
        _write_lineage_participation(
            metadata_table_key=metadata_table_key,
            schema_fingerprint=schema_fingerprint,
            profile_role=normalized_profile_role,
            profiled_at=build_runtime_audit_fields(config=config, env=env, runtime_context=context)["_committed_at"],
            config=config,
            env=env,
            context=context,
            spark_session=df.sparkSession,
        )
    except Exception as exc:
        raise RuntimeError(
            "Profile and catalogue registration succeeded but lineage registration failed "
            f"for metadata_table_key={metadata_table_key!r} and profile_role={normalized_profile_role!r}."
        ) from exc
    return profiled_df
