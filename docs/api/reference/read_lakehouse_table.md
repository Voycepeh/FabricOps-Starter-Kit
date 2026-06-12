# read_lakehouse_table

## Signature

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

## Summary

Read a table from a configured Fabric lakehouse target.

## Usage note

- Use when notebook code needs a managed lakehouse table rather than a file path or warehouse SQL query.

**Do not use when:**

- Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for warehouse SQL tables.

**Additional context:**

Reads a Delta table from a configured Fabric lakehouse target using the environment routing supplied by 00_env_config.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `table` | `str` | Yes | Table name under the lakehouse `Tables` area. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |

## Returns

Spark DataFrame loaded from the configured lakehouse table.

### Return interpretation

The returned DataFrame represents the resolved lakehouse table; validate row counts and schema before relying on it for guardrails or writes.

## Raises / Errors

Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.

### Common failure causes

- The target or table name is misspelled.
- The selected environment does not define the requested lakehouse target.
- Spark cannot access the table.
- The caller lacks permission to read the lakehouse.

## Example

```python
df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", table="orders", spark_session=spark)
```

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

**Glossary terms**

- **Source table:** An input table or file read by the pipeline.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Developer details

- Module: `fabric_input_output`
- Classification: Callable
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `171`
- Signature:

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

**Used in templates:**

- `00_env_config`
- `01_agreement`
- `02_pipeline`
- `03_governance`
- `99_explore`

**Side effects:**

Reads from a lakehouse table; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._current_database_matches`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._registered_table_identifier`
- `fabricops_kit.fabric_input_output._uses_registered_metadata_table`

## Internal implementation summary

??? info "Call flow"

    ```text
    read_lakehouse_table(...)
    ├── _current_database_matches(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    ├── _normalize_table_name(...)
    ├── _registered_table_identifier(...)
    │   ├── _normalize_table_name(...)
    │   └── _quote_identifier(...)
    └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 7"

    This callable uses 7 internal helpers for metadata loading, fabric or spark access, and other.

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
          <td data-label="Helpers"><code>_current_database_matches</code>, <code>_normalize_table_name</code>, <code>_registered_table_identifier</code>, <code>_uses_registered_metadata_table</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_get_spark</code>, <code>_get_store</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_quote_identifier</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Metadata loading helpers"

            **`def _current_database_matches(spark_obj: Any, store: FabricStore) -> bool`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L107-L115)

            ```python
            def _current_database_matches(spark_obj: Any, store: FabricStore) -> bool:
                catalog = getattr(spark_obj, "catalog", None)
                current_database = getattr(catalog, "currentDatabase", None)
                if not callable(current_database):
                    return False
                try:
                    return str(current_database()).strip().lower() == store.name.strip().lower()
                except Exception:
                    return False
            ```

            **`def _normalize_table_name(table: str) -> str`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L81-L90)

            ```python
            def _normalize_table_name(table: str) -> str:
                """Return a safe Spark table name, never a nested folder path."""
                value = str(table or "").strip()
                if not value:
                    raise ValueError("table is required.")
                if any(separator in value for separator in ("/", "\\")) or ".." in value:
                    raise ValueError("table must be a table name, not a file path or nested folder path.")
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                    raise ValueError("table must contain only letters, numbers, and underscores, and must not start with a number.")
                return value
            ```

            **`def _registered_table_identifier(store: FabricStore, table: str) -> str`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L97-L99)

            ```python
            def _registered_table_identifier(store: FabricStore, table: str) -> str:
                """Return a metadata lakehouse-qualified Spark table identifier."""
                return f"{_quote_identifier(store.name)}.{_quote_identifier(_normalize_table_name(table))}"
            ```

            **`def _uses_registered_metadata_table(target: str) -> bool`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L102-L104)

            ```python
            def _uses_registered_metadata_table(target: str) -> bool:
                """Return whether a target should use Spark table registration."""
                return str(target or "").strip().lower() == "metadata"
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

        ??? example "Other helpers"

            **`def _quote_identifier(identifier: str) -> str`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L93-L94)

            ```python
            def _quote_identifier(identifier: str) -> str:
                return f"`{str(identifier).replace('`', '``')}`"
            ```


## Used by

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_metadata_rows`
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`

## Source link

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L171-L224">View read_lakehouse_table on GitHub</a>

```python
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
    table_name = _normalize_table_name(table)

    spark_obj = _get_spark(spark_session)
    if _uses_registered_metadata_table(target):
        try:
            return spark_obj.table(_registered_table_identifier(store, table_name))
        except Exception:
            if _current_database_matches(spark_obj, store):
                try:
                    return spark_obj.table(table_name)
                except Exception:
                    pass
    path = f"{store.root.rstrip('/')}/Tables/{table_name}"
    return spark_obj.read.format("delta").load(path)
```

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_table`
- Short name: `read_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `171`
- Inbound references count: 10
- Outbound references count: 6
- Used in templates: 00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore
- Glossary terms: source table, metadata lakehouse

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, table, optional schema, verbose flag, and spark_session.
- **output:** Spark DataFrame loaded from the configured lakehouse table.
- **side_effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.
- **verification:** Verify the target/table name comes from CONFIG and check the returned DataFrame schema or row count before downstream transformations.

### Inbound references

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_metadata_rows`
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._current_database_matches`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._registered_table_identifier`
- `fabricops_kit.fabric_input_output._uses_registered_metadata_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L171-L224">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/fabric_input_output.py#L171-L224</a>
- Start line: `171`
- End line: `224`
- Signature:

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Internal implementation summary

- Internal helper count: 7
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
