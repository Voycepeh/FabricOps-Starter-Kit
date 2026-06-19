# display_guardrail_results

Return summary, detailed, or debug guardrail display output for Fabric notebooks.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:506`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L506-L534">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 02_pipeline immediately after run_table_guardrails and before stop_if_failed so users see guardrail outcomes before the notebook stops.

### Do not use when

- Do not use to mutate guardrail results or decide active rules; it is presentation-only.

### Additional context

Returns summary, detailed, or debug guardrail display output so Fabric notebooks show readable tables by default while preserving raw result bundles for developers.


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

- `fabricops_kit.pipeline._rows_for_display`
- `fabricops_kit.pipeline.build_guardrail_detail_rows`
- `fabricops_kit.pipeline.build_guardrail_summary_rows`

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

??? info "Internal helpers used: 12"

    This callable uses 12 internal helpers for metadata loading, rule parsing, rule evaluation, result summary, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L368-L375"><code>_table_keys</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L259-L261"><code>_result_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L340-L352"><code>_dq_reason</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L278-L289"><code>_next_action</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L264-L268"><code>_result_can_continue</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L271-L275"><code>_result_reason</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L499-L503"><code>_rows_for_display</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L306-L310"><code>_freshness_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L355-L365"><code>_guardrail_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L313-L337"><code>_profile_behavior_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L292-L303"><code>_schema_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L254-L256"><code>_yes_no</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.display_guardrail_results`
- Short name: `display_guardrail_results`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `506`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 02_pipeline
- Glossary terms: guardrails, notebook template

### Implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail display`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.pipeline._rows_for_display`
- `fabricops_kit.pipeline.build_guardrail_detail_rows`
- `fabricops_kit.pipeline.build_guardrail_summary_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L506-L534">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L506-L534</a>
- Start line: `506`
- End line: `534`
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

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 12
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
