"""Release-facing public API lifecycle registry for notebook functions."""

# Live public functions carry the supported compatibility guarantee for the
# current release line. Importability alone does not imply Live support.
SUPPORTED_PUBLIC_API = (
    "fabricops_kit.config.setup_notebook.setup_notebook",
    "fabricops_kit.config.setup_metadata_tables.setup_metadata_tables",
    "fabricops_kit.io.read_lakehouse_csv.read_lakehouse_csv",
    "fabricops_kit.io.read_lakehouse_excel.read_lakehouse_excel",
    "fabricops_kit.io.read_lakehouse_json.read_lakehouse_json",
    "fabricops_kit.io.read_lakehouse_parquet.read_lakehouse_parquet",
    "fabricops_kit.io.read_lakehouse_table.read_lakehouse_table",
    "fabricops_kit.io.read_warehouse_query.read_warehouse_query",
    "fabricops_kit.io.read_warehouse_table.read_warehouse_table",
    "fabricops_kit.io.write_lakehouse_table.write_lakehouse_table",
    "fabricops_kit.io.write_warehouse_table.write_warehouse_table",
    "fabricops_kit.pipeline.profile_table.profile_table",
    "fabricops_kit.pipeline.orchestrate_read.orchestrate_read",
    "fabricops_kit.pipeline.orchestrate_write.orchestrate_write",
    "fabricops_kit.pipeline.pipeline_read.pipeline_read",
    "fabricops_kit.pipeline.setup_pipeline.setup_pipeline",
    "fabricops_kit.pipeline.resolve_table_id.resolve_table_id",
    "fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement",
    "fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward",
)

# Preview public functions remain importable for evaluation, but are not part of
# the supported compatibility surface until promoted in a future release.
PREVIEW_PUBLIC_API = (
    "fabricops_kit.pipeline.finalize_pipeline.finalize_pipeline",
    "fabricops_kit.data_agent.create_data_agent.create_data_agent",
    "fabricops_kit.widgets.widget_data_contract.widget_data_contract",
    "fabricops_kit.widgets.widget_activate_pipeline.widget_activate_pipeline",
    "fabricops_kit.access_scanner.scan_effective_access.scan_effective_access",
    "fabricops_kit.access_scanner.scan_workspace_access.scan_workspace_access",
    "fabricops_kit.access_scanner.scan_onelake_access.scan_onelake_access",
    "fabricops_kit.access_scanner.scan_sql_access.scan_sql_access",
)

RELEASE_PUBLIC_API = SUPPORTED_PUBLIC_API + PREVIEW_PUBLIC_API
