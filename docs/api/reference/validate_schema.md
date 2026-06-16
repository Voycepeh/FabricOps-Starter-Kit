# validate_schema

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:304`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b120087e070e05954473739b25e04c14a2a99b65/src/fabricops_kit/guardrails.py#L304-L394">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use as an early guardrail when a source or target DataFrame must match a known schema contract.

**Do not use when:**

- Do not use for DQ-rule enforcement or metadata persistence.

**Additional context:**

Checks whether a DataFrame contains the expected columns and compatible types before downstream transformations or writes continue.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def validate_schema(
    dataframe,
    expected_schema: dict[str, str],
    preset: str='strict',
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
schema_result = validate_schema(df, {"order_id": "string"}, preset="allow_new_columns")
stop_if_failed(schema_result)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark, pandas, or dataframe-like object with schema metadata. |
| `expected_schema` | `dict[str, str]` | Yes | Mapping of required column names to expected datatype strings. |
| `preset` | `str` | No | Schema validation intent. ``strict`` blocks missing columns, datatype changes, and unexpected columns. ``allow_new_columns`` blocks missing columns and datatype changes while reporting additional columns as a warning. ``monitor_only`` reports all differences without blocking. |

## Returns

Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.

### Return interpretation

When can_continue is true, schema checks passed or only non-blocking issues were found. When false, fix missing or mismatched columns before writing data.

## Raises / Errors

ValueError when preset is not one of the supported schema presets.

### Common failure causes

- Required columns are missing.
- Column types differ from expected schema.
- The expected schema configuration is incomplete.
- The DataFrame supplied to the check is not the intended table.

## Relationships

### Used by

- <a href="../validate_schema_rule/"><code>fabricops_kit.guardrails.validate_schema_rule</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.guardrails._actual_schema`
- `fabricops_kit.guardrails._normalize_datatype`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Inspects DataFrame schema only; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    validate_schema(...)
    ├── _actual_schema(...)
    │   └── _normalize_datatype(...)
    └── _normalize_datatype(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for rule parsing and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b120087e070e05954473739b25e04c14a2a99b65/src/fabricops_kit/guardrails.py#L136-L182"><code>_normalize_datatype</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b120087e070e05954473739b25e04c14a2a99b65/src/fabricops_kit/guardrails.py#L185-L200"><code>_actual_schema</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.validate_schema`
- Short name: `validate_schema`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `304`
- Inbound references count: 2
- Outbound references count: 2
- Used in templates: 02_pipeline
- Glossary terms: guardrail, can_continue, source table, target table

### AI implementation contract

- **required_context:** Use in 02_pipeline before write helpers so schema guardrails run before publishing data.
- **inputs:** dataframe, expected_schema mapping, and preset controlling blocking behavior.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.
- **side_effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when preset is not one of the supported schema presets.
- **verification:** Verify can_continue before calling write helpers and pass the result to stop_if_failed when blocking behavior is required.

### Inbound references

- <a href="../validate_schema_rule/"><code>fabricops_kit.guardrails.validate_schema_rule</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.guardrails._actual_schema`
- `fabricops_kit.guardrails._normalize_datatype`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b120087e070e05954473739b25e04c14a2a99b65/src/fabricops_kit/guardrails.py#L304-L394">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b120087e070e05954473739b25e04c14a2a99b65/src/fabricops_kit/guardrails.py#L304-L394</a>
- Start line: `304`
- End line: `394`
- Signature:

```python
def validate_schema(
    dataframe,
    expected_schema: dict[str, str],
    preset: str='strict',
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 2
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
