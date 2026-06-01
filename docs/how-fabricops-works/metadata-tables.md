# Metadata Tables

The governance `metadata_lakehouse` is the shared coordination layer between governance and engineering. Notebook templates write evidence to the configured metadata target, and later notebooks reuse approved evidence for enforcement and handover.

<figure markdown>
  ![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }
  <figcaption>Shared metadata keeps agreements, profiles, lineage, approved rules, classifications, context, and handover evidence connected.</figcaption>
</figure>

## Lightweight conceptual model

Start with this small conceptual model. The physical `METADATA_*` reference later on this page shows how the starter kit stores the detailed evidence.

| Conceptual table | Main writer | What it is used for |
| --- | --- | --- |
| `data_stewards` | `01_da` or steward administration | Keeps steward and owner assignments available for agreement intake. |
| `data_agreements` | `01_da` | Records purpose, scope, intended use, and agreement context. |
| `notebook_registry` | All workflow notebooks | Links notebook evidence to agreements, workspaces, tables, and notebook URLs. |
| `data_profiles` | `02_ex` and `03_pc` | Stores exploration and output-table profile evidence. |
| `data_lineage` | `03_pc` | Captures table-level source-to-output lineage and transformation evidence. |
| `data_quality_rules` | `04_gov`, enforced by `03_pc` | Stores reviewed and approved quality expectations. |
| `sensitivity_classification` | `04_gov` | Stores approved sensitivity, confidentiality, and handling context. |
| `business_context` | `04_gov` | Stores descriptions, units, derivation notes, and glossary context. |
| `handover_manifest` | Handover generation | Stores or publishes generated handover and AI-ready manifest records. |

Metadata reads and writes must use the metadata route from `00_env_config`, for example `read_lakehouse_table(CONFIG, env_name, "metadata", "<metadata_table>")` and `write_lakehouse_table(df, CONFIG, env_name, "metadata", "<metadata_table>", mode="append")`.

## Detailed physical table reference

FabricOps keeps separate append-only metadata tables when workflow outputs have different ownership, grain, or lifecycle. The handover is generated from approved metadata and run evidence; it is not another competing source table.

The physical workflow evidence tables are:

| No. | Table | Grain | Why it exists |
| --: | --- | --- | --- |
| 1 | `METADATA_DATA_AGREEMENT` | One row per agreement version | Defines the agreement intake and usage-boundary anchor. |
| 2 | `METADATA_DATA_CATALOGUE` | One row per table per profiling run or latest table snapshot | Captures table-level catalogue and profile evidence from exploration or pipeline profiling. |
| 3 | `METADATA_COLUMN_BUSINESS_CONTEXT` | One row per table-column per approved version | Stores approved business meaning, descriptions, units, derivation, and glossary terms. |
| 4 | `METADATA_COLUMN_GOVERNANCE` | One row per table-column per approved version | Stores approved classification, PII, sensitivity, confidentiality, and handling requirements. |
| 5 | `METADATA_DQ_RULES` | One row per rule version | Stores approved executable data quality expectations. |
| 6 | `METADATA_NOTEBOOK_REGISTRY` | One row per notebook tied to an agreement | Links workflow notebooks to agreements, tables, workspaces, and URLs. |
| 7 | `METADATA_DQ_RESULTS` | One row per rule execution per run | Stores runtime results of approved DQ rules. |
| 8 | `METADATA_DRIFT_RESULTS` | One row per table per drift check | Stores schema, profile, and data-drift evidence over time. |
| 9 | `METADATA_LINEAGE_EVENTS` | One row per source-target table event | Stores source-to-target lineage and transformation evidence. |

Maintained reference metadata includes:

| Table | Grain | Why it exists |
| --- | --- | --- |
| `METADATA_DATA_STEWARD` | One row per steward assignment or effective period | Maintains the selectable steward source of truth for agreement intake. |

`METADATA_DATA_STEWARD` is maintained reference metadata rather than workflow evidence. Administrators or stewards maintain real rows and set `is_active = true` for selectable stewards. Setup may create or check the empty table, but it should not seed fake steward profiles.

## Notebook responsibilities

