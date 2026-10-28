# Step 5. Activate Data Contracts and deploy

Use Dry Run in [Step 4](04-validate-frozen-data-contract.md) to inspect frozen Data Contracts without persisting target or operational state. Activation is a separate Governance decision: it requires exact frozen contracts for every participant, an effective Data Agreement, complete accepted validation evidence and explicit approval. A Dry Run summary is session-only and does not activate a release.

## Review the affected release

1. Open `widget_activate_pipeline()` in the Governance notebook and explicitly select the pipeline and Engineering workspace.
2. Select the retained accepted validation evidence and exact effective Data Agreement.
3. Review participating tables, proposed contract versions and current writer ownership. When a shared table changes, include compatible accepted candidates for every affected active pipeline. Missing or failed evidence and competing writers block approval.
4. Choose **Review complete release**. Inspect the current/proposed table mappings, affected pipelines and readiness report.
5. Confirm Governance approval and choose **Activate release** once. A stale review or metadata conflict requires refresh and another review.

The backend revalidates the Data Contract and processing configuration identities. It publishes all selected pipeline configurations and table mappings in one `METADATA_PIPELINE_REGISTRY` revision. No individual contract activation or manual multi-pipeline switching is needed.

## Deploy and execute Governed

Engineering and Microsoft Fabric own source control, executable checksums, CI/CD and deployment. Deploy the reviewed notebook with Fabric or CI tooling separately. FabricOps requires no packaging files or deployment verification call. Activation does not deploy artifacts or publish business data. Approve each execution workspace explicitly against its configured physical destinations; global Data Contract definitions are shared, so DEV and PROD can adopt different frozen versions without copying contracts.

Run `setup_notebook()` in the destination workspace, retain the original UUID as `PIPELINE_ID`, and set `PIPELINE_MODE = "Governed"`. `setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode=PIPELINE_MODE)` resolves approved workspace participants, contracts, configuration and destinations automatically. Run Read → Transform → Write → Finalize. Changed table identities, destinations, strategies or frozen contracts fail before publication. Call `finalize_pipeline(pipeline)` after the entire workflow to record completion and release its reservation; stopped notebooks remain incomplete.

## Drain and cut over

A running Governed plan pins its revision. Activation blocks affected changes until those runs finish; unrelated pipelines can continue. Metadata publication, notebook deployment and business writes are separate transactions. Crashed runs retain reservations until an operator confirms they stopped and performs a reviewed metadata repair.

See the [complete lifecycle, failure policy and limits](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#activate-deploy-and-run-unattended).

## Initialize metadata

Run `setup_metadata_tables()` under controlled administration to initialize the consolidated Pipeline Registry and Pipeline Run table. Carry the saved Pipeline UUID into Production and approve that workspace explicitly. Registration never activates a pipeline.

**Expected result:** one consistent approved workspace revision with one table contract, at most one writer per table, and all affected pipelines reviewed together.

??? info "What activation checks"

    Registry selects exact accepted evidence for each pipeline and workspace. Run operations record the tables, frozen contract versions, physical destinations and read/write modes. Governed execution validates those facts before each orchestrator operation; contracts continue to control table rules, processing and profiling policies. No separate Definition/Configuration table or full argument snapshot is used. Approval does not scan future notebook cells or verify arbitrary transformation code.
