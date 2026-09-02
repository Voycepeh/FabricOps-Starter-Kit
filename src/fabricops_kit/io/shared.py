"""Shared internal IO utilities used by public IO owner files."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Mapping
import re
import tempfile
from uuid import uuid4

from fabricops_kit.config import FabricStore
from fabricops_kit.config.shared import get_store, resolve_fabric_context

DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"


# ---------------------------------------------------------------------------
# Same-file private helpers for shared IO implementation details.
# ---------------------------------------------------------------------------


def _load_pandas() -> Any:
    """Return pandas for Excel/Parquet helpers that need it."""
    return import_module("pandas")


def _join_lakehouse_area_path(store: FabricStore, area: str, relative_path: str) -> str:
    """Return an ABFSS path under a lakehouse area."""
    return f"{store.root.rstrip('/')}/{area.strip('/')}/{relative_path.strip('/')}"


def _build_warehouse_object_name(warehouse_name: str, schema_name: str, table_name: str) -> str:
    """Return the connector warehouse object name."""
    return f"{warehouse_name}.{schema_name}.{table_name}"


def _normalize_table_name(table: str) -> str:
    """Return a safe table identifier."""
    value = str(table or "").strip()
    if not value:
        raise ValueError("table is required.")
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("table must be a simple table name; pass schema separately and do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("table must contain only letters, numbers, and underscores, and must not start with a number.")
    return value


def _normalize_schema_name(schema: str | None) -> str | None:
    """Return a safe schema identifier, or None when omitted."""
    if schema is None:
        return None
    value = str(schema).strip()
    if not value:
        raise ValueError("schema must be a non-empty identifier when provided.")
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("schema must be a simple schema name; do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(
            "schema must contain only letters, numbers, and underscores, and must not start with a number."
        )
    return value


def _validate_lakehouse_store(store: FabricStore, env: str, target: str) -> None:
    """Validate that a resolved store is a lakehouse."""
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")


def _validate_warehouse_store(store: FabricStore, env: str, target: str) -> None:
    """Validate that a resolved store is a warehouse."""
    if store.kind != "warehouse":
        raise ValueError(f"Target '{env}/{target}' is not a warehouse store.")


def _validate_relative_path(relative_path: str) -> str:
    """Return a normalized lakehouse file path fragment."""
    value = str(relative_path or "").strip().lstrip("/")
    if not value:
        raise ValueError("relative_path must be a non-empty string.")
    if value.startswith("Files/"):
        value = value[len("Files/") :]
    return value


def _resolve_lakehouse_schema(store: FabricStore, schema: str | None) -> str | None:
    """Resolve explicit or configured lakehouse schema names."""
    return _normalize_schema_name(schema if schema is not None else (store.schema if store.schema_enabled else None))


def _resolve_lakehouse_table_path(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the physical OneLake Delta table path."""
    table_relative_path = f"{schema_name}/{table_name}" if schema_name else table_name
    return _join_lakehouse_area_path(store, "Tables", table_relative_path)


def _require_fabric_connector() -> Any:
    """Return Fabric connector constants or raise a runtime-specific error."""
    try:
        import com.microsoft.spark.fabric  # noqa: F401
        from com.microsoft.spark.fabric.Constants import Constants
    except Exception as exc:
        raise RuntimeError(
            "This function must run inside Microsoft Fabric Spark with com.microsoft.spark.fabric available."
        ) from exc
    return Constants


# ---------------------------------------------------------------------------
# Architecture-visible shared IO helpers used by public IO owner files.
# ---------------------------------------------------------------------------


def get_spark_session(spark_session=None):
    """Return the explicit or active notebook Spark session."""
    if spark_session is not None:
        return spark_session
    try:
        return globals()["spark"]
    except KeyError as exc:
        raise RuntimeError(
            "Spark session was not provided and global 'spark' was not found. Run this inside Fabric/Spark or pass spark_session explicitly."
        ) from exc


def resolve_target_store(
    target: str, expected_kind: str, *, context: dict[str, Any] | None = None
) -> tuple[FabricStore, str]:
    """Resolve and validate a configured Fabric target store."""
    config, env, _context = resolve_fabric_context(context=context)
    store = get_store(config, env, target)
    if expected_kind == "lakehouse":
        _validate_lakehouse_store(store, env, target)
    elif expected_kind == "warehouse":
        _validate_warehouse_store(store, env, target)
    else:
        raise ValueError("expected_kind must be one of: lakehouse, warehouse.")
    return store, env


