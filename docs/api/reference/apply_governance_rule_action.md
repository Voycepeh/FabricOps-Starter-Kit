# apply_governance_rule_action

Apply approve, reject, or supersede actions to a guardrail rule record.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1812`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L1812-L1844">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when a governance reviewer needs to approve, reject, or otherwise record an explicit action against a governance rule/review item.

**Do not use when:**

- Do not use for automatic DQ enforcement during pipeline execution, and do not use it to infer table profile state. Use the DQ enforcement and profile selector helpers for those workflows.

**Additional context:**

Apply a governance review action to a pending governance rule or review record, preserving the decision metadata needed for governed promotion and downstream enforcement.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def apply_governance_rule_action(
    rule: Mapping[str, Any],
    action: str,
    actor: str | None=None,
    superseded_by_rule_key: str='',
    config: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `rule` | `Mapping[str, Any]` | Yes | Existing rule row. |
| `action` | `str` | Yes | One of ``approve``, ``reject``, or ``supersede``. |
| `actor` | `str \| None` | No | Reviewer identity. |
| `superseded_by_rule_key` | `str` | No | Replacement rule key for supersede actions. |
| `config` | `Any` | No | Runtime configuration used for timestamps. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The returned rule record contains updated lifecycle fields such as review_status, is_active, approved_by, approved_at, or superseded_by_rule_key for persistence.

## Raises / Errors

Not documented yet

### Common failure causes

- The referenced rule or review record does not exist.
- The action value is not one of the supported governance actions.
- Required reviewer or decision metadata is missing.
- Metadata tables have not been initialized by 00_env_config.

## Relationships

### Used by

- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Calls

- `fabricops_kit.metadata._now_utc_iso`
- `fabricops_kit.metadata._resolve_action_by`

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
    apply_governance_rule_action(...)
    ├── _now_utc_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── _get_audit_timezone(...)
    │           └── _validate_audit_timezone(...)
    └── _resolve_action_by(...)
        ├── _context_get(...)
        └── _runtime_context(...)
            └── _context_get(...)
    ```

??? info "Internal helpers used: 7"

    This callable uses 7 internal helpers for audit timestamp and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/config.py#L70-L76"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/config.py#L62-L67"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/config.py#L27-L59"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.apply_governance_rule_action`
- Short name: `apply_governance_rule_action`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1812`
- Inbound references count: 1
- Outbound references count: 2
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

- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Outbound references

- `fabricops_kit.metadata._now_utc_iso`
- `fabricops_kit.metadata._resolve_action_by`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L1812-L1844">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L1812-L1844</a>
- Start line: `1812`
- End line: `1844`
- Signature:

```python
def apply_governance_rule_action(
    rule: Mapping[str, Any],
    action: str,
    actor: str | None=None,
    superseded_by_rule_key: str='',
    config: Any=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 7
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
