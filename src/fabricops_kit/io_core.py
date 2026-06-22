"""Lower-level Fabric IO implementations shared by package internals."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any
import re
import tempfile

from .config import _get_store, resolve_fabric_context

DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"


@dataclass(frozen=True)
class FabricStore:
    """Fabric lakehouse or warehouse connection details."""

    env: str
    workspace_id: str
    item_id: str
    name: str
    kind: str
    schema_enabled: bool = False
    schema: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        for field_name in ("env", "workspace_id", "item_id", "name", "kind"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        normalized_kind = self.kind.strip().lower()
        if normalized_kind not in {"lakehouse", "warehouse"}:
            raise ValueError("kind must be one of: lakehouse, warehouse.")
        object.__setattr__(self, "kind", normalized_kind)
        object.__setattr__(self, "schema_enabled", bool(self.schema_enabled))
        schema_value = None if self.schema is None else str(self.schema).strip()
        if self.schema_enabled and normalized_kind == "lakehouse":
            if not schema_value:
                raise ValueError("schema is required when schema_enabled is True for a lakehouse store.")
            if any(separator in schema_value for separator in ("/", "\\", ".")):
                raise ValueError("schema must be a simple schema name; do not use paths or dots.")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema_value):
                raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
        object.__setattr__(self, "schema", schema_value or None)

    @property
    def root(self) -> str:
        """Return the OneLake ABFSS root for lakehouse stores."""
        if self.kind != "lakehouse":
            raise ValueError("root is only available for lakehouse stores.")
        return f"abfss://{self.workspace_id}@onelake.dfs.fabric.microsoft.com/{self.item_id}"


# ---------------------------------------------------------------------------
# Utility layer: small pure helpers only.
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


def _resolve_lakehouse_table_identifier(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the Spark table identifier for an already-normalized lakehouse table."""
    return f"{schema_name}.{table_name}" if schema_name else table_name


# ---------------------------------------------------------------------------
# Validator layer: input shape and runtime-target validation.
# ---------------------------------------------------------------------------


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
        raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
    return value


def _normalize_write_mode(mode: str) -> str:
    """Return a supported Spark write mode."""
    value = str(mode or "").lower().strip()
    if value not in {"append", "overwrite", "errorifexists", "ignore"}:
        raise ValueError("mode must be one of append, overwrite, errorifexists, ignore.")
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


def _validate_select_query(query: str) -> str:
    """Return a safe warehouse read query shape for connector pushdown."""
    sql = str(query or "").strip()
    if not sql:
        raise ValueError("query must be a non-empty SQL SELECT statement.")
    if not sql.lower().lstrip().startswith(("select", "with")):
        raise ValueError("query must be a SELECT statement or a CTE ending in a SELECT statement.")
    return sql


def _validate_dataframe_writer(df) -> None:
    """Validate that the object exposes the Spark DataFrame write contract."""
    if not hasattr(df, "write"):
        raise ValueError("df must be a Spark DataFrame-like object with a write attribute.")


# ---------------------------------------------------------------------------
# Resolver layer: context, stores, physical paths, and connector targets.
# ---------------------------------------------------------------------------


def _get_spark(spark_session=None):
    """Return an explicit Spark session or the active notebook global spark."""
    if spark_session is not None:
        return spark_session
    try:
        return globals()["spark"]
    except KeyError as exc:
        raise RuntimeError("Spark session was not provided and global 'spark' was not found. Run this inside Fabric/Spark or pass spark_session explicitly.") from exc


def _resolve_target_store(target: str, expected_kind: str, *, context: dict[str, Any] | None = None) -> tuple[FabricStore, str]:
    """Resolve a configured Fabric target and validate its store kind."""
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    if expected_kind == "lakehouse":
        _validate_lakehouse_store(store, env, target)
    elif expected_kind == "warehouse":
        _validate_warehouse_store(store, env, target)
    else:
        raise ValueError("expected_kind must be one of: lakehouse, warehouse.")
    return store, env


def _resolve_lakehouse_schema(store: FabricStore, schema: str | None) -> str | None:
    """Resolve explicit or configured lakehouse schema names."""
    return _normalize_schema_name(schema if schema is not None else (store.schema if store.schema_enabled else None))


