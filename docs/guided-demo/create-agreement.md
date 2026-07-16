# Create Agreement

Run `01_agreement` after environment setup to capture steward and agreement context before pipeline execution. This notebook gives later technical evidence an accountable owner, business purpose, and approved usage context.

## What to do

1. Reuse the `CONFIG` and `ENV` values from `00_env_config`.
2. Enter demo steward details, including role, contact, and effective dates.
3. Create a public-safe data agreement with a readable name, domain, recipient, business purpose, usage flags, and readiness notes.
The visible widget configuration comes from `DATA_AGREEMENT_CONFIG` in `00_env_config`. Edit steward role options, visible columns, and custom fields there rather than hardcoding dropdown values in `01_agreement` or downstream notebooks.

## Expected evidence

The configured metadata target receives steward and agreement rows. `02_pipeline` later selects the agreement so catalogue, profile, lineage, and guardrail evidence can be tied back to ownership and purpose.

| Intake step | Metadata written |
| ----------- | ---------------- |
| Data steward intake | `METADATA_DATA_STEWARD` rows with steward identity, lifecycle fields, optional custom fields, and audit columns. |
| Agreement intake | `METADATA_DATA_AGREEMENT` rows with agreement identity, contract version, selected steward context, usage fields, optional custom fields, and audit columns. |
Next, continue to [Run a Data Pipeline](run-pipeline.md).

See also: [List of Metadata Tables](../reference/metadata.md) and [List of Functions](../reference/index.md).
