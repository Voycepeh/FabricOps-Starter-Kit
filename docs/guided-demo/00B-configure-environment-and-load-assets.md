# 0B. Load and configure the Guided Demo assets

### Before you begin

Complete [Step 0A](00A-prepare-fabric-artifacts.md) before importing and configuring the demo assets.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Download and import the [FabricOps notebook templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)

Download the current notebook templates from the FabricOps repository:

</div>
</div>


Import the two reusable notebooks:

| Notebook | Where it goes now |
| --- | --- |
| `01_governance.ipynb` | Governance workspace |
| `02_pipeline.ipynb` | Engineering Development workspace |

In Fabric, open the target workspace, choose **Import notebook**, and upload the downloaded `.ipynb` file.

After importing the notebooks, the two required workspaces should now look like this.

![Governance workspace assets](../assets/00B/Governance_Assets.png)

The Governance workspace contains the `metadata` Lakehouse, its published Fabric Environment and `01_governance`.

![Engineering Development workspace assets](../assets/00B/Engineering_Assets.png)

The Engineering Development workspace contains `bronze`, `silver`, `gold`, the approved Fabric Environment, the reusable `02_pipeline`, and the three demo notebooks.

Consumers can use SQL or other native Fabric interfaces directly. Project-specific consumer notebooks use native Fabric IO or public FabricOps IO with an explicit context and existing Production permissions; no governed pipeline is required.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Open all the notebooks and set the Fabric Environment

Attach the shared Fabric Environment to the imported notebooks before running them.

</div>
</div>

Open each imported notebook and make sure it uses the Fabric Environment created in 0A that contains the FabricOps custom library.

1. Open the notebook.
2. In the notebook toolbar, make sure the runtime is set to **PySpark (Python)**.
3. Beside it, open the **Environment** dropdown and choose **Change environment**.
4. Select the Environment created for that workspace in 0A, where the FabricOps `.whl` was uploaded as a custom library.
5. Repeat this for every imported notebook in Governance, Engineering Development, and Consumer.

![Set the notebook Environment](../assets/00B/fabric-example-set-notebook-environment.png)

![Choose the workspace-specific Fabric Environment](../assets/00B/Environment_Selection.png)

If you are a member of several Fabric workspaces, the Environment picker may show Environments from more than one workspace. For this Guided Demo, choose the centrally published Environment when compatible; otherwise use its centrally managed equivalent.

Use the same FabricOps wheel version across the workspace-specific Environments so the notebooks run against a consistent package version.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Central Workspace Registry

Governance administrators configure the shared registry once; engineers import `02_pipeline`.

</div>
</div>

1. Create one schema-enabled **Metadata Lakehouse** in the Governance Workspace.
2. In controlled deployment tooling, build the FabricOps wheel with a reviewed locator:

    ```json
    {
      "governance_workspace_id": "<governance-workspace-uuid>",
      "metadata_item_id": "<metadata-lakehouse-uuid>",
      "governance_schema": "governance",
      "engineering_schema": "engineering"
    }
    ```

    ```bash
    python scripts/build_governed_wheel.py --bootstrap bootstrap.json --output dist-governed
    ```

    The locator is packaged inside the wheel. The public wheel is deliberately
    unconfigured and fails closed. Notebook globals, environment variables and
    pipeline parameters cannot redirect the registry. Protect the build, wheel,
    Environment publication and deployment identities through native Fabric and
    source-control permissions. The locator contains identities, not credentials.

3. Publish this wheel in the centrally managed Fabric Environment. In a Governance
   administrator notebook initialize the shared tables with
   `setup_metadata_tables(spark=spark, raise_on_failure=True)`. Initial provisioning
   uses the pinned locator and verifies the runtime Governance Workspace; it does
   not require an existing registration. Initialization is additive and retains
   historical tables and records.
