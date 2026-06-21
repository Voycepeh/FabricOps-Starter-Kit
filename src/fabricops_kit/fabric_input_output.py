"""Fabric path and IO helpers for cross-environment lakehouse/warehouse routing.

This module contains the framework helpers used at the start and end of a
Fabric notebook workflow:

1. Validate Fabric lakehouse and warehouse configuration from a config notebook.
2. Resolve logical environment and target names into Fabric paths.
3. Read source data from lakehouse tables, lakehouse files, and warehouses.
4. Write curated outputs back to lakehouse tables or warehouses.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any
import re
import tempfile

from .config import _get_store, resolve_fabric_context


def _load_pandas() -> Any:
    """Return pandas for Excel/Parquet helpers that need it."""
    return import_module("pandas")


@dataclass(frozen=True)
class FabricStore:
    """Fabric lakehouse or warehouse connection details.

    `FabricStore` stores the minimum identifiers needed to read from or write to
    a Fabric lakehouse or warehouse using framework helpers.

    In normal use, define these values in a separate Fabric config notebook,
    validate the `CONFIG` mapping with `setup_notebook`, then retrieve the
    required environment and target via public IO helpers.

    Attributes
    ----------
    workspace_id : str
        Fabric workspace ID that contains the lakehouse or warehouse.
    house_id : str
        Fabric lakehouse or warehouse item ID.
    house_name : str
        Lakehouse or warehouse name.
    root : str
        ABFSS root path for the lakehouse or warehouse.

    Examples
    --------
    >>> lh = FabricStore(
    ...     workspace_id="<workspace-id>",
    ...     house_id="<lakehouse-id>",
    ...     house_name="DEX_SB_SOURCE",
    ...     root="abfss://<workspace-id>@onelake.dfs.fabric.microsoft.com/<lakehouse-id>",
    ... )
    >>> lh.house_name
    'DEX_SB_SOURCE'

    """

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
        """Return root."""
        if self.kind != "lakehouse":
            raise ValueError("root is only available for lakehouse stores.")
        return f"abfss://{self.workspace_id}@onelake.dfs.fabric.microsoft.com/{self.item_id}"


def _normalize_table_name(table: str) -> str:
    """Return a safe Spark table identifier, never a path or qualified name."""
    value = str(table or "").strip()
    if not value:
        raise ValueError("table is required.")
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("table must be a simple table name; pass schema separately and do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("table must contain only letters, numbers, and underscores, and must not start with a number.")
    return value


def _normalize_schema_name(schema: str | None) -> str | None:
    """Return a safe Spark schema identifier, or ``None`` when omitted."""
    if schema is None:
        return None
    value = str(schema).strip()
    if not value:
        raise ValueError("schema must be a non-empty Spark identifier when provided.")
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("schema must be a simple schema name; do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
    return value


def _resolve_lakehouse_schema(store: FabricStore, schema: str | None = None) -> str | None:
    """Return the explicit schema or configured store schema when enabled."""
    if schema is not None:
        return _normalize_schema_name(schema)
    if getattr(store, "schema_enabled", False):
        return _normalize_schema_name(getattr(store, "schema", None))
    return None


def _resolve_lakehouse_table_path(store: FabricStore, table: str, schema: str | None = None) -> str:
    """Return the physical OneLake Delta table path for a lakehouse table."""
    if store.kind != "lakehouse":
        raise ValueError("Lakehouse table paths are only available for lakehouse stores.")
    table_name = _normalize_table_name(table)
    schema_name = _resolve_lakehouse_schema(store, schema)
    table_relative_path = f"{schema_name}/{table_name}" if schema_name else table_name
    return f"{store.root.rstrip('/')}/Tables/{table_relative_path}"


def _resolve_lakehouse_table_identifier(store: FabricStore, table: str, schema: str | None = None) -> str:
    """Return the Spark table identifier for a lakehouse table."""
    table_name = _normalize_table_name(table)
    schema_name = _resolve_lakehouse_schema(store, schema)
    return f"{schema_name}.{table_name}" if schema_name else table_name


def _configured_lakehouse_schema(config, env: str, target: str) -> str | None:
    """Return the configured schema for a Lakehouse target, if enabled.

    Lightweight tests may pass partial config objects while monkeypatching the
    actual writer. Missing path mappings resolve to no explicit schema; real IO
    calls still validate configured targets through ``_get_store``.
    """
    try:
        store = _get_store(config, env, target)
    except ValueError:
        return None
    if store.kind != "lakehouse" or not getattr(store, "schema_enabled", False):
        return None
    return _normalize_schema_name(getattr(store, "schema", None))


DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"


# NOTE: _get_store is now owned by fabricops_kit.config.


def _get_spark(spark_session=None):
    """Return an explicit Spark session or the active notebook global `spark`.

    Most Fabric notebooks already expose a global `spark` object. Tests and
    local scripts can pass `spark_session` explicitly to avoid relying on the
    notebook runtime.

    Parameters
    ----------
    spark_session : object, optional
        Spark session to use instead of the notebook global `spark`.

    Returns
    -------
    object
        Spark session object.

    Raises
    ------
    RuntimeError
        If no Spark session is passed and no global `spark` object exists.

    """
    if spark_session is not None:
        return spark_session
    try:
        return globals()["spark"]
    except KeyError as exc:
        raise RuntimeError(
            "Spark session was not provided and global 'spark' was not found. "
            "Run this inside Fabric/Spark or pass spark_session explicitly."
        ) from exc


def _lakehouse_file_path(store, env: str, target: str, relative_path: str) -> str:
    """Return an ABFSS path under a configured lakehouse Files area."""
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("relative_path must be a non-empty string.")

    normalized_relative_path = relative_path.strip().lstrip("/")
    if normalized_relative_path.startswith("Files/"):
        normalized_relative_path = normalized_relative_path[len("Files/") :]
    return f"{store.root.rstrip('/')}/Files/{normalized_relative_path}"



def read_data(
    source: str,
    *,
    target: str = "source",
    format: str = "table",
    schema: str | None = None,
    table: str | None = None,
    relative_path: str | None = None,
    spark_session=None,
    options: dict | None = None,
    context: dict[str, Any] | None = None,
    **kwargs,
):
    """Read data from the active Fabric context.

    Parameters
    ----------
    source : str
        Table name for table reads or relative file path for file reads.
    target : str, default="source"
        Logical target name in ``FABRIC_CONTEXT["config"]``.
    format : str, default="table"
        Read format. Supported values are ``"table"``, ``"delta"``,
        ``"csv"``, ``"parquet"``, ``"excel"``, and ``"warehouse"``.
    schema : str, optional
        Lakehouse or warehouse schema name.
    table : str, optional
        Explicit table name. Overrides ``source`` for table and warehouse reads.
    relative_path : str, optional
        Explicit lakehouse Files path. Overrides ``source`` for file reads.
    spark_session : object, optional
        Spark session to use.
    options : dict, optional
        Additional reader options passed to the format-specific implementation.
    context : dict, optional
        Advanced override context. Defaults to the active ``FABRIC_CONTEXT``
        initialized by ``00_env_config``.
    **kwargs
        Additional reader options.

    Returns
    -------
    pyspark.sql.DataFrame
        DataFrame loaded from the configured Fabric target.

    """
    config, env, resolved_context = resolve_fabric_context(context=context)
    normalized_format = str(format or "table").strip().lower()
    reader_options = {**(options or {}), **kwargs}
    if normalized_format in {"table", "delta", "lakehouse_table"}:
        table_name = table or source
        if not table_name:
            raise ValueError("table or source is required for Lakehouse table reads.")
        return read_lakehouse_table(table_name, target=target, schema=schema, spark_session=spark_session, context=resolved_context)
    if normalized_format == "csv":
        path = relative_path or source
        if not path:
            raise ValueError("relative_path or source is required for CSV reads.")
        return read_lakehouse_csv(path, target=target, spark_session=spark_session, context=resolved_context, **reader_options)
    if normalized_format == "parquet":
        path = relative_path or source
        if not path:
            raise ValueError("relative_path or source is required for Parquet reads.")
        return read_lakehouse_parquet(path, target=target, spark_session=spark_session, context=resolved_context, **reader_options)
    if normalized_format == "excel":
        path = relative_path or source
        if not path:
            raise ValueError("relative_path or source is required for Excel reads.")
        return read_lakehouse_excel(path, target=target, spark_session=spark_session, context=resolved_context, **reader_options)
    if normalized_format == "warehouse":
        table_name = table or source
        if not schema or not table_name:
            raise ValueError("schema and table/source are required for warehouse reads.")
        return read_warehouse_table(schema, table_name, target=target, spark_session=spark_session, context=resolved_context)
    raise ValueError("format must be one of table, delta, csv, parquet, excel, or warehouse.")


def write_data(
    df,
    name: str,
    *,
    target: str = "unified",
    format: str = "table",
    schema: str | None = None,
    table: str | None = None,
    mode: str = "append",
    options: dict | None = None,
    context: dict[str, Any] | None = None,
    **kwargs,
):
    """Write data using the active Fabric context.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        DataFrame to write.
    name : str
        Target table name.
    target : str, default="unified"
        Logical target name in ``FABRIC_CONTEXT["config"]``.
    format : str, default="table"
        Write format. Supported values are ``"table"``, ``"delta"``, and
        ``"warehouse"``.
    schema : str, optional
        Lakehouse or warehouse schema name.
    table : str, optional
        Explicit table name. Overrides ``name``.
    mode : str, default="append"
        Write mode.
    options : dict, optional
        Additional writer options for Lakehouse Delta writes.
    context : dict, optional
        Advanced override context. Defaults to the active ``FABRIC_CONTEXT``
        initialized by ``00_env_config``.
    **kwargs
        Additional writer options for Lakehouse Delta writes.

    Returns
    -------
    None
        The DataFrame is written to the configured Fabric target.

    """
    config, env, resolved_context = resolve_fabric_context(context=context)
    normalized_format = str(format or "table").strip().lower()
    table_name = table or name
    if not table_name:
        raise ValueError("table or name is required for writes.")
    writer_options = {**(options or {}), **kwargs.pop("options", {})}
    if normalized_format in {"table", "delta", "lakehouse_table"}:
        return write_lakehouse_table(
            df,
            table_name,
            target=target,
            schema=schema,
            mode=mode,
            options=writer_options or None,
            context=resolved_context,
            **kwargs,
        )
    if normalized_format == "warehouse":
        if not schema:
            raise ValueError("schema is required for warehouse writes.")
        return write_warehouse_table(df, schema, table_name, target=target, mode=mode, context=resolved_context)
    raise ValueError("format must be one of table, delta, or warehouse.")


def read_lakehouse_table(table_name: str, *, target: str = "source", schema: str | None = None, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Delta table from a Fabric lakehouse.

    This reads from the lakehouse `Tables/` area by loading the ABFSS path from
    the configured `FabricStore` root. It does not use registered Spark table
    names, partial namespaces, or the current/default lakehouse context. In the
    notebook lifecycle, call this near the start of the Source or Unified step
    when loading Delta-backed source datasets.

    Parameters
    ----------
    table_name : str
        Name of the Lakehouse table to read. Do not pass ``schema.table``; use
        ``schema`` separately.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    schema : str or None, default=None
        Optional schema override for schema-enabled Lakehouses. When omitted,
        schema routing comes from the configured lakehouse target. Schema-enabled
        targets read from ``Tables/<schema>/<table>``; classic targets read from
        ``Tables/<table>``.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the Delta table.

    Raises
    ------
    ValueError
        If `table` is missing or the resolved target is not a lakehouse.
    RuntimeError
        If no Spark session is available.

    Examples
    --------
    >>> df = read_lakehouse_table("RAW_ORDERS", target="source", schema=SOURCE_SCHEMA)

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    _normalize_table_name(table_name)

    spark_obj = _get_spark(spark_session)
    path = _resolve_lakehouse_table_path(store, table_name, schema=schema)
    return spark_obj.read.format("delta").load(path)


def write_lakehouse_table(
    df,
    table_name: str,
    *,
    target: str = "unified",
    schema=None,
    mode="append",
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose=True,
    context=None,
):
    """Write a Spark DataFrame to a Fabric lakehouse Delta table.

    This writes to the lakehouse `Tables/` area by saving to the ABFSS path from
    the configured `FabricStore` root. It does not use registered Spark table
    names, partial namespaces, or the current/default lakehouse context. Use this
    in the Unified/Product stage after transformations, DQ checks, and runtime
    audit-column enrichment are complete.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    table_name : str
        Name of the Lakehouse table to write. Do not pass ``schema.table``; use
        ``schema`` separately.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    schema : str or None, default=None
        Optional schema override for schema-enabled Lakehouses. When omitted,
        schema routing comes from the configured lakehouse target. Schema-enabled
        targets save to ``Tables/<schema>/<table>``; classic targets save to
        ``Tables/<table>``.
    mode : str, default "append"
        Spark write mode. Supported values are `"append"`, `"overwrite"`,
        `"errorifexists"`, and `"ignore"`.
    partition_by : str or list[str], optional
        Column or columns used to physically partition the Delta table.
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning before write.
    options : dict, optional
        Additional Spark DataFrameWriter options to apply before saving, such
        as ``{"overwriteSchema": "true"}``.
    verbose : bool, default=True
        Whether to print the resolved output path before writing.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    None
        The DataFrame is written to the target Delta table path.

    Notes
    -----
    Side effects:
    - Persists data to OneLake Delta storage under ``Tables/<table>`` or ``Tables/<schema>/<table>`` when schema routing is enabled.
    - Optional repartitioning can change output file sizing and partition
      layout.

    Raises
    ------
    ValueError
        If `table` is missing, `mode` is invalid, or the resolved target is not a lakehouse.

    Examples
    --------
    >>> write_lakehouse_table(df, "CLEAN_ORDERS", target="unified", schema=UNIFIED_SCHEMA)

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    _normalize_table_name(table_name)

    normalized_mode = str(mode or "").lower().strip()
    if normalized_mode not in {"append", "overwrite", "errorifexists", "ignore"}:
        raise ValueError("mode must be one of append, overwrite, errorifexists, ignore.")

    path = _resolve_lakehouse_table_path(store, table_name, schema=schema)

    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            if len(repartition_by) > 0 and isinstance(repartition_by[0], int):
                df = df.repartition(repartition_by[0], *repartition_by[1:])
            else:
                df = df.repartition(*repartition_by)
        elif isinstance(repartition_by, int):
            df = df.repartition(repartition_by)
        else:
            df = df.repartition(repartition_by)

    writer = df.write.mode(normalized_mode).format("delta")

    if partition_by is not None:
        if isinstance(partition_by, (list, tuple)):
            writer = writer.partitionBy(*partition_by)
        else:
            writer = writer.partitionBy(partition_by)

    for key, value in (options or {}).items():
        writer = writer.option(key, value)

    if verbose:
        print(f"Writing Lakehouse table to {path}")

    writer.save(path)


