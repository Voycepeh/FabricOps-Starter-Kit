# Create Agreement

Run `01_agreement` after environment setup to capture steward, agreement, and evidence context before pipeline execution. This notebook gives later technical evidence an accountable owner, business purpose, approved usage context, and supporting file references.

## What to do

1. Reuse the `CONFIG` and `ENV` values from `00_env_config`.
2. Enter demo steward details, including role, contact, and effective dates.
3. Create a public-safe data agreement with a readable name, domain, recipient, business purpose, usage flags, and readiness notes.
4. Save agreement evidence references where needed. Upload binary evidence files separately to the metadata Lakehouse `Files` area before recording their `Files/...` paths.

The visible widget configuration comes from `DATA_AGREEMENT_CONFIG` in `00_env_config`. Edit steward role options, visible columns, and custom fields there rather than hardcoding dropdown values in `01_agreement` or downstream notebooks.

## Expected evidence

The configured metadata target receives steward, agreement, and agreement evidence rows. `02_pipeline` later selects the agreement so pipeline summary, lineage, guardrail, and run evidence can be tied back to ownership and purpose.

| Intake step | Metadata written |
| ----------- | ---------------- |
| Data steward intake | `METADATA_DATA_STEWARD` rows with steward identity, lifecycle fields, optional custom fields, and audit columns. |
| Agreement intake | `METADATA_DATA_AGREEMENT` rows with agreement identity, contract version, selected steward context, usage fields, optional custom fields, and audit columns. |
| Agreement evidence | `METADATA_DATA_AGREEMENT_EVIDENCE` rows pointing to supporting file references or links. |

Next, continue to [Run Pipeline](run-pipeline.md).

See also: [List of Metadata Tables](../reference/metadata.md) and [List of Functions](../reference/index.md).
