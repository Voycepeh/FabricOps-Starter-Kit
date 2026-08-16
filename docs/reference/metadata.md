# List of Metadata Tables

FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

The diagram below shows how the FabricOps metadata tables relate to one another across agreement, profiling, guardrail, lineage, and pipeline-run evidence.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

## Data Agreement versus Data Contract

A Data Agreement is the overarching governance agreement between the accountable data producer and consumer parties, represented by their data stewards. It defines why the data may be shared, who is accountable, the permitted purpose and scope, usage conditions, and the agreement’s review period.

A Data Contract is the machine-readable dataset-level promise governed by a Data Agreement. In the current FabricOps metadata model, the contract records the parent agreement, authorised catalogue tables, and their schema fingerprints. Related catalogue, enrichment, guardrail, profiling, and lineage metadata provide the broader technical and quality context for those tables.

One Data Agreement can govern multiple Data Contracts.

The agreement answers: Why and under what governance arrangement may this data be shared?

The contract answers: Exactly what data will be delivered, in what structure, at what quality, and how reliably?

## [METADATA_DATA_STEWARD](metadata/metadata_data_steward.md)

Know who is responsible for the data.

**Grain:** One registered Data Steward.

**Primary key:** `steward_id`

**Relationships:**

* **1:N**: One Data Steward can appear as the provider steward on many Data Agreement versions.
* **1:N**: One Data Steward can appear as the recipient steward on many Data Agreement versions.

[View full schema](metadata/metadata_data_steward.md)

---

## [METADATA_DATA_AGREEMENT](metadata/metadata_data_agreement.md)

Define why the data is shared, with whom, and under what conditions.

**Grain:** One version of one Data Agreement.

**Primary key:** `agreement_id` + `agreement_version`

**Relationships:**

* `provider_steward_id` → `METADATA_DATA_STEWARD.steward_id` (**N:1**). Each Data Agreement version has one provider steward; one steward can provide many agreement versions.
* `recipient_steward_id` → `METADATA_DATA_STEWARD.steward_id` (**N:1**). Each Data Agreement version has one recipient steward; one steward can receive many agreement versions.
* **1:N**: One Data Agreement lifecycle can govern many Data Contract rows through agreement_id.

[View full schema](metadata/metadata_data_agreement.md)

---

## [METADATA_DATA_CONTRACT](metadata/metadata_data_contract.md)

Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement.

**Grain:** One authorised catalogue table and schema fingerprint governed by one Data Agreement.

**Primary key:** `agreement_id` + `metadata_table_key` + `schema_fingerprint`

**Relationships:**

* `agreement_id` → `METADATA_DATA_AGREEMENT.agreement_id` (**N:1**). Many Data Contract rows can belong to one Data Agreement lifecycle; the current schema does not store agreement_version on the contract row.
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**1:N**). One contracted table identity can match the catalogue rows for that table's columns.

[View full schema](metadata/metadata_data_contract.md)

---

## [METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)

See what data is available and how it is structured.

**Grain:** One registered column for one table and schema fingerprint in one environment.

**Primary key:** `environment_name` + `metadata_table_key` + `metadata_column_key` + `schema_fingerprint`

**Relationships:**

* **1:N**: One catalogue table identity can be referenced by many Source Observation, Data Profiled, Data Lineage, Enrichment and Guardrail rows.

[View full schema](metadata/metadata_data_catalogue.md)

---

## [METADATA_SOURCE_OBSERVATION](metadata/metadata_source_observation.md)

See whether the source arrived and changed as expected.

**Grain:** One observed partition state for one source table at one observation time.

**Primary key:** `metadata_table_key` + `partition_column` + `partition_value` + `observed_at`

**Relationships:**

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many source partition observations can belong to one logical catalogue table identity.

[View full schema](metadata/metadata_source_observation.md)

---

## [METADATA_DATA_PROFILED](metadata/metadata_data_profiled.md)

Understand the shape, completeness, and characteristics of the data.

**Grain:** One profiled column for one dataset snapshot.

**Primary key:** `environment_name` + `metadata_column_key` + `schema_fingerprint` + `profiled_at`

**Relationships:**

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many profiled column snapshots can belong to one logical catalogue table identity.
* `metadata_column_key` → `METADATA_DATA_CATALOGUE.metadata_column_key` (**N:1**). Many profile snapshots can describe the same logical catalogue column over time.
* **1:N**: One profiled column snapshot can have many Data Profiled Frequency rows through metadata_column_key and profiled_at.