def resolve_configured_file_path(
    target: str, relative_path: str, *, context: dict[str, Any] | None = None
) -> tuple[FabricStore, str, str]:
    """Resolve a logical target and relative file path through Fabric config."""
    store, _env = resolve_target_store(target, "lakehouse", context=context)
    normalized_relative_path, path = resolve_lakehouse_file_location(store, relative_path)
    return store, normalized_relative_path, path


def resolve_configured_lakehouse_table(
    target: str, table_name: str, schema: str | None, *, context: dict[str, Any] | None = None
) -> tuple[FabricStore, str, str | None, str]:
    """Resolve a logical target and table through configured lakehouse metadata."""
    store, _env = resolve_target_store(target, "lakehouse", context=context)
    table_value, schema_value, path = resolve_lakehouse_table_location(store, table_name, schema)
    return store, table_value, schema_value, path


def resolve_configured_warehouse_table(
    target: str, schema: str, table_name: str, *, context: dict[str, Any] | None = None
) -> tuple[FabricStore, str, str, str]:
    """Resolve a logical target and table through configured warehouse metadata."""
    store, _env = resolve_target_store(target, "warehouse", context=context)
    schema_value, table_value, object_name = resolve_warehouse_table_location(store, schema, table_name)
    return store, schema_value, table_value, object_name


def resolve_configured_warehouse_query_target(target: str, *, context: dict[str, Any] | None = None) -> FabricStore:
    """Resolve a logical target for Fabric warehouse query execution."""
    store, _env = resolve_target_store(target, "warehouse", context=context)
    return store


def resolve_lakehouse_table_location(
    store: FabricStore, table_name: str, schema: str | None
) -> tuple[str, str | None, str]:
    """Resolve a Lakehouse table to normalized table, schema, and ABFSS path."""
    table_value = _normalize_table_name(table_name)
    schema_value = _resolve_lakehouse_schema(store, schema)
    return table_value, schema_value, _resolve_lakehouse_table_path(store, table_value, schema_value)


def resolve_lakehouse_file_location(store: FabricStore, relative_path: str) -> tuple[str, str]:
    """Resolve a Lakehouse Files path to normalized relative and ABFSS paths."""
    normalized_relative_path = _validate_relative_path(relative_path)
    return normalized_relative_path, resolve_lakehouse_file_path(store, normalized_relative_path)


def resolve_lakehouse_file_path(store: FabricStore, relative_path: str) -> str:
    """Resolve a normalized Lakehouse Files relative path to an ABFSS path."""
    normalized_relative_path = _validate_relative_path(relative_path)
    return _join_lakehouse_area_path(store, "Files", normalized_relative_path)


def resolve_warehouse_table_location(store: FabricStore, schema: str, table_name: str) -> tuple[str, str, str]:
    """Resolve a Warehouse table to normalized schema, table, and connector target."""
    schema_value = _normalize_schema_name(schema)
    table_value = _normalize_table_name(table_name)
    return schema_value, table_value, _build_warehouse_object_name(store.name, schema_value, table_value)


def normalize_write_mode(mode: str) -> str:
    """Return a supported Spark write mode."""
    value = str(mode or "").lower().strip()
    if value not in {"append", "overwrite", "errorifexists", "ignore"}:
        raise ValueError("mode must be one of append, overwrite, errorifexists, ignore.")
    return value


def validate_dataframe_writer(df) -> None:
    """Validate that an object exposes the Spark DataFrame write contract."""
    if not hasattr(df, "write"):
        raise ValueError("df must be a Spark DataFrame-like object with a write attribute.")


def validate_select_query(query: str) -> str:
    """Validate and normalize SQL suitable for Warehouse pushdown."""
    sql = str(query or "").strip()
    if not sql:
        raise ValueError("query must be a non-empty SQL SELECT statement.")
    if not sql.lower().lstrip().startswith(("select", "with")):
        raise ValueError("query must be a SELECT statement or a CTE ending in a SELECT statement.")
    return sql


