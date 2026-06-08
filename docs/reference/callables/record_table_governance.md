# record_table_governance

Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.

## What this is for and when to use it

Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.

- Use in 03_review after human approval to persist approved column context, DQ rules, and classification evidence for a profiled table.

## When not to use it

- Do not use to draft governance recommendations, bypass review approval, or write unapproved rows.

## Example

```python
written = record_table_governance(CONFIG, env, profile_rows, spark_session=spark, context_reviews=context_rows, dq_rule_reviews=dq_rows, classification_reviews=classification_rows, approved_by="reviewer")
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Shared ``00_env_config`` configuration that routes metadata writes to the configured metadata lakehouse target.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key in ``config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>profile_rows</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Column-profile rows loaded for the selected catalogue table.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used to create DataFrames for metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>context_reviews</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Human-approved rows from the governance review workflow. Only rows with ``review_status=&quot;approved&quot;`` and ``commit=True`` are written.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dq_rule_reviews</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>classification_reviews</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>approved_by</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Reviewer identity to stamp on records. When omitted, runtime defaults are used.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Write mode for metadata table commits.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of records written for column_context, dq_rules, and column_classification.

## Errors and side effects

**Errors:** Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.

**Side effects:** Writes approved governance metadata records to configured metadata tables.

## Related functions

- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/governance_review.py#L511-L591">View record_table_governance on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    *,
    spark_session: Any,
    context_reviews: list[dict[str, Any]] | None = None,
    dq_rule_reviews: list[dict[str, Any]] | None = None,
    classification_reviews: list[dict[str, Any]] | None = None,
    approved_by: str | None = None,
    mode: str = "append",
) -> dict[str, list[dict[str, Any]]]:
    """Persist approved table-governance review evidence.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration that routes metadata writes to
        the configured metadata lakehouse target.
    env : str
        Environment key in ``config``.
    profile_rows : list of dict
        Column-profile rows loaded for the selected catalogue table.
    spark_session : pyspark.sql.SparkSession
        Spark session used to create DataFrames for metadata writes.
    context_reviews, dq_rule_reviews, classification_reviews : list of dict, optional
        Human-approved rows from the governance review workflow. Only rows with
        ``review_status="approved"`` and ``commit=True`` are written.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        Records written for ``column_context``, ``dq_rules``, and
        ``column_classification``.

    Notes
    -----
    This is the v1 governance commit action for ``03_review`` notebooks. It merges
    the previous row-builder and per-table commit helpers into one explicit
    human approval step while preserving configured metadata lakehouse routing.
    """
    context_records = _build_column_context_records(
        profile_rows,
        context_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    dq_rule_records = _build_dq_rule_records(
        profile_rows,
        dq_rule_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    classification_records = _build_classification_records(
        profile_rows,
        classification_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    writes = {
        COLUMN_CONTEXT_TABLE: context_records,
        DQ_RULES_TABLE: dq_rule_records,
        COLUMN_CLASSIFICATION_TABLE: classification_records,
    }
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table(spark_session.createDataFrame(records), config, env, "metadata", table_name, mode=mode)

    return {
        "column_context": context_records,
        "dq_rules": dq_rule_records,
        "column_classification": classification_records,
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.record_table_governance`
- Short name: `record_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `511`
- Inbound references count: 0
- Outbound references count: 4

### AI implementation contract

- **required_context:** Requires 03_review profile rows and 00_env_config metadata routing; governance metadata must be written to the configured metadata target.
- **inputs:** config, env, profile_rows, spark_session, optional approved context/DQ/classification review rows, approved_by, and mode.
- **output:** Dictionary of records written for column_context, dq_rules, and column_classification.
- **side_effects:** Writes approved governance metadata records to configured metadata tables.
- **failure_modes:** Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.
- **verification:** Verify review_status is approved and commit is true for intended rows before calling; confirm returned record groups match expected approvals.

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/governance_review.py#L511-L591">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/governance_review.py#L511-L591</a>
- Start line: `511`
- End line: `591`
- Signature:

```python
def record_table_governance(config: Any, env: str, profile_rows: list[dict[str, Any]], *, spark_session: Any, context_reviews: list[dict[str, Any]] | None=None, dq_rule_reviews: list[dict[str, Any]] | None=None, classification_reviews: list[dict[str, Any]] | None=None, approved_by: str | None=None, mode: str='append') -> dict[str, list[dict[str, Any]]]
```

### Internal relationship graph

### Public related functions

- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation helpers

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

</details>
