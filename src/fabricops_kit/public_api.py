"""Release-facing public API lifecycle registry for notebook functions."""

# Live public functions carry the supported compatibility guarantee for the
# current release line. Importability alone does not imply Live support.
SUPPORTED_PUBLIC_API = (
    "fabricops_kit.config.setup_notebook.setup_notebook",
    "fabricops_kit.config.setup_metadata_tables.setup_metadata_tables",
    "fabricops_kit.io.read_lakehouse_csv.read_lakehouse_csv",
    "fabricops_kit.io.read_lakehouse_excel.read_lakehouse_excel",
    "fabricops_kit.io.read_lakehouse_parquet.read_lakehouse_parquet",
    "fabricops_kit.io.read_lakehouse_table.read_lakehouse_table",
    "fabricops_kit.io.read_warehouse_query.read_warehouse_query",
    "fabricops_kit.io.read_warehouse_table.read_warehouse_table",
    "fabricops_kit.io.write_lakehouse_table.write_lakehouse_table",
    "fabricops_kit.io.write_warehouse_table.write_warehouse_table",
    "fabricops_kit.pipeline.profile_dataframe",
    "fabricops_kit.pipeline.profile_frequency_distribution",
    "fabricops_kit.pipeline.profile_and_register_table",
)

# Preview public functions remain importable for evaluation, but are not part of
# the supported compatibility surface until promoted in a future release.
PREVIEW_PUBLIC_API = (
    "fabricops_kit.pipeline.check_schema",
    "fabricops_kit.pipeline.check_freshness",
    "fabricops_kit.pipeline.check_changes",
    "fabricops_kit.pipeline.observe_source.observe_source",
    "fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement",
    "fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward",
    "fabricops_kit.widgets.widget_view_agreement_catalogue.widget_view_agreement_catalogue",
    "fabricops_kit.widgets.widget_view_pipeline_catalogue.widget_view_pipeline_catalogue",
    "fabricops_kit.widgets.widget_view_data_catalogue.widget_view_data_catalogue",
    "fabricops_kit.widgets.widget_register_data_contract.widget_register_data_contract",
    "fabricops_kit.widgets.widget_author_dq_rules.widget_author_dq_rules",
    "fabricops_kit.widgets.widget_author_schema_freshness_profile_rules.widget_author_schema_freshness_profile_rules",
    "fabricops_kit.widgets.widget_enrich_table_metadata.widget_enrich_table_metadata",
    "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
    "fabricops_kit.widgets.widget_select_guardrail_target.widget_select_guardrail_target",
    "fabricops_kit.pipeline.display_guardrail_results",
    "fabricops_kit.pipeline.run_table_guardrails",
)

RELEASE_PUBLIC_API = SUPPORTED_PUBLIC_API + PREVIEW_PUBLIC_API