def _resolve_lakehouse_table_path(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the physical OneLake Delta table path."""
    table_relative_path = f"{schema_name}/{table_name}" if schema_name else table_name
    return _join_lakehouse_area_path(store, "Tables", table_relative_path)


def _lakehouse_file_path(store: FabricStore, relative_path: str) -> str:
    """Return an ABFSS path under a configured lakehouse Files area."""
    normalized_relative_path = _validate_relative_path(relative_path)
    return _join_lakehouse_area_path(store, "Files", normalized_relative_path)


def _resolve_lakehouse_table_location(store: FabricStore, table_name: str, schema: str | None) -> tuple[str, str | None, str]:
    """Resolve a lakehouse table to normalized table, schema, and path."""
    table_value = _normalize_table_name(table_name)
    schema_value = _resolve_lakehouse_schema(store, schema)
    return table_value, schema_value, _resolve_lakehouse_table_path(store, table_value, schema_value)


def _resolve_lakehouse_file_location(store: FabricStore, relative_path: str) -> tuple[str, str]:
    """Resolve a lakehouse Files path to normalized relative and ABFSS paths."""
    normalized_relative_path = _validate_relative_path(relative_path)
    return normalized_relative_path, _lakehouse_file_path(store, normalized_relative_path)


def _resolve_warehouse_table_location(store: FabricStore, schema: str, table_name: str) -> tuple[str, str, str]:
    """Resolve a warehouse table to normalized schema, table, and connector object."""
    schema_value = _normalize_schema_name(schema)
    table_value = _normalize_table_name(table_name)
    return schema_value, table_value, _build_warehouse_object_name(store.name, schema_value, table_value)


def configured_lakehouse_schema(config: Any, env: str, target: str) -> str | None:
    """Return the configured schema for a schema-enabled lakehouse target."""
    try:
        store = _get_store(config, env, target)
    except ValueError:
        return None
    if store.kind != "lakehouse" or not getattr(store, "schema_enabled", False):
        return None
    return _normalize_schema_name(getattr(store, "schema", None))


# ---------------------------------------------------------------------------
# Adapter layer: runtime connector and Spark/pandas calls.
# ---------------------------------------------------------------------------


def _require_fabric_connector() -> Any:
    """Return Fabric connector constants or raise a runtime-specific error."""
    try:
        import com.microsoft.spark.fabric  # noqa: F401
        from com.microsoft.spark.fabric.Constants import Constants
    except Exception as exc:
        raise RuntimeError("This function must run inside Microsoft Fabric Spark with com.microsoft.spark.fabric available.") from exc
    return Constants


def _read_delta_path(spark_obj, path: str):
    """Read a Delta path through Spark."""
    return spark_obj.read.format("delta").load(path)


def _read_csv_path(spark_obj, path: str, *, header: bool, options: dict[str, Any]):
    """Read a CSV path through Spark."""
    reader = spark_obj.read.option("header", header)
    for key, value in options.items():
        reader = reader.option(key, value)
    return reader.csv(path)


def _write_delta_path(df, path: str, *, mode: str, partition_by=None, options: dict[str, Any] | None = None) -> None:
    """Write a DataFrame to a Delta path through Spark."""
    writer = df.write.mode(mode).format("delta")
    if partition_by is not None:
        writer = writer.partitionBy(*partition_by) if isinstance(partition_by, (list, tuple)) else writer.partitionBy(partition_by)
    for key, value in (options or {}).items():
        writer = writer.option(key, value)
    writer.save(path)


def _read_warehouse_synapsesql(spark_obj, store: FabricStore, synapsesql_target: str):
    """Read from Fabric Warehouse through the Spark connector."""
    constants = _require_fabric_connector()
    return spark_obj.read.option(constants.WorkspaceId, store.workspace_id).option(constants.DatawarehouseId, store.item_id).synapsesql(synapsesql_target)


def _write_warehouse_synapsesql(df, store: FabricStore, synapsesql_target: str, *, mode: str) -> None:
    """Write to Fabric Warehouse through the Spark connector."""
    constants = _require_fabric_connector()
    df.write.mode(mode).option(constants.WorkspaceId, store.workspace_id).option(constants.DatawarehouseId, store.item_id).synapsesql(synapsesql_target)


def _read_excel_file(spark_obj, lakehouse_path: str, *, sheet_name, read_excel_kwargs: dict[str, Any]):
    """Read an Excel file from binary Spark content and convert it to a Spark DataFrame."""
    bin_df = spark_obj.read.format("binaryFile").option("recursiveFileLookup", "false").load(lakehouse_path)
    if bin_df.count() == 0:
        raise FileNotFoundError(f"No file found at path: {lakehouse_path}")
    content = bin_df.select("content").collect()[0][0]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_file.write(bytearray(content))
        temp_file_path = temp_file.name
    pandas_df = _load_pandas().read_excel(temp_file_path, sheet_name=sheet_name, **read_excel_kwargs)
    return spark_obj.createDataFrame(pandas_df)


def _convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=True):
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


# ---------------------------------------------------------------------------
# Internal workflow layer: public wrappers delegate one-to-one to these.
# ---------------------------------------------------------------------------


def read_lakehouse_table_core(table_name: str, *, target: str, schema: str | None = None, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Lakehouse Delta table for package-internal callers."""
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    _table_value, _schema_value, path = _resolve_lakehouse_table_location(store, table_name, schema)
    return _read_delta_path(_get_spark(spark_session), path)


def write_lakehouse_table_core(df, table_name: str, *, target: str, schema: str | None, mode: str, partition_by=None, repartition_by=None, options=None, verbose: bool = True, context=None):
    """Write a Lakehouse Delta table for package-internal callers."""
    _validate_dataframe_writer(df)
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    _table_value, _schema_value, path = _resolve_lakehouse_table_location(store, table_name, schema)
    normalized_mode = _normalize_write_mode(mode)
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = df.repartition(*repartition_by) if not (repartition_by and isinstance(repartition_by[0], int)) else df.repartition(repartition_by[0], *repartition_by[1:])
        else:
            df = df.repartition(repartition_by)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    _write_delta_path(df, path, mode=normalized_mode, partition_by=partition_by, options=options)


def read_lakehouse_csv_core(relative_path: str, *, target: str, spark_session=None, header: bool = True, context: dict[str, Any] | None = None, **options):
    """Read Lakehouse CSV files for package-internal callers."""
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    _relative_path, path = _resolve_lakehouse_file_location(store, relative_path)
    return _read_csv_path(_get_spark(spark_session), path, header=header, options=options)


def read_lakehouse_parquet_core(relative_path: str, *, target: str, verbose: bool = True, spark_session=None, context: dict[str, Any] | None = None):
    """Read Lakehouse Parquet files for package-internal callers."""
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    normalized_relative_path, orig_spark_path = _resolve_lakehouse_file_location(store, relative_path)
    spark_obj = _get_spark(spark_session)
    parts = normalized_relative_path.split("/")
    if len(parts) < 2:
        raise ValueError("relative_path should look like folder/file.parquet or folder/subfolder/file.parquet.")
    tsus_dir = parts[:-2] + [parts[-2] + "_tsus"]
    tsus_relative_path = "/".join(tsus_dir + [parts[-1]])
    tsus_spark_path = _lakehouse_file_path(store, tsus_relative_path)
    orig_local_path = f"/lakehouse/default/Files/{normalized_relative_path}"
    tsus_local_path = f"/lakehouse/default/Files/{tsus_relative_path}"
    if verbose:
        print(f"Try Spark read: {orig_spark_path}")
    try:
        df = spark_obj.read.parquet(orig_spark_path)
        _ = df.limit(1).collect()
        if verbose:
            print("SUCCESS: Spark read original path.")
        return df
    except Exception as exc:
        if verbose:
            print(f"Original Parquet read failed. Will try fallback path. Exception: {exc}")
    for try_convert in range(2):
        if verbose:
            print(f"Try Spark read: {tsus_spark_path}{' after single-file convert' if try_convert else ''}")
        try:
            df = spark_obj.read.parquet(tsus_spark_path)
            _ = df.limit(1).collect()
            if verbose:
                print("SUCCESS: Spark read _tsus path.")
            return df
        except Exception as exc:
            msg = str(exc)
            path_not_found = "[PATH_NOT_FOUND]" in msg or "Path does not exist" in msg or "No such file or directory" in msg
            if try_convert == 0 and path_not_found:
                if verbose:
                    print("PATH NOT FOUND for _tsus parquet. Will convert one file and retry.")
                try:
                    mssparkutils.fs.mkdirs(_lakehouse_file_path(store, "/".join(tsus_dir)))
                except Exception:
                    pass
                _convert_single_parquet_ns_to_us(local_in_path=orig_local_path, local_out_path=tsus_local_path, verbose=verbose)
            else:
                if verbose:
                    print(f"FAILED: Spark read _tsus path. Exception: {exc}")
                break
    raise RuntimeError("Failed to read from both original and _tsus Parquet paths.")


def read_lakehouse_excel_core(relative_path: str, *, target: str, sheet_name=0, spark_session=None, context: dict[str, Any] | None = None, **read_excel_kwargs):
    """Read Lakehouse Excel files for package-internal callers."""
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    _relative_path, lakehouse_path = _resolve_lakehouse_file_location(store, relative_path)
    return _read_excel_file(_get_spark(spark_session), lakehouse_path, sheet_name=sheet_name, read_excel_kwargs=read_excel_kwargs)


def read_warehouse_table_core(schema: str, table_name: str, *, target: str, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Warehouse table for package-internal callers."""
    store, _env = _resolve_target_store(target, "warehouse", context=context)
    _schema_value, _table_value, object_name = _resolve_warehouse_table_location(store, schema, table_name)
    return _read_warehouse_synapsesql(_get_spark(spark_session), store, object_name)


def read_warehouse_query_core(query: str, *, target: str, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Warehouse SQL query for package-internal callers."""
    store, _env = _resolve_target_store(target, "warehouse", context=context)
    sql = _validate_select_query(query)
    return _read_warehouse_synapsesql(_get_spark(spark_session), store, sql)


def write_warehouse_table_core(df, schema: str, table_name: str, *, target: str, mode: str, context: dict[str, Any] | None = None):
    """Write a Warehouse table for package-internal callers."""
    _validate_dataframe_writer(df)
    store, _env = _resolve_target_store(target, "warehouse", context=context)
    _schema_value, _table_value, object_name = _resolve_warehouse_table_location(store, schema, table_name)
    _write_warehouse_synapsesql(df, store, object_name, mode=mode)
