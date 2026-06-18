# enforce_dq_rules

Enforce approved active DQ rules as a target-write guardrail without filtering rows.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1488`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1488-L1571">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in pipeline guardrails after governance-approved DQ rules exist for the dataset and table.

### Do not use when

- Do not use to filter bad rows, author new DQ rules, or bypass governance review approval.

### Additional context

Evaluates approved data-quality rules against a DataFrame and returns guardrail evidence that can block unsafe writes.


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
    run_id: str='',
    write_results: bool=False,
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
| `dataset_name` | `str` | Yes | Dataset identifier used with ``table_name`` to scope active DQ guardrail rules when those columns exist in the metadata table. |
| `table_name` | `str` | Yes | Target table name whose active DQ guardrail rules should be enforced. |
| `spark_session` | `pyspark.sql.SparkSession` | No | Spark session used to read metadata when required by the configured storage helper. |
| `run_id` | `str` | No | Pipeline run identifier written to runtime result evidence. |
| `write_results` | `bool` | No | Whether to append the aggregate DQ runtime outcome to ``METADATA_GUARDRAIL_RESULTS`` when a Spark session is available. |

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

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.governance_review._dq_failed_row_count`
- `fabricops_kit.governance_review._dq_summary`
- `fabricops_kit.governance_review._dq_tagged_dataframe`
- `fabricops_kit.governance_review._load_active_dq_rules`
- `fabricops_kit.governance_review._read_guardrail_rule_metadata`
- `fabricops_kit.governance_review._run_dq_guardrail_checks`
- `fabricops_kit.governance_review._summarize_dq_guardrail`
- `fabricops_kit.metadata._write_guardrail_result_row`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `example_dq_rule_smoke_test`

**Side effects:**

Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.

**Notes:**

This v1 guardrail reads active DQ guardrail rules from
``METADATA_GUARDRAIL_RULES`` via the configured metadata route and writes the aggregate runtime
outcome to ``METADATA_GUARDRAIL_RESULTS`` when result writing is enabled. It
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
    │   ├── _normalize_dq_severity(...)
    │   └── _spark_sql_helpers(...)
    ├── _load_active_dq_rules(...)
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _coerce_rows(...)
    │   ├── _latest_dq_rule_versions(...)
    │   │   └── …
    │   ├── _normalize_dq_severity(...)
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
    │   ├── _normalize_dq_severity(...)
    │   ├── _spark_sql_helpers(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _summarize_dq_guardrail(...)
    └── _write_guardrail_result_row(...)
        ├── _build_runtime_audit_fields(...)
        │   └── …
        ├── _configured_lakehouse_schema(...)
        │   └── …
        ├── _now_utc_iso(...)
        │   └── …
        └── write_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 25"

    This callable uses 25 internal helpers for audit timestamp, metadata loading, validation, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1188-L1209"><code>_latest_dq_rule_versions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1212-L1259"><code>_load_active_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1479-L1486"><code>_read_guardrail_rule_metadata</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1114-L1186"><code>_validate_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1347-L1350"><code>_dq_check_status</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L82-L85"><code>_normalize_dq_severity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1353-L1388"><code>_run_dq_guardrail_checks</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L78-L79"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L599-L639"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1263-L1345"><code>_dq_failed_expression</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1427-L1437"><code>_dq_failed_row_count</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1440-L1455"><code>_dq_summary</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1391-L1424"><code>_dq_tagged_dataframe</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1104-L1111"><code>_spark_sql_helpers</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1458-L1475"><code>_summarize_dq_guardrail</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/config.py#L642-L681"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.enforce_dq_rules`
- Short name: `enforce_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1488`
- Inbound references count: 1
- Outbound references count: 8
- Used in templates: example_dq_rule_smoke_test
- Glossary terms: guardrails, can_continue, evidence, metadata lakehouse

### Implementation contract

- **required_context:** Requires active approved DQ-rule evidence in the configured metadata target from 03_governance governance workflows.
- **inputs:** dataframe, config, env, dataset_name, table_name, and optional spark_session.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.
- **side_effects:** Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.
- **failure_modes:** Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.
- **verification:** Verify approved metadata exists, inspect status/can_continue, and call stop_if_failed before writing when blocking failures occur.

### Inbound references

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.governance_review._dq_failed_row_count`
- `fabricops_kit.governance_review._dq_summary`
- `fabricops_kit.governance_review._dq_tagged_dataframe`
- `fabricops_kit.governance_review._load_active_dq_rules`
- `fabricops_kit.governance_review._read_guardrail_rule_metadata`
- `fabricops_kit.governance_review._run_dq_guardrail_checks`
- `fabricops_kit.governance_review._summarize_dq_guardrail`
- `fabricops_kit.metadata._write_guardrail_result_row`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1488-L1571">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5f362a35a02a204ac95dbf339c3661a972eb1cff/src/fabricops_kit/governance_review.py#L1488-L1571</a>
- Start line: `1488`
- End line: `1571`
- Signature:

```python
def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    spark_session=None,
    run_id: str='',
    write_results: bool=False,
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>
- `fabricops_kit.guardrails.stop_if_failed`

### Internal implementation summary

- Internal helper count: 25
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>can_continue</summary>Boolean result that tells downstream notebook code whether processing can keep running.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Governance Review](../../how-fabricops-works/governance-review.md)
