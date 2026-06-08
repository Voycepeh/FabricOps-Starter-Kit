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
      <td data-label="Parameter"><code>drift_results</code></td>
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

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/pipeline.py#L70-L178">View write_catalogue_evidence on GitHub</a>

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
    drift_results: Mapping[str, Mapping[str, Any]] | None = None,
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
    schema_results, drift_results, dq_results : mapping, optional
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
        drift_result = dict((drift_results or {}).get(name) or {})
        schema_result = dict((schema_results or {}).get(name) or {})
        dq_fields = _dq_summary_fields((dq_results or {}).get(name))
        row_count = None
        if hasattr(profile_df, "select"):
            try:
                row_count = profile_df.select("ROW_COUNT").first()["ROW_COUNT"]
            except Exception:
                row_count = None
        evidence = profile_df
        additions = {
            "metadata_table_key": _build_metadata_table_key(env, dataset_name, table_name),
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "pipeline_name": pipeline_name,
            "profile_run_id": run_id,
            "profile_stage": stage,
            "profile_status": "success",
            "baseline_status": str(drift_result.get("baseline_status", drift_result.get("status", ""))),
            "source_data_change_check": str(definition.get("drift_preset", "")),
            "profile_baseline_mode": str(drift_result.get("baseline_mode", "")),
            "agreement_id": agreement_id,
            "contract_version": agreement_contract_version,
            "AGREEMENT_ID": agreement_id,
            "AGREEMENT_CONTRACT_VERSION": agreement_contract_version,
            "NOTEBOOK_REGISTRY_ID": notebook_registry_id,
            "NOTEBOOK_ID": notebook_id,
            "PROFILE_RUN_ID": run_id,
            "ENVIRONMENT_NAME": env,
            "DATASET_NAME": dataset_name,
            "PIPELINE_NAME": pipeline_name,
            "EVIDENCE_ROLE": str(definition.get("evidence_role", f"{stage}_profile")),
            "PROFILE_STAGE": stage,
            "PROFILE_STATUS": "success",
            "BASELINE_STATUS": str(drift_result.get("status", "")),
            "SOURCE_SCHEMA_CHECK": str(definition.get("schema_preset", "")) if stage == "source" else "",
            "TARGET_SCHEMA_CHECK": str(definition.get("schema_preset", "")) if stage == "target" else "",
            "SOURCE_DATA_CHANGE_CHECK": str(definition.get("drift_preset", "")) if stage == "source" else "",
            "TARGET_DATA_CHANGE_CHECK": str(definition.get("drift_preset", "")) if stage == "target" else "",
            "SOURCE_CHANGE_SIGNAL_JSON": json.dumps({"schema": schema_result, "drift": drift_result}, default=str, sort_keys=True),
            "LAYER": str(definition.get("layer", "")),
            "ASSET_KIND": str(definition.get("kind", "lakehouse")),
            "PROFILED_TABLE_NAME": table_name,
            "PROFILED_ROW_COUNT": row_count,
            **dq_fields,
            **audit,
        }
        for column, value in additions.items():
            evidence = evidence.withColumn(column, F.lit(value))
        evidence = evidence.withColumn("metadata_column_key", F.concat_ws("::", F.lit(_build_metadata_table_key(env, dataset_name, table_name)), F.col("COLUMN_NAME")))
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
- Source line: `70`
- Inbound references count: 0
- Outbound references count: 5

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Catalogue evidence`.
- **inputs:** profiles, dataset definitions, config, env, run_id, agreement context, notebook context, and optional guardrail results.
- **output:** Dictionary of write statuses keyed by dataset alias.
- **side_effects:** Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/pipeline.py#L70-L178">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/pipeline.py#L70-L178</a>
- Start line: `70`
- End line: `178`
- Signature:

```python
def write_catalogue_evidence(profiles: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, run_id: str, agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', schema_results: Mapping[str, Mapping[str, Any]] | None=None, drift_results: Mapping[str, Mapping[str, Any]] | None=None, dq_results: Mapping[str, Mapping[str, Any]] | None=None, metadata_table: str=CATALOGUE_TABLE, mode: str='append') -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__dq_summary_fields/"><code>fabricops_kit.pipeline._dq_summary_fields</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

</details>