def read_delta_path(spark_obj, path: str, *, options: dict[str, Any] | None = None):
    """Read a Delta path through Spark."""
    reader = spark_obj.read.format("delta")
    for key, value in (options or {}).items():
        reader = reader.option(key, value)
    return reader.load(path)


def read_csv_path(spark_obj, path: str, *, header: bool, options: dict[str, Any]):
    """Read a CSV path through Spark."""
    reader = spark_obj.read.option("header", header)
    for key, value in options.items():
        reader = reader.option(key, value)
    return reader.csv(path)


def read_json_path(spark_obj, path: str, *, options: dict[str, Any]):
    """Read a JSON path through Spark."""
    reader = spark_obj.read
    for key, value in options.items():
        reader = reader.option(key, value)
    return reader.json(path)


def repartition_dataframe_for_write(df, repartition_by):
    """Return ``df`` or a repartitioned DataFrame for a write operation."""
    if repartition_by is None:
        return df
    if isinstance(repartition_by, bool):
        raise ValueError(
            "repartition_by must be a positive integer, column name, or non-empty list/tuple of column names."
        )
    if isinstance(repartition_by, int):
        if repartition_by <= 0:
            raise ValueError("repartition_by integer partition count must be greater than zero.")
        return df.repartition(repartition_by)
    partition_count = None
    if isinstance(repartition_by, str):
        columns = [repartition_by]
    elif isinstance(repartition_by, (list, tuple)):
        if not repartition_by:
            raise ValueError("repartition_by column list or tuple must not be empty.")
        values = list(repartition_by)
        if isinstance(values[0], bool):
            raise ValueError("repartition_by partition count must be a positive integer when supplied.")
        if isinstance(values[0], int):
            partition_count = values.pop(0)
            if partition_count <= 0:
                raise ValueError("repartition_by integer partition count must be greater than zero.")
            if not values:
                return df.repartition(partition_count)
        if not all(isinstance(column, str) for column in values):
            raise ValueError(
                "repartition_by list or tuple values must be column names, optionally preceded by a positive integer."
            )
        columns = values
    else:
        raise ValueError(
            "repartition_by must be a positive integer, column name, or non-empty list/tuple of column names."
        )

    normalized_columns = [column.strip() for column in columns]
    if any(not column for column in normalized_columns):
        raise ValueError("repartition_by column names must be non-empty strings.")
    available_columns = list(getattr(df, "columns", []) or [])
    if available_columns:
        missing = [column for column in normalized_columns if column not in available_columns]
        if missing:
            raise ValueError(f"repartition_by column(s) do not exist in df: {', '.join(missing)}.")
    if partition_count is not None:
        return df.repartition(partition_count, *normalized_columns)
    return df.repartition(*normalized_columns)


def write_delta_path(df, path: str, *, mode: str, partition_by=None, options: dict[str, Any] | None = None) -> None:
    """Write a DataFrame to a Delta path through Spark."""
    writer = df.write.mode(mode).format("delta")
    if partition_by is not None:
        writer = (
            writer.partitionBy(*partition_by)
            if isinstance(partition_by, (list, tuple))
            else writer.partitionBy(partition_by)
        )
    for key, value in (options or {}).items():
        writer = writer.option(key, value)
    writer.save(path)


def configured_lakehouse_schema(config: Any, env: str, target: str) -> str | None:
    """Return the configured schema for a schema-enabled lakehouse target."""
    try:
        store = get_store(config, env, target)
    except ValueError:
        return None
    if store.kind != "lakehouse" or not getattr(store, "schema_enabled", False):
        return None
    return _normalize_schema_name(getattr(store, "schema", None))


def read_lakehouse_table_core(
    table_name: str,
    *,
    target: str,
    schema: str | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
):
    """Read a configured Lakehouse Delta table for internal workflows."""
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    return read_delta_path(get_spark_session(spark_session), path, options=options)


def write_lakehouse_table_core(
    df,
    table_name: str,
    *,
    target: str,
    schema: str | None = None,
    mode: str = "append",
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose: bool = True,
    context=None,
):
    """Write a configured Lakehouse Delta table for internal workflows."""
    validate_dataframe_writer(df)
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    normalized_mode = normalize_write_mode(mode)
    df = repartition_dataframe_for_write(df, repartition_by)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    write_delta_path(df, path, mode=normalized_mode, partition_by=partition_by, options=options)


