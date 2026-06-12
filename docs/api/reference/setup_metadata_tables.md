# setup_metadata_tables

Create or validate all FabricOps metadata tables through one setup action.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config.py:1114`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1114-L1218">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use after setup_notebook in 00_env_config when bootstrapping or validating the metadata store for an environment.

**Do not use when:**

- Do not use for writing business data or pipeline target tables; use write_lakehouse_table or write_warehouse_table for data outputs.

**Additional context:**

Prepares FabricOps metadata tables through configured metadata target ABFSS paths, not Spark partial namespaces or an attached default lakehouse.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_metadata_tables(
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
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
- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_framework_config`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._get_governance_metadata_schemas`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `00_env_config`

**Side effects:**

Creates or validates FabricOps metadata tables through configured metadata target ABFSS paths, not Spark partial namespaces.

**Notes:**

This is the v1 notebook setup action for metadata provisioning. It keeps
``00_env_config`` simple while delegating to internal helpers that route all
metadata reads and writes through configured metadata target ABFSS paths,
never Spark partial namespaces or the current/default lakehouse context.

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
        ├── _validate_framework_config(...)
        │   └── …
        └── read_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 25"

    This callable uses 25 internal helpers for audit timestamp, metadata loading, validation, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L27-L58"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1040-L1042"><code>_create_empty_metadata_dataframe</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L942-L962"><code>_detect_nested_metadata_delta_folders</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L898-L925"><code>_get_active_metadata_tables</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/governance_review.py#L152-L195"><code>_get_governance_metadata_schemas</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L990-L1019"><code>_get_metadata_table_schema_registry</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/governance_review.py#L198-L218"><code>_is_table_not_found_error</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/data_agreement.py#L453-L482"><code>_list_data_stewards</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L965-L969"><code>_metadata_schema_field_names</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1031-L1037"><code>_metadata_table_columns</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L928-L939"><code>_metadata_tables_from_setup_results</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1045-L1069"><code>_setup_metadata_table_registry</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L972-L987"><code>_string_metadata_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/data_agreement.py#L414-L430"><code>_to_bool</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1072-L1111"><code>_validate_metadata_table_registration</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/governance_review.py#L112-L137"><code>_validate_schema_field_names</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L551-L624"><code>_validate_framework_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/governance_review.py#L103-L109"><code>_spark_types</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1022-L1028"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L627-L667"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/data_agreement.py#L433-L443"><code>_active_steward</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/data_agreement.py#L397-L402"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/data_agreement.py#L149-L153"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/data_agreement.py#L405-L411"><code>_latest_by_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/governance_review.py#L140-L143"><code>_schema</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.config.setup_metadata_tables`
- Short name: `setup_metadata_tables`
- Module: `config`
- Classification: Callable
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source line: `1114`
- Inbound references count: 0
- Outbound references count: 9
- Used in templates: 00_env_config
- Glossary terms: metadata lakehouse, catalogue evidence

### AI implementation contract

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
- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_framework_config`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._get_governance_metadata_schemas`

### Raw source metadata

- Source file path: `src/fabricops_kit/config.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1114-L1218">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L1114-L1218</a>
- Start line: `1114`
- End line: `1218`
- Signature:

```python
def setup_metadata_tables(
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    require_active_steward: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 25
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
