# Review Guardrails

Run `03_governance` to review enrichment and guardrail intent before relying on active rules in future pipeline runs.

## What to do

1. Select the governed table context.
2. Review schema, freshness, profile behavior, DQ, and enrichment records.
3. Approve, reject, replace, deactivate, or request follow-up using the review widgets.
4. Rerun `02_pipeline` when you want active guardrails enforced against fresh data.

## Expected evidence

Guardrail and enrichment review decisions are appended to their metadata tables, and active rules become available to runtime enforcement.

See also: [METADATA_GUARDRAIL_RULES](../reference/metadata-tables/metadata-guardrail-rules.md) and [List of DQ Rules](../reference/dq-rules/index.md).
