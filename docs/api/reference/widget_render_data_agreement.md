# widget_render_data_agreement

Render the standalone data-agreement intake widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agreement.py:1468`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L1468-L1487">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 01_agreement after steward context exists and before pipeline or governance notebooks need an approved agreement selection.

**Additional context:**

Renders the data agreement intake widget used to capture agreement identity, scope, and business metadata for later notebook workflows.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_data_agreement(
    config: Any=None,
    env_name: str | None=None,
    spark: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `Any` | No | Configuration containing agreement widget fields and metadata routing. |
| `env_name` | `str \| None` | No | Environment key configured by ``00_env_config``. |
| `spark` | `Any` | Yes | Fabric Spark session used for metadata reads and append-only writes. |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |

## Returns

dict[str, Any]
    Rendered controls, including read-only generated-identifier context.

### Return interpretation

The rendered widget collects agreement input; downstream helpers can only use the agreement after the user saves valid values.

## Raises / Errors

Not documented yet

### Common failure causes

- ipywidgets is not available in the runtime.
- Required agreement fields are missing.
- Agreement identifiers conflict with existing metadata.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.data_agreement._render_maintenance_widget`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `01_agreement`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_render_data_agreement(...)
    ├── _render_maintenance_widget(...)
    │   ├── _agreement_identity_text(...)
    │   │   └── …
    │   ├── _collect_custom_fields(...)
    │   │   └── …
    │   ├── _config_value(...)
    │   ├── _create_or_update_data_agreement(...)
    │   │   └── …
    │   ├── _create_or_update_data_steward(...)
    │   │   └── …
    │   ├── _deserialize_custom_fields(...)
    │   ├── _get_widget_visible_fields(...)
    │   │   └── …
    │   ├── _list_data_agreements(...)
    │   │   └── …
    │   ├── _list_data_stewards(...)
    │   │   └── …
    │   ├── _render_custom_fields(...)
    │   │   └── …
    │   ├── _render_searchable_selector(...)
    │   │   └── …
    │   ├── _require_ipywidgets(...)
    │   ├── _standard_widget(...)
    │   │   └── …
    │   ├── _to_bool(...)
    │   └── _to_iso_date(...)
    └── resolve_fabric_context(...)
        └── get_default_fabric_context(...)
    ```

??? info "Internal helpers used: 42"

    This callable uses 42 internal helpers for audit timestamp, metadata loading, validation, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/config.py#L191-L197"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/config.py#L183-L188"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L158-L180"><code>_get_widget_visible_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/config.py#L148-L180"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L451-L455"><code>_generate_steward_id</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L366-L399"><code>_collect_custom_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L497-L507"><code>_parse_iso_date</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L119-L148"><code>_deserialize_custom_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/config.py#L597-L637"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L570-L576"><code>_parse_contract_version</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L102-L116"><code>_serialize_custom_fields</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/config.py#L640-L679"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L438-L448"><code>_active_steward</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L1063-L1073"><code>_agreement_identity_text</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L636-L640"><code>_business_agreement_snapshot</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L626-L627"><code>_generate_agreement_id</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L195-L198"><code>_html_escape</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L410-L416"><code>_latest_by_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L579-L582"><code>_next_minor_version</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L313-L363"><code>_render_custom_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L1076-L1284"><code>_render_maintenance_widget</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L1047-L1060"><code>_standard_widget</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L630-L633"><code>_to_iso_date</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_data_agreement`
- Short name: `widget_render_data_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1468`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 01_agreement
- Glossary terms: notebook template

### Implementation contract

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** config : FrameworkConfig or dict
    Configuration containing agreement widget fields and metadata routing.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads and append-only writes.
- **output:** dict[str, Any]
    Rendered controls, including read-only generated-identifier context.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.data_agreement._render_maintenance_widget`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L1468-L1487">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8fa331e352aa534d4c341adaf3c1f6635a2051b/src/fabricops_kit/data_agreement.py#L1468-L1487</a>
- Start line: `1468`
- End line: `1487`
- Signature:

```python
def widget_render_data_agreement(
    config: Any=None,
    env_name: str | None=None,
    spark: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 42
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
