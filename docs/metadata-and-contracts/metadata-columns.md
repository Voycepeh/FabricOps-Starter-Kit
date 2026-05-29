# Metadata columns

## Purpose

This page defines the minimum spreadsheet-style column catalogue view. It is a practical row-per-column handover view, not the full FabricOps metadata model.

FabricOps also stores operational, approval, lineage, DQ, drift, and notebook traceability evidence. The long-term target is to assemble this evidence into FabricOps JSON, ODCS YAML, and OpenMetadata-compatible payloads through the `handover` module.

## Minimum metadata column mapping

| Field | Purpose | Example value | Status | Notebook template | Function/module | Metadata table | ODCS mapping | OpenMetadata mapping | Enhancement required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Column Name | Identifies the field in the governed table. | `customer_id` | Collected | `02_ex_*` | `data_profiling.profile_dataframe`; metadata key helpers | Profile/evidence table using `COLUMN_NAME`; related business/governance/DQ rows use `column_name` or `columns` | Schema property name | Table column name | Standardize final catalogue field name in `handover.build_contract_json`. |
| Description | Explains approved business meaning. | `Unique customer identifier used for matching records.` | Collected | `02_ex_*` | `business_context.review_business_context`, `business_context.write_business_context` | `METADATA_COLUMN_BUSINESS_CONTEXT` | Schema property description | Column description | Include in final catalogue assembly. |
| Data Type | Records observed runtime type. | `string` | Collected | `02_ex_*` | `data_profiling.profile_dataframe` | Profile/evidence table using `DATA_TYPE` | Schema property physical/logical type | Column data type | Map Spark/Fabric types to ODCS/OpenMetadata type vocabularies. |
| Field Classification | Records governed classification label. | `identifier`, `confidential` | Collected | `04_gov_*` and governance review in `02_ex_*` | `data_governance.review_governance`, `data_governance.write_governance` | `METADATA_COLUMN_GOVERNANCE` | Classification/custom property | Tags, classification, glossary term | Define canonical taxonomy mapping. |
| Units | Describes measurement unit for numeric/time fields. | `USD`, `days`, `percent` | Planned | Future `02_ex_*` or `04_gov_*` review field | Planned `business_context` enhancement | Planned business context/catalogue field | Custom property or schema property metadata | Column custom property or glossary term | Add `units` to business-context review and catalogue assembly. |
| Allowed Values | Captures finite accepted values, ranges, or patterns. | `['active', 'inactive']` | Partial | `02_ex_*` and `03_pc_*` | `data_quality.draft_dq_rules`, `data_quality.review_dq_rules`, `data_quality.write_dq_rules` | `METADATA_DQ_RULES` with `rule_json` | Quality rule constraints | Data quality test / custom property | Flatten `accepted_values`, `value_range`, and `regex_pattern` into catalogue fields. |
| Example Values | Shows safe illustrative values for readers. | `active`, `2026-01-31` | Planned | Future `02_ex_*` profiling/review | Planned `data_profiling.profile_dataframe` enhancement | Planned profile/catalogue field | Examples/custom property | Column profile sample/custom property | Add masking-aware example value collection. |
| Top 5 Values | Shows most frequent low-cardinality values. | `active: 920`, `inactive: 80` | Planned | Future `02_ex_*` profiling | Planned `data_profiling.profile_dataframe` enhancement | Planned profile/catalogue field | Profiling/statistics extension | Column profile statistics | Add masking-aware top-value aggregation. |
| Low Frequency Count | Flags rare values below a threshold. | `3 values occur once` | Planned | Future `02_ex_*` profiling | Planned `data_profiling.profile_dataframe` enhancement | Planned profile/catalogue field | Profiling/statistics extension | Column profile statistics | Define threshold and aggregate rare-value count. |
| Missing Data | Records null count and percentage. | `NULL_COUNT=12`, `NULL_PERCENT=1.2` | Collected | `02_ex_*` | `data_profiling.profile_dataframe` | Profile/evidence table using `NULL_COUNT`, `NULL_PERCENT` | Quality rule/statistics | Column profile statistics / data quality test | Map nullability and missing-rate rules explicitly. |
| Source/Derivation | Explains source or transformation logic for the column. | `Derived from source status code.` | Partial | `02_ex_*`, `03_pc_*`, `04_gov_*` | `data_lineage`; notebook registry helpers in `metadata` | Lineage/evidence tables and `METADATA_NOTEBOOK_REGISTRY` | Lineage/source/custom property | Lineage edge or column custom property | Add approved per-column `source_derivation` review field. |
| PII/Sensitive | Indicates personal data and sensitivity handling. | `direct_identifier`, `not_pii`, `confidential` | Collected | `04_gov_*` and governance review in `02_ex_*` | `data_governance.review_governance`, `data_governance.write_governance` | `METADATA_COLUMN_GOVERNANCE` | Classification/custom property | Tags/classification | Define canonical PII/sensitivity taxonomy mapping. |
| Business Rules | Lists approved quality and policy expectations. | `not_null`, `regex_format`, `severity=error` | Collected | `02_ex_*`, `03_pc_*` | `data_quality.review_dq_rules`, `data_quality.write_dq_rules`, `data_quality.enforce_dq` | `METADATA_DQ_RULES` and runtime DQ outputs | Quality rules | Tests/test cases | Normalize active rules into final contract JSON and exporters. |

## Collection status legend

- **Collected**: FabricOps captures the evidence today in an existing notebook/function flow.
- **Partial**: FabricOps captures related evidence, but the final catalogue field still needs flattening or standard mapping.
- **Planned**: The field is a documented backlog item and should be added before claiming full catalogue coverage.

## Catalogue assembly backlog

- Add `metadata.load_column_catalogue_evidence` to load profiles, business context, governance, DQ rules, lineage, drift, and notebook registry evidence.
- Add `handover.build_contract_json` to assemble the canonical row-per-column catalogue inside the final FabricOps JSON artifact.
- Add `handover.export_odcs_yaml` and `handover.export_openmetadata_payload` mappings for the catalogue fields.
- Enhance `profile_dataframe` with safe example values, top values, and low-frequency counts.
- Enhance `business_context` review with optional `units` and `source_derivation` fields.
