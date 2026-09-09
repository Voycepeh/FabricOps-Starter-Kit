# Step 5: Link the Data Agreement and Activate

**Governance explicitly links the tested frozen Data Contract version to the required Data Agreement, then activates that version for Production resolution.**

## High-level flow

```text
tested frozen Data Contract version + selected Data Agreement
                              ↓
                  explicit Governance linkage
                              ↓
                    activate for Production
```

!!! important "This linkage did not happen in Step 3"

    Step 3 authored and froze a table-centric definition: `table_id` plus Enrichment and Guardrails. Step 5 is the explicit governance decision that associates the tested version with the required Data Agreement and designates it for Production.

## Before you begin

Confirm Engineering Development selected and validated the exact frozen version for the same `table_id`. Identify the required Data Agreement and complete the organisation's review and sign-off practice.

## What to do

1. In `01_governance`, select the tested frozen Data Contract version and review its `table_id`, immutable Enrichment, Guardrails, schema, and processing definition.
2. Select the required Data Agreement and explicitly confirm the linkage between that Agreement and this tested version. Verify the provider and recipient Data Stewards, purpose, approved usages, and applicable Agreement version.
3. Record any required governance sign-off through the organisation's operating process.
4. Use `widget_activate_data_contract(...)` to activate that exact frozen version for its governed `table_id`.
5. Confirm it is the one active Data Contract version Production will resolve.

!!! warning "Test and sign-off are operating practice, not a technical activation gate"

    The current implementation does not technically enforce a recorded passing Development test or approval state before activation. Governance must verify those conditions as operating practice before invoking activation.

Activation changes Data Contract lifecycle state. It does not copy notebooks, deploy code, move data, or promote `02_pipeline`; promotion remains Step 6.

## Expected result

The tested frozen Data Contract version is visibly associated with the required Data Agreement and is the one active version Production resolves for the governed `table_id`. No notebook has been promoted by this action.

**Previous:** [Step 4: Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)
**Next:** [Step 6: Promote and run Production with the active Data Contract](06-promote-to-production.md)

See also: [`widget_activate_data_contract()`](../api/reference/widget_activate_data_contract.md) and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
