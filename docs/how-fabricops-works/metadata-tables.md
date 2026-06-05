# Metadata Tables

The governance `metadata_lakehouse` is the shared coordination layer between governance and engineering. Notebook templates write evidence to the configured metadata target, and later notebooks reuse approved evidence for enforcement, lineage, governance review, and handover.

  ![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }


## Architecture

Use the architecture diagram as the source of truth for the starter kit metadata model. It shows the key metadata domains and relationships. The detailed `METADATA_*` reference later on this page preserves the wider implementation columns used by the starter kit.

| Metadata tables | Level | Main writer | What it is used for |
| --- | --- | --- | --- |
| `data_stewards` | Agreement setup | `01_da` or steward administration | Maintains steward identities used during agreement intake. |
| `data_agreements` | Agreement setup | `01_da` | Anchors the agreement name, domain, steward, and status. |
| `notebook_registry` | Notebook traceability | All workflow notebooks | Links every `02_ex` and `03_pc` notebook to a data agreement. |
| `data_access` | Table level | Lakehouse or warehouse access logs | Records table access assignments, access levels, and expiry windows. |
| `data_catalogue` | Table level | `02_ex` and `03_pc` | Stores the central table registry for profiled sources and pipeline outputs. |
| `data_lineage` | Table level | `03_pc` | Captures source-to-target table lineage during pipeline runtime. |
| `data_contracts` | Table level | `04_gov`, enforced by enhanced `03_pc` after approval | Stores table-level schema, required-rule, drift, and enforcement guardrails. |
| `data_catalogue` | Column level | `02_ex` and `03_pc` | Stores column names, data types, positions, and nullability. |
| `data_lineage` | Column level | `03_pc`, assisted by AI where needed | Captures source-to-target column lineage. |
| `data_quality_rules` | Column level | `04_gov`, enforced by enhanced `03_pc` after approval | Stores approved column-level quality expectations. |
| `sensitivity_classification` | Column level | `04_gov` | Stores approved column sensitivity labels and handling context. |
| `business_context` | Column level | `04_gov` | Stores approved business definitions, ownership, and usage notes. |

Metadata reads and writes must use the metadata route from `00_env_config`, for example:

```python
read_lakehouse_table(CONFIG, env_name, "metadata", "<metadata_table>")
write_lakehouse_table(df, CONFIG, env_name, "metadata", "<metadata_table>", mode="append")
```

## Table Relationships

| Relationship | Meaning |
| --- | --- |
| `data_stewards` 1 → many `data_agreements` | One steward can own or support many agreements. |
| `data_agreements` 1 → many `notebook_registry` | Every workflow notebook is linked back to an agreement. |
| `data_agreements` 1 → many table-level `data_catalogue` | An agreement can cover many profiled or produced tables. |
| Table-level `data_catalogue` 1 → many column-level `data_catalogue` | Each table has many column records. |
| Table-level `data_catalogue` 1 → many table-level `data_lineage` | Each table can participate in many source-target lineage events. |
| Column-level `data_catalogue` 1 → many column-level `data_lineage` | Each column can participate in many source-target column mappings. |
| Table-level `data_catalogue` 1 → many `data_access` | Table access evidence is attached to the table. |
| Table-level `data_catalogue` 1 → many `data_contracts` | Contracts are table-level guardrails. |
| Column-level `data_catalogue` 1 → many `data_quality_rules` | Rules are column-level expectations, except where a rule is table-wide. |
| Column-level `data_catalogue` 1 → many `sensitivity_classification` | Classification decisions are column-level governance records. |
| Column-level `data_catalogue` 1 → many `business_context` | Business meaning and usage notes are column-level governance records. |

## Standard runtime audit columns

All metadata tables written by Fabric notebooks should include the same runtime audit fields. They are defined once here and not repeated in every table reference below to keep the page lightweight.

| Column | Example | Purpose |
| --- | --- | --- |
| `_committed_by` | `user@example.com` | Fabric runtime user who committed the row. |
| `_committed_at` | `2026-06-01T10:00:00+00:00` | Row commit timestamp, used for traceability and latest-row selection. |
| `_notebook_name` | `01_da_governed_reporting` | Fabric notebook that committed the row. |
| `_workspace_name` | `Fabric Workspace` | Fabric workspace captured from runtime context. |
| `_metadata_lakehouse_name` | `Metadata Lakehouse` | Configured metadata lakehouse captured at commit time. |
| `_activity_id` | `activity-id` | Fabric activity identifier for troubleshooting. |

These fields are populated by runtime audit helpers, for example `metadata.build_runtime_audit_fields(...)`. They are stored in backend tables but hidden from normal widget users.

## Lightweight `01_da` intake

`00_env_config` defines the physical steward, agreement, and evidence metadata tables plus the editable configuration for the visible `01_da` intake widgets. FabricOps currently supports two `01_da` layouts:

- **Option A** is a compact section switcher via `widget_render_agreement_intake_app(...)`.
- **Option B** is separate widget cells for Data Steward, Data Agreement, and Agreement Evidence via `widget_render_data_steward(...)`, `widget_render_data_agreement(...)`, and `widget_render_agreement_evidence(...)`. Use Option B if Fabric output scrolling feels jumpy or if users prefer rerunning one section at a time.

