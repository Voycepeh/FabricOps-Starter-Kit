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
from typing import Any
import tempfile

import pandas as pd

from .config import FrameworkConfig, PathConfig, _get_store


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

    def __post_init__(self) -> None:
        for field_name in ("env", "workspace_id", "item_id", "name", "kind"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        normalized_kind = self.kind.strip().lower()
        if normalized_kind not in {"lakehouse", "warehouse"}:
            raise ValueError("kind must be one of: lakehouse, warehouse.")
        object.__setattr__(self, "kind", normalized_kind)

    @property
    def root(self) -> str:
        if self.kind != "lakehouse":
            raise ValueError("root is only available for lakehouse stores.")
        return f"abfss://{self.workspace_id}@onelake.dfs.fabric.microsoft.com/{self.item_id}"


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


def read_lakehouse_table(config, env, target, table, spark_session=None):
    """Read a Delta table from a Fabric lakehouse.

    This reads from the lakehouse `Tables/` area using the ABFSS root stored in
    a `FabricStore`. In the notebook lifecycle, call this near the start of the
    Source or Unified step when loading Delta-backed source datasets.

    Parameters
    ----------
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    table : str
        Table name under the lakehouse `Tables` area.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.

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
    >>> df = read_lakehouse_table(CONFIG, ENV, "source", "RAW_ORDERS")
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    if not table:
        raise ValueError("table is required.")

    spark_obj = _get_spark(spark_session)
    path = f"{store.root.rstrip('/')}/Tables/{table}"
    return spark_obj.read.format("delta").load(path)


def write_lakehouse_table(
    df,
    config,
    env,
    target,
    table,
    mode="append",
    partition_by=None,
    repartition_by=None,
    overwrite_schema=True,
):
    """Write a Spark DataFrame to a Fabric lakehouse Delta table.

    This writes to the lakehouse `Tables/` area using the ABFSS root stored in
    a `FabricStore`. Use this in the Unified/Product stage after transformations,
    DQ checks, and technical-column enrichment are complete.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    table : str
        Target table name under the lakehouse `Tables` area.
    mode : str, default "append"
        Spark write mode. Supported values are `"append"`, `"overwrite"`,
        `"errorifexists"`, and `"ignore"`.
    partition_by : str or list[str], optional
        Column or columns used to physically partition the Delta table.
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning before write.
    overwrite_schema : bool, default True
        Whether to set Spark Delta `overwriteSchema=true` before saving.

    Returns
    -------
    None
        The DataFrame is written to the target Delta table path.

    Notes
    -----
    Side effects:
    - Persists data to OneLake Delta storage under ``Tables/<table>``.
    - Optional repartitioning can change output file sizing and partition
      layout.

    Raises
    ------
    ValueError
        If `table` is missing, `mode` is invalid, or the resolved target is not a lakehouse.

    Examples
    --------
    >>> write_lakehouse_table(df, CONFIG, ENV, "unified", "CLEAN_ORDERS")
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    if not table:
        raise ValueError("table is required.")

    normalized_mode = str(mode or "").lower().strip()
    if normalized_mode not in {"append", "overwrite", "errorifexists", "ignore"}:
        raise ValueError("mode must be one of append, overwrite, errorifexists, ignore.")

    path = f"{store.root.rstrip('/')}/Tables/{table}"

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

    if overwrite_schema:
        writer = writer.option("overwriteSchema", "true")

    writer.save(path)


def read_lakehouse_csv(config, env, target, relative_path, spark_session=None, header=True):
    """Read a CSV file from a Fabric lakehouse Files path.

    This reads from the lakehouse `Files/` area using the ABFSS root stored in
    a `FabricStore`. In the Source step, use it for raw file ingestion before
    standardisation or conversion to Delta tables.

    Parameters
    ----------
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    relative_path : str
        Path to the CSV file or folder under the lakehouse root, for example
        `"Files/raw/orders.csv"` or `"Files/raw/orders/"`.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
    header : bool, default True
        Whether the first row of the CSV file contains column names.

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
    >>> df = read_lakehouse_csv(CONFIG, ENV, "source", "raw/orders.csv")
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    if not relative_path:
        raise ValueError("relative_path is required.")

    spark_obj = _get_spark(spark_session)
    normalized_relative_path = relative_path.lstrip("/")
    if normalized_relative_path.startswith("Files/"):
        normalized_relative_path = normalized_relative_path[len("Files/"):]
    path = f"{store.root.rstrip('/')}/Files/{normalized_relative_path}"
    return spark_obj.read.option("header", header).csv(path)


def read_warehouse_table(config, env, target, schema, table, spark_session=None):
    """Read a table from a Microsoft Fabric warehouse.

    This uses Fabric Spark's `synapsesql` connector to read from a warehouse
    configured in the framework `CONFIG` mapping. In Source → Unified →
    Product workflows, this is commonly used when curated inputs are stored in
    Fabric Warehouse instead of Lakehouse tables.

    Parameters
    ----------
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment name in the config mapping, for example `"Sandbox"` or `"DE"`.
    target : str
        Warehouse target name under the selected environment, for example
        `"Warehouse"` or `"wh_Bronze"`.
    schema : str
        Warehouse schema name, for example `"dbo"`.
    table : str
        Warehouse table name.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.

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
    >>> df = read_warehouse_table(CONFIG, ENV, "product", "dbo", "TABLE_NAME")
    """
    spark_obj = _get_spark(spark_session)
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
        .synapsesql(f"{store.name}.{schema}.{table}")
    )


def write_warehouse_table(df, config, env, target, schema, table, mode="append"):
    """Write a Spark DataFrame to a Microsoft Fabric warehouse table.

    This uses Fabric Spark's `synapsesql` connector to write to a warehouse
    configured in the framework `CONFIG` mapping. Use this near the end of the
    Product step when publishing serving tables.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment name in the config mapping, for example `"Sandbox"` or `"DE"`.
    target : str
        Warehouse target name under the selected environment, for example
        `"Warehouse"` or `"wh_Bronze"`.
    schema : str
        Warehouse schema name, for example `"dbo"`.
    table : str
        Warehouse table name.
    mode : str, default "append"
        Spark write mode, for example `"append"` or `"overwrite"`.

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
    >>> write_warehouse_table(df, CONFIG, ENV, "product", "dbo", "TABLE_NAME")
    """
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
        .synapsesql(f"{store.name}.{schema}.{table}")
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

        pdf = pd.read_parquet(local_in_path, engine="pyarrow")
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


def read_lakehouse_parquet(config, env, target, relative_path, verbose=True, spark_session=None):
    """Read a Parquet file from a Fabric lakehouse Files path.

    This reads from the lakehouse `Files/` area using Spark. If Spark cannot
    read the original Parquet file because of timestamp precision issues, the
    helper tries a fallback `_tsus` path. If that fallback file does not exist,
    it converts the single local Parquet file from nanosecond to microsecond
    timestamps and retries the fallback path.

    Parameters
    ----------
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    relative_path : str
        Path to the Parquet file under the lakehouse `Files/` folder, without
        the leading `"Files/"`. For example:
        `"raw/orders/orders_2026.parquet"`.
    verbose : bool, default True
        Whether to print read and fallback progress.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.

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
    >>> df = read_lakehouse_parquet(CONFIG, ENV, "source", "raw/orders.parquet")
    Notes
    -----
    Assumes Fabric notebook runtime filesystem conventions for local fallback
    conversion paths (``/lakehouse/default/Files/...``).
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    if not relative_path:
        raise ValueError("relative_path is required.")

    spark_obj = _get_spark(spark_session)

    relative_path = relative_path.lstrip("/")
    if relative_path.startswith("Files/"):
        relative_path = relative_path[len("Files/") :]

    orig_spark_path = f"Files/{relative_path}"
    lakehouse_prefix = "/lakehouse/default/"
    parts = relative_path.split("/")

    if len(parts) < 2:
        raise ValueError("relative_path should look like folder/file.parquet or folder/subfolder/file.parquet.")

    tsus_dir = parts[:-2] + [parts[-2] + "_tsus"]
    tsus_relative_path = "/".join(tsus_dir + [parts[-1]])
    tsus_spark_path = f"Files/{tsus_relative_path}"

    orig_local_path = f"{lakehouse_prefix}{orig_spark_path}"
    tsus_local_path = f"{lakehouse_prefix}{tsus_spark_path}"

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
                    mssparkutils.fs.mkdirs("/".join(tsus_dir))
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


def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None):
    """Read an Excel file from a Fabric lakehouse Files path.

    Spark does not natively read Excel files. This helper reads the Excel file
    as binary from the lakehouse, writes it to a temporary local file, loads it
    with pandas, then converts it into a Spark DataFrame.

    This is intended for small reference files, mapping tables, and manually
    maintained business inputs. Large source datasets should be stored as
    Delta, Parquet, or CSV instead.

    Parameters
    ----------
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    relative_path : str
        Path to the Excel file under the lakehouse root, for example
        `"Files/reference/faculty_mapping.xlsx"`.
    sheet_name : str or int, default 0
        Worksheet name or index to read. Defaults to the first worksheet.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.

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
    >>> df_mapping = read_lakehouse_excel(CONFIG, ENV, "source", "reference/mapping.xlsx")
    Notes
    -----
    Side effects:
    - Creates a temporary local file during conversion.
    - Materializes rows through pandas before creating a Spark DataFrame.
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    if not relative_path:
        raise ValueError("relative_path is required.")

    spark_obj = _get_spark(spark_session)
    lakehouse_file_path = f"{store.root.rstrip('/')}/Files/{relative_path.lstrip('/')}"

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

    pandas_df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
    return spark_obj.createDataFrame(pandas_df)


def _get_fabric_runtime_context():
    """Return the Fabric notebook runtime context when available.

    Fabric notebooks expose runtime metadata through `notebookutils.runtime`.
    This helper keeps that dependency optional so the module can still be
    imported in local tests or non-Fabric environments.

    Returns
    -------
    dict
        Fabric runtime context when running inside Fabric. Returns an empty
        dictionary when the context is unavailable.
    """
    try:
        from notebookutils import runtime

        return runtime.context
    except Exception:
        return {}


def check_naming_convention(notebook_name=None, allowed_prefixes=None, fail_on_error=True):
    """Check whether a Fabric notebook name starts with an allowed prefix.

    The allowed prefixes should come from the project config notebook, not from
    this module. This keeps naming policy configurable per project. Call this
    early in notebooks (before Source reads) to enforce naming governance in
    the project lifecycle.

    Parameters
    ----------
    notebook_name : str, optional
        Notebook name to check. If omitted, the helper tries to read the
        current Fabric notebook name from `notebookutils.runtime`.
    allowed_prefixes : list[str] or tuple[str, ...]
        Prefixes that are valid for this project.
    fail_on_error : bool, default True
        If True, raise `ValueError` when the notebook name is unavailable or
        invalid. If False, return a result dictionary instead.

    Returns
    -------
    dict
        Validation result containing notebook name, compliance status, allowed
        prefixes, and message.

    Raises
    ------
    ValueError
        If `allowed_prefixes` is missing, the notebook name is unavailable, or
        the notebook name does not match any allowed prefix.

    Examples
    --------
    >>> # %run 00_env_config
    >>> check_naming_convention(allowed_prefixes=NOTEBOOK_PREFIX_LIST)
    """
    if not allowed_prefixes:
        message = "allowed_prefixes is required. Define it in your config notebook and pass it in."
        if fail_on_error:
            raise ValueError(message)
        return {
            "notebook_name": notebook_name,
            "compliant": False,
            "allowed_prefixes": [],
            "message": message,
        }

    prefixes = list(allowed_prefixes)

    if notebook_name is None:
        context = _get_fabric_runtime_context()
        notebook_name = context.get("currentNotebookName")

    if not notebook_name:
        message = "Notebook name is unavailable. Pass notebook_name or run inside Fabric."
        if fail_on_error:
            raise ValueError(message)
        return {
            "notebook_name": None,
            "compliant": False,
            "allowed_prefixes": prefixes,
            "message": message,
        }

    notebook_name_normalized = notebook_name.lower()
    prefixes_normalized = [prefix.lower() for prefix in prefixes]
    match = any(notebook_name_normalized.startswith(prefix) for prefix in prefixes_normalized)

    status = "comply" if match else "failed - please follow standard naming convention for notebook"

    print(f"Notebook name: {notebook_name_normalized}")
    print(f"Naming convention check: {status}\n")

    df = pd.DataFrame({"No": list(range(1, len(prefixes) + 1)), "Allowed Prefix": prefixes})
    print("Standard Naming Convention Prefix List:")
    print(df.to_string(index=False))

    if not match and fail_on_error:
        raise ValueError(
            f"Notebook name '{notebook_name_normalized}' does not comply with naming conventions. "
            f"Allowed prefixes: {', '.join(prefixes)}"
        )

    return {
        "notebook_name": notebook_name_normalized,
        "compliant": match,
        "allowed_prefixes": prefixes,
        "message": status,
    }


def seed_minimal_sample_source_table(
    config,
    env,
    target,
    table_name: str = "minimal_source",
    mode: str = "overwrite",
    spark_session=None,
):
    """Create and persist a minimal demo source table for end-to-end samples.

    Parameters
    ----------
    source_lakehouse : FabricStore
        Source lakehouse target selected by config/environment/target inputs.
    table_name : str, default="minimal_source"
        Destination source-table name to seed for sample notebook runs.
    mode : str, default="overwrite"
        Write mode passed to :func:`write_lakehouse_table`.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses notebook global ``spark``.

    Returns
    -------
    pyspark.sql.DataFrame
        Seeded Spark DataFrame that was written to the source table.

    Notes
    -----
    Runtime assumptions:
    - Fabric notebook runtime with Spark session available, or ``spark_session`` provided.
    - Writes a tiny deterministic dataset for demo/tutorial workflows only.
    """
    rows = [
        {"customer_id": 1001, "event_ts": "2026-01-01T09:00:00Z", "status": "active", "amount": 120.5, "email": "user1001@example.com", "country_code": "SG"},
        {"customer_id": 1002, "event_ts": "2026-01-02T10:15:00Z", "status": "inactive", "amount": 89.0, "email": "user1002@example.com", "country_code": "US"},
        {"customer_id": 1003, "event_ts": "2026-01-03T12:30:00Z", "status": "active", "amount": 0.0, "email": "user1003@example.com", "country_code": "GB"},
        {"customer_id": 1004, "event_ts": "2026-01-04T14:45:00Z", "status": "pending", "amount": 410.2, "email": "user1004@example.com", "country_code": "SG"},
    ]
    spark_obj = _get_spark(spark_session)
    df = spark_obj.createDataFrame(rows)
    write_lakehouse_table(df, config, env, target, table_name, mode=mode)
    return df
