# widget_review_guardrail_governance

Render interactive controls for reviewing proposed and bypassed guardrail rules.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2788`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a44ba80ddd5b368e63951e7e195100e45e5319c2/src/fabricops_kit/governance_review.py#L2788-L2884">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance after selecting a guardrail target to perform human review of enrichment and guardrail rule intent.

**Do not use when:**

- Do not use for automatic pipeline enforcement or profile evidence generation; it is an interactive governance review widget.

**Additional context:**

Renders governance review controls for reviewing proposed or bypass-active enrichment and guardrail rules, and applying approve, reject, or supersede actions.

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
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target`. The state may include ``existing_rules`` from ``METADATA_GUARDRAIL_RULES`` and ``existing_enrichment_rules`` from ``METADATA_ENRICHMENT_RULES``. |
| `config` | `Any` | No | Runtime objects used for save actions. |
| `env` | `str \| None` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns controls, current rule history, and action helpers that write to enrichment or guardrail rule tables when invoked.

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

- `fabricops_kit.governance_review.apply_governance_enrichment_action`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.load_rule_review_history`

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

    ```text
    widget_review_guardrail_governance(...)
    ├── apply_governance_enrichment_action(...)
    │   ├── _assert_governance_review_context(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   ├── _record_identity(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    ├── apply_governance_rule_action(...)
    │   ├── _assert_governance_review_context(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   ├── _record_identity(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    └── load_rule_review_history(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `widget_review_guardrail_governance` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_guardrail_governance`
- Short name: `widget_review_guardrail_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2788`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 02_pipeline
- Glossary terms: guardrail, metadata lakehouse, notebook template

### Implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review.apply_governance_enrichment_action`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.load_rule_review_history`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a44ba80ddd5b368e63951e7e195100e45e5319c2/src/fabricops_kit/governance_review.py#L2788-L2884">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a44ba80ddd5b368e63951e7e195100e45e5319c2/src/fabricops_kit/governance_review.py#L2788-L2884</a>
- Start line: `2788`
- End line: `2884`
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

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
