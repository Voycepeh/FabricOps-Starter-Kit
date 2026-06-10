# read_lakehouse_parquet

Read a Parquet path from a configured Fabric lakehouse Files path.

## What this is for and when to use it

Read a Parquet path from a configured Fabric lakehouse Files path.

- Use when reading a Parquet file or path from a configured Fabric lakehouse Files path.

## When not to use it

- Do not use for Delta tables, CSV files, Excel files, or warehouse SQL tables.

## Example

```python
df = read_lakehouse_parquet(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.parquet", spark_session=spark)
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">FabricOps FrameworkConfig or compatible config object.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key such as `&quot;dev&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Logical target name such as `&quot;source&quot;` or `&quot;unified&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>relative_path</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Path to the Parquet file under the lakehouse `Files/` folder, without the leading `&quot;Files/&quot;`. For example: `&quot;raw/orders/orders_2026.parquet&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>verbose</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Whether to print read and fallback progress.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark session to use. If omitted, the helper uses the notebook global `spark`.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.

## Errors and side effects

**Errors:** Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

**Side effects:** Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.

## Related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/pipeline__read_source_dataframe/"><code>fabricops_kit.pipeline._read_source_dataframe</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/fabric_input_output.py#L507-L629">View read_lakehouse_parquet on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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

</details>

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
- Source line: `507`
- Inbound references count: 1
- Outbound references count: 4

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.
- **side_effects:** Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.
- **failure_modes:** Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.
- **verification:** Verify the file path is a lakehouse Files Parquet path and check row count/schema after reading.

### Inbound references

- <a href="../internal/pipeline__read_source_dataframe/"><code>fabricops_kit.pipeline._read_source_dataframe</code></a>

### Outbound references

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/fabric_input_output.py#L507-L629">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/fabric_input_output.py#L507-L629</a>
- Start line: `507`
- End line: `629`
- Signature:

```python
def read_lakehouse_parquet(config, env, target, relative_path, verbose=True, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../internal/pipeline__read_source_dataframe/"><code>fabricops_kit.pipeline._read_source_dataframe</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

</details>
