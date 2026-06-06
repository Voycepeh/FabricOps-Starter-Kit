# Metadata Dashboard

The metadata dashboard is planned after v1.0.0. This page describes the recommended direction for a future Power BI reporting layer over FabricOps metadata.

FabricOps v1.0.0 already collects metadata through notebooks and stores it in the configured metadata lakehouse. A future dashboard can make agreement status, table health, column context, reviewed DQ expectations, classification metadata, data-change results, and lineage easier to review without inspecting raw metadata tables.

## v1.0.0 scope

Dashboard improvements are not part of the v1.0.0 implementation scope. The v1.0.0 production guardrail boundary remains each `03_pc` notebook. Separate data contracts are not required, and reviewed governance DQ expectations remain advisory unless manually implemented inside the relevant `03_pc` notebook.

## Planned dashboard pages

![FabricOps metadata dashboard wireframe](../assets/fabricops-metadata-dashboard.png){ .full-width }

| Page | Purpose | Likely metadata sources |
| --- | --- | --- |
| Overview | Agreement status, owner, steward, coverage, and readiness. | Agreement, steward, catalogue, lineage, and governance metadata. |
| Table Health | Table profile, latest guardrail evidence, data-change status, freshness, and lineage coverage. | Catalogue/profile evidence, lineage, and run summaries. |
| Column Catalogue | Column descriptions, classifications, data types, null percentages, and reviewed expectations. | Catalogue, column context, DQ expectations, and classifications. |
| Quality View | Reviewed DQ expectations and any implemented notebook guardrail outcomes. | `METADATA_DQ_RULES`, catalogue evidence, and `03_pc` run evidence. |
| Lineage View | Source tables, target tables, notebook traceability, and lineage status. | `METADATA_DATA_LINEAGE_TABLE` and notebook registry. |
| Readiness View | Metadata coverage for review and operational follow-up. | Agreement, catalogue, governance, and handover metadata. |

## Planned reporting views

A future dashboard should consume assembled views rather than raw metadata tables directly. Suggested view names are intentionally descriptive and not v1.0.0 source-of-truth objects.

| View | Grain | Dashboard use |
| --- | --- | --- |
| `VW_AGREEMENT_SUMMARY` | One row per agreement | Overview, stewardship, and readiness pages. |
| `VW_TABLE_HEALTH_SUMMARY` | One row per table/run context | Table health, quality, data-change, freshness, lineage, and readiness pages. |
| `VW_COLUMN_CATALOGUE` | One row per table and column | Column catalogue, classification, profiling, and expectation coverage pages. |

Each view should stay at its own grain. Lower-grain views may include parent keys such as `agreement_id` and `table_name` for joining and filtering, but they should not duplicate full parent-level narratives.

## Suggested dashboard fields

### Overview page

| Field | Purpose |
| --- | --- |
| `agreement_id` | Agreement key. |
| `agreement_name` | Human-readable agreement name. |
| `business_domain` | Business area or data product domain. |
| `data_owner` | Accountable owner. |
| `data_steward` | Operational steward. |
| `agreement_status` | Current agreement status. |
| `table_count` | Number of governed tables. |
| `column_count` | Number of governed columns. |
| `classified_column_count` | Classification coverage. |
| `dq_expectation_count` | Reviewed DQ expectation coverage. |
| `latest_guardrail_status` | Latest implemented `03_pc` guardrail outcome where available. |
| `lineage_coverage_status` | Lineage coverage summary. |
| `readiness_status` | Overall metadata readiness indicator. |

### Table Health page

| Field | Purpose |
| --- | --- |
| `agreement_id` | Parent agreement key where available. |
| `dataset_name` | Dataset or topic name. |
| `table_name` | Governed table name. |
| `row_count` | Latest profiled row count. |
| `column_count` | Latest profiled column count. |
| `profile_status` | Profiling completion status. |
| `dq_expectation_count` | Number of reviewed expectations for the table. |
| `latest_schema_status` | Latest implemented schema guardrail status where available. |
| `latest_data_change_status` | Latest implemented data-change guardrail status where available. |
| `lineage_status` | Whether lineage evidence exists. |
| `source_tables` | Upstream source tables. |
| `target_table` | Output table. |
| `pipeline_notebook_url` | Link to producing notebook where available. |
| `overall_table_status` | Overall table health indicator. |

### Column Catalogue page

| Field | Purpose |
| --- | --- |
| `agreement_id` | Parent agreement key where available. |
| `table_name` | Parent table. |
| `column_name` | Column name. |
| `ordinal_position` | Column order. |
| `data_type` | Observed or declared data type. |
| `description` | Reviewed business description. |
| `field_classification` | Field category. |
| `pii_classification` | PII classification. |
| `confidentiality_label` | Confidentiality level. |
| `handling_requirement` | Handling instruction. |
| `dq_expectations` | Reviewed expectations affecting the column. |
| `null_count` | Missing value count. |
| `null_percent` | Missing value percentage. |
| `example_values` | Example observed values. |
| `lineage_summary` | Column or table lineage summary. |
| `evidence_notebook_url` | Link back to evidence notebook where available. |

## Dashboard asset guidance

Future dashboard assets should use only generic sample or anonymised metadata. Do not include real data, secrets, tenant/workspace identifiers, internal URLs, or production screenshots.
