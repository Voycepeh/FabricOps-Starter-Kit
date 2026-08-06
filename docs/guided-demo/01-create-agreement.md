# Step 1: Create data stewards, establish an agreement, and later register contracts

Run `01_agreement` in the Governance workspace after Step 0 to capture steward and agreement context before pipeline execution. This notebook supports two governance stages: establish the Data Agreement first, then return later to register one or more Data Contracts after the relevant catalogue and validation evidence exists.

The agreement workflow uses `DATA_AGREEMENT_CONFIG` from `00_env_config` to control the agreement form fields and widget behaviour. Review the [configuration reference](../api/reference/data_agreement_config.md) when you need to understand or customise those settings.

## What to do

1. Reuse the `CONFIG` and `ENV` values from `00_env_config`.
2. Enter demo steward details, including role, contact, and effective dates.
3. Create a public-safe Data Agreement with a readable name, domain, recipient, business purpose, usage flags, and readiness notes.

### Stage A: Establish the Data Agreement

Create the overarching governance agreement between the accountable producer and consumer parties. The agreement defines the purpose, scope, ownership, permitted use, and governance conditions for sharing data. It does not yet define the exact tables or technical delivery promise.

### Stage B: Register the Data Contract

After the engineering and review workflow has produced catalogue and validation evidence, register a machine-readable Data Contract under the selected Data Agreement. In the current FabricOps metadata model, the contract links the parent agreement to authorised catalogue tables and their schema fingerprints. Related catalogue, enrichment, guardrail, profiling, and lineage metadata provide broader technical and quality context for those tables. One Data Agreement can govern multiple Data Contracts.

The visible widget configuration comes from `DATA_AGREEMENT_CONFIG` in `00_env_config`. Edit steward role options, visible columns, and custom fields there rather than hardcoding dropdown values in `01_agreement` or downstream notebooks.

## Expected evidence

The configured metadata target receives steward and agreement rows during Stage A. `02_pipeline` and `03_review` later produce catalogue, lineage, profile, and validation evidence. During Stage B, `01_agreement` registers Data Contract rows under the selected Data Agreement without changing the notebook execution order or evidence requirements.

| Intake step | Metadata written |
| ----------- | ---------------- |
| Data steward intake | `METADATA_DATA_STEWARD` rows with steward identity, lifecycle fields, optional custom fields, and audit columns. |
| Agreement intake | `METADATA_DATA_AGREEMENT` rows with agreement identity, selected steward context, usage fields, optional custom fields, and audit columns. |
| Contract registration | `METADATA_DATA_CONTRACT` rows linking the parent Data Agreement to authorised catalogue tables and their schema fingerprints, together with runtime audit fields. |
Previous: [Step 0: Set up the operating environment](run-environment-setup.md).

Next, continue to [Step 2: Run the first Development pipeline](run-pipeline.md).

See also: [List of Metadata Tables](../reference/metadata.md) and [List of Functions](../reference/index.md).
