# Step 5. Activate the tested pipeline and promote to Production

Run `finalize_pipeline()` after completing Testing in [Step 4](04-validate-frozen-data-contract.md). It publishes the final `METADATA_PIPELINE_RUN` and linked `METADATA_GUARDRAIL_RESULTS` for review. Activation requires complete successful Testing, frozen contracts for every participant, an effective Data Agreement and explicit Governance approval. Interactive diagnostics alone cannot activate a release.

## Review the affected release

1. Open `widget_activate_pipeline()` in `01_governance`. First use `setup_governance(target_workspace_id=...)` for the registered workspace being approved; its environment is shown automatically.
2. Select the successful Testing run, immutable pipeline version, exact effective Data Agreement.
3. Review participating tables, proposed contract versions and current writer ownership. When a shared table changes, include compatible successful Testing candidates for every affected active pipeline. Missing or failed tests and competing writers block approval.
4. Choose **Review complete release**. Inspect the current/proposed table mappings, affected pipelines and readiness report.
5. Confirm Governance approval and choose **Activate release** once. A stale review or metadata conflict requires refresh and another review.

The backend revalidates complete Testing and exact Data Contract and processing configuration identities. It publishes all selected pipeline configurations and table mappings in one `METADATA_ACTIVATION_STATE` revision. No individual contract activation or manual multi-pipeline switching is needed.

## Deploy and execute Live

When promoting to another workspace, deploy the validated notebook with a
centrally registered **Test** binding first. Run and finalize evaluation against
that workspace's approved physical resources, then have Governance select that
workspace and approve its exact successful run. Change the binding to **Live**
and start a new session. Frozen contract identities and versions are reused;
workspace approvals and physical bindings are validated separately. Neither DEV
nor PROD infers a mode or grants activation authority.


Engineering and Microsoft Fabric own source control, executable checksums, CI/CD and deployment. Deploy the tested notebook with Fabric or CI tooling separately. FabricOps requires no packaging files or deployment verification call. Activation does not deploy artifacts or publish business data. Test and approve each execution environment explicitly against its configured physical destinations; global Data Contract definitions are shared, so DEV and PROD can adopt different frozen versions without copying contracts.

Have Governance register this notebook binding as `Live`. `setup_pipeline()` resolves approved environment participants, contracts, configuration and destinations automatically. Run Read → Transform → Write → Finalize. Changed table identities, destinations, strategies or frozen contracts fail before publication. Call `finalize_pipeline()` after the entire workflow to record completion and release its reservation; stopped notebooks remain incomplete.

## Drain and cut over

A running Live plan pins its revision. Activation blocks affected changes until those runs finish; unrelated pipelines can continue. Metadata publication, notebook deployment and business writes are separate transactions. Crashed runs retain reservations until an operator confirms they stopped and performs a reviewed metadata repair.

See the [complete lifecycle, failure policy and limits](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#activate-deploy-and-run-unattended).

## Migrate existing metadata

Follow the [central registry migration procedure](00B-configure-environment-and-load-assets.md#migration-from-local-configuration). Existing approved manifests can be assigned explicitly to one workspace after stopped-workload verification and physical mapping checks. Immutable contract payloads, versions and approval history are preserved; additional workspaces require separate successful Testing and approval. No environment label grants inherited approval.

**Expected result:** one consistent approved environment revision with one table contract, at most one writer per table, and all affected pipelines tested together.
