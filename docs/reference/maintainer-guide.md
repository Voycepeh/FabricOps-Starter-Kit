# Maintainer Guide

Use this page as the maintainer entry point for preparing the FabricOps Starter Kit v1.0.0 public API release. The release checkpoint is intentionally centered on the [Public API contract](public-api-contract.md): it defines the notebook-facing functions that must remain stable for release readiness while internal implementation details can continue to be refactored.

## v1.0.0 API release contract

For v1.0.0, the supported public API contract contains exactly **26 public notebook-facing functions**. These functions are the stable API surface for release preparation, notebook templates, and maintainer validation. The canonical machine-readable list is `fabricops_kit.public_api.SUPPORTED_PUBLIC_API`; maintainers should verify that list before release sign-off and avoid treating generated docs or hand-maintained tables as the source of truth.

The [Public API contract](public-api-contract.md) remains the release anchor for this contract. The table below mirrors its maintainer-facing summary so release reviewers can confirm the supported surface without leaving this entry point.

| Domain | Function | Purpose |
|---|---|---|
| Environment setup | `fabricops_kit.config.setup_metadata_tables` | Prepare all FabricOps metadata tables for the configured environment. |
| Environment setup | `fabricops_kit.config.setup_notebook` | Run consolidated FabricOps startup for delivery and optional support notebooks. |
| Data agreement | `fabricops_kit.data_agreement.widget_render_agreement_evidence` | Render standalone agreement evidence upload controls. |
| Data agreement | `fabricops_kit.data_agreement.widget_render_data_agreement` | Render append-only agreement create/update maintenance using active stewards. |
| Data agreement | `fabricops_kit.data_agreement.widget_render_data_steward` | Render append-only data steward create/update maintenance. |
| Profiling | `fabricops_kit.data_profiling.profile_dataframe` | Build canonical DQ-ready profiling rows from a Spark DataFrame. |
| Data access | `fabricops_kit.read_lakehouse_csv` | Read a CSV file from a Fabric lakehouse Files path. |
| Data access | `fabricops_kit.read_lakehouse_excel` | Read an Excel file from a Fabric lakehouse Files path. |
| Data access | `fabricops_kit.read_lakehouse_parquet` | Read a Parquet file from a Fabric lakehouse Files path. |
| Data access | `fabricops_kit.read_lakehouse_table` | Read a Delta table from a Fabric lakehouse. |
| Data access | `fabricops_kit.read_warehouse_query` | Read warehouse rows with SQL pushdown. |
| Data access | `fabricops_kit.read_warehouse_table` | Read a full table from a Microsoft Fabric warehouse. |
| Data access | `fabricops_kit.write_lakehouse_table` | Write a Spark DataFrame to a Fabric lakehouse Delta table. |
| Data access | `fabricops_kit.write_warehouse_table` | Write a Spark DataFrame to a Microsoft Fabric warehouse table. |
| Governance review | `fabricops_kit.governance_review.get_latest_metadata_catalogue` | Return the latest metadata catalogue rows for an exploratory table lookup. |
| Governance review | `fabricops_kit.governance_review.widget_author_dq_rules` | Render interactive manual DQ rule authoring UI. |
| Governance review | `fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules` | Render interactive schema, freshness, and profile behavior authoring UI. |
| Governance review | `fabricops_kit.governance_review.widget_enrich_table_metadata` | Render one consolidated governed table metadata enrichment widget. |
| Governance review | `fabricops_kit.governance_review.widget_review_guardrail_governance` | Render interactive governance policy and shared rule-review controls. |
| Governance review | `fabricops_kit.governance_review.widget_select_guardrail_target` | Render an interactive guardrail target selector and return handover state. |
| Pipeline | `fabricops_kit.pipeline.display_guardrail_results` | Return guardrail results prepared for summary, detailed, or debug display. |
| Pipeline | `fabricops_kit.pipeline.prepare_pipeline_table_configs` | Prepare source or target table configs for a pipeline notebook. |
| Pipeline | `fabricops_kit.pipeline.run_table_guardrails` | Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails. |
| Pipeline | `fabricops_kit.pipeline.widget_pipeline_bootstrap` | Start a guided notebook run and store runtime defaults. |
| Pipeline | `fabricops_kit.pipeline.write_pipeline_lineage` | Write many-to-many source-to-target lineage evidence. |
| Pipeline | `fabricops_kit.pipeline.write_pipeline_run_summary` | Write a pipeline runtime summary to metadata. |

## Public API boundary

Notebook-facing release work should depend only on the 26 supported functions listed in `fabricops_kit.public_api.SUPPORTED_PUBLIC_API`. Those functions are the stable API surface for v1.0.0 release preparation.

Implementation helpers are not part of the stable public API. Shared helpers, private helpers, classes, methods, validators, resolvers, workflows, adapters, and utilities may be reorganized before release without being treated as supported public API changes. Maintainers should keep notebook templates and public guidance on the supported functions above, and use generated implementation references only when maintaining package internals.

## Supporting maintainer references

Use these pages after confirming the v1.0.0 public API release contract:

- [Function Call Graph](function-call-graph.md): generated function call graph relationships and graph context for maintainers.
- [Function Call Graph](../assets/function-call-graph-dashboard.html): review public API shape, chain depth, fan-out, source Python files, cross-layer warnings, and flattening recommendations.
- [Function Inventory](../assets/function-inventory.html): search/filter all callables, select rows, and export AI refactor packets.
- [Release Management](../development/release-management.md): release process and checklist guidance.
- [Release Traceability](../release-info.md): published release traceability and release evidence.
- [Documentation Versioning](../development/docs-versioning.md): docs versioning expectations for release preparation.
- [Glossary](glossary.md): canonical terms for maintainer and user-facing documentation wording.
