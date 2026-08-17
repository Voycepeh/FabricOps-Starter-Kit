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
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). The current Data Contract column retains its pre-Stage-2 name, but its stable hash value identifies the same logical table now exposed by Catalogue as table_id. Data Contract redesign is deferred to Stage 5.

[View full schema](metadata/metadata_data_contract.md)

---

## [METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)

See the tables and columns FabricOps has observed.

**Grain:** One table or column asset in one environment.

**Primary key:** `environment_name` + `table_id` + `column_id`

**Relationships:**

* **1:N**: A Catalogue table identity can be referenced by many Profile, Lineage, Source Observation, Enrichment, Access and Guardrail rows over time.

[View full schema](metadata/metadata_data_catalogue.md)

---

## [METADATA_SOURCE_OBSERVATION](metadata/metadata_source_observation.md)

See what FabricOps previously observed about the source data.

**Grain:** One partition observation within one source-table observation.

**Primary key:** `observation_id` + `partition_value`

**Relationships:**

* `table_id` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Many source observations can belong to one logical Catalogue table identity in an environment.

[View full schema](metadata/metadata_source_observation.md)

---

## [METADATA_DATA_PROFILED](metadata/metadata_data_profiled.md)

See the column-level profile metrics captured for a dataset snapshot.

**Grain:** One observed column in one profiling snapshot.

**Primary key:** `profile_id`

**Relationships:**

* `table_id` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Many column profile snapshots can describe the same logical Catalogue table over time.
* `column_id` → `METADATA_DATA_CATALOGUE.column_id` (**N:1**). Many profile snapshots can describe the same logical Catalogue column over time.
* **1:1**: One logical column Profile has one corresponding frequency distribution. The distribution is stored separately and flattened into multiple physical Frequency rows to avoid a large JSON payload in the Profile row.

[View full schema](metadata/metadata_data_profiled.md)

---

## [METADATA_DATA_PROFILED_FREQUENCY](metadata/metadata_data_profiled_frequency.md)

See the frequency distribution captured for a profiled column.

**Grain:** One flattened ranked value within one logical frequency distribution for a column Profile.

**Primary key:** `frequency_id`

**Relationships:**

* `profile_id` → `METADATA_DATA_PROFILED.profile_id` (**N:1**). Physical Frequency rows link back to the Profile that owns the logical distribution through profile_id.
* `profile_snapshot_id` → `METADATA_DATA_PROFILED.profile_snapshot_id` (**N:1**). Profile and Frequency are produced together in the same profiling snapshot.
* **1:1**: Logically this table stores the one frequency distribution belonging to a Profile; that distribution is physically flattened into multiple rows for storage.

[View full schema](metadata/metadata_data_profiled_frequency.md)

---

## [METADATA_DATA_LINEAGE](metadata/metadata_data_lineage.md)

See where the data came from and where it ends up.

**Grain:** One table participating as a source or target in one pipeline/profiling execution.

**Primary key:** `lineage_id`

**Relationships:**

* `table_id` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Many lineage participation records can refer to the same logical Catalogue table identity.
* `profile_snapshot_id` → `METADATA_DATA_PROFILED.profile_snapshot_id` (**N:1**). The lineage participation is recorded for the same profiling execution identified by profile_snapshot_id.

[View full schema](metadata/metadata_data_lineage.md)

---

## [METADATA_ENRICHMENT](metadata/metadata_enrichment.md)

Add business and governance context to the data.

**Grain:** One appended enrichment value for one table or column identity.

**Primary key:** `enrichment_id`

**Relationships:**

* `metadata_key` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Until the Stage 3 rename, table-level enrichment keeps metadata_key while referencing the same stable value now exposed by Catalogue as table_id.
* `metadata_key` → `METADATA_DATA_CATALOGUE.column_id` (**N:1**). Until the Stage 3 rename, column-level enrichment keeps metadata_key while referencing the same stable value now exposed by Catalogue as column_id.

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

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Until Stage 4 renames the Guardrail identity fields, metadata_table_key carries the same stable value now exposed by Catalogue as table_id.
* `metadata_column_key` → `METADATA_DATA_CATALOGUE.column_id` (**N:1**). Until Stage 4 renames the Guardrail identity fields, metadata_column_key carries the same stable value now exposed by Catalogue as column_id.
* **1:N**: One Guardrail rule can produce many Guardrail Results across pipeline runs through guardrail_rule_id.
* **1:N**: One Guardrail rule can produce many Guardrail Row Results when DQ quarantine evidence is captured.

[View full schema](metadata/metadata_guardrail.md)

---

## [METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)

See whether the expectations of the data in the ETL pipeline run are met.

**Grain:** One runtime outcome for one guardrail rule in one pipeline run.

**Primary key:** `guardrail_result_id`

**Relationships:**

* `guardrail_rule_id` → `METADATA_GUARDRAIL.guardrail_rule_id` (**N:1**). Many runtime outcomes can come from one authored Guardrail rule.
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Until Stage 4 normalization, the result keeps metadata_table_key while carrying the same stable Catalogue table_id value.

[View full schema](metadata/metadata_guardrail_results.md)

---

## [METADATA_GUARDRAIL_ROW_RESULTS](metadata/metadata_guardrail_row_results.md)

See the failed or quarantined rows produced by a Data Quality guardrail.

**Grain:** One failed-row evidence record produced by one Guardrail rule evaluation.

**Primary key:** `guardrail_row_result_id`

**Relationships:**

* `guardrail_rule_id` → `METADATA_GUARDRAIL.guardrail_rule_id` (**N:1**). Row-level DQ quarantine evidence belongs directly to the Guardrail rule that produced it.
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Until Stage 4 normalization, the row result keeps metadata_table_key while carrying the same stable Catalogue table_id value.

[View full schema](metadata/metadata_guardrail_row_results.md)

---
