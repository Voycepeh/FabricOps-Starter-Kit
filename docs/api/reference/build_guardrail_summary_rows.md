# build_guardrail_summary_rows

Build compact one-row-per-table guardrail summary rows.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:258`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L258-L321">View on GitHub</a>
</div>


## Signature

<div class="reference-api-definition" markdown="1">

```python
def build_guardrail_summary_rows(
    result_bundle: Mapping[str, Any],
) -> list[dict[str, Any]]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `result_bundle` | `Mapping[str, Any]` | Yes | Result bundle returned by :func:`run_table_guardrails`. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

## Raises / Errors

Not documented yet

## Relationships

### Used by

- `fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle`
- <a href="../display_guardrail_results/"><code>fabricops_kit.pipeline.display_guardrail_results</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.pipeline._guardrail_reason`
- `fabricops_kit.pipeline._next_action`
- `fabricops_kit.pipeline._result_can_continue`
- `fabricops_kit.pipeline._result_status`
- `fabricops_kit.pipeline._table_keys`
- `fabricops_kit.pipeline._yes_no`

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

    ```text
    build_guardrail_summary_rows(...)
    ├── _guardrail_reason(...)
    │   ├── _dq_reason(...)
    │   │   └── _result_reason(...)
    │   ├── _freshness_reason(...)
    │   │   ├── _result_reason(...)
    │   │   └── _result_status(...)
    │   ├── _profile_behavior_reason(...)
    │   │   ├── _result_reason(...)
    │   │   └── _result_status(...)
    │   ├── _result_reason(...)
    │   ├── _result_status(...)
    │   └── _schema_reason(...)
    ├── _next_action(...)
    ├── _result_can_continue(...)
    ├── _result_status(...)
    ├── _table_keys(...)
    └── _yes_no(...)
    ```

??? info "Internal helpers used: 11"

    This callable uses 11 internal helpers for metadata loading, rule parsing, rule evaluation, result summary, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L248-L255"><code>_table_keys</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L139-L141"><code>_result_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L220-L232"><code>_dq_reason</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L158-L169"><code>_next_action</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L144-L148"><code>_result_can_continue</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L151-L155"><code>_result_reason</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L186-L190"><code>_freshness_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L235-L245"><code>_guardrail_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L193-L217"><code>_profile_behavior_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L172-L183"><code>_schema_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L134-L136"><code>_yes_no</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.build_guardrail_summary_rows`
- Short name: `build_guardrail_summary_rows`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `258`
- Inbound references count: 3
- Outbound references count: 6
- Used in templates: 02_pipeline
- Glossary terms: —

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail display`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- `fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle`
- <a href="../display_guardrail_results/"><code>fabricops_kit.pipeline.display_guardrail_results</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.pipeline._guardrail_reason`
- `fabricops_kit.pipeline._next_action`
- `fabricops_kit.pipeline._result_can_continue`
- `fabricops_kit.pipeline._result_status`
- `fabricops_kit.pipeline._table_keys`
- `fabricops_kit.pipeline._yes_no`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L258-L321">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/pipeline.py#L258-L321</a>
- Start line: `258`
- End line: `321`
- Signature:

```python
def build_guardrail_summary_rows(
    result_bundle: Mapping[str, Any],
) -> list[dict[str, Any]]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 11
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## See also

No related guides documented.
