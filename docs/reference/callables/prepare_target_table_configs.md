# prepare_target_table_configs

Enrich target table configs and add FabricOps audit columns for 02_pipeline.

## What this is for and when to use it

Enrich target table configs and add FabricOps audit columns for 02_pipeline.

- Use after TARGET_TABLES and DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS are defined to add audit columns, derive target defaults, and build TARGET_CONFIG_BY_KEY.

## When not to use it

- Do not use before business target DataFrames have been created in the transform section.

## Example

```python
TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_target_table_configs(TARGET_TABLES, DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS, RUN_ID, PIPELINE_NAME)
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
      <td data-label="Parameter"><code>target_table_configs</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">User-authored ``TARGET_TABLES`` entries. Each entry must include ``key``, ``df``, ``layer``, and ``table_name``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>default_target_guardrails_and_write_options</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Default target guardrail and write settings merged before each target config.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Current pipeline run identifier for audit columns.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline name for audit columns.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Enriched target configs and a dictionary keyed by target key.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Adds FabricOps audit columns to target DataFrames; it does not write targets.

## Related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../write_target_tables/"><code>fabricops_kit.pipeline.write_target_tables</code></a>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L223-L278">View prepare_target_table_configs on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def prepare_target_table_configs(
    target_table_configs: list[dict[str, Any]],
    default_target_guardrails_and_write_options: Mapping[str, Any],
    run_id: str,
    pipeline_name: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Enrich target table configs and add FabricOps runtime audit columns.

    Parameters
    ----------
    target_table_configs : list of dict
        User-authored ``TARGET_TABLES`` entries. Each entry must include
        ``key``, ``df``, ``layer``, and ``table_name``.
    default_target_guardrails_and_write_options : mapping
        Default target guardrail and write settings merged before each target
        config.
    run_id : str
        Current pipeline run identifier for audit columns.
    pipeline_name : str
        Pipeline name for audit columns.

    Returns
    -------
    tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
        Enriched target configs and a lookup keyed by target ``key``.
    """
    from pyspark.sql import functions as F

    audit_created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    enriched_targets: list[dict[str, Any]] = []
    for target_config in target_table_configs:
        merged_target = {**default_target_guardrails_and_write_options, **target_config}
        target_df = (
            merged_target["df"]
            .withColumn("_fabricops_run_id", F.lit(run_id))
            .withColumn("_fabricops_pipeline_name", F.lit(pipeline_name))
            .withColumn("_fabricops_created_at", F.lit(audit_created_at))
        )
        dataset_name = merged_target.get("dataset_name", merged_target["table_name"])
        stage = merged_target.get("stage", merged_target["layer"])
        target_layer = merged_target.get("target_layer", merged_target["layer"])
        target_name = merged_target.get("target_name", merged_target["table_name"])
        target_kind = merged_target.get("target_kind", merged_target.get("kind", "lakehouse"))
        watermark_value = merged_target.get("watermark_value", None)
        enriched_target = {
            **merged_target,
            "df": target_df,
            "dataset_name": dataset_name,
            "stage": stage,
            "target_layer": target_layer,
            "target_name": target_name,
            "target_kind": target_kind,
            "watermark_value": watermark_value,
        }
        enriched_targets.append(enriched_target)
    return enriched_targets, {target_config["key"]: target_config for target_config in enriched_targets}
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.prepare_target_table_configs`
- Short name: `prepare_target_table_configs`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `223`
- Inbound references count: 0
- Outbound references count: 0

### AI implementation contract

- **required_context:** Run inside Fabric/Spark after target DataFrames exist and before target guardrails run.
- **inputs:** target_table_configs, default_target_guardrails_and_write_options, run_id, and pipeline_name.
- **output:** Enriched target configs and a dictionary keyed by target key.
- **side_effects:** Adds FabricOps audit columns to target DataFrames; it does not write targets.
- **failure_modes:** Not documented yet
- **verification:** Verify run_table_guardrails receives the enriched TARGET_TABLES and write_target_tables runs only after stop_if_any_guardrail_failed passes.

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L223-L278">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L223-L278</a>
- Start line: `223`
- End line: `278`
- Signature:

```python
def prepare_target_table_configs(target_table_configs: list[dict[str, Any]], default_target_guardrails_and_write_options: Mapping[str, Any], run_id: str, pipeline_name: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../write_target_tables/"><code>fabricops_kit.pipeline.write_target_tables</code></a>

### Internal implementation helpers

Not documented yet

</details>
