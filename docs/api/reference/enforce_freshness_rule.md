# enforce_freshness_rule

Evaluate freshness using an active metadata-backed freshness guardrail rule.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:113`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L113-L131">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 02_pipeline when active freshness rules from METADATA_GUARDRAIL_RULES should determine the freshness column and maximum lag.

**Do not use when:**

- Do not use to create or review freshness rules; use the guardrail authoring and governance review widgets for lifecycle changes.

**Additional context:**

Evaluates freshness using a metadata-backed guardrail rule so active freshness intent from governance is enforced during pipeline execution.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def enforce_freshness_rule(
    dataframe,
    rules_df,
    dataset_name: str,
    table_name: str,
    environment_name: str='',
    metadata_table_key: str='',
    reference_date=None,
) -> dict:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `—` | Yes | Not documented yet |
| `rules_df` | `—` | Yes | Not documented yet |
| `dataset_name` | `str` | Yes | Not documented yet |
| `table_name` | `str` | Yes | Not documented yet |
| `environment_name` | `str` | No | Not documented yet |
| `metadata_table_key` | `str` | No | Not documented yet |
| `reference_date` | `—` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

A can_continue value of true means the latest freshness value satisfied the active rule or no blocking rule applied; false means the run should stop after display.

## Raises / Errors

Not documented yet

### Common failure causes

- The freshness column is missing.
- The max lag parameter is invalid.
- No active freshness rule matches the table.
- Metadata evidence cannot be read.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.guardrails._apply_bypass_post_review_warning`
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._parse_rule_parameters`
- `fabricops_kit.guardrails._select_table_guardrail_rule`
- `fabricops_kit.guardrails._string_value`
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>

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
    enforce_freshness_rule(...)
    ├── _apply_bypass_post_review_warning(...)
    │   └── _rule_review_status(...)
    │       ├── _catalogue_value(...)
    │       └── _string_value(...)
    ├── _catalogue_value(...)
    ├── _parse_rule_parameters(...)
    │   └── _catalogue_value(...)
    ├── _select_table_guardrail_rule(...)
    │   ├── _catalogue_value(...)
    │   ├── _is_active_guardrail_rule(...)
    │   │   ├── _catalogue_value(...)
    │   │   ├── _rule_review_status(...)
    │   │   │   ├── _catalogue_value(...)
    │   │   │   └── _string_value(...)
    │   │   └── _string_value(...)
    │   ├── _row_to_dict(...)
    │   └── _string_value(...)
    ├── _string_value(...)
    └── enforce_freshness(...)
        ├── _coerce_date(...)
        ├── _iso_date_value(...)
        │   └── _coerce_date(...)
        └── _max_column_value(...)
    ```

??? info "Internal helpers used: 8"

    This callable uses 8 internal helpers for metadata loading, rule parsing, profile comparison, rule evaluation, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Profile comparison</h4>
        <p>Compare current evidence with accepted profile values and behavior baselines.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L482-L489"><code>_row_to_dict</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.enforce_freshness_rule`
- Short name: `enforce_freshness_rule`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `113`
- Inbound references count: 1
- Outbound references count: 6
- Used in templates: 02_pipeline
- Glossary terms: guardrail, metadata lakehouse, can_continue

### Implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail enforcement`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.guardrails._apply_bypass_post_review_warning`
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._parse_rule_parameters`
- `fabricops_kit.guardrails._select_table_guardrail_rule`
- `fabricops_kit.guardrails._string_value`
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L113-L131">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/20538b666f8496652d413fb1d644dc6f198dcc61/src/fabricops_kit/guardrails.py#L113-L131</a>
- Start line: `113`
- End line: `131`
- Signature:

```python
def enforce_freshness_rule(
    dataframe,
    rules_df,
    dataset_name: str,
    table_name: str,
    environment_name: str='',
    metadata_table_key: str='',
    reference_date=None,
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 8
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
