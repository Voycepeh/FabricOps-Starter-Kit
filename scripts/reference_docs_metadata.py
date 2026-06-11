"""Metadata registry for generated public API documentation."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class PublicSymbolDocMetadata(TypedDict):
    """Documentation metadata for a public symbol exported in ``__all__``."""

    symbol_name: str
    module: str
    kind: str
    template_notebook: str
    template_segment: str
    function_type: NotRequired[str]
    purpose: NotRequired[str]
    summary_override: str | None
    use_when: NotRequired[str]
    when_to_use: NotRequired[list[str]]
    do_not_use_when: NotRequired[str]
    parameters: NotRequired[str | dict[str, str] | list[str]]
    returns: NotRequired[str]
    raises: NotRequired[str | dict[str, str] | list[str]]
    side_effects: NotRequired[str | list[str]]
    fabric_context: NotRequired[str]
    ai_verification: NotRequired[str | list[str]]
    preferred_example: NotRequired[str]
    related_functions: NotRequired[list[str]]






class ModuleDocMetadata(TypedDict):
    """Documentation metadata that drives module navigation and overview generation."""

    module_name: str
    visibility: str
    module_summary: str
    sidebar_group: str
    sidebar_include: bool


MODULE_DOCS_METADATA: list[ModuleDocMetadata] = [
    {"module_name": "config", "visibility": "public", "module_summary": "Owns environment setup, runtime initialization, paths, and notebook-wide configuration.", "sidebar_group": "0. Environment setup", "sidebar_include": True},
    {"module_name": "data_agreement", "visibility": "public", "module_summary": "Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements. Standard notebooks create or check agreement metadata tables in `00_env_config`, render agreement intake in `01_agreement`, and bind downstream work with `widget_select_agreement(...)` and `get_selected_agreement()`.", "sidebar_group": "1. Governance steward", "sidebar_include": True},
    {"module_name": "data_profiling", "visibility": "public", "module_summary": "Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and optional lightweight distributions.", "sidebar_group": "2. Analyst / data scientist", "sidebar_include": True},
    {"module_name": "fabric_input_output", "visibility": "public", "module_summary": "Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.", "sidebar_group": "3. Data engineer", "sidebar_include": True},
    {"module_name": "data_lineage", "visibility": "public", "module_summary": "Owns source-to-target lineage and transformation evidence.", "sidebar_group": "3. Data engineer", "sidebar_include": True},
    {"module_name": "guardrails", "visibility": "public", "module_summary": "Owns schema, freshness, and profile behavior checks as pipeline guardrails during runtime enforcement.", "sidebar_group": "3. Data engineer", "sidebar_include": True},
    {"module_name": "metadata", "visibility": "public", "module_summary": "Owns metadata evidence persistence, stable keys, notebook registry, catalogue keys, and runtime audit helpers.", "sidebar_group": "5. Metadata store", "sidebar_include": True},
    {"module_name": "pipeline", "visibility": "public", "module_summary": "Owns thin 02_pipeline metadata evidence helpers for catalogue evidence internals, lineage persistence, and runtime summaries.", "sidebar_group": "3. Data engineer", "sidebar_include": True},
    {"module_name": "governance_review", "visibility": "public", "module_summary": "Owns table-scoped 03_governance catalogue selection, business context review, DQ-rule review guidance, classification review, AI-assisted internal drafting helpers, and approved metadata commit through record_table_governance.", "sidebar_group": "1. Governance steward", "sidebar_include": True},
    {"module_name": "ai", "visibility": "internal", "module_summary": "Internal AI utility surface used by workflow-facing public functions.", "sidebar_group": "Internal", "sidebar_include": False},
    {"module_name": "schemas", "visibility": "internal", "module_summary": "Internal schema artifacts used for validation and contracts.", "sidebar_group": "Internal", "sidebar_include": False},
]


class TemplateFlowSegmentMetadata(TypedDict):
    """Segment metadata for starter template guidance on the reference landing page."""

    title: str
    symbols: list[str]
    text: NotRequired[str]


class TemplateFlowDocMetadata(TypedDict):
    """Starter template metadata used to render the template-first function reference."""

    notebook_key: str
    notebook_label: str
    template_path: str
    segment_intro: str
    segments: list[TemplateFlowSegmentMetadata]


TEMPLATE_FLOW_DOCS: list[TemplateFlowDocMetadata] = [{'notebook_key': '00_env_config',
  'notebook_label': '`00_env_config`',
  'segment_intro': 'Shared environment bootstrap and metadata table setup.',
  'segments': [{'symbols': ['setup_notebook', 'setup_metadata_tables'],
                'title': 'Environment setup'}],
  'template_path': 'templates/notebooks/00_env_config.ipynb'},
 {'notebook_key': '01_agreement',
  'notebook_label': '`01_agreement`',
  'segment_intro': 'Standalone steward, agreement, and evidence widgets for Fabric stability.',
  'segments': [{'symbols': ['widget_render_data_steward',
                            'widget_render_data_agreement',
                            'widget_render_agreement_evidence'],
                'title': 'Agreement intake'}],
  'template_path': 'templates/notebooks/01_agreement.ipynb'},
 {'notebook_key': '02_pipeline',
  'notebook_label': '`02_pipeline`',
  'segment_intro': 'Thin production orchestration that keeps source reads, beginner-editable configs, transform logic, target writes, lineage relationships, and pipeline naming visible while package helpers handle reusable config enrichment, guardrails, and evidence plumbing.',
  'segments': [{'symbols': ['widget_select_agreement',
                            'get_selected_agreement',
                            'read_lakehouse_table',
                            'read_lakehouse_csv',
                            'read_lakehouse_parquet',
                            'read_lakehouse_excel',
                            'read_warehouse_table',
                            'prepare_pipeline_table_configs',
                            'run_table_guardrails',
                            'write_lakehouse_table',
                            'write_warehouse_table',
                            'write_pipeline_lineage',
                            'write_pipeline_run_summary'],
                'title': 'Pipeline run'}],
  'template_path': 'templates/notebooks/02_pipeline.ipynb'},
 {'notebook_key': '03_governance',
  'notebook_label': '`03_governance`',
  'segment_intro': 'Table-scoped governance review and approved metadata recording.',
  'segments': [{'symbols': ['widget_select_catalogue_table',
                            'get_selected_catalogue_table',
                            'load_catalogue_profile_rows',
                            'widget_review_column_context',
                            'widget_review_dq_rules',
                            'widget_review_column_classification',
                            'record_table_governance'],
                'title': 'Governance review'}],
  'template_path': 'templates/notebooks/03_governance.ipynb'},
 {'notebook_key': '99_explore',
  'notebook_label': '`99_explore`',
  'segment_intro': 'Optional discovery, profiling, troubleshooting, investigation, and ad hoc '
                   'analysis support.',
  'segments': [{'symbols': ['widget_select_agreement',
                            'read_lakehouse_table',
                            'read_lakehouse_csv',
                            'read_lakehouse_parquet',
                            'read_lakehouse_excel',
                            'read_warehouse_table',
                            'profile_dataframe'],
                'title': 'Exploration'}],
  'template_path': 'templates/notebooks/99_explore.ipynb'}]

PUBLIC_SYMBOL_DOCS: list[PublicSymbolDocMetadata] = [{'kind': 'function',
  'module': 'config',
  'function_type': 'callable',
  'summary_override': 'Shared environment setup and runtime validation for notebook templates.',
  'purpose': 'Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.',
  'symbol_name': 'setup_notebook',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap',
  'use_when': 'Use at the start of 00_env_config or a notebook template to validate FabricOps '
              'configuration, resolve required targets, and capture runtime context before other '
              'helpers run.',
  'when_to_use': ['Starting a FabricOps notebook from 00_env_config',
                  'Validating configured environment targets before downstream helpers run',
                  'Capturing runtime metadata for later lineage, review, or handover steps'],
  'do_not_use_when': 'Do not use as a replacement for metadata table setup or per-table governance '
                     'writes; call setup_metadata_tables for metadata storage preparation.',
  'parameters': 'config, env, optional required_targets, notebook_name, run_id_prefix, and '
                'local_fallback_name that define the runtime setup context.',
  'returns': 'NotebookSetupContext with resolved configuration paths, runtime metadata, '
             'smoke-check results, and readiness status.',
  'raises': 'ValueError for invalid configuration sections, missing required paths, or unresolved '
            'required targets.',
  'side_effects': 'Runs configuration validation and Fabric readiness checks; it does not write '
                  'FabricOps metadata tables.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify the returned context is ready before generating downstream notebook '
                     'code and confirm required targets resolve for the selected env.',
  'preferred_example': 'context = setup_notebook(CONFIG, env="Sandbox", '
                       'required_targets=["Source", "Unified"], notebook_name="00_env_config")',
  'related_functions': ['setup_metadata_tables']},
 {'kind': 'function',
  'module': 'config',
  'function_type': 'callable',
  'summary_override': 'Create or validate all FabricOps metadata tables through one setup action.',
  'symbol_name': 'setup_metadata_tables',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap',
  'use_when': 'Use after setup_notebook in 00_env_config to create or validate the FabricOps '
              'metadata tables required by agreement, profiling, lineage, stability, and governance '
              'workflows.',
  'do_not_use_when': 'Do not use for writing business data or pipeline target tables; use '
                     'write_lakehouse_table or write_warehouse_table for data outputs.',
  'parameters': 'config, env, optional spark_session, and mode/check options used to prepare '
                'metadata storage through configured metadata routing.',
  'returns': 'Setup result describing metadata table creation or validation status.',
  'raises': 'Raises configuration, Spark, or storage errors when metadata routing or table '
            'preparation fails.',
  'side_effects': 'Creates or validates FabricOps metadata tables in the configured metadata '
                  'lakehouse target.',
  'fabric_context': 'Requires the metadata target from 00_env_config; metadata tables must be '
                    'routed through CONFIG.path_config paths for the selected env.',
  'ai_verification': 'Verify metadata setup completes before recommending agreement, profiling, '
                     'lineage, stability, or governance workflows that persist evidence.',
  'preferred_example': 'setup_metadata_tables(CONFIG, env="Sandbox", spark_session=spark)',
  'related_functions': ['setup_notebook', 'record_table_governance']},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render the standalone data-steward intake widget.',
  'symbol_name': 'widget_render_data_steward',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake'},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render the standalone data-agreement intake widget.',
  'symbol_name': 'widget_render_data_agreement',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake'},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render the standalone agreement-evidence widget.',
  'symbol_name': 'widget_render_agreement_evidence',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake'},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render an agreement selector and optionally register the active notebook.',
  'symbol_name': 'widget_select_agreement',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Agreement selection',
  'use_when': 'Use in 02_pipeline or 99_explore notebooks to let a user select an approved data '
              'agreement before reading, profiling, or writing governed data.',
  'do_not_use_when': 'Do not use when an agreement has already been programmatically selected and '
                     'validated, or for catalogue table review selection in 03_governance.',
  'parameters': 'config, env, optional spark_session, and notebook registration options for '
                'loading agreement choices from metadata.',
  'returns': 'Interactive widget state; call get_selected_agreement to retrieve the selected '
             'agreement record.',
  'raises': 'Raises metadata read, widget dependency, or configuration errors when agreement '
            'metadata cannot be loaded.',
  'side_effects': 'Displays an IPython widget and may register the active notebook selection in '
                  'metadata when requested.',
  'fabric_context': 'Requires agreement metadata created through 01_agreement and metadata routing '
                    'from 00_env_config.',
  'ai_verification': 'Verify the user selected an agreement and call get_selected_agreement before '
                     'generating pipeline code that depends on agreement context.',
  'preferred_example': 'widget_select_agreement(CONFIG, env="Sandbox", spark_session=spark)\n'
                       'agreement = get_selected_agreement()',
  'related_functions': ['get_selected_agreement', 'setup_metadata_tables']},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Return the agreement selected by widget_select_agreement.',
  'symbol_name': 'get_selected_agreement',
  'template_notebook': '02_pipeline',
  'template_segment': 'Agreement selection',
  'use_when': 'Use immediately after widget_select_agreement to retrieve the selected agreement '
              'record for pipeline logic and evidence binding.',
  'do_not_use_when': 'Do not use before rendering and completing widget_select_agreement, or as a '
                     'substitute for querying all agreement metadata.',
  'parameters': 'No required parameters; reads the current in-memory widget selection state.',
  'returns': 'Selected agreement dictionary for the active notebook session.',
  'raises': 'Raises an error when no agreement has been selected in the current session.',
  'side_effects': 'Reads session/widget state only; it does not write metadata, tables, or files.',
  'fabric_context': 'Depends on a prior widget_select_agreement call in the same notebook session '
                    'and agreement metadata loaded via 00_env_config routing.',
  'ai_verification': 'Verify the returned agreement has the expected dataset/table identifiers '
                     'before using it to drive reads, writes, or governance evidence.',
  'preferred_example': 'agreement = get_selected_agreement()\n'
                       'dataset_name = agreement["dataset_name"]',
  'related_functions': ['widget_select_agreement']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a table from a configured Fabric lakehouse target.',
  'symbol_name': 'read_lakehouse_table',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a Delta table from a configured Fabric lakehouse target.',
  'do_not_use_when': 'Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for '
                     'warehouse SQL tables.',
  'parameters': 'config, env, target, table, optional schema, verbose flag, and spark_session.',
  'returns': 'Spark DataFrame loaded from the configured lakehouse table.',
  'raises': 'Raises configuration, Spark, or table-read errors when the target or table cannot be '
            'resolved/read.',
  'side_effects': 'Reads from a lakehouse table; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify the target/table name comes from CONFIG and check the returned '
                     'DataFrame schema or row count before downstream transformations.',
  'preferred_example': 'df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", '
                       'table="orders", spark_session=spark)',
  'related_functions': ['write_lakehouse_table',
                        'read_lakehouse_csv',
                        'read_lakehouse_parquet',
                        'read_lakehouse_excel']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Write a DataFrame to a configured Fabric lakehouse target.',
  'symbol_name': 'write_lakehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when publishing a Spark DataFrame to a configured Fabric lakehouse table.',
  'do_not_use_when': 'Do not use for metadata evidence tables unless the helper explicitly routes '
                     'metadata, and do not use for warehouse tables.',
  'parameters': 'df, config, env, target, table, optional schema, mode, and partitioning/write '
                'options.',
  'returns': 'None; the DataFrame is written to the configured lakehouse table.',
  'raises': 'Raises configuration, Spark, or write errors when the target cannot be resolved or '
            'the write fails.',
  'side_effects': 'Writes data to a Fabric lakehouse table using the selected write mode.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify upstream guardrails passed, confirm target routing from CONFIG, and '
                     'check the intended write mode before generating code that calls this helper.',
  'preferred_example': 'write_lakehouse_table(curated_df, CONFIG, env="Sandbox", target="Unified", '
                       'table="orders_curated", mode="overwrite")',
  'related_functions': ['read_lakehouse_table', 'write_warehouse_table', 'stop_if_failed']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a CSV file from a configured Fabric lakehouse Files path.',
  'symbol_name': 'read_lakehouse_csv',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a CSV file from a configured Fabric lakehouse Files path.',
  'do_not_use_when': 'Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL '
                     'tables.',
  'parameters': 'config, env, target, relative_path, CSV read options, verbose flag, and optional '
                'spark_session.',
  'returns': 'Spark DataFrame loaded from the lakehouse Files CSV path.',
  'raises': 'Raises ValueError for invalid file paths and configuration/Spark errors when the file '
            'cannot be read.',
  'side_effects': 'Reads from lakehouse Files; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify relative_path points under Files, then check row count and schema '
                     'after reading.',
  'preferred_example': 'df = read_lakehouse_csv(CONFIG, env="Sandbox", target="Source", '
                       'relative_path="raw/orders/orders.csv", header=True, spark_session=spark)',
  'related_functions': ['read_lakehouse_table', 'read_lakehouse_parquet', 'read_lakehouse_excel']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a Parquet path from a configured Fabric lakehouse Files path.',
  'symbol_name': 'read_lakehouse_parquet',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a Parquet file or path from a configured Fabric lakehouse Files '
              'path.',
  'do_not_use_when': 'Do not use for Delta tables, CSV files, Excel files, or warehouse SQL '
                     'tables.',
  'parameters': 'config, env, target, relative_path, verbose flag, and optional spark_session.',
  'returns': 'Spark DataFrame loaded from the original Parquet path or timestamp-converted '
             'fallback path.',
  'raises': 'Raises ValueError for invalid relative paths and Spark/read errors when the Parquet '
            'path cannot be loaded.',
  'side_effects': 'Reads from lakehouse Files and may create a local timestamp-converted fallback '
                  'for single-file Parquet precision issues; it does not write metadata tables.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify the file path is a lakehouse Files Parquet path and check row '
                     'count/schema after reading.',
  'preferred_example': 'df = read_lakehouse_parquet(CONFIG, env="Sandbox", target="Source", '
                       'relative_path="raw/orders/orders.parquet", spark_session=spark)',
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_excel', 'read_lakehouse_table']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read an Excel file from a configured Fabric lakehouse Files path.',
  'symbol_name': 'read_lakehouse_excel',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading .xlsx files from a configured Fabric lakehouse Files path, '
              'especially small reference files, mapping tables, or manually maintained business '
              'inputs.',
  'do_not_use_when': 'Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL '
                     'tables.',
  'parameters': 'config, env, target, relative_path, optional sheet_name, optional spark_session, '
                'and pandas read_excel keyword arguments.',
  'returns': 'Spark DataFrame converted from the selected Excel worksheet.',
  'raises': 'Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when '
            'the file cannot be read.',
  'side_effects': 'Reads from lakehouse Files through a temporary local Excel file; it does not '
                  'write metadata, tables, or files.',
  'fabric_context': 'Requires 00_env_config config/env/target context for resolving the configured '
                    'lakehouse Files path.',
  'ai_verification': 'Verify the DataFrame row count and schema after reading, and confirm the '
                     'Excel file is appropriate for a small reference-style input.',
  'preferred_example': 'mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", '
                       'relative_path="reference/faculty_mapping.xlsx", sheet_name=0, '
                       'spark_session=spark)',
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_parquet', 'read_lakehouse_table']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a table from a configured Fabric warehouse target.',
  'symbol_name': 'read_warehouse_table',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a table from a configured Fabric warehouse target.',
  'do_not_use_when': 'Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or '
                     'Excel paths.',
  'parameters': 'config, env, target, schema, table, optional verbose flag, and optional '
                'spark_session.',
  'returns': 'Spark DataFrame loaded from the configured warehouse table.',
  'raises': 'Raises configuration, Spark SQL, or warehouse-read errors when the target/table '
            'cannot be resolved/read.',
  'side_effects': 'Reads from a warehouse table; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify the warehouse target/schema/table are configured and inspect the '
                     'resulting DataFrame schema before downstream use.',
  'preferred_example': 'df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", '
                       'schema="dbo", table="orders", spark_session=spark)',
  'related_functions': ['write_warehouse_table', 'read_lakehouse_table']},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Write a DataFrame to a configured Fabric warehouse target.',
  'symbol_name': 'write_warehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when publishing a Spark DataFrame to a configured Fabric warehouse table.',
  'do_not_use_when': 'Do not use for lakehouse table writes, lakehouse Files writes, or metadata '
                     'evidence writes.',
  'parameters': 'df, config, env, target, schema, table, and write mode.',
  'returns': 'None; the DataFrame is written to the configured warehouse table.',
  'raises': 'Raises configuration, Spark connector, or warehouse write errors when the '
            'target/table cannot be written.',
  'side_effects': 'Writes data to a Fabric warehouse table using the selected mode.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify guardrails passed, confirm schema/table routing from CONFIG, and '
                     'check the intended write mode before calling.',
  'preferred_example': 'write_warehouse_table(serving_df, CONFIG, env="Sandbox", '
                       'target="Warehouse", schema="dbo", table="orders_serving", mode="append")',
  'related_functions': ['read_warehouse_table', 'write_lakehouse_table', 'stop_if_failed']},
 {'kind': 'function',
  'module': 'data_profiling',
  'function_type': 'callable',
  'summary_override': 'Profile a source or target DataFrame for schema, quality, and catalogue '
                      'evidence.',
  'symbol_name': 'profile_dataframe',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Profiling',
  'use_when': 'Use to create schema, null, distinct, min/max, and optional distribution evidence '
              'from a Spark DataFrame.',
  'do_not_use_when': 'Do not use as a data-quality enforcement step or as a persistence helper; it '
                     'builds profile rows but does not approve governance evidence.',
  'parameters': 'df, table_name, optional exclude_columns, timezone, distribution options, bin '
                'edges, category baselines, and top-N settings.',
  'returns': 'Spark DataFrame containing one profile row per eligible business column.',
  'raises': 'Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.',
  'side_effects': 'Computes profiling aggregations on the provided DataFrame; it does not write '
                  'metadata, tables, or files.',
  'fabric_context': 'Use after reading source/target data and before metadata persistence or '
                    'governance review workflows that need profile evidence.',
  'ai_verification': 'Verify the profile row count matches expected business columns and inspect '
                     'key schema/profile fields before writing evidence.',
  'preferred_example': 'profile_rows_df = profile_dataframe(df, table_name="orders", '
                       'include_distributions=True, distribution_columns=["status"] )',
  'related_functions': ['enforce_profile_behavior', 'record_table_governance']},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Validate a DataFrame schema using strict, allow-new-columns, or '
                      'monitor-only presets.',
  'symbol_name': 'validate_schema',
  'template_notebook': '02_pipeline',
  'template_segment': 'Schema validation',
  'use_when': 'Use before writes to compare a DataFrame schema against an expected schema with '
              'strict, allow-new-columns, or monitor-only behavior.',
  'do_not_use_when': 'Do not use for DQ-rule enforcement or metadata '
                     'persistence.',
  'parameters': 'dataframe, expected_schema mapping, and preset controlling blocking behavior.',
  'returns': 'Guardrail result dictionary with status, can_continue, checks, message, and schema '
             'difference details.',
  'raises': 'ValueError when preset is not one of the supported schema presets.',
  'side_effects': 'Inspects DataFrame schema only; it does not write metadata, tables, or files.',
  'fabric_context': 'Use in 02_pipeline before write helpers so schema guardrails run before '
                    'publishing data.',
  'ai_verification': 'Verify can_continue before calling write helpers and pass the result to '
                     'stop_if_failed when blocking behavior is required.',
  'preferred_example': 'schema_result = validate_schema(df, {"order_id": "string"}, '
                       'preset="allow_new_columns")\n'
                       'stop_if_failed(schema_result)',
  'related_functions': ['enforce_freshness', 'enforce_profile_behavior', 'stop_if_failed']},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Enforce whether the latest data arrived within the configured freshness lag.',
  'symbol_name': 'enforce_freshness',
  'template_notebook': '02_pipeline',
  'template_segment': 'Freshness enforcement',
  'use_when': 'Use in 02_pipeline to validate max(freshness_column) is at least today minus freshness_max_lag_days.',
  'do_not_use_when': 'Do not use for schema validation, load-behavior enforcement, or DQ-rule enforcement; use validate_schema, enforce_profile_behavior, or enforce_dq_rules for those checks.',
  'parameters': 'dataframe, freshness_column, max_lag_days, severity, and optional reference_date for deterministic validation.',
  'returns': 'Guardrail result dictionary with status, can_continue, latest_value, required_min_value, and freshness evidence fields.',
  'raises': 'ValueError when severity is unsupported, lag is missing for a configured column, lag is negative, or reference_date is invalid.',
  'side_effects': 'Computes max(freshness_column) on the provided DataFrame; it does not write metadata, tables, or files.',
  'fabric_context': 'Use in 02_pipeline after schema validation and before downstream writes so stale data can block or warn independently from profile behavior.',
  'ai_verification': 'Verify freshness_column and freshness_max_lag_days come from the table config and that blocking severity stops writes when can_continue is false.',
  'preferred_example': 'freshness_result = enforce_freshness(df, "business_date", 1, severity="blocking")\nstop_if_failed(freshness_result)',
  'related_functions': ['validate_schema', 'enforce_profile_behavior', 'stop_if_failed']},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.',
  'symbol_name': 'enforce_profile_behavior',
  'template_notebook': '02_pipeline',
  'template_segment': 'Profile behavior enforcement',
  'use_when': 'Use in 02_pipeline to enforce load_behavior expectations against previous accepted catalogue profile evidence.',
  'do_not_use_when': 'Do not use for simple schema validation or DQ-rule enforcement; use '
                     'validate_schema or enforce_dq_rules for those checks.',
  'parameters': 'spark, dataframe, metadata_table, dataset_name, table_name, required stage, '
                'run_id, load_behavior, optional watermark column, exclude_columns, and exclude_run_id.',
  'returns': 'Guardrail result dictionary with status, can_continue, message, current profile, '
             'baseline details, and profile behavior checks.',
  'raises': 'Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded '
            'or compared.',
  'side_effects': 'Reads baseline profile metadata and computes current profile evidence; it does '
                  'not write target data.',
  'fabric_context': 'Requires profile metadata routed through the configured 00_env_config '
                    'metadata target and a valid source/target stage.',
  'ai_verification': 'Verify baseline selection, status, and can_continue before allowing '
                     'downstream writes or calling stop_if_failed.',
  'preferred_example': 'stability_result = enforce_profile_behavior(spark, df, "METADATA_DATA_CATALOGUE", dataset_name, table_name, stage="target", run_id=run_id, load_behavior="overwrite")\n'
                       'stop_if_failed(stability_result)',
  'related_functions': ['profile_dataframe', 'validate_schema', 'enforce_freshness', 'stop_if_failed']},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks '
                      'continuation.',
  'symbol_name': 'stop_if_failed',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail enforcement',
  'use_when': 'Use after schema, freshness, profile behavior, or DQ guardrail helpers to stop the notebook when '
              'can_continue is false.',
  'do_not_use_when': 'Do not use for informational warnings that should not block execution, or '
                     'before a guardrail result exists.',
  'parameters': 'guardrail result dictionary and optional message/runtime controls.',
  'returns': 'None when execution may continue; otherwise raises or exits according to runtime '
             'behavior.',
  'raises': 'Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail '
            'must stop execution.',
  'side_effects': 'May terminate notebook execution through Fabric notebook utilities or raise an '
                  'exception.',
  'fabric_context': 'Use in 02_pipeline after validate_schema, enforce_freshness, enforce_profile_behavior, or '
                    'enforce_dq_rules and before write helpers.',
  'ai_verification': 'Verify the guardrail result shape includes status/can_continue/message '
                     'before passing it to stop_if_failed.',
  'preferred_example': 'schema_result = validate_schema(df, expected_schema)\n'
                       'stop_if_failed(schema_result)',
  'related_functions': ['validate_schema', 'enforce_freshness', 'enforce_profile_behavior', 'enforce_dq_rules']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Enforce approved active DQ rules as a target-write guardrail without '
                      'filtering rows.',
  'symbol_name': 'enforce_dq_rules',
  'template_notebook': '02_pipeline',
  'template_segment': 'DQ guardrails',
  'use_when': 'Use before target writes to enforce active approved DQ rules for a dataset/table as '
              'a pipeline guardrail.',
  'do_not_use_when': 'Do not use to filter bad rows, author new DQ rules, or bypass governance '
                     'review approval.',
  'parameters': 'dataframe, config, env, dataset_name, table_name, and optional spark_session.',
  'returns': 'Guardrail result dictionary with status, can_continue, checks, message, tagged '
             'dataframe, and summary fields.',
  'raises': 'Raises configuration, metadata-read, or Spark expression errors when approved rules '
            'cannot be loaded or evaluated.',
  'side_effects': 'Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it '
                  'does not filter the DataFrame or write target data.',
  'fabric_context': 'Requires active approved DQ-rule evidence in the configured metadata target '
                    'from 03_governance governance workflows.',
  'ai_verification': 'Verify approved metadata exists, inspect status/can_continue, and call '
                     'stop_if_failed before writing when blocking failures occur.',
  'preferred_example': 'dq_result = enforce_dq_rules(df, CONFIG, env, dataset_name, table_name, '
                       'spark_session=spark)\n'
                       'stop_if_failed(dq_result)',
  'related_functions': ['record_table_governance', 'stop_if_failed']},
 {'kind': 'function',
  'module': 'data_lineage',
  'function_type': 'callable',
  'summary_override': 'Build source-to-target lineage evidence records for a pipeline run.',
  'symbol_name': 'build_lineage_records',
  'template_notebook': '02_pipeline',
  'template_segment': 'Lineage evidence',
  'use_when': 'Use in pipeline notebooks to build source-to-target lineage evidence rows for a '
              'completed transformation run.',
  'do_not_use_when': 'Do not use to scan notebooks automatically or persist metadata; it only '
                     'builds records from supplied lineage inputs.',
  'parameters': 'dataset_name, run_id, source_tables, target_table, and transformation_steps.',
  'returns': 'List of lineage record dictionaries suitable for metadata persistence.',
  'raises': 'Raises normal Python errors if required lineage inputs are missing or malformed.',
  'side_effects': 'Pure record-building helper; it does not write metadata, tables, or files.',
  'fabric_context': 'Use with run context from 00_env_config and persist through configured '
                    'metadata routing when lineage evidence is required.',
  'ai_verification': 'Verify each source table, target table, transformation step, dataset_name, '
                     'and run_id are populated before persisting lineage records.',
 'preferred_example': 'lineage_rows = build_lineage_records(dataset_name=dataset_name, '
                       'run_id=run_id, source_tables=["source.orders"], '
                       'target_table="unified.orders", transformation_steps=[{"step": '
                       '"clean_orders"}])',
  'related_functions': ['setup_notebook', 'write_lakehouse_table']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Prepare source or target table configs for 02_pipeline.',
  'symbol_name': 'prepare_pipeline_table_configs',
  'template_notebook': '02_pipeline',
  'template_segment': 'Table config preparation',
  'use_when': 'Use after SOURCE_TABLES or TARGET_TABLES and their defaults are defined to derive standard config fields or add target audit columns.',
  'do_not_use_when': 'Do not use for ad hoc reads or writes outside the pipeline table-config pattern.',
  'parameters': 'table_configs, default_settings, table_role, and role-specific context such as run_id/pipeline_name for targets.',
  'returns': 'Enriched table configs and a dictionary keyed by table key.',
  'side_effects': 'Source role validates pre-loaded DataFrames. Target role adds FabricOps audit columns to target DataFrames.',
  'fabric_context': 'Source DataFrames should be loaded directly in the notebook with existing FabricOps read helpers. Target audit columns require a Spark-compatible DataFrame.',
  'ai_verification': 'Verify the correct table_role is used and enriched configs are passed to run_table_guardrails before transformation or writes.',
  'preferred_example': 'SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(SOURCE_TABLES, DEFAULT_SOURCE_GUARDRAILS, table_role="source")',
  'related_functions': ['run_table_guardrails', 'read_lakehouse_table']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.',
  'symbol_name': 'run_table_guardrails',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail orchestration',
  'use_when': 'Use in 02_pipeline to run source guardrails before transformation and target guardrails before writes while keeping per-table results separated.',
  'do_not_use_when': 'Do not use as a replacement for individual helper calls when debugging one specific guardrail interactively.',
  'parameters': 'table_configs plus config, env, run_id, spark_session, and agreement/notebook context.',
  'returns': 'Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.',
  'side_effects': 'Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.',
  'fabric_context': 'Requires CONFIG and env from 00_env_config so metadata operations use the configured metadata target.',
  'ai_verification': 'Verify stop_on_failure=True is used before transformation or writes when blocking guardrails should stop execution.',
  'preferred_example': 'source_guardrail_results = run_table_guardrails(SOURCE_TABLES, config=CONFIG, env=ENV_NAME, run_id=RUN_ID, spark_session=spark, stop_on_failure=True)',
  'related_functions': ['prepare_pipeline_table_configs', 'write_catalogue_evidence']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Enrich profile rows with guardrail context and write catalogue evidence.',
  'symbol_name': 'write_catalogue_evidence',
  'template_notebook': '02_pipeline',
  'template_segment': 'Catalogue evidence',
  'use_when': 'Use after source or target profiles and guardrail results are available to persist catalogue evidence through the configured metadata route.',
  'parameters': 'profiles, dataset definitions, config, env, run_id, agreement context, notebook context, and optional guardrail results.',
  'returns': 'Dictionary of write statuses keyed by dataset alias.',
  'side_effects': 'Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse target.',
  'related_functions': ['profile_dataframe', 'write_lakehouse_table']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Write many-to-many source-to-target lineage evidence.',
  'symbol_name': 'write_pipeline_lineage',
  'template_notebook': '02_pipeline',
  'template_segment': 'Lineage evidence',
  'use_when': 'Use after target writes to persist lineage relationships tied to agreement and notebook registry context.',
  'parameters': 'spark, config, env, run_id, source_definitions, target_definitions, relationships, and governance context.',
  'returns': 'Status, row count, and lineage rows.',
  'side_effects': 'Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse target.',
  'related_functions': ['write_catalogue_evidence', 'build_lineage_records', 'write_pipeline_run_summary']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Write one pipeline runtime summary row to metadata.',
  'symbol_name': 'write_pipeline_run_summary',
  'template_notebook': '02_pipeline',
  'template_segment': 'Runtime summary',
  'use_when': 'Use at the end of 02_pipeline to store operational run evidence in METADATA_PIPELINE_RUNS.',
  'parameters': 'spark, config, env, run_id, agreement context, source/target definitions, guardrail results, and evidence statuses.',
  'returns': 'Runtime summary row that was written.',
  'side_effects': 'Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.',
  'related_functions': ['write_catalogue_evidence', 'write_pipeline_lineage', 'write_lakehouse_table']},

 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render a searchable selector for latest successful catalogue profiles.',
  'symbol_name': 'widget_select_catalogue_table',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Return the table selected by widget_select_catalogue_table.',
  'symbol_name': 'get_selected_catalogue_table',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Load column profile rows for the selected catalogue table.',
  'symbol_name': 'load_catalogue_profile_rows',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render standalone business-context review guidance for selected profile '
                      'rows.',
  'symbol_name': 'widget_review_column_context',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render standalone DQ-rule review guidance for selected profile rows.',
  'symbol_name': 'widget_review_dq_rules',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render standalone sensitivity and PII classification review guidance for '
                      'selected profile rows.',
  'symbol_name': 'widget_review_column_classification',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Persist approved table-governance context, DQ-rule, and classification '
                      'evidence in one v1 commit action.',
  'symbol_name': 'record_table_governance',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review',
  'use_when': 'Use in 03_governance after human approval to persist approved column context, DQ rules, '
              'and classification evidence for a profiled table.',
  'do_not_use_when': 'Do not use to draft governance recommendations, bypass review approval, or '
                     'write unapproved rows.',
  'parameters': 'config, env, profile_rows, spark_session, optional approved '
                'context/DQ/classification review rows, approved_by, and mode.',
  'returns': 'Dictionary of records written for column_context, dq_rules, and '
             'column_classification.',
  'raises': 'Raises configuration, validation, Spark, or metadata-write errors when approved '
            'records cannot be built or persisted.',
  'side_effects': 'Writes approved governance metadata records to configured metadata tables.',
  'fabric_context': 'Requires 03_governance profile rows and 00_env_config metadata routing; '
                    'governance metadata must be written to the configured metadata target.',
  'ai_verification': 'Verify review_status is approved and commit is true for intended rows before '
                     'calling; confirm returned record groups match expected approvals.',
  'preferred_example': 'written = record_table_governance(CONFIG, env, profile_rows, '
                       'spark_session=spark, context_reviews=context_rows, '
                       'dq_rule_reviews=dq_rows, classification_reviews=classification_rows, '
                       'approved_by="reviewer")',
  'related_functions': ['load_catalogue_profile_rows',
                        'enforce_dq_rules',
                        'setup_metadata_tables']}]
