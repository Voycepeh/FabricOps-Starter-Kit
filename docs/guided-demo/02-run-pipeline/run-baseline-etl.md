# Unit 2: Run the baseline pipeline

**Run the complete `02_pipeline` template once before adding Guardrails.**

This first execution writes the `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE` records that Governance uses in the next module.

## Before you begin

Complete [Step 0B: Set up the operating environment](../00B-run-environment-setup.md) and [Step 1: Create data stewards and a data agreement](../01-create-agreement.md).

Confirm that `00_env_config` defines the source, unified, product, and metadata stores required by your demo environment.

Confirm that Step 0B landed the raw demo files as these managed Fabric sources:

```text
Source Lakehouse:  demo.orders + demo.products
Product Warehouse: demo.order_history
```

Then open `02_pipeline` in Engineering Development, attach the Fabric Environment used by `00_env_config`, and run the Environment setup cells.

![Config](../../assets/02/Config.png)

## Run Read → Transform → Write

The template executes the same visible workflow used throughout FabricOps:

```text
Environment → target identity → Read → Transform → Write
```

At this stage, no Data Contract exists yet for the demo table. This is expected. **Do not run or interact with the Data Contract selection section in Step 2.** That reusable capability is first used by Engineering in Step 4, after Governance creates and freezes a version in Step 3.

Use the pre-wired blocks rather than reconstructing the framework lifecycle function by function. First identify the one governed target, then run the existing Read blocks, your project-specific Transform block, and the Write block.

??? info "Why identify the target before Read?"

    The governed target identity is needed by the pipeline's metadata and Source Observation context. Define it first; do not restructure the notebook.

### Read

Use the three source blocks already wired into the template:

1. a Lakehouse table Read for `demo.orders`,
2. a Lakehouse table Read for `demo.products`,
3. a Warehouse query over `demo.order_history`.

These are the managed sources created in Step 0B. Raw CSV, JSON, Parquet, and Excel reading belongs to that setup step, not this governed baseline run.

### Transform

Add project-owned Spark logic in the **User defined transformation** section.

![Transform DataFrame](../../assets/02/Transform_DF.png)

### Write

Write the transformed result to the configured governed target through the template.

![Write Lakehouse](../../assets/02/Write_LH.png)

Read the persisted target back and let the profiling and registration workflow capture the complete physical target.

![Read written Lakehouse table](../../assets/02/Read_Written_LH.png)

## What FabricOps records

The baseline run can write `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE` records alongside pipeline activity.

Step 3 reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED` to add `METADATA_ENRICHMENT`, author `METADATA_GUARDRAIL` records, and freeze the first Data Contract version for the governed `table_id`.

!!! info "No Guardrails yet is expected"

    The pipeline is complete even though Guardrails and a Data Contract have not been authored. Step 3 creates and freezes the first Data Contract version, and Step 4 reruns this same pipeline so the selected frozen version becomes the Development validation context.

## Expected result

You should now have one persisted governed target plus the metadata needed for the next governance step.

**Previous:** [Unit 1: Understand the template](understand-template.md)  
**Next:** [Unit 3: Configure sources](configure-sources.md)