| Notebook family | Metadata responsibility |
| --- | --- |
| `01_da` | Defines the agreement and selects an active steward. |
| `02_ex` | Profiles and discovers source or unified data. |
| `04_gov` | Approves column business context, classifications, and quality rules. |
| `03_pc` | Enforces approved rules and records DQ results, drift results, and lineage events. |
| All workflow notebooks | Register notebook traceability. |
| Handover generation | Assembles views and exports reusable support artifacts. |

## Detailed columns by physical table

The sections below preserve the implementation-oriented table reference. Add columns deliberately when the workflow needs more evidence; keep the conceptual model small for new readers.
### `METADATA_DATA_AGREEMENT`

**Why it exists:** This is the highest-grain agreement-level contract anchor written by the `01_da_*` **Data Agreement Intake / Usage Boundary** notebook. It records the captured usage boundary in which downstream notebook work is allowed to operate. It is not a workbook-style data dictionary and does not store detailed table or column metadata.

**Grain:** One row = one agreement version. Agreement changes are append-only: a new revision adds a row rather than overwriting a previous version.

**Stable agreement key:** `agreement_id` identifies the agreement across versions.

**Append-only version key:** `contract_version` identifies one semantic version of that agreement.

**Unique agreement-version identity:** `agreement_id + contract_version`.

**Main foreign keys:** `steward_id` references `METADATA_DATA_STEWARD`. Downstream metadata tables reference `agreement_id` and, where version-specific traceability is needed, `contract_version`.

**Main writer notebook:** `01_da_*` through `render_agreement_intake_app()`. Advanced customized flows may call `collect_agreement_metadata()` and `commit_agreement_metadata()` directly.

**Main downstream use:** Scopes every catalogue, context, governance, rule, result, drift, lineage, and handover output.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| agreement_id | DA-20260529-100000 | 01_da_* | Implemented | Stable agreement key reused across appended versions |
| contract_version | 1.0.0 | 01_da_* | Implemented | Append-only semantic agreement version key |
| agreement_name | Governed Reporting Agreement | 01_da_* | Implemented | Human-readable agreement name |
| steward_id | steward-001 | 01_da_* | Implemented | Steward reference key resolved from `METADATA_DATA_STEWARD` |
| business_purpose | Support governed reporting | 01_da_* | Implemented | Business reason for the agreement |
| approved_usage | Approved reporting only | 01_da_* | Implemented | Allowed use within the agreement boundary |
| restricted_usage | No redistribution | 01_da_* | Implemented | Restricted or prohibited uses |
| allowed_consumer_type | Internal Department | 01_da_* | Implemented | Permitted consumer category |
| expected_output | Dashboard | 01_da_* | Implemented | Expected output type |
| source_system | ERP | 01_da_* | Implemented | Source-system category |
| refresh_frequency | Daily | 01_da_* | Implemented | Expected refresh cadence |
| retention_expectation | Retain approved extracts for 30 days | 01_da_* | Implemented | Retention boundary or expectation |
| start_date | 2026-06-01 | 01_da_* | Implemented | Agreement start date |
| expiry_date | 2027-05-31 | 01_da_* | Implemented | Agreement expiry date used to derive current agreement status dynamically |
| renewal_required | Yes | 01_da_* | Implemented | Whether renewal is expected |
| _committed_by | user@example.com | `metadata.build_runtime_audit_fields(...)` | Implemented | Fabric runtime user who committed the version |
| _committed_at | 2026-06-01T10:00:00+00:00 | `metadata.build_runtime_audit_fields(...)` | Implemented | Agreement-version commit timestamp |
| _notebook_name | 01_da_governed_reporting | `metadata.build_runtime_audit_fields(...)` | Implemented | Fabric notebook that committed the version |
| _workspace_name | Fabric Workspace | `metadata.build_runtime_audit_fields(...)` | Implemented | Fabric workspace captured from runtime context |
| _metadata_lakehouse_name | Metadata Lakehouse | `metadata.build_runtime_audit_fields(...)` | Implemented | Configured metadata lakehouse captured at commit time |
| _activity_id | activity-id | `metadata.build_runtime_audit_fields(...)` | Implemented | Fabric activity identifier |

Agreement rows persist `steward_id` only. Steward identity and organizational fields resolve from `METADATA_DATA_STEWARD`; they are not copied into each agreement version. Agreement status is also not persisted: consumers derive the current status dynamically from `expiry_date` so it remains correct after the commit date.

