"""Public owner for notebook-facing statistical and frequency profiling."""

from __future__ import annotations

import json
import math
from typing import Any, Mapping, Sequence
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import build_column_id
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_physical_schema, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table, read_warehouse_table
from fabricops_kit.io.shared import (
    resolve_configured_lakehouse_table,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.shared import (
    build_frequency_distribution_dataframe,
    build_profile_dataframe,
    resolve_catalogue_table_identity,
    resolve_physical_table_identity,
)

PROFILED_TABLE = "METADATA_DATA_PROFILED"
PROFILED_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILED_COLUMNS = metadata_table_schema_registry()[PROFILED_TABLE].fieldNames()
PROFILED_FREQUENCY_COLUMNS = metadata_table_schema_registry()[PROFILED_FREQUENCY_TABLE].fieldNames()
CATALOGUE_COLUMNS = metadata_table_schema_registry()[CATALOGUE_TABLE].fieldNames()
LOAD_STRATEGIES = {"overwrite", "append", "scd1", "scd2"}


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


def _processing_definition(
    profile_role: str,
    load_strategy: Any,
    load_strategy_parameters: Any,
) -> tuple[str | None, str | None]:
    """Validate and canonically serialize one table-owned processing definition."""
    supplied = load_strategy is not None or load_strategy_parameters is not None
    if profile_role == "source":
        if supplied:
            raise ValueError("Source registration does not accept target processing arguments.")
        return None, None
    if load_strategy is None:
        if load_strategy_parameters is not None:
            raise ValueError("load_strategy is required when load_strategy_parameters is supplied.")
        return None, None
    strategy = _normalize_choice(load_strategy, "load_strategy", LOAD_STRATEGIES)
    if load_strategy_parameters is None:
        parameters: dict[str, Any] = {}
    elif not isinstance(load_strategy_parameters, dict):
        raise ValueError("load_strategy_parameters must be a mapping when supplied.")
    else:
        parameters = dict(load_strategy_parameters)
    allowed = {
        "overwrite": {"partition_column"},
        "append": set(),
        "scd1": {"key_columns"},
        "scd2": {"key_columns", "effective_column", "tracked_columns"},
    }[strategy]
    unexpected = sorted(set(parameters) - allowed)
    if unexpected:
        raise ValueError(f"{strategy} does not accept processing parameters: {', '.join(unexpected)}.")
    for name in ("key_columns", "tracked_columns"):
        if name in parameters:
            values = parameters[name]
            if not isinstance(values, (list, tuple)) or not values:
                raise ValueError(f"{name} must be a non-empty sequence of column names.")
            parameters[name] = [_require_non_empty_string(value, name) for value in values]
    for name in ("partition_column", "effective_column"):
        if name in parameters:
            parameters[name] = _require_non_empty_string(parameters[name], name)
    if strategy in {"scd1", "scd2"} and "key_columns" not in parameters:
        raise ValueError(f"{strategy} requires key_columns.")
    if strategy == "scd2" and "effective_column" not in parameters:
        raise ValueError("scd2 requires effective_column.")
    return strategy, json.dumps(parameters, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_processing_columns(df: Any, parameters_json: str | None) -> None:
    """Require every authored processing column name to exist in the target schema."""
    if parameters_json is None:
        return
    parameters = json.loads(parameters_json)
    available = {str(field.name) for field in df.schema.fields}
    referenced = []
    for name in ("partition_column", "effective_column"):
        if parameters.get(name):
            referenced.append(str(parameters[name]))
    for name in ("key_columns", "tracked_columns"):
        referenced.extend(str(value) for value in parameters.get(name, []))
    missing = sorted(set(referenced) - available)
    if missing:
        raise ValueError(f"Processing definition references columns not present in df: {', '.join(missing)}.")


def _validate_resolved_identity(table: Any, *, config: Any, env: str) -> dict[str, str | None]:
    """Validate a caller-supplied identity against the active Fabric config."""
    if not isinstance(table, Mapping):
        raise ValueError("table must be a canonical table identity mapping.")
    required = {"table_id", "target", "schema", "table_name", "store_kind"}
    missing = sorted(required - set(table))
    if missing:
        raise ValueError(f"table identity is missing required fields: {', '.join(missing)}.")
    resolved = resolve_physical_table_identity(
        config,
        env,
        target=table["target"],
        schema=table["schema"],
        table_name=table["table_name"],
    )
    supplied = {name: table[name] for name in required}
    if supplied != resolved:
        raise ValueError(
            "table identity is inconsistent with the canonical identity resolved from the active Fabric config."
        )
    return resolved


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
    return _automatic_frequency_columns(profile_df, scalar_columns=scalar_columns, threshold_percent=threshold_percent)


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
    config: Any,
    env: str,
    runtime_context: dict[str, Any],
    environment_name: str,
    table_id: str,
    profile_snapshot_id: str,
):
    """Map statistical profiler output to the normalized Profile schema."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    column_id_udf = F.udf(lambda column_name: build_column_id(table_id, column_name), T.StringType())
    audit_columns = _audit_literal_columns(config=config, env=env, runtime_context=runtime_context)
    base = profile_df.select(
        F.col("COLUMN_NAME").alias("_column_name"),
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
    return base.select(
        F.expr("uuid()").cast("string").alias("profile_id"),
        F.lit(profile_snapshot_id).cast("string").alias("profile_snapshot_id"),
        F.lit(table_id).cast("string").alias("table_id"),
        column_id_udf(F.col("_column_name")).alias("column_id"),
        F.lit(environment_name).cast("string").alias("environment_name"),
        F.col("data_type").cast("string"),
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_COLUMNS)


def _frequency_metadata_dataframe(
    frequency_df,
    *,
    profiled_df,
    table_id: str,
    config: Any,
    env: str,
    runtime_context: dict[str, Any],
):
    """Map flattened frequency output to the same logical column profile."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    column_id_udf = F.udf(lambda column_name: build_column_id(table_id, column_name), T.StringType())
    identities = profiled_df.select("column_id", "data_type", "profile_id", "profile_snapshot_id")
    joined = frequency_df.withColumn("_column_id", column_id_udf(F.col("COLUMN_NAME"))).join(
        identities,
        (F.col("_column_id") == identities.column_id) & (frequency_df.DATA_TYPE == identities.data_type),
        "inner",
    )
    audit_columns = _audit_literal_columns(config=config, env=env, runtime_context=runtime_context)
    return joined.select(
        F.expr("uuid()").cast("string").alias("frequency_id"),
        identities.profile_id.cast("string").alias("profile_id"),
        identities.profile_snapshot_id.cast("string").alias("profile_snapshot_id"),
        F.col("VALUE").cast("string").alias("value"),
        F.col("FREQUENCY_COUNT").cast("long").alias("frequency_count"),
        F.col("FREQUENCY_PERCENT").cast("double").alias("frequency_percent"),
        F.col("FREQUENCY_RANK").cast("integer").alias("frequency_rank"),
        F.col("PROFILED_ROW_COUNT").cast("long").alias("profiled_row_count"),
        F.col("PROFILED_NON_NULL_COUNT").cast("long").alias("profiled_non_null_count"),
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_FREQUENCY_COLUMNS)


def _replace_frequency_rows(
    *, frequency_df: Any | None, profiled_df: Any, config: Any, env: str, spark_session: Any
) -> None:
    """Replace flattened Frequency rows only for the current profiling snapshot."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake support is required for replacement METADATA_DATA_PROFILED_FREQUENCY writes."
        ) from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        PROFILED_FREQUENCY_TABLE,
        metadata_table_physical_schema(config, PROFILED_FREQUENCY_TABLE),
        context={"config": config, "env": env},
    )
    snapshots = profiled_df.select("profile_snapshot_id").dropDuplicates()
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(snapshots.alias("source"), "target.profile_snapshot_id = source.profile_snapshot_id")
        .whenMatchedDelete()
        .execute()
    )
    if frequency_df is not None:
        write_lakehouse_table_core(
            frequency_df,
            PROFILED_FREQUENCY_TABLE,
            target="metadata",
            schema=metadata_table_physical_schema(config, PROFILED_FREQUENCY_TABLE),
            context={"config": config, "env": env},
            mode="append",
        )


def _catalogue_dataframe_from_profiled(
    profiled_df,
    *,
    source_df: Any,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
    load_strategy: str | None = None,
    load_strategy_parameters_json: str | None = None,
):
    """Return one table row and one row for each observed column asset."""
    from pyspark.sql import functions as F

    first = profiled_df.select(
        "table_id",
        "environment_name",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ).first()
    if first is None:
        return profiled_df.sparkSession.createDataFrame([], schema=metadata_table_schema_registry()[CATALOGUE_TABLE])
    audit = {name: first[name] for name in CATALOGUE_COLUMNS if name.startswith("_")}
    common = {
        "table_id": first["table_id"],
        "environment_name": first["environment_name"],
        "store_type": store_type,
        "layer": layer,
        "schema_name": schema_name,
        "table_name": table_name,
        "first_profiled_at": first["_committed_at"],
        "last_profiled_at": first["_committed_at"],
        "is_active": True,
        **audit,
    }
    rows = [
        coerce_metadata_row_types(
            CATALOGUE_TABLE,
            {
                **common,
                "metadata_level": "table",
                "column_id": None,
                "column_name": None,
                "data_type": None,
                "load_strategy": load_strategy,
                "load_strategy_parameters_json": load_strategy_parameters_json,
            },
        )
    ]
    for field in source_df.schema.fields:
        column_id = build_column_id(first["table_id"], field.name)
        rows.append(
            coerce_metadata_row_types(
                CATALOGUE_TABLE,
                {
                    **common,
                    "metadata_level": "column",
                    "column_id": column_id,
                    "column_name": field.name,
                    "data_type": field.dataType.simpleString(),
                    "load_strategy": None,
                    "load_strategy_parameters_json": None,
                },
            )
        )
    return profiled_df.sparkSession.createDataFrame(rows, schema=metadata_table_schema_registry()[CATALOGUE_TABLE])


def _upsert_catalogue_identities(*, catalogue_df: Any, config: Any, env: str, spark_session: Any) -> None:
    """Upsert Catalogue rows by environment-aware asset grain and deactivate missing columns."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake merge support is required for idempotent METADATA_DATA_CATALOGUE writes."
        ) from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        CATALOGUE_TABLE,
        metadata_table_physical_schema(config, CATALOGUE_TABLE),
        context={"config": config, "env": env},
    )
    first = catalogue_df.select("environment_name", "table_id").first()
    if first is None:
        return
    environment_name = str(first["environment_name"]).replace("'", "''")
    table_id = str(first["table_id"]).replace("'", "''")
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(
            catalogue_df.alias("source"),
            "target.environment_name = source.environment_name "
            "AND target.metadata_level = source.metadata_level "
            "AND target.table_id = source.table_id "
            "AND coalesce(target.column_id, '') = coalesce(source.column_id, '')",
        )
        .whenMatchedUpdate(
            set={
                "store_type": "source.store_type",
                "layer": "source.layer",
                "schema_name": "source.schema_name",
                "table_name": "source.table_name",
                "column_name": "source.column_name",
                "data_type": "source.data_type",
                "load_strategy": "coalesce(source.load_strategy, target.load_strategy)",
                "load_strategy_parameters_json": (
                    "coalesce(source.load_strategy_parameters_json, target.load_strategy_parameters_json)"
                ),
                "last_profiled_at": "source.last_profiled_at",
                "is_active": "true",
                "_committed_by": "source._committed_by",
                "_committed_at": "source._committed_at",
                "_workspace_id": "source._workspace_id",
                "_workspace_name": "source._workspace_name",
                "_notebook_id": "source._notebook_id",
                "_notebook_name": "source._notebook_name",
                "_metadata_lakehouse_name": "source._metadata_lakehouse_name",
                "_activity_id": "source._activity_id",
            }
        )
        .whenNotMatchedInsertAll()
        .whenNotMatchedBySourceUpdate(
            condition=(
                f"target.environment_name = '{environment_name}' AND target.table_id = '{table_id}' "
                "AND target.metadata_level = 'column' AND target.is_active = true"
            ),
            set={"is_active": "false"},
        )
        .execute()
    )


