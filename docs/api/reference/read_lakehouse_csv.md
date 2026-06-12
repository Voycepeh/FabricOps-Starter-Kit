# read_lakehouse_csv

Read a CSV file from a configured Fabric lakehouse Files path.

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use for file-based source ingestion when the source is CSV and should be resolved through configured lakehouse paths.

**Do not use when:**

- Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL tables.

**Additional context:**

Reads a CSV file from the Files area of a configured Fabric lakehouse and returns it as a Spark DataFrame.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_csv(
    config,
    env,
    target,
    relative_path,
    spark_session=None,
    header=True,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_csv(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.csv", header=True, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `relative_path` | `str` | Yes | Path to the CSV file or folder under the lakehouse root, for example `"Files/raw/orders.csv"` or `"Files/raw/orders/"`. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |
| `header` | `bool, default True` | No | Whether the first row of the CSV file contains column names. |

## Returns

Spark DataFrame loaded from the lakehouse Files CSV path.

### Return interpretation

The returned DataFrame reflects Spark CSV parsing options; inspect schema and sample rows before profiling or writing.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

### Common failure causes

- The file path is wrong or outside the configured lakehouse.
- CSV options do not match the file shape.
- Spark cannot access the file.
- The selected environment is missing the source lakehouse target.

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

- `00_env_config`
- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from lakehouse Files; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    read_lakehouse_csv(...)
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

`fabricops_kit/fabric_input_output.py:326`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L326-L368">View on GitHub</a>
</div>

??? example "Source code"

    ```python
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
        spark_obj = _get_spark(spark_session)
        return spark_obj.read.option("header", header).csv(_lakehouse_file_path(store, env, target, relative_path))
    ```

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- Short name: `read_lakehouse_csv`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `326`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 00_env_config, 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, CSV read options, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the lakehouse Files CSV path.
- **side_effects:** Reads from lakehouse Files; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.
- **verification:** Verify relative_path points under Files, then check row count and schema after reading.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L326-L368">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L326-L368</a>
- Start line: `326`
- End line: `368`
- Signature:

```python
def read_lakehouse_csv(
    config,
    env,
    target,
    relative_path,
    spark_session=None,
    header=True,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:326`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L326-L368">View on GitHub</a>
</div>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
