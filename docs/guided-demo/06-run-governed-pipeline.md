# Step 6. Run the governed pipeline

!!! important "Governed admission remains blocked"
    Complete the signed-in Fabric acceptance checklist before enabling Governed execution. The workflow below describes the intended validated runtime. A promoted Registry row does not override this gate. Imported dependencies are not frozen; saved-definition verification has TOCTOU limits.

### Before you begin

Complete [Step 5](05-activate-contracts-and-deploy.md) and use the separately deployed Governed notebook in the approved Engineering workspace.

### Load the Engineering workspace configuration

The Governed notebook calls `setup_notebook()`, which loads the current Engineering workspace's `00_env_config` automatically. To use a shared deployment, pass its workspace ID as `config_workspace_id` in the Setup Notebook block. The following `setup_pipeline(pipeline_mode="Governed")` reuses this configuration and resolves the approved pipeline. One Engineering workspace can host both the Dry Run and separately deployed Governed notebooks. A cloned pipeline in another workspace requires its own configuration, Step 4 validation, workspace-scoped Contract activations and Step 5 pipeline approval.

Logical store names resolve to the Lakehouses, Warehouses, schemas, paths, and SQL endpoints configured for that Engineering workspace.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run the promoted pipeline

Run the promoted `02A_full_refresh_demo` pipeline from start to finish.

</div>
</div>






The governed execution runs the reviewed workflow in its configured Engineering workspace:

```text
Read → Transform → Write
```

Source reads, transformations, Guardrail checks, governed write logic, profiling, [Lineage](../reference/metadata/metadata_data_lineage.md), and [Processing State](../reference/metadata/metadata_processing_state.md) run against the configured resources.

Governed uses the **same pipeline workflow in its approved Engineering workspace**, with Contracts resolved exclusively from activated workspace authority. It verifies the exact effective Agreement, Data Contract versions, active approval and configured physical bindings before execution. Read and Write behavior must match the activated operation configuration.

Run the **separate deployed Governed notebook** returned by Step 5, after tenant validation is complete. Do not switch the Dry Run notebook to Governed manually. Its frozen setup mode and exact behavior parameters are verified; ordinary parameter overrides cannot change approved behavior.

Use the same public calls: `setup_pipeline()`, `orchestrate_read()`, `orchestrate_write()` and `finalize_pipeline()`. A new start must use the currently active notebook version. Already admitted older versions may finish with their captured version and Contracts; each target table has one owning pipeline, and schedules must prevent overlapping runs. Stop that pipeline before changing its Contract Activation. Engineers explicitly rebind their schedules to the intended active item. Schedule timing alone may change without promotion.

### Check the two independent publications

Confirm both `writes["curated_orders_lakehouse"]["published"]` and `writes["customer_summary_warehouse"]["published"]` are true. Review the applicable Guardrail Results and inspect the persisted target values, including the configured Sensitive Data treatment on `curated_orders`.

If approval or a manifest Contract is missing, return to Governance and resolve the exact pipeline version; do not bypass enforcement or create an unapproved clone to continue. If a blocking Guardrail fails, resolve the data or implementation issue and rerun. The two Writes are independent: if the second fails, the first target may already be published. See [Step 2A's publication boundary](02A-full-refresh-demo.md#configure-the-governed-writes).

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Grant direct consumer access

Once the governed output exists, consumers can query it through PySpark, SQL, or other native Fabric interfaces.

</div>
</div>



Grant the required access through the appropriate native Fabric path, such as Workspace roles, SQL endpoint grants, or OneLake security roles. Keep access scoped to the approved data the consumer needs.

Consumers can then use the standard Fabric experience that fits their work: connect a notebook to the permitted Lakehouse, query the Warehouse or SQL analytics endpoint, use SQL tooling, or connect another supported Fabric consumer. They should not need to recreate the Production engineering pipeline or use FabricOps readers merely to access an already-published table.

FabricOps remains relevant to the access boundary through its effective-access scanning and governance context. It does not need to own the consumer's exploration interface.

### Expected result

The approved Engineering workspace completes the validated pipeline workflow, publishes governed outputs using the reviewed Pipeline Promotion, and approved consumers can reach those outputs through native Fabric access controls and interfaces.

**Next:** [Step 7. Publish governed data to a Fabric Data Agent](07-consume-governed-data.md)
