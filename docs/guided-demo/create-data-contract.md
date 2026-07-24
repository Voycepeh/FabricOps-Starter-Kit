# Step 5: Create the Data Contract and record steward sign-off

Return to `01_agreement` in the Governance workspace after Step 4 has validated the approved guardrails. This step creates the Data Contract that links governed catalogue tables to the Data Agreement and records steward sign-off.

Approval and promotion occur only after this contract is signed off. Do not promote the Development `02_pipeline` to Engineering Production before completing this step.

## What to do

1. Open `01_agreement` in the Governance workspace.
2. Reuse the active `CONFIG` and metadata routing from `00_env_config`.
3. Select the relevant tables from the Data Catalogue created by the Development pipeline runs.
4. Select the Data Agreement created in Step 1.
5. Create the Data Contract that links those catalogue tables to the Data Agreement.
6. Record the required data steward sign-off for promotion approval.

## Expected evidence

The configured metadata target receives Data Contract evidence that links the approved dataset, relevant catalogue tables, responsible agreement context, and steward sign-off. This approval context is what allows the validated `02_pipeline` to move to Engineering Production.

Previous: [Step 4: Rerun the Development pipeline with guardrails](run-pipeline-with-guardrails.md).

Next, continue to [Step 6: Promote the validated pipeline to Production](promote-to-production.md).

See also: [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md) and [List of Metadata Tables](../reference/metadata.md).
