# Step 5. Activate Contracts and promote the notebook

Governance independently approves a portable notebook candidate; Engineering separately deploys the exact approved snapshot.

!!! important "Fabric acceptance remains pending"
    Governed execution is blocked until signed-in Fabric validation is complete. Promotion metadata and saved-code checks alone cannot establish execution-time code identity. Only the notebook is frozen; imported dependencies are not.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Activate the physical table Contracts

Choose an exact frozen definition for every approved source and target.

</div>
</div>

1. Use a Governance-authorized identity and the configured central Metadata Lakehouse.
2. Scope the notebook context to the **physical table workspace**, including any intentional cross-workspace source or target.
3. Open `widget_activate_data_contract(TABLE_ID, CONTRACT_ID, VERSION, workspace_id=PHYSICAL_WORKSPACE_ID)`, select the applicable exact effective Agreement, review the frozen payload and physical workspace, then explicitly confirm activation.
4. Repeat for every source and target. `METADATA_DATA_CONTRACT_ACTIVATION` stores these independent selections. The global frozen definition remains unchanged; authoring evidence workspace does not select activation scope.

??? info "Protection and independent versions"
    Active Contracts protect physical targets from Ungoverned writes, including logical aliases. Two physical workspaces can activate different versions of the same Table ID. Newly admitted runs adopt the current active Contract; existing admitted runs retain their exact captured versions.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Submit, independently approve and deploy

Transfer a complete immutable package across independent notebook sessions.

</div>
</div>

1. In Engineering, save the development notebook with one literal `setup_pipeline` call containing its stable Pipeline ID and `pipeline_mode="Dry Run"`. Save before execution so the verifier can capture the complete definition.
2. Execute the complete notebook through `finalize_pipeline(preview)`. Available saved-definition and execution claims persist in Engineering Files without publishing business data, Run rows, checkpoints, profiling or lineage.
3. Open `widget_deploy_pipeline(dry_run=preview)`, select the execution destination and export the complete JSON package. Saved source changes require another Dry Run. Download the file for explicit handoff.
4. In a separate Governance session, open `widget_activate_pipeline()`, paste the package JSON and import it. Inspect complete source/promoted notebooks, recorded Dry Run claims, tested versus proposed bindings, and independently resolved active Contract/Agreement policy. A digest identifies content; it does not prove claimed testing occurred.
5. Supply an independent review note and explicitly approve or reject. Decisions and accepted packages persist in `METADATA_PIPELINE_APPROVAL`. Approval creates no Engineering notebook and changes no Registry deployment.
6. In Engineering, open `widget_deploy_pipeline(pipeline_id=PIPELINE_ID)`, select the authoritative approval, review and explicitly deploy. FabricOps verifies exact approved bytes, creates a separate notebook, verifies full saved readback and conditionally commits a new active Registry version. Previous versions remain immutable. Exact retries recover the same promotion identity.

??? info "Rollback and restoration"
    Engineering can select a retained implementation and export a rollback or restoration request. Governance independently reviews that package and authorizes the operation. Rollback deploys a new auditable version; restoration preserves modified content before repairing the intended active version. Neither silently reactivates or rewrites an old Registry row.

??? info "Schedules and security limits"
    Same-workspace copies live in an organizational `Governed/` folder; folders confer no permissions. Engineers own schedules and explicitly rebind them to the returned new notebook ID. Promotion never moves schedules. Schedules targeting superseded notebooks must fail admission. Schedule-time changes alone do not need promotion; behavior changes do.

    Saved-definition checks have TOCTOU limits and cannot prove the identity of already executing code. Privileged users can bypass FabricOps and invoke Spark directly. Governance owns all central metadata. Restrict Engineering to its schema/Files writes and read-only Governance policy; schema permissions do not automatically secure Files.

### Expected result

`METADATA_PIPELINE_REGISTRY` retains an immutable per-workspace Pipeline version with a separate Governed notebook ID, snapshot pointers/hashes, exact Governance approval/submission references and reviewed bindings. **Governed admission remains blocked pending the [signed-in Fabric checklist](../maintainer/governed-pipeline-fabric-acceptance.md).** Do not treat green local tests as secured Fabric execution.

**Next:** [Step 6. Run Production](06-run-production.md)
