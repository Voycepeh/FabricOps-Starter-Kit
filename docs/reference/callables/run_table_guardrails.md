# run_table_guardrails

Run profiling, schema, stability, DQ, and catalogue guardrails for table configs.

## What this is for and when to use it

Run profiling, schema, stability, DQ, and catalogue guardrails for table configs.

- Use in 02_pipeline to run source guardrails before transformation and target guardrails before writes while keeping per-table results separated.

## When not to use it

- Do not use as a replacement for individual helper calls when debugging one specific guardrail interactively.

## Example

```python
source_guardrail_results = run_table_guardrails(SOURCE_TABLES, config=CONFIG, env=ENV_NAME, run_id=RUN_ID, spark_session=spark)
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
      <td data-label="Parameter"><code>table_configs</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target table configs. Each config must contain ``key``, ``df``, and ``expected_schema``. Optional keys such as ``dataset_name``, ``stage``, ``schema_preset``, ``data_behavior``, ``stability_check_type``, ``watermark_column``, ``watermark_value``, ``dq_preset``, ``distribution_columns``, and ``exclude_columns`` control the guardrail behavior.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">FabricOps framework configuration from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key used for configured metadata routing.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Current pipeline run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used by stability and DQ helpers.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>agreement_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Governance context written with catalogue evidence.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>agreement_contract_version</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>notebook_registry_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>notebook_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Guardrail result bundle with profiles, schema results, stability results, DQ results, catalogue status, evidence definitions, can_continue, and failed_tables.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.

## Related functions

- <a href="../guardrail_summary/"><code>fabricops_kit.pipeline.guardrail_summary</code></a>
- <a href="../stop_if_any_guardrail_failed/"><code>fabricops_kit.pipeline.stop_if_any_guardrail_failed</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../internal/pipeline__guardrail_can_continue/"><code>fabricops_kit.pipeline._guardrail_can_continue</code></a>
- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>
- <a href="../build_guardrail_evidence_definitions/"><code>fabricops_kit.pipeline.build_guardrail_evidence_definitions</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L156-L307">View run_table_guardrails on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    spark_session: Any,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
) -> dict[str, Any]:
    """Run profiling, schema, stability, DQ, and catalogue guardrails.

    Parameters
    ----------
    table_configs : list of dict
        Source or target table configs. Each config must contain ``key``,
        ``df``, and ``expected_schema``. Optional keys such as
        ``dataset_name``, ``stage``, ``schema_preset``, ``data_behavior``,
        ``stability_check_type``, ``watermark_column``, ``watermark_value``,
        ``dq_preset``, ``distribution_columns``, and ``exclude_columns``
        control the guardrail behavior.
    config : Any
        FabricOps framework configuration from ``00_env_config``.
    env : str
        Environment key used for configured metadata routing.
    run_id : str
        Current pipeline run identifier.
    spark_session : Any
        Spark session used by stability and DQ helpers.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context written with catalogue evidence.

    Returns
    -------
    dict[str, Any]
        Guardrail result bundle containing profiles, schema results, stability
        results, DQ results, catalogue status, evidence definitions,
        ``can_continue``, and ``failed_tables``. Results remain separated by
        table key and guardrail type.

    Notes
    -----
    This helper intentionally collects all per-table schema, stability, and DQ
    results before reporting blocking failures. DQ results that return an
    annotated DataFrame update the corresponding table config ``df`` in place
    so downstream writes use the checked DataFrame. Metadata reads and writes
    are routed through the configured metadata target by the called helpers.
    """
    profiles: dict[str, Any] = {}
    schema_results: dict[str, Mapping[str, Any]] = {}
    stability_results: dict[str, Mapping[str, Any]] = {}
    dq_results: dict[str, Mapping[str, Any]] = {}
    failed_tables: list[str] = []
    evidence_definitions = build_guardrail_evidence_definitions(table_configs)

    for table_config in table_configs:
        table_key = _table_key(table_config)
        table_name = _table_name(table_config)
        dataset_name = table_config.get("dataset_name", table_name)
        stage = table_config.get("stage", "target")
        dataframe = table_config["df"]

        profiles[table_key] = profile_dataframe(
            dataframe,
            table_name=table_name,
            # profile_dataframe automatically excludes FabricOps/DQ technical annotation columns
            # and unions those defaults with any table-specific exclude_columns.
            exclude_columns=table_config.get("exclude_columns"),
            include_distributions=True,
            distribution_columns=table_config.get("distribution_columns"),
        )

        schema_results[table_key] = validate_schema(
            dataframe,
            table_config["expected_schema"],
            preset=table_config.get("schema_preset", "strict"),
        )

        stability_results[table_key] = enforce_catalogue_stability(
            spark_session,
            dataframe,
            CATALOGUE_TABLE,
            dataset_name,
            table_name,
            stage=stage,
            run_id=run_id,
            data_behavior=table_config.get("data_behavior", "changing"),
            stability_check_type=table_config.get("stability_check_type", "watermark_slice_hash"),
            watermark_column=table_config.get("watermark_column"),
            watermark_value=table_config.get("watermark_value"),
            exclude_columns=table_config.get("exclude_columns"),
            exclude_run_id=run_id,
            config=config,
            env=env,
        )

        if table_config.get("dq_preset", "approved_rules") == "skip":
            dq_results[table_key] = {
                "status": "skipped",
                "can_continue": True,
                "checks": [],
                "message": "DQ guardrail skipped by preset.",
            }
        else:
            dq_results[table_key] = enforce_dq_rules(
                dataframe,
                config,
                env,
                dataset_name,
                table_name,
                spark_session=spark_session,
            )

        if "dataframe" in dq_results[table_key]:
            table_config["df"] = dq_results[table_key]["dataframe"]

        table_can_continue = all(
            _guardrail_can_continue(result)
            for result in (schema_results[table_key], stability_results[table_key], dq_results[table_key])
        )
        if not table_can_continue:
            failed_tables.append(table_key)

    catalogue_status = write_catalogue_evidence(
        profiles,
        evidence_definitions,
        config=config,
        env=env,
        run_id=run_id,
        agreement_id=agreement_id,
        agreement_contract_version=agreement_contract_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        pipeline_name=pipeline_name,
        schema_results=schema_results,
        stability_results=stability_results,
        dq_results=dq_results,
    )

    return {
        "profiles": profiles,
        "schema_results": schema_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "evidence_definitions": evidence_definitions,
        "can_continue": not failed_tables,
        "failed_tables": failed_tables,
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_table_guardrails`
- Short name: `run_table_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `156`
- Inbound references count: 0
- Outbound references count: 9

### AI implementation contract

- **required_context:** Requires CONFIG and env from 00_env_config so metadata operations use the configured metadata target.
- **inputs:** table_configs plus config, env, run_id, spark_session, and agreement/notebook context.
- **output:** Guardrail result bundle with profiles, schema results, stability results, DQ results, catalogue status, evidence definitions, can_continue, and failed_tables.
- **side_effects:** Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.
- **failure_modes:** Not documented yet
- **verification:** Verify stop_if_any_guardrail_failed is called after displaying or inspecting results and before transformation or writes continue.

### Inbound references

Not documented yet

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../internal/pipeline__guardrail_can_continue/"><code>fabricops_kit.pipeline._guardrail_can_continue</code></a>
- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>
- <a href="../build_guardrail_evidence_definitions/"><code>fabricops_kit.pipeline.build_guardrail_evidence_definitions</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L156-L307">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L156-L307</a>
- Start line: `156`
- End line: `307`
- Signature:

```python
def run_table_guardrails(table_configs: list[dict[str, Any]], *, config: Any, env: str, run_id: str, spark_session: Any, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='') -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../guardrail_summary/"><code>fabricops_kit.pipeline.guardrail_summary</code></a>
- <a href="../stop_if_any_guardrail_failed/"><code>fabricops_kit.pipeline.stop_if_any_guardrail_failed</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Internal implementation helpers

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../internal/pipeline__guardrail_can_continue/"><code>fabricops_kit.pipeline._guardrail_can_continue</code></a>
- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>
- <a href="../build_guardrail_evidence_definitions/"><code>fabricops_kit.pipeline.build_guardrail_evidence_definitions</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

</details>