Both layouts expose the same workflow sections:

1. **Data Steward** maintenance creates or updates append-only steward assignments.
2. **Data Agreement** maintenance creates append-only agreement versions and selects from currently active stewards.
3. **Agreement Evidence** optionally uploads supporting documents or screenshots for an existing agreement version.

Each intake widget exposes a short standard field list plus configured custom fields. Table-backed selectors in `01_da` are searchable so long steward, agreement, and agreement-version lists can be filtered without rerunning the notebook cell. The search matches friendly labels plus stable IDs and key metadata fields, while the value saved to metadata remains the stable key: `steward_id` for steward selections, `agreement_id` for agreement selections, and `agreement_id||contract_version` for agreement evidence version selections. The selector also renders read-only selected-record context below the search controls so long steward names, agreement names, IDs, versions, roles, contacts, and recipients remain visible even when option labels are too long for the control.

Agreement identifiers (`agreement_id` and `contract_version`) are backend-generated context: new agreements receive an ID and `1.0.0` version automatically, while updates carry the stable ID forward and increment the version. Normal users should not manually edit these technical identifiers.

Add organization-specific concepts such as a faculty, department, division, consumer group, or expected output in `00_env_config`; the widget stores those values in `custom_fields_json`. Custom field definitions support `text`, `textarea`, `select`, `multiselect`, `date`, and `boolean` controls. Do not add a physical column for each local intake concept.

## List of Metadata Tables

`Input type` shows whether the value is entered by a user, generated by the starter kit, derived from other metadata, collected at runtime, or planned for future support.

### `METADATA_DATA_STEWARD`

| Item | Details |
| --- | --- |
| Concept | `data_stewards` |
| Purpose | Maintained source of truth for data steward identity used during agreement intake. Use optional group assignments for organisation-specific labels such as faculty or department. |
| Grain | One row per steward assignment or effective period. |
| Key relationships | `METADATA_DATA_AGREEMENT.steward_id` references this table. |
| Main writer | Steward administrator, setup process, or `01_da_*` if steward administration is handled inside the starter kit. |
| Main downstream use | Used by `01_da_*` to select an active steward for each data agreement. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| steward_id | STEW-8d889875dd | Backend-generated | Stable steward reference key generated by the steward save path and persisted by agreement rows. Normal users do not manually edit it. |
| steward_name | Configured Steward | User input | Steward display name |
| steward_role | Data Owner | User input | Controlled steward role selected from `DataAgreementConfig.steward_role_options` in `00_env_config` and saved in the existing `steward_role` column. |
| contact | steward@example.com | User input | Steward contact details |
| effective_from | 2026-01-01 | User input | Optional start date for the steward assignment; blank starts immediately. |
| effective_to | 2026-12-31 | User input | Optional end date for the steward assignment; blank remains active after the start date. |
| is_active | `true` | Backend-derived | Lowercase `true` or `false` string derived from effective dates unless an existing backend value is explicitly false. Normal users do not manually edit it. |
| custom_fields_json | `{"group":"Shared Services"}` | User input | Config-driven extra fields collected by the steward widget. |

The steward maintenance form hides backend-managed `steward_id` and `is_active` from normal users. Active steward dropdowns are based on effective dates, with `is_active=false` only acting as a backend override. `steward_role` is a controlled dropdown configured through `steward_role_options` in `00_env_config`; add organization-specific role extensions to that config list rather than adding new physical role columns.

### `METADATA_DATA_AGREEMENT`

| Item | Details |
| --- | --- |
| Concept | `data_agreements` |
| Purpose | Agreement-level usage boundary created by `01_da_*`. It defines what the data work is approved for, captures both the steward/provider and recipient/consumer sides, and links the agreement to an active steward. |
| Grain | One row per agreement version. New agreement revisions are appended instead of overwriting previous versions. |
| Key relationships | `steward_id` references `METADATA_DATA_STEWARD`. Downstream metadata tables use `agreement_id` to link catalogue, governance, rules, contracts, lineage, and handover evidence back to the approved agreement. |
| Main writer | `01_da_*` |
| Main downstream use | Scopes what `02_ex`, base `03_pc`, and `04_gov` are allowed to profile, govern, and hand over; enhanced `03_pc` variants can enforce approved metadata after governance review, including different treatment for internal, external, and research usage purposes. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| agreement_id | DA-20260529-100000 | System generated | Backend-generated stable agreement key reused across appended versions. Normal users do not manually edit it. |
| contract_version | 1.0.0 | System generated | Backend-generated append-only semantic version. Updates increment it automatically. |
| agreement_name | Governed Reporting Agreement | User input | Human-readable agreement name. |
| domain | Operations | User input | Business or data domain for the agreement. Can be free text or selected from config. |
| steward_id | steward-001 | System derived | Steward/provider reference key resolved from `METADATA_DATA_STEWARD`. |
| recipient | Internal analytics team | User input | Free-text recipient or consumer side of the agreement. |
| start_date | `2026-06-01` | User input | Agreement start date. |
| expiry_date | `2027-05-31` | User input | Agreement expiry date. |
| business_purpose | `Support governed reporting` | User input | Business reason for the agreement. |
| approved_usage_internal | `Internal performance reporting` | User input | Approved internal-use purpose, restrictions, or expectations. |
| approved_usage_external | `External partner reporting` | User input | Approved external-use purpose, restrictions, or expectations. |
| approved_usage_research | `Approved research analysis` | User input | Approved research-use purpose, restrictions, or expectations. |
| custom_fields_json | `{"consumer_group":"ODI"}` | User input | Config-driven extra fields collected by the agreement intake widget. |