!!! note "Keep workbook-style dictionary detail downstream"
    Detailed table and column metadata belongs downstream, not in `METADATA_DATA_AGREEMENT`. LYRA-style workbook or data-dictionary fields such as column description, data type, field classification, allowed values, top values, missing data, PII/sensitive indicators, and business rules belong in `METADATA_DATA_CATALOGUE`, `METADATA_COLUMN_BUSINESS_CONTEXT`, `METADATA_COLUMN_GOVERNANCE`, and `METADATA_DQ_RULES` according to their grain and ownership.

### `METADATA_DATA_STEWARD`

**Why it exists:** This is the maintained source of truth for data steward identity and organizational assignment used by `01_da_*` agreement intake.

**Grain:** One row per steward assignment/effective period.

**Primary key:** `steward_id + effective_from`, or `steward_id` if each steward row is maintained as the current row only.

**Main foreign keys:** None required. `METADATA_DATA_AGREEMENT.steward_id` references this table.

**Main maintainer:** Administrators or stewards maintain real reference rows. Setup creates or checks the table without seeding fake data.

**Main downstream use:** `01_da_*` uses active/effective rows for the data steward dropdown. Agreement rows persist `steward_id` only. Historical displays resolve steward details by `steward_id` and the agreement start/effective date.

**Columns:**

| Column | Example value | Maintainer | Status | Purpose |
| --- | --- | --- | --- | --- |
| steward_id | steward-001 | Admin or steward | Maintained | Stable steward reference key persisted by agreement rows |
| data_steward_name | Configured Steward | Admin or steward | Maintained | Steward display name |
| data_steward_email | steward@example.com | Admin or steward | Maintained | Steward contact email |
| domain | Operations | Admin or steward | Maintained | Steward domain |
| department | Analytics | Admin or steward | Maintained | Steward department |
| faculty | Shared Services | Admin or steward | Maintained | Steward faculty or organizational grouping |
| effective_from | 2026-01-01 | Admin or steward | Maintained | Start date for the steward assignment |
| effective_to | 2026-12-31 | Admin or steward | Maintained | Optional end date for the steward assignment |
| is_active | true | Admin or steward | Maintained | Whether the steward assignment is available for active use |
| created_at | 2026-01-01T09:00:00+00:00 | Metadata runtime | Maintained | Reference-row creation timestamp |
| updated_at | 2026-05-29T09:00:00+00:00 | Metadata runtime | Maintained | Reference-row latest-update timestamp |

Do not put steward reference rows inside `METADATA_DATA_CATALOGUE`. The catalogue stores table-level profiling and discovery evidence from `02_ex_*`; the steward table is a maintained reference dimension.

### `METADATA_DATA_CATALOGUE`

**Why it exists:** This is the table-level catalogue created from profiling and discovery. It records what table was profiled, basic table health, schema summary, row count, column count, and when the table was observed.

**Grain:** One row per agreement, table, and profiling run. A latest view can expose one current row per table.

**Primary key:** `catalogue_id` or `metadata_table_key` plus `profile_run_id`.

**Main foreign keys:** `agreement_id`.

**Main writer notebook:** `02_ex_*` through `profile_dataframe()` or profiling writer.

**Main downstream use:** Feeds table-level contract summary, column catalogue, dashboard, and handover JSON.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| catalogue_id | cat_lyra_output_20260529 | profiling writer | Planned | Unique catalogue observation row |
| agreement_id | lyra_deid_v1 | 02_ex_* | Planned / partial | Parent agreement key |
| profile_run_id | run_20260529_091000 | profile_dataframe() | Planned | Profiling run identifier |
| metadata_table_key | hash value | metadata helper / profiling writer | Planned / partial | Stable table join key |
| environment_name | prod | 00_env_config / runtime context | Partial | Environment context |
| dataset_name | lyra | 02_ex_* | Partial | Dataset or data product name |
| table_name | res_output_lyra_deid_all_v1 | profile_dataframe() | Collected | Governed table name |
| source_system | student_records | 02_ex_* | Planned | Source system name |
| table_type | lakehouse_table | 02_ex_* | Planned | Asset type |
| row_count | 10000 | profile_dataframe() | Collected | Profiled row count |
| column_count | 48 | profile_dataframe() | Planned / derivable | Profiled column count |
| schema_hash | a91f... | profiling writer | Planned | Detect schema changes |
| profile_status | complete | profiling writer | Planned | Profiling completion status |
| profiled_at | 2026-05-29T09:10:00Z | profile_dataframe() | Collected as run timestamp | Profiling timestamp |
| profile_payload_json | {"columns":[...]} | profiling writer | Planned | Extended table and column profile payload |

