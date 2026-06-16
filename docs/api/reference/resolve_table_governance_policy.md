# resolve_table_governance_policy

Resolve the effective table-level guardrail governance policy.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1743`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L1743-L1781">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use whenever 02_pipeline or 03_governance needs the effective governed or ungoverned state for a selected table.

**Do not use when:**

- Do not use to enforce a rule outcome or infer physical profile behavior; it only resolves policy state.

**Additional context:**

Resolves the latest active table-level governance policy so guardrail authoring can decide whether rules are self-approved, proposed, or bypass-active pending review.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def resolve_table_governance_policy(
    governance_rows: Any,
    environment_name: str='',
    dataset_name: str='',
    table_name: str='',
    metadata_table_key: str='',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `governance_rows` | `Any` | Yes | Governance review rows or a DataFrame-like object containing rows from ``METADATA_GOVERNANCE_REVIEWS``. |
| `environment_name` | `str` | No | Table identity used to filter policy rows. |
| `dataset_name` | `str` | No | Not documented yet |
| `table_name` | `str` | No | Not documented yet |
| `metadata_table_key` | `str` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The returned policy dictionary defaults to ungoverned/no-approval-required unless an active governance review row marks the table governed.

## Raises / Errors

Not documented yet

### Common failure causes

- Governance review rows are missing or stale.
- Table identity fields do not match.
- Policy values are malformed.
- The metadata lakehouse cannot be read.

## Relationships

### Used by

- <a href="../widget_select_guardrail_target/"><code>fabricops_kit.governance_review.widget_select_guardrail_target</code></a>

### Calls

- `fabricops_kit.governance_review._coerce_rows`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`
- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    resolve_table_governance_policy(...)
    └── _coerce_rows(...)
    ```

??? info "Internal helpers used: 1"

    This callable uses 1 internal helpers for other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L65-L70"><code>_coerce_rows</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.resolve_table_governance_policy`
- Short name: `resolve_table_governance_policy`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1743`
- Inbound references count: 1
- Outbound references count: 1
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: guardrail, metadata lakehouse

### AI implementation contract

- **required_context:** Starter template: `02_pipeline / 03_governance`; segment: `Guardrail governance`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="../widget_select_guardrail_target/"><code>fabricops_kit.governance_review.widget_select_guardrail_target</code></a>

### Outbound references

- `fabricops_kit.governance_review._coerce_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L1743-L1781">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L1743-L1781</a>
- Start line: `1743`
- End line: `1781`
- Signature:

```python
def resolve_table_governance_policy(
    governance_rows: Any,
    environment_name: str='',
    dataset_name: str='',
    table_name: str='',
    metadata_table_key: str='',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 1
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
