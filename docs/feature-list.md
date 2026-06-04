# Feature List

This page inventories FabricOps Starter Kit user-facing surfaces for release review. It only lists items that exist in the repository. Entries marked `Needs maintainer review` should be verified from the release diff before publishing a release.

## Callable package functions

| Feature | Function | Status | Introduced | Last changed | Notes |
| --- | --- | --- | --- | --- | --- |
| 0. Environment setup | `setup_notebook` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `config`. Template mapping: —. Owns environment setup, runtime initialization, paths, and notebook-wide configuration. |
| 1. Governance steward | `select_agreement` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_agreement`. Template mapping: —. Render a searchable agreement selector and store selected agreement metadata row in module state. |
| 1. Governance steward | `get_selected_agreement` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_agreement`. Template mapping: —. Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements. |
| 5. Metadata / contract store | `register_current_notebook` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `metadata`. Template mapping: —. Register current notebook metadata evidence for agreement traceability. |
| 5. Metadata / contract store | `load_notebook_registry` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `metadata`. Template mapping: —. Load notebook registration metadata rows for agreement notebook traceability. |
| 5. Metadata / contract store | `setup_notebook_registry_table` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `metadata`. Template mapping: `00_env_config`. Create or validate notebook registry metadata before workflow notebooks register themselves. |
| 5. Metadata / contract store | `get_notebook_registry_schema` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `metadata`. Template mapping: —. Return the required notebook registry metadata columns. |
| 5. Metadata / contract store | `build_runtime_audit_fields` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `metadata`. Template mapping: —. Build shared underscore-prefixed runtime audit fields for metadata-table rows. |
| 3. Data engineer | `read_lakehouse_table` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 3. Data engineer | `write_lakehouse_table` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 3. Data engineer | `read_warehouse_table` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 3. Data engineer | `write_warehouse_table` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 2. Analyst / data scientist | `profile_dataframe` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_profiling`. Template mapping: —. Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and samples. |
| 1. Governance steward | `draft_business_context` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `business_context`. Template mapping: —. Owns business meaning for tables and columns. |
| 1. Governance steward | `prepare_business_context_profile_input` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `business_context`. Template mapping: —. Owns business meaning for tables and columns. |
| 1. Governance steward | `extract_column_business_context_suggestions` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `business_context`. Template mapping: —. Owns business meaning for tables and columns. |
| 1. Governance steward | `review_business_context` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `business_context`. Template mapping: —. Owns business meaning for tables and columns. |
| 1. Governance steward | `get_reviewed_business_context_rows` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `business_context`. Template mapping: —. Owns business meaning for tables and columns. |
| 1. Governance steward | `write_business_context` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `business_context`. Template mapping: —. Owns business meaning for tables and columns. |
| 2. Analyst / data scientist | `draft_dq_rules` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `review_dq_rules` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `run_dq_rule_review_widget` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Render the notebook widget for human review and approval/rejection of candidate DQ rules. |
| 2. Analyst / data scientist | `get_dq_review_results` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `write_dq_rules` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `load_dq_rules` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `enforce_dq` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `assert_dq_passed` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 1. Governance steward | `draft_governance` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_governance`. Template mapping: —. Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence. |
| 1. Governance steward | `prepare_governance_input` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `data_governance`. Template mapping: —. Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence. |
| 1. Governance steward | `extract_governance_suggestions` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `data_governance`. Template mapping: —. Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence. |
| 1. Governance steward | `review_governance` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_governance`. Template mapping: —. Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence. |
| 1. Governance steward | `write_governance` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_governance`. Template mapping: —. Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence. |
| 1. Governance steward | `load_governance` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_governance`. Template mapping: —. Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence. |
| 3. Data engineer | `standardize_columns` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `technical_columns`. Template mapping: —. Owns standard output/audit columns for pipeline outputs. |
| 3. Data engineer | `build_lineage_records` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_lineage`. Template mapping: —. Owns source-to-target lineage and transformation evidence. |
| 3. Data engineer | `build_lineage_handover_markdown` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_lineage`. Template mapping: —. Owns source-to-target lineage and transformation evidence. |
| 4. Handover / data contract | `build_handover` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `handover`. Template mapping: —. Owns final handover assembly and contract artifact rendering/export. |
| 4. Handover / data contract | `render_handover_markdown` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `handover`. Template mapping: —. Owns final handover assembly and contract artifact rendering/export. |
| 3. Data engineer | `read_lakehouse_csv` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 3. Data engineer | `read_lakehouse_parquet` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 3. Data engineer | `read_lakehouse_excel` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |
| 2. Analyst / data scientist | `validate_dq_rules` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 2. Analyst / data scientist | `review_dq_rule_deactivations` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `data_quality`. Template mapping: —. Owns DQ rule drafting, review, enforcement, quarantine, and quality results. |
| 3. Data engineer | `check_schema_drift` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `drift`. Template mapping: —. Owns schema/profile/data drift checks as engineering guardrails during pipeline runs. |
| 3. Data engineer | `check_partition_drift` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `drift`. Template mapping: —. Owns schema/profile/data drift checks as engineering guardrails during pipeline runs. |
| 3. Data engineer | `check_profile_drift` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `drift`. Template mapping: —. Owns schema/profile/data drift checks as engineering guardrails during pipeline runs. |
| 3. Data engineer | `summarize_drift_results` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `drift`. Template mapping: —. Owns schema/profile/data drift checks as engineering guardrails during pipeline runs. |
| 1. Governance steward | `render_agreement_intake_app` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_agreement`. Template mapping: `01_da_<agreement>`. Render and wire the default agreement-intake form application. |
| 1. Governance steward | `render_data_agreement_widget` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_agreement`. Template mapping: `01_da_<agreement>`. Render append-only agreement maintenance using active steward rows. |
| 1. Governance steward | `render_data_steward_widget` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_agreement`. Template mapping: `01_da_<agreement>`. Render append-only data steward maintenance. |
| 1. Governance steward | `setup_data_agreement_tables` | essential | v1.0.0 baseline | v1.0.0 baseline | Module: `data_agreement`. Template mapping: `00_env_config`. Create, validate, and report readiness for agreement metadata tables. |
| 3. Data engineer | `FabricStore` | optional | v1.0.0 baseline | v1.0.0 baseline | Module: `fabric_input_output`. Template mapping: —. Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO. |

