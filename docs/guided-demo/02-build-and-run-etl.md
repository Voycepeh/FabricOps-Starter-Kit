# Step 2. Build a Pipeline

### Before you begin

1. Complete [Step 00B. Configure the Environment and load assets](00B-configure-environment-and-load-assets.md).
2. Download [`02_pipeline.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/notebooks/02_pipeline.ipynb) and import it into the Engineering Development workspace.
3. Import `00_env_config.ipynb` beside it and attach the same Fabric Environment used in Step 00B.

The template deliberately contains placeholder table names. Read this walkthrough first, then replace them before running the Read or Write cells.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## The big picture

Start by understanding the shape of the notebook before changing its code.

</div>
</div>

**Learn the reusable `02_pipeline` notebook from top to bottom, then adapt it to your own governed pipeline.**

![FabricOps places governed Read and Write boundaries around project-owned PySpark](../assets/pipeline-boundaries-implementation.svg)

The same pattern supports Full and Incremental reads and the Overwrite, Append, SCD1, and SCD2 load strategies. The later demos apply it to each processing style.

### Get familiar with the notebook

The notebook follows one visible lifecycle:

| Notebook section | What happens |
| --- | --- |
| Environment | Loads the shared Fabric configuration and imports the three public functions used by the pipeline. |
| Data Contract | Lets you choose whether each governed target should **Enforce** an active contract or **Validate** a frozen candidate. |
| Governed Read | Reads each configured source and runs the applicable source checks. |
| PySpark Transform | Contains the joins, filters, derived columns, aggregations, or selections owned by your project. |
| Governed Write | Checks and, when allowed, publishes each target using its configured load strategy. |
| Optional inspection | Exposes selected Read and Write results while you develop or troubleshoot. |

The template starts with one Read, one transformation, and one Write. Add more Read or Write blocks only when your pipeline needs them.

### Load the shared environment

```python
%run 00_env_config
```

`00_env_config` loads the configured Bronze, Silver, Gold, and Metadata stores, the environment and notebook identity, the Spark session, and metadata routing. You should see the shared FabricOps configuration load without an error.

### Import required widget functions

Then run the import cell immediately below it. The import cell provides the public APIs used by that notebook, so its exact list can vary by demo.

![Notebook after loading the shared FabricOps environment](../assets/02/Setup.png)

### Run the Data Contract block

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

For the initial Guided Demo run, there is no Data Contract yet, so leave the selection unchanged. Contract-backed checks will return as skipped, and the targets can publish in Engineering Development.

![Data Contract selector before a contract exists](../assets/02/Data%20_Contract_None.png)


??? info "Under the hood"

    The selector resolves the notebook's source and target identities from `METADATA_DATA_LINEAGE`, then resolves the available Data Contract state for each table.

    In Engineering Development, **Validate** is available only for targets and requires an exact frozen Data Contract version. It does not activate that version. In Production, FabricOps requires the active version and uses **Enforce**.

    The returned `CONTRACTS` object carries the table-level mode and contract identity into `orchestrate_write()`. See [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md) for the exact return contract.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Configure the Governed Read

Select governed sources and run Read checks before transforming the data.

</div>
</div>

First, run the source results dictionary cell:

```python
sources = {}
```

This creates an empty dictionary for the governed Read results. Each Read is stored by name so the Transform can use its DataFrame and the Write can reuse its governed source identity for lineage and source-aware checks.

Then run the configured Read cell:

```python
source = orchestrate_read(
    store="Bronze",
    schema="demo",
    table_name="source_table",  # Replace with the governed source table.
    read_mode="full",
    query=None,
    spark_session=spark,
    frequency_top_n=5,
)
sources["source"] = source
```

| Parameter | What you normally change |
| --- | --- |
| `name` | A short notebook-facing name for this source. Use the same key in `sources`. |
| `store` | The configured source store, such as `Bronze`. |
| `schema` | The physical source schema. |
| `table_name` | The physical source table. Replace `source_table`. |
| `read_mode` | Use `"full"` or `"incremental"`. |
| `query` | Optionally provide a read-only Warehouse query; otherwise leave it as `None`. |
| `read_parameters` | Add mode-specific options such as the watermark column for an Incremental read. |
| `target_table_id` | Add the governed target identity required by an Incremental read. |

The result is a dictionary, not only a DataFrame. Use its DataFrame for transformation while retaining the complete result for checks and lineage:

```python
source_df = sources["source"]["dataframe"]
display(source_df)
```

If a transformation needs another governed source, duplicate the complete **READ 1 — Example source** block, give the Read and its dictionary key a unique name, and configure the second table. Remove a Read block when it does not contribute to the pipeline. Every source that contributes to a target should later appear in that target's `sources` list.

For Incremental reads, add `read_parameters` and `target_table_id` rather than implementing watermark filtering in the transformation. See [Read and Load Strategies](../reference/read-and-load-strategies.md) and the [Step 2B demo](02B-build-and-run-incremental-append-etl.md).

??? info "Under the hood"

    [`orchestrate_read()`](../api/reference/orchestrate_read.md) runs the standard lifecycle:

    1. **Read** the configured source.
    2. Evaluate the **Freshness** Guardrail when one applies.
    3. Check the **Schema** when a governed expectation applies.
    4. Evaluate **Data Quality** Guardrails when defined.
    5. **Profile** the full source and store the snapshot in `METADATA_DATA_PROFILED` and, where applicable, `METADATA_DATA_PROFILED_FREQUENCY`.

    Checks without an applicable Data Contract or Guardrail return a skipped result rather than inventing an expectation. Incremental batches are not profiled; FabricOps instead returns the eligible scope and uses `METADATA_SOURCE_OBSERVATION` plus the governed target's successful watermark progress to manage incremental execution.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Write your PySpark Transform

Implement project-specific PySpark transformations between governed boundaries.

</div>
</div>

**Replace this entire cell with the business transformation your project needs.**

The template begins with a valid identity transformation:

```python
transformed_df = sources["source"]["dataframe"].select("*")

# Optional development inspection.
# display(transformed_df)
```

Leaving the identity selection in place is fine when the source already has the target shape. Otherwise, this is where normal PySpark belongs: join DataFrames from multiple `sources` entries, filter rows, derive columns, aggregate records, or select the final schema.

FabricOps does not prescribe the transformation style. Keep project-owned PySpark in this section and keep the governed orchestration calls in their Read and Write sections.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Configure the Governed Write

Publish the transformed data through the governed Write orchestrator.

</div>
</div>

First, run the write results dictionary cell:

```python
writes = {}
```

This creates an empty dictionary for the governed Write results. Each Write is stored by target name so its publication status, orchestration stages, Guardrail results, and, when published, target profile remain available for inspection.

Then run the configured Write cell:

```python
writes["target"] = orchestrate_write(
    transformed_df,
    sources=[sources["source"]],
    store="Silver",
    schema="demo",
    table_name="target_table",  # Replace with the governed target table.
    write_mode="overwrite",
    contracts=CONTRACTS,
    repartition_by=None,
    spark_session=spark,
    frequency_top_n=5,
)
```

| Parameter | What you normally change |
| --- | --- |
| `transformed_df` | The DataFrame produced by your transformation section. |
| `name` | A short notebook-facing name for the target. Use the same key in `writes`. |
| `sources` | Every complete Read result that contributed to this target. |
| `store`, `schema`, `table_name` | The configured target store and physical target identity. Replace `target_table`. |
| `write_mode` | The load strategy: `"overwrite"`, `"append"`, `"scd1"`, or `"scd2"`. |
| `write_parameters` | Add parameters required by the selected strategy, such as SCD keys and tracked columns. |
| `contracts` | Leave as `CONTRACTS` so the target follows the widget selection. |
| `repartition_by` | Optionally control the Spark partition count before writing; otherwise leave it as `None`. |


??? info "Under the hood"

    [`orchestrate_write()`](../api/reference/orchestrate_write.md) runs the standard pre-publication checks in this order:

    1. **Schema**
    2. **Sensitive Data**
    3. **Source Drift**
    4. **Data Quality**
    5. **Guardrail Coverage**

    With **Validate**, FabricOps returns after those checks with `published=False`; the target is not written. With **Enforce**, passing the required checks allows FabricOps to continue through **Write** and then **Profile** the persisted target in `METADATA_DATA_PROFILED` and, where applicable, `METADATA_DATA_PROFILED_FREQUENCY`.

    A successful Write also records the source and target pipeline participation in `METADATA_DATA_LINEAGE`. Source Observation history used by Source Drift and incremental execution is committed only through the successful write path.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Inspect selected results

Review orchestration stages, Data Quality results, and published profiles.

</div>
</div>

**Uncomment only the displays that help you understand or troubleshoot the current run.**

The template keeps inspection outside the orchestration calls so the standard lifecycle remains easy to see.

```python
# Read DataFrame and ordered Read stages.
# display(sources["source"]["dataframe"])
# display(sources["source"]["orchestration_stages"])

# Ordered Write stages and Data Quality results.
# display(writes["target"]["orchestration_stages"])
# display(writes["target"]["dq_result"])

# Column-level profile metrics after publication.
# display(writes["target"].get("profile_result", {}).get("profile"))
```

The guarded `.get()` call is useful because a Validate-mode Write does not publish or return a persisted-target profile.

With `verbose=True` (the default), every successful Read and Write ends with a summary. `total_duration_seconds` includes the complete lifecycle, including Guardrails and profiling. Inspect the same measurements programmatically:

```python
print(sources["source"]["read_metrics"])
print(writes["target"]["write_metrics"])
print(writes["target"]["total_duration_seconds"])
```

`rows_committed` measures this physical publication; `total_target_rows` describes the profiled persisted target. `input_rows` is a separate measure. Unmeasured values are `None` in results and `Not available` in notebook output. Reporting adds no Spark counts or target scans.

??? info "Availability and retries"

    Lakehouse Append and Overwrite use the exact tagged Delta commit's output-row metric, including zero-row commits. Reporting uses bounded metadata-file reads, with no extra Spark jobs. Inaccessible metadata, a concurrent later commit, an exhausted metadata-probe budget, or missing operation metrics produce `Not available`. Caller-supplied Delta `userMetadata` in writer options or Spark session configuration is preserved and disables this attribution. The lookup uses checkpoint metadata and at most 32 exact log-file probes; it never enumerates the Delta log directory.

    Warehouse connector writes do not return attributable row counts. Existing SCD merges include technical audit updates, so business inserts, updates, unchanged rows, and expired versions remain unavailable unless independently measurable. A new Lakehouse SCD target uses a measured bootstrap write when supported; its inserted rows or versions are reported separately. An already-applied Append or Overwrite retry reports zero newly committed rows. Validate-only runs report `Published → No` and zero committed rows.

??? tip "A summary is missing in Microsoft Fabric"

    Confirm the call uses `orchestrate_read()` or `orchestrate_write()` with `verbose=True`; Read, Write and Guardrail stages are internal to those public orchestrators. Summaries print to driver stdout after successful execution. A failed stage does not print a successful final summary.

    Fabric runs the package installed in the notebook's Environment, which can differ from repository `main`. Check the imported package and function source in the running session:

    ```python
    import inspect
    import fabricops_kit
    from fabricops_kit import orchestrate_write

    print(fabricops_kit.__version__)
    print(fabricops_kit.__file__)
    print(inspect.getsource(orchestrate_write))
    ```

    Publish the updated wheel in the correct Fabric Environment and start a fresh notebook session before importing again. A previously imported function can remain bound to old code. Check the notebook cell or activity's stdout output. The orchestrator intentionally quiets physical writer logs; this does not suppress its own summary, and changing Write mode does not restore missing summary code.


??? info "More useful inspection keys"

    The notebook also includes these focused options:

    ```python
    # Incremental Read scope.
    # display(sources["source"]["scope"])

    # Write-side Schema and Source Drift results.
    # display(writes["target"]["schema_result"])
    # display(writes["target"]["source_drift_results"])
    ```

    The complete result contracts are documented on the [`orchestrate_read()`](../api/reference/orchestrate_read.md) and [`orchestrate_write()`](../api/reference/orchestrate_write.md) reference pages.


### Expected result

You can now identify every section of `02_pipeline`, know which cells to customize, and understand what FabricOps handles at the governed Read and Write boundaries. You are ready to apply the same scaffold in a working example.

**Next:** Start with Full Refresh, then use the other demos to explore stateful processing patterns.

| Demo | What you will learn |
| --- | --- |
| [Step 2A. Full Refresh](02A-full-refresh-demo.md) | The recommended starting point. Read three retail sources, transform them with PySpark, and publish two targets using Full reads and Overwrite. |
| [Step 2B. Incremental Append](02B-build-and-run-incremental-append-etl.md) | Use a watermark and governed source-to-target identity to process only newly eligible inventory movements. Its three runs show the initial load, new source data, and a no-change run. |
| [Step 2C. SCD1 and SCD2](02C-build-and-run-scd-etl.md) | Send three complete Product Master snapshots through Full reads. Compare SCD1, which replaces changed values in the current record, with SCD2, which preserves prior versions as history. |
