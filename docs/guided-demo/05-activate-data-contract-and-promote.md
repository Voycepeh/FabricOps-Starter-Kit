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

Contract definitions and versions are global, but activation is scoped to each physical workspace/table (or file source). If `02_pipeline` is cloned to another Engineering workspace, activate the exact required Contract versions for that workspace's physical sources and targets as well.

??? info "Protection and independent versions"
    Active Contracts protect physical targets from Ungoverned writes, including logical aliases. Two physical workspaces can activate different versions of the same Table ID. Newly admitted runs adopt the current active Contract; existing admitted runs retain their exact captured versions.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Submit, independently approve and deploy

Review saved submissions directly from the Metadata Lakehouse.

</div>
</div>

1. **Engineering:** save the development notebook with `PIPELINE_MODE = "Dry Run"`; FabricOps derives its identity from Fabric. Run it through `finalize_pipeline(pipeline)`. FabricOps automatically saves the submission in the Metadata Lakehouse.
2. **Governance:** run `widget_activate_pipeline()` and click **Refresh submissions**. Select the **Saved pipeline submission**, choose **Approve**, and click **Review submission**. Review the notebook and checks, enter a review note, tick the confirmation, and click **Save Governance decision**.
3. **Engineering:** beneath Finalize, click **Refresh approvals**, select that approval, and click **Review approved deployment**. Tick the deployment confirmation and click **Deploy approved notebook**. FabricOps creates the separate Governed notebook, archives its snapshot and records it in Registry.
4. **Engineering:** open the new notebook in the Engineering workspace's **Governed** folder and update your Fabric schedule or notebook activity to target it. Keep the development notebook in Dry Run mode.

The standard walkthrough can use one Engineering workspace for both Dry Run and governed execution. If you clone `02_pipeline` into another workspace, configure that workspace's `00_env_config`, repeat Step 4 validation there, repeat the applicable physical Contract activations above, and submit the clone as a new pipeline package for Governance approval. Pipeline approval is tied to the exact submission and Engineering workspace; it does not transfer with the clone.

There is no package download, upload or JSON paste. Governance reads the saved submission directly.

To reopen Engineering controls in the same kernel, rerun only `finalize_pipeline(pipeline)`. After a restart, rerun the Environment cell and call `finalize_pipeline()`; another Dry Run is not required just to deploy an existing approval.

For recovery, select a **Retained implementation**, choose **Restore the active notebook** or **Rollback through a new version**, and click **Submit recovery request**. Governance selects that saved request in the same widget and approves it; Engineering then applies the approval using step 3.

??? info "Rollback and restoration"
    Engineering selects a retained implementation and clicks **Submit recovery request**. Governance selects the saved request and independently reviews it and authorizes the operation. Rollback deploys a new auditable version; restoration preserves modified content before repairing the intended active version. Neither silently reactivates or rewrites an old Registry row.

??? info "Schedules and security limits"
    Same-workspace copies live in an organizational `Governed/` folder; folders confer no permissions. Engineers own schedules and explicitly rebind them to the returned new notebook ID. Promotion never moves schedules. Schedules targeting superseded notebooks must fail admission. Schedule-time changes alone do not need promotion; behavior changes do.

    Saved-definition checks have TOCTOU limits and cannot prove the identity of already executing code. Privileged users can bypass FabricOps and invoke Spark directly. Governance owns all central metadata. Restrict Engineering to its schema/Files writes and read-only Governance policy; schema permissions do not automatically secure Files.

### Expected result

`METADATA_PIPELINE_REGISTRY` retains an immutable per-workspace Pipeline version with a separate Governed notebook ID, snapshot pointers/hashes, exact Governance approval/submission references and reviewed bindings. **Governed admission remains blocked pending the [signed-in Fabric checklist](../maintainer/governed-pipeline-fabric-acceptance.md).** Do not treat green local tests as secured Fabric execution.

**Next:** [Step 6. Run the governed pipeline](06-run-production.md)

Processing is Engineering-owned. Review the exact read/write modes, read/write parameters, repartitioning and source-to-target associations in the submitted package. Any change requires a new Pipeline Activation approval. File source authorizations retain exact selectors, reader options and frozen Contract hashes; deployment remains blocked until a file orchestration boundary can enforce their Guardrails.
