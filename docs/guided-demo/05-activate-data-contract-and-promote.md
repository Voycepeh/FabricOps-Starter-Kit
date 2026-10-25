# Step 5. Activate the tested pipeline and promote to Production

Run `finalize_pipeline(CONTRACTS)` after completing Testing in [Step 4](04-validate-frozen-data-contract.md). It commits the complete Test run and Guardrail results for review. Activation requires complete successful Testing, frozen contracts for every participant, an effective Data Agreement and explicit Governance approval. Interactive diagnostics alone cannot activate a release.

## Review the affected release

1. Open `widget_activate_pipeline()` in Governance in the same environment. It loads the Test outcomes committed by explicit pipeline finalization.
2. Select the successful Testing run, immutable pipeline version, exact effective Data Agreement.
3. Review participating tables, proposed contract versions and current writer ownership. When a shared table changes, include compatible successful Testing candidates for every affected active pipeline. Missing or failed tests and competing writers block approval.
4. Choose **Review complete release**. Inspect the current/proposed table mappings, affected pipelines and readiness report.
5. Confirm Governance approval and choose **Activate release** once. A stale review or metadata conflict requires refresh and another review.

The backend revalidates complete Testing and exact Data Contract and processing configuration identities. It publishes all selected pipeline configurations and table mappings in one `METADATA_PIPELINE_REGISTRY` revision. No individual contract activation or manual multi-pipeline switching is needed.

## Deploy and execute Live

Engineering and Microsoft Fabric own source control, executable checksums, CI/CD and deployment. Deploy the tested notebook with Fabric or CI tooling separately. FabricOps requires no packaging files or deployment verification call. Activation does not deploy artifacts or publish business data. Test and approve each execution environment explicitly against its configured physical destinations; global Data Contract definitions are shared, so DEV and PROD can adopt different frozen versions without copying contracts.

Set `PIPELINE_MODE = "Live"`. `setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode=PIPELINE_MODE)` resolves approved environment participants, contracts, configuration and destinations automatically. Run Read → Transform → Write → Finalize. Changed table identities, destinations, strategies or frozen contracts fail before publication. Call `finalize_pipeline(CONTRACTS)` after the entire workflow to record completion and release its reservation; stopped notebooks remain incomplete.

## Drain and cut over

A running Live plan pins its revision. Activation blocks affected changes until those runs finish; unrelated pipelines can continue. Metadata publication, notebook deployment and business writes are separate transactions. Crashed runs retain reservations until an operator confirms they stopped and performs a reviewed metadata repair.

See the [complete lifecycle, failure policy and limits](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#activate-deploy-and-run-unattended).

## Initialize metadata

Run `setup_metadata_tables()` under controlled administration to initialize the consolidated Pipeline Registry and immutable Definition/Run tables. Carry the saved Pipeline UUID into Production, run Test there, and approve that environment explicitly. Registration never activates a pipeline.

**Expected result:** one consistent approved environment revision with one table contract, at most one writer per table, and all affected pipelines tested together.
