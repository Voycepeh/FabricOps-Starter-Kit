# Step 6. Run the pipeline in Production

### Before you begin

Complete [Step 5](05-activate-data-contract-and-promote.md) and use the promoted Production pipeline.

### Load the Production configuration

Confirm Governance registered this Production workspace and notebook ID with the approved Live binding:

```python
from fabricops_kit import setup_governance
context = setup_governance()
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

Live uses the **same tested workflow in the Production environment**, with contracts resolved exclusively from the approved environment Activated Pipeline manifest. It verifies the exact effective Agreement, Data Contract versions, current active approval and configured physical bindings before execution. Read/Write behavior must match the approved operation configuration.

Have Governance register this notebook binding as `Live` after Step 5. Headless setup resolves the currently approved environment revision automatically. There is no Live contract-selection widget or deployment-file selection. The environment name routes execution and never infers Live.

Pass the shared `EXECUTION_PLAN` to every operation and execute reads, transformations and writes inside `with EXECUTION_PLAN:`. Its exit records the complete outcome automatically, including read-only runs. The plan pins one activation revision; affected running executions must drain before a coordinated switch. Changed code, dependencies, contract identity, unsafe destinations or transformation settings fail safely. Permitted operational differences warn and are recorded.

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
