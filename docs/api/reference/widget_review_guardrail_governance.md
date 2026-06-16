# widget_review_guardrail_governance

Render interactive controls for reviewing proposed and bypassed guardrail rules.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2430`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/governance_review.py#L2430-L2518">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance after selecting a guardrail target to perform human review of rule intent and table policy state.

**Do not use when:**

- Do not use for automatic pipeline enforcement or profile evidence generation; it is an interactive governance review widget.

**Additional context:**

Renders governance review controls for marking table policy, reviewing proposed or bypass-active guardrail rules, and applying approve, reject, or supersede actions.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_guardrail_governance(
    state: Mapping[str, Any],
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target`. |
| `config` | `Any` | No | Runtime objects used for save actions. |
| `env` | `str \| None` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns controls, current rule history, and action helpers that write to guardrail rules or governance review tables when invoked.

## Raises / Errors

Not documented yet

### Common failure causes

- No target state is selected.
- No proposed or bypassed rules are available for review.
- Unsupported governance action is selected.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._write_governance_policy_record`
- `fabricops_kit.governance_review._write_rule_records`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.mark_table_governed`
- `fabricops_kit.governance_review.mark_table_ungoverned`

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

    ```text
    widget_review_guardrail_governance(...)
    ├── _write_governance_policy_record(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   ├── _get_store(...)
    │   │   │   └── _normalize_path_config(...)
    │   │   │       └── PathConfig(...)
    │   │   └── _normalize_schema_name(...)
    │   └── write_lakehouse_table(...)
    │       ├── _get_store(...)
    │       │   └── _normalize_path_config(...)
    │       │       └── PathConfig(...)
    │       ├── _normalize_table_name(...)
    │       └── _resolve_lakehouse_table_path(...)
    │           ├── _normalize_table_name(...)
    │           └── _resolve_lakehouse_schema(...)
    │               └── _normalize_schema_name(...)
    ├── _write_rule_records(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   ├── _get_store(...)
    │   │   │   └── _normalize_path_config(...)
    │   │   │       └── PathConfig(...)
    │   │   └── _normalize_schema_name(...)
    │   └── write_lakehouse_table(...)
    │       ├── _get_store(...)
    │       │   └── _normalize_path_config(...)
    │       │       └── PathConfig(...)
    │       ├── _normalize_table_name(...)
    │       └── _resolve_lakehouse_table_path(...)
    │           ├── _normalize_table_name(...)
    │           └── _resolve_lakehouse_schema(...)
    │               └── _normalize_schema_name(...)
    ├── apply_governance_rule_action(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    ├── mark_table_governed(...)
    │   └── build_table_governance_policy_record(...)
    │       ├── _now_utc_iso(...)
    │       │   └── _current_audit_timestamp(...)
    │       │       └── _get_audit_timezone(...)
    │       │           └── _validate_audit_timezone(...)
    │       └── _resolve_action_by(...)
    │           ├── _context_get(...)
    │           └── _runtime_context(...)
    │               └── _context_get(...)
    └── mark_table_ungoverned(...)
        └── build_table_governance_policy_record(...)
            ├── _now_utc_iso(...)
            │   └── _current_audit_timestamp(...)
            │       └── _get_audit_timezone(...)
            │           └── _validate_audit_timezone(...)
            └── _resolve_action_by(...)
                ├── _context_get(...)
                └── _runtime_context(...)
                    └── _context_get(...)
    ```

??? info "Internal helpers used: 6"

    This callable uses 6 internal helpers for metadata loading, rule parsing, and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/governance_review.py#L1850-L1860"><code>_write_governance_policy_record</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/governance_review.py#L1835-L1847"><code>_write_rule_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/config.py#L661-L701"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/config.py#L704-L743"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_guardrail_governance`
- Short name: `widget_review_guardrail_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2430`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 03_governance
- Glossary terms: guardrail, metadata lakehouse, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._write_governance_policy_record`
- `fabricops_kit.governance_review._write_rule_records`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.mark_table_governed`
- `fabricops_kit.governance_review.mark_table_ungoverned`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/governance_review.py#L2430-L2518">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/governance_review.py#L2430-L2518</a>
- Start line: `2430`
- End line: `2518`
- Signature:

```python
def widget_review_guardrail_governance(
    state: Mapping[str, Any],
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 6
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
