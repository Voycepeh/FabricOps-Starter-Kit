# FabricOps Starter Kit 0.2.0 release contract

Package version: `0.2.0`

## Release notes

Release notes have not yet been prepared.

## Expected distribution filenames

These filenames are derived from `pyproject.toml`; verify actual files after `uv build`.

- `fabricops_kit-0.2.0-py3-none-any.whl`
- `fabricops-kit-0.2.0.tar.gz`

## Functions

### Live functions

No assets.

### Preview functions

| Name | Documentation | Source |
| --- | --- | --- |
| `display_guardrail_results` | [docs/api/reference/display_guardrail_results.md](../../api/reference/display_guardrail_results.md) | `src/fabricops_kit/pipeline/display_guardrail_results.py` |
| `prepare_pipeline_table_configs` | [docs/api/reference/prepare_pipeline_table_configs.md](../../api/reference/prepare_pipeline_table_configs.md) | `src/fabricops_kit/pipeline/prepare_pipeline_table_configs.py` |
| `profile_dataframe` | [docs/api/reference/profile_dataframe.md](../../api/reference/profile_dataframe.md) | `src/fabricops_kit/pipeline/profile_dataframe.py` |
| `read_lakehouse_csv` | [docs/api/reference/read_lakehouse_csv.md](../../api/reference/read_lakehouse_csv.md) | `src/fabricops_kit/io/read_lakehouse_csv.py` |
| `read_lakehouse_excel` | [docs/api/reference/read_lakehouse_excel.md](../../api/reference/read_lakehouse_excel.md) | `src/fabricops_kit/io/read_lakehouse_excel.py` |
| `read_lakehouse_parquet` | [docs/api/reference/read_lakehouse_parquet.md](../../api/reference/read_lakehouse_parquet.md) | `src/fabricops_kit/io/read_lakehouse_parquet.py` |
| `read_lakehouse_table` | [docs/api/reference/read_lakehouse_table.md](../../api/reference/read_lakehouse_table.md) | `src/fabricops_kit/io/read_lakehouse_table.py` |
| `read_warehouse_query` | [docs/api/reference/read_warehouse_query.md](../../api/reference/read_warehouse_query.md) | `src/fabricops_kit/io/read_warehouse_query.py` |
| `read_warehouse_table` | [docs/api/reference/read_warehouse_table.md](../../api/reference/read_warehouse_table.md) | `src/fabricops_kit/io/read_warehouse_table.py` |
| `run_table_guardrails` | [docs/api/reference/run_table_guardrails.md](../../api/reference/run_table_guardrails.md) | `src/fabricops_kit/pipeline/run_table_guardrails.py` |
| `setup_metadata_tables` | [docs/api/reference/setup_metadata_tables.md](../../api/reference/setup_metadata_tables.md) | `src/fabricops_kit/config/setup_metadata_tables.py` |
| `setup_notebook` | [docs/api/reference/setup_notebook.md](../../api/reference/setup_notebook.md) | `src/fabricops_kit/config/setup_notebook.py` |
| `widget_author_dq_rules` | [docs/api/reference/widget_author_dq_rules.md](../../api/reference/widget_author_dq_rules.md) | `src/fabricops_kit/widgets/widget_author_dq_rules.py` |
| `widget_author_schema_freshness_profile_rules` | [docs/api/reference/widget_author_schema_freshness_profile_rules.md](../../api/reference/widget_author_schema_freshness_profile_rules.md) | `src/fabricops_kit/widgets/widget_author_schema_freshness_profile_rules.py` |
| `widget_browse_metadata_catalogue` | [docs/api/reference/widget_browse_metadata_catalogue.md](../../api/reference/widget_browse_metadata_catalogue.md) | `src/fabricops_kit/widgets/widget_browse_metadata_catalogue.py` |
| `widget_enrich_table_metadata` | [docs/api/reference/widget_enrich_table_metadata.md](../../api/reference/widget_enrich_table_metadata.md) | `src/fabricops_kit/widgets/widget_enrich_table_metadata.py` |
| `widget_pipeline_bootstrap` | [docs/api/reference/widget_pipeline_bootstrap.md](../../api/reference/widget_pipeline_bootstrap.md) | `src/fabricops_kit/widgets/widget_pipeline_bootstrap.py` |
| `widget_render_agreement_evidence` | [docs/api/reference/widget_render_agreement_evidence.md](../../api/reference/widget_render_agreement_evidence.md) | `src/fabricops_kit/widgets/widget_render_agreement_evidence.py` |
| `widget_render_data_agreement` | [docs/api/reference/widget_render_data_agreement.md](../../api/reference/widget_render_data_agreement.md) | `src/fabricops_kit/widgets/widget_render_data_agreement.py` |
| `widget_render_data_steward` | [docs/api/reference/widget_render_data_steward.md](../../api/reference/widget_render_data_steward.md) | `src/fabricops_kit/widgets/widget_render_data_steward.py` |
| `widget_review_guardrail_governance` | [docs/api/reference/widget_review_guardrail_governance.md](../../api/reference/widget_review_guardrail_governance.md) | `src/fabricops_kit/widgets/widget_review_guardrail_governance.py` |
| `widget_select_guardrail_target` | [docs/api/reference/widget_select_guardrail_target.md](../../api/reference/widget_select_guardrail_target.md) | `src/fabricops_kit/widgets/widget_select_guardrail_target.py` |
| `write_lakehouse_table` | [docs/api/reference/write_lakehouse_table.md](../../api/reference/write_lakehouse_table.md) | `src/fabricops_kit/io/write_lakehouse_table.py` |
| `write_pipeline_lineage` | [docs/api/reference/write_pipeline_lineage.md](../../api/reference/write_pipeline_lineage.md) | `src/fabricops_kit/pipeline/write_pipeline_lineage.py` |
| `write_pipeline_run_summary` | [docs/api/reference/write_pipeline_run_summary.md](../../api/reference/write_pipeline_run_summary.md) | `src/fabricops_kit/pipeline/write_pipeline_run_summary.py` |
| `write_warehouse_table` | [docs/api/reference/write_warehouse_table.md](../../api/reference/write_warehouse_table.md) | `src/fabricops_kit/io/write_warehouse_table.py` |

