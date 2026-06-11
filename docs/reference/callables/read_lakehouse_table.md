# read_lakehouse_table

## Purpose

Read a table from a configured Fabric lakehouse target.

## At a glance

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Item</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Item">Use when</td>
      <td data-label="Details">Use when reading a Delta table from a configured Fabric lakehouse target.</td>
    </tr>
    <tr>
      <td data-label="Item">Do not use when</td>
      <td data-label="Details">Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for warehouse SQL tables.</td>
    </tr>
    <tr>
      <td data-label="Item">Example</td>
      <td data-label="Details">```python
df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", table="orders", spark_session=spark)
```</td>
    </tr>
    <tr>
      <td data-label="Item">Errors</td>
      <td data-label="Details">Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.</td>
    </tr>
    <tr>
      <td data-label="Item">Side effects</td>
      <td data-label="Details">Reads from a lakehouse table; it does not write metadata, tables, or files.</td>
    </tr>
    <tr>
      <td data-label="Item">Related functions</td>
      <td data-label="Details">- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a><br>- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a><br>- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a><br>- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a></td>
    </tr>
  </tbody>
</table>
</div>

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
      <td data-label="Parameter"><code>table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Table name under the lakehouse `Tables` area.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark session to use. If omitted, the helper uses the notebook global `spark`.</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

Spark DataFrame loaded from the configured lakehouse table.

## Used by

- `fabricops_kit.data_agreement._ensure_metadata_tables`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_metadata_rows`
- `fabricops_kit.governance_review._setup_governance_metadata_tables`
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`
- `fabricops_kit.metadata._setup_notebook_registry_table`

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._current_database_matches`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._registered_table_identifier`
- `fabricops_kit.fabric_input_output._uses_registered_metadata_table`

## Implementation details

### Call flow

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

## Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L171-L224">View read_lakehouse_table on GitHub</a>

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

## Nested helper functions

??? info "Nested helper functions: 7"

    These helpers support `read_lakehouse_table` by handling shared implementation tasks reached from the public call flow; expand the source block only when you need maintainer-level details.

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
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L618-L658"><code>src/fabricops_kit/config.py#L618-L658</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_current_database_matches</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L107-L115"><code>src/fabricops_kit/fabric_input_output.py#L107-L115</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_spark</code></td>
          <td data-label="Role">Return an explicit Spark session or the active notebook global `spark`.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L125-L155"><code>src/fabricops_kit/fabric_input_output.py#L125-L155</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_normalize_table_name</code></td>
          <td data-label="Role">Return a safe Spark table name, never a nested folder path.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L81-L90"><code>src/fabricops_kit/fabric_input_output.py#L81-L90</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_registered_table_identifier</code></td>
          <td data-label="Role">Return a metadata lakehouse-qualified Spark table identifier.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L97-L99"><code>src/fabricops_kit/fabric_input_output.py#L97-L99</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_quote_identifier</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L93-L94"><code>src/fabricops_kit/fabric_input_output.py#L93-L94</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_uses_registered_metadata_table</code></td>
          <td data-label="Role">Return whether a target should use Spark table registration.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L102-L104"><code>src/fabricops_kit/fabric_input_output.py#L102-L104</code></a></td>
        </tr>
      </tbody>
    </table>

    ??? example "View helper source code"

        **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

        Used by `read_lakehouse_table` through the implementation path shown above.

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

        **`def _current_database_matches(spark_obj: Any, store: FabricStore) -> bool`**

        Used by `read_lakehouse_table` through the implementation path shown above.

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

        **`def _get_spark(spark_session=None)`**

        Used by `read_lakehouse_table` through the implementation path shown above.

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

        **`def _normalize_table_name(table: str) -> str`**

        Used by `read_lakehouse_table` through the implementation path shown above.

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

        Used by `read_lakehouse_table` through the implementation path shown above.

        ```python
        def _registered_table_identifier(store: FabricStore, table: str) -> str:
            """Return a metadata lakehouse-qualified Spark table identifier."""
            return f"{_quote_identifier(store.name)}.{_quote_identifier(_normalize_table_name(table))}"
        ```

        **`def _quote_identifier(identifier: str) -> str`**

        Used by `read_lakehouse_table` through the implementation path shown above.

        ```python
        def _quote_identifier(identifier: str) -> str:
            return f"`{str(identifier).replace('`', '``')}`"
        ```

        **`def _uses_registered_metadata_table(target: str) -> bool`**

        Used by `read_lakehouse_table` through the implementation path shown above.

        ```python
        def _uses_registered_metadata_table(target: str) -> bool:
            """Return whether a target should use Spark table registration."""
            return str(target or "").strip().lower() == "metadata"
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
- Inbound references count: 11
- Outbound references count: 6

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, table, optional schema, verbose flag, and spark_session.
- **output:** Spark DataFrame loaded from the configured lakehouse table.
- **side_effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.
- **verification:** Verify the target/table name comes from CONFIG and check the returned DataFrame schema or row count before downstream transformations.

### Inbound references

- `fabricops_kit.data_agreement._ensure_metadata_tables`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_metadata_rows`
- `fabricops_kit.governance_review._setup_governance_metadata_tables`
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`
- `fabricops_kit.metadata._setup_notebook_registry_table`

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._current_database_matches`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._registered_table_identifier`
- `fabricops_kit.fabric_input_output._uses_registered_metadata_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L171-L224">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L171-L224</a>
- Start line: `171`
- End line: `224`
- Signature:

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

### Internal relationship graph

The human-readable implementation view above is the source of truth for public call flow, public callable source, and collapsed nested helper details.

### Public related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Call flow

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

</details>
