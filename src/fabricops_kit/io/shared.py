"""Shared internal IO utilities used by public IO owner files."""

from __future__ import annotations

from importlib import import_module
from typing import Any
import re
import tempfile

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


def _resolve_lakehouse_table_identifier(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the Spark table identifier for a normalized lakehouse table."""
    return f"{schema_name}.{table_name}" if schema_name else table_name


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
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = (
                df.repartition(*repartition_by)
                if not (repartition_by and isinstance(repartition_by[0], int))
                else df.repartition(repartition_by[0], *repartition_by[1:])
            )
        else:
            df = df.repartition(repartition_by)
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
