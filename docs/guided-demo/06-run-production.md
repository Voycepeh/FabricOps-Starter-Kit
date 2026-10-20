# Step 6. Run the pipeline in Production

### Before you begin

Complete [Step 5](05-activate-data-contract-and-promote.md) and use the promoted Production pipeline.

### Load the Production configuration

Run the Production copy of `00_env_config`:

```python
%run 00_env_config
```

The same logical store names now resolve to the Production Lakehouses, Warehouses, schemas, paths, and SQL endpoints.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run the promoted pipeline

Run the promoted `02A_full_refresh_demo` pipeline from start to finish.

</div>
</div>






Production runs the same tested workflow in the Production environment. It follows the same visible lifecycle used in Development:

```text
Read → Transform → Write
```

The same source reads, transformations, Guardrail checks, governed write logic, profiling, [Lineage](../reference/metadata/metadata_data_lineage.md), and [Source Observation](../reference/metadata/metadata_source_observation.md) flow run again against Production resources.

The key difference is Data Contract resolution:

* **Testing** explicitly selects eligible frozen candidates in any configured environment.
* **Live** requires the active frozen Data Contract for each governed `table_id`, in any configured environment.

The same Guardrail functions therefore enforce the Production-active definition, and [`orchestrate_write()`](../api/reference/orchestrate_write.md) uses the active governed Processing configuration for each target.

Run the `widget_pipeline()` selector cell to create a fresh widget, deliberately select **Live** for the whole pipeline and its eligible contracts, then build a new `EXECUTION_PLAN`. A previously built selector is locked; calling its `build_plan()` again reuses the existing plan. Pass that same plan to all three Reads and both Writes. Scheduled execution must call `widget_pipeline(interactive=False, execution_mode="live", ...)` explicitly. The environment only routes work; it never infers Live. All three sources and both targets need the active frozen versions prepared in Step 5.

### Check the two independent publications

Confirm both `writes["curated_orders_lakehouse"]["published"]` and `writes["customer_summary_warehouse"]["published"]` are true. Review the applicable Guardrail Results and inspect the persisted target values, including the configured Sensitive Data treatment on `curated_orders`.

If a contract is missing or more than one version is active, return to Governance and correct the selection for that exact `table_id`; do not bypass enforcement or create a Production draft to continue. If a blocking Guardrail fails, resolve the data or implementation issue and rerun. The two Writes are independent: if the second fails, the first target may already be published. See [Step 2A's publication boundary](02A-full-refresh-demo.md#configure-the-governed-writes).

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Grant direct consumer access

Once the governed Production output exists, consumers do not need a FabricOps exploration notebook to use it.

</div>
</div>



Grant the required access through the appropriate native Fabric path, such as Workspace roles, SQL endpoint grants, or OneLake security roles. Keep access scoped to the approved Production data the consumer needs.

Consumers can then use the standard Fabric experience that fits their work: connect a notebook to the permitted Lakehouse, query the Warehouse or SQL analytics endpoint, use SQL tooling, or connect another supported Fabric consumer. They should not need to recreate the Production engineering pipeline or use FabricOps readers merely to access an already-published table.

FabricOps remains relevant to the access boundary through its effective-access scanning and governance context. It does not need to own the consumer's exploration interface.

### Expected result

Engineering Production completes the validated pipeline workflow, publishes governed Production outputs using the active Data Contract, and approved consumers can reach those outputs through native Fabric access controls and interfaces.

**Next:** [Step 7. Publish governed data to a Fabric Data Agent](07-consume-production-data.md)
