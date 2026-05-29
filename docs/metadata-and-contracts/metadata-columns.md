# Metadata columns

This page describes the column catalogue slice of FabricOps metadata: the row-per-column view that helps humans and export tools understand fields in a governed asset.

```text
Separate notebooks.
Shared metadata evidence.
Curated decisions plus run observations.
Assembled handover contract.
Standards-compatible export.
```

!!! note "Column catalogue slice"
    This page documents the column-level catalogue slice of the broader metadata architecture. It is not the full FabricOps metadata model. The full model separates curated human-owned decisions, machine/run observations, assembled views, and handover exports.

    See [Metadata Architecture](metadata-architecture.md) for the full table design.

## Purpose

The catalogue view is assembled from approved metadata evidence. It should not become a manually maintained source table or a separate spreadsheet that competes with governed evidence.

FabricOps follows this rule:

```text
Standalone curated tables = human-owned decisions.
Collapsed fact/evidence tables = machine/run observations.
Views and exports = assembled outputs, not source of truth.
```

Agreement, classification, business meaning, and DQ rules are governed decisions. Profiling, drift, DQ execution, lineage, and run results are evidence observations. The final column catalogue is assembled from both.

## Column catalogue coverage

The catalogue view is assembled from several metadata sources. Column names and data types come from profiling and column identity. Descriptions and units come from business context review. PII and sensitivity come from governance review. Allowed values and business rules come from DQ rules. Missingness, examples, top values, and low-frequency counts come from profile observations.

The table below documents the intended output view coverage for FabricOps JSON, ODCS YAML, and OpenMetadata-compatible payloads. It is not a physical source table definition.

