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
    expanded_purpose: NotRequired[str]
    summary_override: str | None
    use_when: NotRequired[str]
    when_to_use: NotRequired[list[str] | str]
    do_not_use_when: NotRequired[str]
    glossary_terms: NotRequired[list[str]]
    parameters: NotRequired[str | dict[str, str] | list[str]]
    returns: NotRequired[str]
    return_interpretation: NotRequired[str]
    raises: NotRequired[str | dict[str, str] | list[str]]
    common_failure_causes: NotRequired[str | list[str]]
    side_effects: NotRequired[str | list[str]]
    fabric_context: NotRequired[str]
    ai_verification: NotRequired[str | list[str]]
    preferred_example: NotRequired[str]
    related_functions: NotRequired[list[str]]
    related_guides: NotRequired[list[dict[str, str]]]


class ModuleDocMetadata(TypedDict):
    """Documentation metadata that drives module navigation and overview generation."""

    module_name: str
    visibility: str
    module_summary: str
    sidebar_group: str
    sidebar_include: bool


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


MODULE_DOCS_METADATA = [{'module_name': 'config',
  'visibility': 'public',
  'module_summary': 'Owns environment setup, runtime initialization, paths, and notebook-wide '
                    'configuration.',
  'sidebar_group': '0. Environment setup',
  'sidebar_include': True},
 {'module_name': 'data_agreement',
  'visibility': 'public',
  'module_summary': 'Owns agreement metadata capture, audited record building, metadata commit '
                    'helpers, agreement intake widgets, and 02_pipeline agreement '
                    'selection/registration helpers.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': True},
 {'module_name': 'data_profiling',
  'visibility': 'public',
  'module_summary': 'Owns deterministic profiling evidence such as schema, nulls, distincts, '
                    'min/max, and optional lightweight distributions.',
  'sidebar_group': '2. Analyst / data scientist',
  'sidebar_include': True},
 {'module_name': 'fabric_input_output',
  'visibility': 'public',
  'module_summary': 'Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.',
  'sidebar_group': '3. Data engineer',
  'sidebar_include': True},
 {'module_name': 'data_lineage',
  'visibility': 'public',
  'module_summary': 'Owns source-to-target lineage and transformation evidence.',
  'sidebar_group': '3. Data engineer',
  'sidebar_include': True},
 {'module_name': 'guardrails',
  'visibility': 'public',
  'module_summary': 'Owns schema, freshness, and profile behavior checks as pipeline guardrails '
                    'during runtime enforcement.',
  'sidebar_group': '3. Data engineer',
  'sidebar_include': True},
 {'module_name': 'metadata',
  'visibility': 'public',
  'module_summary': 'Owns metadata evidence persistence, stable keys, notebook registry, catalogue '
                    'keys, and runtime audit helpers.',
  'sidebar_group': '5. Metadata store',
  'sidebar_include': True},
 {'module_name': 'pipeline',
  'visibility': 'public',
  'module_summary': 'Owns thin 02_pipeline metadata evidence helpers for catalogue evidence '
                    'internals, lineage persistence, and runtime summaries.',
  'sidebar_group': '3. Data engineer',
  'sidebar_include': True},
 {'module_name': 'governance_review',
  'visibility': 'public',
  'module_summary': 'Owns current guardrail authoring and governance review widgets plus internal '
                    'review helpers required by the template-driven workflow.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': True},
 {'module_name': 'ai',
  'visibility': 'internal',
  'module_summary': 'Internal utility surface used by workflow-facing public functions.',
  'sidebar_group': 'Internal',
  'sidebar_include': False},
 {'module_name': 'schemas',
  'visibility': 'internal',
  'module_summary': 'Internal schema artifacts used for validation and contracts.',
  'sidebar_group': 'Internal',
  'sidebar_include': False}]

TEMPLATE_FLOW_DOCS = [{'notebook_key': '00_env_config',
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
  'segment_intro': 'Thin production orchestration that keeps source reads, beginner-editable '
                   'configs, transform logic, target writes, lineage relationships, and pipeline '
                   'naming visible while package helpers handle reusable config enrichment, '
                   'guardrails, and evidence plumbing.',
  'segments': [{'symbols': ['widget_select_agreement',
                            'get_selected_agreement',
                            'read_data',
                            'prepare_pipeline_table_configs',
                            'run_table_guardrails',
                            'write_data',
                            'write_pipeline_lineage',
                            'write_pipeline_run_summary',
                            'display_guardrail_results',
                            'widget_select_guardrail_target',
                            'widget_author_schema_freshness_profile_rules',
                            'widget_author_dq_rules',
                            'widget_enrich_table_metadata',
                            'widget_review_guardrail_governance'],
                'title': 'Pipeline run'}],
  'template_path': 'templates/notebooks/02_pipeline.ipynb'},
 {'notebook_key': '03_governance',
  'notebook_label': '`03_governance`',
  'segment_intro': 'Guardrail governance review using the current supported review widget flow.',
  'segments': [{'symbols': ['widget_select_guardrail_target',
                            'widget_author_guardrail_rules',
                            'widget_enrich_table_metadata',
                            'widget_review_table_governance'],
                'title': 'Guardrail governance review'}],
  'template_path': 'templates/notebooks/03_governance.ipynb'},
 {'notebook_key': '99_explore',
  'notebook_label': '`99_explore`',
  'segment_intro': 'Optional discovery, profiling, troubleshooting, investigation, and ad hoc '
                   'analysis support.',
  'segments': [{'symbols': ['read_data',
                            'profile_dataframe'],
                'title': 'Exploration'}],
  'template_path': 'templates/notebooks/99_explore.ipynb'},
 {'notebook_key': 'example_pipeline_demo',
  'notebook_label': '`example_pipeline_demo`',
  'segment_intro': 'Demo data seeding for the real pipeline template.',
  'segments': [{'symbols': ['write_data'],
                'title': 'Pipeline demo setup'}],
  'template_path': 'templates/notebooks/example_pipeline_demo.ipynb'},
 {'notebook_key': 'example_dq_rule_smoke_test',
  'notebook_label': '`example_dq_rule_smoke_test`',
  'segment_intro': 'Isolated DQ rule smoke-test checks for notebook authors.',
  'segments': [{'symbols': ['write_data', 'enforce_dq_rules'],
                'title': 'DQ smoke checks'}],
  'template_path': 'templates/notebooks/example_dq_rule_smoke_test.ipynb'}]