def read_warehouse_synapsesql(
    spark_obj, store: FabricStore, synapsesql_target: str, *, options: dict[str, Any] | None = None
):
    """Read from Fabric Warehouse through the Spark connector."""
    constants = _require_fabric_connector()
    reader = (
        spark_obj.read.option(constants.WorkspaceId, store.workspace_id)
        .option(constants.DatawarehouseId, store.item_id)
        .option(constants.DatabaseName, store.name)
    )
    for key, value in (options or {}).items():
        reader = reader.option(key, value)
    return reader.synapsesql(synapsesql_target)


def read_warehouse_query_core(
    query: str, *, target: str = "warehouse", spark_session=None,
    context: dict[str, Any] | None = None, options: dict[str, Any] | None = None,
):
    """Execute a validated read-only Warehouse query for internal workflows."""
    store = resolve_configured_warehouse_query_target(target, context=context)
    sql = validate_select_query(query)
    return read_warehouse_synapsesql(get_spark_session(spark_session), store, sql, options=options)


def write_warehouse_synapsesql(
    df, store: FabricStore, synapsesql_target: str, *, mode: str, options: dict[str, Any] | None = None
) -> None:
    """Write to Fabric Warehouse through the Spark connector."""
    constants = _require_fabric_connector()
    writer = (
        df.write.mode(mode)
        .option(constants.WorkspaceId, store.workspace_id)
        .option(constants.DatawarehouseId, store.item_id)
    )
    for key, value in (options or {}).items():
        writer = writer.option(key, value)
    writer.synapsesql(synapsesql_target)


def execute_warehouse_sql(
    spark_obj, store: FabricStore, sql: str, *, options: dict[str, Any] | None = None
) -> None:
    """Execute a Warehouse T-SQL mutation batch through the configured connector."""
    read_warehouse_synapsesql(spark_obj, store, sql, options=options).collect()


def _quoted_warehouse_identifier(value: str) -> str:
    """Return a validated Warehouse identifier quoted for T-SQL."""
    return f"[{_normalize_table_name(value)}]"


def _warehouse_column_list(columns: list[str], *, alias: str | None = None) -> str:
    """Return a safe comma-separated T-SQL column list."""
    prefix = f"{alias}." if alias else ""
    return ", ".join(f"{prefix}{_quoted_warehouse_identifier(column)}" for column in columns)


def _warehouse_null_safe_difference(columns: list[str], left: str, right: str) -> str:
    """Return a null-safe T-SQL difference predicate."""
    if not columns:
        return "1 = 0"
    return " OR ".join(
        f"({left}.{_quoted_warehouse_identifier(column)} <> {right}.{_quoted_warehouse_identifier(column)} "
        f"OR ({left}.{_quoted_warehouse_identifier(column)} IS NULL AND "
        f"{right}.{_quoted_warehouse_identifier(column)} IS NOT NULL) "
        f"OR ({left}.{_quoted_warehouse_identifier(column)} IS NOT NULL AND "
        f"{right}.{_quoted_warehouse_identifier(column)} IS NULL))"
        for column in columns
    )


def _drop_warehouse_stage_best_effort(
    spark_obj,
    store: FabricStore,
    schema_name: str,
    stage_name: str,
    *,
    options: dict[str, Any] | None = None,
) -> None:
    """Try to remove a failed run's Warehouse staging table."""
    qstage = f"{_quoted_warehouse_identifier(schema_name)}.{_quoted_warehouse_identifier(stage_name)}"
    sql = f"""IF OBJECT_ID(N'{schema_name}.{stage_name}', N'U') IS NOT NULL DROP TABLE {qstage};
SELECT CAST(1 AS int) AS fabricops_stage_cleanup_attempted;"""
    try:
        execute_warehouse_sql(spark_obj, store, sql, options=options)
    except Exception:
        # Cleanup is deliberately secondary: callers must receive the original
        # staging or target-mutation error even when this attempt also fails.
        pass


