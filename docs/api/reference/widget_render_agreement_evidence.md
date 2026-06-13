# widget_render_agreement_evidence

Render the standalone agreement-evidence widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agreement.py:1386`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L1386-L1419">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 01_agreement when agreement records need supporting evidence that downstream users can audit.

**Additional context:**

Renders the supporting-evidence widget for agreement workflows so users can record links or files that justify an agreement.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_agreement_evidence(
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
| `config` | `Any` | Yes | Configuration containing agreement metadata routing and evidence table settings. |
| `env_name` | `str` | Yes | Environment key configured by ``00_env_config``. |
| `spark` | `Any` | Yes | Fabric Spark session used for metadata reads, file writes, and append-only evidence metadata writes. |

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

- `fabricops_kit.data_agreement._render_agreement_evidence_widget`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

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
    └── _render_agreement_evidence_widget(...)
        ├── _list_all_data_agreement_rows(...)
        │   └── …
        ├── _render_searchable_selector(...)
        │   └── …
        ├── _require_ipywidgets(...)
        ├── _save_agreement_evidence_records(...)
        │   └── …
        └── _widget_common(...)
    ```

??? info "Internal helpers used: 22"

    This callable uses 22 internal helpers for audit timestamp, metadata loading, validation, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/metadata.py#L147-L217"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L69-L75"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L61-L66"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L27-L58"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/fabric_input_output.py#L152-L157"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L589-L598"><code>_list_all_data_agreement_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L1265-L1383"><code>_render_agreement_evidence_widget</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L198-L308"><code>_render_searchable_selector</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L739-L770"><code>_save_agreement_evidence_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L687-L737"><code>_prepare_evidence_file_references</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/fabric_input_output.py#L105-L116"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L675-L684"><code>_get_notebookutils</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L627-L667"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L397-L402"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L149-L153"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/metadata.py#L101-L113"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L192-L195"><code>_html_escape</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/metadata.py#L120-L144"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/metadata.py#L116-L117"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L180-L189"><code>_widget_common</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L485-L486"><code>_write_row</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_agreement_evidence`
- Short name: `widget_render_agreement_evidence`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1386`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 01_agreement
- Glossary terms: notebook template, catalogue evidence

### AI implementation contract

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** config : FrameworkConfig or dict
    Configuration containing agreement metadata routing and evidence table
    settings.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads, file writes, and
    append-only evidence metadata writes.
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

- `fabricops_kit.data_agreement._render_agreement_evidence_widget`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L1386-L1419">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/data_agreement.py#L1386-L1419</a>
- Start line: `1386`
- End line: `1419`
- Signature:

```python
def widget_render_agreement_evidence(
    config: Any,
    env_name: str,
    spark: Any,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 22
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