Do not put approved descriptions, PII labels, or DQ rule definitions here. This table owns observed catalogue and profiling evidence only.

### `METADATA_COLUMN_BUSINESS_CONTEXT`

**Why it exists:** This stores approved column-level business meaning. It is separate because descriptions, units, derivation, semantic meaning, and glossary mapping are human-reviewed context, not raw profiling output.

**Grain:** One row per agreement, table, column, and approved business-context version.

**Primary key:** `business_context_id`.

**Main foreign keys:** `agreement_id`, `metadata_table_key`, `metadata_column_key`.

**Main writer notebook:** `04_gov_*` through `review_business_context()` and `write_business_context()`.

**Main downstream use:** Feeds the column catalogue, handover JSON, ODCS schema descriptions, and OpenMetadata column descriptions.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| business_context_id | bc_student_id_v1 | write_business_context() | Planned | Unique business context row |
| agreement_id | lyra_deid_v1 | 04_gov_* | Planned / partial | Parent agreement key |
| metadata_table_key | hash value | metadata helper | Implemented helper | Stable table join key |
| metadata_column_key | hash value | metadata helper | Implemented helper | Stable column join key |
| table_name | res_output_lyra_deid_all_v1 | review_business_context() | Collected | Parent table |
| column_name | student_id | review_business_context() | Collected | Column being described |
| ai_suggested_business_context | Identifier for student record | review_business_context() | Collected | AI suggested meaning |
| approved_business_context | Unique de-identified student identifier | write_business_context() | Collected | Human approved meaning |
| approved_description | Unique de-identified student identifier | write_business_context() | Planned / partial | Export friendly description |
| units | days | 04_gov_* business review | Planned | Unit of measure |
| source_derivation | Hashed from source student number | 04_gov_* business review | Planned | Business derivation note |
| semantic_domain | identity | 04_gov_* business review | Planned | Business grouping |
| glossary_term | Student Identifier | 04_gov_* business review | Planned | Glossary mapping |
| business_context_notes | Use only for matching | review_business_context() | Collected | Reviewer notes |
| approval_status | approved | write_business_context() | Collected | Review state |
| reviewer_notes | Approved with wording change | review_business_context() | Collected | Review comment |
| approved_by | user@org.com | review context / metadata runtime | Partial | Approver |
| approved_at | 2026-05-29T10:30:00Z | write_business_context() | Collected | Approval timestamp |
| version | 1 | metadata writer | Planned | Version of approved context |
| is_active | true | metadata writer | Planned | Current active context |

Do not put PII, sensitivity, confidentiality, row count, or DQ result fields here.

### `METADATA_COLUMN_GOVERNANCE`

**Why it exists:** This stores approved column-level classification and sensitivity decisions. It is separate from business context because governance has a different review purpose, risk profile, and audit requirement.

**Grain:** One row per agreement, table, column, and approved governance version.

**Primary key:** `governance_context_id`.

**Main foreign keys:** `agreement_id`, `metadata_table_key`, `metadata_column_key`.

**Main writer notebook:** `04_gov_*` through `review_governance()` and `write_governance()`.

