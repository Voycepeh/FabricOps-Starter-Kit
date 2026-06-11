# read_lakehouse_excel

Read an Excel file from a configured Fabric lakehouse Files path.

## What this is for and when to use it

Read an Excel file from a configured Fabric lakehouse Files path.

- Use when reading .xlsx files from a configured Fabric lakehouse Files path, especially small reference files, mapping tables, or manually maintained business inputs.

## When not to use it

- Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

## Example

```python
mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)
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
      <td data-label="Meaning">Path to the Excel file relative to the lakehouse ``Files`` area, for example ``&quot;reference/faculty_mapping.xlsx&quot;``. A leading ``&quot;Files/&quot;`` prefix is accepted for consistency with notebook examples and is normalized away before the lakehouse path is resolved.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>sheet_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Worksheet name or index to read. Defaults to the first worksheet.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark session to use. If omitted, the helper uses the notebook global `spark`. **read_excel_kwargs Additional keyword arguments passed directly to :func:`pandas.read_excel`. Common options include ``skiprows`` for title rows above the real header, ``header`` for custom header-row selection, ``usecols`` for column filtering, ``dtype`` for mixed-type columns, and ``nrows`` for sampling or bounded reads.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Spark DataFrame converted from the selected Excel worksheet.

## Errors and side effects

**Errors:** Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.

**Side effects:** Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.

## Related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/pipeline__load_source_dataframe/"><code>fabricops_kit.pipeline._load_source_dataframe</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/fabric_input_output.py#L632-L719">View read_lakehouse_excel on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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

</details>

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
- Source line: `632`
- Inbound references count: 1
- Outbound references count: 3

### AI implementation contract

- **required_context:** Requires 00_env_config config/env/target context for resolving the configured lakehouse Files path.
- **inputs:** config, env, target, relative_path, optional sheet_name, optional spark_session, and pandas read_excel keyword arguments.
- **output:** Spark DataFrame converted from the selected Excel worksheet.
- **side_effects:** Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.
- **verification:** Verify the DataFrame row count and schema after reading, and confirm the Excel file is appropriate for a small reference-style input.

### Inbound references

- <a href="../internal/pipeline__load_source_dataframe/"><code>fabricops_kit.pipeline._load_source_dataframe</code></a>

### Outbound references

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/fabric_input_output.py#L632-L719">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/fabric_input_output.py#L632-L719</a>
- Start line: `632`
- End line: `719`
- Signature:

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../internal/pipeline__load_source_dataframe/"><code>fabricops_kit.pipeline._load_source_dataframe</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

</details>
