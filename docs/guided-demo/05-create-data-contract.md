# Step 5: Create the Data Contract and prepare for promotion

Use `01_governance` to create the Data Contract that links governed Data Catalogues to the Data Agreement. Then prepare the ETL contract and governance sign-off for promotion and release management.

## What to do

1. Open `01_governance` in the Governance workspace.
2. Run `00_env_config`, then select the relevant Data Steward records and Data Agreement.
3. Inspect the Catalogue and Profile evidence written by `02_pipeline` for the governed datasets.
4. Select the registered logical datasets discovered from the active environment.
5. Save the Data Contract membership linking those governed Data Catalogues to the Data Agreement.
6. Finalise the ETL contract and governance sign-off needed to prepare the validated workflow for promotion and release management.

## Expected evidence

Each agreement links once to each logical `metadata_table_key`. Development and Production use the same logical key and do not require duplicate contract membership, while their catalogue, profile, lineage, guardrail, and other evidence remains stored as separate environment-specific metadata observations.

Previous: [Step 4: Rerun the Development pipeline with guardrails](04-run-pipeline-with-guardrails.md).

Next, continue to [Step 6: Promote the validated pipeline to Production](06-promote-to-production.md).

See also: [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md) and [List of Metadata Tables](../reference/metadata.md).
