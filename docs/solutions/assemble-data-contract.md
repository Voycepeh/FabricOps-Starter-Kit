# Assemble a complete Data Contract for a governed table

Freeze the governed definition of one table into a versioned Data Contract that can be reviewed, tested, and used by Production checks.

## Why this is useful

**Governance authoring changes over time, but Production needs a stable version of the expectations it is meant to enforce.**

FabricOps keeps mutable authoring metadata in its normal tables, then assembles the selected state into one immutable contract snapshot:

```text
Data Agreement
+ Data Stewards
+ Data Catalogue structure
+ Enrichment
+ active Guardrails
+ approved usages
        ↓
widget_register_data_contract()
        ↓
versioned contract_payload_json
```

## How it works

1. Governance selects one exact Data Agreement version.
2. Governance selects one governed `table_id`.
3. `widget_register_data_contract()` resolves the current table structure, Enrichment, active Guardrails, Data Stewards, and approved usages.
4. The widget previews the assembled definition before any write.
5. Saving appends a new draft Data Contract version for that table lifecycle.
6. `widget_activate_data_contract()` can manually make one version active for Production use.

## One table, versioned over time

A Data Contract governs exactly one logical `table_id`.

The same table can have multiple historical versions:

```text
Data Contract v1 — superseded
Data Contract v2 — active
Data Contract v3 — draft
```

Only one version may be active for that table at a time.

## What is frozen

The contract payload includes the governed definition needed to interpret the table and its expectations:

- Data Agreement and version
- relevant Data Stewards
- canonical table identity and column structure
- Enrichment
- active Guardrails with their exact `guardrail_version`
- approved usages

Guardrail Results and Guardrail Row Results are runtime evidence. They remain outside the contract snapshot.

!!! note "Activation is not promotion"

    Manual Data Contract activation tells FabricOps which frozen version Production is authorised to use. It does not move the notebook or table from Engineering Development to Engineering Production. The external approval and promotion workflow is intentionally deferred.

## Next

Follow the Guided Demo to [create and activate the Data Contract](../guided-demo/05-create-data-contract.md), then [run Production with the active Data Contract](../guided-demo/06-promote-to-production.md).

See also: [`widget_register_data_contract()`](../api/reference/widget_register_data_contract.md), [`widget_activate_data_contract()`](../api/reference/widget_activate_data_contract.md), and [METADATA_DATA_CONTRACT](../reference/metadata/metadata_data_contract.md).
