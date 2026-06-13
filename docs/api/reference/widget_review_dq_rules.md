# widget_review_dq_rules

Render standalone DQ-rule review guidance for selected profile rows.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:624`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L624-L787">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance after profile rows are loaded and before record_table_governance persists approved DQ rules.

**Additional context:**

Renders data-quality rule review guidance so reviewers can approve executable expectations for a selected table.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_dq_rules(
    profile_rows: list[dict[str, Any]],
    existing_rules: list[dict[str, Any]] | None=None,
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
    table_name: str | None=None,
    business_context: str='',
) -> list[dict[str, Any]]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `profile_rows` | `list[dict[str, Any]]` | Yes | Selected catalogue profile rows containing columns and profile evidence. |
| `existing_rules` | `list[dict[str, Any]] \| None` | No | Previously persisted active and inactive DQ rule rows for the selected table. When supplied, the widget displays them in an editable review table. Runtime enforcement still reads ``METADATA_DQ_RULES`` later. |
| `config` | `Any` | No | Runtime objects used only when reviewers click AI suggestion actions. |
| `env` | `str \| None` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |
| `table_name` | `str \| None` | No | Selected table name. Defaults to the table in ``profile_rows``. |
| `business_context` | `str` | No | Optional context sent to the Fabric AI suggestion helper. |

## Returns

list[dict[str, Any]]
    Mutable review list. The widget appends approved create, update,
    deactivation, and reactivation dictionaries to this list; pass it to
    ``record_table_governance`` to persist append-only metadata history.

### Return interpretation

The widget captures proposed and approved DQ rule rows. Only approved rows should be persisted and later enforced by pipeline guardrails.

## Raises / Errors

Not documented yet

### Common failure causes

- Profile rows are missing.
- Rule parameters are incomplete or unsupported.
- The reviewer has not approved any rules.
- Widget state is reset before records are collected.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._canonical_dq_rule_type`
- `fabricops_kit.governance_review._dq_parameter_fields_for_rule_type`
- `fabricops_kit.governance_review._dq_rule_display_rows`
- `fabricops_kit.governance_review._draft_dq_rules`
- `fabricops_kit.governance_review._validate_dq_rules`
- `fabricops_kit.governance_review._value`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_review_dq_rules(...)
    ├── _canonical_dq_rule_type(...)
    ├── _dq_parameter_fields_for_rule_type(...)
    │   └── _canonical_dq_rule_type(...)
    ├── _dq_rule_display_rows(...)
    │   ├── _canonical_dq_rule_type(...)
    │   └── _dq_rule_parameters_summary(...)
    ├── _draft_dq_rules(...)
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _extract_assignment_payload(...)
    │   │   └── …
    │   ├── _prepare_dq_profile_input_rows(...)
    │   │   └── …
    │   ├── _run_fabric_ai_drafting(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _validate_dq_rules(...)
    │   └── _canonical_dq_rule_type(...)
    └── _value(...)
    ```

??? info "Internal helpers used: 16"

    This callable uses 16 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L69-L75"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L61-L66"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L27-L58"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L553-L583"><code>_dq_rule_display_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1585-L1593"><code>_draft_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1129-L1143"><code>_extract_assignment_payload</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1146-L1219"><code>_validate_dq_rules</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L78-L79"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L586-L604"><code>_dq_parameter_fields_for_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1111-L1126"><code>_parse_ai_dict_response</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L535-L550"><code>_dq_rule_parameters_summary</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1558-L1582"><code>_prepare_dq_profile_input_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1083-L1090"><code>_spark_sql_helpers</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L1093-L1098"><code>_run_fabric_ai_drafting</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_dq_rules`
- Short name: `widget_review_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `624`
- Inbound references count: 0
- Outbound references count: 6
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, guardrail, metadata lakehouse

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected catalogue profile rows containing columns and profile evidence.
existing_rules : list of dict, optional
    Previously persisted active and inactive DQ rule rows for the selected
    table. When supplied, the widget displays them in an editable review
    table. Runtime enforcement still reads ``METADATA_DQ_RULES`` later.
config, env, spark_session : optional
    Runtime objects used only when reviewers click AI suggestion actions.
table_name : str, optional
    Selected table name. Defaults to the table in ``profile_rows``.
business_context : str, default=""
    Optional context sent to the Fabric AI suggestion helper.
- **output:** list[dict[str, Any]]
    Mutable review list. The widget appends approved create, update,
    deactivation, and reactivation dictionaries to this list; pass it to
    ``record_table_governance`` to persist append-only metadata history.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._canonical_dq_rule_type`
- `fabricops_kit.governance_review._dq_parameter_fields_for_rule_type`
- `fabricops_kit.governance_review._dq_rule_display_rows`
- `fabricops_kit.governance_review._draft_dq_rules`
- `fabricops_kit.governance_review._validate_dq_rules`
- `fabricops_kit.governance_review._value`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L624-L787">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L624-L787</a>
- Start line: `624`
- End line: `787`
- Signature:

```python
def widget_review_dq_rules(
    profile_rows: list[dict[str, Any]],
    existing_rules: list[dict[str, Any]] | None=None,
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
    table_name: str | None=None,
    business_context: str='',
) -> list[dict[str, Any]]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 16
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
