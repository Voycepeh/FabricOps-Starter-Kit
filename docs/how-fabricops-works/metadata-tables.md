# Metadata Tables

Metadata tables are the shared memory of the FabricOps notebook handshake. They keep agreement context, observed evidence, approved intent, runtime outcomes, lineage, run summaries, enrichment, and review state separate so users can explain what happened without reading every notebook cell.

| Table | Primary role | Written by | Read by |
| --- | --- | --- | --- |
| `METADATA_DATA_CATALOGUE` | Observed physical/profile evidence for datasets, tables, columns, schemas, row counts, profile payloads, hashes, watermark values, and profile status. | `02_pipeline` profiling and guardrail flows. | `02_pipeline` guardrails, `03_governance` target selection/review, dashboard. |
| `METADATA_GUARDRAIL_RULES` | Approved or pending guardrail intent for schema, freshness, profile behaviour, and DQ rules. | `02_pipeline` optional authoring and `03_governance` authoring/review. | `02_pipeline` runtime guardrail execution, `03_governance`, dashboard. |
| `METADATA_GUARDRAIL_RESULTS` | Runtime guardrail outcomes: status, `can_continue`, severity, reasons, expected/actual values, and result payloads. | `02_pipeline` through guardrail execution. | Dashboard, support review, governance users. |
| `METADATA_PIPELINE_RUNS` | Run-level pipeline summary and status evidence. | `02_pipeline`. | Dashboard, support review, handover workflows. |
| `METADATA_DATA_LINEAGE_TABLE` | Source-to-target lineage relationships for pipeline outputs. | `02_pipeline`. | Dashboard and support/governance review. |
| Agreement metadata tables | Steward, agreement, contract, notebook registry, and agreement evidence context used to anchor runs to governed intent. | `01_agreement`; notebook registry linkage is selected/updated by `02_pipeline`. | `02_pipeline`, dashboard, handover workflows. |
| `METADATA_ENRICHMENT_RULES` | Descriptive enrichment intent and lifecycle state for table/column metadata. | `02_pipeline` optional enrichment and `03_governance`. | `03_governance`, dashboard. |
| `METADATA_DATA_ACCESS` | Access/governance metadata when configured by the implementation. | Governance/enrichment workflows. | Dashboard or review workflows when surfaced. |

## Separation of responsibilities

- `METADATA_DATA_CATALOGUE` is observed evidence.
- `METADATA_GUARDRAIL_RULES` is governed rule intent.
- `METADATA_GUARDRAIL_RESULTS` is runtime outcome evidence.

Keeping these responsibilities separate prevents a pipeline result from being mistaken for an approved rule, or a rule from being mistaken for observed physical evidence.

## Metadata routing

All metadata tables should be accessed through the configured `metadata` target from `00_env_config`. The workflow should not assume an attached/default Lakehouse for `METADATA_*` reads or writes.

## Key helpers

Metadata setup starts with [setup_metadata_tables](../api/reference/setup_metadata_tables/). Pipeline lineage evidence is written with [write_pipeline_lineage](../api/reference/write_pipeline_lineage/).
