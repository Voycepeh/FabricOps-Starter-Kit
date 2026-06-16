# widget_author_dq_rules

Render interactive manual or AI-assisted DQ guardrail authoring controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2189`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L2189-L2387">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 02_pipeline after target selection when engineering needs to batch-create, edit, clear, or draft DQ guardrail rules.

**Do not use when:**

- Do not use for runtime DQ enforcement or catalogue profiling; use enforce_dq_rules for execution and profile helpers for observed evidence.

**Additional context:**

Renders manual and AI-assisted DQ authoring controls that produce editable guardrail rule intent rows under the selected table governance policy.

</details>

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
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
    bypass_reason: str='',
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
| `dq_authoring_mode` | `str` | No | Authoring mode selected before the notebook cell runs. |
| `rule_type` | `str` | No | Initial DQ rule type for manual mode. |
| `selected_columns` | `Iterable[str] \| None` | No | Initial batch-selected columns. Defaults to all selected table columns. |
| `parameters` | `Mapping[str, Any] \| None` | No | Initial JSON rule parameters. |
| `severity` | `str` | No | Initial rule severity. |
| `config` | `Any` | No | Runtime objects used for AI suggestions and saves. |
| `env` | `str \| None` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |
| `bypass_reason` | `str` | No | Initial approval-bypass reason. |
| `commit` | `bool` | No | Whether to save the initial generated records immediately. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns mutable preview records and AI draft suggestions; approved saves write guardrail rule intent to METADATA_GUARDRAIL_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- Rule parameters are invalid for the selected DQ type.
- AI suggestions cannot be parsed.
- Bypass reason is missing when bypass is requested.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._dq_records_from_selection`
- `fabricops_kit.governance_review._draft_dq_rules`
- `fabricops_kit.governance_review._latest_rule`
- `fabricops_kit.governance_review._rule_params`
- `fabricops_kit.governance_review._write_rule_records`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

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
    ├── _draft_dq_rules(...)
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _extract_assignment_payload(...)
    │   │   └── …
    │   ├── _prepare_dq_profile_input_rows(...)
    │   │   └── …
    │   ├── _run_fabric_ai_drafting(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _latest_rule(...)
    ├── _rule_params(...)
    └── _write_rule_records(...)
        ├── _configured_lakehouse_schema(...)
        │   └── …
        └── write_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 30"

    This callable uses 30 internal helpers for audit timestamp, metadata loading, validation, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L66-L72"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L58-L63"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L23-L55"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1800-L1809"><code>_base_guardrail_rule_record</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1592-L1600"><code>_draft_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1097-L1111"><code>_extract_assignment_payload</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1114-L1186"><code>_validate_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1872-L1884"><code>_write_rule_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L84-L87"><code>_normalize_dq_severity</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L80-L81"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L651-L691"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1079-L1094"><code>_parse_ai_dict_response</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1863-L1869"><code>_rule_params</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L2156-L2186"><code>_dq_records_from_selection</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1847-L1860"><code>_latest_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1565-L1589"><code>_prepare_dq_profile_input_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1061-L1068"><code>_spark_sql_helpers</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L694-L733"><code>_get_store</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L1071-L1076"><code>_run_fabric_ai_drafting</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L64-L69"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_author_dq_rules`
- Short name: `widget_author_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2189`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 02_pipeline
- Glossary terms: guardrail, catalogue evidence, metadata lakehouse, notebook template

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail authoring`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._dq_records_from_selection`
- `fabricops_kit.governance_review._draft_dq_rules`
- `fabricops_kit.governance_review._latest_rule`
- `fabricops_kit.governance_review._rule_params`
- `fabricops_kit.governance_review._write_rule_records`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L2189-L2387">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L2189-L2387</a>
- Start line: `2189`
- End line: `2387`
- Signature:

```python
def widget_author_dq_rules(
    state: Mapping[str, Any],
    dq_authoring_mode: str='manual',
    rule_type: str='not_null',
    selected_columns: Iterable[str] | None=None,
    parameters: Mapping[str, Any] | None=None,
    severity: str='warning',
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
    bypass_reason: str='',
    commit: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 30
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
