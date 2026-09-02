# Step 6: Promote and run Production with the active Data Contract

**Promote the validated `02_pipeline` into Engineering Production, then run it so FabricOps resolves the one active Data Contract for each governed table automatically.**

The Production runtime behaviour below is implemented but remains **Preview** in the Guided Demo until the complete promotion-to-run path is revalidated end to end in Fabric.

!!! info "Key concepts for this step"

    **Data Contract**, **Enforcement**, **Guardrail Result**, and **Data Quality** explain why Production resolves a saved immutable table-level contract instead of mutable Development authoring.

    Hover over a glossary term for its canonical definition, or open the [Glossary](../glossary.md) for the full entry.

## High-level flow

```text
Validated Development 02_pipeline
→ Promote into Engineering Production
→ Resolve active Data Contract
→ Resolve saved immutable Guardrails + processing
→ Prepare source scope
→ Validate source
→ Transform
→ Validate target
→ Governed write
→ Full read-back + profile
```

## Before you begin

Confirm that the governed table has exactly one active Data Contract version, the validated `02_pipeline` has passed Development validation, and the notebook uses the Production `00_env_config` after it is promoted into Engineering Production.

As an operating practice, the version should have been tested in Development and completed any required governance sign-off before activation. FabricOps does not currently enforce those checks as a technical activation gate.

??? note "Planned — Promote the validated pipeline"

    Move the validated `02_pipeline` into Engineering Production using the organisation's approved deployment process.

    FabricOps keeps this promotion action separate from Data Contract activation. Activating a contract does not deploy the notebook. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process.

??? info "Preview — Resolve the active Data Contract automatically"

    Open the promoted `02_pipeline` in Engineering Production and confirm the source, unified, and product targets resolve to the expected Production Fabric items.

    Run the Data Contract selector area. In Production it is read only and shows the active Data Contract version for the table.

    Production never falls back to mutable authoring metadata.

    ```text
    physical Production table
    → canonical Data Catalogue table_id
    → exactly one active Data Contract
    → saved immutable Guardrails + target processing
    ```

    If no active contract exists, or more than one active version exists for the same table, the governed Production run fails.

??? info "Preview — Prepare and validate the Production source"

    Use `read_pipeline_prep()` with the source `table_id` so FabricOps resolves the registered source, its own active contract processing where change safety requires it, and the configured source-read strategy. It then prepares the runtime mode as `skip`, `full_dataset`, or `incremental_subset`.

    The source-read strategy itself is Full Dataset, Incremental Watermark, or Incremental Partition. The source strategy and runtime read mode are separate concepts.

    Run source Schema, Freshness, and Changes Guardrails before the business-data read. Read the source using the prepared scope and run DQ on the DataFrame being processed.

    Register a source Profile only when that DataFrame represents the complete physical source table. An Incremental Subset must not replace the latest complete Profile.

???+ success "Live — Apply the visible transformation"

    Apply the normal project-owned transformation logic. The Production runtime uses the same visible transformation section as Development.

??? info "Preview — Validate and write the Production target"

    Run target Schema and DQ checks before changing the Production target.

    Use `write_pipeline_prep()` with the target `table_id` and continue with the Production write only when the Guardrail continuation decisions allow it. Target preparation independently resolves the target's one active Data Contract and its saved immutable processing definition.

??? info "Preview — Read back and register the complete target"

    Read the persisted target back in full and profile/register the complete persisted target.

    The active Data Contract therefore controls the governed runtime boundary while the physical read, transformation, writer, and persisted target remain visible in `02_pipeline`.

## Expected result

You should understand the Production path as **promote the validated `02_pipeline` → resolve the active saved Data Contract → run the governed Production pipeline**. Promotion and Data Contract activation are separate actions, and the Production runtime applies the active contract's saved immutable Guardrails and processing definition around the same canonical ETL lifecycle.

**Previous:** [Step 5: Save, test, and activate the Data Contract](05-create-data-contract.md)  
**Next:** [Step 7: Consume approved Production data](99-explore-via-notebook.md)

See also: [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md), [`read_pipeline_prep()`](../api/reference/read_pipeline_prep.md), [`write_pipeline_prep()`](../api/reference/write_pipeline_prep.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
