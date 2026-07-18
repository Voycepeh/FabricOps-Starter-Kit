"""Public notebook-facing DataFrame profile registration callable."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Sequence

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, resolve_configured_lakehouse_table, write_lakehouse_table_core
from fabricops_kit.pipeline.profile_frequency_distribution import profile_frequency_distribution
from fabricops_kit.pipeline.shared import build_profile_dataframe

PROFILED_TABLE = "METADATA_DATA_PROFILED"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
PROFILED_COLUMNS = metadata_table_schema_registry()[PROFILED_TABLE].fieldNames()
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


def _stable_catalogue_key(*parts: Any) -> str:
    """Return a deterministic key that preserves nulls and delimiter values."""
    payload = [{"is_null": part is None, "value": None if part is None else str(part).strip().lower()} for part in parts]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def _metadata_table_key(environment_name: str, store_type: str, layer: str, schema_name: str | None, table_name: str) -> str:
    """Return the canonical physical asset key for a catalogue table snapshot."""
    return _stable_catalogue_key(environment_name, store_type, layer, schema_name, table_name)


def _metadata_column_key(metadata_table_key: str, column_name: str) -> str:
    """Return the canonical physical asset key for a catalogue column snapshot."""
    return _stable_catalogue_key(metadata_table_key, column_name)


def _schema_fingerprint(df: Any) -> str:
    """Return the deterministic fingerprint for an observed Spark schema."""
    fields = [
        {"name": str(field.name).strip(), "type": field.dataType.simpleString()}
        for field in getattr(getattr(df, "schema", None), "fields", [])
    ]
    payload = {"fields": fields}
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


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


def _skipped_frequency_json_dataframe(profile_df, *, scalar_columns: Sequence[str], threshold_percent: float | None):
    """Return automatic frequency skip JSON for high-cardinality or all-null columns."""
    from pyspark.sql import functions as F

    non_null_count = F.col("NON_NULL_COUNT").cast("double")
    distinct_count = F.col("DISTINCT_COUNT").cast("double")
    raw_cardinality_percent = (distinct_count / non_null_count) * 100
    cardinality_percent = F.when(non_null_count == 0, F.lit(None).cast("double")).otherwise(
        F.round(raw_cardinality_percent, 3)
    )
    threshold = F.lit(None if threshold_percent is None else float(threshold_percent)).cast("double")
    no_non_null = F.col("NON_NULL_COUNT").cast("long") == F.lit(0)
    high_cardinality = (F.lit(threshold_percent is not None)) & (raw_cardinality_percent > threshold)
    reason = F.when(no_non_null, F.lit("no_non_null_values")).otherwise(F.lit("high_cardinality"))
    message = F.when(
        no_non_null,
        F.lit("Frequency profiling skipped because the column contains no non-null values."),
    ).otherwise(
        F.concat(
            F.lit("Frequency profiling skipped because distinct percentage exceeded "),
            F.regexp_replace(F.format_number(threshold, 3), r"\.?0+$", ""),
            F.lit("%."),
        )
    )
    return (
        profile_df.where(F.col("COLUMN_NAME").isin(list(scalar_columns)))
        .where(no_non_null | high_cardinality)
        .select(
            F.col("COLUMN_NAME"),
            F.to_json(
                F.struct(
                    F.lit("skipped").alias("status"),
                    reason.alias("reason"),
                    cardinality_percent.alias("distinct_percent"),
                    threshold.alias("threshold_percent"),
                    message.alias("message"),
                ),
                options={"ignoreNullFields": "false"},
            ).alias("frequency_json"),
        )
    )


def _automatic_frequency_columns(profile_df, *, scalar_columns: Sequence[str], threshold_percent: float | None) -> list[str]:
    """Return automatic scalar columns that pass the frequency cardinality guard."""
    from pyspark.sql import functions as F

    non_null_count = F.col("NON_NULL_COUNT").cast("double")
    distinct_count = F.col("DISTINCT_COUNT").cast("double")
    raw_cardinality_percent = (distinct_count / non_null_count) * 100
    eligible = profile_df.where(F.col("COLUMN_NAME").isin(list(scalar_columns))).where(F.col("NON_NULL_COUNT").cast("long") > 0)
    if threshold_percent is not None:
        eligible = eligible.where(raw_cardinality_percent <= F.lit(float(threshold_percent)))
    return [row.COLUMN_NAME for row in eligible.select("COLUMN_NAME").collect()]


def _frequency_json_dataframe(
    source_df,
    frequency_profile_df,
    profile_df,
    frequency_columns: Sequence[str] | None,
    frequency_top_n: int | None,
    frequency_max_distinct_percent: float | None,
):
    """Return per-column deterministic frequency JSON evidence."""
    from pyspark.sql import functions as F

    if frequency_columns is not None and len(frequency_columns) == 0:
        return None

    explicit_columns = None if frequency_columns is None else list(frequency_columns)
    if explicit_columns is None:
        profiled_columns = [row.COLUMN_NAME for row in profile_df.select("COLUMN_NAME").collect()]
        scalar_columns = _scalar_frequency_columns(source_df, profiled_columns)
        selected_columns = _automatic_frequency_columns(
            profile_df,
            scalar_columns=scalar_columns,
            threshold_percent=frequency_max_distinct_percent,
        )
        skipped_df = _skipped_frequency_json_dataframe(
            profile_df,
            scalar_columns=scalar_columns,
            threshold_percent=frequency_max_distinct_percent,
        )
    else:
        selected_columns = explicit_columns
        skipped_df = None

    frequency_json_df = None
    if selected_columns:
        source_row_count_df = profile_df.select(
            F.first("ROW_COUNT", ignorenulls=True).cast("long").alias("SOURCE_ROW_COUNT")
        )
        frequency_source_df, frequency_scope = _validate_frequency_profile_dataframe(
            source_df,
            frequency_profile_df,
            selected_columns,
        )
        frequency_df = profile_frequency_distribution(
            frequency_source_df, columns=selected_columns, top_n=frequency_top_n
        ).crossJoin(source_row_count_df)
        value_struct = F.struct(
            F.col("FREQUENCY_RANK").cast("int").alias("rank"),
            F.col("VALUE").alias("value"),
            F.col("FREQUENCY_COUNT").cast("long").alias("count"),
            F.col("FREQUENCY_PERCENT").cast("double").alias("percent"),
        )
        ordered = F.sort_array(F.collect_list(value_struct))
        values = F.transform(
            ordered,
            lambda x: F.struct(
                x["value"].alias("value"),
                x["count"].alias("count"),
                x["percent"].alias("percent"),
                x["rank"].alias("rank"),
            ),
        )
        frequency_json_df = frequency_df.groupBy("COLUMN_NAME").agg(
            F.to_json(
                F.struct(
                    F.first("SOURCE_ROW_COUNT", ignorenulls=True).cast("long").alias("source_row_count"),
                    F.first("PROFILED_ROW_COUNT", ignorenulls=True).cast("long").alias("profiled_row_count"),
                    F.first("PROFILED_NON_NULL_COUNT", ignorenulls=True).cast("long").alias("profiled_non_null_count"),
                    F.lit(frequency_scope).cast("string").alias("frequency_scope"),
                    values.alias("values"),
                ),
                options={"ignoreNullFields": "false"},
            ).alias("frequency_json")
        )

    if skipped_df is not None:
        frequency_json_df = skipped_df if frequency_json_df is None else frequency_json_df.unionByName(skipped_df)
    return frequency_json_df


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
    frequency_columns: Sequence[str] | None,
    frequency_top_n: int | None,
    frequency_max_distinct_percent: float | None,
    frequency_profile_df: Any,
):
    """Return profile rows mapped to the detailed profiled schema."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    metadata_table_key = _metadata_table_key(environment_name, store_type, layer, schema_name, table_name)
    column_key_udf = F.udf(lambda column_name: _metadata_column_key(metadata_table_key, column_name), T.StringType())
    frequency_df = _frequency_json_dataframe(
        source_df,
        frequency_profile_df,
        profile_df,
        frequency_columns,
        frequency_top_n,
        frequency_max_distinct_percent,
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
    if frequency_df is not None:
        profiled_df = profiled_df.join(frequency_df, profiled_df.column_name == frequency_df.COLUMN_NAME, "left").drop(frequency_df.COLUMN_NAME)
    else:
        profiled_df = profiled_df.withColumn("frequency_json", F.lit(None).cast("string"))

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
        F.col("frequency_json").cast("string"),
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

    return profiled_df.select(
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
    ).dropDuplicates(["metadata_table_key", "metadata_column_key", "schema_fingerprint"]).select(*CATALOGUE_COLUMNS)


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
    activity_id = _require_non_empty_string(audit.get("_activity_id"), "activity_id")
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
            "activity_id": activity_id,
            "notebook_id": _require_non_empty_string(audit.get("_notebook_id"), "notebook_id"),
            "notebook_name": _require_non_empty_string(audit.get("_notebook_name"), "notebook_name"),
            "workspace_id": _require_non_empty_string(audit.get("_workspace_id"), "workspace_id"),
            "workspace_name": _require_non_empty_string(audit.get("_workspace_name"), "workspace_name"),
            "metadata_table_key": normalized_key,
            "schema_fingerprint": normalized_fingerprint,
            "profile_role": normalized_role,
            "profiled_at": profiled_at,
            "committed_by": _require_non_empty_string(audit.get("_committed_by"), "committed_by"),
            "environment_name": env,
            "metadata_lakehouse_name": audit.get("_metadata_lakehouse_name"),
            **audit,
        },
    )
    lineage_schema = metadata_table_schema_registry()[LINEAGE_TABLE]
    lineage_df = spark_session.createDataFrame([row], schema=lineage_schema)
    _upsert_lineage_event(lineage_df=lineage_df, config=config, env=env, spark_session=spark_session)


