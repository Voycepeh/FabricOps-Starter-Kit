# display_guardrail_results

Return summary, detailed, or debug guardrail display output for Fabric notebooks.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:368`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L368-L396">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 02_pipeline immediately after run_table_guardrails and before stop_if_failed so users see guardrail outcomes before the notebook stops.

**Do not use when:**

- Do not use to mutate guardrail results or decide active rules; it is presentation-only.

**Additional context:**

Returns summary, detailed, or debug guardrail display output so Fabric notebooks show readable tables by default while preserving raw result bundles for developers.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def display_guardrail_results(
    result_bundle: Mapping[str, Any],
    mode: str='summary',
    spark_session: Any | None=None,
) -> Any:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `result_bundle` | `Mapping[str, Any]` | Yes | Result bundle returned by :func:`run_table_guardrails`. |
| `mode` | `str` | No | Display mode for notebook output. ``summary`` is compact, ``detailed`` is per-guardrail diagnostics, and ``debug`` returns raw nested results. |
| `spark_session` | `Any \| None` | No | Spark session used to convert summary or detailed rows to a display-friendly DataFrame. When omitted, a list of dictionaries is returned. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

Summary and detailed modes return display-friendly rows or Spark DataFrames; debug mode returns the raw nested guardrail summary or bundle.

## Raises / Errors

Not documented yet

### Common failure causes

- Mode is not summary, detailed, or debug.
- The Spark session cannot create a DataFrame from display rows.
- The result bundle is malformed.
- The caller expects debug internals while using summary mode.

## Relationships

### Used by

Not documented yet

### Calls

Not documented yet

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
    display_guardrail_results(...)
    ├── _rows_for_display(...)
    ├── build_guardrail_detail_rows(...)
    │   ├── _guardrail_reason(...)
    │   │   ├── _dq_reason(...)
    │   │   │   └── _result_reason(...)
    │   │   ├── _freshness_reason(...)
    │   │   │   ├── _result_reason(...)
    │   │   │   └── _result_status(...)
    │   │   ├── _profile_behavior_reason(...)
    │   │   │   ├── _result_reason(...)
    │   │   │   └── _result_status(...)
    │   │   ├── _result_reason(...)
    │   │   ├── _result_status(...)
    │   │   └── _schema_reason(...)
    │   ├── _next_action(...)
    │   ├── _result_can_continue(...)
    │   ├── _result_status(...)
    │   ├── _table_keys(...)
    │   └── _yes_no(...)
    └── build_guardrail_summary_rows(...)
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

??? info "Internal helpers used: 1"

    This callable uses 1 internal helpers for fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L361-L365"><code>_rows_for_display</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.display_guardrail_results`
- Short name: `display_guardrail_results`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `368`
- Inbound references count: 0
- Outbound references count: 0
- Used in templates: 02_pipeline
- Glossary terms: guardrail, notebook template

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail display`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L368-L396">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L368-L396</a>
- Start line: `368`
- End line: `396`
- Signature:

```python
def display_guardrail_results(
    result_bundle: Mapping[str, Any],
    mode: str='summary',
    spark_session: Any | None=None,
) -> Any:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 1
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
