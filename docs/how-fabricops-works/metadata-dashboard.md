# Metadata Dashboard

FabricOps Starter Kit collects metadata through project notebooks and assembles it into a dashboard-ready reporting layer.

This page describes the recommended Power BI dashboard wireframe and the assembled views that the dashboard consumes.

The dashboard is the user-facing layer of the metadata collected by the framework. It helps users review agreement status, table health, column definitions, data quality results, drift checks, and lineage evidence without inspecting raw metadata tables directly.

The governed source evidence remains in the metadata tables described on the [Metadata Tables](metadata-tables.md) page.

## Dashboard wireframe

A lightweight Power BI dashboard can be organised into the following pages.

| Page | Purpose | Main view |
| --- | --- | --- |
| Overview | Shows agreement status, owner, steward, coverage, and readiness. | `VW_AGREEMENT_CONTRACT_SUMMARY` |
| Table Health | Shows table profile, data quality status, drift status, freshness, and lineage coverage. | `VW_TABLE_CONTRACT_SUMMARY` |
| Column Catalogue | Shows column definitions, data types, classifications, profiling evidence, and rule coverage. | `VW_COLUMN_CATALOGUE` |
| Quality View | Shows rule counts, latest validation status, failed rules, and affected tables or columns. | `VW_TABLE_CONTRACT_SUMMARY`, `VW_COLUMN_CATALOGUE` |
| Lineage View | Shows source tables, target tables, notebook traceability, and lineage status. | `VW_TABLE_CONTRACT_SUMMARY` |
| Readiness View | Shows whether agreements and tables have enough metadata coverage for review and operational follow-up. | `VW_AGREEMENT_CONTRACT_SUMMARY`, `VW_TABLE_CONTRACT_SUMMARY` |

## Dashboard preview

The documentation should include screenshots of the dashboard so users can understand the intended experience before downloading or recreating it.

Recommended screenshots:

| Screenshot | What it should show |
| --- | --- |
| Overview page | Agreement status, coverage, owner, steward, and readiness cards. |
| Table Health page | Table-level quality, drift, freshness, lineage, and overall health. |
| Column Catalogue page | Column descriptions, classifications, data types, null percentage, and rule coverage. |
| Quality View page | Rule status, failures, warnings, and affected assets. |
| Lineage View page | Source-to-target relationship and notebook evidence. |

Screenshots should use sample or anonymised metadata only.

## Views consumed by the dashboard

The dashboard should consume assembled reporting views rather than raw metadata tables directly.

| View | Grain | Dashboard use |
| --- | --- | --- |
| `VW_AGREEMENT_CONTRACT_SUMMARY` | One row per agreement | Overview, stewardship, and readiness pages. |
| `VW_TABLE_CONTRACT_SUMMARY` | One row per agreement and table | Table health, quality, drift, freshness, lineage, and readiness pages. |
| `VW_COLUMN_CATALOGUE` | One row per agreement, table, and column | Column catalogue, classification, profiling, and rule coverage pages. |

These views are derived from the governed metadata tables. They are not separate sources of truth.

## View design rule

Each view should stay at its own grain.

| View | Owns | Should avoid |
| --- | --- | --- |
| `VW_AGREEMENT_CONTRACT_SUMMARY` | Agreement ownership, usage, status, coverage, and readiness. | Table-level row counts or column-level descriptions. |
| `VW_TABLE_CONTRACT_SUMMARY` | Table profile, quality status, drift status, freshness, lineage, and table health. | Agreement policy text or column-level business definitions. |
| `VW_COLUMN_CATALOGUE` | Column definitions, data types, classifications, profiling evidence, and rule coverage. | Agreement-level ownership summary or table-level health narrative. |

Lower-grain views may include parent keys such as `agreement_id` and `table_name` for joining and filtering, but they should not duplicate full parent-level narratives.

## Suggested dashboard fields

### Overview page

Use `VW_AGREEMENT_CONTRACT_SUMMARY`.

Suggested fields:

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
| `dq_rule_count` | Data quality rule coverage. |
| `latest_dq_status` | Latest quality outcome. |
| `latest_drift_status` | Latest drift outcome. |
| `lineage_coverage_status` | Lineage coverage summary. |
| `overall_contract_status` | Overall dashboard readiness. |

### Table Health page

Use `VW_TABLE_CONTRACT_SUMMARY`.

Suggested fields:

| Field | Purpose |
| --- | --- |
| `agreement_id` | Parent agreement key. |
| `dataset_name` | Dataset or data product name. |
| `table_name` | Governed table name. |
| `row_count` | Latest profiled row count. |
| `column_count` | Latest profiled column count. |
| `profile_status` | Profiling completion status. |
| `dq_rule_count` | Number of rules for the table. |
| `latest_dq_status` | Latest table-level quality result. |
| `failed_rule_count` | Failed rules in the latest run. |
| `latest_drift_status` | Latest drift result. |
| `drift_summary` | Short drift explanation. |
| `lineage_status` | Whether lineage evidence exists. |
| `source_tables` | Upstream source tables. |
| `target_table` | Output table. |
| `pipeline_notebook_url` | Link to producing or enforcing notebook. |
| `overall_table_status` | Overall table health status. |

### Column Catalogue page

Use `VW_COLUMN_CATALOGUE`.

Suggested fields:

| Field | Purpose |
| --- | --- |
| `agreement_id` | Parent agreement key. |
| `table_name` | Parent table. |
| `column_name` | Column name. |
| `ordinal_position` | Column order. |
| `data_type` | Observed or declared data type. |
| `description` | Business description. |
| `source_derivation` | How the column is derived. |
| `field_classification` | Field category. |
| `pii_classification` | PII classification. |
| `confidentiality_label` | Confidentiality level. |
| `sensitivity_label` | Sensitivity summary. |
| `handling_requirement` | Handling instruction. |
| `business_rules` | Rules affecting the column. |
| `latest_dq_status` | Latest rule outcome. |
| `null_count` | Missing value count. |
| `null_percent` | Missing value percentage. |
| `example_values` | Example observed values. |
| `latest_drift_status` | Latest drift status. |
| `lineage_summary` | Column or table lineage summary. |
| `evidence_notebook_url` | Link back to evidence notebook. |

## Downloadable dashboard asset

The repository can provide a Power BI dashboard file as a starter template.

The dashboard file should connect to the assembled views above. Users can then point the template to their own Fabric metadata lakehouse and refresh it with their project metadata.

Recommended assets:

| Asset | Purpose |
| --- | --- |
| Power BI dashboard file | Reusable dashboard template. |
| Dashboard screenshots | Preview of the expected dashboard. |
| Sample metadata | Optional sample data for testing the dashboard layout. |

## Next step

Continue to [Workspace Operating Model](workspace-operating-model.md) for workspace responsibilities, production promotion, and handover evidence.