One agreement may populate one, two, or all three approved usage fields. Splitting internal, external, and research usage lets later governance workflows apply different review expectations, restrictions, and evidence requirements by purpose. Existing metadata tables that still contain only the old `approved_usage` column need a deliberate schema update before rendering the updated `01_da` form; the framework does not silently map old usage text into a new purpose field because that would change its meaning.


### `METADATA_DATA_AGREEMENT_EVIDENCE`

| Item | Details |
| --- | --- |
| Concept | `data_agreement_evidence` |
| Purpose | Supporting file-reference ledger for documents or screenshots that support a saved agreement version. Evidence files are uploaded manually to the metadata lakehouse `Files` area first; the table stores links and descriptive metadata, not binary content or JSON embedded in `METADATA_DATA_AGREEMENT`. |
| Grain | One row per evidence file link per agreement version. |
| Key relationships | `agreement_id` and `contract_version` reference `METADATA_DATA_AGREEMENT`. |
| Main writer | `01_da_*` Agreement Evidence section |
| Main downstream use | Lets governance or audit users find supporting agreement files without bloating agreement/version metadata rows. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

Evidence upload is optional. Users can save steward and agreement records without evidence, then return later to attach supporting documents. Upload evidence files manually to the metadata lakehouse `Files` area first, then paste one `Files/...` path per line in the Agreement Evidence widget, for example `Files/fabricops/agreement_evidence/<agreement_id>/<contract_version>/signed_agreement.pdf`. The widget validates each path and appends one `METADATA_DATA_AGREEMENT_EVIDENCE` row per valid evidence file link. The metadata table stores only file references and descriptive metadata; it does not store uploaded binary content. `METADATA_DATA_AGREEMENT` stays focused on agreement identity, versioning, steward, recipient, purpose, approved usage, dates, and config-driven extension fields.

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| agreement_id | DA-20260529-100000 | System derived | Agreement key for the supported agreement version. |
| contract_version | 1.0.0 | System derived | Agreement version supported by the evidence file. |
| evidence_type | Signed Agreement | User input | Simple evidence category selected in the Agreement Evidence widget. |
| file_name | signed_agreement.pdf | Runtime derived | Final file name segment derived from the pasted `Files/...` path. |
| file_path | Files/fabricops/agreement_evidence/DA-20260529-100000/1.0.0/signed_agreement.pdf | User input | Metadata lakehouse `Files/...` path pasted by the user after manually uploading the evidence file. |
| mime_type | application/pdf | Runtime derived | Best-effort MIME type derived from the file extension, or blank. |
| file_size | 24576 | Runtime collected | Best-effort file size from `notebookutils.fs.ls(parent)`, or blank. |
| uploaded_at | 2026-06-01T10:30:00Z | Runtime collected | Upload timestamp aligned to runtime audit context when available. |
| uploaded_by | user@example.com | Runtime collected | Uploading user aligned to runtime audit context when available. |

### `METADATA_NOTEBOOK_REGISTRY`

| Item | Details |
| --- | --- |
| Concept | `notebook_registry` |
| Purpose | Records which notebooks support an agreement, where they live, and what role they play in the workflow. |
| Grain | Append-only registration events. The latest event per `registration_id` determines whether a notebook/agreement link is active or superseded. |
| Key relationships | `agreement_id` links the notebook to `METADATA_DATA_AGREEMENT`. Table fields can optionally link a notebook to catalogue records. |
| Main writer | All workflow notebooks through `register_current_notebook()`. |
| Main downstream use | Lets handover and audit views point back to the notebooks that produced or approved metadata evidence. |
| Runtime audit | The row uses explicit runtime columns listed below rather than the shared underscore-prefixed `01_da` audit-column block. |

`METADATA_NOTEBOOK_REGISTRY` is not created or written by the `01_da` widgets. `setup_data_agreement_tables()` remains scoped to agreement intake only: `METADATA_DATA_STEWARD`, `METADATA_DATA_AGREEMENT`, and `METADATA_DATA_AGREEMENT_EVIDENCE`. Prepare this registry separately with `setup_notebook_registry_table()` before workflow notebooks register themselves, then let each workflow notebook append its own row through `register_current_notebook()`. Existing registry tables with the original lightweight columns remain compatible; setup adds the minimal registration-state columns so replacements can preserve audit history instead of deleting earlier rows.

Recommended route-based usage:

