# validate_schema_rule

Validate a DataFrame schema using an active metadata-backed schema guardrail rule.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:88`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L88-L101">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 02_pipeline when active schema guardrail rules from METADATA_GUARDRAIL_RULES should drive schema validation for a selected table.

**Do not use when:**

- Do not use to author or approve schema rules; use the guardrail authoring and governance widgets for rule intent and review workflows.

**Additional context:**

Validates a DataFrame schema using a metadata-backed schema guardrail rule so runtime enforcement follows governed rule intent instead of ad hoc notebook configuration.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def validate_schema_rule(
    dataframe,
    rules_df,
    dataset_name: str,
    table_name: str,
    environment_name: str='',
    metadata_table_key: str='',
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

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The returned schema result indicates whether the DataFrame may continue and includes metadata from the matched active rule when one is enforced.

## Raises / Errors

Not documented yet

### Common failure causes

- No active schema rule matches the table identity.
- The DataFrame is missing required columns.
- Rule parameters are malformed.
- Metadata table routing is unavailable.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.guardrails._apply_bypass_post_review_warning`
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._parse_rule_parameters`
- `fabricops_kit.guardrails._select_table_guardrail_rule`
- `fabricops_kit.guardrails._string_value`
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>

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
    validate_schema_rule(...)
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
    │   │   └── _rule_review_status(...)
    │   │       ├── _catalogue_value(...)
    │   │       └── _string_value(...)
    │   ├── _row_to_dict(...)
    │   └── _string_value(...)
    ├── _string_value(...)
    └── validate_schema(...)
        ├── _actual_schema(...)
        │   └── _normalize_datatype(...)
        └── _normalize_datatype(...)
    ```

??? info "Internal helpers used: 8"

    This callable uses 8 internal helpers for metadata loading, rule parsing, profile comparison, rule evaluation, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L50-L75"><code>_select_table_guardrail_rule</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L42-L47"><code>_parse_rule_parameters</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Profile comparison</h4>
        <p>Compare current evidence with accepted profile values and behavior baselines.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L659-L670"><code>_catalogue_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L468-L475"><code>_row_to_dict</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L673-L674"><code>_string_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L36-L39"><code>_is_active_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L78-L85"><code>_apply_bypass_post_review_warning</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.validate_schema_rule`
- Short name: `validate_schema_rule`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `88`
- Inbound references count: 1
- Outbound references count: 6
- Used in templates: 02_pipeline
- Glossary terms: guardrail, metadata lakehouse, source table, target table

### AI implementation contract

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
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L88-L101">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/guardrails.py#L88-L101</a>
- Start line: `88`
- End line: `101`
- Signature:

```python
def validate_schema_rule(
    dataframe,
    rules_df,
    dataset_name: str,
    table_name: str,
    environment_name: str='',
    metadata_table_key: str='',
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
- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