**Main downstream use:** Feeds sensitivity labels, PII flags, confidentiality metadata, dashboard filters, ODCS custom properties, and OpenMetadata tags/classifications.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| governance_context_id | gov_student_id_v1 | write_governance() | Planned | Unique governance row |
| agreement_id | lyra_deid_v1 | 04_gov_* | Planned / partial | Parent agreement key |
| metadata_table_key | hash value | metadata helper | Implemented helper | Stable table join key |
| metadata_column_key | hash value | metadata helper | Implemented helper | Stable column join key |
| table_name | res_output_lyra_deid_all_v1 | review_governance() | Collected | Parent table |
| column_name | student_id | review_governance() | Collected | Column being classified |
| ai_suggested_personal_identifier_classification | direct_identifier | review_governance() | Collected | AI suggested classification |
| approved_personal_identifier_classification | de_identified_identifier | write_governance() | Collected | Human approved PII classification |
| field_classification | identifier | 04_gov_* governance review | Planned / partial | Field category |
| confidentiality_label | restricted | write_governance() | Collected | Confidentiality level |
| sensitivity_label | high | 04_gov_* governance review | Planned | Sensitivity summary |
| handling_requirement | Do not export outside approved workspace | 04_gov_* governance review | Planned | Handling instruction |
| masking_requirement | hash before sharing | 04_gov_* governance review | Planned | Masking instruction |
| retention_requirement | 7 years | 04_gov_* governance review | Planned | Retention requirement |
| reviewer_notes | Treat as restricted | review_governance() | Collected | Governance reviewer notes |
| approval_status | approved | write_governance() | Collected | Review state |
| approved_by | user@org.com | write_governance() | Collected | Approver |
| approved_at | 2026-05-29T10:30:00Z | write_governance() | Collected | Approval timestamp |
| version | 1 | metadata writer | Planned | Version of governance decision |
| is_active | true | metadata writer | Planned | Current active classification |

Do not put business description, units, source derivation, row count, or DQ execution results here.

### `METADATA_DQ_RULES`

**Why it exists:** This stores approved executable data quality expectations. It must be separate from DQ results because the rule is the contract expectation, while the result is evidence from one run.

**Grain:** One row per rule version.

**Primary key:** `rule_key`.

**Main foreign keys:** `agreement_id`, `metadata_table_key`, `metadata_column_key`.

**Main writer notebook:** `03_pc_*` through `write_dq_rules()`, with candidates possibly suggested by `02_ex_*`.

**Main downstream use:** Used by `03_pc_*` to enforce quality and by assembled views to describe business rules and allowed values.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| rule_key | hash value | metadata.build_dq_rule_key | Implemented helper | Stable DQ rule key |
| rule_id | student_id_not_null | write_dq_rules() | Collected | Human readable rule ID |
| agreement_id | lyra_deid_v1 | 03_pc_* | Planned | Parent agreement key |
| metadata_table_key | hash value | _attach_rule_metadata_keys() | Partial | Table affected by rule |
| metadata_column_key | hash value | _attach_rule_metadata_keys() | Partial | Column affected by rule when applicable |
| table_name | res_output_lyra_deid_all_v1 | write_dq_rules() | Collected | Table affected by rule |
| column_name | student_id | write_dq_rules() | Collected / conditional | Column affected by rule |
| rule_type | not_null | write_dq_rules() | Collected | Rule type |
| severity | error | write_dq_rules() | Collected | Enforcement severity |
| description | Student ID must not be null | write_dq_rules() | Collected | Rule description |
| allowed_values | ["active","inactive"] | accepted_values rule payload | Conditional | Accepted value list |
| lower_bound | 0 | value_range rule payload | Conditional | Minimum accepted value |
| upper_bound | 100 | value_range rule payload | Conditional | Maximum accepted value |
| regex_pattern | ^[A-Z0-9]+$ | regex_format rule payload | Conditional | Required pattern |
| rule_json | {"type":"not_null","columns":["student_id"]} | write_dq_rules() | Collected | Full executable rule payload |
| is_active | true | write_dq_rules() | Collected | Active rule flag |
| action_type | approved | write_dq_rules() | Collected | Rule lifecycle action |
| action_by | user@org.com | write_dq_rules() | Collected | User who approved or changed rule |
| action_ts | 2026-05-29T10:40:00Z | write_dq_rules() | Collected | Rule action timestamp |
| action_reason | Approved after governance review | write_dq_rules() | Collected | Approval/change reason |
| rule_source | ai_widget_approval | write_dq_rules() | Collected | How rule was created |
| version | 1 | metadata writer | Planned / derivable | Rule version |

Do not put pass or fail counts here. Those belong in METADATA_DQ_RESULTS.

### `METADATA_NOTEBOOK_REGISTRY`

**Why it exists:** This ties notebooks to the agreement. It records which notebook plays which role, where it lives in Fabric, which workspace it belongs to, and who registered it.

