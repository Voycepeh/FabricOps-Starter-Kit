# Step 3. Author and freeze the Data Contract

**Return to `01_governance` and turn the real Engineering evidence from Step 2 into a versioned Data Contract.**

This is where FabricOps closes the first Governance to Engineering loop. You are no longer defining rules against an imagined table. `02_pipeline` has already created and profiled the real target, so Governance can author against its canonical `table_id`.

## Select the governed table

Use the table selection section in `01_governance` to choose the target produced in Step 2.

Review the available Catalogue and profiling evidence so you understand the physical table before defining its contract.

## Open the Data Contract authoring widget

`widget_data_contract()` brings the table-specific Governance definition together in one place.

Author the contract in three parts:

1. **Enrichment**: descriptions, business meaning, classifications, sensitivity context, and other descriptive metadata.
2. **Guardrails**: enforceable Schema, Freshness, Source Drift, Data Quality, and Sensitive Data expectations.
3. **Processing**: the target load strategy and any parameters required by that strategy, plus the logical notebook ownership.

The important concept is that these are not separate disconnected metadata records from the user's point of view. Together they form the governed definition for that table and version.

## Make the Step 2 behaviour governed

Use the contract to formalise decisions that were only Development proposals in Step 2.

For example:

- keep `curated_orders` as `overwrite`, or
- configure a suitable target as `append`, SCD1, or SCD2 with its required keys and parameters,
- add a Schema Guardrail based on the observed table,
- add one or two understandable DQ rules,
- add Freshness and Source Drift expectations where appropriate,
- add Sensitive Data handling when the demo columns support it.

Do not add rules only to make the screen look busy. The goal is to make it obvious that the Data Contract changes what the same `02_pipeline` will enforce in Step 4.

## Review the complete definition

Before freezing, review the selected `table_id`, Enrichment, Guardrails, Processing, and ownership together.

A user should be able to answer:

> What does this table mean, what must be true about it, and how is it allowed to be published?

## Freeze the version

Freeze the reviewed draft to create an immutable Data Contract version.

Freezing does not activate the version for Production. It creates the exact version Engineering Development can select and test next.

## Expected result

You now have a frozen immutable Data Contract built from the real table evidence produced in Step 2.

**Next:** [Step 4. Select and validate the Data Contract](04-run-pipeline-with-guardrails.md)