4. Publish a complete registration for each workspace, using `register_workspace`:

    ```python
    from fabricops_kit import register_workspace

    registration = {
        "workspace_id": "<engineering-workspace-uuid>",
        "display_name": "Engineering Development Team A",
        "environment": "DEV",  # DEV, TEST or PROD; administrators select this.
        "status": "active",
        "resources": {
            name: {
                "workspace_id": workspace_id,
                "item_id": item_id,
                "kind": kind,
                "schema_enabled": True,
                "schema": schema,
                **({"item_name": physical_name} if kind == "warehouse" else {}),
            }
            for name, workspace_id, item_id, kind, schema, physical_name in [
                ("Bronze", "<engineering-workspace-uuid>", "<bronze-item-uuid>", "lakehouse", "dbo", None),
                ("Silver", "<engineering-workspace-uuid>", "<silver-item-uuid>", "lakehouse", "dbo", None),
                ("Gold", "<engineering-workspace-uuid>", "<gold-item-uuid>", "warehouse", "dbo", "Gold"),
                ("Metadata", "<governance-workspace-uuid>", "<metadata-lakehouse-uuid>", "lakehouse", "governance", None),
            ]
        },
        "notebooks": {
            "<runtime-notebook-uuid>": {"pipeline_id": "orders", "mode": "Test"}
        },
        "settings": {"audit_timezone": "UTC"},
    }
    registry_token = register_workspace(registration, expected_token="initial", spark_session=spark)
    ```

    Read and review the current registry token before subsequent changes; the
    returned token may be used for the next reviewed registration. Stale tokens
    fail closed. Get workspace/item/notebook IDs from the Fabric portal URL.
    IDs in engineering notebooks are obtained from `notebookutils.runtime.context`.
    Register every imported demo notebook ID under `notebooks` with its own stable
    pipeline ID. For normal Production execution, register the deployed notebook IDs as `Live`.
    Test versus Live is an explicit registered policy in every workspace; neither
    DEV nor PROD labels infer or restrict the execution mode. Additional workspaces
    can share the same deployment environment without sharing approvals.

5. In `01_governance`, call
   `setup_governance(target_workspace_id="<registered-engineering-workspace-uuid>")`
   before the existing Steward, Agreement, Contract and Activation widgets.
   Selecting a target is an administrative operation restricted to the pinned
   Governance Workspace. In engineering, call `pipeline = setup_pipeline()` and
   finish with `finalize_pipeline()`. `00C_demo_setup` initializes its registered
   DEV workspace without starting a pipeline before exercising independent IO.

### Fabric Environment publication and reuse

Create the Environment item in Governance, upload the administrator-built wheel
and compatible dependencies as custom libraries, select the supported Spark
runtime and publish. Grant engineering identities permission to use the published
item while restricting edit/publish access to administrators. Attach it through
the notebook Environment picker, or have a workspace administrator set the Spark
default Environment in workspace settings. FabricOps Python does not change those
workspace settings.

