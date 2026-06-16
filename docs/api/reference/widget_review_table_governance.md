# widget_review_table_governance

Render the 03-only formal table governance review widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2649`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2649-L2762">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance after selecting a profiled table and optionally authoring enrichment or guardrail records.

**Do not use when:**

- Do not use from 02_pipeline or for runtime enforcement results; runtime outcomes belong in METADATA_GUARDRAIL_RESULTS.

**Additional context:**

Reviews enrichment and guardrail records for a selected table and appends approve, approve-and-activate, reject, replace, deactivate, and history decisions to the rule history tables.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_table_governance(
    state: Mapping[str, Any],
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
    source_notebook_type: str='03_governance',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target` with existing enrichment and guardrail rows for the selected table. |
| `config` | `Any` | No | Runtime configuration used for review writes. |
| `env` | `str \| None` | No | Environment key used to route metadata writes. |
| `spark_session` | `Any` | No | Spark session used to append review action rows. |
| `source_notebook_type` | `str` | No | Notebook context. Formal action callbacks are guarded and only write when this value is ``03_governance``. |

## Returns

Widget state with grouped review sections, controls, buttons, and action helpers.

### Return interpretation

Needs-review, active, inactive/rejected, and superseded sections show append-only governance history; action helpers append new lifecycle rows.

## Raises / Errors

Not documented yet

### Common failure causes

- The helper is called outside 03_governance.
- No reviewable records are selected.
- The metadata target cannot be written.

## Relationships

### Used by

- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Calls

- `fabricops_kit.governance_review._assert_governance_review_context`
- `fabricops_kit.governance_review._governance_review_sections`
- `fabricops_kit.governance_review.apply_governance_enrichment_action`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.load_rule_review_history`

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
    widget_review_table_governance(...)
    ├── _assert_governance_review_context(...)
    ├── _governance_review_sections(...)
    ├── apply_governance_enrichment_action(...)
    │   ├── _activation_fields(...)
    │   │   ├── _now_utc_iso(...)
    │   │   │   └── _current_audit_timestamp(...)
    │   │   │       └── _get_audit_timezone(...)
    │   │   │           └── _validate_audit_timezone(...)
    │   │   └── _resolve_action_by(...)
    │   │       ├── _context_get(...)
    │   │       └── _runtime_context(...)
    │   │           └── _context_get(...)
    │   ├── _assert_governance_review_context(...)
    │   ├── _build_dq_rule_key(...)
    │   │   └── _stable_metadata_key(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   ├── _record_id(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    ├── apply_governance_rule_action(...)
    │   ├── _activation_fields(...)
    │   │   ├── _now_utc_iso(...)
    │   │   │   └── _current_audit_timestamp(...)
    │   │   │       └── _get_audit_timezone(...)
    │   │   │           └── _validate_audit_timezone(...)
    │   │   └── _resolve_action_by(...)
    │   │       ├── _context_get(...)
    │   │       └── _runtime_context(...)
    │   │           └── _context_get(...)
    │   ├── _assert_governance_review_context(...)
    │   ├── _build_dq_rule_key(...)
    │   │   └── _stable_metadata_key(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   ├── _record_id(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    └── load_rule_review_history(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L68-L84"><code>_assert_governance_review_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2631-L2646"><code>_governance_review_sections</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_table_governance`
- Short name: `widget_review_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2649`
- Inbound references count: 1
- Outbound references count: 5
- Used in templates: 03_governance
- Glossary terms: guardrail, metadata lakehouse, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Formal governance review`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and context parameters accepted by this helper.
- **output:** Widget state with grouped review sections, controls, buttons, and action helpers.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Outbound references

- `fabricops_kit.governance_review._assert_governance_review_context`
- `fabricops_kit.governance_review._governance_review_sections`
- `fabricops_kit.governance_review.apply_governance_enrichment_action`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.load_rule_review_history`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2649-L2762">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2649-L2762</a>
- Start line: `2649`
- End line: `2762`
- Signature:

```python
def widget_review_table_governance(
    state: Mapping[str, Any],
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
    source_notebook_type: str='03_governance',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../widget_enrich_table_metadata/"><code>fabricops_kit.governance_review.widget_enrich_table_metadata</code></a>
- <a href="../widget_author_guardrail_rules/"><code>fabricops_kit.governance_review.widget_author_guardrail_rules</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
