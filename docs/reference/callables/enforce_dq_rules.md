# enforce_dq_rules

Enforce approved active DQ rules as a target-write guardrail without filtering rows.

## Use this when

Use before target writes to enforce active approved DQ rules for a dataset/table as a pipeline guardrail.

## Do not use this for

Do not use to filter bad rows, author new DQ rules, or bypass governance review approval.

## Example

```python
dq_result = enforce_dq_rules(df, CONFIG, env, dataset_name, table_name, spark_session=spark)
stop_if_failed(dq_result)
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>What it means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>dataframe</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Spark DataFrame to evaluate before the target write. The full DataFrame is never filtered or split by this helper.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Runtime configuration containing the configured metadata lakehouse route from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Environment name used to read ``METADATA_DQ_RULES`` from the configured metadata target.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Dataset identifier used with ``table_name`` to scope approved DQ rules when those columns exist in the metadata table.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Target table name whose approved active DQ rules should be enforced.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="What it means">Spark session used to read metadata when required by the configured storage helper.</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def enforce_dq_rules(dataframe, config, env, dataset_name, table_name, *, spark_session=None) -> dict
```

</details>

## Output

Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.

## Raises

Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.

## Side effects

Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.

## Related functions

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_summary/"><code>fabricops_kit.governance_review._dq_summary</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__summarize_dq_guardrail/"><code>fabricops_kit.governance_review._summarize_dq_guardrail</code></a>

</details>

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Requires active approved DQ-rule evidence in the configured metadata target from 03_review governance workflows.
- **inputs:** dataframe, config, env, dataset_name, table_name, and optional spark_session.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.
- **side_effects:** Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.
- **failure_modes:** Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.
- **verification:** Verify approved metadata exists, inspect status/can_continue, and call stop_if_failed before writing when blocking failures occur.

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.governance_review.enforce_dq_rules`
- Short name: `enforce_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `886`
- Inbound references count: 0
- Outbound references count: 7

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_summary/"><code>fabricops_kit.governance_review._dq_summary</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__summarize_dq_guardrail/"><code>fabricops_kit.governance_review._summarize_dq_guardrail</code></a>

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L886-L943">View enforce_dq_rules on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    *,
    spark_session=None,
) -> dict:
    """Enforce active approved DQ rules as a simple pipeline guardrail.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame to evaluate before the target write. The full DataFrame
        is never filtered or split by this helper.
    config : FrameworkConfig or dict
        Runtime configuration containing the configured metadata lakehouse
        route from ``00_env_config``.
    env : str
        Environment name used to read ``METADATA_DQ_RULES`` from the configured
        metadata target.
    dataset_name : str
        Dataset identifier used with ``table_name`` to scope approved DQ rules
        when those columns exist in the metadata table.
    table_name : str
        Target table name whose approved active DQ rules should be enforced.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to read metadata when required by the configured
        storage helper.

    Returns
    -------
    dict
        Guardrail result with ``status``, ``can_continue``, ``checks``, and
        ``message``. The result also carries the full tagged ``dataframe`` and
        aggregate ``summary`` fields for the existing catalogue evidence path.
        Error-severity rule failures return ``status='failed'`` and
        ``can_continue=False``. Warning-severity failures return
        ``status='warning'`` and ``can_continue=True``. Passing or absent rules
        return ``status='passed'`` and ``can_continue=True``.

    Notes
    -----
    This v1 guardrail reads approved active rules from ``METADATA_DQ_RULES`` via
    the configured metadata route. It records aggregate rule outcomes only; it
    does not quarantine rows, write row-level failure metadata, filter invalid
    rows, send alerts, or partially write targets.
    """
    metadata_df = read_lakehouse_table(config, env, "metadata", DQ_RULES_TABLE, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, table_name=table_name, env_name=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = _dq_failed_row_count(dataframe, rules) if rules else 0
    result = _summarize_dq_guardrail(checks)
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    result["summary"] = _dq_summary(checks, total_count, failed_row_count)
    return result
```

</details>
