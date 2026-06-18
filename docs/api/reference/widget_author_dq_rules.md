# widget_author_dq_rules

Render interactive manual DQ guardrail authoring controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2317`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L2317-L2485">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 02_pipeline after target selection when engineering needs to batch-create, edit, clear, or draft DQ guardrail rules.

### Do not use when

- Do not use for runtime DQ enforcement or catalogue profiling; use enforce_dq_rules for execution and profile helpers for observed evidence.

### Additional context

Renders manual DQ authoring controls that produce editable guardrail rule intent rows under the selected table governance policy.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_dq_rules(
    state: Mapping[str, Any],
    dq_authoring_mode: str='manual',
    rule_type: str='not_null',
    selected_columns: Iterable[str] | None=None,
    parameters: Mapping[str, Any] | None=None,
    severity: str='warning',
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    bypass_reason: str='',
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
    commit: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target`. |
| `dq_authoring_mode` | `str` | No | Manual DQ authoring mode. |
| `rule_type` | `str` | No | Initial DQ rule type for manual mode. |
| `selected_columns` | `Iterable[str] \| None` | No | Initial batch-selected columns. Defaults to all selected table columns. |
| `parameters` | `Mapping[str, Any] \| None` | No | Initial JSON rule parameters. |
| `severity` | `str` | No | Initial rule severity. |
| `spark_session` | `Any` | No | Spark session used for saves. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `bypass_reason` | `str` | No | Initial approval-bypass reason. |
| `source_notebook_type` | `str` | No | Notebook type stamped on authored records. |
| `created_by_role` | `str` | No | Role stamped on authored records. |
| `commit` | `bool` | No | Whether to save the initial generated records immediately. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns mutable preview records; approved saves write guardrail rule intent to METADATA_GUARDRAIL_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- Rule parameters are invalid for the selected DQ type.
- Rule suggestions cannot be parsed.
- Bypass reason is missing when bypass is requested.
- The metadata target cannot be written.

## Relationships

### Used by

- <a href="widget_author_guardrail_rules/"><code>fabricops_kit.governance_review.widget_author_guardrail_rules</code></a>

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._dq_records_from_selection`
- `fabricops_kit.governance_review._latest_rule`
- `fabricops_kit.governance_review._rule_params`
- `fabricops_kit.governance_review._write_rule_records`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_author_dq_rules(...)
    ├── _dq_records_from_selection(...)
    │   └── _base_guardrail_rule_record(...)
    │       └── …
    ├── _latest_rule(...)
    ├── _rule_params(...)
    ├── _write_rule_records(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
    │       └── …
    └── resolve_fabric_context(...)
        └── get_default_fabric_context(...)
    ```

??? info "Internal helpers used: 20"

    This callable uses 20 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L193-L199"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L185-L190"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L150-L182"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1885-L1902"><code>_base_guardrail_rule_record</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1964-L1975"><code>_write_rule_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L599-L639"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1955-L1961"><code>_rule_params</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L2278-L2314"><code>_dq_records_from_selection</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1939-L1952"><code>_latest_rule</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L642-L681"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_author_dq_rules`
- Short name: `widget_author_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2317`
- Inbound references count: 1
- Outbound references count: 5
- Used in templates: 02_pipeline
- Glossary terms: guardrails, evidence, metadata lakehouse, notebook template

### Implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail authoring`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="widget_author_guardrail_rules/"><code>fabricops_kit.governance_review.widget_author_guardrail_rules</code></a>

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._dq_records_from_selection`
- `fabricops_kit.governance_review._latest_rule`
- `fabricops_kit.governance_review._rule_params`
- `fabricops_kit.governance_review._write_rule_records`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L2317-L2485">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L2317-L2485</a>
- Start line: `2317`
- End line: `2485`
- Signature:

```python
def widget_author_dq_rules(
    state: Mapping[str, Any],
    dq_authoring_mode: str='manual',
    rule_type: str='not_null',
    selected_columns: Iterable[str] | None=None,
    parameters: Mapping[str, Any] | None=None,
    severity: str='warning',
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    bypass_reason: str='',
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
    commit: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 20
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>
- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