```python
setup_notebook_registry_table(spark=spark, config=CONFIG, env=ENV)

register_current_notebook(
    spark=spark,
    config=CONFIG,
    env=ENV,
    agreement_id=agreement_id,
    notebook_type="03_pc",
    environment_name=ENV,
    dataset_name=dataset_name,
    table_name=table_name,
)
```

!!! important "Notebook registry function"
    Use `register_current_notebook()`, not `register_notebook_metadata()`.

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| agreement_id | lyra_deid_v1 | Runtime collected | Agreement this notebook supports |
| environment_name | prod | Runtime collected | Environment context |
| dataset_name | lyra | Runtime collected | Dataset or data product |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Table context if applicable |
| topic | profiling | Runtime collected | Notebook topic |
| pipeline_name | lyra_pipeline | Runtime collected | Pipeline or workflow name |
| notebook_type | 04_gov | Runtime collected | Notebook family |
| workspace_id | Fabric workspace ID | Runtime collected | Fabric workspace ID |
| workspace_name | ODI Dev | Runtime collected | Fabric workspace name |
| notebook_id | Fabric notebook ID | Runtime collected | Fabric notebook ID |
| notebook_name | 04_gov_lyra_column_review | Runtime collected | Fabric notebook name |
| notebook_url | https://fabric.microsoft.com/... | Runtime collected | Link to notebook |
| user_name | user@example.com | Runtime collected | Registering user name or email from Fabric runtime context |
| user_id | user-guid | Runtime collected | Registering user ID |
| registered_at | 2026-05-29T10:30:00Z | Runtime collected | Registration event timestamp |
| registration_id | 24-character hash | System derived | Stable notebook/agreement/version/role link identifier used to collapse append-only events into current state. |
| agreement_contract_version | 1.0.0 | Runtime collected | Agreement contract version selected at registration time. |
| registration_role | primary | Runtime collected | `primary` for the default user-facing agreement, or `additional` for an advanced audit link. |
| registration_status | active | Runtime collected | `active` for current links, or `superseded` when a primary link was replaced. |
| superseded_at | 2026-06-04T12:00:00Z | Runtime collected | Timestamp populated on superseded events. |
| superseded_by_registration_id | 24-character hash | Runtime collected | Replacement registration that superseded the prior primary link. |

The backend supports many agreement links per notebook by appending one event per link. This keeps the registry many-to-many: a notebook can have one primary active agreement for its main purpose plus additional active agreement links for supporting datasets it joins or references. The `02_ex` template defaults to one active primary agreement at a time: replacing an agreement appends a superseded event for the prior primary link and appends or activates the new primary registration, while the additional-link option keeps the primary link active and appends a clearly marked `additional` link. Superseded agreement links remain as audit history for wrong or outdated primary registrations.

Do not store profiling metrics, business context, classification, or DQ results here. This table owns notebook traceability only.

### `METADATA_DATA_ACCESS`

| Item | Details |
| --- | --- |
| Concept | `data_access` |
| Purpose | Records table-level access assignments, access level, and expiry windows. |
| Grain | One row per table access assignment. |
| Key relationships | `table_id` or `metadata_table_key` links access evidence to `METADATA_DATA_CATALOGUE_TABLE`. |
| Main writer | Lakehouse or warehouse access export process, access review notebook, or administrator-maintained metadata process. |
| Main downstream use | Supports access review, handover, and governance visibility. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| access_id | acc_res_output_analyst_20260601 | Planned | Unique access record |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Table reference from the catalogue |
| metadata_table_key | hash value | Planned | Stable table join key. Generated by metadata helper. |
| user_id | user@example.com | Planned | User granted access, when access is user-based |
| group_id | governance-analysts | Planned | Group granted access, when access is group-based |
| access_level | read | Planned | Access level, such as read, write, owner, or admin |
| effective_date | 2026-06-01 | Planned | Access start date |
| expiry_date | 2026-12-31 | Planned | Access expiry date |
| source_system | Fabric Lakehouse | Planned | System where the access assignment was observed |
| captured_at | 2026-06-01T10:00:00Z | Planned | Metadata capture timestamp |

### `METADATA_DATA_CATALOGUE_TABLE`