### Discontinued functions

No assets.

## Metadata tables

### Live metadata tables

No assets.

### Preview metadata tables

| Name | Documentation | Source |
| --- | --- | --- |
| `METADATA_DATA_ACCESS` | [docs/reference/metadata/metadata_data_access.md](../../reference/metadata/metadata_data_access.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_DATA_AGREEMENT` | [docs/reference/metadata/metadata_data_agreement.md](../../reference/metadata/metadata_data_agreement.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | [docs/reference/metadata/metadata_data_agreement_evidence.md](../../reference/metadata/metadata_data_agreement_evidence.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_DATA_CATALOGUE` | [docs/reference/metadata/metadata_data_catalogue.md](../../reference/metadata/metadata_data_catalogue.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_DATA_LINEAGE_TABLE` | [docs/reference/metadata/metadata_data_lineage_table.md](../../reference/metadata/metadata_data_lineage_table.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_DATA_STEWARD` | [docs/reference/metadata/metadata_data_steward.md](../../reference/metadata/metadata_data_steward.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_ENRICHMENT_RULES` | [docs/reference/metadata/metadata_enrichment_rules.md](../../reference/metadata/metadata_enrichment_rules.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_GUARDRAIL_RESULTS` | [docs/reference/metadata/metadata_guardrail_results.md](../../reference/metadata/metadata_guardrail_results.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_GUARDRAIL_RULES` | [docs/reference/metadata/metadata_guardrail_rules.md](../../reference/metadata/metadata_guardrail_rules.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_NOTEBOOK_REGISTRY` | [docs/reference/metadata/metadata_notebook_registry.md](../../reference/metadata/metadata_notebook_registry.md) | `src/fabricops_kit/config/metadata_schemas.py` |
| `METADATA_PIPELINE_RUNS` | [docs/reference/metadata/metadata_pipeline_runs.md](../../reference/metadata/metadata_pipeline_runs.md) | `src/fabricops_kit/config/metadata_schemas.py` |

### Discontinued metadata tables

No assets.

## Templates

### Live templates

No assets.

### Preview templates

| Name | Documentation | Source |
| --- | --- | --- |
| `00_env_config` | [docs/notebook-templates-implementation-guide/environment-config.md](../../notebook-templates-implementation-guide/environment-config.md) | `templates/notebooks/00_env_config.ipynb` |
| `01_agreement` | [docs/notebook-templates-implementation-guide/agreement-setup.md](../../notebook-templates-implementation-guide/agreement-setup.md) | `templates/notebooks/01_agreement.ipynb` |
| `02_pipeline` | [docs/notebook-templates-implementation-guide/pipeline-execution.md](../../notebook-templates-implementation-guide/pipeline-execution.md) | `templates/notebooks/02_pipeline.ipynb` |
| `03_governance` | [docs/notebook-templates-implementation-guide/governance-review.md](../../notebook-templates-implementation-guide/governance-review.md) | `templates/notebooks/03_governance.ipynb` |
| `99_explore` | [docs/notebook-templates-implementation-guide/index.md](../../notebook-templates-implementation-guide/index.md) | `templates/notebooks/99_explore.ipynb` |
| `example_dq_rule_smoke_test` | [docs/notebook-templates-implementation-guide/index.md](../../notebook-templates-implementation-guide/index.md) | `templates/notebooks/example_dq_rule_smoke_test.ipynb` |
| `example_pipeline_demo` | [docs/notebook-templates-implementation-guide/index.md](../../notebook-templates-implementation-guide/index.md) | `templates/notebooks/example_pipeline_demo.ipynb` |

### Discontinued templates

No assets.

## DQ rules

### Live dq rules

No assets.

### Preview dq rules

| Name | Documentation | Source |
| --- | --- | --- |
| `accepted_values` | [docs/reference/dq-rules/accepted-values.md](../../reference/dq-rules/accepted-values.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `between` | [docs/reference/dq-rules/between.md](../../reference/dq-rules/between.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `column_a_gt_column_b` | [docs/reference/dq-rules/column-a-gt-column-b.md](../../reference/dq-rules/column-a-gt-column-b.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `column_a_gte_column_b` | [docs/reference/dq-rules/column-a-gte-column-b.md](../../reference/dq-rules/column-a-gte-column-b.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `column_pair_equal` | [docs/reference/dq-rules/column-pair-equal.md](../../reference/dq-rules/column-pair-equal.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `date_between` | [docs/reference/dq-rules/date-between.md](../../reference/dq-rules/date-between.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `date_not_future` | [docs/reference/dq-rules/date-not-future.md](../../reference/dq-rules/date-not-future.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `expression_true` | [docs/reference/dq-rules/expression-true.md](../../reference/dq-rules/expression-true.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `freshness` | [docs/reference/dq-rules/freshness.md](../../reference/dq-rules/freshness.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `greater_than` | [docs/reference/dq-rules/greater-than.md](../../reference/dq-rules/greater-than.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `greater_than_or_equal` | [docs/reference/dq-rules/greater-than-or-equal.md](../../reference/dq-rules/greater-than-or-equal.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `less_than` | [docs/reference/dq-rules/less-than.md](../../reference/dq-rules/less-than.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `less_than_or_equal` | [docs/reference/dq-rules/less-than-or-equal.md](../../reference/dq-rules/less-than-or-equal.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `max_age_days` | [docs/reference/dq-rules/max-age-days.md](../../reference/dq-rules/max-age-days.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `non_empty_string` | [docs/reference/dq-rules/non-empty-string.md](../../reference/dq-rules/non-empty-string.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `not_in_values` | [docs/reference/dq-rules/not-in-values.md](../../reference/dq-rules/not-in-values.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `not_null` | [docs/reference/dq-rules/not-null.md](../../reference/dq-rules/not-null.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `null_rate_below` | [docs/reference/dq-rules/null-rate-below.md](../../reference/dq-rules/null-rate-below.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `regex_match` | [docs/reference/dq-rules/regex-match.md](../../reference/dq-rules/regex-match.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `required_when` | [docs/reference/dq-rules/required-when.md](../../reference/dq-rules/required-when.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `unique` | [docs/reference/dq-rules/unique.md](../../reference/dq-rules/unique.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `unique_combination` | [docs/reference/dq-rules/unique-combination.md](../../reference/dq-rules/unique-combination.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |
| `value_when` | [docs/reference/dq-rules/value-when.md](../../reference/dq-rules/value-when.md) | `src/fabricops_kit/pipeline/guardrails_shared.py` |

### Discontinued dq rules

No assets.
