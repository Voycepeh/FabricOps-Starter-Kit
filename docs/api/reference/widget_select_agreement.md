# widget_select_agreement

Render an agreement selector and optionally register the active notebook.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agreement.py:788`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L788-L1020">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use near the start of 02_pipeline or 99_explore before reads, profiling, lineage, or governance evidence need an agreement id.

**Do not use when:**

- Do not use for guardrail target selection; use widget_select_guardrail_target for catalogue-backed guardrail authoring and review targets.

**Additional context:**

Displays an agreement selector and stores the chosen agreement so pipeline and exploration notebooks can bind work to approved business context.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_agreement(
    agreement_rows_or_config: Any,
    env_name: str | None=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    register_notebook: bool=False,
    notebook_type: str | None=None,
    environment_name: str | None=None,
    dataset_name: str | None=None,
    table_name: str | None=None,
    topic: str | None=None,
    pipeline_name: str | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
widget_select_agreement(CONFIG, env="Sandbox", spark_session=spark)
agreement = get_selected_agreement()
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement_rows_or_config` | `Any` | Yes | Pass ``CONFIG`` in normal notebooks, or provide preloaded agreement rows when the caller already has them available. |
| `env_name` | `str \| None` | No | Environment key used to load agreements when ``CONFIG`` is supplied. |
| `spark_session` | `Any` | No | Fabric Spark session used for configured metadata-table reads. |
| `metadata_schema` | `str \| None` | No | Explicit metadata Lakehouse schema override. Pass ``METADATA_SCHEMA`` from ``00_env_config`` in schema-enabled Lakehouses so agreement reads and notebook registration use the same metadata route. |
| `register_notebook` | `bool` | No | When True, render registration status and a button that links the current notebook to the selected agreement. |
| `notebook_type` | `str \| None` | No | Workflow metadata passed to ``_register_current_notebook`` when ``register_notebook`` is enabled. |
| `environment_name` | `str \| None` | No | Not documented yet |
| `dataset_name` | `str \| None` | No | Not documented yet |
| `table_name` | `str \| None` | No | Not documented yet |
| `topic` | `str \| None` | No | Not documented yet |
| `pipeline_name` | `str \| None` | No | Not documented yet |

## Returns

Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.

### Return interpretation

A visible selection widget does not mean an agreement is selected; call get_selected_agreement after the user chooses a row.

## Raises / Errors

Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.

### Common failure causes

- No agreement metadata rows are available.
- The user has not selected an agreement.
- Notebook registration metadata cannot be written.
- The configured metadata lakehouse cannot be read.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.data_agreement._html_escape`
- `fabricops_kit.data_agreement._latest_agreement_versions`
- `fabricops_kit.data_agreement._list_data_agreements`
- `fabricops_kit.data_agreement._render_searchable_selector`
- `fabricops_kit.data_agreement._require_ipywidgets`
- `fabricops_kit.metadata._current_notebook_active_registrations`
- `fabricops_kit.metadata._register_current_notebook`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Displays an IPython widget and may register the active notebook selection in metadata when requested.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_select_agreement(...)
    ├── _current_notebook_active_registrations(...)
    │   ├── _context_get(...)
    │   ├── _load_notebook_registry(...)
    │   │   └── …
    │   ├── _runtime_context(...)
    │   │   └── …
    │   └── _safe_str(...)
    ├── _html_escape(...)
    ├── _latest_agreement_versions(...)
    │   ├── _coerce_row_dicts(...)
    │   └── _parse_contract_version(...)
    ├── _list_data_agreements(...)
    │   ├── _latest_agreement_versions(...)
    │   │   └── …
    │   └── _list_all_data_agreement_rows(...)
    │       └── …
    ├── _register_current_notebook(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _context_get(...)
    │   ├── _current_audit_timestamp(...)
    │   │   └── …
    │   ├── _notebook_registration_key(...)
    │   ├── _rows_for_spark(...)
    │   ├── _runtime_context(...)
    │   │   └── …
    │   ├── _safe_str(...)
    │   └── write_lakehouse_table(...)
    │       └── …
    ├── _render_searchable_selector(...)
    │   ├── _html_escape(...)
    │   └── _widget_common(...)
    └── _require_ipywidgets(...)
    ```

??? info "Internal helpers used: 26"

    This callable uses 26 internal helpers for audit timestamp, metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/config.py#L66-L72"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/config.py#L58-L63"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/config.py#L23-L55"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/config.py#L472-L512"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L570-L576"><code>_parse_contract_version</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/config.py#L515-L554"><code>_get_store</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L142-L151"><code>_rows_for_spark</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L56-L61"><code>_coerce_row_dicts</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L195-L198"><code>_html_escape</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L44-L53"><code>_notebook_registration_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_select_agreement`
- Short name: `widget_select_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `788`
- Inbound references count: 0
- Outbound references count: 7
- Used in templates: 02_pipeline
- Glossary terms: notebook template

### Implementation contract

- **required_context:** Requires agreement metadata created through 01_agreement and metadata routing from 00_env_config.
- **inputs:** config, env, optional spark_session, and notebook registration options for loading agreement choices from metadata.
- **output:** Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.
- **side_effects:** Displays an IPython widget and may register the active notebook selection in metadata when requested.
- **failure_modes:** Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.
- **verification:** Verify the user selected an agreement and call get_selected_agreement before generating pipeline code that depends on agreement context.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.data_agreement._html_escape`
- `fabricops_kit.data_agreement._latest_agreement_versions`
- `fabricops_kit.data_agreement._list_data_agreements`
- `fabricops_kit.data_agreement._render_searchable_selector`
- `fabricops_kit.data_agreement._require_ipywidgets`
- `fabricops_kit.metadata._current_notebook_active_registrations`
- `fabricops_kit.metadata._register_current_notebook`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L788-L1020">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/data_agreement.py#L788-L1020</a>
- Start line: `788`
- End line: `1020`
- Signature:

```python
def widget_select_agreement(
    agreement_rows_or_config: Any,
    env_name: str | None=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    register_notebook: bool=False,
    notebook_type: str | None=None,
    environment_name: str | None=None,
    dataset_name: str | None=None,
    table_name: str | None=None,
    topic: str | None=None,
    pipeline_name: str | None=None,
) -> Any:
```

### Internal relationship graph

### Public related functions

- <a href="../get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation summary

- Internal helper count: 26
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
