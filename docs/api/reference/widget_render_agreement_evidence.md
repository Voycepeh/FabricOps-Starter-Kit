# widget_render_agreement_evidence

Render the standalone agreement-evidence widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agreement.py:1407`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L1407-L1440">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 01_agreement when agreement records need supporting evidence that downstream users can audit.

### Additional context

Renders the supporting-evidence widget for agreement workflows so users can record links or files that justify an agreement.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_agreement_evidence(
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
| `spark` | `Any` | Yes | Fabric Spark session used for metadata reads, file writes, and append-only evidence metadata writes. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |

## Returns

dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.

### Return interpretation

The widget records evidence references when saved; review the resulting metadata rows before relying on them in handover or audit flows.

## Raises / Errors

Not documented yet

### Common failure causes

- Evidence details are incomplete.
- File or URL references are malformed.
- Widget state is reset before saving.
- The configured metadata target is not writable.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.data_agreement._render_agreement_evidence_widget`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `01_agreement`

**Side effects:**

Not documented yet

**Notes:**

This public wrapper is intended for the separate-widget ``01_agreement`` layout.
Evidence files must be uploaded manually to the metadata lakehouse
``Files`` area first. The widget appends one file-reference row per
pasted ``Files/...`` path to ``METADATA_DATA_AGREEMENT_EVIDENCE`` and
does not read or write binary file content.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_render_agreement_evidence(...)
    ├── _render_agreement_evidence_widget(...)
    │   ├── _list_all_data_agreement_rows(...)
    │   │   └── …
    │   ├── _render_searchable_selector(...)
    │   │   └── …
    │   ├── _require_ipywidgets(...)
    │   ├── _save_agreement_evidence_records(...)
    │   │   └── …
    │   └── _widget_common(...)
    └── resolve_fabric_context(...)
        └── get_default_fabric_context(...)
    ```

??? info "Internal helpers used: 23"

    This callable uses 23 internal helpers for audit timestamp, metadata loading, validation, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L193-L199"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L185-L190"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L150-L182"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L702-L752"><code>_prepare_evidence_file_references</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L599-L639"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L690-L699"><code>_get_notebookutils</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L642-L681"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L195-L198"><code>_html_escape</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_agreement_evidence`
- Short name: `widget_render_agreement_evidence`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1407`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 01_agreement
- Glossary terms: notebook template, evidence

### Implementation contract

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads, file writes, and
    append-only evidence metadata writes.
context : dict[str, Any], optional
    Advanced override for the active Fabric context. When omitted, the
    helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
- **output:** dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.data_agreement._render_agreement_evidence_widget`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L1407-L1440">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/data_agreement.py#L1407-L1440</a>
- Start line: `1407`
- End line: `1440`
- Signature:

```python
def widget_render_agreement_evidence(
    spark: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 23
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
