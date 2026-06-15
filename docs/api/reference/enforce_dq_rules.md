# enforce_dq_rules

Enforce approved active DQ rules as a target-write guardrail without filtering rows.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1614`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1614-L1672">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in pipeline guardrails after governance-approved DQ rules exist for the dataset and table.

**Do not use when:**

- Do not use to filter bad rows, author new DQ rules, or bypass governance review approval.

**Additional context:**

Evaluates approved data-quality rules against a DataFrame and returns guardrail evidence that can block unsafe writes.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    spark_session=None,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
dq_result = enforce_dq_rules(df, CONFIG, env, dataset_name, table_name, spark_session=spark)
stop_if_failed(dq_result)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark DataFrame to evaluate before the target write. The full DataFrame is never filtered or split by this helper. |
| `config` | `FrameworkConfig or dict` | Yes | Runtime configuration containing the configured metadata lakehouse route from ``00_env_config``. |
| `env` | `str` | Yes | Environment name used to read ``METADATA_GUARDRAIL_RULES`` from the configured metadata target. |
| `dataset_name` | `str` | Yes | Dataset identifier used with ``table_name`` to scope approved DQ rules when those columns exist in the metadata table. |
| `table_name` | `str` | Yes | Target table name whose approved active DQ rules should be enforced. |
| `spark_session` | `pyspark.sql.SparkSession` | No | Spark session used to read metadata when required by the configured storage helper. |

## Returns

Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.

### Return interpretation

When can_continue is true, active rules passed or only non-blocking issues were found. When false, inspect failing rule details before writing the table.

## Raises / Errors

Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.

### Common failure causes

- No approved active DQ rules exist for the table.
- Rule parameters are invalid or unsupported.
- Required columns are missing from the DataFrame.
- The metadata lakehouse cannot be read.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.governance_review._dq_failed_row_count`
- `fabricops_kit.governance_review._dq_summary`
- `fabricops_kit.governance_review._dq_tagged_dataframe`
- `fabricops_kit.governance_review._load_active_dq_rules`
- `fabricops_kit.governance_review._read_guardrail_rule_metadata`
- `fabricops_kit.governance_review._run_dq_guardrail_checks`
- `fabricops_kit.governance_review._summarize_dq_guardrail`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`
- `03_governance`

**Side effects:**

Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.

**Notes:**

This v1 guardrail reads approved active DQ rules from
``METADATA_GUARDRAIL_RULES`` via the configured metadata route. It records aggregate rule outcomes only; it
does not quarantine rows, write row-level failure metadata, filter invalid
rows, send alerts, or partially write targets.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    enforce_dq_rules(...)
    ├── _dq_failed_row_count(...)
    │   ├── _dq_failed_expression(...)
    │   │   └── …
    │   └── _spark_sql_helpers(...)
    ├── _dq_summary(...)
    │   ├── _current_audit_timestamp(...)
    │   │   └── …
    │   └── _summarize_dq_guardrail(...)
    ├── _dq_tagged_dataframe(...)
    │   ├── _dq_failed_expression(...)
    │   │   └── …
    │   └── _spark_sql_helpers(...)
    ├── _load_active_dq_rules(...)
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _coerce_rows(...)
    │   ├── _latest_dq_rule_versions(...)
    │   │   └── …
    │   ├── _spark_sql_helpers(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _read_guardrail_rule_metadata(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _spark_sql_helpers(...)
    │   └── read_lakehouse_table(...)
    │       └── …
    ├── _run_dq_guardrail_checks(...)
    │   ├── _dq_check_status(...)
    │   ├── _dq_failed_expression(...)
    │   │   └── …
    │   ├── _spark_sql_helpers(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    └── _summarize_dq_guardrail(...)
    ```

??? info "Internal helpers used: 18"

    This callable uses 18 internal helpers for metadata loading, validation, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1326-L1347"><code>_latest_dq_rule_versions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1350-L1385"><code>_load_active_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1605-L1612"><code>_read_guardrail_rule_metadata</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1251-L1324"><code>_validate_dq_rules</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1473-L1476"><code>_dq_check_status</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1479-L1514"><code>_run_dq_guardrail_checks</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L81-L82"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1389-L1471"><code>_dq_failed_expression</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1553-L1563"><code>_dq_failed_row_count</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1566-L1581"><code>_dq_summary</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1517-L1550"><code>_dq_tagged_dataframe</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1188-L1195"><code>_spark_sql_helpers</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1584-L1601"><code>_summarize_dq_guardrail</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L65-L70"><code>_coerce_rows</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.enforce_dq_rules`
- Short name: `enforce_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1614`
- Inbound references count: 1
- Outbound references count: 7
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: guardrail, can_continue, catalogue evidence, metadata lakehouse

### AI implementation contract

- **required_context:** Requires active approved DQ-rule evidence in the configured metadata target from 03_governance governance workflows.
- **inputs:** dataframe, config, env, dataset_name, table_name, and optional spark_session.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.
- **side_effects:** Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.
- **failure_modes:** Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.
- **verification:** Verify approved metadata exists, inspect status/can_continue, and call stop_if_failed before writing when blocking failures occur.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.governance_review._dq_failed_row_count`
- `fabricops_kit.governance_review._dq_summary`
- `fabricops_kit.governance_review._dq_tagged_dataframe`
- `fabricops_kit.governance_review._load_active_dq_rules`
- `fabricops_kit.governance_review._read_guardrail_rule_metadata`
- `fabricops_kit.governance_review._run_dq_guardrail_checks`
- `fabricops_kit.governance_review._summarize_dq_guardrail`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1614-L1672">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1614-L1672</a>
- Start line: `1614`
- End line: `1672`
- Signature:

```python
def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    spark_session=None,
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 18
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Governance Review](../../how-fabricops-works/governance-review.md)