| Item | Details |
| --- | --- |
| Concept | Table-level `data_catalogue` |
| Purpose | Stores table-level catalogue and profiling evidence from exploration or production pipeline runs. |
| Grain | One row per agreement, table, and profiling run. A latest view can expose one current row per table. |
| Key relationships | `agreement_id` links to `METADATA_DATA_AGREEMENT`. `notebook_id`, `notebook_registry_key`, or `notebook_registry_id` links to `METADATA_NOTEBOOK_REGISTRY`. |
| Main writer | `02_ex_*` and `03_pc_*` profiling steps. |
| Main downstream use | Feeds contracts, access review, lineage, dashboards, and handover. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Unique table catalogue row |
| catalogue_id | cat_lyra_output_20260529 | Planned | Unique catalogue observation row |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| notebook_id | Fabric notebook ID | Planned | Notebook that produced or profiled the table |
| notebook_registry_key | hash value | Planned | Producing notebook registry key |
| profile_run_id | orders_to_product_dev_20260605123000123456 | Runtime collected | Unique execution-level profiling run identifier. `PIPELINE_NAME` remains stable while this value changes every execution. |
| pipeline_name | orders_to_product | Runtime collected | Stable pipeline identity shared across executions. |
| profile_stage | source | Runtime collected | Distinguishes source and target profile evidence for drift baseline lookup. |
| profile_status | successful | Runtime collected | Marks evidence written after the guarded pipeline path has reached the successful profile-write point. |
| baseline_status | observed | Runtime collected / Steward maintained | `observed` for normal evidence or `approved` for an explicitly approved stable-source baseline. |
| source_behaviour | evolving | Runtime collected | Source drift behaviour configured in `03_pc`: `evolving` or `stable`. |
| profile_baseline_mode | latest_successful | Runtime collected | Baseline selection mode configured in `03_pc`: `latest_successful` or `approved`. |
| source_change_signal_json | {"strategy":"watermark"} | Runtime collected | Optional lightweight source-change signal used to skip unchanged evolving-source runs. |
| metadata_table_key | hash value | Planned | Stable table join key. Generated by metadata helper. |
| environment_name | prod | Planned | Environment context |
| dataset_name | lyra | Planned | Dataset or data product name |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Governed table name |
| lakehouse | unified_lakehouse | Planned | Lakehouse where the table lives |
| schema | dbo | Planned | Schema name where relevant |
| layer | unified | Planned | Source, unified, product, or output layer |
| status | active | Planned | Table status |
| source_system | student_records | Planned | Source system name |
| table_type | lakehouse_table | Planned | Asset type |
| row_count | 10000 | Runtime collected | Profiled row count |
| column_count | 48 | Planned | Profiled column count |
| schema_hash | a91f... | Planned | Detect schema changes |
| profile_status | complete | Planned | Profiling completion status |
| profiled_at | 2026-05-29T09:10:00Z | Runtime collected | Profiling timestamp |
| profile_payload_json | {"columns":[...]} | Planned | Extended table profile payload |


### `METADATA_DATA_CATALOGUE_COLUMN`

| Item | Details |
| --- | --- |
| Concept | Column-level `data_catalogue` |
| Purpose | Stores column-level catalogue and profiling evidence separately from the table-level catalogue. |
| Grain | One row per table column per profiling run or latest column snapshot. |
| Key relationships | `table_id` or `metadata_table_key` links to `METADATA_DATA_CATALOGUE_TABLE`. |
| Main writer | `02_ex_*` and `03_pc_*` profiling steps. |
| Main downstream use | Feeds quality rules, sensitivity classification, business context, column lineage, contracts, and handover. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| column_id | col_student_id | Planned | Unique column catalogue row |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Parent table reference |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| profile_run_id | orders_to_product_dev_20260605123000123456 | Runtime collected | Unique execution-level profiling run identifier. `PIPELINE_NAME` remains stable while this value changes every execution. |
| pipeline_name | orders_to_product | Runtime collected | Stable pipeline identity shared across executions. |
| profile_stage | source | Runtime collected | Distinguishes source and target profile evidence for drift baseline lookup. |
| profile_status | successful | Runtime collected | Marks evidence written after the guarded pipeline path has reached the successful profile-write point. |
| baseline_status | observed | Runtime collected / Steward maintained | `observed` for normal evidence or `approved` for an explicitly approved stable-source baseline. |
| source_behaviour | evolving | Runtime collected | Source drift behaviour configured in `03_pc`: `evolving` or `stable`. |
| profile_baseline_mode | latest_successful | Runtime collected | Baseline selection mode configured in `03_pc`: `latest_successful` or `approved`. |
| source_change_signal_json | {"strategy":"watermark"} | Runtime collected | Optional lightweight source-change signal used to skip unchanged evolving-source runs. |
| metadata_table_key | hash value | System derived | Stable table join key. Generated by metadata helper. |
| metadata_column_key | hash value | System derived | Stable column join key. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Parent table name |
| column_name | student_id | Runtime collected | Column name |
| data_type | string | Runtime collected | Observed data type |
| ordinal_position | 1 | Planned | Column order in the table |
| nullable | false | Planned | Whether the column allows nulls |
| null_count | 0 | Planned | Observed null count |
| distinct_count | 9997 | Planned | Observed distinct value count |
| min_value | 1 | Planned | Minimum value where relevant |
| max_value | 9999 | Planned | Maximum value where relevant |
| distribution_type | categorical | Runtime collected | Optional profile distribution type: `numeric` or `categorical`. |
| distribution_json | {"category_counts":{"A":100},"other_count":2} | Runtime collected | Optional lightweight distribution summary reused by profile drift checks. |
| profiled_at | 2026-05-29T09:10:00Z | Runtime collected | Profiling timestamp |

### `METADATA_DATA_LINEAGE_TABLE`

