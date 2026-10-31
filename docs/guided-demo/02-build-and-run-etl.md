# Step 2. Build a Pipeline

### Before you begin

1. Complete [Step 00B. Configure the Environment and load assets](00B-configure-environment-and-load-assets.md).
2. Download [`02_pipeline.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/notebooks/02_pipeline.ipynb) and import it into your Engineering Development workspace.
3. Keep `00_env_config.ipynb` beside the pipeline notebook and attach the same Fabric Environment used in Step 00B.

The template intentionally uses placeholder source and target names. Replace them with tables available in your workspace before running the Read or Write cells.

!!! note "Recommended first run: Ungoverned"
    Run the complete notebook once in **Ungoverned** mode, including `finalize_pipeline(pipeline)`. This publishes data and records observations that Governance can use when authoring Data Contracts. It does **not** approve or activate a contract.

    In Governance, author and freeze the required Contracts, use **Dry Run** to validate them where useful, and activate the exact versions for the target workspace. Then rerun the pipeline in **Governed** mode. Ungoverned execution cannot bypass an already-governed destination.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## The big picture

Learn the reusable notebook lifecycle, then replace the example source, transformation, and target with your own pipeline logic.

</div>
</div>

![FabricOps places governed Read and Write boundaries around project-owned PySpark](../assets/pipeline-boundaries-implementation.svg)

The notebook follows this sequence:

| Section | Responsibility |
| --- | --- |
| Environment | `setup_notebook()` loads configuration and resolves the caller's workspace environment. |
| Setup Pipeline | `setup_pipeline()` registers or recovers the pipeline identity and starts the selected execution mode. |
| Read | `orchestrate_read()` reads a source and runs applicable checks and profiling. |
| Transform | Your project-owned PySpark logic joins, filters, derives, aggregates, or selects data. |
| Write | `orchestrate_write()` checks and publishes the prepared DataFrame using the selected load strategy. |
| Finalize | `finalize_pipeline(pipeline)` records the outcome and releases Governed execution reservations. |

A successful Read or Write is not proof that the entire notebook completed. Always run Finalize after the pipeline work; use `finalize_pipeline(pipeline, failed=True)` when catching a project exception.

## 1. Set up the notebook and pipeline

Run the Environment cell first. For a shared configuration workspace, pass its ID to `setup_notebook()`:

```python
context = setup_notebook(
    # config_workspace_id="<configuration-workspace-id>",
)
```

Then run Setup Pipeline. The default `PIPELINE_ID = None` lets FabricOps register or recover this notebook's permanent pipeline UUID automatically. Retain an explicit UUID in source only when you need to promote the same pipeline identity across workspaces.

```python
PIPELINE_ID = None
PIPELINE_MODE = "Ungoverned"  # "Dry Run", "Ungoverned", or "Governed"

pipeline = setup_pipeline(
    pipeline_id=PIPELINE_ID,
    pipeline_mode=PIPELINE_MODE,
)
PIPELINE_ID = pipeline.pipeline_id
```

![Notebook after loading the shared FabricOps environment](../assets/02/Setup.png)

| Mode | Publishes target data? | Data Contract behavior |
| --- | --- | --- |
| `"Dry Run"` | No | Validates the selected frozen contract configuration where applicable; operational changes are not published. |
| `"Ungoverned"` | Yes | Runs without contract-dependent checks and records observations for Governance. It cannot write to a destination that is already governed. |
| `"Governed"` | Yes, when required checks pass | Resolves and enforces the activated contracts for the current workspace. |

Profiling is controlled by the active Data Contract profiling policy and execution triggers. Standard pipeline calls do not need manual profiling calls or a manually constructed execution plan.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## 2. Configure the Read

Read each source through `orchestrate_read()`. Keep the complete result in `sources` so later cells can use its DataFrame and retain the result details.

</div>
</div>

Initialize the source dictionary:

```python
sources = {}
```

Configure the example Read:

```python
source = orchestrate_read(
    store="Bronze",
    schema="demo",
    table_name="source_table",  # Replace with your source table.
    read_mode="full",
    query=None,
    dq_diagnostics="sample",
)
sources["source"] = source

display(sources["source"]["dataframe"].limit(10))
```

Change `store`, `schema`, and `table_name` to match the source. Use `read_mode="full"` for a complete read or `read_mode="incremental"` when implementing a watermark-based flow; the Incremental demo shows the required source-to-target configuration.

The result is a dictionary rather than just a DataFrame. Use the contained DataFrame in the transform:

```python
source_df = sources["source"]["dataframe"]
```

For another input, add a second Read block, save it under a distinct key such as `sources["products"]`, and use that DataFrame in your transformation. Only add sources that contribute to the target.

`dq_diagnostics` controls Data Quality failure detail: `"sample"` returns a sample, `"none"` keeps metrics only, and `"full"` returns all failed rows as a lazy DataFrame. Other strategy-specific settings are demonstrated in the relevant examples.

See the [Read and Load Strategies](../reference/read-and-load-strategies.md) reference and [Step 2B: Incremental Append](02B-build-and-run-incremental-append-etl.md).

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## 3. Write your PySpark transformation

Keep project-owned transformation logic between the governed Read and Write boundaries.

</div>
</div>

The template starts with an identity transformation:

```python
transformed_df = sources["source"]["dataframe"].select("*")

# Optional development inspection.
# display(transformed_df)
```

Replace this with your business logic: join DataFrames from multiple source entries, filter rows, derive columns, aggregate records, or select the target schema. FabricOps does not prescribe the transformation style.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## 4. Configure the Write

Publish the prepared DataFrame through `orchestrate_write()`.

</div>
</div>

Initialize the Write results dictionary:

```python
writes = {}
```

Configure the example target:

```python
writes["target"] = orchestrate_write(
    transformed_df,
    store="Silver",
    schema="demo",
    table_name="target_table",  # Replace with your target table.
    write_mode="overwrite",
    repartition_by=None,
    dq_diagnostics="sample",
)

display(writes["target"]["dataframe"].limit(10))
```

Choose the target store, schema, and table. The supported load strategies are `"overwrite"`, `"append"`, `"scd1"`, and `"scd2"`. Strategy-specific parameters such as SCD keys belong in `write_parameters`; see [Step 2C: SCD1 and SCD2](02C-build-and-run-scd-etl.md).

Read and Write previews show the DataFrames returned or submitted by those calls. To verify what was actually committed, inspect the persisted target table in Fabric after a successful persistent run. The returned Write dictionary also contains the load outcome, stage results, and available metrics.

### How repeated loads behave

FabricOps identifies an exact prepared batch before it writes the target. It materialises the prepared DataFrame, calculates an order-independent content fingerprint over its business columns, and binds that fingerprint to the target, source participants, schema, and processing strategy. It then checks the recorded batch receipt and the physical target evidence.

| Write result | Meaning | What FabricOps does |
| --- | --- | --- |
| **Loaded** | This prepared batch has not already been applied. | Runs the selected physical write and records its receipt. |
| **Already loaded** | The same prepared batch has a verified successful receipt for this target. | Skips the redundant physical write. No new rows are written by this attempt. |
| **Skipped — no new data** | An Incremental Read produced an empty scope. | Skips the write because there are no eligible rows to load. |

This applies to **Overwrite** as well as Append and the SCD strategies. An Overwrite request does not force a redundant physical overwrite when the exact same prepared batch has already been applied. If the source or transformation produces different business data, the fingerprint changes and FabricOps treats it as a new batch.

The batch check does not make the upstream Read or your PySpark transformation disappear: those steps still run to produce and identify the prepared input. It avoids repeating the physical target write after an exact prior batch is verified. **Rows loaded: 0** for **Already loaded** means zero rows were written by this attempt; it does not mean the target contains zero rows.

These two outcomes are different:

- **Already loaded**: FabricOps received a non-empty prepared batch, matched its exact content and target to a previously successful load, and verified the earlier write. The current attempt skips only the physical Write; it does not mean the incoming DataFrame was empty.
- **Skipped — no new data**: the current Incremental Read returned no eligible rows for this target, so there is nothing to write. No batch is loaded in this attempt.

In both cases, **Rows loaded: 0** means this Write attempt added no rows. The reason is shown by **Load status**.

With managed Sensitive Data token mappings, FabricOps uses the configured Governance store. Supply `existing_mapping` only when you manage a previously saved mapping yourself.

??? info "What happens inside Read and Write?"

    Read evaluates applicable Freshness, Schema, Grain, and Data Quality checks, then profiles eligible full-source data according to policy.

    Before publication, Write evaluates the configured Schema, Sensitive Data, Source Drift, Grain, and Data Quality checks. Only configured checks run. Governed execution stops when required checks fail or cannot execute.

    Dry Run prepares and validates the operation without publishing target data or persistent operational state. Successful persistent Writes publish the target and record the associated metadata at the relevant lifecycle boundaries. These separate Fabric operations are not one atomic transaction.

??? tip "A summary is missing in Microsoft Fabric"

    Confirm the call uses `orchestrate_read()` or `orchestrate_write()` and has not disabled verbose output. Fabric notebooks run the package installed in the attached Environment, which may differ from repository `main`. Check the installed package version and restart the notebook session after updating the Environment package.

## 5. Finalize and verify

After every Read, transformation, and Write has completed, run:

```python
pipeline_result = finalize_pipeline(pipeline)
```

Review the returned outcome and verify the persisted target when using Ungoverned or Governed mode. Dry Run returns a session-only summary. If your code catches an exception, finalize the run with `failed=True` so it is not recorded as a successful completion.

## Expected result

You can now identify the reusable notebook sections and know which values to customize. Keep project-owned PySpark in Transform and use the Read and Write orchestrators for the governed boundaries.

**Next:** Start with Full Refresh, then explore the stateful processing examples.

| Demo | What you will learn |
| --- | --- |
| [Step 2A. Full Refresh](02A-full-refresh-demo.md) | Read three retail sources, transform them with PySpark, and publish two targets using Full reads and Overwrite. |
| [Step 2B. Incremental Append](02B-build-and-run-incremental-append-etl.md) | Use a watermark to process newly eligible inventory movements across three runs. |
| [Step 2C. SCD1 and SCD2](02C-build-and-run-scd-etl.md) | Compare SCD1 current-state updates with SCD2 historical versioning. |
