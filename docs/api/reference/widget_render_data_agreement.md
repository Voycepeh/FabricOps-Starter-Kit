# widget_render_data_agreement

Render the standalone data-agreement intake widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agreement.py:1442`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L1442-L1459">View on GitHub</a>
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
    config: Any,
    env_name: str,
    spark: Any,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `Any` | Yes | Configuration containing agreement widget fields and metadata routing. |
| `env_name` | `str` | Yes | Environment key configured by ``00_env_config``. |
| `spark` | `Any` | Yes | Fabric Spark session used for metadata reads and append-only writes. |

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

- `fabricops_kit.data_agreement._render_maintenance_widget`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

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
    └── _render_maintenance_widget(...)
        ├── _agreement_identity_text(...)
        │   └── …
        ├── _collect_custom_fields(...)
        │   └── …
        ├── _config_value(...)
        ├── _create_or_update_data_agreement(...)
        │   └── …
        ├── _create_or_update_data_steward(...)
        │   └── …
        ├── _deserialize_custom_fields(...)
        ├── _get_widget_visible_fields(...)
        │   └── …
        ├── _list_data_agreements(...)
        │   └── …
        ├── _list_data_stewards(...)
        │   └── …
        ├── _render_custom_fields(...)
        │   └── …
        ├── _render_searchable_selector(...)
        │   └── …
        ├── _require_ipywidgets(...)
        ├── _standard_widget(...)
        │   └── …
        ├── _to_bool(...)
        └── _to_iso_date(...)
    ```

??? info "Internal helpers used: 42"

    This callable uses 42 internal helpers for audit timestamp, metadata loading, validation, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L147-L219"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L502-L552"><code>_create_or_update_data_steward</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L69-L75"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L61-L66"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L156-L177"><code>_get_widget_visible_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L27-L58"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/fabric_input_output.py#L152-L165"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L446-L450"><code>_generate_steward_id</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L570-L586"><code>_latest_agreement_versions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L589-L598"><code>_list_all_data_agreement_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L601-L608"><code>_list_data_agreements</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L453-L482"><code>_list_data_stewards</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L198-L308"><code>_render_searchable_selector</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L414-L430"><code>_to_bool</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L362-L394"><code>_collect_custom_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L489-L499"><code>_parse_iso_date</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L118-L146"><code>_deserialize_custom_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L627-L667"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/fabric_input_output.py#L105-L116"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L555-L561"><code>_parse_contract_version</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L102-L115"><code>_serialize_custom_fields</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L670-L708"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L433-L443"><code>_active_steward</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L1041-L1051"><code>_agreement_identity_text</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L621-L625"><code>_business_agreement_snapshot</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L397-L402"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L149-L153"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L101-L113"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L628-L672"><code>_create_or_update_data_agreement</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L611-L612"><code>_generate_agreement_id</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L192-L195"><code>_html_escape</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L405-L411"><code>_latest_by_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L564-L567"><code>_next_minor_version</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L310-L359"><code>_render_custom_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L1054-L1262"><code>_render_maintenance_widget</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L120-L144"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L116-L117"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L1025-L1038"><code>_standard_widget</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L615-L618"><code>_to_iso_date</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L180-L189"><code>_widget_common</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L485-L486"><code>_write_row</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_data_agreement`
- Short name: `widget_render_data_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1442`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 01_agreement
- Glossary terms: notebook template

### AI implementation contract

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

- `fabricops_kit.data_agreement._render_maintenance_widget`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L1442-L1459">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/data_agreement.py#L1442-L1459</a>
- Start line: `1442`
- End line: `1459`
- Signature:

```python
def widget_render_data_agreement(
    config: Any,
    env_name: str,
    spark: Any,
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
