# Step 5. Activate the tested pipeline and promote to Production

Complete [Step 4](04-validate-frozen-data-contract.md), including explicit finalization after all declared Reads and Writes.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Approve the exact whole pipeline

Return to `01_governance` and open [`widget_activate_pipeline()`](../api/reference/widget_activate_pipeline.md).

</div>
</div>

Select a complete successful Testing candidate. Expand every source/target contract and rule, executable/dependency identity, processing configuration, operation evidence and Guardrail diagnostics. Review the warnings about permissions, publication transactions and concurrency that Testing cannot exercise. Select the exact currently effective Data Agreement and pipeline name/version, provide the exported tested notebook, then review and explicitly confirm Governance approval.

Keep every project transformation setting in `PROJECT_CONFIGURATION`. All its keys, including `schema`, `store` and `table_name`, contribute to exact candidate identity. Nested Read/Write parameters also retain these keys; only the explicit top-level orchestration routing arguments are separate physical bindings.

The service validates all requirements independently of the widget. Bootstrap, missing operations, failed persistence, changed code/contracts/configuration, blocking diagnostics, partial tests and isolated passing rules cannot authorize activation. The full 02A demo produces **one whole-pipeline approval** covering three inputs and two outputs.

Contracts remain immutable and reusable after **Draft → Frozen**. `METADATA_ACTIVATED_PIPELINE` links the exact Agreement, successful Testing run and manifest. Version contents are immutable; only an explicit switch/deactivation changes the active version. There is at most one active version per stable logical pipeline. Concurrent/stale changes fail and must be reviewed again; do not blindly retry activation.

Headless Governance uses the same service:

```python
from fabricops_kit import activate_pipeline
approved = activate_pipeline(
    testing_run_id=TESTING_RUN_ID, candidate_fingerprint=TESTED_FINGERPRINT,
    pipeline_name="Orders", pipeline_version="1",
    agreement_id=AGREEMENT_ID, agreement_version=AGREEMENT_VERSION,
    executable_path=EXPORTED_TESTED_NOTEBOOK,
    governance_confirmed=True, spark_session=spark,
)
```

An existing active version requires `expected_active_id` for an explicit switch. `set_pipeline_active()` switches or deactivates an existing immutable version with the same confirmation and concurrency gate. Activation neither deploys artifacts nor publishes business data.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Package, deploy and verify

Promote the unchanged tested notebook together with its exact approved definitions; keep physical bindings in external configuration.

</div>
</div>

In the approval environment, package deterministic approved metadata and the tested executable into an explicit deployment directory:

```python
from fabricops_kit import package_activated_pipeline
package_activated_pipeline(
    approved["activated_pipeline_id"], destination=PACKAGE_DIRECTORY,
    executable_path=EXPORTED_TESTED_NOTEBOOK, spark_session=spark,
)
```

Deploy the notebook with your Fabric Deployment Pipeline or normal CI tooling, and copy the package directory alongside it to a shared mounted durable location. FabricOps does **not** assume that Deployment Pipelines copy metadata rows. The approved manifest contains the exact frozen definitions; the configured Governance authority environment must remain reachable to verify active approval and the effective Agreement. The current notebook and deployed package are verified separately so an unchanged sidecar cannot hide changed running code.

![Select the pipeline artifact for Production](../assets/05/DeploymentPipeline.png)

![Confirm the Fabric deployment](../assets/05/Deployment.png)

In the destination environment, verify explicit bindings after deploying the artifact:

```python
from fabricops_kit import verify_pipeline_deployment
verify_pipeline_deployment(
    deployment_path=DEPLOYMENT_DIRECTORY, authority_environment="dev",
    sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS,
    spark_session=spark,
)
```

This fetches the actual deployed Fabric notebook definition and compares its executable identity with the approved manifest before writing `deployment.json` for the configured workspace, notebook, stores and participants. A changed notebook or unavailable definition export leaves the binding file untouched. It does not activate a version, select Live or publish data. `approved.json` and `executable.bin` remain deterministic approved artifacts. Bindings are outside portable identity. Store endpoint, workspace/item, schema, participant and role mismatches are rejected. A missing approval, definition, export permission or dependency fails closed.

### Save the exact Live selection