[View full schema](metadata/metadata_data_profiled.md)

---

## [METADATA_DATA_PROFILED_FREQUENCY](metadata/metadata_data_profiled_frequency.md)

See how values are distributed across the data.

**Grain:** One ranked observed value frequency for one profiled column snapshot.

**Primary key:** `metadata_column_key` + `profiled_at` + `frequency_rank`

**Relationships:**

* `metadata_column_key` → `METADATA_DATA_PROFILED.metadata_column_key` (**N:1**). Frequency rows belong to a profiled column; metadata_column_key and profiled_at together identify the parent snapshot.
* `profiled_at` → `METADATA_DATA_PROFILED.profiled_at` (**N:1**). The profile timestamp is the second part of the logical link back to the profiled column snapshot.

[View full schema](metadata/metadata_data_profiled_frequency.md)

---

## [METADATA_DATA_LINEAGE](metadata/metadata_data_lineage.md)

See where the data came from and where it ends up.

**Grain:** One source or target participation event for one profiled table snapshot in one Fabric activity.

**Primary key:** `lineage_event_id`

**Relationships:**

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many lineage events can refer to the same logical catalogue table identity.
* **1:N**: One lineage event can describe a table snapshot that is represented by many profiled column rows through metadata_table_key, schema_fingerprint and profiled_at.

[View full schema](metadata/metadata_data_lineage.md)

---

## [METADATA_ENRICHMENT](metadata/metadata_enrichment.md)

Add business and governance context to the data.

**Grain:** One appended enrichment value for one table or column identity.

**Primary key:** `enrichment_id`

**Relationships:**

* `metadata_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). When enrichment_level is table, many enrichment rows can describe one catalogue table identity.
* `metadata_key` → `METADATA_DATA_CATALOGUE.metadata_column_key` (**N:1**). When enrichment_level is column, many enrichment rows can describe one catalogue column identity.

[View full schema](metadata/metadata_enrichment.md)

---

## [METADATA_DATA_ACCESS](metadata/metadata_data_access.md)

See who can use the data and how it can be used.

**Grain:** One access review record for one user and governed scope.

**Primary key:** Not defined in the current implementation.

**Relationships:**

* No immediate logical relationship is defined in the current implementation.

[View full schema](metadata/metadata_data_access.md)

---

## [METADATA_GUARDRAIL](metadata/metadata_guardrail.md)

Define the expectations the data used in the ETL pipeline should meet.

**Grain:** One authored guardrail configuration row for one rule lifecycle or version.

**Primary key:** `guardrail_rule_id`

**Relationships:**

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many guardrail configurations can apply to one logical catalogue table identity.
* `metadata_column_key` → `METADATA_DATA_CATALOGUE.metadata_column_key` (**N:1**). Column level guardrails can point to one logical catalogue column identity.
* **1:N**: One guardrail rule can produce many Guardrail Results across pipeline runs through guardrail_rule_id.

[View full schema](metadata/metadata_guardrail.md)

---

## [METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)

See whether the expectations of the data in the ETL pipeline run are met.

**Grain:** One runtime outcome for one guardrail rule in one pipeline run.

**Primary key:** `guardrail_result_id`

**Relationships:**

* `guardrail_rule_id` → `METADATA_GUARDRAIL.guardrail_rule_id` (**N:1**). Many runtime outcomes can come from one authored guardrail rule.
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many runtime guardrail outcomes can refer to one logical catalogue table identity.
* **1:N**: One Guardrail Result can have many Guardrail Row Results when row level failure evidence is captured.

[View full schema](metadata/metadata_guardrail_results.md)

---

## [METADATA_GUARDRAIL_ROW_RESULTS](metadata/metadata_guardrail_row_results.md)

See which records did not meet the expectations.

**Grain:** One failed source row or DQ rule evidence row linked to one runtime guardrail result.

**Primary key:** `guardrail_row_result_id`

**Relationships:**

* `guardrail_result_id` → `METADATA_GUARDRAIL_RESULTS.guardrail_result_id` (**N:1**). Many row level failure evidence rows can belong to one Guardrail Result.
* `guardrail_rule_id` → `METADATA_GUARDRAIL.guardrail_rule_id` (**N:1**). Many row level failure evidence rows can trace back to one authored guardrail rule.
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many row level failure evidence rows can refer to one logical catalogue table identity.

[View full schema](metadata/metadata_guardrail_row_results.md)

---