| Item | Details |
| --- | --- |
| Concept | Table-level `data_lineage` |
| Purpose | Stores source-to-target table movement and transformation evidence. |
| Grain | One row per source table to target table lineage event. |
| Key relationships | Source and target table keys link to `METADATA_DATA_CATALOGUE_TABLE`. `notebook_registry_key` or `notebook_registry_id` links to the producing notebook. |
| Main writer | `03_pc_*` lineage capture or transformation summary step. |
| Main downstream use | Feeds handover, metadata dashboard, OpenMetadata lineage payloads, and operational traceability. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| lineage_id | lin_lyra_raw_to_output_20260529 | Planned | Unique table lineage row |
| run_id | run_20260529_110000 | Planned | Execution run key |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| source_table_id | tbl_raw_lyra_students | Planned | Upstream table reference |
| target_table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Downstream table reference |
| source_metadata_table_key | hash value | Planned | Upstream table stable join key. Generated by metadata helper. |
| target_metadata_table_key | hash value | Planned | Downstream table stable join key. Generated by metadata helper. |
| source_table | raw_lyra_students | Planned | Upstream table |
| target_table | res_output_lyra_deid_all_v1 | Planned | Downstream table |
| notebook_id | Fabric notebook ID | Planned | Producing notebook reference |
| notebook_registry_key | hash value | Planned | Producing notebook registry key |
| lineage_level | table | Planned | Indicates table-level lineage |
| transformation_type | hash, filter, aggregate | Planned | Transformation category |
| transformation_summary | De-identified student records and filtered active population | Planned | Human readable transformation note |
| columns_used_json | ["student_no","status_code"] | Planned | Source columns used |
| columns_created_json | ["student_id","active_flag"] | Planned | Output columns created |
| captured_at | 2026-05-29T11:10:00Z | Planned | Capture timestamp |
| lineage_payload_json | {"source":"raw_lyra_students","target":"res_output_..."} | Planned | Extended lineage payload |


### `METADATA_DATA_LINEAGE_COLUMN`

| Item | Details |
| --- | --- |
| Concept | Column-level `data_lineage` |
| Purpose | Stores source-to-target column mappings. |
| Grain | One row per source column to target column mapping. |
| Key relationships | Source and target column keys link to `METADATA_DATA_CATALOGUE_COLUMN`. `notebook_registry_key` links to the producing notebook. |
| Main writer | `03_pc_*` lineage capture step, with AI assistance where mappings are not obvious. |
| Main downstream use | Feeds impact analysis, explainability, handover, and AI-ready metadata exports. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| column_lineage_id | clin_student_no_to_student_id_20260529 | Planned | Unique column lineage row |
| run_id | run_20260529_110000 | Planned | Execution run key |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| source_column_id | col_raw_student_no | Planned | Source column reference |
| target_column_id | col_output_student_id | Planned | Target column reference |
| source_metadata_column_key | hash value | Planned | Source column stable join key. Generated by metadata helper. |
| target_metadata_column_key | hash value | Planned | Target column stable join key. Generated by metadata helper. |
| source_table | raw_lyra_students | Planned | Source table name |
| source_column | student_no | Planned | Source column name |
| target_table | res_output_lyra_deid_all_v1 | Planned | Target table name |
| target_column | student_id | Planned | Target column name |
| notebook_id | Fabric notebook ID | Planned | Producing notebook reference |
| notebook_registry_key | hash value | Planned | Producing notebook registry key |
| lineage_level | column | Planned | Indicates column-level lineage |
| transformation_summary | Hashed source student number | Planned | Human-readable transformation note |
| confidence_score | 0.92 | Planned | Optional confidence for AI-suggested mapping |
| approval_status | approved | Planned | Review state when AI assisted |
| captured_at | 2026-05-29T11:10:00Z | Planned | Capture timestamp |

### `METADATA_DATA_CONTRACTS`

| Item | Details |
| --- | --- |
| Concept | `data_contracts` |
| Purpose | Stores table-level guardrails approved by `04_gov` for enhanced `03_pc` pipeline runs. |
| Grain | One row per table contract version. |
| Key relationships | `table_id` or `metadata_table_key` links to `METADATA_DATA_CATALOGUE_TABLE`. Required rules link to `METADATA_DATA_QUALITY_RULES`. |
| Main writer | `04_gov_*` after AI-assisted and human-approved governance review. |
| Main downstream use | Enhanced `03_pc_*` runs can read approved contracts after `04_gov` to decide whether to continue, warn, quarantine, or fail. The base `03_pc` template does not enforce these guardrails before approval. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| contract_id | contract_res_output_lyra_deid_all_v1 | Planned | Unique contract row |
| contract_version | 1.0.0 | Planned | Append-only contract version |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Table reference from the catalogue |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| metadata_table_key | hash value | Planned | Stable table join key. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Planned | Table covered by the contract |
| expected_schema | [{"name":"student_id","type":"string"}] | Planned | Expected schema definition |
| required_rules | ["student_id_not_null"] | Planned | Rules that must be active for this table |
| drift_policy | allow_add_nullable_columns | Planned | Drift policy for schema or profile changes |
| enforcement_mode | fail_on_error | Planned | How an enhanced `03_pc` should enforce the contract after approval |
| approval_status | approved | Planned | Review state |
| approved_by | user@org.com | Planned | Approver |
| approved_at | 2026-05-29T10:45:00Z | Planned | Approval timestamp |
| is_active | true | Planned | Current active contract flag |
| contract_payload_json | {"schema":[],"rules":[]} | Planned | Full executable contract payload |