Select the activated version once in the destination pipeline notebook:

```python
from fabricops_kit import setup_pipeline
plan = setup_pipeline(
    execution_mode="live", pipeline_id=PIPELINE_ID,
    sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS,
    configuration=PROJECT_CONFIGURATION, deployment_path=DEPLOYMENT_DIRECTORY,
    activated_pipeline_id=approved["activated_pipeline_id"], spark_session=spark,
)
```

Subsequent manual and scheduled calls omit `activated_pipeline_id` and reuse the durable environment selection without UI or human input. A saved selection never switches silently. For an intentional version change, deploy/verify its artifacts and select it explicitly with `replace_selection=True` where a different selection already exists.

For the canonical notebooks, set `PIPELINE_LIVE_ENABLED=True`, `PIPELINE_DEPLOYMENT_PATH` and the one-time `PIPELINE_SELECT_ACTIVATED_VERSION` in `00_env_config` or notebook parameters. Remove the one-time version parameter after selection. Keep the tested notebook source unchanged; set `PIPELINE_CONTRACT_TESTING=True` externally to return to Testing. Default unattended Bootstrap remains for initial projects.

### Migrate existing metadata

1. Stop affected schedules and back up the configured metadata. Export the old contract rows, including `is_active`, Agreement IDs and versions, to an external audit file before dropping legacy fields. Keep frozen `contract_payload_json` unchanged.
2. Run `setup_metadata_tables()` with the configured Metadata store. It creates `governance.METADATA_ACTIVATED_PIPELINE` and adds nullable `engineering.METADATA_PIPELINE_RUN.activated_pipeline_id` through the existing additive migration behavior. Review every returned setup result before continuing.
3. Remove the legacy top-level `agreement_id`, `agreement_version` and `is_active` columns from `METADATA_DATA_CONTRACT` using your Lakehouse schema migration procedure. Delta column dropping requires column mapping and compatible reader/writer protocol versions; validate that upgrade in a non-production copy first. The new canonical schema and writers do not use these fields or provide compatibility aliases.
4. Rerun complete Testing with the new engine and every exact frozen contract. This also applies when upgrading an existing Activated Pipeline: the engine source hash changes, so previous approvals cannot authorize the upgraded engine. Earlier per-contract activations and older run snapshots lacking full operation configuration never become Activated Pipeline approval automatically.
5. Explicitly approve, package, deploy/verify, save the exact Live selection and re-enable schedules. Keep historical release snapshots unchanged.

??? info "Exact Delta column-drop commands after backup"

    Resolve the configured Metadata Lakehouse root and Governance schema; do not
    use an attached/default Lakehouse shortcut. After testing reader compatibility,
    run these maintenance commands against that explicit configured contract path:

    ```sql
    ALTER TABLE delta.`<configured-Metadata-root>/Tables/<configured-governance-schema>/METADATA_DATA_CONTRACT`
    SET TBLPROPERTIES (
      'delta.columnMapping.mode' = 'name',
      'delta.minReaderVersion' = '2',
      'delta.minWriterVersion' = '5'
    );
    ALTER TABLE delta.`<configured-Metadata-root>/Tables/<configured-governance-schema>/METADATA_DATA_CONTRACT`
    DROP COLUMNS (agreement_id, agreement_version, is_active);
    ```

    Preserve any already higher protocol versions. Do not edit frozen payload JSON
    or translate old per-contract active flags into pipeline approval. Keep the
    exported legacy linkage file outside the current canonical metadata schema.

??? info "What remains a real Fabric check"

    Local tests simulate Fabric transport and activation transactions. Confirm native Delta Serializable conflict handling for concurrent first activation/switching, actual notebook definition export permissions and format, unchanged executable export/import identity, durable shared deployment files, store bindings, repeated scheduled Live, Read-only Live, Warn/Block and partial-publication recovery in Fabric. Failed Live never falls back to Bootstrap. Business publication, diagnostics and run snapshots remain separate transactions.

### Expected result

One exact tested whole pipeline is approved, its immutable manifest and definitions are packaged beside the deployed executable, bindings are verified, and the destination saves that exact version for unattended Live.

**Next:** [Step 6. Run the pipeline in Production](06-run-production.md)