def _upsert_catalogue_identities(*, catalogue_df: Any, config: Any, env: str, spark_session: Any) -> None:
    """Upsert catalogue identities by table key, column key, and schema fingerprint."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError("Delta Lake merge support is required for idempotent METADATA_DATA_CATALOGUE writes.") from exc

    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata", CATALOGUE_TABLE, configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}
    )
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(
            catalogue_df.alias("source"),
            "target.metadata_table_key = source.metadata_table_key AND target.metadata_column_key = source.metadata_column_key AND target.schema_fingerprint = source.schema_fingerprint",
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
        "metadata", LINEAGE_TABLE, configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}
    )
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(lineage_df.alias("source"), "target.lineage_event_id = source.lineage_event_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def profile_and_register_dataframe(
    df,
    *,
    profile_role,
    environment_name,
    store_type,
    layer,
    table_name,
    schema_name=None,
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
    configured in ``00_env_config`` for the selected environment.

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
    environment_name : str
        FabricOps environment context used to find the configured metadata
        lakehouse and persist the environment identity.
    store_type : {"lakehouse", "warehouse"}
        Physical store type of the business asset being profiled. This
        identifies the asset and does not redirect metadata writes to that
        business store.
    layer : str
        Logical lakehouse or warehouse layer of the business asset being
        profiled. This identifies the asset and does not redirect metadata
        writes.
    table_name : str
        Physical table name of the business asset being profiled. This
        identifies the asset and does not redirect metadata writes.
    schema_name : str, optional
        Optional physical schema name for the business asset. Use ``None`` for
        lakehouse tables without a separate schema. This identifies the asset
        and does not redirect metadata writes.
    frequency_columns : sequence of str, optional
        Selected columns that should receive embedded frequency evidence. ``None``
        profiles all eligible non-technical scalar columns. An empty sequence
        skips frequency profiling entirely and persists null ``frequency_json``
        for every statistical profile row. Requested columns should also be
        eligible for the main statistical profile.
    frequency_top_n : int or None, optional
        Optional number of ranked values to retain per selected frequency
        column. ``None`` retains every distinct value.
    frequency_max_distinct_percent : float or None, default=80.0
        Automatic frequency-profiling safeguard used only when
        ``frequency_columns=None``. Columns whose distinct-per-non-null
        percentage is greater than this threshold receive structured skipped
        JSON instead of generated frequencies. Values must be between ``0.0``
        and ``100.0`` when supplied. ``None`` disables the high-cardinality
        threshold; all-null automatic columns still receive structured skipped
        JSON. Explicit ``frequency_columns`` selections override this threshold.
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
        identity, statistical metrics, frequency JSON where enabled, schema
        identity, and runtime audit fields. The function
        does not return the generated catalogue rows or lineage event.

    Raises
    ------
    ValueError
        If profile role, store type, or required physical identity inputs are invalid.
    RuntimeError
        If lineage registration fails after profile and catalogue registration
        succeed.

    Notes
    -----
    Processing flow:

    1. Build a statistical profile against the complete supplied DataFrame to
       produce one statistical profile row per eligible input column.
    2. Use that statistical profile to choose automatic frequency columns
       when ``frequency_columns=None``: eligible scalar columns at or below
       ``frequency_max_distinct_percent`` are profiled, high-cardinality
       columns receive structured skipped JSON, and all-null columns receive
       structured no-non-null-values skipped JSON. Explicit non-empty
       ``frequency_columns`` bypass this threshold, while
       ``frequency_columns=[]`` skips frequency profiling entirely.
    3. Convert the multiple frequency rows for each column into one
       deterministic JSON document.
    4. Left-join that JSON to the statistical profile on
       ``profile_dataframe.COLUMN_NAME = profile_frequency_distribution.COLUMN_NAME``.
    5. Save a new profiling snapshot to ``METADATA_DATA_PROFILED``.
    6. Create stable table and column IDs, then update matching catalogue
       records or add new records in ``METADATA_DATA_CATALOGUE``.
    7. Record whether the table was used as an input or produced as an output
       in ``METADATA_DATA_LINEAGE``.
    8. Return the detailed Spark DataFrame written to
       ``METADATA_DATA_PROFILED``.

    User-facing workflow:

    Supplied DataFrame
        ↓
    Calculate column statistics and value frequencies
        ↓
    Save a new profiling snapshot
    ``METADATA_DATA_PROFILED``
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

    Frequency join behavior:

    - The statistical profile is the left side of the join, so every eligible
      statistical profile row remains in the returned result.
    - ``frequency_columns=None`` automatically profiles eligible non-technical
      scalar columns whose distinct-per-non-null percentage is less than or
      equal to ``frequency_max_distinct_percent``. The default threshold is
      ``80.0`` percent.
    - Automatically selected columns above the threshold receive deterministic
      structured ``frequency_json`` with ``status="skipped"`` and
      ``reason="high_cardinality"``. All-null automatic columns receive
      ``reason="no_non_null_values"``.
    - ``frequency_max_distinct_percent=None`` disables the high-cardinality
      threshold for automatic columns.
    - Only columns listed in a non-empty ``frequency_columns`` sequence receive
      generated frequency evidence; explicit selections override the automatic
      threshold. Other profiled columns receive null.
    - ``frequency_columns=[]`` skips frequency profiling entirely and persists
      null ``frequency_json`` for every row.
    - ``frequency_profile_df=None`` profiles frequencies against the complete
      supplied source DataFrame. When a caller supplies ``frequency_profile_df``,
      frequency counts, percentages, ranks, profiled row counts, and profiled
      non-null counts describe that caller-provided DataFrame, while
      ``source_row_count`` records the complete source DataFrame row count.
    - ``frequency_top_n`` restricts embedded values only when supplied. It
      limits output rows after grouped counts are calculated and does not
      reduce grouping cost.
    - Frequency values are ordered deterministically by rank.

    Example ``frequency_json`` structure:

    .. code-block:: json

       {
         "source_row_count": 1000,
         "profiled_row_count": 1000,
         "profiled_non_null_count": 995,
         "frequency_scope": "full_source",
         "values": [
           {
             "value": "Active",
             "count": 700,
             "percent": 70.0,
             "rank": 1
           }
         ]
       }

    ``METADATA_DATA_PROFILED`` receives one appended row per eligible input
    DataFrame column. Repeated executions create additional profiling
    snapshots, and the returned DataFrame is the same detailed DataFrame
    appended to this table. Its logical field groups are:

    - Identity fields: ``metadata_table_key``, ``metadata_column_key``,
      ``environment_name``, ``store_type``, ``layer``, ``schema_name``,
      ``table_name``, ``column_name``, ``data_type``.
    - Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
      ``null_percent``, ``distinct_count``, ``distinct_percent``,
      ``mean_value``, ``stddev_value``, ``min_value``,
      ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
      ``max_value``.
    - Frequency and runtime fields: ``frequency_json``, ``schema_fingerprint``,
      ``profiled_at``.
    - Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
      ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
      ``_metadata_lakehouse_name``, ``_activity_id``.

    ``METADATA_DATA_PROFILED`` saves a new profiling snapshot. One row is
    saved for each eligible DataFrame column. Earlier profiling snapshots are
    retained.

    ``METADATA_DATA_CATALOGUE`` stores table and column records, not profiling
    measurements. FabricOps creates a stable ID for the table and each column,
    then checks whether the same table, column, and schema already exist. If a
    matching record exists, it is updated. Otherwise, a new record is added.
    Matching uses ``metadata_table_key + metadata_column_key +
    schema_fingerprint``:

    - ``metadata_table_key``: stable ID for the table.
    - ``metadata_column_key``: stable ID for a column within that table.
    - ``schema_fingerprint``: identifier for the DataFrame structure observed
      during profiling.

    A changed ``schema_fingerprint`` represents a newly observed table
    structure and can create a new catalogue snapshot.

    ``METADATA_DATA_LINEAGE`` records whether the table was used as an input
    or produced as an output during the current notebook activity. A
    ``profile_role="source"`` value means the DataFrame was used as an input.
    A ``profile_role="target"`` value means the DataFrame was produced as an
    output. Key lineage fields include ``lineage_event_id``,
    ``activity_id``, ``notebook_id``, ``notebook_name``, ``workspace_id``,
    ``workspace_name``, ``metadata_table_key``, ``schema_fingerprint``,
    ``profile_role``, ``profiled_at``, ``committed_by``,
    ``environment_name``, ``metadata_lakehouse_name``, and the standard audit
    fields. ``lineage_event_id`` is deterministically derived from
    ``activity_id``, ``metadata_table_key``, ``schema_fingerprint``, and
    ``profile_role``.

    What the notebook receives: a Spark DataFrame containing one profiling
    result row for each eligible column.

    What FabricOps saves:

    - ``METADATA_DATA_PROFILED``: a new profiling snapshot.
    - ``METADATA_DATA_CATALOGUE``: updated or newly added table and column
      records.
    - ``METADATA_DATA_LINEAGE``: the current source or target activity.

    Statistical profiling records describe the complete DataFrame supplied
    during the notebook activity. If ``frequency_profile_df`` is supplied,
    only generated frequency evidence uses that DataFrame and its JSON records
    ``frequency_scope="caller_provided"``. The function does not claim or
    verify that the caller-provided DataFrame is sampled, random,
    representative, persisted, or governed; those responsibilities stay with
    the upstream ingestion or notebook workflow.

    Profile and catalogue registration occur before lineage registration. If
    lineage registration fails after those writes succeed, the function raises
    a ``RuntimeError`` explaining that profile and catalogue registration
    succeeded but lineage registration failed. Guardrail execution is a
    separate workflow.

    """
    normalized_profile_role = _normalize_choice(profile_role, "profile_role", {"source", "target"})
    normalized_store_type = _normalize_choice(store_type, "store_type", {"lakehouse", "warehouse"})
    normalized_environment = _require_non_empty_string(environment_name, "environment_name")
    normalized_layer = _require_non_empty_string(layer, "layer")
    normalized_table = _require_non_empty_string(table_name, "table_name")
    normalized_schema = None if schema_name is None else _require_non_empty_string(schema_name, "schema_name")
    selected_frequency_columns = None if frequency_columns is None else list(frequency_columns)
    if frequency_max_distinct_percent is not None and (
        not math.isfinite(frequency_max_distinct_percent) or not 0.0 <= frequency_max_distinct_percent <= 100.0
    ):
        raise ValueError("frequency_max_distinct_percent must be finite and between 0.0 and 100.0 when supplied.")

    config, env, context = resolve_fabric_context(env=normalized_environment)
    profile_df = build_profile_dataframe(df)
    schema_fingerprint = _schema_fingerprint(df)
    profiled_df = _canonical_profiled_dataframe(
        profile_df,
        source_df=df,
        config=config,
        env=env,
        runtime_context=context,
        environment_name=normalized_environment,
        store_type=normalized_store_type,
        layer=normalized_layer,
        schema_name=normalized_schema,
        table_name=normalized_table,
        frequency_columns=selected_frequency_columns,
        frequency_top_n=frequency_top_n,
        frequency_max_distinct_percent=frequency_max_distinct_percent,
        frequency_profile_df=frequency_profile_df,
    )
    write_lakehouse_table_core(
        profiled_df,
        PROFILED_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )
    catalogue_df = _catalogue_dataframe_from_profiled(profiled_df)
    _upsert_catalogue_identities(catalogue_df=catalogue_df, config=config, env=env, spark_session=df.sparkSession)
    metadata_table_key = _metadata_table_key(
        normalized_environment,
        normalized_store_type,
        normalized_layer,
        normalized_schema,
        normalized_table,
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
