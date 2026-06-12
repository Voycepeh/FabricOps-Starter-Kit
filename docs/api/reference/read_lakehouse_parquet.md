# read_lakehouse_parquet

Read a Parquet path from a configured Fabric lakehouse Files path.

## Purpose

Reads a Parquet file or folder from the Files area of a configured Fabric lakehouse into a Spark DataFrame.

## When to use this

- Use for file-based source ingestion when the source is Parquet rather than a managed table.

## At a glance

**Do not use when:**

- Do not use for Delta tables, CSV files, Excel files, or warehouse SQL tables.

**Errors:**

Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

**Side effects:**

Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.

## Key terms

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../reference/glossary/) for more FabricOps terms.

## Related guides

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

## Used in templates

- `02_pipeline`
- `99_explore`

## Used by

Not documented yet

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

## Function details and source

### Function details

- Module: `fabric_input_output`
- Classification: Callable
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `555`
- Signature:

```python
def read_lakehouse_parquet(config, env, target, relative_path, verbose=True, spark_session=None)
```

### Parameters

`config` : `FrameworkConfig | dict`, required
: FabricOps FrameworkConfig or compatible config object.

`env` : `str`, required
: Environment key such as `"dev"`.

`target` : `str`, required
: Logical target name such as `"source"` or `"unified"`.

`relative_path` : `str`, required
: Path to the Parquet file under the lakehouse `Files/` folder, without the leading `"Files/"`. For example: `"raw/orders/orders_2026.parquet"`.

`verbose` : `bool, default True`, optional
: Whether to print read and fallback progress.

`spark_session` : `object`, optional
: Spark session to use. If omitted, the helper uses the notebook global `spark`.

### Returns

Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.

### Return interpretation

The returned DataFrame uses the Parquet schema read by Spark; validate it before downstream profile or guardrail checks.

### Common failure causes

- The Parquet path is missing or misspelled.
- The file is not valid Parquet.
- The configured lakehouse target is unavailable.
- The caller lacks read permission.

### Notes

Assumes Fabric notebook runtime filesystem conventions for local fallback
conversion paths (``/lakehouse/default/Files/...``).

### Example

```python
df = read_lakehouse_parquet(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.parquet", spark_session=spark)
```

### Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L555-L677">View read_lakehouse_parquet on GitHub</a>

```python
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
```

## Internal implementation summary

??? info "Call flow"

    ```text
    read_lakehouse_parquet(...)
    ├── _convert_single_parquet_ns_to_us(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    └── _lakehouse_file_path(...)
    ```

??? info "Internal helpers used: 4"

    This callable uses 4 internal helpers for audit timestamp, metadata loading, and fabric or spark access.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Audit timestamp</td>
          <td data-label="Helpers"><code>_convert_single_parquet_ns_to_us</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_lakehouse_file_path</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_get_spark</code>, <code>_get_store</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=True)`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L500-L552)

            ```python
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
            ```

        ??? example "Metadata loading helpers"

            **`def _lakehouse_file_path(store, env: str, target: str, relative_path: str) -> str`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L158-L168)

            ```python
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
            ```

        ??? example "Fabric or Spark access helpers"

            **`def _get_spark(spark_session=None)`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L125-L155)

            ```python
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
            ```

            **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L627-L667)

            ```python
            def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any:
                """Resolve a configured Fabric path for an environment and target.

                Parameters
                ----------
                env : str
                    Environment key such as ``Sandbox``, ``DE``, or ``Prod``.
                target : str
                    Target key such as ``Source``, ``Unified``, ``Product``, or ``Warehouse``.
                config : FrameworkConfig | PathConfig | None
                    Configuration that contains environment-to-target path mappings.

                Returns
                -------
                Any
                    FabricStore object with ``workspace_id``, ``house_id``, ``house_name``, and ``root``.

                Raises
                ------
                ValueError
                    If config is missing, or if the environment/target mapping does not exist.

                Examples
                --------
                >>> get_path("Sandbox", "Source", config=CONFIG)
                Housepath(...)
                """
                if config is None:
                    raise ValueError("No Fabric config was provided. Pass a FrameworkConfig or PathConfig instance.")
                paths = config.path_config.paths if isinstance(config, FrameworkConfig) else config.paths
                if env not in paths:
                    available_envs = ", ".join(sorted(paths.keys())) or "<none>"
                    raise ValueError(
                        f"Environment '{env}' was not found in Fabric config. Available environments: {available_envs}."
                    )
                if target not in paths[env]:
                    available_targets = ", ".join(sorted(paths[env].keys())) or "<none>"
                    raise ValueError(
                        f"Target '{target}' was not found under environment '{env}'. Available targets: {available_targets}."
                    )
                return paths[env][target]
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- Short name: `read_lakehouse_parquet`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `555`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.
- **side_effects:** Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.
- **failure_modes:** Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.
- **verification:** Verify the file path is a lakehouse Files Parquet path and check row count/schema after reading.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L555-L677">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L555-L677</a>
- Start line: `555`
- End line: `677`
- Signature:

```python
def read_lakehouse_parquet(config, env, target, relative_path, verbose=True, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 4
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