Cross-workspace Environment attachment requires compatible capacity and network
security settings. Where sharing is unavailable, centrally publish equivalent
Environment items with the same approved wheel and pinned locator. These items
do not hold separate authoritative configuration. See Microsoft's
[Environment configuration requirements](https://learn.microsoft.com/en-us/fabric/data-engineering/create-and-use-environment).

### Security boundaries

| Identity | Governance tables | Engineering metadata | Business resources |
| --- | --- | --- | --- |
| Governance administrator | Manage registry, contracts and approvals | Provision, inspect and recover | Only necessary administrative access |
| Engineering execution | Read approved configuration/contracts | ReadWrite on execution tables only | Explicit approved Bronze/Silver/Gold permissions |
| Consumer | Approved metadata reads | No execution writes required | Approved Production reads |

Keep governance and engineering ownership schemas in **one** Lakehouse; these are
not DEV and PROD schemas. Use OneLake security object-scoped **ReadWrite** on
engineering tables and Read on governance tables. Do not grant engineering
Contributor, Member or Admin in Governance: broader grants bypass table scoping.
Verify the effective identity, table permissions, cross-workspace routing and
network policies in your tenant before activation. If scoped writes are unavailable,
do not substitute broad Governance write access; this direct-write deployment is
not supported securely until the necessary platform capability is available.
See [OneLake access control](https://learn.microsoft.com/en-us/fabric/onelake/security/data-access-control-model).

`METADATA_ACTIVATION_STATE` holds governance decisions;
`METADATA_EXECUTION_STATE` holds reservations and a persistent cutover lock.
Activation and reservation changes serialize through that lock. An interrupted
cutover fails closed. There is no timeout that proves Spark stopped: administrators
must verify native Fabric jobs stopped, inspect the last confirmed authority and
reservations, then recover the execution snapshot using its reviewed CAS token.
Never blindly unlock or expire running reservations.

Python validation prevents accidental misrouting in the supported workflow; it
cannot sandbox arbitrary notebook code. Native Fabric permissions must prevent
DEV identities from writing Production data or modifying governance decisions.
Execution records are operational metadata, not cryptographically signed proof
against an identity already authorized to edit them.

### Migration from local configuration

1. Back up the Metadata Lakehouse and retain the previous approved wheel for rollback.
   Stop and verify native Fabric executions, drain reservations, and disable **all**
   registrations before metadata migration. An old authority with outstanding
   reservations fails closed until administrators verify stopped runs and reconcile it.
2. Provision the two new singleton tables and additive engineering scope columns
   with `setup_metadata_tables`. No frozen payloads or existing IDs are rewritten.
3. Use `migrate_workspace_config(old_config, assignments=[...])` to preview explicit
   assignments containing `legacy_environment`, `workspace_id`, `display_name`,
   `environment`, `status="inactive"` and `notebooks`. Review and publish each
   registration. Existing Warehouse names fall back to their former logical keys;
   review physical `item_name` before publishing. Existing Metadata mappings must
   already point to the single pinned Lakehouse; mismatches require an explicit
   administrator data consolidation before registering them.
4. In Governance, read and review the activation/reservation token using the
   administrative metadata context. Call `migrate_workspace_metadata` with the
   exact `legacy_environment`, receiving `workspace_id`, reviewed `expected_token`,
   `workloads_stopped=True` and `spark_session=spark`. One old environment may be
   assigned to **one** workspace. Other workspaces need their own Testing and
   activation. The migration verifies approved physical resource IDs, assigns
   unscoped engineering rows, retains their original environment labels in
   `_legacy_environment_name`, preserves immutable manifests and contract versions,
   and moves active decisions into the receiving workspace scope. The old scope
   retains approval history and a migration destination marker.
5. Migration is idempotent per table, not a cross-table transaction. Keep all
   registrations inactive until every step is confirmed; rerun interrupted table
   updates with the reviewed state. An interrupted authority cutover requires
   administrator lock recovery first. Verify historical counts, contract hashes,
   mappings, manifests and run outcomes against the backup. After verification, activate a DEV registration for a controlled Test smoke run,
   then validate and activate Production with actual Fabric ACLs before resuming normal jobs.
6. Replace `%run 00_env_config` and manual ENV selection with central setup. Remove
   notebook globals and parameters that override configuration. Existing optional
   `pipeline_id`/`pipeline_mode` arguments only assert the registered binding;
   mismatches raise clear errors. `setup_notebook()` is deprecated, while explicit
   FrameworkConfig contexts remain supported for independent public IO and
   administrative migration. Do not use them to bypass the governed lifecycle.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Download the demo data

Download the supplied demo files from: [FabricOps DemoData](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData)

</div>
</div>


Download the **entire DemoData folder**. Every retained file has an explicit Guided Demo owner:

| Demo asset | When it is used |
| --- | --- |
| `orders.csv`, `orders.json`, `orders.parquet`, `orders.xlsx` | 0C uses these equivalent 120-row files to demonstrate the FabricOps file readers. |
| `products.csv` | 0C seeds `bronze.demo.products`. |
| `order_history.csv` | 0C seeds `gold.demo.order_history` and demonstrates Warehouse reads. |
| `inventory_day1.csv`, `inventory_day2.csv` | Step 2B stages the inventory batches; Day 3 intentionally has no file. |
| `products_day1.csv`, `products_day2.csv`, `products_day3.csv` | Step 2C overwrites Bronze with each complete Product Master snapshot. |

Also download the ready-to-run pipeline demos from [FabricOps DemoData](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData):

| Demo notebook | Where it goes now |
| --- | --- |
| `02A_full_refresh_demo.ipynb` | Engineering Development workspace |
| `02B_incremental_append_demo.ipynb` | Engineering Development workspace |
| `02C_scd_demo.ipynb` | Engineering Development workspace |
| `00C_demo_setup.ipynb` | Engineering Development workspace |


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Upload the demo data

Upload the downloaded demo files to the Bronze Lakehouse and the demo notebooks into the engineering workspace.

</div>
</div>

1. Open the **Engineering Development** workspace.
2. Open the `bronze` Lakehouse created in 0A.
3. Under **Files**, create a subfolder named `Demo`.
4. Upload the **entire downloaded DemoData folder contents** into that folder.

![Upload the packaged demo files into Bronze Files/Demo](../assets/00B/Demo_Files.png)

At this point, stop. Do not create the managed source tables manually in 0B.

The next setup notebook demonstrates the FabricOps I/O helpers and prepares the original managed tables used by the Step 2A Full Refresh demo. Steps 2B and 2C stage their own source tables from the uploaded files.

### Expected result

The demo notebooks, Fabric Environment configuration, metadata tables, and demo files are ready for the next preparation step.

**Next:** [0C. Prepare the demo data with FabricOps I/O](00C-prepare-demo-data-with-fabricops-io.md)
