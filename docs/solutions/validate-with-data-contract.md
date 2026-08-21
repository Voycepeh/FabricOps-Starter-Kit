# Validate with a frozen Data Contract

Use the same Guardrail checks against current authoring rules in Development or the one active frozen Data Contract in Production.

## Why this is useful

**A governed pipeline should be able to test proposed expectations in Development without letting mutable authoring metadata become the Production source of truth.**

FabricOps separates the rule source by environment:

```text
DEVELOPMENT
current authoring Guardrails
or
one exact selected Data Contract version per table

PRODUCTION
exactly one active Data Contract per table
```

The public check calls stay the same:

- `check_schema()`
- `check_freshness()`
- `check_changes()`
- `check_dq()`

## Development

`widget_select_data_contract()` is a read-only selector in `02_pipeline`.

For each governed `table_id`:

- **Current authoring Guardrails** is the default and reads the current rules in `METADATA_GUARDRAIL`.
- Selecting **Data Contract vN** makes the checks use the frozen Guardrails from that exact contract version.

Selections are table-scoped, so different tables in the same notebook can use different contract versions or remain on current authoring Guardrails independently.

## Production

Production does not allow manual contract selection.

For each governed table FabricOps resolves:

```text
physical table
→ canonical Data Catalogue table_id
→ one active Data Contract
→ frozen Guardrails
→ check_schema / check_freshness / check_changes / check_dq
```

There is no fallback to mutable `METADATA_GUARDRAIL` in Production.

If no active contract exists, the governed Production check fails. More than one active version for the same table is treated as an integrity error.

## Why frozen rules matter

Suppose Data Contract v1 freezes Rule A and Governance later changes the current authoring rule to Rule B.

| Run | Rule used |
| --- | --- |
| Development, current authoring | Rule B |
| Development, Data Contract v1 selected | Rule A |
| Production, Data Contract v1 active | Rule A |

The frozen contract therefore remains stable even while Governance prepares later authoring changes.

!!! note "Approval and promotion are separate"

    This solution covers Data Contract-backed validation only. The external approval and Development-to-Production promotion workflow is deferred until the Fabric GUI flow can be configured and demonstrated end to end.

## Next

Follow the Guided Demo to [test Guardrails in Development](../guided-demo/04-run-pipeline-with-guardrails.md), [assemble and activate a Data Contract](../guided-demo/05-create-data-contract.md), then [run Production against the active contract](../guided-demo/06-promote-to-production.md).

See also: [`widget_select_data_contract()`](../api/reference/widget_select_data_contract.md) and [ETL Guardrails](etl-guardrails.md).
