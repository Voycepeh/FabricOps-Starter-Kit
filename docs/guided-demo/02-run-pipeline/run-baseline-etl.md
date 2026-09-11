# Unit 2: Run the baseline ETL

**Run the complete `02_pipeline` template once before adding Guardrails.**

This first execution writes the `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE` records that Governance uses in the next module.

## Before you begin

Complete [Step 0B: Set up the operating environment](../00B-run-environment-setup.md) and [Step 1: Create data stewards and a data agreement](../01-create-agreement.md).

Confirm that `00_env_config` defines the source, unified, product, and metadata stores required by your demo environment.

Upload the demo source files to the Source Lakehouse under `Files/DemoData/`, open `02_pipeline` in Engineering Development, attach the Fabric Environment used by `00_env_config`, and run the setup cells.

![Config](../../assets/02/Config.png)

## Run the ETL

The template executes the same visible workflow used throughout FabricOps:

```text
Environment → Data Contracts → Read → Transform → Write
```

At this stage, no Data Contract exists yet for the demo table. The Data Contracts section is still part of the template, but the baseline run continues without selected Guardrails so Engineering can first produce the Catalogue, Profiled, and Lineage metadata Governance needs.

Run the notebook end to end rather than manually reconstructing the framework lifecycle.

### Read

Use the source configuration already wired into the template. The demo can read Lakehouse files or tables and Warehouse tables or SQL results.

![Read CSV for Lakehouse](../../assets/02/Read_CSV_LH_DEMO.png)

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

    The pipeline is complete even though Guardrails have not been authored. Step 3 adds those governed expectations, and Step 4 reruns this same pipeline so the selected frozen Data Contract becomes the Development validation context.

## Expected result

You should now have one persisted governed target plus the metadata needed for the next governance step.

**Previous:** [Unit 1: Understand the template](understand-template.md)  
**Next:** [Unit 3: Configure sources](configure-sources.md)
