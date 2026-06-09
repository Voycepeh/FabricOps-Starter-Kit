# write_pipeline_lineage

Write many-to-many source-to-target lineage evidence.

## What this is for and when to use it

Write many-to-many source-to-target lineage evidence.

- Use after target writes to persist lineage relationships tied to agreement and notebook registry context.

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
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used to create lineage rows.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Metadata route from ``00_env_config``.</td>
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
      <td data-label="Parameter"><code>source_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source and target definitions keyed by alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>relationships</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Many-to-many lineage relationships. Each item may contain ``sources``, ``targets``, ``operation``, and ``description``. When omitted, every source is linked to every target.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Governance context embedded in lineage payloads.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>agreement_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
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
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Metadata lineage table.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Write mode for lineage evidence.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Status, row count, and lineage rows.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.

## Related functions

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../build_lineage_records/"><code>fabricops_kit.data_lineage.build_lineage_records</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/pipeline.py#L220-L304">View write_pipeline_lineage on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def write_pipeline_lineage(
    *,
    spark: Any,
    config: Any,
    env: str,
    run_id: str,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None = None,
    dataset_name: str = "",
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    metadata_table: str = LINEAGE_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write many-to-many source-to-target lineage evidence.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create lineage rows.
    config, env : object, str
        Metadata route from ``00_env_config``.
    run_id : str
        Pipeline run identifier.
    source_definitions, target_definitions : mapping
        Source and target definitions keyed by alias.
    relationships : list of mapping, optional
        Many-to-many lineage relationships. Each item may contain ``sources``,
        ``targets``, ``operation``, and ``description``. When omitted, every
        source is linked to every target.
    dataset_name, agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context embedded in lineage payloads.
    metadata_table : str, default="METADATA_DATA_LINEAGE_TABLE"
        Metadata lineage table.
    mode : str, default="append"
        Write mode for lineage evidence.

    Returns
    -------
    dict[str, Any]
        Status, row count, and written rows.
    """
    audit = _runtime_audit_fields(config, env)
    created_at = _now_iso()
    if relationships is None:
        relationships = [{"sources": list(source_definitions), "targets": list(target_definitions), "operation": "pipeline_transform", "description": "User-defined pipeline transformation."}]
    rows: list[dict[str, Any]] = []
    sequence = 0
    for relationship in relationships:
        for source_alias in relationship.get("sources", []):
            for target_alias in relationship.get("targets", []):
                sequence += 1
                source_table = _definition_name(str(source_alias), source_definitions[str(source_alias)])
                target_table = _definition_name(str(target_alias), target_definitions[str(target_alias)])
                payload = {
                    "run_id": run_id,
                    "agreement_id": agreement_id,
                    "agreement_contract_version": agreement_contract_version,
                    "notebook_registry_id": notebook_registry_id,
                    "notebook_id": notebook_id,
                    "pipeline_name": pipeline_name,
                    "source_alias": source_alias,
                    "target_alias": target_alias,
                    "operation": relationship.get("operation", "pipeline_transform"),
                    "description": relationship.get("description", ""),
                }
                rows.append({
                    "lineage_id": f"{run_id}_{sequence}",
                    "dataset_name": dataset_name or str(target_definitions[str(target_alias)].get("dataset_name") or target_table),
                    "run_id": run_id,
                    "source_table": source_table,
                    "target_table": target_table,
                    "source_table_key": _build_metadata_table_key(env, str(source_definitions[str(source_alias)].get("dataset_name") or source_table), source_table),
                    "target_table_key": _build_metadata_table_key(env, str(target_definitions[str(target_alias)].get("dataset_name") or target_table), target_table),
                    "transformation_steps_json": json.dumps(payload, default=str, sort_keys=True),
                    "created_at": created_at,
                    **audit,
                })
    if rows:
        write_lakehouse_table(spark.createDataFrame(rows), config, env, "metadata", metadata_table, mode=mode)
    return {"status": "written" if rows else "skipped", "row_count": len(rows), "rows": rows}
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_pipeline_lineage`
- Short name: `write_pipeline_lineage`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `220`
- Inbound references count: 0
- Outbound references count: 5

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Lineage evidence`.
- **inputs:** spark, config, env, run_id, source_definitions, target_definitions, relationships, and governance context.
- **output:** Status, row count, and lineage rows.
- **side_effects:** Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/pipeline.py#L220-L304">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/pipeline.py#L220-L304</a>
- Start line: `220`
- End line: `304`
- Signature:

```python
def write_pipeline_lineage(*, spark: Any, config: Any, env: str, run_id: str, source_definitions: Mapping[str, Mapping[str, Any]], target_definitions: Mapping[str, Mapping[str, Any]], relationships: list[Mapping[str, Any]] | None=None, dataset_name: str='', agreement_id: str='', agreement_contract_version: str='', notebook_registry_id: str='', notebook_id: str='', pipeline_name: str='', metadata_table: str=LINEAGE_TABLE, mode: str='append') -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../build_lineage_records/"><code>fabricops_kit.data_lineage.build_lineage_records</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation helpers

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

</details>
