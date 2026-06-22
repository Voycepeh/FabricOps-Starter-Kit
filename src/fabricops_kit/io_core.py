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


def _load_pandas() -> Any:
    """Return pandas for Excel/Parquet helpers that need it."""
    return import_module("pandas")


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


def _get_spark(spark_session=None):
    """Return an explicit Spark session or the active notebook global spark."""
    if spark_session is not None:
        return spark_session
    try:
        return globals()["spark"]
    except KeyError as exc:
        raise RuntimeError("Spark session was not provided and global 'spark' was not found. Run this inside Fabric/Spark or pass spark_session explicitly.") from exc


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


def _resolve_lakehouse_table_path(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the physical OneLake Delta table path."""
    table_relative_path = f"{schema_name}/{table_name}" if schema_name else table_name
    return f"{store.root.rstrip('/')}/Tables/{table_relative_path}"


def _lakehouse_file_path(store: FabricStore, relative_path: str) -> str:
    """Return an ABFSS path under a configured lakehouse Files area."""
    normalized_relative_path = str(relative_path).strip().lstrip("/")
    if normalized_relative_path.startswith("Files/"):
        normalized_relative_path = normalized_relative_path[len("Files/") :]
    return f"{store.root.rstrip('/')}/Files/{normalized_relative_path}"


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



def _require_fabric_connector() -> Any:
    """Return Fabric connector constants or raise a runtime-specific error."""
    try:
        import com.microsoft.spark.fabric  # noqa: F401
        from com.microsoft.spark.fabric.Constants import Constants
    except Exception as exc:
        raise RuntimeError("This function must run inside Microsoft Fabric Spark with com.microsoft.spark.fabric available.") from exc
    return Constants



def _build_warehouse_object_name(warehouse_name: str, schema_name: str, table_name: str) -> str:
    """Return the connector warehouse object name."""
    return f"{warehouse_name}.{schema_name}.{table_name}"


def _resolve_lakehouse_table_identifier(store: FabricStore, table_name: str, schema_name: str | None = None) -> str:
    """Return the Spark table identifier for an already-normalized lakehouse table."""
    return f"{schema_name}.{table_name}" if schema_name else table_name


def read_lakehouse_table_core(table_name: str, *, target: str, schema: str | None = None, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Lakehouse Delta table for package-internal callers.

    Parameters
    ----------
    table_name : str
        Lakehouse table name.
    target : str
        Configured lakehouse target key.
    schema : str or None, default=None
        Optional schema override for schema-enabled lakehouses.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame loaded from the resolved Delta table path.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_lakehouse_store(store, env, target)
    table_value = _normalize_table_name(table_name)
    schema_value = _normalize_schema_name(schema if schema is not None else (store.schema if store.schema_enabled else None))
    spark_obj = _get_spark(spark_session)
    return spark_obj.read.format("delta").load(_resolve_lakehouse_table_path(store, table_value, schema_value))


def write_lakehouse_table_core(df, table_name: str, *, target: str, schema: str | None, mode: str, partition_by=None, repartition_by=None, options=None, verbose: bool = True, context=None):
    """Write a Lakehouse Delta table for package-internal callers.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    table_name : str
        Lakehouse table name.
    target : str
        Configured lakehouse target key.
    schema : str or None
        Optional schema override for schema-enabled lakehouses.
    mode : str
        Spark write mode.
    partition_by : str or list[str], optional
        Delta partition column or columns.
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning before write.
    options : dict, optional
        Additional Spark writer options.
    verbose : bool, default=True
        Whether to print the resolved output path.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The DataFrame is written to the resolved Delta table path.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_lakehouse_store(store, env, target)
    table_value = _normalize_table_name(table_name)
    schema_value = _normalize_schema_name(schema if schema is not None else (store.schema if store.schema_enabled else None))
    normalized_mode = _normalize_write_mode(mode)
    path = _resolve_lakehouse_table_path(store, table_value, schema_value)
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = df.repartition(*repartition_by) if not (repartition_by and isinstance(repartition_by[0], int)) else df.repartition(repartition_by[0], *repartition_by[1:])
        else:
            df = df.repartition(repartition_by)
    writer = df.write.mode(normalized_mode).format("delta")
    if partition_by is not None:
        writer = writer.partitionBy(*partition_by) if isinstance(partition_by, (list, tuple)) else writer.partitionBy(partition_by)
    for key, value in (options or {}).items():
        writer = writer.option(key, value)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    writer.save(path)


def read_lakehouse_csv_core(relative_path: str, *, target: str, spark_session=None, header: bool = True, context: dict[str, Any] | None = None, **options):
    """Read Lakehouse CSV files for package-internal callers.

    Parameters
    ----------
    relative_path : str
        Path under the lakehouse ``Files`` area.
    target : str
        Configured lakehouse target key.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    header : bool, default=True
        Whether the first row contains column names.
    context : dict[str, Any], optional
        Active Fabric context override.
    **options
        Additional Spark CSV reader options.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame loaded from the resolved CSV path.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_lakehouse_store(store, env, target)
    path_value = _validate_relative_path(relative_path)
    spark_obj = _get_spark(spark_session)
    reader = spark_obj.read.option("header", header)
    for key, value in options.items():
        reader = reader.option(key, value)
    return reader.csv(_lakehouse_file_path(store, path_value))


def read_lakehouse_parquet_core(relative_path: str, *, target: str, verbose: bool = True, spark_session=None, context: dict[str, Any] | None = None):
    """Read Lakehouse Parquet files for package-internal callers.

    Parameters
    ----------
    relative_path : str
        Path under the lakehouse ``Files`` area.
    target : str
        Configured lakehouse target key.
    verbose : bool, default=True
        Whether to print fallback read progress.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame loaded from the resolved Parquet path.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_lakehouse_store(store, env, target)
    normalized_relative_path = _validate_relative_path(relative_path)
    spark_obj = _get_spark(spark_session)
    orig_spark_path = _lakehouse_file_path(store, normalized_relative_path)
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
    """Read Lakehouse Excel files for package-internal callers.

    Parameters
    ----------
    relative_path : str
        Path under the lakehouse ``Files`` area.
    target : str
        Configured lakehouse target key.
    sheet_name : str or int, default=0
        Worksheet name or index to read.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.
    **read_excel_kwargs
        Additional keyword arguments passed to ``pandas.read_excel``.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame converted from the selected Excel worksheet.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_lakehouse_store(store, env, target)
    path_value = _validate_relative_path(relative_path)
    spark_obj = _get_spark(spark_session)
    lakehouse_path = _lakehouse_file_path(store, path_value)
    bin_df = spark_obj.read.format("binaryFile").option("recursiveFileLookup", "false").load(lakehouse_path)
    if bin_df.count() == 0:
        raise FileNotFoundError(f"No file found at path: {lakehouse_path}")
    content = bin_df.select("content").collect()[0][0]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_file.write(bytearray(content))
        temp_file_path = temp_file.name
    pandas_df = _load_pandas().read_excel(temp_file_path, sheet_name=sheet_name, **read_excel_kwargs)
    return spark_obj.createDataFrame(pandas_df)


def read_warehouse_table_core(schema: str, table_name: str, *, target: str, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Warehouse table for package-internal callers.

    Parameters
    ----------
    schema : str
        Warehouse schema name.
    table_name : str
        Warehouse table name.
    target : str
        Configured warehouse target key.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame loaded through the Fabric Warehouse connector.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_warehouse_store(store, env, target)
    schema_value = _normalize_schema_name(schema)
    table_value = _normalize_table_name(table_name)
    constants = _require_fabric_connector()
    spark_obj = _get_spark(spark_session)
    return spark_obj.read.option(constants.WorkspaceId, store.workspace_id).option(constants.DatawarehouseId, store.item_id).synapsesql(_build_warehouse_object_name(store.name, schema_value, table_value))


def read_warehouse_query_core(query: str, *, target: str, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Warehouse SQL query for package-internal callers.

    Parameters
    ----------
    query : str
        SQL ``SELECT`` statement, or CTE beginning with ``WITH``.
    target : str
        Configured warehouse target key.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame loaded through the Fabric Warehouse connector.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_warehouse_store(store, env, target)
    sql = str(query or "").strip()
    if not sql:
        raise ValueError("query must be a non-empty SQL SELECT statement.")
    if not sql.lower().lstrip().startswith(("select", "with")):
        raise ValueError("query must be a SELECT statement or a CTE ending in a SELECT statement.")
    constants = _require_fabric_connector()
    spark_obj = _get_spark(spark_session)
    return spark_obj.read.option(constants.WorkspaceId, store.workspace_id).option(constants.DatawarehouseId, store.item_id).synapsesql(sql)


def write_warehouse_table_core(df, schema: str, table_name: str, *, target: str, mode: str, context: dict[str, Any] | None = None):
    """Write a Warehouse table for package-internal callers.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to publish.
    schema : str
        Warehouse schema name.
    table_name : str
        Warehouse table name.
    target : str
        Configured warehouse target key.
    mode : str
        Spark writer mode passed to the Fabric Warehouse connector.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The DataFrame is written through the Fabric Warehouse connector.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    _validate_warehouse_store(store, env, target)
    schema_value = _normalize_schema_name(schema)
    table_value = _normalize_table_name(table_name)
    constants = _require_fabric_connector()
    df.write.mode(mode).option(constants.WorkspaceId, store.workspace_id).option(constants.DatawarehouseId, store.item_id).synapsesql(_build_warehouse_object_name(store.name, schema_value, table_value))




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




def configured_lakehouse_schema(config: Any, env: str, target: str) -> str | None:
    """Return the configured schema for a schema-enabled lakehouse target."""
    try:
        store = _get_store(config, env, target)
    except ValueError:
        return None
    if store.kind != "lakehouse" or not getattr(store, "schema_enabled", False):
        return None
    return _normalize_schema_name(getattr(store, "schema", None))
