# Step 5: Create the draft Data Contract

Use `01_governance` to link a selected Data Agreement to the logical datasets it governs. Data Contract status remains draft in v0.2.0; signing, approval, and promotion are not implemented by this step.

## What to do

1. Open `01_governance` in the Governance workspace.
2. Run `00_env_config`, then select or create the relevant Data Steward records.
3. Select or create the Data Agreement.
4. Select registered logical datasets discovered from the active environment.
5. Save the draft Data Contract membership.

## Expected evidence

Each agreement links once to each logical `metadata_table_key`. Development and Production use the same logical key and do not require duplicate contract membership, while their catalogue, profile, lineage, guardrail, and other evidence remains stored and reviewed as separate environment-specific metadata observations.

Previous: [Step 4: Rerun the Development pipeline with guardrails](04-run-pipeline-with-guardrails.md).

Next, continue to [Step 6: Promote the validated pipeline to Production](06-promote-to-production.md). That later demonstration step does not make contract approval, signing, or automatic environment promotion part of the v0.2.0 Data Contract workflow.

See also: [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md) and [List of Metadata Tables](../reference/metadata.md).
