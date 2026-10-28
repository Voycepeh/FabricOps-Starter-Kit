# Step 6. Run the pipeline in Production

### Before you begin

Complete [Step 5](05-activate-data-contract-and-promote.md) and use the promoted Production pipeline.

### Load the Production configuration

The promoted pipeline calls `setup_notebook()`, which loads the Production workspace's `00_env_config` automatically. To use a shared deployment, pass its workspace ID as `config_workspace_id` in the Setup Notebook block. The following `setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Governed")` reuses this configuration and resolves the approved pipeline.

The same logical store names now resolve to the Production Lakehouses, Warehouses, schemas, paths, and SQL endpoints.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run the promoted pipeline

Run the promoted `02A_full_refresh_demo` pipeline from start to finish.

</div>
</div>






Production runs the same tested workflow in the Production workspace. It follows the same visible lifecycle used in Development:

```text
Read → Transform → Write
```

The same source reads, transformations, Guardrail checks, governed write logic, profiling, [Lineage](../reference/metadata/metadata_data_lineage.md), and [Processing State](../reference/metadata/metadata_processing_state.md) flow run again against Production resources.

Governed uses the **same pipeline workflow in the Production workspace**, with contracts resolved exclusively from activated workspace authority. It verifies the exact effective Agreement, Data Contract versions, active approval and configured physical bindings before execution. Read and Write behavior must match the activated operation configuration.

Set `PIPELINE_MODE = "Governed"` after Step 5. Headless setup resolves the currently activated workspace revision automatically. Governed has no contract-selection widget or deployment-file selection. Workspace names route execution and never infer a mode.

Use the same public calls as every other mode: `setup_pipeline()`, `orchestrate_read()`, `orchestrate_write()` and `finalize_pipeline()`. The active session is shared internally; do not pass an execution-plan argument. Governed pins one activation revision, and affected running executions must drain before a coordinated switch.

### Check the two independent publications

Confirm both `writes["curated_orders_lakehouse"]["published"]` and `writes["customer_summary_warehouse"]["published"]` are true. Review the applicable Guardrail Results and inspect the persisted target values, including the configured Sensitive Data treatment on `curated_orders`.

If approval or a manifest contract is missing, return to Governance and resolve the exact pipeline version; do not bypass enforcement or create a Production draft to continue. If a blocking Guardrail fails, resolve the data or implementation issue and rerun. The two Writes are independent: if the second fails, the first target may already be published. See [Step 2A's publication boundary](02A-full-refresh-demo.md#configure-the-governed-writes).

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Grant direct consumer access

Once the governed Production output exists, consumers can query it through PySpark, SQL, or other native Fabric interfaces.

</div>
</div>



Grant the required access through the appropriate native Fabric path, such as Workspace roles, SQL endpoint grants, or OneLake security roles. Keep access scoped to the approved Production data the consumer needs.

Consumers can then use the standard Fabric experience that fits their work: connect a notebook to the permitted Lakehouse, query the Warehouse or SQL analytics endpoint, use SQL tooling, or connect another supported Fabric consumer. They should not need to recreate the Production engineering pipeline or use FabricOps readers merely to access an already-published table.

FabricOps remains relevant to the access boundary through its effective-access scanning and governance context. It does not need to own the consumer's exploration interface.

### Expected result

Engineering Production completes the validated pipeline workflow, publishes governed Production outputs using the approved Activated Pipeline manifest, and approved consumers can reach those outputs through native Fabric access controls and interfaces.

**Next:** [Step 7. Publish governed data to a Fabric Data Agent](07-consume-production-data.md)
