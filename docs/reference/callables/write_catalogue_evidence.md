# write_catalogue_evidence

Enrich profile rows with guardrail context and write catalogue evidence.

## What this is for and when to use it

Enrich profile rows with guardrail context and write catalogue evidence.

- Use after source or target profiles and guardrail results are available to persist catalogue evidence through the configured metadata route.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
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
      <td data-label="Parameter"><code>profiles</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Profile DataFrames produced by ``profile_dataframe`` for each dataset.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target definitions containing table, stage, and layer context.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Metadata lakehouse route from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>agreement_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Governance context added to each catalogue row.</td>
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
    <tr>
      <td data-label="Parameter"><code>schema_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Guardrail results keyed by dataset alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>freshness_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>stability_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dq_results</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Metadata table to append.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Write mode for catalogue evidence.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of write statuses keyed by dataset alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse target.

## Related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__canonical_catalogue_profile_df/"><code>fabricops_kit.pipeline._canonical_catalogue_profile_df</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/pipeline.py#L450-L555">View write_catalogue_evidence on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def write_catalogue_evidence(
    profiles: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    metadata_table: str = CATALOGUE_TABLE,
    mode: str = "append",
) -> dict[str, str]:
    """Enrich profile rows with guardrail context and write catalogue evidence.

    Parameters
    ----------
    profiles : mapping of str to DataFrame
        Profile DataFrames produced by ``profile_dataframe`` for each dataset.
    dataset_definitions : mapping of str to mapping
        Source or target definitions containing table, stage, and layer context.
    config, env : object, str
        Metadata lakehouse route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context added to each catalogue row.
    schema_results, freshness_results, stability_results, dq_results : mapping, optional
        Guardrail results keyed by dataset alias.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Metadata table to append.
    mode : str, default="append"
        Write mode for catalogue evidence.

    Returns
    -------
    dict[str, str]
        Write status keyed by dataset alias.
    """
    from pyspark.sql import functions as F

    audit = _runtime_audit_fields(config, env)
    statuses: dict[str, str] = {}
    for name, profile_df in profiles.items():
        definition = dataset_definitions[name]
        table_name = _definition_name(name, definition)
        dataset_name = str(definition.get("dataset_name") or table_name)
        stage = str(definition.get("stage", "target"))
        stability_result = dict((stability_results or {}).get(name) or {})
        freshness_result = dict((freshness_results or {}).get(name) or {})
        schema_result = dict((schema_results or {}).get(name) or {})
        dq_fields = _dq_summary_fields((dq_results or {}).get(name))
        evidence = _canonical_catalogue_profile_df(profile_df)
        metadata_table_key = _build_metadata_table_key(env, dataset_name, table_name)
        additions = {
            "metadata_table_key": metadata_table_key,
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "pipeline_name": pipeline_name,
            "profile_run_id": run_id,
            "profile_stage": stage,
            "profile_status": "success",
            "baseline_status": str(stability_result.get("baseline_status", stability_result.get("status", ""))),
            "source_data_change_check": str(definition.get("load_behavior", "")) if stage == "source" else "",
            "target_data_change_check": str(definition.get("load_behavior", "")) if stage == "target" else "",
            "profile_baseline_mode": str(stability_result.get("load_behavior", "")),
            "profiled_at": _now_iso(),
            "agreement_id": agreement_id,
            "contract_version": agreement_contract_version,
            "notebook_registry_id": notebook_registry_id,
            "notebook_id": notebook_id,
            "evidence_role": str(definition.get("evidence_role", f"{stage}_profile")),
            "source_schema_check": str(definition.get("schema_preset", "")) if stage == "source" else "",
            "target_schema_check": str(definition.get("schema_preset", "")) if stage == "target" else "",
            "stability_check_enabled": bool(stability_result.get("stability_check_enabled", False)),
            "load_behavior": str(stability_result.get("load_behavior", definition.get("load_behavior", ""))),
            "watermark_column": str(stability_result.get("watermark_column", definition.get("watermark_column", ""))),
            "freshness_column": str(freshness_result.get("freshness_column", definition.get("freshness_column", ""))),
            "freshness_max_lag_days": str(freshness_result.get("freshness_max_lag_days", definition.get("freshness_max_lag_days", ""))),
            "freshness_status": str(freshness_result.get("freshness_status", freshness_result.get("status", ""))),
            "freshness_can_continue": bool(freshness_result.get("freshness_can_continue", freshness_result.get("can_continue", True))),
            "freshness_message": str(freshness_result.get("freshness_message", freshness_result.get("message", ""))),
            "baseline_run_id": str(stability_result.get("baseline_run_id", "")),
            "stability_status": str(stability_result.get("stability_status", stability_result.get("status", ""))),
            "stability_can_continue": bool(stability_result.get("stability_can_continue", stability_result.get("can_continue", True))),
            "stability_message": str(stability_result.get("stability_message", stability_result.get("message", ""))),
            "stability_difference_summary": str(stability_result.get("stability_difference_summary", "")),
            "source_change_signal_json": json.dumps({"schema": schema_result, "freshness": freshness_result, "stability": stability_result}, default=str, sort_keys=True),
            **dq_fields,
            **audit,
        }
        for column, value in additions.items():
            evidence = evidence.withColumn(column, F.lit(value))
        evidence = evidence.withColumn("metadata_column_key", F.concat_ws("::", F.lit(metadata_table_key), F.col("column_name")))
        write_lakehouse_table(evidence, config, env, "metadata", metadata_table, mode=mode)
        statuses[name] = "written"
    return statuses
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_catalogue_evidence`
- Short name: `write_catalogue_evidence`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `450`
- Inbound references count: 1
- Outbound references count: 7

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Catalogue evidence`.
- **inputs:** profiles, dataset definitions, config, env, run_id, agreement context, notebook context, and optional guardrail results.
- **output:** Dictionary of write statuses keyed by dataset alias.
- **side_effects:** Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__canonical_catalogue_profile_df/"><code>fabricops_kit.pipeline._canonical_catalogue_profile_df</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/pipeline.py#L450-L555">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/pipeline.py#L450-L555</a>
- Start line: `450`
- End line: `555`
- Signature:

```python
def write_catalogue_evidence(profiles: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', schema_results: Mapping[str, Mapping[str, Any]] | None=None, freshness_results: Mapping[str, Mapping[str, Any]] | None=None, stability_results: Mapping[str, Mapping[str, Any]] | None=None, dq_results: Mapping[str, Mapping[str, Any]] | None=None, metadata_table: str=CATALOGUE_TABLE, mode: str='append') -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__canonical_catalogue_profile_df/"><code>fabricops_kit.pipeline._canonical_catalogue_profile_df</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

</details>
