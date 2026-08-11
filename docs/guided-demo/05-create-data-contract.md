# Step 5: Create the Data Contract and prepare for promotion

**Use `01_governance` to link the governed Data Catalogue to the Data Agreement through a Data Contract, then prepare the validated ETL workflow for promotion.**

## Before you begin

Confirm that:

- the relevant Data Agreement exists
- `02_pipeline` has produced the required Data Catalogue and Data Profiled evidence
- Guardrails have been defined and re-validated in Engineering Development

## What to do

1. Open `01_governance` in the Governance workspace.
2. Run `00_env_config`.
3. Select the relevant Data Steward records and Data Agreement.
4. Inspect the Data Catalogue and Data Profiled evidence written by `02_pipeline`.
5. Select the registered logical datasets discovered from the active environment.
6. Save the Data Contract membership linking those governed Data Catalogues to the Data Agreement.
7. Finalise the ETL contract and Governance sign-off needed for promotion and release management.

!!! note "Logical contract membership"

    Each agreement links once to each logical `metadata_table_key`. Engineering Development and Engineering Production use the same logical key, while their catalogue, profile, lineage, Guardrail, and other evidence remains stored as separate environment-specific observations.

## Expected result

You should now have:

- a Data Contract linked to the parent Data Agreement
- governed Data Catalogue membership recorded in the contract
- the approval context needed to promote the validated `02_pipeline`

**Previous:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)  
**Next:** [Step 6: Promote the validated pipeline to Production](06-promote-to-production.md)

See also: [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md) and [List of Metadata Tables](../reference/metadata.md).
