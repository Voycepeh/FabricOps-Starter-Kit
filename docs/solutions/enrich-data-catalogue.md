# Enrich Data Catalogue metadata with business context

Add business meaning to the Data Catalogue without mixing manually authored context into the observed table and column identity.

## Why this is useful

**Profiling tells you what Engineering observed; Enrichment records the business context that Governance adds to that observed asset.**

A Data Catalogue row can identify the table, column, data type, environment, store, and layer. That does not explain what the table means, how a field should be interpreted, or other governance context that is not physically discoverable from the data itself.

FabricOps keeps those responsibilities separate:

```text
Engineering
profile_and_register_table()
→ METADATA_DATA_CATALOGUE

Governance
widget_enrich_table_metadata()
→ METADATA_ENRICHMENT
```

## How it works

1. Engineering profiles and registers the table so the canonical table and column identities exist in the Data Catalogue.
2. Governance opens `widget_enrich_table_metadata()` in `01_governance`.
3. Governance selects the registered table and adds the required table- or column-level business context.
4. FabricOps stores the authored context in `METADATA_ENRICHMENT` against the canonical Data Catalogue identity.
5. When a Data Contract version is assembled, the relevant Enrichment is frozen into that contract snapshot.

## What stays separate

| Metadata | Owner | Purpose |
| --- | --- | --- |
| `METADATA_DATA_CATALOGUE` | Engineering observation | Current table and column identity discovered from the data. |
| `METADATA_DATA_PROFILED` | Engineering observation | Current profile evidence. |
| `METADATA_ENRICHMENT` | Governance authoring | Business context added to a catalogued table or column. |
| `METADATA_DATA_CONTRACT` | Governance contract snapshot | Frozen governed definition, including the relevant Enrichment. |

!!! note "Enrichment does not replace profiling"

    Keep observed data facts in the Data Catalogue and Data Profiled tables. Use Enrichment only for business context that Governance intentionally authors.

## Next

Follow the Guided Demo to [enrich the Data Catalogue and define Guardrails](../guided-demo/03-enrich-guardrails.md), then [assemble the Data Contract](../guided-demo/05-create-data-contract.md).

See also: [`widget_enrich_table_metadata()`](../api/reference/widget_enrich_table_metadata.md) and [METADATA_ENRICHMENT](../reference/metadata/metadata_enrichment.md).