def read_lakehouse_csv(relative_path: str, *, target: str = "source", spark_session=None, header: bool = True, context: dict[str, Any] | None = None):
    """Read a CSV file from a Fabric lakehouse Files path.

    This reads from the lakehouse `Files/` area using the ABFSS root stored in
    a `FabricStore`. In the Source step, use it for raw file ingestion before
    standardisation or conversion to Delta tables.

    Parameters
    ----------
    relative_path : str
        Path to the CSV file or folder under the lakehouse root, for example
        `"Files/raw/orders.csv"` or `"Files/raw/orders/"`.
    target : str, default="source"
        Logical lakehouse target from the active Fabric context.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
    header : bool, default True
        Whether the first row of the CSV file contains column names.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the CSV path.

    Raises
    ------
    ValueError
        If `relative_path` is missing or the resolved target is not a lakehouse.
    RuntimeError
        If no Spark session is available.

    Examples
    --------
    >>> df = read_lakehouse_csv("raw/orders.csv", target="source")

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    spark_obj = _get_spark(spark_session)
    return spark_obj.read.option("header", header).csv(_lakehouse_file_path(store, env, target, relative_path))


def read_warehouse_table(schema: str, table_name: str, *, target: str = "warehouse", spark_session=None, context: dict[str, Any] | None = None):
    """Read a table from a Microsoft Fabric warehouse.

    This uses Fabric Spark's `synapsesql` connector to read from a warehouse
    configured in the framework `CONFIG` mapping. In Source → Unified →
    Product workflows, this is commonly used when curated inputs are stored in
    Fabric Warehouse instead of Lakehouse tables.

    Parameters
    ----------
    schema : str
        Warehouse schema name, for example `"dbo"`.
    table_name : str
        Name of the Warehouse table to read.
    target : str
        Warehouse target name under the selected environment, for example
        `"Warehouse"` or `"wh_Bronze"`.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the Fabric warehouse table.

    Raises
    ------
    RuntimeError
        If the Microsoft Fabric Spark connector is unavailable.
    ValueError
        If the selected environment or target is missing from the config.

    Examples
    --------
    >>> df = read_warehouse_table("dbo", "TABLE_NAME", target="product")

    """
    spark_obj = _get_spark(spark_session)
    config, env, _context = resolve_fabric_context(context=context)
    config, env, _context = resolve_fabric_context(context=context)
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    if store.kind != "warehouse":
        raise ValueError(f"Target '{env}/{target}' is not a warehouse store.")

    try:
        import com.microsoft.spark.fabric
        from com.microsoft.spark.fabric.Constants import Constants
    except Exception as exc:
        raise RuntimeError(
            "This function must run inside Microsoft Fabric Spark with "
            "com.microsoft.spark.fabric available."
        ) from exc

    return (
        spark_obj.read.option(Constants.WorkspaceId, store.workspace_id)
        .option(Constants.DatawarehouseId, store.item_id)
        .synapsesql(f"{store.name}.{schema}.{table_name}")
    )


def write_warehouse_table(df, schema: str, table_name: str, *, target: str = "warehouse", mode: str = "append", context: dict[str, Any] | None = None):
    """Write a Spark DataFrame to a Microsoft Fabric warehouse table.

    This uses Fabric Spark's `synapsesql` connector to write to a warehouse
    configured in the framework `CONFIG` mapping. Use this near the end of the
    Product step when publishing serving tables.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    schema : str
        Warehouse schema name, for example `"dbo"`.
    table_name : str
        Name of the Warehouse table to write.
    target : str
        Warehouse target name under the selected environment, for example
        `"Warehouse"` or `"wh_Bronze"`.
    mode : str, default "append"
        Spark write mode, for example `"append"` or `"overwrite"`.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    None
        The DataFrame is written to the target warehouse table.

    Notes
    -----
    Side effect: performs a write operation to the target warehouse object via
    Fabric runtime connector APIs.

    Raises
    ------
    RuntimeError
        If the Microsoft Fabric Spark connector is unavailable.
    ValueError
        If the selected environment or target is missing from the config.

    Examples
    --------
    >>> write_warehouse_table(df, "dbo", "TABLE_NAME", target="product")

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    if store.kind != "warehouse":
        raise ValueError(f"Target '{env}/{target}' is not a warehouse store.")

    try:
        import com.microsoft.spark.fabric
        from com.microsoft.spark.fabric.Constants import Constants
    except Exception as exc:
        raise RuntimeError(
            "This function must run inside Microsoft Fabric Spark with "
            "com.microsoft.spark.fabric available."
        ) from exc

    (
        df.write.mode(mode)
        .option(Constants.WorkspaceId, store.workspace_id)
        .option(Constants.DatawarehouseId, store.item_id)
        .synapsesql(f"{store.name}.{schema}.{table_name}")
    )