def execute_warehouse_processing(
    df,
    *,
    schema: str,
    table_name: str,
    target: str,
    processing: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> None:
    """Apply a validated governed SCD definition to a Fabric Warehouse target."""
    from pyspark.sql import functions as F

    from fabricops_kit.pipeline.shared import (
        validated_processing,
        resolve_scd1_business_columns,
        resolve_scd2_tracked_columns,
    )

    definition = validated_processing(dict(processing))
    strategy = definition["load_strategy"]
    if strategy not in {"scd1", "scd2"}:
        raise ValueError("Warehouse governed processing requires scd1 or scd2.")
    columns = list(getattr(df, "columns", ()) or ())
    if not columns or len(columns) != len(set(columns)):
        raise ValueError("Incoming Warehouse SCD data must have unique named columns.")
    for column in columns:
        _normalize_table_name(column)
    keys = list(definition["key_columns"])
    missing = sorted(set(keys) - set(columns))
    if missing:
        raise ValueError(f"Incoming Warehouse SCD data is missing key columns: {', '.join(missing)}.")
    if df.groupBy(*keys).count().where(F.col("count") > 1).limit(1).count():
        raise ValueError("Incoming target scope contains duplicate business keys.")
    tracked: list[str] = []
    if strategy == "scd2":
        required = {definition["effective_column"], "_effective_from", "_effective_to", "_is_current"}
        missing = sorted(required - set(columns))
        if missing:
            raise ValueError(f"Incoming Warehouse SCD2 data is missing required columns: {', '.join(missing)}.")
        tracked = resolve_scd2_tracked_columns(columns, definition)

    store, schema_value, table_value, _object_name = resolve_configured_warehouse_table(
        target, schema, table_name, context=dict(context or {})
    )
    stage_name = f"_fabricops_scd_{uuid4().hex}"
    stage_object = _build_warehouse_object_name(store.name, schema_value, stage_name)

    qschema = _quoted_warehouse_identifier(schema_value)
    qtarget = f"{qschema}.{_quoted_warehouse_identifier(table_value)}"
    qstage = f"{qschema}.{_quoted_warehouse_identifier(stage_name)}"
    join = " AND ".join(
        f"target.{_quoted_warehouse_identifier(key)} = source.{_quoted_warehouse_identifier(key)}" for key in keys
    )
    incoming_columns = _warehouse_column_list(columns)
    source_columns = _warehouse_column_list(columns, alias="source")
    schema_checks = f"""
IF OBJECT_ID(N'{schema_value}.{table_value}', N'U') IS NOT NULL
AND (EXISTS (SELECT name, system_type_id, max_length, precision, scale, is_nullable
            FROM sys.columns WHERE object_id = OBJECT_ID(N'{schema_value}.{table_value}')
            EXCEPT SELECT name, system_type_id, max_length, precision, scale, is_nullable
            FROM sys.columns WHERE object_id = OBJECT_ID(N'{schema_value}.{stage_name}')))
 OR EXISTS (SELECT name, system_type_id, max_length, precision, scale, is_nullable
            FROM sys.columns WHERE object_id = OBJECT_ID(N'{schema_value}.{stage_name}')
            EXCEPT SELECT name, system_type_id, max_length, precision, scale, is_nullable
            FROM sys.columns WHERE object_id = OBJECT_ID(N'{schema_value}.{table_value}')))
    THROW 50001, 'Warehouse SCD target and incoming schemas are incompatible.', 1;
"""
    if strategy == "scd1":
        business = resolve_scd1_business_columns(columns, keys)
        update_columns = [column for column in columns if column not in keys]
        updates = ", ".join(
            f"target.{_quoted_warehouse_identifier(column)} = source.{_quoted_warehouse_identifier(column)}"
            for column in update_columns
        )
        technical = [column for column in update_columns if column not in business]
        differences = [
            value for value in (
                _warehouse_null_safe_difference(business, "target", "source") if business else "",
                _warehouse_null_safe_difference(technical, "target", "source") if technical else "",
            ) if value
        ]
        matched = f"WHEN MATCHED AND ({' OR '.join(differences)}) THEN UPDATE SET {updates}" if differences else ""
        mutation = f"""
IF OBJECT_ID(N'{schema_value}.{table_value}', N'U') IS NULL
    SELECT * INTO {qtarget} FROM {qstage};
ELSE
    MERGE {qtarget} AS target
    USING {qstage} AS source ON {join}
    {matched}
    WHEN NOT MATCHED BY TARGET THEN INSERT ({incoming_columns}) VALUES ({source_columns});
"""
    else:
        effective = _quoted_warehouse_identifier(str(definition["effective_column"]))
        changed = _warehouse_null_safe_difference(tracked, "target", "source")
        technical = [
            column for column in columns
            if column not in {*keys, *tracked, definition["effective_column"], "_effective_from", "_effective_to", "_is_current"}
        ]
        technical_updates = ", ".join(
            f"target.{_quoted_warehouse_identifier(column)} = source.{_quoted_warehouse_identifier(column)}"
            for column in technical
        )
        unchanged_update = f"""
    UPDATE target SET {technical_updates}
    FROM {qtarget} target JOIN {qstage} source ON {join}
    WHERE target.[_is_current] = 1 AND NOT ({changed});
""" if technical_updates else ""
        mutation = f"""
IF OBJECT_ID(N'{schema_value}.{table_value}', N'U') IS NULL
    SELECT * INTO {qtarget} FROM {qstage};
ELSE
BEGIN
    IF EXISTS (SELECT 1 FROM {qtarget} GROUP BY {_warehouse_column_list(keys)}
               HAVING SUM(CASE WHEN [_is_current] = 1 THEN 1 ELSE 0 END) > 1)
        THROW 50002, 'SCD2 target contains multiple current records for a business key.', 1;
    IF EXISTS (SELECT 1 FROM {qtarget} target JOIN {qstage} source ON {join}
               WHERE target.[_is_current] = 1 AND source.{effective} < target.[_effective_from])
        THROW 50003, 'Incoming SCD2 effective time moves backwards.', 1;

    UPDATE target SET target.[_effective_to] = source.{effective}, target.[_is_current] = 0
    FROM {qtarget} target JOIN {qstage} source ON {join}
    WHERE target.[_is_current] = 1 AND ({changed});
{unchanged_update}

    INSERT INTO {qtarget} ({incoming_columns})
    SELECT {source_columns} FROM {qstage} source
    WHERE NOT EXISTS (
        SELECT 1 FROM {qtarget} target WHERE {join} AND target.[_is_current] = 1
          AND NOT ({changed})
    );
END;
"""
    sql = f"""SET XACT_ABORT ON;
BEGIN TRY
BEGIN TRANSACTION;
{schema_checks}
{mutation}
DROP TABLE {qstage};
COMMIT TRANSACTION;
SELECT CAST(1 AS int) AS fabricops_scd_committed;
END TRY
BEGIN CATCH
IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
IF OBJECT_ID(N'{schema_value}.{stage_name}', N'U') IS NOT NULL DROP TABLE {qstage};
THROW;
END CATCH;"""
    try:
        write_warehouse_synapsesql(df, store, stage_object, mode="overwrite", options=options)
        execute_warehouse_sql(df.sparkSession, store, sql, options=options)
    except Exception:
        _drop_warehouse_stage_best_effort(
            df.sparkSession,
            store,
            schema_value,
            stage_name,
            options=options,
        )
        raise


def read_excel_file(spark_obj, lakehouse_path: str, *, sheet_name, read_excel_kwargs: dict[str, Any]):
    """Read Excel binary content from Lakehouse Files and return a Spark DataFrame."""
    bin_df = spark_obj.read.format("binaryFile").option("recursiveFileLookup", "false").load(lakehouse_path)
    if bin_df.count() == 0:
        raise FileNotFoundError(f"No file found at path: {lakehouse_path}")
    content = bin_df.select("content").collect()[0][0]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_file.write(bytearray(content))
        temp_file_path = temp_file.name
    pandas_df = _load_pandas().read_excel(temp_file_path, sheet_name=sheet_name, **read_excel_kwargs)
    return spark_obj.createDataFrame(pandas_df)


def convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=True):
    """Convert one local Parquet file from nanosecond to microsecond timestamps."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    try:
        if verbose:
            print(f"Reading with pyarrow: {local_in_path}")
            print(f"Writing us timestamps to: {local_out_path}")
        pdf = import_module("pandas").read_parquet(local_in_path, engine="pyarrow")
        table = pa.Table.from_pandas(pdf, preserve_index=False)
        pq.write_table(table, local_out_path, coerce_timestamps="us", allow_truncated_timestamps=True)
        if verbose:
            print(f"done: {local_out_path}")
    except Exception as exc:
        print(f"FAILED converting ns to us for file {local_in_path}: {exc}")


def validate_processing_scope(processing_scope: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize a governed physical-read scope."""
    if not isinstance(processing_scope, Mapping):
        raise ValueError("processing_scope must be a mapping with a supported scope type.")
    scope_type = str(processing_scope.get("type") or "").strip()
    if scope_type not in {"skip", "full_dataset", "watermark", "partition"}:
        raise ValueError("processing_scope type must be one of: skip, full_dataset, watermark, partition.")
    if scope_type in {"skip", "full_dataset"}:
        return {"type": scope_type}

    raw_column = processing_scope.get("column")
    if raw_column is None or not str(raw_column).strip():
        raise ValueError(f"{scope_type} processing_scope requires column.")
    try:
        column = _normalize_table_name(raw_column)
    except ValueError as exc:
        raise ValueError(f"{scope_type} processing_scope column must be a simple identifier.") from exc
    if scope_type == "watermark":
        if "lower_bound" not in processing_scope or processing_scope["lower_bound"] is None:
            raise ValueError("watermark processing_scope requires lower_bound.")
        if "upper_bound" not in processing_scope or processing_scope["upper_bound"] is None:
            raise ValueError("watermark processing_scope requires upper_bound.")
        return {
            "type": scope_type,
            "column": column,
            "lower_bound": processing_scope["lower_bound"],
            "upper_bound": processing_scope["upper_bound"],
        }

    values = processing_scope.get("values")
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError("partition processing_scope requires a non-empty values list or tuple.")
    if any(value is None for value in values):
        raise ValueError("partition processing_scope values must not contain None.")
    return {"type": scope_type, "column": column, "values": list(values)}


