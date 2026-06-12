# read_lakehouse_excel

## Signature

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs)
```

## Summary

Read an Excel file from a configured Fabric lakehouse Files path.

## Usage note

- Use when source data arrives as an Excel workbook and should still follow configured Fabric lakehouse routing.

**Do not use when:**

- Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

**Additional context:**

Reads an Excel file from a configured lakehouse Files path and converts it into a Spark DataFrame for notebook processing.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `relative_path` | `str` | Yes | Path to the Excel file relative to the lakehouse ``Files`` area, for example ``"reference/faculty_mapping.xlsx"``. A leading ``"Files/"`` prefix is accepted for consistency with notebook examples and is normalized away before the lakehouse path is resolved. |
| `sheet_name` | `str or int, default 0` | No | Worksheet name or index to read. Defaults to the first worksheet. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. **read_excel_kwargs Additional keyword arguments passed directly to :func:`pandas.read_excel`. Common options include ``skiprows`` for title rows above the real header, ``header`` for custom header-row selection, ``usecols`` for column filtering, ``dtype`` for mixed-type columns, and ``nrows`` for sampling or bounded reads. |

## Returns

Spark DataFrame converted from the selected Excel worksheet.

### Return interpretation

The returned DataFrame depends on workbook sheet and parsing options; confirm headers and types before using it as pipeline input.

## Raises / Errors

Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.

### Common failure causes

- The workbook path or sheet name is incorrect.
- Excel parsing dependencies are unavailable.
- The workbook layout does not match expected headers.
- The configured lakehouse target cannot be read.

## Example

```python
mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)
```

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

**Glossary terms**

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Developer details

- Module: `fabric_input_output`
- Classification: Callable
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `680`
- Signature:

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs)
```

**Used in templates:**

- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.

**Notes:**

Side effects:
- Creates a temporary local file during conversion.
- Materializes rows through pandas before creating a Spark DataFrame.

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

## Internal implementation summary

??? info "Call flow"

    ```text
    read_lakehouse_excel(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    └── _lakehouse_file_path(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for metadata loading and fabric or spark access.

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

        ??? example "Metadata loading helpers"

            **`def _lakehouse_file_path(store, env: str, target: str, relative_path: str) -> str`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/fabric_input_output.py#L158-L168)

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

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/fabric_input_output.py#L125-L155)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L627-L667)

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


## Source link

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/fabric_input_output.py#L680-L767">View read_lakehouse_excel on GitHub</a>

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs):
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
        Path to the Excel file relative to the lakehouse ``Files`` area, for
        example ``"reference/faculty_mapping.xlsx"``. A leading ``"Files/"``
        prefix is accepted for consistency with notebook examples and is
        normalized away before the lakehouse path is resolved.
    sheet_name : str or int, default 0
        Worksheet name or index to read. Defaults to the first worksheet.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.
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
    >>> df_mapping = read_lakehouse_excel(CONFIG, ENV, "source", "reference/mapping.xlsx")
    >>> df_publications = read_lakehouse_excel(
    ...     CONFIG,
    ...     ENV,
    ...     "source",
    ...     "Publications_at_the_National_University_of_Singapore_2020_-_2026.xlsx",
    ...     sheet_name=0,
    ...     skiprows=1,
    ... )
    Notes
    -----
    Side effects:
    - Creates a temporary local file during conversion.
    - Materializes rows through pandas before creating a Spark DataFrame.
    """
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

    pandas_df = pd.read_excel(temp_file_path, sheet_name=sheet_name, **read_excel_kwargs)
    return spark_obj.createDataFrame(pandas_df)
```

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- Short name: `read_lakehouse_excel`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `680`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires 00_env_config config/env/target context for resolving the configured lakehouse Files path.
- **inputs:** config, env, target, relative_path, optional sheet_name, optional spark_session, and pandas read_excel keyword arguments.
- **output:** Spark DataFrame converted from the selected Excel worksheet.
- **side_effects:** Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.
- **verification:** Verify the DataFrame row count and schema after reading, and confirm the Excel file is appropriate for a small reference-style input.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/fabric_input_output.py#L680-L767">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/fabric_input_output.py#L680-L767</a>
- Start line: `680`
- End line: `767`
- Signature:

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
