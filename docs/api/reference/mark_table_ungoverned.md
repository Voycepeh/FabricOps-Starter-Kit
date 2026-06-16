# mark_table_ungoverned

Persist a governance policy row that marks a table as ungoverned.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2507`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L2507-L2509">View on GitHub</a>
</div>


## Signature

<div class="reference-api-definition" markdown="1">

```python
def mark_table_ungoverned(
    state: Mapping[str, Any],
    actor: str | None=None,
    reason: str='',
    config: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Not documented yet |
| `actor` | `str \| None` | No | Not documented yet |
| `reason` | `str` | No | Not documented yet |
| `config` | `Any` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

## Raises / Errors

Not documented yet

## Relationships

### Used by

- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Calls

- <a href="../build_table_governance_policy_record/"><code>fabricops_kit.governance_review.build_table_governance_policy_record</code></a>

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
    mark_table_ungoverned(...)
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

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `mark_table_ungoverned` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.mark_table_ungoverned`
- Short name: `mark_table_ungoverned`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2507`
- Inbound references count: 1
- Outbound references count: 1
- Used in templates: 03_governance
- Glossary terms: —

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

- <a href="../build_table_governance_policy_record/"><code>fabricops_kit.governance_review.build_table_governance_policy_record</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L2507-L2509">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L2507-L2509</a>
- Start line: `2507`
- End line: `2509`
- Signature:

```python
def mark_table_ungoverned(
    state: Mapping[str, Any],
    actor: str | None=None,
    reason: str='',
    config: Any=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## See also

No related guides documented.