| Field | Purpose | Example value | Status | Notebook template | Function/module | Metadata source | ODCS mapping | OpenMetadata mapping | Enhancement required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Column Name | Identifies the field in the governed table. | `customer_id` | Collected | `02_ex_*` | `data_profiling.profile_dataframe`; metadata key helpers | `METADATA_COLUMN` or profile evidence using `COLUMN_NAME`; related business/governance/DQ rows use `metadata_column_key`, `column_name`, or `columns` | Schema property name | Table column name | Standardize final catalogue field name in `handover.build_contract_json`. |
| Description | Explains approved business meaning. | `Unique customer identifier used for matching records.` | Collected | `02_ex_*` | `business_context.review_business_context`, `business_context.write_business_context` | Latest active `METADATA_COLUMN_BUSINESS_CONTEXT` | Schema property description | Column description | Include in final catalogue assembly. |
| Data Type | Records observed runtime type. | `string` | Collected | `02_ex_*` | `data_profiling.profile_dataframe` | `METADATA_COLUMN.current_data_type` or latest `METADATA_PROFILE_OBSERVATIONS.DATA_TYPE` | Schema property physical/logical type | Column data type | Map Spark/Fabric types to ODCS/OpenMetadata type vocabularies. |
| Field Classification | Records semantic/governance classification for the field. | `identifier`, `measure`, `confidential` | Partial | `04_gov_*` and governance review in `02_ex_*` | `data_governance.review_governance`, `data_governance.write_governance` | Latest active `METADATA_COLUMN_GOVERNANCE` plus profiling-derived taxonomy | Classification/custom property | Tags, classification, glossary term | Define canonical taxonomy and map governance labels plus profiling hints into final field classification. |
| Units | Describes measurement unit for numeric/time fields. | `USD`, `days`, `percent` | Planned | Future `02_ex_*` or `04_gov_*` review field | Planned `business_context` enhancement | Planned `METADATA_COLUMN_BUSINESS_CONTEXT.units` | Custom property or schema property metadata | Column custom property or glossary term | Add `units` to business-context review and catalogue assembly. |
| Allowed Values | Captures finite accepted values, ranges, or patterns. | `['active', 'inactive']` | Partial | `02_ex_*` and `03_pc_*` | `data_quality.draft_dq_rules`, `data_quality.review_dq_rules`, `data_quality.write_dq_rules` | Active `METADATA_DQ_RULES.rule_json` | Quality rule constraints | Data quality test / custom property | Flatten `accepted_values`, `value_range`, and `regex_pattern` into catalogue fields. |
| Example Values | Shows safe illustrative values for readers. | `active`, `2026-01-31` | Planned | Future `02_ex_*` profiling/review | Planned `data_profiling.profile_dataframe` enhancement | Planned `METADATA_PROFILE_OBSERVATIONS.example_values_json` | Examples/custom property | Column profile sample/custom property | Add masking-aware example value collection. |
| Top 5 Values | Shows most frequent low-cardinality values. | `active: 920`, `inactive: 80` | Planned | Future `02_ex_*` profiling | Planned `data_profiling.profile_dataframe` enhancement | Planned `METADATA_PROFILE_OBSERVATIONS.top_values_json` | Profiling/statistics extension | Column profile statistics | Add masking-aware top-value aggregation. |
| Low Frequency Count | Flags rare values below a threshold. | `3 values occur once` | Planned | Future `02_ex_*` profiling | Planned `data_profiling.profile_dataframe` enhancement | Planned `METADATA_PROFILE_OBSERVATIONS.low_frequency_count` | Profiling/statistics extension | Column profile statistics | Define threshold and aggregate rare-value count. |
| Missing Data | Records null count and percentage. | `NULL_COUNT=12`, `NULL_PERCENT=1.2` | Collected | `02_ex_*` | `data_profiling.profile_dataframe` | Latest `METADATA_PROFILE_OBSERVATIONS.null_count`, `null_percent` | Quality rule/statistics | Column profile statistics / data quality test | Map nullability and missing-rate rules explicitly. |
| Source/Derivation | Explains source or transformation logic for the column. | `Derived from source status code.` | Partial | `02_ex_*`, `03_pc_*`, `04_gov_*` | `data_lineage`; notebook registry helpers in `metadata` | Business context source-derivation field or `METADATA_LINEAGE_EVENTS` | Lineage/source/custom property | Lineage edge or column custom property | Add approved per-column `source_derivation` review field. |
| PII/Sensitive | Indicates personal data and sensitivity handling. | `direct_identifier`, `not_pii`, `confidential` | Collected | `04_gov_*` and governance review in `02_ex_*` | `data_governance.review_governance`, `data_governance.write_governance` | Latest active `METADATA_COLUMN_GOVERNANCE` | Classification/custom property | Tags/classification | Define canonical PII/sensitivity taxonomy mapping. |
| Business Rules | Lists approved quality and policy expectations. | `not_null`, `regex_format`, `severity=error` | Collected | `02_ex_*`, `03_pc_*` | `data_quality.review_dq_rules`, `data_quality.write_dq_rules`, `data_quality.enforce_dq` | Active `METADATA_DQ_RULES` plus runtime `METADATA_DQ_RESULTS` | Quality rules | Tests/test cases | Normalize active rules into final contract JSON and exporters. |

## Collection status legend

- **Collected**: FabricOps captures the evidence today in an existing notebook/function flow.
- **Partial**: FabricOps captures related evidence, but the final catalogue field still needs flattening or standard mapping.
- **Planned**: The field is a documented backlog item and should be added before claiming full catalogue coverage.

## Catalogue assembly backlog

- Add or standardize `metadata.load_column_catalogue_evidence` as the planned loader for profile, business context, governance, DQ rule, lineage, drift, and notebook registry evidence.
- Add or standardize `handover.build_contract_json` as the planned assembler for the canonical row-per-column catalogue inside the final FabricOps JSON artifact.
- Add ODCS YAML and OpenMetadata-compatible mappings for the catalogue fields through `handover` export boundaries.
- Enhance `profile_dataframe` with safe example values, top values, and low-frequency counts before claiming full catalogue coverage.
- Enhance business context review with optional `units` and `source_derivation` fields.

The catalogue remains an assembled output. Curated decision tables and run evidence facts remain the source records.