**Grain:** One row per agreement and notebook registration.

**Primary key:** `notebook_registry_key` or composite notebook identity plus `registered_at`.

**Main foreign keys:** `agreement_id`.

**Main writer notebook:** All notebooks through `register_current_notebook()`.

**Main downstream use:** Lets the handover point back to the notebooks that produced or approved the evidence.

!!! important "Notebook registry function"
    Use `register_current_notebook()`, not `register_notebook_metadata()`.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| notebook_registry_key | hash value | register_current_notebook() enhancement | Planned | Stable notebook registry key |
| agreement_id | lyra_deid_v1 | register_current_notebook() | Collected | Agreement this notebook supports |
| environment_name | prod | register_current_notebook() | Collected | Environment context |
| dataset_name | lyra | register_current_notebook() | Collected | Dataset or data product |
| table_name | res_output_lyra_deid_all_v1 | register_current_notebook() | Collected | Table context if applicable |
| topic | profiling | register_current_notebook() | Collected | Notebook topic |
| pipeline_name | lyra_pipeline | register_current_notebook() | Collected | Pipeline or workflow name |
| notebook_type | 04_gov | register_current_notebook() | Collected | Notebook family |
| workspace_id | Fabric workspace ID | register_current_notebook() | Collected | Fabric workspace ID |
| workspace_name | ODI Dev | register_current_notebook() | Collected | Fabric workspace name |
| notebook_id | Fabric notebook ID | register_current_notebook() | Collected | Fabric notebook ID |
| notebook_name | 04_gov_lyra_column_review | register_current_notebook() | Collected | Fabric notebook name |
| notebook_url | https://fabric.microsoft.com/... | register_current_notebook() | Collected | Link to notebook |
| user_name | Voyce | register_current_notebook() | Collected | Registering user |
| user_id | user-guid | register_current_notebook() | Collected | Registering user ID |
| registered_at | 2026-05-29T10:30:00Z | register_current_notebook() | Collected | Registration timestamp |

Do not put profiling metrics, business context, classification, or DQ results here. This table owns traceability only.

### `METADATA_DQ_RESULTS`

**Why it exists:** This stores runtime evidence from executing approved DQ rules. It shows whether each rule passed, failed, or quarantined rows for a specific run.

**Grain:** One row per rule execution per run.

**Primary key:** `dq_result_id`.

**Main foreign keys:** `agreement_id`, `rule_key`, `metadata_table_key`, `metadata_column_key`, `run_id`.

**Main writer notebook:** `03_pc_*` through `enforce_dq()` and DQ result writer.

**Main downstream use:** Feeds the quality section of dashboards, assembled views, and handover exports.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| dq_result_id | dqres_20260529_student_id_not_null | DQ result writer | Planned | Unique DQ result row |
| run_id | run_20260529_110000 | 03_pc_* runtime context | Partial | Execution run key |
| agreement_id | lyra_deid_v1 | 03_pc_* | Planned | Parent agreement key |
| rule_key | hash value | enforce_dq() | Partial | Rule that was executed |
| rule_id | student_id_not_null | enforce_dq() | Partial | Human readable rule ID |
| metadata_table_key | hash value | metadata helper | Planned | Affected table |
| metadata_column_key | hash value | metadata helper | Planned | Affected column when applicable |
| table_name | res_output_lyra_deid_all_v1 | enforce_dq() | Partial | Table checked |
| column_name | student_id | enforce_dq() | Partial | Column checked when applicable |
| status | passed | enforce_dq() | Partial | Rule result status |
| passed_count | 9997 | DQ result enhancement | Planned | Passing row count |
| failed_count | 3 | DQ result enhancement | Planned | Failing row count |
| quarantine_count | 3 | enforce_dq() / DQ writer | Partial | Quarantined row count |
| failure_sample_path | Tables/dq_failures/student_id_not_null | DQ result enhancement | Planned | Pointer to failed sample |
| evaluated_at | 2026-05-29T11:00:00Z | DQ result writer | Planned | Evaluation timestamp |
| result_payload_json | {"failed_count":3,"quarantine_count":3} | DQ result writer | Planned | Extended DQ result payload |

Do not put rule definition details here except IDs needed to join back to METADATA_DQ_RULES.

### `METADATA_DRIFT_RESULTS`