PUBLIC_SYMBOL_DOCS = [{'kind': 'function',
  'module': 'config',
  'function_type': 'callable',
  'summary_override': 'Shared environment setup and runtime validation for notebook templates.',
  'purpose': 'Prepare a FabricOps notebook by validating configuration, resolving environment '
             'targets, and returning reusable runtime context.',
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
  'related_functions': ['setup_metadata_tables'],
  'expanded_purpose': 'Validates the selected FabricOps environment, resolves configured runtime '
                      'targets, and returns the notebook context that downstream helpers depend '
                      'on.',
  'glossary_terms': ['notebook template', 'metadata lakehouse'],
  'return_interpretation': 'A ready context means required targets resolved and runtime checks '
                           'passed. Review validation messages before running downstream cells '
                           'when readiness is not successful.',
  'common_failure_causes': ['The environment name is not present in CONFIG.',
                            'Required targets are missing from path configuration.',
                            'Fabric runtime metadata is unavailable and no local fallback was '
                            'provided.',
                            'Configured lakehouse or warehouse targets cannot be resolved.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../how-fabricops-works/metadata-tables.md'}]},
 {'kind': 'function',
  'module': 'config',
  'function_type': 'callable',
  'summary_override': 'Create or validate all FabricOps metadata tables through one setup action.',
  'symbol_name': 'setup_metadata_tables',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap',
  'use_when': 'Use after setup_notebook in 00_env_config to create or validate the FabricOps '
              'metadata tables required by agreement, profiling, lineage, stability, and '
              'governance workflows.',
  'do_not_use_when': 'Do not use for writing business data or pipeline target tables; use '
                     'write_data or write_warehouse_table for data outputs.',
  'parameters': 'spark, config, env, and optional require_active_steward controls used to prepare '
                'metadata storage through configured metadata routing.',
  'returns': 'Setup result describing metadata table creation or validation status.',
  'raises': 'Raises configuration, Spark, or storage errors when metadata routing or table '
            'preparation fails.',
  'side_effects': 'Creates or validates FabricOps metadata tables through configured metadata '
                  'target ABFSS paths, not Spark partial namespaces.',
  'fabric_context': 'Requires the metadata target from 00_env_config; metadata tables are created '
                    'and validated through configured metadata target paths and do not require an '
                    'attached default lakehouse.',
  'ai_verification': 'Verify metadata setup completes before recommending agreement, profiling, '
                     'lineage, stability, or governance workflows that persist evidence.',
  'preferred_example': 'setup_metadata_tables(\n'
                       '    spark=spark,\n'
                       '    config=CONFIG,\n'
                       '    env="Sandbox",\n'
                       ')',
  'related_functions': ['setup_notebook', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Prepares FabricOps metadata tables through configured metadata target ABFSS '
                      'paths, not Spark partial namespaces or an attached default lakehouse.',
  'when_to_use': 'Use after setup_notebook in 00_env_config when bootstrapping or validating the '
                 'metadata store for an environment.',
  'glossary_terms': ['metadata lakehouse', 'catalogue evidence'],
  'return_interpretation': 'The returned setup status tells you which metadata tables were created '
                           'or validated and whether the environment is ready for workflows that '
                           'write evidence.',
  'common_failure_causes': ['The configured metadata lakehouse ABFSS path is missing or invalid.',
                            'Spark cannot create or inspect metadata tables through the configured '
                            'ABFSS paths.',
                            'The selected environment does not include metadata routing.',
                            'The caller lacks permission to create or update metadata tables.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../how-fabricops-works/metadata-tables.md'}]},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render the standalone data-steward intake widget.',
  'symbol_name': 'widget_render_data_steward',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake',
  'expanded_purpose': 'Renders the data steward intake widget so a notebook user can capture '
                      'steward contact and ownership details for an agreement workflow.',
  'when_to_use': 'Use in 01_agreement when collecting or updating data steward details before '
                 'creating a data agreement.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'The widget itself is the user interface; saved steward values are '
                           'available to downstream agreement evidence only after the user '
                           'completes the widget action.',
  'common_failure_causes': ['ipywidgets is not available in the runtime.',
                            'Required steward fields are left blank.',
                            'Widget state is cleared by rerunning cells out of order.',
                            'Metadata routing is unavailable when the widget tries to persist '
                            'records.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render the standalone data-agreement intake widget.',
  'symbol_name': 'widget_render_data_agreement',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake',
  'expanded_purpose': 'Renders the data agreement intake widget used to capture agreement '
                      'identity, scope, and business metadata for later notebook workflows.',
  'when_to_use': 'Use in 01_agreement after steward context exists and before pipeline or '
                 'governance notebooks need an approved agreement selection.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'The rendered widget collects agreement input; downstream helpers can '
                           'only use the agreement after the user saves valid values.',
  'common_failure_causes': ['ipywidgets is not available in the runtime.',
                            'Required agreement fields are missing.',
                            'Agreement identifiers conflict with existing metadata.',
                            'The metadata target cannot be written.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render the standalone agreement-evidence widget.',
  'symbol_name': 'widget_render_agreement_evidence',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake',
  'expanded_purpose': 'Renders the supporting-evidence widget for agreement workflows so users can '
                      'record links or files that justify an agreement.',
  'when_to_use': 'Use in 01_agreement when agreement records need supporting evidence that '
                 'downstream users can audit.',
  'glossary_terms': ['notebook template', 'catalogue evidence'],
  'return_interpretation': 'The widget records evidence references when saved; review the '
                           'resulting metadata rows before relying on them in handover or audit '
                           'flows.',
  'common_failure_causes': ['Evidence details are incomplete.',
                            'File or URL references are malformed.',
                            'Widget state is reset before saving.',
                            'The configured metadata target is not writable.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../how-fabricops-works/metadata-tables.md'}]},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Render an agreement selector and optionally register the active notebook.',
  'symbol_name': 'widget_select_agreement',
  'template_notebook': '02_pipeline',
  'template_segment': 'Agreement selection',
  'use_when': 'Use in 02_pipeline to select an approved data agreement and optionally register the '
              'active notebook before pipeline evidence is written.',
  'do_not_use_when': 'Do not use for guardrail target selection; use '
                     'widget_select_guardrail_target for catalogue-backed guardrail authoring and '
                     'review targets.',
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
  'related_functions': ['get_selected_agreement', 'setup_metadata_tables'],
  'expanded_purpose': 'Displays an agreement selector and stores the chosen agreement so pipeline '
                      'and exploration notebooks can bind work to approved business context.',
  'when_to_use': 'Use near the start of 02_pipeline or 99_explore before reads, profiling, '
                 'lineage, or governance evidence need an agreement id.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'A visible selection widget does not mean an agreement is selected; '
                           'call get_selected_agreement after the user chooses a row.',
  'common_failure_causes': ['No agreement metadata rows are available.',
                            'The user has not selected an agreement.',
                            'Notebook registration metadata cannot be written.',
                            'The configured metadata lakehouse cannot be read.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['widget_select_agreement'],
  'expanded_purpose': 'Returns the agreement chosen by widget_select_agreement so downstream cells '
                      'can pass consistent agreement identifiers to pipeline helpers.',
  'when_to_use': 'Use after rendering and completing widget_select_agreement when code needs the '
                 'selected agreement values.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'A returned dictionary contains the selected agreement fields. A '
                           'missing value means the selector has not been completed in the current '
                           'notebook state.',
  'common_failure_causes': ['widget_select_agreement has not been run.',
                            'The user has not selected an agreement.',
                            'Notebook state was reset.',
                            'The selected row is no longer present in metadata.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read Lakehouse tables, Lakehouse files, or Warehouse tables through one notebook-facing IO function.',
  'symbol_name': 'read_data',
  'template_notebook': '02_pipeline / 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use in starter notebooks when reading configured Fabric data without choosing a low-level storage helper.',
  'do_not_use_when': 'Do not use inside package internals that intentionally need a specific storage implementation helper.',
  'parameters': 'config, env, target, optional name, format, schema, table, relative_path, spark_session, options, and reader kwargs.',
  'returns': 'Spark DataFrame loaded from the configured Fabric target.',
  'raises': 'Raises ValueError for unsupported formats or missing table/path/schema inputs.',
  'side_effects': 'Reads data only; it does not write metadata, files, or tables.',
  'fabric_context': 'Routes reads through configured FabricOps environment targets instead of an attached/default lakehouse.',
  'ai_verification': 'Verify target, format, schema, and table/path values come from CONFIG or notebook parameters before generating calls.',
  'preferred_example': 'df_orders = read_data(CONFIG, ENV_NAME, "source", "orders", schema=SOURCE_SCHEMA, spark_session=spark)',
  'related_functions': ['write_data', 'profile_dataframe'],
  'expanded_purpose': 'Provides a stable notebook-facing read orchestrator while format-specific Lakehouse and Warehouse helpers remain implementation details.',
  'when_to_use': 'Use whenever a starter notebook needs to load data from a configured Fabric target.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'The returned DataFrame is the input for profiling, transformations, guardrails, or exploration.',
  'common_failure_causes': ['Unsupported format value.', 'Missing table, relative_path, or schema for the selected format.', 'Target kind does not match the selected format.'],
  'related_guides': [{'title': 'Notebook Templates', 'path': '../../how-fabricops-works/notebook-templates.md'}]},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Write Lakehouse or Warehouse targets through one notebook-facing IO function.',
  'symbol_name': 'write_data',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use in starter notebooks when writing configured Fabric data without choosing a low-level storage helper.',
  'do_not_use_when': 'Do not use inside package metadata persistence helpers that already use configured metadata routing.',
  'parameters': 'df, config, env, target, optional name, format, schema, table, mode, options, and writer kwargs.',
  'returns': 'None; the DataFrame is written to the configured Fabric target.',
  'raises': 'Raises ValueError for unsupported formats or missing table/schema inputs.',
  'side_effects': 'Writes data to the configured Fabric target.',
  'fabric_context': 'Routes writes through configured FabricOps environment targets instead of an attached/default lakehouse.',
  'ai_verification': 'Verify target, format, schema, table, and mode values before generating calls.',
  'preferred_example': 'write_data(df_orders, CONFIG, ENV_NAME, "unified", "orders_clean", schema=UNIFIED_SCHEMA, mode="overwrite")',
  'related_functions': ['read_data', 'run_table_guardrails'],
  'expanded_purpose': 'Provides a stable notebook-facing write orchestrator while format-specific Lakehouse and Warehouse helpers remain implementation details.',
  'when_to_use': 'Use whenever a starter notebook needs to publish data to a configured Fabric target.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'No value is returned; successful completion means the configured target write completed.',
  'common_failure_causes': ['Unsupported format value.', 'Missing table or schema for the selected format.', 'Target kind does not match the selected format.'],
  'related_guides': [{'title': 'Notebook Templates', 'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['read_data', 'read_lakehouse_parquet', 'read_lakehouse_excel'],
  'expanded_purpose': 'Reads a CSV file from the Files area of a configured Fabric lakehouse and '
                      'returns it as a Spark DataFrame.',
  'when_to_use': 'Use for file-based source ingestion when the source is CSV and should be '
                 'resolved through configured lakehouse paths.',
  'glossary_terms': ['source table', 'notebook template'],
  'return_interpretation': 'The returned DataFrame reflects Spark CSV parsing options; inspect '
                           'schema and sample rows before profiling or writing.',
  'common_failure_causes': ['The file path is wrong or outside the configured lakehouse.',
                            'CSV options do not match the file shape.',
                            'Spark cannot access the file.',
                            'The selected environment is missing the source lakehouse target.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_excel', 'read_data'],
  'expanded_purpose': 'Reads a Parquet file or folder from the Files area of a configured Fabric '
                      'lakehouse into a Spark DataFrame.',
  'when_to_use': 'Use for file-based source ingestion when the source is Parquet rather than a '
                 'managed table.',
  'glossary_terms': ['source table', 'notebook template'],
  'return_interpretation': 'The returned DataFrame uses the Parquet schema read by Spark; validate '
                           'it before downstream profile or guardrail checks.',
  'common_failure_causes': ['The Parquet path is missing or misspelled.',
                            'The file is not valid Parquet.',
                            'The configured lakehouse target is unavailable.',
                            'The caller lacks read permission.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_parquet', 'read_data'],
  'expanded_purpose': 'Reads an Excel file from a configured lakehouse Files path and converts it '
                      'into a Spark DataFrame for notebook processing.',
  'when_to_use': 'Use when source data arrives as an Excel workbook and should still follow '
                 'configured Fabric lakehouse routing.',
  'glossary_terms': ['source table', 'notebook template'],
  'return_interpretation': 'The returned DataFrame depends on workbook sheet and parsing options; '
                           'confirm headers and types before using it as pipeline input.',
  'common_failure_causes': ['The workbook path or sheet name is incorrect.',
                            'Excel parsing dependencies are unavailable.',
                            'The workbook layout does not match expected headers.',
                            'The configured lakehouse target cannot be read.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['write_warehouse_table', 'read_data'],
  'expanded_purpose': 'Reads data from a configured Fabric Warehouse table or query target into a '
                      'Spark DataFrame.',
  'when_to_use': 'Use when source data lives in a Fabric Warehouse rather than a lakehouse file or '
                 'Delta table.',
  'glossary_terms': ['source table', 'notebook template'],
  'return_interpretation': 'The returned DataFrame represents the warehouse read result; confirm '
                           'filters and row counts before profiling or transformation.',
  'common_failure_causes': ['The warehouse target is not configured.',
                            'The table or SQL text is invalid.',
                            'Warehouse connector context is unavailable.',
                            'The caller lacks warehouse read permission.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['read_warehouse_table', 'write_data', 'stop_if_failed'],
  'expanded_purpose': 'Writes a DataFrame to a configured Fabric Warehouse destination for '
                      'pipeline outputs that belong in warehouse storage.',
  'when_to_use': 'Use for target writes after guardrails pass and the configured output layer is a '
                 'warehouse table.',
  'glossary_terms': ['target table', 'guardrail'],
  'return_interpretation': 'A successful write means the helper submitted the DataFrame write to '
                           'the configured warehouse target; verify downstream table state for '
                           'business checks.',
  'common_failure_causes': ['The warehouse target is missing from configuration.',
                            'The target table name or write mode is invalid.',
                            'Warehouse connector support is unavailable.',
                            'The caller lacks write permission.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'}]},
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
  'related_functions': ['enforce_profile_behavior', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Builds deterministic profile evidence for a DataFrame, including schema, '
                      'row counts, nulls, distinct counts, and optional summary values.',
  'when_to_use': 'Use during exploration, governance review, or guardrail preparation when a table '
                 'needs reproducible profile evidence.',
  'glossary_terms': ['catalogue evidence', 'source table', 'target table'],
  'return_interpretation': 'Each returned profile row describes one table or column metric. '
                           'Downstream governance and guardrail helpers use those rows as '
                           'evidence.',
  'common_failure_causes': ['The DataFrame is empty or missing expected columns.',
                            'Requested statistics are unsupported for a column type.',
                            'Spark actions fail while computing counts or summaries.',
                            'Excluded columns remove fields needed for review.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                     {'title': 'Governance Review',
                      'path': '../../how-fabricops-works/governance-review.md'}]},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Enforce whether the latest data arrived within the configured freshness '
                      'lag.',
  'symbol_name': 'enforce_freshness',
  'template_notebook': '02_pipeline',
  'template_segment': 'Freshness enforcement',
  'use_when': 'Use in 02_pipeline to validate max(freshness_column) is at least today minus '
              'freshness_max_lag_days.',
  'do_not_use_when': 'Do not use for schema validation, load-behavior enforcement, or DQ-rule '
                     'enforcement; use enforce_profile_behavior or '
                     'enforce_dq_rules for those checks.',
  'parameters': 'dataframe, freshness_column, max_lag_days, severity, and optional reference_date '
                'for deterministic validation.',
  'returns': 'Guardrail result dictionary with status, can_continue, latest_value, '
             'required_min_value, and freshness evidence fields.',
  'raises': 'ValueError when severity is unsupported, lag is missing for a configured column, lag '
            'is negative, or reference_date is invalid.',
  'side_effects': 'Computes max(freshness_column) on the provided DataFrame; it does not write '
                  'metadata, tables, or files.',
  'fabric_context': 'Use in 02_pipeline after schema validation and before downstream writes so '
                    'stale data can block or warn independently from profile behavior.',
  'ai_verification': 'Verify freshness_column and freshness_max_lag_days come from the table '
                     'config and that blocking severity stops writes when can_continue is false.',
  'preferred_example': 'freshness_result = enforce_freshness(df, "business_date", 1, '
                       'severity="blocking")\n'
                       'stop_if_failed(freshness_result)',
  'related_functions': ['enforce_profile_behavior', 'stop_if_failed'],
  'expanded_purpose': 'Checks whether the latest value in a freshness column is recent enough for '
                      'the configured maximum lag before pipeline writes continue.',
  'when_to_use': 'Use as a pipeline guardrail when stale source or target data should block or '
                 'warn before downstream work proceeds.',
  'glossary_terms': ['guardrail', 'can_continue', 'source table', 'target table'],
  'return_interpretation': 'If can_continue is true, the latest freshness value is within the '
                           'allowed lag or the check was skipped. If false, investigate stale data '
                           'before writing outputs.',
  'common_failure_causes': ['The freshness column is missing.',
                            'The max lag value is missing or invalid.',
                            'The latest date is older than the allowed lag.',
                            'Severity is invalid or configured as blocking for stale data.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'}]},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Enforce static, changing, or skipped profile behavior against accepted '
                      'catalogue profile evidence.',
  'symbol_name': 'enforce_profile_behavior',
  'template_notebook': '02_pipeline',
  'template_segment': 'Profile behavior enforcement',
  'expanded_purpose': 'This function protects against silent data behavior changes. It compares '
                      'current static_data or changing_data profile evidence with previous '
                      'accepted catalogue evidence. If the current profile no longer matches the '
                      'approved baseline, the function returns a failed guardrail result so the '
                      'pipeline can stop before writing data.',
  'use_when': 'Use in 02_pipeline to enforce profile_mode expectations against previous accepted '
              'catalogue profile evidence.',
  'when_to_use': 'Use this when promoting or running a pipeline that should follow a previously '
                 'approved profile behavior pattern. It is especially useful when full-table '
                 'static data changes unexpectedly or when a previous watermark group changes or '
                 'disappears.',
  'do_not_use_when': 'Do not use for simple schema validation or DQ-rule enforcement; use '
                     'run_table_guardrails or enforce_dq_rules for those checks.',
  'glossary_terms': ['profile behavior',
                     'accepted catalogue profile evidence',
                     'baseline profile',
                     'stage',
                     'profile behavior check',
                     'guardrail',
                     'can_continue',
                     'static_data',
                     'changing_data',
                     'skip',
                     'metadata lakehouse'],
  'parameters': {'spark': 'Spark session used to read accepted profile evidence from the '
                          'configured metadata target.',
                 'dataframe': 'Current source or target DataFrame being checked.',
                 'metadata_table': 'Metadata table that stores accepted catalogue profile '
                                   'evidence.',
                 'dataset_name': 'Dataset name used to find matching catalogue evidence.',
                 'table_name': 'Table name used to find matching catalogue evidence.',
                 'stage': 'The part of the pipeline being checked, such as source or target.',
                 'run_id': 'Current pipeline run identifier recorded in the generated profile '
                           'evidence.',
                 'profile_mode': 'Profile behavior mode to evaluate: static_data, changing_data, '
                                 'or skip.',
                 'watermark_column': 'Column used to group changing_data profile evidence when '
                                     'configured.',
                 'exclude_columns': 'Optional columns to ignore while comparing profile fields.',
                 'exclude_run_id': 'Optional run id to exclude when selecting the accepted '
                                   'baseline evidence.'},
  'returns': 'Guardrail result dictionary with status, can_continue, message, current profile, '
             'baseline details, and profile behavior checks.',
  'return_interpretation': 'If can_continue is true, the current profile behavior matches the '
                           'accepted baseline and the pipeline can continue. If can_continue is '
                           'false, review whether the behavior change is intentional before '
                           'writing the table. If intentional, review or supersede the relevant '
                           'guardrail rule in governance. If not intentional, fix the source data '
                           'or pipeline configuration.',
  'raises': 'Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded '
            'or compared.',
  'common_failure_causes': ['Accepted profile evidence has not been created or approved yet.',
                            'The current profile behavior does not match the accepted baseline.',
                            'The configured dataset or table name does not match catalogue '
                            'evidence.',
                            'The configured stage does not match the accepted evidence.',
                            'The metadata lakehouse or catalogue profile table cannot be read.',
                            'The accepted evidence is missing required profile behavior fields.',
                            'The current profile_mode value is invalid or unsupported.',
                            'The accepted evidence is stale or incomplete.'],
  'side_effects': 'Reads baseline profile metadata and computes current profile evidence; it does '
                  'not write target data.',
  'fabric_context': 'Requires profile metadata routed through the configured 00_env_config '
                    'metadata target and a valid source/target stage.',
  'ai_verification': 'Verify baseline selection, status, and can_continue before allowing '
                     'downstream writes or calling stop_if_failed.',
  'preferred_example': 'stability_result = enforce_profile_behavior(\n'
                       '    spark=spark,\n'
                       '    dataframe=df,\n'
                       '    metadata_table="METADATA_DATA_CATALOGUE",\n'
                       '    dataset_name="sales_orders",\n'
                       '    table_name="orders_raw",\n'
                       '    stage="target",\n'
                       '    run_id=run_id,\n'
                       '    profile_mode="changing_data",\n'
                       '    watermark_column="business_date",\n'
                       ')\n'
                       'stop_if_failed(stability_result)',
  'related_functions': ['profile_dataframe',
                        'enforce_freshness',
                        'stop_if_failed'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                     {'title': 'Governance Review',
                      'path': '../../how-fabricops-works/governance-review.md'}]},
 {'kind': 'function',
  'module': 'guardrails',
  'function_type': 'callable',
  'summary_override': 'Stop a notebook only when a schema, freshness, profile behavior, or DQ '
                      'guardrail result blocks continuation.',
  'symbol_name': 'stop_if_failed',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail enforcement',
  'use_when': 'Use after schema, freshness, profile behavior, or DQ guardrail helpers to stop the '
              'notebook when can_continue is false.',
  'do_not_use_when': 'Do not use for informational warnings that should not block execution, or '
                     'before a guardrail result exists.',
  'parameters': 'guardrail result dictionary and optional message/runtime controls.',
  'returns': 'None when execution may continue; otherwise raises or exits according to runtime '
             'behavior.',
  'raises': 'Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail '
            'must stop execution.',
  'side_effects': 'May terminate notebook execution through Fabric notebook utilities or raise an '
                  'exception.',
  'fabric_context': 'Use in 02_pipeline after run_table_guardrails, enforce_freshness, '
                    'enforce_profile_behavior, or enforce_dq_rules and before write helpers.',
  'ai_verification': 'Verify the guardrail result shape includes status/can_continue/message '
                     'before passing it to stop_if_failed.',
  'preferred_example': 'guardrail_result = run_table_guardrails(table_configs, config=CONFIG, env=ENV_NAME, run_id=RUN_ID, spark_session=spark)\n'
                       'stop_if_failed(guardrail_result)',
  'related_functions': ['enforce_freshness',
                        'enforce_profile_behavior',
                        'enforce_dq_rules'],
  'expanded_purpose': 'Stops or raises for a blocking guardrail result so a notebook does not '
                      'continue into unsafe downstream writes.',
  'when_to_use': 'Use immediately after schema, freshness, profile behavior, or DQ guardrail '
                 'helpers when can_continue controls whether the pipeline should proceed.',
  'glossary_terms': ['guardrail', 'can_continue'],
  'return_interpretation': 'No return value means execution may continue. A blocking result raises '
                           'or exits according to runtime settings.',
  'common_failure_causes': ['The guardrail result is missing can_continue or status fields.',
                            'A blocking guardrail returned can_continue as false.',
                            'Notebook exit behavior is not supported in the current runtime.',
                            'The caller passed a warning result that should not stop execution.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'}]},
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
  'related_functions': ['widget_review_guardrail_governance', 'stop_if_failed'],
  'expanded_purpose': 'Evaluates approved data-quality rules against a DataFrame and returns '
                      'guardrail evidence that can block unsafe writes.',
  'when_to_use': 'Use in pipeline guardrails after governance-approved DQ rules exist for the '
                 'dataset and table.',
  'glossary_terms': ['guardrail', 'can_continue', 'catalogue evidence', 'metadata lakehouse'],
  'return_interpretation': 'When can_continue is true, active rules passed or only non-blocking '
                           'issues were found. When false, inspect failing rule details before '
                           'writing the table.',
  'common_failure_causes': ['No approved active DQ rules exist for the table.',
                            'Rule parameters are invalid or unsupported.',
                            'Required columns are missing from the DataFrame.',
                            'The metadata lakehouse cannot be read.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                     {'title': 'Governance Review',
                      'path': '../../how-fabricops-works/governance-review.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Prepare source or target table configs for 02_pipeline.',
  'symbol_name': 'prepare_pipeline_table_configs',
  'template_notebook': '02_pipeline',
  'template_segment': 'Table config preparation',
  'use_when': 'Use after SOURCE_TABLES or TARGET_TABLES and their defaults are defined to derive '
              'standard config fields or add target audit columns.',
  'do_not_use_when': 'Do not use for ad hoc reads or writes outside the pipeline table-config '
                     'pattern.',
  'parameters': 'table_configs, default_settings, table_role, and role-specific context such as '
                'run_id/pipeline_name for targets.',
  'returns': 'Enriched table configs and a dictionary keyed by table key.',
  'side_effects': 'Source role validates pre-loaded DataFrames. Target role adds FabricOps audit '
                  'columns to target DataFrames.',
  'fabric_context': 'Source DataFrames should be loaded directly in the notebook with existing '
                    'FabricOps read helpers. Target audit columns require a Spark-compatible '
                    'DataFrame.',
  'ai_verification': 'Verify the correct table_role is used and enriched configs are passed to '
                     'run_table_guardrails before transformation or writes.',
  'preferred_example': 'SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = '
                       'prepare_pipeline_table_configs(SOURCE_TABLES, {}, table_role="source")',
  'related_functions': ['run_table_guardrails', 'read_data'],
  'expanded_purpose': 'Normalizes source and target table configuration dictionaries so pipeline '
                      'guardrail, write, lineage, and evidence helpers receive consistent fields.',
  'when_to_use': 'Use before running table guardrails or writes when notebook-editable table '
                 'configs need package defaults and derived keys.',
  'glossary_terms': ['source table', 'target table', 'stage', 'guardrail'],
  'return_interpretation': 'The returned configs are enriched copies keyed for downstream helpers. '
                           'Confirm each table has the expected stage, key, and write settings.',
  'common_failure_causes': ['A table config is missing key or table_name fields.',
                            'Stage or write settings are inconsistent.',
                            'Source and target config shapes differ from expected dictionaries.',
                            'Defaults in CONFIG do not match the notebook environment.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'},
                     {'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Run profiling, schema, freshness, profile behavior, DQ, and catalogue '
                      'guardrails for table configs.',
  'symbol_name': 'run_table_guardrails',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail orchestration',
  'use_when': 'Use in 02_pipeline to run source guardrails before transformation and target '
              'guardrails before writes while keeping per-table results separated.',
  'do_not_use_when': 'Do not use as a replacement for individual helper calls when debugging one '
                     'specific guardrail interactively.',
  'parameters': 'table_configs plus config, env, run_id, spark_session, and agreement/notebook '
                'context.',
  'returns': 'Guardrail result bundle with profiles, schema results, freshness results, stability '
             'results, DQ results, catalogue status, evidence definitions, summary, can_continue, '
             'and failed_tables.',
  'side_effects': 'Profiles DataFrames, reads stability/DQ metadata through configured metadata '
                  'routing, writes catalogue evidence, and may update table config DataFrames with '
                  'DQ annotations.',
  'fabric_context': 'Requires CONFIG and env from 00_env_config so metadata operations use the '
                    'configured metadata target.',
  'ai_verification': 'Verify stop_on_failure=True is used before transformation or writes when '
                     'blocking guardrails should stop execution.',
  'preferred_example': 'source_guardrail_results = run_table_guardrails(SOURCE_TABLES, '
                       'config=CONFIG, env=ENV_NAME, run_id=RUN_ID, spark_session=spark, '
                       'stop_on_failure=True)',
  'related_functions': ['prepare_pipeline_table_configs', 'write_catalogue_evidence'],
  'expanded_purpose': 'Coordinates profiling, schema, freshness, profile behavior, DQ, and '
                      'catalogue evidence checks for a group of pipeline table configs.',
  'when_to_use': 'Use in 02_pipeline before transformations or writes when table configs should be '
                 'validated by the standard guardrail sequence.',
  'glossary_terms': ['guardrail',
                     'can_continue',
                     'source table',
                     'target table',
                     'catalogue evidence'],
  'return_interpretation': 'The result groups each guardrail outcome and a summary DataFrame. If '
                           'any blocking result has can_continue false, stop before writing data.',
  'common_failure_causes': ['One of the table configs is incomplete.',
                            'A schema, freshness, profile behavior, or DQ check fails.',
                            'Approved metadata evidence cannot be read.',
                            'Spark cannot profile or validate one of the DataFrames.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Enrich profile rows with guardrail context and write catalogue evidence.',
  'symbol_name': 'write_catalogue_evidence',
  'template_notebook': '02_pipeline',
  'template_segment': 'Catalogue evidence',
  'use_when': 'Use after source or target profiles and guardrail results are available to persist '
              'catalogue evidence through the configured metadata route.',
  'parameters': 'profiles, dataset definitions, config, env, run_id, agreement context, notebook '
                'context, and optional guardrail results.',
  'returns': 'Dictionary of write statuses keyed by dataset alias.',
  'side_effects': 'Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse '
                  'target.',
  'related_functions': ['profile_dataframe', 'write_data'],
  'expanded_purpose': 'Writes runtime catalogue evidence rows generated by pipeline guardrails to '
                      'the configured metadata target.',
  'when_to_use': 'Use after guardrail evidence is built and before governance or handover '
                 'workflows need the latest runtime evidence.',
  'glossary_terms': ['catalogue evidence', 'metadata lakehouse', 'guardrail'],
  'return_interpretation': 'The returned status summarizes which evidence rows were prepared or '
                           'written. Confirm expected table keys appear before relying on '
                           'governance review outputs.',
  'common_failure_causes': ['Evidence definitions are missing required fields.',
                            'The metadata lakehouse cannot be written.',
                            'Spark cannot convert evidence rows to the target schema.',
                            'The caller lacks metadata write permission.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../how-fabricops-works/metadata-tables.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Write many-to-many source-to-target lineage evidence.',
  'symbol_name': 'write_pipeline_lineage',
  'template_notebook': '02_pipeline',
  'template_segment': 'Lineage evidence',
  'use_when': 'Use after target writes to persist lineage relationships tied to agreement and '
              'notebook registry context.',
  'parameters': 'spark, config, env, run_id, source_definitions, target_definitions, '
                'relationships, and governance context.',
  'returns': 'Status, row count, and lineage rows.',
  'side_effects': 'Writes METADATA_DATA_LINEAGE_TABLE through the configured metadata lakehouse '
                  'target.',
  'related_functions': ['write_catalogue_evidence', 'write_pipeline_run_summary'],
  'expanded_purpose': 'Persists lineage records for a pipeline run so source tables, target '
                      'tables, and transformation steps remain traceable.',
  'when_to_use': 'Use near the end of 02_pipeline after transformations and target config '
                 'resolution have produced lineage-ready records.',
  'glossary_terms': ['source table', 'target table', 'catalogue evidence', 'metadata lakehouse'],
  'return_interpretation': 'A successful result indicates lineage rows were prepared for metadata '
                           'persistence; review returned counts against expected transformation '
                           'steps.',
  'common_failure_causes': ['Lineage records are empty or malformed.',
                            'run_id, source, or target identifiers are missing.',
                            'The metadata table cannot be written.',
                            'Audit fields cannot be resolved from configuration.'],
  'related_guides': [{'title': 'Notebook Templates',
                      'path': '../../how-fabricops-works/notebook-templates.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../how-fabricops-works/metadata-tables.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Write one pipeline runtime summary row to metadata.',
  'symbol_name': 'write_pipeline_run_summary',
  'template_notebook': '02_pipeline',
  'template_segment': 'Runtime summary',
  'use_when': 'Use at the end of 02_pipeline to store operational run evidence in '
              'METADATA_PIPELINE_RUNS.',
  'parameters': 'spark, config, env, run_id, agreement context, source/target definitions, '
                'guardrail results, and evidence statuses.',
  'returns': 'Runtime summary row that was written.',
  'side_effects': 'Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.',
  'related_functions': ['write_catalogue_evidence',
                        'write_pipeline_lineage',
                        'write_data'],
  'expanded_purpose': 'Writes a compact run-level summary that ties pipeline name, agreement '
                      'context, guardrail results, lineage, and write outcomes together.',
  'when_to_use': 'Use at the end of 02_pipeline when downstream operators need one metadata record '
                 'describing the run outcome.',
  'glossary_terms': ['guardrail', 'can_continue', 'catalogue evidence', 'metadata lakehouse'],
  'return_interpretation': 'The returned summary shows what run metadata was assembled or written. '
                           'Compare status and guardrail counts with expected pipeline outcomes.',
  'common_failure_causes': ['Required run identifiers are missing.',
                            'Guardrail result structures are malformed.',
                            'Metadata routing is unavailable.',
                            'The configured summary table cannot be written.'],
  'related_guides': [{'title': 'Pipeline Guardrails',
                      'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../how-fabricops-works/metadata-tables.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Evaluate freshness using an active metadata-backed freshness guardrail '
                      'rule.',
  'symbol_name': 'enforce_freshness_rule',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail enforcement',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Evaluates freshness using a metadata-backed guardrail rule so active '
                      'freshness intent from governance is enforced during pipeline execution.',
  'when_to_use': 'Use in 02_pipeline when active freshness rules from METADATA_GUARDRAIL_RULES '
                 'should determine the freshness column and maximum lag.',
  'do_not_use_when': 'Do not use to create or review freshness rules; use the guardrail authoring '
                     'and governance review widgets for lifecycle changes.',
  'glossary_terms': ['guardrail', 'metadata lakehouse', 'can_continue'],
  'return_interpretation': 'A can_continue value of true means the latest freshness value '
                           'satisfied the active rule or no blocking rule applied; false means the '
                           'run should stop after display.',
  'common_failure_causes': ['The freshness column is missing.',
                            'The max lag parameter is invalid.',
                            'No active freshness rule matches the table.',
                            'Metadata evidence cannot be read.']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Return summary, detailed, or debug guardrail display output for Fabric '
                      'notebooks.',
  'symbol_name': 'display_guardrail_results',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail display',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Returns summary, detailed, or debug guardrail display output so Fabric '
                      'notebooks show readable tables by default while preserving raw result '
                      'bundles for developers.',
  'when_to_use': 'Use in 02_pipeline immediately after run_table_guardrails and before '
                 'stop_if_failed so users see guardrail outcomes before the notebook stops.',
  'do_not_use_when': 'Do not use to mutate guardrail results or decide active rules; it is '
                     'presentation-only.',
  'glossary_terms': ['guardrail', 'notebook template'],
  'return_interpretation': 'Summary and detailed modes return display-friendly rows or Spark '
                           'DataFrames; debug mode returns the raw nested guardrail summary or '
                           'bundle.',
  'common_failure_causes': ['Mode is not summary, detailed, or debug.',
                            'The Spark session cannot create a DataFrame from display rows.',
                            'The result bundle is malformed.',
                            'The caller expects debug internals while using summary mode.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render a consolidated column metadata enrichment widget.',
  'symbol_name': 'widget_enrich_table_metadata',
  'template_notebook': '03_governance',
  'template_segment': 'Guardrail governance review',
  'use_when': 'Use in 03_governance after widget_select_guardrail_target to enrich selected catalogue columns with descriptive business context, sensitivity, PII, and configured custom metadata.',
  'parameters': 'See the source docstring for the selected guardrail state, configuration, environment, and Spark session parameters.',
  'returns': 'Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.',
  'related_functions': ['widget_select_guardrail_target', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or catalogue profile evidence.',
  'when_to_use': 'Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.',
  'do_not_use_when': 'Do not use to author DQ rules or runtime enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.',
  'glossary_terms': ['catalogue evidence', 'metadata lakehouse', 'guardrail'],
  'return_interpretation': 'The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT_RULES.',
  'common_failure_causes': ['The selected guardrail target has no column-level catalogue evidence.',
                            'Configured custom fields omit a field name.',
                            'Metadata lakehouse writes cannot be routed through 00_env_config.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render an interactive target selector for guardrail authoring and '
                      'governance review.',
  'symbol_name': 'widget_select_guardrail_target',
  'template_notebook': '02_pipeline / 03_governance',
  'template_segment': 'Guardrail authoring',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders an interactive selector that reads catalogue profile evidence, '
                      'existing guardrail rules, and table governance policy to create the '
                      'handover state for guardrail authoring or review.',
  'when_to_use': 'Use at the start of 02_pipeline authoring or 03_governance review when a user '
                 'must choose which profiled table to work on.',
  'do_not_use_when': 'Do not use for automatic pipeline enforcement or to write metadata; this '
                     'selector reads metadata and prepares widget state only.',
  'glossary_terms': ['catalogue evidence', 'guardrail', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The returned state includes environment, dataset, table, metadata '
                           'keys, profile rows, existing rules, and governance policy values for '
                           'downstream widgets.',
  'common_failure_causes': ['METADATA_DATA_CATALOGUE has no profile evidence.',
                            'The selected table lacks metadata identity fields.',
                            'Metadata tables cannot be read.',
                            'ipywidgets is unavailable.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render interactive schema, freshness, and profile-behavior guardrail '
                      'authoring controls.',
  'symbol_name': 'widget_author_schema_freshness_profile_rules',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail authoring',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders interactive controls for authoring schema, freshness, and '
                      'profile-behavior guardrail rule intent while applying the selected table '
                      'governance policy.',
  'when_to_use': 'Use in 02_pipeline after selecting a guardrail target to save active '
                 'self-approved rules, submit proposed rules, or bypass approval with a required '
                 'reason.',
  'do_not_use_when': 'Do not use to write catalogue evidence or runtime outcomes; it writes rule '
                     'intent only to METADATA_GUARDRAIL_RULES when saving.',
  'glossary_terms': ['guardrail', 'profile behavior', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget state exposes controls, preview records, and save actions '
                           'that produce append-only guardrail rule rows under the table policy.',
  'common_failure_causes': ['The handover state is missing columns.',
                            'Changing-data profile behavior has no watermark column.',
                            'Freshness max lag is invalid.',
                            'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render interactive manual DQ guardrail authoring controls.',
  'symbol_name': 'widget_author_dq_rules',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail authoring',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders manual DQ authoring controls that produce editable '
                      'guardrail rule intent rows under the selected table governance policy.',
  'when_to_use': 'Use in 02_pipeline after target selection when engineering needs to '
                 'batch-create, edit, clear, or draft DQ guardrail rules.',
  'do_not_use_when': 'Do not use for runtime DQ enforcement or catalogue profiling; use '
                     'enforce_dq_rules for execution and profile helpers for observed evidence.',
  'glossary_terms': ['guardrail', 'catalogue evidence', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget returns mutable preview records; '
                           'approved saves write guardrail rule intent to '
                           'METADATA_GUARDRAIL_RULES.',
  'common_failure_causes': ['Rule parameters are invalid for the selected DQ type.',
                            'Rule suggestions cannot be parsed.',
                            'Bypass reason is missing when bypass is requested.',
                            'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render combined guardrail authoring controls for the selected table.',
  'symbol_name': 'widget_author_guardrail_rules',
  'template_notebook': '03_governance',
  'template_segment': 'Author guardrail rules',
  'use_when': 'Use in 03_governance when governance users need to author schema, freshness, profile, or DQ guardrail records before formal review.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.',
  'returns': 'Combined widget states for schema/freshness/profile and DQ authoring.',
  'related_functions': ['widget_author_schema_freshness_profile_rules', 'widget_author_dq_rules', 'widget_review_table_governance'],
  'expanded_purpose': 'Renders the existing guardrail authoring widgets together so guardrail creation remains separate from formal governance review.',
  'when_to_use': 'Use after selecting a target in 03_governance when governance users need to create guardrail records.',
  'do_not_use_when': 'Do not use for formal approve, reject, replace, or deactivate decisions; use widget_review_table_governance.',
  'glossary_terms': ['guardrail', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The helper returns child widget states whose saves append guardrail intent to METADATA_GUARDRAIL_RULES.',
  'common_failure_causes': ['No target state is selected.', 'Rule parameters are invalid.', 'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render 03-only formal review controls for enrichment and guardrail records.',
  'symbol_name': 'widget_review_table_governance',
  'template_notebook': '03_governance',
  'template_segment': 'Review table governance',
  'use_when': 'Use in 03_governance after selecting a target to approve, reject, replace, deactivate, or view history for table governance records.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.',
  'returns': 'Widget controls and action helpers for formal governance review.',
  'related_functions': ['widget_select_guardrail_target', 'widget_enrich_table_metadata', 'widget_author_guardrail_rules'],
  'expanded_purpose': 'Renders the formal review workflow that reads and appends review history in METADATA_ENRICHMENT_RULES and METADATA_GUARDRAIL_RULES.',
  'when_to_use': 'Use only in 03_governance for formal governance review decisions.',
  'do_not_use_when': 'Do not use in 02_pipeline or for runtime enforcement results; runtime results belong in METADATA_GUARDRAIL_RESULTS.',
  'glossary_terms': ['guardrail', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget returns controls and action helpers that append formal review rows to the enrichment or guardrail rule history tables.',
  'common_failure_causes': ['The notebook context is not 03_governance.', 'No reviewable records are available.', 'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render interactive controls for reviewing proposed and bypassed guardrail '
                      'rules.',
  'symbol_name': 'widget_review_guardrail_governance',
  'template_notebook': '03_governance',
  'template_segment': 'Governance review',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders governance review controls for reviewing '
                      'proposed or bypass-active enrichment and guardrail rules, and applying approve, reject, or '
                      'supersede actions.',
  'when_to_use': 'Use in 03_governance after selecting a guardrail target to perform human review '
                 'of enrichment and guardrail rule intent.',
  'do_not_use_when': 'Do not use for automatic pipeline enforcement or profile evidence '
                     'generation; it is an interactive governance review widget.',
  'glossary_terms': ['guardrail', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget returns controls, current rule history, and action helpers '
                           'that write to enrichment or guardrail rule tables when '
                           'invoked.',
  'common_failure_causes': ['No target state is selected.',
                            'No proposed or bypassed rules are available for review.',
                            'Unsupported governance action is selected.',
                            'The metadata target cannot be written.']}]

PUBLIC_SYMBOL_DOCS_SUPPLEMENTAL = {'setup_notebook': {'expanded_purpose': 'Validates the selected FabricOps environment, resolves '
                                        'configured runtime targets, and returns the notebook '
                                        'context that downstream helpers depend on.',
                    'glossary_terms': ['notebook template', 'metadata lakehouse'],
                    'return_interpretation': 'A ready context means required targets resolved and '
                                             'runtime checks passed. Review validation messages '
                                             'before running downstream cells when readiness is '
                                             'not successful.',
                    'common_failure_causes': ['The environment name is not present in CONFIG.',
                                              'Required targets are missing from path '
                                              'configuration.',
                                              'Fabric runtime metadata is unavailable and no local '
                                              'fallback was provided.',
                                              'Configured lakehouse or warehouse targets cannot be '
                                              'resolved.']},
 'setup_metadata_tables': {'expanded_purpose': 'Prepares FabricOps metadata tables through '
                                               'configured metadata target ABFSS paths, not Spark '
                                               'partial namespaces or an attached default '
                                               'lakehouse.',
                           'when_to_use': 'Use after setup_notebook in 00_env_config when '
                                          'bootstrapping or validating the metadata store for an '
                                          'environment.',
                           'glossary_terms': ['metadata lakehouse', 'catalogue evidence'],
                           'return_interpretation': 'The returned setup status tells you which '
                                                    'metadata tables were created or validated and '
                                                    'whether the environment is ready for '
                                                    'workflows that write evidence.',
                           'common_failure_causes': ['The configured metadata lakehouse ABFSS path '
                                                     'is missing or invalid.',
                                                     'Spark cannot create or inspect metadata '
                                                     'tables through the configured ABFSS paths.',
                                                     'The selected environment does not include '
                                                     'metadata routing.',
                                                     'The caller lacks permission to create or '
                                                     'update metadata tables.']},
 'widget_render_data_steward': {'expanded_purpose': 'Renders the data steward intake widget so a '
                                                    'notebook user can capture steward contact and '
                                                    'ownership details for an agreement workflow.',
                                'when_to_use': 'Use in 01_agreement when collecting or updating '
                                               'data steward details before creating a data '
                                               'agreement.',
                                'glossary_terms': ['notebook template'],
                                'return_interpretation': 'The widget itself is the user interface; '
                                                         'saved steward values are available to '
                                                         'downstream agreement evidence only after '
                                                         'the user completes the widget action.',
                                'common_failure_causes': ['ipywidgets is not available in the '
                                                          'runtime.',
                                                          'Required steward fields are left blank.',
                                                          'Widget state is cleared by rerunning '
                                                          'cells out of order.',
                                                          'Metadata routing is unavailable when '
                                                          'the widget tries to persist records.']},
 'widget_render_data_agreement': {'expanded_purpose': 'Renders the data agreement intake widget '
                                                      'used to capture agreement identity, scope, '
                                                      'and business metadata for later notebook '
                                                      'workflows.',
                                  'when_to_use': 'Use in 01_agreement after steward context exists '
                                                 'and before pipeline or governance notebooks need '
                                                 'an approved agreement selection.',
                                  'glossary_terms': ['notebook template'],
                                  'return_interpretation': 'The rendered widget collects agreement '
                                                           'input; downstream helpers can only use '
                                                           'the agreement after the user saves '
                                                           'valid values.',
                                  'common_failure_causes': ['ipywidgets is not available in the '
                                                            'runtime.',
                                                            'Required agreement fields are '
                                                            'missing.',
                                                            'Agreement identifiers conflict with '
                                                            'existing metadata.',
                                                            'The metadata target cannot be '
                                                            'written.']},
 'widget_render_agreement_evidence': {'expanded_purpose': 'Renders the supporting-evidence widget '
                                                          'for agreement workflows so users can '
                                                          'record links or files that justify an '
                                                          'agreement.',
                                      'when_to_use': 'Use in 01_agreement when agreement records '
                                                     'need supporting evidence that downstream '
                                                     'users can audit.',
                                      'glossary_terms': ['notebook template', 'catalogue evidence'],
                                      'return_interpretation': 'The widget records evidence '
                                                               'references when saved; review the '
                                                               'resulting metadata rows before '
                                                               'relying on them in handover or '
                                                               'audit flows.',
                                      'common_failure_causes': ['Evidence details are incomplete.',
                                                                'File or URL references are '
                                                                'malformed.',
                                                                'Widget state is reset before '
                                                                'saving.',
                                                                'The configured metadata target is '
                                                                'not writable.']},
 'read_data': {'expanded_purpose': 'Reads a Delta table from the configured Fabric '
                                              'lakehouse target, resolving to '
                                              '{store.root}/Tables/{table} for classic targets or '
                                              '{store.root}/Tables/{schema}/{table} for '
                                              'schema-enabled targets.',
                          'when_to_use': 'Use when notebook code needs a managed lakehouse Delta '
                                         'table by ABFSS path rather than a file path, registered '
                                         'Spark table name, or warehouse SQL query.',
                          'glossary_terms': ['source table', 'metadata lakehouse'],
                          'return_interpretation': 'The returned DataFrame represents the resolved '
                                                   'lakehouse table; validate row counts and '
                                                   'schema before relying on it for guardrails or '
                                                   'writes.',
                          'common_failure_causes': ['The target or table name is misspelled.',
                                                    'The selected environment does not define the '
                                                    'requested lakehouse target.',
                                                    'Spark cannot access the table.',
                                                    'The caller lacks permission to read the '
                                                    'lakehouse.']},
 'write_data': {'expanded_purpose': 'Writes a DataFrame to the configured Fabric '
                                               'lakehouse target, resolving to '
                                               '{store.root}/Tables/{table} for classic targets or '
                                               '{store.root}/Tables/{schema}/{table} for '
                                               'schema-enabled targets.',
                           'when_to_use': 'Use for lakehouse or metadata table writes after '
                                          'guardrails have passed when the destination should be '
                                          'saved by ABFSS Delta path, not saveAsTable or a Spark '
                                          'namespace.',
                           'glossary_terms': ['target table', 'guardrail', 'metadata lakehouse'],
                           'return_interpretation': 'The helper returns the write operation result '
                                                    'from the underlying DataFrame writer when '
                                                    'available; verify downstream table state for '
                                                    'business validation.',
                           'common_failure_causes': ['Guardrails were skipped before a target '
                                                     'write.',
                                                     'The target lakehouse is not configured for '
                                                     'the environment.',
                                                     'The write mode is unsupported for the '
                                                     'destination.',
                                                     'The caller lacks write permission or Spark '
                                                     'cannot create the table.']},
 'read_lakehouse_csv': {'expanded_purpose': 'Reads a CSV file from the Files area of a configured '
                                            'Fabric lakehouse and returns it as a Spark DataFrame.',
                        'when_to_use': 'Use for file-based source ingestion when the source is CSV '
                                       'and should be resolved through configured lakehouse paths.',
                        'glossary_terms': ['source table', 'notebook template'],
                        'return_interpretation': 'The returned DataFrame reflects Spark CSV '
                                                 'parsing options; inspect schema and sample rows '
                                                 'before profiling or writing.',
                        'common_failure_causes': ['The file path is wrong or outside the '
                                                  'configured lakehouse.',
                                                  'CSV options do not match the file shape.',
                                                  'Spark cannot access the file.',
                                                  'The selected environment is missing the source '
                                                  'lakehouse target.']},
 'read_lakehouse_parquet': {'expanded_purpose': 'Reads a Parquet file or folder from the Files '
                                                'area of a configured Fabric lakehouse into a '
                                                'Spark DataFrame.',
                            'when_to_use': 'Use for file-based source ingestion when the source is '
                                           'Parquet rather than a managed table.',
                            'glossary_terms': ['source table', 'notebook template'],
                            'return_interpretation': 'The returned DataFrame uses the Parquet '
                                                     'schema read by Spark; validate it before '
                                                     'downstream profile or guardrail checks.',
                            'common_failure_causes': ['The Parquet path is missing or misspelled.',
                                                      'The file is not valid Parquet.',
                                                      'The configured lakehouse target is '
                                                      'unavailable.',
                                                      'The caller lacks read permission.']},
 'read_lakehouse_excel': {'expanded_purpose': 'Reads an Excel file from a configured lakehouse '
                                              'Files path and converts it into a Spark DataFrame '
                                              'for notebook processing.',
                          'when_to_use': 'Use when source data arrives as an Excel workbook and '
                                         'should still follow configured Fabric lakehouse routing.',
                          'glossary_terms': ['source table', 'notebook template'],
                          'return_interpretation': 'The returned DataFrame depends on workbook '
                                                   'sheet and parsing options; confirm headers and '
                                                   'types before using it as pipeline input.',
                          'common_failure_causes': ['The workbook path or sheet name is incorrect.',
                                                    'Excel parsing dependencies are unavailable.',
                                                    'The workbook layout does not match expected '
                                                    'headers.',
                                                    'The configured lakehouse target cannot be '
                                                    'read.']},
 'read_warehouse_table': {'expanded_purpose': 'Reads data from a configured Fabric Warehouse table '
                                              'or query target into a Spark DataFrame.',
                          'when_to_use': 'Use when source data lives in a Fabric Warehouse rather '
                                         'than a lakehouse file or Delta table.',
                          'glossary_terms': ['source table', 'notebook template'],
                          'return_interpretation': 'The returned DataFrame represents the '
                                                   'warehouse read result; confirm filters and row '
                                                   'counts before profiling or transformation.',
                          'common_failure_causes': ['The warehouse target is not configured.',
                                                    'The table or SQL text is invalid.',
                                                    'Warehouse connector context is unavailable.',
                                                    'The caller lacks warehouse read permission.']},
 'write_warehouse_table': {'expanded_purpose': 'Writes a DataFrame to a configured Fabric '
                                               'Warehouse destination for pipeline outputs that '
                                               'belong in warehouse storage.',
                           'when_to_use': 'Use for target writes after guardrails pass and the '
                                          'configured output layer is a warehouse table.',
                           'glossary_terms': ['target table', 'guardrail'],
                           'return_interpretation': 'A successful write means the helper submitted '
                                                    'the DataFrame write to the configured '
                                                    'warehouse target; verify downstream table '
                                                    'state for business checks.',
                           'common_failure_causes': ['The warehouse target is missing from '
                                                     'configuration.',
                                                     'The target table name or write mode is '
                                                     'invalid.',
                                                     'Warehouse connector support is unavailable.',
                                                     'The caller lacks write permission.']},
 'profile_dataframe': {'expanded_purpose': 'Builds deterministic profile evidence for a DataFrame, '
                                           'including schema, row counts, nulls, distinct counts, '
                                           'and optional summary values.',
                       'when_to_use': 'Use during exploration, governance review, or guardrail '
                                      'preparation when a table needs reproducible profile '
                                      'evidence.',
                       'glossary_terms': ['catalogue evidence', 'source table', 'target table'],
                       'return_interpretation': 'Each returned profile row describes one table or '
                                                'column metric. Downstream governance and '
                                                'guardrail helpers use those rows as evidence.',
                       'common_failure_causes': ['The DataFrame is empty or missing expected '
                                                 'columns.',
                                                 'Requested statistics are unsupported for a '
                                                 'column type.',
                                                 'Spark actions fail while computing counts or '
                                                 'summaries.',
                                                 'Excluded columns remove fields needed for '
                                                 'review.']},
 'enforce_freshness': {'expanded_purpose': 'Checks whether the latest value in a freshness column '
                                           'is recent enough for the configured maximum lag before '
                                           'pipeline writes continue.',
                       'when_to_use': 'Use as a pipeline guardrail when stale source or target '
                                      'data should block or warn before downstream work proceeds.',
                       'glossary_terms': ['guardrail',
                                          'can_continue',
                                          'source table',
                                          'target table'],
                       'return_interpretation': 'If can_continue is true, the latest freshness '
                                                'value is within the allowed lag or the check was '
                                                'skipped. If false, investigate stale data before '
                                                'writing outputs.',
                       'common_failure_causes': ['The freshness column is missing.',
                                                 'The max lag value is missing or invalid.',
                                                 'The latest date is older than the allowed lag.',
                                                 'Severity is invalid or configured as blocking '
                                                 'for stale data.']},
 'enforce_profile_behavior': {'expanded_purpose': 'This function protects against silent data '
                                                  'behavior changes. It compares current '
                                                  'static_data or changing_data profile evidence '
                                                  'with previous accepted catalogue evidence. If '
                                                  'the current profile no longer matches the '
                                                  'approved baseline, the function returns a '
                                                  'failed guardrail result so the pipeline can '
                                                  'stop before writing data.',
                              'when_to_use': 'Use this when promoting or running a pipeline that '
                                             'should follow a previously approved profile behavior '
                                             'pattern. It is especially useful when full-table '
                                             'static data changes unexpectedly or when a previous '
                                             'watermark group changes or disappears.',
                              'glossary_terms': ['profile behavior',
                                                 'accepted catalogue profile evidence',
                                                 'baseline profile',
                                                 'stage',
                                                 'profile behavior check',
                                                 'guardrail',
                                                 'can_continue',
                                                 'static_data',
                                                 'changing_data',
                                                 'skip',
                                                 'metadata lakehouse'],
                              'return_interpretation': 'If can_continue is true, the current '
                                                       'profile behavior matches the accepted '
                                                       'baseline and the pipeline can continue. If '
                                                       'can_continue is false, review whether the '
                                                       'behavior change is intentional before '
                                                       'writing the table. If intentional, review '
                                                       'or supersede the relevant guardrail rule '
                                                       'in governance. If not intentional, fix the '
                                                       'source data or pipeline configuration.',
                              'common_failure_causes': ['Accepted profile evidence has not been '
                                                        'created or approved yet.',
                                                        'The current profile behavior does not '
                                                        'match the accepted baseline.',
                                                        'The configured dataset or table name does '
                                                        'not match catalogue evidence.',
                                                        'The configured stage does not match the '
                                                        'accepted evidence.',
                                                        'The metadata lakehouse or catalogue '
                                                        'profile table cannot be read.',
                                                        'The accepted evidence is missing required '
                                                        'profile behavior fields.',
                                                        'The current profile_mode value is invalid '
                                                        'or unsupported.',
                                                        'The accepted evidence is stale or '
                                                        'incomplete.']},
 'stop_if_failed': {'expanded_purpose': 'Stops or raises for a blocking guardrail result so a '
                                        'notebook does not continue into unsafe downstream writes.',
                    'when_to_use': 'Use immediately after schema, freshness, profile behavior, or '
                                   'DQ guardrail helpers when can_continue controls whether the '
                                   'pipeline should proceed.',
                    'glossary_terms': ['guardrail', 'can_continue'],
                    'return_interpretation': 'No return value means execution may continue. A '
                                             'blocking result raises or exits according to runtime '
                                             'settings.',
                    'common_failure_causes': ['The guardrail result is missing can_continue or '
                                              'status fields.',
                                              'A blocking guardrail returned can_continue as '
                                              'false.',
                                              'Notebook exit behavior is not supported in the '
                                              'current runtime.',
                                              'The caller passed a warning result that should not '
                                              'stop execution.']},
 'enforce_dq_rules': {'expanded_purpose': 'Evaluates approved data-quality rules against a '
                                          'DataFrame and returns guardrail evidence that can block '
                                          'unsafe writes.',
                      'when_to_use': 'Use in pipeline guardrails after governance-approved DQ '
                                     'rules exist for the dataset and table.',
                      'glossary_terms': ['guardrail',
                                         'can_continue',
                                         'catalogue evidence',
                                         'metadata lakehouse'],
                      'return_interpretation': 'When can_continue is true, active rules passed or '
                                               'only non-blocking issues were found. When false, '
                                               'inspect failing rule details before writing the '
                                               'table.',
                      'common_failure_causes': ['No approved active DQ rules exist for the table.',
                                                'Rule parameters are invalid or unsupported.',
                                                'Required columns are missing from the DataFrame.',
                                                'The metadata lakehouse cannot be read.']},
 'prepare_pipeline_table_configs': {'expanded_purpose': 'Normalizes source and target table '
                                                        'configuration dictionaries so pipeline '
                                                        'guardrail, write, lineage, and evidence '
                                                        'helpers receive consistent fields.',
                                    'when_to_use': 'Use before running table guardrails or writes '
                                                   'when notebook-editable table configs need '
                                                   'package defaults and derived keys.',
                                    'glossary_terms': ['source table',
                                                       'target table',
                                                       'stage',
                                                       'guardrail'],
                                    'return_interpretation': 'The returned configs are enriched '
                                                             'copies keyed for downstream helpers. '
                                                             'Confirm each table has the expected '
                                                             'stage, key, and write settings.',
                                    'common_failure_causes': ['A table config is missing key or '
                                                              'table_name fields.',
                                                              'Stage or write settings are '
                                                              'inconsistent.',
                                                              'Source and target config shapes '
                                                              'differ from expected dictionaries.',
                                                              'Defaults in CONFIG do not match the '
                                                              'notebook environment.']},
 'run_table_guardrails': {'expanded_purpose': 'Coordinates profiling, schema, freshness, profile '
                                              'behavior, DQ, and catalogue evidence checks for a '
                                              'group of pipeline table configs.',
                          'when_to_use': 'Use in 02_pipeline before transformations or writes when '
                                         'table configs should be validated by the standard '
                                         'guardrail sequence.',
                          'glossary_terms': ['guardrail',
                                             'can_continue',
                                             'source table',
                                             'target table',
                                             'catalogue evidence'],
                          'return_interpretation': 'The result groups each guardrail outcome and a '
                                                   'summary DataFrame. If any blocking result has '
                                                   'can_continue false, stop before writing data.',
                          'common_failure_causes': ['One of the table configs is incomplete.',
                                                    'A schema, freshness, profile behavior, or DQ '
                                                    'check fails.',
                                                    'Approved metadata evidence cannot be read.',
                                                    'Spark cannot profile or validate one of the '
                                                    'DataFrames.']},
 'write_catalogue_evidence': {'expanded_purpose': 'Writes runtime catalogue evidence rows '
                                                  'generated by pipeline guardrails to the '
                                                  'configured metadata target.',
                              'when_to_use': 'Use after guardrail evidence is built and before '
                                             'governance or handover workflows need the latest '
                                             'runtime evidence.',
                              'glossary_terms': ['catalogue evidence',
                                                 'metadata lakehouse',
                                                 'guardrail'],
                              'return_interpretation': 'The returned status summarizes which '
                                                       'evidence rows were prepared or written. '
                                                       'Confirm expected table keys appear before '
                                                       'relying on governance review outputs.',
                              'common_failure_causes': ['Evidence definitions are missing required '
                                                        'fields.',
                                                        'The metadata lakehouse cannot be written.',
                                                        'Spark cannot convert evidence rows to the '
                                                        'target schema.',
                                                        'The caller lacks metadata write '
                                                        'permission.']},
 'write_pipeline_lineage': {'expanded_purpose': 'Persists lineage records for a pipeline run so '
                                                'source tables, target tables, and transformation '
                                                'steps remain traceable.',
                            'when_to_use': 'Use near the end of 02_pipeline after transformations '
                                           'and target config resolution have produced '
                                           'lineage-ready records.',
                            'glossary_terms': ['source table',
                                               'target table',
                                               'catalogue evidence',
                                               'metadata lakehouse'],
                            'return_interpretation': 'A successful result indicates lineage rows '
                                                     'were prepared for metadata persistence; '
                                                     'review returned counts against expected '
                                                     'transformation steps.',
                            'common_failure_causes': ['Lineage records are empty or malformed.',
                                                      'run_id, source, or target identifiers are '
                                                      'missing.',
                                                      'The metadata table cannot be written.',
                                                      'Audit fields cannot be resolved from '
                                                      'configuration.']},
 'write_pipeline_run_summary': {'expanded_purpose': 'Writes a compact run-level summary that ties '
                                                    'pipeline name, agreement context, guardrail '
                                                    'results, lineage, and write outcomes '
                                                    'together.',
                                'when_to_use': 'Use at the end of 02_pipeline when downstream '
                                               'operators need one metadata record describing the '
                                               'run outcome.',
                                'glossary_terms': ['guardrail',
                                                   'can_continue',
                                                   'catalogue evidence',
                                                   'metadata lakehouse'],
                                'return_interpretation': 'The returned summary shows what run '
                                                         'metadata was assembled or written. '
                                                         'Compare status and guardrail counts with '
                                                         'expected pipeline outcomes.',
                                'common_failure_causes': ['Required run identifiers are missing.',
                                                          'Guardrail result structures are '
                                                          'malformed.',
                                                          'Metadata routing is unavailable.',
                                                          'The configured summary table cannot be '
                                                          'written.']},

 'enforce_freshness_rule': {'expanded_purpose': 'Evaluates freshness using a metadata-backed '
                                                'guardrail rule so active freshness intent from '
                                                'governance is enforced during pipeline execution.',
                            'when_to_use': 'Use in 02_pipeline when active freshness rules from '
                                           'METADATA_GUARDRAIL_RULES should determine the '
                                           'freshness column and maximum lag.',
                            'do_not_use_when': 'Do not use to create or review freshness rules; '
                                               'use the guardrail authoring and governance review '
                                               'widgets for lifecycle changes.',
                            'glossary_terms': ['guardrail', 'metadata lakehouse', 'can_continue'],
                            'return_interpretation': 'A can_continue value of true means the '
                                                     'latest freshness value satisfied the active '
                                                     'rule or no blocking rule applied; false '
                                                     'means the run should stop after display.',
                            'common_failure_causes': ['The freshness column is missing.',
                                                      'The max lag parameter is invalid.',
                                                      'No active freshness rule matches the table.',
                                                      'Metadata evidence cannot be read.']},
 'display_guardrail_results': {'expanded_purpose': 'Returns summary, detailed, or debug guardrail '
                                                   'display output so Fabric notebooks show '
                                                   'readable tables by default while preserving '
                                                   'raw result bundles for developers.',
                               'when_to_use': 'Use in 02_pipeline immediately after '
                                              'run_table_guardrails and before stop_if_failed so '
                                              'users see guardrail outcomes before the notebook '
                                              'stops.',
                               'do_not_use_when': 'Do not use to mutate guardrail results or '
                                                  'decide active rules; it is presentation-only.',
                               'glossary_terms': ['guardrail', 'notebook template'],
                               'return_interpretation': 'Summary and detailed modes return '
                                                        'display-friendly rows or Spark '
                                                        'DataFrames; debug mode returns the raw '
                                                        'nested guardrail summary or bundle.',
                               'common_failure_causes': ['Mode is not summary, detailed, or debug.',
                                                         'The Spark session cannot create a '
                                                         'DataFrame from display rows.',
                                                         'The result bundle is malformed.',
                                                         'The caller expects debug internals while '
                                                         'using summary mode.']},
 'widget_select_guardrail_target': {'expanded_purpose': 'Renders an interactive selector that '
                                                        'reads catalogue profile evidence, '
                                                        'existing guardrail rules, and table '
                                                        'governance policy to create the handover '
                                                        'state for guardrail authoring or review.',
                                    'when_to_use': 'Use at the start of 02_pipeline authoring or '
                                                   '03_governance review when a user must choose '
                                                   'which profiled table to work on.',
                                    'do_not_use_when': 'Do not use for automatic pipeline '
                                                       'enforcement or to write metadata; this '
                                                       'selector reads metadata and prepares '
                                                       'widget state only.',
                                    'glossary_terms': ['catalogue evidence',
                                                       'guardrail',
                                                       'metadata lakehouse',
                                                       'notebook template'],
                                    'return_interpretation': 'The returned state includes '
                                                             'environment, dataset, table, '
                                                             'metadata keys, profile rows, '
                                                             'existing rules, and governance '
                                                             'policy values for downstream '
                                                             'widgets.',
                                    'common_failure_causes': ['METADATA_DATA_CATALOGUE has no '
                                                              'profile evidence.',
                                                              'The selected table lacks metadata '
                                                              'identity fields.',
                                                              'Metadata tables cannot be read.',
                                                              'ipywidgets is unavailable.']},
 'widget_author_schema_freshness_profile_rules': {'expanded_purpose': 'Renders interactive '
                                                                      'controls for authoring '
                                                                      'schema, freshness, and '
                                                                      'profile-behavior guardrail '
                                                                      'rule intent while applying '
                                                                      'the selected table '
                                                                      'governance policy.',
                                                  'when_to_use': 'Use in 02_pipeline after '
                                                                 'selecting a guardrail target to '
                                                                 'save active self-approved rules, '
                                                                 'submit proposed rules, or bypass '
                                                                 'approval with a required reason.',
                                                  'do_not_use_when': 'Do not use to write '
                                                                     'catalogue evidence or '
                                                                     'runtime outcomes; it writes '
                                                                     'rule intent only to '
                                                                     'METADATA_GUARDRAIL_RULES '
                                                                     'when saving.',
                                                  'glossary_terms': ['guardrail',
                                                                     'profile behavior',
                                                                     'metadata lakehouse',
                                                                     'notebook template'],
                                                  'return_interpretation': 'The widget state '
                                                                           'exposes controls, '
                                                                           'preview records, and '
                                                                           'save actions that '
                                                                           'produce append-only '
                                                                           'guardrail rule rows '
                                                                           'under the table '
                                                                           'policy.',
                                                  'common_failure_causes': ['The handover state is '
                                                                            'missing columns.',
                                                                            'Changing-data profile '
                                                                            'behavior has no '
                                                                            'watermark column.',
                                                                            'Freshness max lag is '
                                                                            'invalid.',
                                                                            'The metadata target '
                                                                            'cannot be written.']},
 'widget_author_dq_rules': {'expanded_purpose': 'Renders manual DQ authoring '
                                                'controls that produce editable guardrail rule '
                                                'intent rows under the selected table governance '
                                                'policy.',
                            'when_to_use': 'Use in 02_pipeline after target selection when '
                                           'engineering needs to batch-create, edit, clear, or '
                                           'draft DQ guardrail rules.',
                            'do_not_use_when': 'Do not use for runtime DQ enforcement or catalogue '
                                               'profiling; use enforce_dq_rules for execution and '
                                               'profile helpers for observed evidence.',
                            'glossary_terms': ['guardrail',
                                               'catalogue evidence',
                                               'metadata lakehouse',
                                               'notebook template'],
                            'return_interpretation': 'The widget returns mutable preview records '
                                                     'and draft suggestions; approved saves '
                                                     'write guardrail rule intent to '
                                                     'METADATA_GUARDRAIL_RULES.',
                            'common_failure_causes': ['Rule parameters are invalid for the '
                                                      'selected DQ type.',
                                                      'Rule suggestions cannot be parsed.',
                                                      'Bypass reason is missing when bypass is '
                                                      'requested.',
                                                      'The metadata target cannot be written.']},
 'widget_author_guardrail_rules': {'expanded_purpose': 'Renders the guardrail authoring widgets together so creation remains separate from formal review.',
                                  'when_to_use': 'Use in 03_governance after target selection to author guardrail records.',
                                  'do_not_use_when': 'Do not use for formal review decisions; use widget_review_table_governance.',
                                  'glossary_terms': ['guardrail', 'metadata lakehouse', 'notebook template'],
                                  'return_interpretation': 'Returns combined child widget states for guardrail authoring.',
                                  'common_failure_causes': ['No target state is selected.', 'Rule parameters are invalid.']},
 'widget_review_table_governance': {'expanded_purpose': 'Renders 03-only formal review controls for enrichment and guardrail records.',
                                    'when_to_use': 'Use only in 03_governance to approve, reject, replace, deactivate, or view history.',
                                    'do_not_use_when': 'Do not use from 02_pipeline or to write runtime enforcement results.',
                                    'glossary_terms': ['guardrail', 'metadata lakehouse', 'notebook template'],
                                    'return_interpretation': 'Returns controls and helpers that append review outcomes to review history tables.',
                                    'common_failure_causes': ['The notebook context is not 03_governance.', 'No reviewable records are available.']},
 'widget_review_guardrail_governance': {'expanded_purpose': 'Renders governance review controls '
                                                            'for reviewing '
                                                            'proposed or bypass-active enrichment and guardrail '
                                                            'rules, and applying approve, reject, '
                                                            'or supersede actions.',
                                        'when_to_use': 'Use in 03_governance after selecting a '
                                                       'guardrail target to perform human review '
                                                       'of enrichment and guardrail rule intent.',
                                        'do_not_use_when': 'Do not use for automatic pipeline '
                                                           'enforcement or profile evidence '
                                                           'generation; it is an interactive '
                                                           'governance review widget.',
                                        'glossary_terms': ['guardrail',
                                                           'metadata lakehouse',
                                                           'notebook template'],
                                        'return_interpretation': 'The widget returns controls, '
                                                                 'current rule history, and action '
                                                                 'helpers that write to guardrail '
                                                                 'rules or guardrail rule '
                                                                 'tables when invoked.',
                                        'common_failure_causes': ['No target state is selected.',
                                                                  'No proposed or bypassed rules '
                                                                  'are available for review.',
                                                                  'Unsupported governance action '
                                                                  'is selected.',
                                                                  'The metadata target cannot be '
                                                                  'written.']},
 'widget_select_agreement': {'expanded_purpose': 'Displays an agreement selector and stores the '
                                                 'chosen agreement so pipeline and exploration '
                                                 'notebooks can bind work to approved business '
                                                 'context.',
                             'when_to_use': 'Use near the start of 02_pipeline or 99_explore '
                                            'before reads, profiling, lineage, or governance '
                                            'evidence need an agreement id.',
                             'glossary_terms': ['notebook template'],
                             'return_interpretation': 'A visible selection widget does not mean an '
                                                      'agreement is selected; call '
                                                      'get_selected_agreement after the user '
                                                      'chooses a row.',
                             'common_failure_causes': ['No agreement metadata rows are available.',
                                                       'The user has not selected an agreement.',
                                                       'Notebook registration metadata cannot be '
                                                       'written.',
                                                       'The configured metadata lakehouse cannot '
                                                       'be read.']},
 'get_selected_agreement': {'expanded_purpose': 'Returns the agreement chosen by '
                                                'widget_select_agreement so downstream cells can '
                                                'pass consistent agreement identifiers to pipeline '
                                                'helpers.',
                            'when_to_use': 'Use after rendering and completing '
                                           'widget_select_agreement when code needs the selected '
                                           'agreement values.',
                            'glossary_terms': ['notebook template'],
                            'return_interpretation': 'A returned dictionary contains the selected '
                                                     'agreement fields. A missing value means the '
                                                     'selector has not been completed in the '
                                                     'current notebook state.',
                            'common_failure_causes': ['widget_select_agreement has not been run.',
                                                      'The user has not selected an agreement.',
                                                      'Notebook state was reset.',
                                                      'The selected row is no longer present in '
                                                      'metadata.']}}

RELATED_GUIDES_BY_SYMBOL = {'setup_notebook': [{'title': 'Notebook Templates',
                     'path': '../../how-fabricops-works/notebook-templates.md'},
                    {'title': 'Metadata Tables',
                     'path': '../../how-fabricops-works/metadata-tables.md'}],
 'setup_metadata_tables': [{'title': 'Notebook Templates',
                            'path': '../../how-fabricops-works/notebook-templates.md'},
                           {'title': 'Metadata Tables',
                            'path': '../../how-fabricops-works/metadata-tables.md'}],
 'widget_render_data_steward': [{'title': 'Notebook Templates',
                                 'path': '../../how-fabricops-works/notebook-templates.md'}],
 'widget_render_data_agreement': [{'title': 'Notebook Templates',
                                   'path': '../../how-fabricops-works/notebook-templates.md'}],
 'widget_render_agreement_evidence': [{'title': 'Notebook Templates',
                                       'path': '../../how-fabricops-works/notebook-templates.md'},
                                      {'title': 'Metadata Tables',
                                       'path': '../../how-fabricops-works/metadata-tables.md'}],
 'read_data': [{'title': 'Notebook Templates',
                           'path': '../../how-fabricops-works/notebook-templates.md'}],
 'write_data': [{'title': 'Notebook Templates',
                            'path': '../../how-fabricops-works/notebook-templates.md'},
                           {'title': 'Metadata Tables',
                            'path': '../../how-fabricops-works/metadata-tables.md'}],
 'read_lakehouse_csv': [{'title': 'Notebook Templates',
                         'path': '../../how-fabricops-works/notebook-templates.md'}],
 'read_lakehouse_parquet': [{'title': 'Notebook Templates',
                             'path': '../../how-fabricops-works/notebook-templates.md'}],
 'read_lakehouse_excel': [{'title': 'Notebook Templates',
                           'path': '../../how-fabricops-works/notebook-templates.md'}],
 'read_warehouse_table': [{'title': 'Notebook Templates',
                           'path': '../../how-fabricops-works/notebook-templates.md'}],
 'write_warehouse_table': [{'title': 'Notebook Templates',
                            'path': '../../how-fabricops-works/notebook-templates.md'}],
 'profile_dataframe': [{'title': 'Pipeline Guardrails',
                        'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                       {'title': 'Governance Review',
                        'path': '../../how-fabricops-works/governance-review.md'}],
 'enforce_freshness': [{'title': 'Pipeline Guardrails',
                        'path': '../../how-fabricops-works/pipeline-guardrails.md'}],
 'enforce_profile_behavior': [{'title': 'Pipeline Guardrails',
                               'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                              {'title': 'Governance Review',
                               'path': '../../how-fabricops-works/governance-review.md'}],
 'stop_if_failed': [{'title': 'Pipeline Guardrails',
                     'path': '../../how-fabricops-works/pipeline-guardrails.md'}],
 'enforce_dq_rules': [{'title': 'Pipeline Guardrails',
                       'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                      {'title': 'Governance Review',
                       'path': '../../how-fabricops-works/governance-review.md'}],
 'prepare_pipeline_table_configs': [{'title': 'Notebook Templates',
                                     'path': '../../how-fabricops-works/notebook-templates.md'},
                                    {'title': 'Pipeline Guardrails',
                                     'path': '../../how-fabricops-works/pipeline-guardrails.md'}],
 'run_table_guardrails': [{'title': 'Pipeline Guardrails',
                           'path': '../../how-fabricops-works/pipeline-guardrails.md'}],
 'write_catalogue_evidence': [{'title': 'Pipeline Guardrails',
                               'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                              {'title': 'Metadata Tables',
                               'path': '../../how-fabricops-works/metadata-tables.md'}],
 'write_pipeline_lineage': [{'title': 'Notebook Templates',
                             'path': '../../how-fabricops-works/notebook-templates.md'},
                            {'title': 'Metadata Tables',
                             'path': '../../how-fabricops-works/metadata-tables.md'}],
 'write_pipeline_run_summary': [{'title': 'Pipeline Guardrails',
                                 'path': '../../how-fabricops-works/pipeline-guardrails.md'},
                                {'title': 'Metadata Tables',
                                 'path': '../../how-fabricops-works/metadata-tables.md'}],
 'widget_select_agreement': [{'title': 'Notebook Templates',
                              'path': '../../how-fabricops-works/notebook-templates.md'}],
 'get_selected_agreement': [{'title': 'Notebook Templates',
                             'path': '../../how-fabricops-works/notebook-templates.md'}]}



def _metadata_row(symbol_name: str) -> PublicSymbolDocMetadata:
    """Return metadata for a public symbol."""
    for row in PUBLIC_SYMBOL_DOCS:
        if row["symbol_name"] == symbol_name:
            return row
    raise KeyError(symbol_name)


def related_guides(symbol_name: str) -> list[dict[str, str]]:
    """Return related guides for a public symbol."""
    return RELATED_GUIDES_BY_SYMBOL.get(symbol_name, [])