def _convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=True):
    """Convert one Parquet file from nanosecond to microsecond timestamps.

    Spark can fail to read some Parquet files that contain nanosecond timestamp
    precision. This helper reads one local Parquet file with PyArrow, rewrites
    it with microsecond timestamp precision, and saves it to a fallback path.

    This is an internal helper used by `read_lakehouse_parquet`.

    Parameters
    ----------
    local_in_path : str
        Local input path to the original Parquet file.
    local_out_path : str
        Local output path for the converted Parquet file.
    verbose : bool, default True
        Whether to print conversion progress.

    Returns
    -------
    None
        The converted Parquet file is written to `local_out_path`.

    Examples
    --------
    >>> _convert_single_parquet_ns_to_us(
    ...     "/lakehouse/default/Files/raw/orders.parquet",
    ...     "/lakehouse/default/Files/raw_tsus/orders.parquet",
    ... )

    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    try:
        if verbose:
            print(f"Reading with pyarrow: {local_in_path}")
            print(f"Writing us timestamps to: {local_out_path}")

        pdf = _load_pandas().read_parquet(local_in_path, engine="pyarrow")
        table = pa.Table.from_pandas(pdf, preserve_index=False)

        pq.write_table(
            table,
            local_out_path,
            coerce_timestamps="us",
            allow_truncated_timestamps=True,
        )

        if verbose:
            print(f"done: {local_out_path}")

    except Exception as exc:
        print(f"FAILED converting ns to us for file {local_in_path}: {exc}")


def read_lakehouse_parquet(relative_path: str, *, target: str = "source", verbose: bool = True, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Parquet file from a Fabric lakehouse Files path.

    This reads from the lakehouse `Files/` area using Spark. If Spark cannot
    read the original Parquet file because of timestamp precision issues, the
    helper tries a fallback `_tsus` path. If that fallback file does not exist,
    it converts the single local Parquet file from nanosecond to microsecond
    timestamps and retries the fallback path.

    Parameters
    ----------
    relative_path : str
        Path to the Parquet file under the lakehouse `Files/` folder, without
        the leading `"Files/"`. For example:
        `"raw/orders/orders_2026.parquet"`.
    target : str, default="source"
        Logical lakehouse target from the active Fabric context.
    verbose : bool, default True
        Whether to print read and fallback progress.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the original or converted Parquet path.

    Raises
    ------
    ValueError
        If `relative_path` is not a nested file path.
    RuntimeError
        If neither the original path nor the converted fallback path can be
        read successfully.

    Examples
    --------
    >>> df = read_lakehouse_parquet("raw/orders.parquet", target="source")

    Notes
    -----
    Assumes Fabric notebook runtime filesystem conventions for local fallback
    conversion paths (``/lakehouse/default/Files/...``).

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    spark_obj = _get_spark(spark_session)
    orig_spark_path = _lakehouse_file_path(store, env, target, relative_path)

    normalized_relative_path = str(relative_path).strip().lstrip("/")
    if normalized_relative_path.startswith("Files/"):
        normalized_relative_path = normalized_relative_path[len("Files/") :]

    lakehouse_prefix = "/lakehouse/default/"
    parts = normalized_relative_path.split("/")

    if len(parts) < 2:
        raise ValueError("relative_path should look like folder/file.parquet or folder/subfolder/file.parquet.")

    tsus_dir = parts[:-2] + [parts[-2] + "_tsus"]
    tsus_relative_path = "/".join(tsus_dir + [parts[-1]])
    tsus_spark_path = _lakehouse_file_path(store, env, target, tsus_relative_path)

    orig_local_path = f"{lakehouse_prefix}Files/{normalized_relative_path}"
    tsus_local_path = f"{lakehouse_prefix}Files/{tsus_relative_path}"

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
        tag = " after single-file convert" if try_convert else ""

        if verbose:
            print(f"Try Spark read: {tsus_spark_path}{tag}")

        try:
            df = spark_obj.read.parquet(tsus_spark_path)
            _ = df.limit(1).collect()
            if verbose:
                print("SUCCESS: Spark read _tsus path.")
            return df

        except Exception as exc:
            msg = str(exc)
            path_not_found = (
                "[PATH_NOT_FOUND]" in msg
                or "Path does not exist" in msg
                or "No such file or directory" in msg
            )

            if try_convert == 0 and path_not_found:
                if verbose:
                    print("PATH NOT FOUND for _tsus parquet. Will convert one file and retry.")

                try:
                    mssparkutils.fs.mkdirs(_lakehouse_file_path(store, env, target, "/".join(tsus_dir)))
                except Exception:
                    pass

                _convert_single_parquet_ns_to_us(
                    local_in_path=orig_local_path,
                    local_out_path=tsus_local_path,
                    verbose=verbose,
                )
            else:
                if verbose:
                    print(f"FAILED: Spark read _tsus path. Exception: {exc}")
                break

    raise RuntimeError("Failed to read from both original and _tsus Parquet paths.")


def read_lakehouse_excel(relative_path: str, *, target: str = "source", sheet_name=0, spark_session=None, context: dict[str, Any] | None = None, **read_excel_kwargs):
    """Read an Excel file from a Fabric lakehouse Files path.

    Spark does not natively read Excel files. This helper reads the Excel file
    as binary from the lakehouse, writes it to a temporary local file, loads it
    with pandas, then converts it into a Spark DataFrame.

    This is intended for small reference files, mapping tables, and manually
    maintained business inputs. Large source datasets should be stored as
    Delta, Parquet, or CSV instead.

    Parameters
    ----------
    relative_path : str
        Path to the Excel file relative to the lakehouse ``Files`` area, for
        example ``"reference/faculty_mapping.xlsx"``. A leading ``"Files/"``
        prefix is accepted for consistency with notebook examples and is
        normalized away before the lakehouse path is resolved.
    target : str, default="source"
        Logical lakehouse target from the active Fabric context.
    sheet_name : str or int, default 0
        Worksheet name or index to read. Defaults to the first worksheet.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    **read_excel_kwargs
        Additional keyword arguments passed directly to
        :func:`pandas.read_excel`. Common options include ``skiprows`` for
        title rows above the real header, ``header`` for custom header-row
        selection, ``usecols`` for column filtering, ``dtype`` for mixed-type
        columns, and ``nrows`` for sampling or bounded reads.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame converted from the selected Excel worksheet.

    Raises
    ------
    ValueError
        If `relative_path` is missing or the resolved target is not a lakehouse.
    FileNotFoundError
        If the Excel file cannot be found at the resolved lakehouse path.
    RuntimeError
        If no Spark session is available.

    Examples
    --------
    >>> df_mapping = read_lakehouse_excel("reference/mapping.xlsx", target="source")
    >>> df_publications = read_lakehouse_excel(
    ...     "Publications_at_the_National_University_of_Singapore_2020_-_2026.xlsx",
    ...     target="source",
    ...     sheet_name=0,
    ...     skiprows=1,
    ... )

    Notes
    -----
    Side effects:
    - Creates a temporary local file during conversion.
    - Materializes rows through pandas before creating a Spark DataFrame.

    """
    config, env, _context = resolve_fabric_context(context=context)
    store = _get_store(config, env, target)
    spark_obj = _get_spark(spark_session)
    lakehouse_file_path = _lakehouse_file_path(store, env, target, relative_path)

    bin_df = (
        spark_obj.read.format("binaryFile")
        .option("recursiveFileLookup", "false")
        .load(lakehouse_file_path)
    )

    if bin_df.count() == 0:
        raise FileNotFoundError(f"No file found at path: {lakehouse_file_path}")

    content = bin_df.select("content").collect()[0][0]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        temp_file.write(bytearray(content))
        temp_file_path = temp_file.name

    pandas_df = _load_pandas().read_excel(temp_file_path, sheet_name=sheet_name, **read_excel_kwargs)
    return spark_obj.createDataFrame(pandas_df)
