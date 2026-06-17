# enforce_freshness

Enforce whether the latest data arrived within the configured freshness lag.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:572`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/guardrails.py#L572-L670">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use as a pipeline guardrail when stale source or target data should block or warn before downstream work proceeds.

**Do not use when:**

- Do not use for schema validation, load-behavior enforcement, or DQ-rule enforcement; use enforce_profile_behavior or enforce_dq_rules for those checks.

**Additional context:**

Checks whether the latest value in a freshness column is recent enough for the configured maximum lag before pipeline writes continue.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def enforce_freshness(
    dataframe,
    freshness_column: str | None,
    max_lag_days: int | str | None,
    severity: str='blocking',
    reference_date: date | datetime | str | None=None,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
freshness_result = enforce_freshness(df, "business_date", 1, severity="blocking")
stop_if_failed(freshness_result)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark DataFrame or iterable of row-like mappings to check. |
| `freshness_column` | `str \| None` | Yes | Column whose maximum value represents the latest available data date. When omitted, the freshness guardrail is skipped. |
| `max_lag_days` | `int \| str \| None` | Yes | Maximum allowed lag, in days, between ``reference_date`` and the latest value in ``freshness_column``. Required when ``freshness_column`` is set. |
| `severity` | `str` | No | Whether stale data blocks continuation or returns a non-blocking warning. |
| `reference_date` | `date \| datetime \| str \| None` | No | Date used as "today" for comparison. Defaults to the current local date. |

## Returns

Guardrail result dictionary with status, can_continue, latest_value, required_min_value, and freshness evidence fields.

### Return interpretation

If can_continue is true, the latest freshness value is within the allowed lag or the check was skipped. If false, investigate stale data before writing outputs.

## Raises / Errors

ValueError when severity is unsupported, lag is missing for a configured column, lag is negative, or reference_date is invalid.

### Common failure causes

- The freshness column is missing.
- The max lag value is missing or invalid.
- The latest date is older than the allowed lag.
- Severity is invalid or configured as blocking for stale data.

## Relationships

### Used by

- <a href="../enforce_freshness_rule/"><code>fabricops_kit.guardrails.enforce_freshness_rule</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.guardrails._coerce_date`
- `fabricops_kit.guardrails._iso_date_value`
- `fabricops_kit.guardrails._max_column_value`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Computes max(freshness_column) on the provided DataFrame; it does not write metadata, tables, or files.

**Notes:**

Freshness is separate from profile behavior. ``profile_mode="skip"`` only
skips profile behavior enforcement; freshness still runs when configured.

</details>

??? info "Call flow"

    ```text
    enforce_freshness(...)
    ├── _coerce_date(...)
    ├── _iso_date_value(...)
    │   └── _coerce_date(...)
    └── _max_column_value(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/guardrails.py#L547-L564"><code>_coerce_date</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/guardrails.py#L567-L569"><code>_iso_date_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/guardrails.py#L514-L544"><code>_max_column_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.enforce_freshness`
- Short name: `enforce_freshness`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `572`
- Inbound references count: 2
- Outbound references count: 3
- Used in templates: 02_pipeline
- Glossary terms: guardrail, can_continue, source table, target table

### Implementation contract

- **required_context:** Use in 02_pipeline after schema validation and before downstream writes so stale data can block or warn independently from profile behavior.
- **inputs:** dataframe, freshness_column, max_lag_days, severity, and optional reference_date for deterministic validation.
- **output:** Guardrail result dictionary with status, can_continue, latest_value, required_min_value, and freshness evidence fields.
- **side_effects:** Computes max(freshness_column) on the provided DataFrame; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when severity is unsupported, lag is missing for a configured column, lag is negative, or reference_date is invalid.
- **verification:** Verify freshness_column and freshness_max_lag_days come from the table config and that blocking severity stops writes when can_continue is false.

### Inbound references

- <a href="../enforce_freshness_rule/"><code>fabricops_kit.guardrails.enforce_freshness_rule</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.guardrails._coerce_date`
- `fabricops_kit.guardrails._iso_date_value`
- `fabricops_kit.guardrails._max_column_value`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/guardrails.py#L572-L670">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/201e4083d549c46a68c370ebf6568bffe8af7d6c/src/fabricops_kit/guardrails.py#L572-L670</a>
- Start line: `572`
- End line: `670`
- Signature:

```python
def enforce_freshness(
    dataframe,
    freshness_column: str | None,
    max_lag_days: int | str | None,
    severity: str='blocking',
    reference_date: date | datetime | str | None=None,
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
