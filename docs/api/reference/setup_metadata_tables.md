# setup_metadata_tables

Create or validate all FabricOps metadata tables through one setup action.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config.py:1156`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1156-L1283">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use after setup_notebook in 00_env_config when bootstrapping or validating the metadata store for an environment.

### Do not use when

- Do not use for writing business data or pipeline target tables; use write_data or write_warehouse_table for data outputs.

### Additional context

Prepares FabricOps metadata tables through configured metadata target ABFSS paths, not Spark partial namespaces or an attached default lakehouse.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_metadata_tables(
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None=None,
    require_active_steward: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
setup_metadata_tables(
    spark=spark,
    config=CONFIG,
    env="Sandbox",
)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Fabric Spark session used by the table setup helpers. |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | Shared ``00_env_config`` configuration containing the metadata target. |
| `env` | `str` | Yes | Environment key to prepare. |
| `metadata_schema` | `str \| None` | No | Optional schema name for schema-enabled Fabric Lakehouses. Keep ``None`` for classic Lakehouses that store metadata tables under ``Tables/<table_name>``. Use a simple schema such as ``"METADATA"`` to create and validate registered tables such as ``METADATA.METADATA_DATA_AGREEMENT``. |
| `require_active_steward` | `bool` | No | Forwarded to the agreement metadata setup to optionally require an active steward before returning success. |

## Returns

Setup result describing metadata table creation or validation status.

### Return interpretation

The returned setup status tells you which metadata tables were created or validated and whether the environment is ready for workflows that write evidence.

## Raises / Errors

Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.

### Common failure causes

- The configured metadata lakehouse ABFSS path is missing or invalid.
- Spark cannot create or inspect metadata tables through the configured ABFSS paths.
- The selected environment does not include metadata routing.
- The caller lacks permission to create or update metadata tables.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config._get_metadata_table_schema_registry`
- `fabricops_kit.config._metadata_schema_field_names`
- `fabricops_kit.config._metadata_tables_from_setup_results`
- `fabricops_kit.config._resolve_metadata_schema`
- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_framework_config`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._get_governance_metadata_schemas`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `00_env_config`

**Side effects:**

Creates or validates FabricOps metadata tables through configured metadata target ABFSS paths, not Spark partial namespaces.

**Notes:**

This is the v1 notebook setup action for metadata provisioning. It keeps
``00_env_config`` simple while delegating to internal helpers that route all
metadata reads and writes through the configured metadata target. With
``metadata_schema=None``, setup preserves classic path-based Lakehouse
behavior under ``Tables/<table_name>``. With ``metadata_schema`` set, setup
uses schema-aware Lakehouse paths such as ``Tables/<schema>/<table>`` and
does not bake the schema into configured metadata table names. FabricOps may warn about
legacy nested or unidentified Delta folders, but it does not delete or
migrate user data automatically.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    setup_metadata_tables(...)
    ├── _get_governance_metadata_schemas(...)
    │   ├── _schema(...)
    │   │   └── …
    │   └── _spark_types(...)
    ├── _get_metadata_table_schema_registry(...)
    │   ├── _get_governance_metadata_schemas(...)
    │   │   └── …
    │   ├── _string_metadata_schema(...)
    │   └── _validate_framework_config(...)
    │       └── …
    ├── _list_data_stewards(...)
    │   ├── _active_steward(...)
    │   │   └── …
    │   ├── _config_value(...)
    │   ├── _latest_by_key(...)
    │   │   └── …
    │   └── read_lakehouse_table(...)
    │       └── …
    ├── _metadata_schema_field_names(...)
    ├── _metadata_tables_from_setup_results(...)
    ├── _resolve_metadata_schema(...)
    │   └── _get_store(...)
    │       └── …
    ├── _setup_metadata_table_registry(...)
    │   ├── _create_empty_metadata_dataframe(...)
    │   ├── _is_table_not_found_error(...)
    │   ├── _metadata_schema_field_names(...)
    │   ├── _metadata_table_columns(...)
    │   │   └── …
    │   ├── read_lakehouse_table(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
    │       └── …
    ├── _validate_framework_config(...)
    │   ├── _validate_audit_timezone(...)
    │   └── FrameworkConfig(...)
    └── _validate_metadata_table_registration(...)
        ├── _detect_nested_metadata_delta_folders(...)
        │   └── …
        ├── _get_active_metadata_tables(...)
        │   └── …
        ├── _get_store(...)
        │   └── …
        ├── _resolve_metadata_schema(...)
        │   └── …
        ├── _validate_framework_config(...)
        │   └── …
        └── read_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 27"

    This callable uses 27 internal helpers for audit timestamp, metadata loading, validation, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L150-L182"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L118-L144"><code>_check_metadata_schema_field_names</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1059-L1061"><code>_create_empty_metadata_dataframe</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L957-L981"><code>_detect_nested_metadata_delta_folders</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L914-L940"><code>_get_active_metadata_tables</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L153-L194"><code>_get_governance_metadata_schemas</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1009-L1038"><code>_get_metadata_table_schema_registry</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L197-L217"><code>_is_table_not_found_error</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L984-L988"><code>_metadata_schema_field_names</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1050-L1056"><code>_metadata_table_columns</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L943-L954"><code>_metadata_tables_from_setup_results</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1065-L1072"><code>_resolve_metadata_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1074-L1104"><code>_setup_metadata_table_registry</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L991-L1006"><code>_string_metadata_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1107-L1153"><code>_validate_metadata_table_registration</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L525-L596"><code>_validate_framework_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L599-L639"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L109-L115"><code>_spark_types</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1041-L1047"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L642-L681"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/data_agreement.py#L438-L448"><code>_active_steward</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/data_agreement.py#L410-L416"><code>_latest_by_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L147-L150"><code>_schema</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_metadata_tables`
- Short name: `setup_metadata_tables`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source line: `1156`
- Inbound references count: 0
- Outbound references count: 10
- Used in templates: 00_env_config
- Glossary terms: metadata lakehouse, evidence

### Implementation contract

- **required_context:** Requires the metadata target from 00_env_config; metadata tables are created and validated through configured metadata target paths and do not require an attached default lakehouse.
- **inputs:** spark, config, env, and optional require_active_steward controls used to prepare metadata storage through configured metadata routing.
- **output:** Setup result describing metadata table creation or validation status.
- **side_effects:** Creates or validates FabricOps metadata tables through configured metadata target ABFSS paths, not Spark partial namespaces.
- **failure_modes:** Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.
- **verification:** Verify metadata setup completes before recommending agreement, profiling, lineage, stability, or governance workflows that persist evidence.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_metadata_table_schema_registry`
- `fabricops_kit.config._metadata_schema_field_names`
- `fabricops_kit.config._metadata_tables_from_setup_results`
- `fabricops_kit.config._resolve_metadata_schema`
- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_framework_config`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._get_governance_metadata_schemas`

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1156-L1283">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L1156-L1283</a>
- Start line: `1156`
- End line: `1283`
- Signature:

```python
def setup_metadata_tables(
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None=None,
    require_active_steward: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 27
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
