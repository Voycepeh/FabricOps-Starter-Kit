# read_lakehouse_excel

Read an Excel file from a configured Fabric lakehouse Files path.

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when source data arrives as an Excel workbook and should still follow configured Fabric lakehouse routing.

**Do not use when:**

- Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

**Additional context:**

Reads an Excel file from a configured lakehouse Files path and converts it into a Spark DataFrame for notebook processing.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_excel(
    config,
    env,
    target,
    relative_path,
    sheet_name=0,
    spark_session=None,
    **read_excel_kwargs,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)
```

</div>

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

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.

**Notes:**

Side effects:
- Creates a temporary local file during conversion.
- Materializes rows through pandas before creating a Spark DataFrame.

</details>

??? info "Call flow"

    ```text
    read_lakehouse_excel(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    └── _lakehouse_file_path(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for metadata loading and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L158-L168"><code>_lakehouse_file_path</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L125-L155"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L627-L667"><code>_get_store</code></a>
        </div>
      </section>
    </div>

    ??? example "View helper source by area"

        ??? example "Metadata loading helpers"

            **`def _lakehouse_file_path(store, env: str, target: str, relative_path: str) -> str`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L158-L168)

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

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L125-L155)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L627-L667)

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


<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:680`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L680-L767">View on GitHub</a>
</div>

??? example "Source code"

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
<summary>Machine-readable metadata / metadata details</summary>

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L680-L767">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L680-L767</a>
- Start line: `680`
- End line: `767`
- Signature:

```python
def read_lakehouse_excel(
    config,
    env,
    target,
    relative_path,
    sheet_name=0,
    spark_session=None,
    **read_excel_kwargs,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:680`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L680-L767">View on GitHub</a>
</div>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
