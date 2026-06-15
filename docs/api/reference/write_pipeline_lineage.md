# write_pipeline_lineage

Write many-to-many source-to-target lineage evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:627`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L627-L712">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use near the end of 02_pipeline after transformations and target config resolution have produced lineage-ready records.

**Additional context:**

Persists lineage records for a pipeline run so source tables, target tables, and transformation steps remain traceable.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_pipeline_lineage(
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None=None,
    dataset_name: str='',
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    metadata_table: str=LINEAGE_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Spark session used to create lineage rows. |
| `config` | `Any` | Yes | Metadata route from ``00_env_config``. |
| `env` | `str` | Yes | Not documented yet |
| `run_id` | `str` | Yes | Pipeline run identifier. |
| `source_definitions` | `Mapping[str, Mapping[str, Any]]` | Yes | Source and target definitions keyed by alias. |
| `target_definitions` | `Mapping[str, Mapping[str, Any]]` | Yes | Not documented yet |
| `relationships` | `list[Mapping[str, Any]] \| None` | No | Many-to-many lineage relationships. Each item may contain ``sources``, ``targets``, ``operation``, and ``description``. When omitted, every source is linked to every target. |
| `dataset_name` | `str` | No | Governance context embedded in lineage payloads. |
| `agreement_id` | `str` | No | Not documented yet |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `metadata_table` | `str` | No | Metadata lineage table. |
| `mode` | `str` | No | Write mode for lineage evidence. |

## Returns

Status, row count, and lineage rows.

### Return interpretation

A successful result indicates lineage rows were prepared for metadata persistence; review returned counts against expected transformation steps.

## Raises / Errors

Not documented yet

### Common failure causes

- Lineage records are empty or malformed.
- run_id, source, or target identifiers are missing.
- The metadata table cannot be written.
- Audit fields cannot be resolved from configuration.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_audit_fields`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    write_pipeline_lineage(...)
    ├── _build_metadata_table_key(...)
    │   └── _stable_metadata_key(...)
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   │   └── …
    │   └── _normalize_schema_name(...)
    ├── _definition_name(...)
    ├── _now_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── …
    ├── _runtime_audit_fields(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   └── …
    │   └── _now_iso(...)
    │       └── …
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        │   └── …
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_table_path(...)
            └── …
    ```

??? info "Internal helpers used: 16"

    This callable uses 16 internal helpers for audit timestamp, metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/metadata.py#L149-L222"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/config.py#L70-L76"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/config.py#L62-L67"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L49-L60"><code>_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/config.py#L27-L59"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/metadata.py#L79-L80"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/metadata.py#L74-L76"><code>_stable_metadata_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L23-L24"><code>_definition_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/metadata.py#L103-L115"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L19-L20"><code>_now_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/metadata.py#L122-L146"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/metadata.py#L118-L119"><code>_safe_str</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_pipeline_lineage`
- Short name: `write_pipeline_lineage`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `627`
- Inbound references count: 0
- Outbound references count: 6
- Used in templates: 02_pipeline
- Glossary terms: source table, target table, catalogue evidence, metadata lakehouse

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Lineage evidence`.
- **inputs:** spark, config, env, run_id, source_definitions, target_definitions, relationships, and governance context.
- **output:** Status, row count, and lineage rows.
- **side_effects:** Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_audit_fields`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L627-L712">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L627-L712</a>
- Start line: `627`
- End line: `712`
- Signature:

```python
def write_pipeline_lineage(
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None=None,
    dataset_name: str='',
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    metadata_table: str=LINEAGE_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation summary

- Internal helper count: 16
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