### `METADATA_DATA_QUALITY_RULES`

| Item | Details |
| --- | --- |
| Concept | `data_quality_rules` |
| Purpose | Stores approved executable data quality expectations. |
| Grain | One row per rule version. |
| Key relationships | `column_id` or `metadata_column_key` links to `METADATA_DATA_CATALOGUE_COLUMN`. Table-wide rules can link to `table_id` or `metadata_table_key`. |
| Main writer | `04_gov_*` for approval and rule governance. Enhanced `03_pc_*` runs read the active rules for enforcement after approval. |
| Main downstream use | Used by enhanced `03_pc_*` runs to enforce quality after approval and by dashboards or handover outputs to explain approved rules. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| rule_key | hash value | System derived | Stable DQ rule key. Generated by metadata helper. |
| rule_id | student_id_not_null | User input | Human readable rule ID |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Table affected by the rule |
| column_id | col_student_id | Planned | Column affected by the rule, where applicable |
| metadata_table_key | hash value | System derived | Table affected by rule. Generated by metadata helper. |
| metadata_column_key | hash value | System derived | Column affected by rule when applicable. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Table affected by rule |
| column_name | student_id | Runtime collected | Column affected by rule |
| rule_type | not_null | Runtime collected | Rule type |
| threshold | 0 | Planned | Allowed threshold for warning or failure |
| severity | error | User input | Enforcement severity |
| description | Student ID must not be null | User input | Rule description |
| allowed_values | ["active","inactive"] | User input | Accepted value list |
| lower_bound | 0 | User input | Minimum accepted value |
| upper_bound | 100 | User input | Maximum accepted value |
| regex_pattern | ^[A-Z0-9]+$ | User input | Required pattern |
| rule_json | {"type":"not_null","columns":["student_id"]} | User input | Full executable rule payload |
| status | approved | User input | Rule review status |
| is_active | true | User input | Active rule flag |
| action_type | approved | User input | Rule lifecycle action |
| action_by | user@org.com | Runtime collected | User who approved or changed rule |
| action_ts | 2026-05-29T10:40:00Z | Runtime collected | Rule action timestamp |
| action_reason | Approved after governance review | User input | Approval or change reason |
| rule_source | ai_widget_approval | Runtime collected | How rule was created |
| version | 1 | Planned | Rule version |


### `METADATA_SENSITIVITY_CLASSIFICATION`

| Item | Details |
| --- | --- |
| Concept | `sensitivity_classification` |
| Purpose | Stores approved column-level sensitivity, PII, confidentiality, and handling decisions. |
| Grain | One row per column classification version. |
| Key relationships | `column_id` or `metadata_column_key` links to `METADATA_DATA_CATALOGUE_COLUMN`. |
| Main writer | `04_gov_*` through AI-assisted and human-approved governance review. |
| Main downstream use | Feeds sensitivity labels, PII flags, confidentiality metadata, dashboard filters, and handover exports. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| classification_id | cls_student_id_v1 | Planned | Unique classification row |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Parent table reference |
| column_id | col_student_id | Planned | Column being classified |
| metadata_table_key | hash value | System derived | Stable table join key. Generated by metadata helper. |
| metadata_column_key | hash value | System derived | Stable column join key. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Parent table |
| column_name | student_id | Runtime collected | Column being classified |
| ai_suggested_personal_identifier_classification | direct_identifier | System generated | AI suggested classification |
| approved_personal_identifier_classification | de_identified_identifier | User input | Human approved PII classification |
| field_classification | identifier | Planned | Field category |
| sensitivity_level | high | Planned | Sensitivity level from the architecture model |
| confidentiality_label | restricted | User input | Confidentiality level |
| handling_requirement | Do not export outside approved workspace | Planned | Handling instruction |
| masking_requirement | hash before sharing | Planned | Masking instruction |
| retention_requirement | 7 years | Planned | Retention requirement |
| reviewer_notes | Treat as restricted | User input | Governance reviewer notes |
| approval_status | approved | User input | Review state |
| approved_by | user@org.com | Runtime collected | Approver |
| approved_at | 2026-05-29T10:30:00Z | Runtime collected | Approval timestamp |
| version | 1 | Planned | Version of governance decision |
| is_active | true | Planned | Current active classification |


### `METADATA_BUSINESS_CONTEXT`