def profile_table(
    *,
    dataframe=None,
    target: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    frequency_columns=None,
    frequency_top_n: int | None = None,
    frequency_max_distinct_percent: float | None = 80.0,
):
    """Profile a Spark DataFrame or a complete governed physical table.

    FabricOps calculates the canonical statistical profile and applicable
    frequency distribution with PySpark. An identity may be supplied as a
    canonical ``table_id`` or as ``target``, optional ``schema``, and
    ``table_name``. When an identity is present, FabricOps associates the
    result with that governed table and persists Catalogue, profile, and
    frequency metadata. Without an identity, the exact supplied DataFrame is
    profiled without creating an identity or writing metadata.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame, optional
        Exact Spark DataFrame to profile. If a governed identity is also
        supplied, FabricOps does not re-read the physical table.
    target : str, optional
        Configured physical target key. Supply with ``table_name`` and optional
        ``schema`` instead of ``table_id``.
    schema : str, optional
        Physical schema when the configured store uses schemas.
    table_name : str, optional
        Physical table name. Required with ``target`` when ``table_id`` is
        omitted.
    table_id : str, optional
        Canonical governed table identity, mutually exclusive with physical
        coordinates.
    frequency_columns : sequence of str, optional
        Columns to frequency profile. ``None`` automatically selects eligible
        scalar columns; an empty sequence skips frequency profiling.
    frequency_top_n : int or None, optional
        Ranked values to retain per frequency column. ``None`` retains all.
    frequency_max_distinct_percent : float or None, default=80.0
        Maximum distinct-per-non-null percentage for automatically selected
        columns. ``None`` disables the cardinality filter.

    Returns
    -------
    dict
        ``profile`` contains the canonical statistical Spark DataFrame and
        ``frequency_profile`` contains the applicable canonical frequency
        Spark DataFrame, or ``None`` when no columns were selected. Governed
        ``profile`` rows additionally contain persisted snapshot identities
        and audit fields.

    Raises
    ------
    ValueError
        If identity inputs conflict or are incomplete, neither a DataFrame nor
        identity is supplied, frequency settings are invalid, or the resolved
        store is unsupported.
    RuntimeError
        If a governed metadata write requires unavailable Delta support.

    Notes
    -----
    The orchestration performs these mechanical steps:

    1. Validate and resolve the optional canonical governed identity.
    2. Use the supplied DataFrame exactly, or read the complete physical table
       through the resolved Lakehouse or Warehouse reader.
    3. Calculate canonical statistical metrics with PySpark.
    4. Select eligible frequency columns and calculate exact grouped counts,
       including null as a frequency value.
    5. When governed, create stable table and column identities, append
       ``METADATA_DATA_PROFILED``, replace the current snapshot rows in
       ``METADATA_DATA_PROFILED_FREQUENCY``, and update
       ``METADATA_DATA_CATALOGUE``.
    6. Return both profiling outputs. DataFrame-only mode performs no metadata
       writes and never invents a ``table_id``.

    Examples
    --------
    Profile an arbitrary DataFrame without persistence:

    >>> result = profile_table(dataframe=raw_df)
    >>> statistical_profile = result["profile"]
    >>> frequencies = result["frequency_profile"]

    Profile a governed complete physical table without knowing its store kind:

    >>> result = profile_table(target="source", schema="dbo", table_name="orders")

    Profile a transformed DataFrame against an explicit governed identity:

    >>> result = profile_table(dataframe=transformed_df, table_id=target_table_id)

    See Also
    --------
    pipeline_read, pipeline_write, read_lakehouse_csv, read_lakehouse_excel,
    read_lakehouse_json, read_lakehouse_parquet

    """
    coordinates = (target, schema, table_name)
    has_coordinates = any(value is not None for value in coordinates)
    if table_id is not None and has_coordinates:
        raise ValueError("table_id cannot be combined with target, schema, or table_name.")
    if has_coordinates and (target is None or table_name is None):
        raise ValueError("Provide both target and table_name when using physical identity.")
    if dataframe is None and table_id is None and not has_coordinates:
        raise ValueError("Provide dataframe, table_id, or both target and table_name.")
    if frequency_max_distinct_percent is not None and (
        not math.isfinite(frequency_max_distinct_percent)
        or not 0.0 <= frequency_max_distinct_percent <= 100.0
    ):
        raise ValueError("frequency_max_distinct_percent must be finite and between 0.0 and 100.0 when supplied.")

    selected_frequency_columns = None if frequency_columns is None else list(frequency_columns)
    identity = None
    config = env = context = None
    if table_id is not None or has_coordinates:
        config, env, context = resolve_fabric_context()
        if table_id is not None:
            identity = resolve_catalogue_table_identity(config, env, table_id, context=context)
        else:
            identity = resolve_physical_table_identity(
                config, env, target=target, schema=schema, table_name=table_name
            )
        store_kind = str(identity.get("store_kind") or identity.get("store_type") or "").lower()
        if store_kind not in {"lakehouse", "warehouse"}:
            raise ValueError(f"Configured table has unsupported store kind {store_kind or '<blank>'!r}.")
        identity["store_kind"] = store_kind
        if dataframe is None:
            if store_kind == "lakehouse":
                dataframe = read_lakehouse_table(table_id=str(identity["table_id"]), context=context)
            else:
                dataframe = read_warehouse_table(
                    str(identity["schema"]), str(identity["table_name"]),
                    target=str(identity["target"]), context=context,
                )
            print(
                f"FabricOps: profiling governed table '{identity['table_id']}'. "
                "Profile and catalogue metadata will be persisted."
            )
        else:
            print(
                f"FabricOps: profiling supplied DataFrame against governed table '{identity['table_id']}'. "
                "Profile and catalogue metadata will be persisted."
            )
    else:
        print(
            "FabricOps: profiling supplied DataFrame only. No Data Catalogue or profiling metadata "
            "will be persisted because no table identity was provided."
        )

    statistical_profile = build_profile_dataframe(dataframe)
    selected_columns = _selected_frequency_columns(
        dataframe, statistical_profile, selected_frequency_columns, frequency_max_distinct_percent
    )
    frequency_profile = None
    if selected_columns:
        frequency_profile = build_frequency_distribution_dataframe(
            dataframe, columns=selected_columns, top_n=frequency_top_n
        )
    if identity is None:
        return {"profile": statistical_profile, "frequency_profile": frequency_profile}

    profile_snapshot_id = str(uuid4())
    profiled_df = _canonical_profiled_dataframe(
        statistical_profile,
        config=config,
        env=env,
        runtime_context=context,
        environment_name=env,
        table_id=identity["table_id"],
        profile_snapshot_id=profile_snapshot_id,
    ).cache()
    profiled_df.count()
    frequency_metadata_df = None
    if frequency_profile is not None:
        frequency_metadata_df = _frequency_metadata_dataframe(
            frequency_profile,
            profiled_df=profiled_df,
            table_id=identity["table_id"],
            config=config,
            env=env,
            runtime_context=context,
        )
    write_lakehouse_table_core(
        profiled_df,
        PROFILED_TABLE,
        target="metadata",
        schema=metadata_table_physical_schema(config, PROFILED_TABLE),
        context={"config": config, "env": env},
        mode="append",
    )
    _replace_frequency_rows(
        frequency_df=frequency_metadata_df,
        profiled_df=profiled_df,
        config=config,
        env=env,
        spark_session=dataframe.sparkSession,
    )
    catalogue_df = _catalogue_dataframe_from_profiled(
        profiled_df,
        source_df=dataframe,
        store_type=identity["store_kind"],
        layer=identity["target"],
        schema_name=identity["schema"],
        table_name=identity["table_name"],
        load_strategy=None,
        load_strategy_parameters_json=None,
    )
    _upsert_catalogue_identities(
        catalogue_df=catalogue_df,
        config=config,
        env=env,
        spark_session=dataframe.sparkSession,
    )
    return {"profile": profiled_df, "frequency_profile": frequency_profile}