def apply_lakehouse_processing_scope(dataframe, processing_scope: Mapping[str, Any]):
    """Apply a validated governed scope to a lazy Lakehouse DataFrame."""
    scope = validate_processing_scope(processing_scope)
    if scope["type"] == "skip":
        raise ValueError("The current source was resolved to skip and must not be read.")
    if scope["type"] == "full_dataset":
        return dataframe
    functions = import_module("pyspark.sql.functions")
    column = functions.col(scope["column"])
    if scope["type"] == "watermark":
        return dataframe.where((column > functions.lit(scope["lower_bound"])) & (column <= functions.lit(scope["upper_bound"])))
    return dataframe.where(column.isin(scope["values"]))


def _warehouse_sql_literal(value: Any) -> str:
    """Return one safely encoded SQL literal for a governed scope value."""
    from datetime import date, datetime
    from decimal import Decimal
    import math
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, Decimal)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("processing_scope numeric values must be finite.")
        return repr(value)
    if isinstance(value, datetime):
        text = value.isoformat(sep=" ")
    elif isinstance(value, date):
        text = value.isoformat()
    elif isinstance(value, str):
        text = value
    else:
        raise ValueError(f"Unsupported processing_scope value type: {type(value).__name__}.")
    return "'" + text.replace("'", "''") + "'"


def build_warehouse_scoped_query(schema: str, table_name: str, processing_scope: Mapping[str, Any]) -> str | None:
    """Build a validated single-table Warehouse query for a governed scope."""
    schema_value = _normalize_schema_name(schema)
    table_value = _normalize_table_name(table_name)
    scope = validate_processing_scope(processing_scope)
    if scope["type"] == "skip":
        raise ValueError("The current source was resolved to skip and must not be read.")
    if scope["type"] == "full_dataset":
        return None
    column = scope["column"]
    source = f"[{schema_value}].[{table_value}]"
    if scope["type"] == "watermark":
        lower = _warehouse_sql_literal(scope["lower_bound"])
        upper = _warehouse_sql_literal(scope["upper_bound"])
        return f"SELECT * FROM {source} WHERE [{column}] > {lower} AND [{column}] <= {upper}"
    values = ", ".join(_warehouse_sql_literal(value) for value in scope["values"])
    return f"SELECT * FROM {source} WHERE [{column}] IN ({values})"