**Why it exists:** This stores drift evidence over time. It records whether the current table differs from the approved or previous baseline in schema, profile, or expected structure.

**Grain:** One row per agreement, table, and drift check run.

**Primary key:** `drift_result_id`.

**Main foreign keys:** `agreement_id`, `metadata_table_key`, `run_id`, `baseline_run_id`.

**Main writer notebook:** `03_pc_*` or `04_gov_*` drift monitoring step.

**Main downstream use:** Feeds contract validity checks, dashboard warnings, and handover action items.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| drift_result_id | drift_lyra_20260529 | drift writer | Planned | Unique drift result row |
| run_id | run_20260529_110000 | runtime context | Planned | Execution run key |
| agreement_id | lyra_deid_v1 | 03_pc_* or 04_gov_* | Planned | Parent agreement key |
| metadata_table_key | hash value | metadata helper | Planned | Table checked for drift |
| table_name | res_output_lyra_deid_all_v1 | drift check | Partial | Table checked |
| baseline_run_id | run_20260429_110000 | drift check | Planned | Baseline run |
| current_run_id | run_20260529_110000 | drift check | Planned | Current comparison run |
| drift_type | schema | drift check | Partial | Drift category |
| status | warning | drift check | Partial | Drift outcome |
| can_continue | true | drift check | Partial | Whether pipeline can continue |
| added_columns_json | ["new_status"] | drift enhancement | Planned | Added columns |
| removed_columns_json | [] | drift enhancement | Planned | Removed columns |
| changed_columns_json | ["status_code"] | drift enhancement | Planned | Changed columns |
| metric_changes_json | {"row_count_delta_pct":4.2} | drift enhancement | Planned | Profile metric changes |
| drift_summary | 1 new nullable column detected | drift check | Planned | Human readable summary |
| checked_at | 2026-05-29T11:05:00Z | drift writer | Planned | Drift check timestamp |

Do not put DQ pass or fail counts here. Those belong in METADATA_DQ_RESULTS.

### `METADATA_LINEAGE_EVENTS`

**Why it exists:** This stores source-to-target movement and transformation evidence. It explains where the table came from and how it was produced.

**Grain:** One row per source-target table relationship or transformation event.

**Primary key:** `lineage_event_id`.

**Main foreign keys:** `agreement_id`, `source_metadata_table_key`, `target_metadata_table_key`, `run_id`, `notebook_registry_key`.

**Main writer notebook:** `03_pc_*` lineage capture or transformation summary step.

**Main downstream use:** Feeds handover, OpenMetadata lineage payloads, and operational traceability.

**Columns:**

| Column | Example value | Writer notebook/function | Status | Purpose |
| --- | --- | --- | --- | --- |
| lineage_event_id | lin_lyra_raw_to_output_20260529 | lineage writer | Planned | Unique lineage event |
| run_id | run_20260529_110000 | runtime context | Planned | Execution run key |
| agreement_id | lyra_deid_v1 | 03_pc_* | Planned | Parent agreement key |
| source_metadata_table_key | hash value | metadata helper | Planned | Upstream table key |
| target_metadata_table_key | hash value | metadata helper | Planned | Downstream table key |
| source_table | raw_lyra_students | lineage capture | Partial | Upstream table |
| target_table | res_output_lyra_deid_all_v1 | lineage capture | Partial | Downstream table |
| transformation_type | hash, filter, aggregate | lineage enhancement | Planned | Transformation category |
| transformation_summary | De-identified student records and filtered active population | lineage capture | Partial | Human readable transformation note |
| columns_used_json | ["student_no","status_code"] | lineage enhancement | Planned | Source columns used |
| columns_created_json | ["student_id","active_flag"] | lineage enhancement | Planned | Output columns created |
| notebook_registry_key | hash value | register_current_notebook() | Planned | Producing notebook link |
| captured_at | 2026-05-29T11:10:00Z | lineage writer | Planned | Capture timestamp |
| lineage_payload_json | {"source":"raw_lyra_students","target":"res_output_..."} | lineage writer | Planned | Extended lineage payload |

Do not put governance labels, DQ results, or profiling metrics here.


## Next step

Continue to [Metadata Dashboard](metadata-dashboard.md) to see how the source evidence becomes useful to people and tools.
