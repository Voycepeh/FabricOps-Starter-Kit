# Step 2. Build a Pipeline

**Learn the reusable `02_pipeline` notebook from top to bottom, then adapt it to your own governed pipeline.**

`02_pipeline` is the standard starting point for governed data engineering in FabricOps. You configure the sources and targets and write the PySpark transformation; FabricOps runs the governance lifecycle around that project-owned logic.

1. Environment
2. Data Contract
3. Read
4. Transform
5. Write

The same pattern supports Full and Incremental reads and the Overwrite, Append, SCD1, and SCD2 load strategies. The later demos apply it to each processing style.

![FabricOps places governed Read and Write boundaries around project-owned PySpark](../assets/pipeline-boundaries-implementation.svg)

## Before you begin

1. Complete [Step 00B. Configure the Environment and load assets](00B-configure-environment-and-load-assets.md).
2. Download [`02_pipeline.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/notebooks/02_pipeline.ipynb) and import it into the Engineering Development workspace.
3. Import `00_env_config.ipynb` beside it and attach the same Fabric Environment used in Step 00B.

The template deliberately contains placeholder table names. Read this walkthrough first, then replace them before running the Read or Write cells.

## What to do

### 1. Get familiar with the notebook

**Start by understanding the shape of the notebook before changing its code.**

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

### 2. Load the Environment

**Run the shared environment first; you will normally leave these cells unchanged.**

```python
%run 00_env_config
```

`00_env_config` establishes the configured Fabric stores, environment, notebook identity, Spark session, and metadata routing used by the rest of the notebook. The next cell imports only the public APIs needed by this scaffold:

```python
from fabricops_kit import orchestrate_read, orchestrate_write, widget_select_data_contract
```

Change these cells only when your project has intentionally changed its shared environment notebook or needs additional public FabricOps functions.

### 3. Select the Data Contract mode

**Run the selector once and keep its result in `CONTRACTS`.**

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

The widget discovers the tables linked to this notebook through `METADATA_DATA_LINEAGE`. Sources remain in **Enforce** mode; in Engineering Development, each target can independently use **Enforce** or **Validate**.

| Mode | When to use it | Publication behavior |
| --- | --- | --- |
| **Enforce** | Run with the active Data Contract for the current environment. A new Development target can remain unselected until Governance authors one. | The Write can publish after the required checks pass. |
| **Validate** | Test one exact frozen candidate before Governance activates it. | The same pre-publication checks run, but the target is not written. |

You generally do not edit the selector code. Use the displayed controls to choose the mode and candidate for each target.

??? example "See the selector before a Data Contract exists"

    During the first Guided Demo run, Governance has not authored a Data Contract yet. The selector can therefore show no enforceable contract for the target.

    ![Data Contract selector with no contract selected](../assets/02/Data%20_Contract_None.png)

??? info "Under the hood"

    The selector resolves the notebook's source and target identities from `METADATA_DATA_LINEAGE`, then resolves the available Data Contract state for each table.

    In Engineering Development, **Validate** is available only for targets and requires an exact frozen Data Contract version. It does not activate that version. In Production, FabricOps requires the active version and uses **Enforce**.

    The returned `CONTRACTS` object carries the table-level mode and contract identity into `orchestrate_write()`. See [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md) for the exact return contract.

### 4. Configure the Governed Read

**Replace the source identity in the existing Read block and keep the complete result in `sources`.**

```python
# Keep each complete Read result for transformation, checks, and lineage.
sources = {}

source = orchestrate_read(
    name="source",
    store="Bronze",
    schema="demo",
    table_name="source_table",  # Replace with the governed source table.
    read_mode="full",
    query=None,
    spark_session=spark,
)
sources["source"] = source
```

The template values show exactly where to customize the Read:

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

### 5. Write your PySpark Transform

**Replace this entire cell with the business transformation your project needs.**

The template begins with a valid identity transformation:

```python
transformed_df = sources["source"]["dataframe"].select("*")

# Optional development inspection.
# display(transformed_df)
```

Leaving the identity selection in place is fine when the source already has the target shape. Otherwise, this is where normal PySpark belongs: join DataFrames from multiple `sources` entries, filter rows, derive columns, aggregate records, or select the final schema.

FabricOps does not prescribe the transformation style. Keep project-owned PySpark in this section and keep the governed orchestration calls in their Read and Write sections.

### 6. Configure the Governed Write

**Pass the transformed DataFrame and every contributing governed Read result into the target's Write block.**

```python
# Keep complete Write results for optional inspection.
writes = {}

writes["target"] = orchestrate_write(
    transformed_df,
    name="target",
    sources=[sources["source"]],
    store="Silver",
    schema="demo",
    table_name="target_table",  # Replace with the governed target table.
    write_mode="overwrite",
    contracts=CONTRACTS,
    repartition_by=None,
    spark_session=spark,
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

The `sources` list is part of the governed hand-off. FabricOps uses those canonical source identities to evaluate source-aware Guardrails and record source-to-target participation in `METADATA_DATA_LINEAGE`.

You can add multiple independent Write blocks and give each result a unique key in `writes`. They do not form an atomic multi-target transaction: an earlier target can publish successfully even if a later Write fails.

??? info "Under the hood"

    [`orchestrate_write()`](../api/reference/orchestrate_write.md) runs the standard pre-publication checks in this order:

    1. **Schema**
    2. **Sensitive Data**
    3. **Source Drift**
    4. **Data Quality**
    5. **Guardrail Coverage**

    With **Validate**, FabricOps returns after those checks with `published=False`; the target is not written. With **Enforce**, passing the required checks allows FabricOps to continue through **Write** and then **Profile** the persisted target in `METADATA_DATA_PROFILED` and, where applicable, `METADATA_DATA_PROFILED_FREQUENCY`.

    A successful Write also records the source and target pipeline participation in `METADATA_DATA_LINEAGE`. Source Observation history used by Source Drift and incremental execution is committed only through the successful write path.

### 7. Inspect selected results

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

### 8. Put the pattern together

**The reusable core is `Governed Read → Your PySpark Transform → Governed Write`.**

You configure the governed source and target identities and own the business transformation. FabricOps executes the standard checks, applies the selected Data Contract mode, publishes when allowed, and writes the applicable records to `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_DATA_LINEAGE`, `METADATA_GUARDRAIL_RESULTS`, and `METADATA_SOURCE_OBSERVATION`.

### 9. Explore the guided demos

**Start with Full Refresh, then use the other demos to explore stateful processing patterns.**

| Demo | What you will learn |
| --- | --- |
| [**Step 2A. Full Refresh**](02A-full-refresh-demo.md) | The recommended starting point. Read three retail sources, transform them with PySpark, and publish two targets using Full reads and Overwrite. |
| [**Step 2B. Incremental Append**](02B-build-and-run-incremental-append-etl.md) | Use a watermark and governed source-to-target identity to process only newly eligible inventory movements. Its three runs show the initial load, new source data, and a no-change run. |
| [**Step 2C. SCD1 and SCD2**](02C-build-and-run-scd-etl.md) | Send three complete Product Master snapshots through Full reads. Compare SCD1, which replaces changed values in the current record, with SCD2, which preserves prior versions as history. |

## Expected result

You can now identify every section of `02_pipeline`, know which cells to customize, and understand what FabricOps handles at the governed Read and Write boundaries. You are ready to apply the same scaffold in a working example.

**Next (recommended):** [Step 2A. Run the Full Refresh Demo](02A-full-refresh-demo.md)

**Other processing modes:** [Step 2B. Incremental Append](02B-build-and-run-incremental-append-etl.md) · [Step 2C. SCD1 and SCD2](02C-build-and-run-scd-etl.md)
