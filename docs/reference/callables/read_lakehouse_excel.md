# read_lakehouse_excel

Read an Excel file from a configured Fabric lakehouse Files path.

## Purpose

Read an Excel file from a configured Fabric lakehouse Files path.

## At a glance

**Use when:**

- Use when reading .xlsx files from a configured Fabric lakehouse Files path, especially small reference files, mapping tables, or manually maintained business inputs.

**Do not use when:**

- Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

**Example:**

```python
mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)
```

**Errors:**

Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.

**Side effects:**

Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.

## Parameters

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

## Returns

Spark DataFrame converted from the selected Excel worksheet.

## Used by

Not documented yet

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

## Implementation details

### Call flow

```text
read_lakehouse_excel(...)
├── _get_spark(...)
├── _get_store(...)
└── _lakehouse_file_path(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L680-L767">View read_lakehouse_excel on GitHub</a>

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

## Maintainer internals

??? info "Nested helper functions: 3"

    These nested helpers support `read_lakehouse_excel` by handling lower-level implementation steps; expand this section only when maintaining or debugging the package internals.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Helper</th>
          <th>Role</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Helper"><code>_get_store</code></td>
          <td data-label="Role">Resolve a configured Fabric path for an environment and target.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L627-L667">src/fabricops_kit/config.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_spark</code></td>
          <td data-label="Role">Return an explicit Spark session or the active notebook global `spark`.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L125-L155">src/fabricops_kit/fabric_input_output.py</a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_lakehouse_file_path</code></td>
          <td data-label="Role">Return an ABFSS path under a configured lakehouse Files area.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L158-L168">src/fabricops_kit/fabric_input_output.py</a></td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source code"

        **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

        Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/config.py#L627-L667)

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

        **`def _get_spark(spark_session=None)`**

        Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L125-L155)

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

        **`def _lakehouse_file_path(store, env: str, target: str, relative_path: str) -> str`**

        Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L158-L168)

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L680-L767">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d01a524e6e404dc5b73c3d4ff41728d9f05e9cd8/src/fabricops_kit/fabric_input_output.py#L680-L767</a>
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

### Internal implementation helpers

### Call flow

```text
read_lakehouse_excel(...)
├── _get_spark(...)
├── _get_store(...)
└── _lakehouse_file_path(...)
```

</details>
