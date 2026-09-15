# Step 5. Link the Data Agreement and activate

**Return to `01_governance` after Development validation and make the tested Data Contract the Production-ready governed definition.**

## Select the tested version

Use the activation section of `01_governance` to select the exact Data Contract version that passed Step 4.

Do not activate a different draft or untested version simply because it is newer.

## Link the Data Agreement

Select the exact Data Agreement version created in Step 1 that governs this producer-to-consumer relationship.

Activation brings the lifecycle together:

```text
Data Steward context
        ↓
Data Agreement
        ↓
real table_id from Engineering
        ↓
Data Contract version
        ↓
Development validation
        ↓
Agreement linkage + activation
```

## Activate for Production

Review the selected `table_id`, tested Data Contract version, and linked Data Agreement version, then activate it.

Activation tells FabricOps which immutable version Production must resolve for that governed table.

Activation does **not** deploy `02_pipeline`. Governance chooses the governed definition; Engineering still promotes the validated pipeline logic through the organisation's normal Fabric deployment process.

## Expected result

The tested contract version is linked to the correct Data Agreement version and is the active Production definition for the governed table.

**Next:** [Step 6. Promote and run Production](06-promote-to-production.md)