## Plug-and-play notebook templates

| Template | Purpose | Status | Introduced | Last changed | Notes |
| --- | --- | --- | --- | --- | --- |
| `templates/notebooks/00_env_config.ipynb` | Defines shared environment, workspace, lakehouse, warehouse, and metadata routing configuration. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Existing notebook template in repository. |
| `templates/notebooks/01_da_agreement_template.ipynb` | Maintains steward and data agreement intake records. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Existing notebook template in repository. |
| `templates/notebooks/02_ex_agreement_topic.ipynb` | Profiles source data and prepares advisory exploration evidence. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Existing notebook template in repository. |
| `templates/notebooks/03_pc_agreement_pipeline_template.ipynb` | Runs repeatable pipeline processing, checks, metadata evidence, and governed output writes. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Existing notebook template in repository. |
| `templates/notebooks/04_gov_agreement_dataset_table.ipynb` | Reviews business context, data quality rules, sensitivity classification, and governance decisions. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Existing notebook template in repository. |

## Metadata outputs

| Output/table | Purpose | Status | Introduced | Last changed | Notes |
| --- | --- | --- | --- | --- | --- |
| `data_stewards` | Maintains steward identities used during agreement intake. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Agreement setup. |
| `data_agreements` | Anchors agreement names, domains, stewards, and status. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Agreement setup. |
| `data_agreement_evidence` | Stores supporting evidence uploaded during agreement intake. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Agreement setup. |
| `notebook_registry` | Links workflow notebooks to data agreements. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Notebook traceability. |
| `data_access` | Records table access assignments, access levels, and expiry windows. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Access evidence. |
| `data_catalogue` | Stores central table and column registry evidence. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Table and column catalogue. |
| `data_lineage` | Captures source-to-target lineage during pipeline runtime. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Table and column lineage. |
| `data_contracts` | Stores table-level schema, required-rule, drift, and enforcement guardrails. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Contract guardrails. |
| `data_quality_rules` | Stores approved column-level quality expectations. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Column quality rules. |
| `sensitivity_classification` | Stores approved sensitivity labels and handling context. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Column governance labels. |
| `business_context` | Stores approved business definitions, ownership, and usage notes. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Column business meaning. |
| `dq_results` | Stores quality check execution results. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Quality execution evidence. |
| `drift_results` | Stores drift check execution results. | Stable baseline; Needs maintainer review | v1.0.0 baseline | v1.0.0 baseline | Documented metadata output in metadata table guide; logical area: Drift execution evidence. |

## Documentation and examples

| Page/example | Purpose | Status | Notes |
| --- | --- | --- | --- |
| `README.md` | Root navigation and project overview. | Current | Keep concise and navigation-focused. |
| `docs/quick-start.md` | Quick-start guidance. | Current | Needs maintainer review for each release. |
| `docs/install.md` | Installation guidance. | Current | Needs maintainer review for wheel/version alignment. |
| `docs/how-fabricops-works/notebook-templates.md` | Notebook-template operating model. | Current | Source for template purpose summaries. |
| `docs/how-fabricops-works/metadata-tables.md` | Metadata table operating model. | Current | Source for metadata output names. |
| `docs/reference/index.md` | Generated public function reference overview. | Generated | Regenerate from source metadata when public APIs change. |
| `src/README.md` | Callable API reference guidance for package source. | Current | Keep callable guidance close to package source. |
| `examples/notebooks/FabricOps_AI_DQ_Governance_Cleaned.ipynb` | Example notebook for AI-assisted data quality and governance flow. | Current | Example notebook present in repository; release impact needs maintainer review. |
| `examples/notebooks/FabricOps_AI_DQ_Governance_Cleaned (1).ipynb` | Duplicate example notebook present in the repository; purpose needs maintainer review. | Current | Example notebook present in repository; release impact needs maintainer review. |
| `examples/notebooks/FabricOps_AI_DQ_Source_of_Truth_Widget_Metadata_Flow.ipynb` | Example notebook for source-of-truth widget metadata flow. | Current | Example notebook present in repository; release impact needs maintainer review. |
