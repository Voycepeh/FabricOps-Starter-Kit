# Step 5. Activate Contracts and promote the notebook

Review exact physical Contract bindings and a completed manual Dry Run before creating a separate Governed notebook.

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
3. Open `widget_activate_data_contract(TABLE_ID, CONTRACT_ID, VERSION, workspace_id=PHYSICAL_WORKSPACE_ID)`, review the frozen payload and workspace, then explicitly confirm activation.
4. Repeat for every source and target. `METADATA_DATA_CONTRACT_ACTIVATION` stores these independent selections. The global frozen definition remains unchanged; authoring evidence workspace does not select activation scope.

??? info "Protection and independent versions"
    Active Contracts protect physical targets from Ungoverned writes, including logical aliases. Two physical workspaces can activate different versions of the same Table ID. Newly admitted runs adopt the current active Contract; existing admitted runs retain their exact captured versions.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Review and promote the manual Dry Run

Create a separate versioned notebook using destination workspace configuration.

</div>
</div>

1. Save the development notebook with one literal `setup_pipeline` call containing its stable Pipeline ID and `pipeline_mode="Dry Run"`. Save before execution so the verifier can retrieve the saved definition.
2. Manually execute the complete notebook through `finalize_pipeline(preview)`. Dry Run retains its review in memory and makes no durable Run, checkpoint, profiling, lineage or Registry mutations.
3. In the same kernel, with a Governance-authorized identity, call `widget_activate_pipeline(dry_run=preview)`. Opening it without a session is an inspection-only view.
4. Select the destination execution workspace and exact effective Agreement where applicable. Cross-workspace data operations require an exact effective Agreement. Click **Review promotion**. Inspect the full notebook, every operation, exact physical workspace/item/kind/schema/table binding and selected frozen Contracts.
5. Explicitly confirm the review, then click **Promote notebook**. FabricOps writes and verifies immutable full snapshots, creates a distinct Governed notebook, checks saved executable content, then atomically switches Registry authority using the reviewed expected active version. Previous versions remain.
6. Retain the returned review object and promotion ID if a request acknowledgement is lost. Inspect staged artifacts before retrying. Staging failure never deactivates the old version.

??? info "Schedules and security limits"
    Same-workspace copies live in an organizational `Governed/` folder; folders confer no permissions. Engineers own schedules and explicitly rebind them to the returned new notebook ID. Promotion never moves schedules. Schedules targeting superseded notebooks must fail admission. Schedule-time changes alone do not need promotion; behavior changes do.

    Saved-definition checks have TOCTOU limits and cannot prove the identity of already executing code. Privileged users can bypass FabricOps and invoke Spark directly. Restrict Governance writes and immutable archives using actual tenant permissions.

### Expected result

`METADATA_PIPELINE_REGISTRY` retains an immutable per-workspace Pipeline version with a separate Governed notebook ID, snapshot pointers/hashes and reviewed bindings. **Governed admission remains blocked pending the [signed-in Fabric checklist](../maintainer/governed-pipeline-fabric-acceptance.md).** Do not treat green local tests as secured Fabric execution.

**Next:** [Step 6. Run Production](06-run-production.md)
