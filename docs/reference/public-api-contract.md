# Public API contract

The FabricOps Starter Kit release contract supports exactly 25 public notebook-facing functions. These functions are the stable API surface for release preparation and should remain available through the internal release refactor.

Implementation helpers are not part of this stable contract. Shared helpers, private helpers, classes, methods, validators, resolvers, workflows, adapters, and utilities may be reorganized before release without being treated as supported public API. Public function behavior should remain stable through that refactor, and notebook templates should only use the supported public functions below.

The canonical machine-readable list lives in `fabricops_kit.public_api.SUPPORTED_PUBLIC_API`.

| Domain | Function | Purpose |
|---|---|---|
| Environment setup | `fabricops_kit.config.setup_metadata_tables` | Prepare all FabricOps metadata tables for the configured environment. |
| Environment setup | `fabricops_kit.config.setup_notebook` | Run consolidated FabricOps startup for workflow and optional support notebooks. |
| Data agreement | `fabricops_kit.widgets.widget_render_agreement_evidence.widget_render_agreement_evidence` | Render standalone agreement supporting-file upload controls. |
| Data agreement | `fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement` | Render append-only agreement create/update maintenance using active stewards. |
| Data agreement | `fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward` | Render append-only data steward create/update maintenance. |
| Profiling | `fabricops_kit.data_profiling.profile_dataframe` | Build canonical DQ-ready profiling rows from a Spark DataFrame. |
| Data access | `fabricops_kit.read_lakehouse_csv` | Read a CSV file from a Fabric lakehouse Files path. |
| Data access | `fabricops_kit.read_lakehouse_excel` | Read an Excel file from a Fabric lakehouse Files path. |
| Data access | `fabricops_kit.read_lakehouse_parquet` | Read a Parquet file from a Fabric lakehouse Files path. |
| Data access | `fabricops_kit.read_lakehouse_table` | Read a Delta table from a Fabric lakehouse. |
| Data access | `fabricops_kit.read_warehouse_query` | Read warehouse rows with SQL pushdown. |
| Data access | `fabricops_kit.read_warehouse_table` | Read a full table from a Microsoft Fabric warehouse. |
| Data access | `fabricops_kit.write_lakehouse_table` | Write a Spark DataFrame to a Fabric lakehouse Delta table. |
| Data access | `fabricops_kit.write_warehouse_table` | Write a Spark DataFrame to a Microsoft Fabric warehouse table. |
| Governance review | `fabricops_kit.widgets.widget_author_dq_rules.widget_author_dq_rules` | Render interactive manual DQ rule authoring UI. |
| Governance review | `fabricops_kit.widgets.widget_author_schema_freshness_profile_rules.widget_author_schema_freshness_profile_rules` | Render interactive schema, freshness, and profile behavior authoring UI. |
| Governance review | `fabricops_kit.widgets.widget_enrich_table_metadata.widget_enrich_table_metadata` | Render one consolidated governed table metadata enrichment widget. |
| Governance review | `fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance` | Render interactive governance policy and shared rule-review controls. |
| Governance review | `fabricops_kit.widgets.widget_select_guardrail_target.widget_select_guardrail_target` | Render an interactive guardrail target selector and return handover state. |
| Pipeline | `fabricops_kit.pipeline.display_guardrail_results` | Return guardrail results prepared for summary, detailed, or debug display. |
| Pipeline | `fabricops_kit.pipeline.prepare_pipeline_table_configs` | Prepare source or target table configs for a pipeline notebook. |
| Pipeline | `fabricops_kit.pipeline.run_table_guardrails` | Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails. |
| Pipeline | `fabricops_kit.widgets.widget_pipeline_bootstrap.widget_pipeline_bootstrap` | Start a guided notebook run and store runtime defaults. |
| Pipeline | `fabricops_kit.pipeline.write_pipeline_lineage` | Write many-to-many source-to-target lineage rows. |
| Pipeline | `fabricops_kit.pipeline.write_pipeline_run_summary` | Write a pipeline runtime summary to metadata. |
