# Step 5. Activate the tested pipeline and promote to Production

Complete [Step 4](04-validate-frozen-data-contract.md) and call `finalize_pipeline(plan)` after all operations. Only complete successful governed Testing qualifies.

## Review the affected release

1. Open `widget_activate_pipeline()` in `01_governance`. The resolved environment is shown automatically.
2. Select the successful Testing run, immutable pipeline version, exact effective Data Agreement.
3. Review participating tables, proposed contract versions and current writer ownership. When a shared table changes, include compatible successful Testing candidates for every affected active pipeline. Missing or failed tests and competing writers block approval.
4. Choose **Review complete release**. Inspect the current/proposed table mappings, affected pipelines and readiness report.
5. Confirm Governance approval and choose **Activate release** once. A stale review or metadata conflict requires refresh and another review.

The backend revalidates complete Testing and exact Data Contract and processing configuration identities. It publishes all selected pipeline configurations and table mappings in one `METADATA_ACTIVATION_STATE` revision. No individual contract activation or manual multi-pipeline switching is needed.

## Deploy and execute Live

Engineering and Microsoft Fabric own source control, executable checksums, CI/CD and deployment. Deploy the tested notebook with Fabric or CI tooling separately. FabricOps requires no packaging files or deployment verification call. Activation does not deploy artifacts or publish business data. Test and approve each execution environment explicitly against its configured physical destinations; global Data Contract definitions are shared, so DEV and PROD can adopt different frozen versions without copying contracts.

Set `PIPELINE_LIVE_ENABLED=True` through external parameters. Headless `setup_pipeline(execution_mode="live", pipeline_id=..., sources=..., targets=..., configuration={})` resolves the approved environment revision automatically. Run Read → Transform → Write, then call `finalize_pipeline(plan)`. Changed Data Contracts, transformation settings, table identities or physical destinations fail before publication. Permitted operational differences warn and are recorded.

## Drain and cut over

A running Live plan pins its revision. Activation blocks affected changes until those runs finish; unrelated pipelines can continue. Metadata publication, notebook deployment and business writes are separate transactions. Crashed runs retain reservations until an operator confirms they stopped and performs a reviewed metadata repair.

See the [complete lifecycle, failure policy and limits](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#activate-deploy-and-run-unattended).

## Migrate existing metadata

Run `setup_metadata_tables()` under controlled administration to create the new singleton authority. Existing individual approvals are not trusted or imported. Reconcile old environment-specific contract histories into one global lifecycle per table, rerun complete governed Testing and approve the affected release. No data or old metadata table is deleted automatically.

**Expected result:** one consistent approved environment revision with one table contract, at most one writer per table, and all affected pipelines tested together.
