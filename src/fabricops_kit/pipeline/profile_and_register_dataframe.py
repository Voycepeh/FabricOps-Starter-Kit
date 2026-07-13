"""Public notebook-facing DataFrame profile registration callable."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Sequence

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, resolve_configured_lakehouse_table, write_lakehouse_table_core
from fabricops_kit.pipeline.profile_dataframe import profile_dataframe
from fabricops_kit.pipeline.profile_frequency_distribution import profile_frequency_distribution

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
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


def _frequency_json_dataframe(df, frequency_columns: Sequence[str] | None, frequency_top_n: int):
    """Return per-column deterministic frequency JSON evidence."""
    from pyspark.sql import functions as F

    if not frequency_columns:
        return None
    frequency_df = profile_frequency_distribution(df, columns=frequency_columns, top_n=frequency_top_n)
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
    return frequency_df.groupBy("COLUMN_NAME").agg(
        F.to_json(
            F.struct(
                F.first("PROFILED_ROW_COUNT", ignorenulls=True).cast("long").alias("profiled_row_count"),
                F.first("PROFILED_NON_NULL_COUNT", ignorenulls=True).cast("long").alias("profiled_non_null_count"),
                values.alias("values"),
            ),
            options={"ignoreNullFields": "false"},
        ).alias("frequency_json")
    )


def _canonical_catalogue_dataframe(
    profile_df,
    *,
    source_df,
    environment_name: str,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
    frequency_columns: Sequence[str] | None,
    frequency_top_n: int,
    is_sampled: bool,
):
    """Return profile rows mapped to the metadata catalogue schema."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    metadata_table_key = _metadata_table_key(environment_name, store_type, layer, schema_name, table_name)
    column_key_udf = F.udf(lambda column_name: _metadata_column_key(metadata_table_key, column_name), T.StringType())
    frequency_df = _frequency_json_dataframe(source_df, frequency_columns, frequency_top_n)
    schema_fingerprint = _schema_fingerprint(source_df)

    catalogue_df = profile_df.select(
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
        catalogue_df = catalogue_df.join(frequency_df, catalogue_df.column_name == frequency_df.COLUMN_NAME, "left").drop(frequency_df.COLUMN_NAME)
    else:
        catalogue_df = catalogue_df.withColumn("frequency_json", F.lit(None).cast("string"))

    return catalogue_df.select(
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
        F.lit(bool(is_sampled)).cast("boolean").alias("is_sampled"),
        F.col("frequency_json").cast("string"),
        F.lit(schema_fingerprint).cast("string").alias("schema_fingerprint"),
        F.current_timestamp().cast("timestamp").alias("profiled_at"),
        F.current_timestamp().cast("timestamp").alias("_committed_at"),
    ).select(*CATALOGUE_COLUMNS)


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
        },
    )
    lineage_schema = metadata_table_schema_registry()[LINEAGE_TABLE]
    lineage_df = spark_session.createDataFrame([row], schema=lineage_schema)
    try:
        from delta.tables import DeltaTable

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
    except Exception:
        write_lakehouse_table_core(
            lineage_df,
            LINEAGE_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            mode="append",
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
    frequency_top_n=20,
    is_sampled=False,
):
    """Profile and append one DataFrame snapshot to ``METADATA_DATA_CATALOGUE``.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to profile exactly as supplied by the caller. The
        helper does not sample, re-read, or mutate this DataFrame.
    profile_role : {"source", "target"}
        Execution participation context for the DataFrame in the notebook flow.
        The validated value is not stored in ``METADATA_DATA_CATALOGUE``; an
        automatic lineage flow records one table-level runtime participation row.
    environment_name : str
        FabricOps environment name to persist with the catalogue snapshot.
    store_type : {"lakehouse", "warehouse"}
        Physical store type for the profiled asset.
    layer : str
        Logical lakehouse or warehouse layer for the profiled asset.
    table_name : str
        Physical table name for the profiled asset.
    schema_name : str, optional
        Optional physical schema name. Use ``None`` for lakehouse tables without
        a separate schema.
    frequency_columns : sequence of str, optional
        Columns to pass to ``profile_frequency_distribution`` for top-N value
        evidence. ``None`` or an empty sequence skips frequency profiling.
    frequency_top_n : int, default=20
        Number of ranked values to request from frequency profiling.
    is_sampled : bool, default=False
        Caller-declared provenance flag persisted in the catalogue snapshot.

    Returns
    -------
    pyspark.sql.DataFrame
        Final catalogue DataFrame appended to ``METADATA_DATA_CATALOGUE``.

    Raises
    ------
    ValueError
        If profile role, store type, or required physical identity inputs are invalid.

    Notes
    -----
    Metadata writes route through the configured ``metadata`` target from
    ``00_env_config`` and append one profile snapshot per invocation. Exact
    lineage registration appends one participation row after the catalogue
    snapshot; guardrail execution is a separate workflow.

    """
    normalized_profile_role = _normalize_choice(profile_role, "profile_role", {"source", "target"})
    normalized_store_type = _normalize_choice(store_type, "store_type", {"lakehouse", "warehouse"})
    normalized_environment = _require_non_empty_string(environment_name, "environment_name")
    normalized_layer = _require_non_empty_string(layer, "layer")
    normalized_table = _require_non_empty_string(table_name, "table_name")
    normalized_schema = None if schema_name is None else _require_non_empty_string(schema_name, "schema_name")
    selected_frequency_columns = None if frequency_columns is None else list(frequency_columns)

    config, env, context = resolve_fabric_context(env=normalized_environment)
    profile_df = profile_dataframe(df)
    schema_fingerprint = _schema_fingerprint(df)
    catalogue_df = _canonical_catalogue_dataframe(
        profile_df,
        source_df=df,
        environment_name=normalized_environment,
        store_type=normalized_store_type,
        layer=normalized_layer,
        schema_name=normalized_schema,
        table_name=normalized_table,
        frequency_columns=selected_frequency_columns,
        frequency_top_n=frequency_top_n,
        is_sampled=is_sampled,
    )
    write_lakehouse_table_core(
        catalogue_df,
        CATALOGUE_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )
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
            "Catalogue registration succeeded but lineage registration failed "
            f"for metadata_table_key={metadata_table_key!r} and profile_role={normalized_profile_role!r}."
        ) from exc
    return catalogue_df