| Item | Details |
| --- | --- |
| Concept | `business_context` |
| Purpose | Stores approved column-level business meaning, ownership, and usage notes. |
| Grain | One row per column business-context version. |
| Key relationships | `column_id` or `metadata_column_key` links to `METADATA_DATA_CATALOGUE_COLUMN`. |
| Main writer | `04_gov_*` through AI-assisted and human-approved business review. |
| Main downstream use | Feeds column catalogue views, handover JSON, ODCS schema descriptions, and OpenMetadata column descriptions. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| context_id | bc_student_id_v1 | Planned | Unique business context row |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| table_id | tbl_res_output_lyra_deid_all_v1 | Planned | Parent table reference |
| column_id | col_student_id | Planned | Column being described |
| metadata_table_key | hash value | System derived | Stable table join key. Generated by metadata helper. |
| metadata_column_key | hash value | System derived | Stable column join key. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Parent table |
| column_name | student_id | Runtime collected | Column being described |
| ai_suggested_business_context | Identifier for student record | System generated | AI suggested meaning |
| business_definition | Unique de-identified student identifier | Planned | Approved business definition from the architecture model |
| approved_business_context | Unique de-identified student identifier | User input | Human approved meaning |
| approved_description | Unique de-identified student identifier | Planned | Export friendly description |
| owner | Data Steward | Planned | Business owner or accountable role |
| usage_notes | Use only for matching | Planned | Usage guidance from the architecture model |
| units | days | Planned | Unit of measure |
| source_derivation | Hashed from source student number | Planned | Business derivation note |
| semantic_domain | identity | Planned | Business grouping |
| glossary_term | Student Identifier | Planned | Glossary mapping |
| business_context_notes | Use only for matching | User input | Reviewer notes |
| approval_status | approved | User input | Review state |
| reviewer_notes | Approved with wording change | User input | Review comment |
| approved_by | user@org.com | Runtime collected | Approver |
| approved_at | 2026-05-29T10:30:00Z | Runtime collected | Approval timestamp |
| version | 1 | Planned | Version of approved context |
| is_active | true | Planned | Current active context |

### `METADATA_DQ_RESULTS`

| Item | Details |
| --- | --- |
| Concept | Runtime evidence for `data_quality_rules` |
| Purpose | Stores runtime evidence from executing approved DQ rules in enhanced production pipelines after `04_gov` approval. |
| Grain | One row per rule execution per run. |
| Key relationships | `rule_key` links to `METADATA_DATA_QUALITY_RULES`. Table and column keys link to catalogue tables. |
| Main writer | Enhanced `03_pc_*` through DQ enforcement after `04_gov` approval. |
| Main downstream use | Feeds quality dashboards, handover, audit checks, and run evidence. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| dq_result_id | dqres_20260529_student_id_not_null | Planned | Unique DQ result row |
| run_id | run_20260529_110000 | Runtime collected | Execution run key |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| rule_key | hash value | Runtime collected | Rule that was executed |
| rule_id | student_id_not_null | Runtime collected | Human readable rule ID |
| metadata_table_key | hash value | Planned | Affected table. Generated by metadata helper. |
| metadata_column_key | hash value | Planned | Affected column when applicable. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Table checked |
| column_name | student_id | Runtime collected | Column checked when applicable |
| status | passed | Runtime collected | Rule result status |
| passed_count | 9997 | Planned | Passing row count |
| failed_count | 3 | Planned | Failing row count |
| quarantine_count | 3 | Runtime collected | Quarantined row count |
| failure_sample_path | Tables/dq_failures/student_id_not_null | Planned | Pointer to failed sample |
| evaluated_at | 2026-05-29T11:00:00Z | Planned | Evaluation timestamp |
| result_payload_json | {"failed_count":3,"quarantine_count":3} | Planned | Extended DQ result payload |


### `METADATA_DRIFT_RESULTS`

| Item | Details |
| --- | --- |
| Concept | Runtime evidence for `data_contracts` |
| Purpose | Stores schema, profile, and data-drift evidence over time. |
| Grain | One row per agreement, table, and drift check run. |
| Key relationships | `metadata_table_key` links to `METADATA_DATA_CATALOGUE_TABLE`. Contract checks link to `METADATA_DATA_CONTRACTS` where relevant. |
| Main writer | `03_pc_*` drift monitoring step. |
| Main downstream use | Feeds contract validity checks, dashboard warnings, handover action items, and run evidence. |
| Runtime audit | Includes the standard runtime audit columns defined above. |

| Column | Example | Input type | Purpose |
| --- | --- | --- | --- |
| drift_result_id | drift_lyra_20260529 | Planned | Unique drift result row |
| run_id | run_20260529_110000 | Planned | Execution run key |
| agreement_id | lyra_deid_v1 | Planned | Parent agreement key |
| metadata_table_key | hash value | Planned | Table checked for drift. Generated by metadata helper. |
| table_name | res_output_lyra_deid_all_v1 | Runtime collected | Table checked |
| baseline_run_id | run_20260429_110000 | Planned | Baseline run |
| current_run_id | run_20260529_110000 | Planned | Current comparison run |
| drift_type | schema | Runtime collected | Drift category |
| status | warning | Runtime collected | Drift outcome |
| can_continue | true | Runtime collected | Whether pipeline can continue |
| added_columns_json | ["new_status"] | Planned | Added columns |
| removed_columns_json | [] | Planned | Removed columns |
| changed_columns_json | ["status_code"] | Planned | Changed columns |
| metric_changes_json | {"row_count_delta_pct":4.2} | Planned | Profile metric changes |
| drift_summary | 1 new nullable column detected | Planned | Human readable summary |
| checked_at | 2026-05-29T11:05:00Z | Planned | Drift check timestamp |


## Next step

Continue to [Metadata Dashboard](metadata-dashboard.md) to see how the source evidence becomes useful to people and tools.
