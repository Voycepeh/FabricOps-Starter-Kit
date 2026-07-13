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
    usage_family: NotRequired[str]
    usage_notes: NotRequired[str]
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


IO_USAGE_NOTE = """These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic."""

WIDGET_USAGE_NOTE = """Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly."""

SETUP_NOTEBOOK_USAGE_NOTE = """Use this in the setup notebook to capture and render the key runtime information required by downstream Starter Kit notebooks.

This helps confirm the active environment, configured stores, notebook context, and runtime values before later notebooks depend on them."""

SETUP_METADATA_USAGE_NOTE = """Use this during setup to create the required metadata tables in the configured metadata lakehouse using predefined Starter Kit schemas.

This prepares the metadata store so downstream notebooks, widgets, lineage logging, evidence capture, and governance steps can write to the expected tables."""

CONFIG_USAGE_NOTE = """Use config helpers when notebook setup or downstream helpers need consistent runtime configuration, configured stores, paths, or audit context.

This keeps Starter Kit notebooks aligned on the same environment and config contract instead of each notebook calculating those values differently."""

PIPELINE_USAGE_NOTE = """Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries."""

CONFIG_PREPARATION_USAGE_NOTE = """Use this to normalize source or target table configurations before guardrails, writes, lineage, and evidence helpers use them.

This is intended for the standard pipeline table-config pattern, not for ad hoc reads or writes."""

USAGE_NOTE_BY_PATH_PREFIX = {
    "fabricops_kit/io/": IO_USAGE_NOTE,
    "fabricops_kit/widgets/": WIDGET_USAGE_NOTE,
    "fabricops_kit/setup/": SETUP_NOTEBOOK_USAGE_NOTE,
    "fabricops_kit/pipeline/": PIPELINE_USAGE_NOTE,
    "fabricops_kit/lineage/": PIPELINE_USAGE_NOTE,
    "fabricops_kit/evidence/": PIPELINE_USAGE_NOTE,
    "fabricops_kit/guardrails/": PIPELINE_USAGE_NOTE,
    "fabricops_kit/dq/": PIPELINE_USAGE_NOTE,
    "fabricops_kit/config/": CONFIG_USAGE_NOTE,
}

METADATA_REFERENCE_OVERVIEW_INTRO = (
    "FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. "
    "These pages are generated from the implemented metadata setup schema registry used by `00_env_config`."
)

METADATA_REFERENCE_MODEL_DIAGRAM = "![FabricOps metadata model](../assets/fabricops-metadata-model.png)"

METADATA_REFERENCE_MODEL_DIAGRAM_CAPTION = (
    "The diagram below shows how the FabricOps metadata tables relate to one another across agreement, "
    "profiling, guardrail, lineage, and pipeline-run evidence."
)

USAGE_NOTE_BY_FUNCTION = {
    "setup_notebook": SETUP_NOTEBOOK_USAGE_NOTE,
    "setup_metadata_tables": SETUP_METADATA_USAGE_NOTE,
    "prepare_pipeline_table_configs": CONFIG_PREPARATION_USAGE_NOTE,
}


MODULE_DOCS_METADATA = [{'module_name': 'config',
  'visibility': 'public',
  'module_summary': 'Owns environment setup, runtime initialization, paths, and notebook-wide '
                    'configuration.',
  'sidebar_group': '0. Environment setup',
  'sidebar_include': True},
 {'module_name': 'widgets.shared',
  'visibility': 'public',
  'module_summary': 'Owns widget implementation details for agreement workflows.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_render_data_steward',
  'visibility': 'public',
  'module_summary': 'Owns widget implementation details for agreement workflows.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_render_data_agreement',
  'visibility': 'public',
  'module_summary': 'Owns widget implementation details for agreement workflows.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_render_agreement_evidence',
  'visibility': 'public',
  'module_summary': 'Owns widget implementation details for agreement workflows.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_pipeline_bootstrap',
  'visibility': 'public',
  'module_summary': 'Owns the pipeline bootstrap widget and active runtime context setup.',
  'sidebar_group': '3. Data engineer',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_select_guardrail_target',
  'visibility': 'public',
  'module_summary': 'Owns the guardrail target selection widget workflow.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_author_schema_freshness_profile_rules',
  'visibility': 'public',
  'module_summary': 'Owns schema, freshness, and profile behavior rule authoring widget workflow.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_author_dq_rules',
  'visibility': 'public',
  'module_summary': 'Owns DQ rule authoring widget workflow.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_enrich_table_metadata',
  'visibility': 'public',
  'module_summary': 'Owns table metadata enrichment widget workflow.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'widgets.widget_review_guardrail_governance',
  'visibility': 'public',
  'module_summary': 'Owns guardrail governance review widget workflow.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'io',
  'visibility': 'public',
  'module_summary': 'Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.',
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
  'module_summary': 'Owns thin 02_pipeline helpers for profiles, lineage relationships, '
                    'guardrail results, and run summaries.',
  'sidebar_group': '3. Data engineer',
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

# Template-flow metadata is reserved for reusable notebooks that live under
# templates/notebooks and participate in TEMPLATE_FLOW_DOCS validation. Guided
# demo downloadable assets, such as
# docs/assets/demo-data/io-profile/guided_demo_io_and_profiling.ipynb, are
# intentionally excluded from this registry.
TEMPLATE_FLOW_DOCS = [{'notebook_key': '00_env_config',
  'notebook_label': '`00_env_config`',
  'segment_intro': 'Shared environment bootstrap and metadata table setup.',
  'segments': [{'symbols': ['FabricStore', 'PathConfig', 'GovernanceConfig', 'DataAgreementConfig', 'FrameworkConfig', 'setup_notebook', 'setup_metadata_tables'],
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
  'segments': [{'symbols': ['widget_pipeline_bootstrap',
                            'read_warehouse_table',
                            'read_warehouse_query',
                            'read_lakehouse_table',
                            'prepare_pipeline_table_configs',
                            'profile_dataframe',
                            'run_table_guardrails',
                            'write_lakehouse_table',
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
                            'widget_author_schema_freshness_profile_rules',
                            'widget_author_dq_rules',
                            'widget_enrich_table_metadata',
                            'widget_review_guardrail_governance'],
                'title': 'Guardrail governance review'}],
  'template_path': 'templates/notebooks/03_governance.ipynb'},
 {'notebook_key': '99_explore',
  'notebook_label': '`99_explore`',
  'segment_intro': 'Optional discovery, profiling, troubleshooting, investigation, and ad hoc '
                   'analysis support.',
  'segments': [{'symbols': ['read_lakehouse_csv',
                            'read_lakehouse_excel',
                            'read_lakehouse_parquet',
                            'read_lakehouse_table',
                            'read_warehouse_query',
                            'read_warehouse_table',
                            'write_lakehouse_table',
                            'write_warehouse_table',
                            'profile_dataframe',
                            'widget_browse_metadata_catalogue',
                            'widget_pipeline_bootstrap'],
                'title': 'Exploration'}],
  'template_path': 'templates/notebooks/99_explore.ipynb'},
 {'notebook_key': 'example_pipeline_demo',
  'notebook_label': '`example_pipeline_demo`',
  'segment_intro': 'Demo data seeding for the real pipeline template.',
  'segments': [{'symbols': ['write_lakehouse_table'],
                'title': 'Pipeline demo setup'}],
  'template_path': 'templates/notebooks/example_pipeline_demo.ipynb'},
 {'notebook_key': 'example_dq_rule_smoke_test',
  'notebook_label': '`example_dq_rule_smoke_test`',
  'segment_intro': 'Isolated DQ rule smoke-test checks for notebook authors.',
  'segments': [{'symbols': ['write_lakehouse_table', 'run_table_guardrails'],
                'title': 'DQ smoke checks'}],
  'template_path': 'templates/notebooks/example_dq_rule_smoke_test.ipynb'}]

PUBLIC_SYMBOL_DOCS = [
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Configured Fabric lakehouse or warehouse connection details.',
  'purpose': 'Describe one configured Fabric store used by path routing.',
  'symbol_name': 'FabricStore',
  'use_when': 'Use in 00_env_config path mappings to define lakehouse or warehouse targets.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'env, workspace_id, item_id, name, kind, schema_enabled, and schema.',
  'returns': 'Validated FabricStore configuration object.',
  'raises': 'ValueError for missing identifiers, unsupported store kind, or invalid schema names.',
  'side_effects': 'None.',
  'fabric_context': 'Use public-safe workspace and item identifiers in templates; do not rely on a default lakehouse.',
  'ai_verification': 'Confirm metadata targets route through the configured metadata store.',
  'glossary_terms': ['metadata lakehouse'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Environment-to-target mapping used for lakehouse and warehouse routing.',
  'purpose': 'Group configured Fabric stores by environment and target name.',
  'symbol_name': 'PathConfig',
  'use_when': 'Use in 00_env_config to define source, unified, product, and metadata targets.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'paths mapping environments to target FabricStore objects.',
  'returns': 'Validated PathConfig object.',
  'raises': 'ValueError when paths is empty or not a mapping.',
  'side_effects': 'None.',
  'fabric_context': 'Metadata targets must be configured explicitly rather than inferred from the attached lakehouse.',
  'ai_verification': 'Check every required environment target exists before downstream helpers run.',
  'glossary_terms': ['metadata lakehouse'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Governance policy and widget option configuration.',
  'purpose': 'Define governance labels, PII options, and enrichment widget custom fields.',
  'symbol_name': 'GovernanceConfig',
  'use_when': 'Use in 00_env_config to customize governance review options.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'required_classification, sensitivity rules and labels, PII classifications, and enrichment widgets.',
  'returns': 'Validated GovernanceConfig object.',
  'raises': 'ValueError for blank custom widget field keys.',
  'side_effects': 'None.',
  'fabric_context': 'Controls notebook review options; it does not read or write Fabric metadata by itself.',
  'ai_verification': 'Confirm custom fields use stable public-safe keys.',
  'glossary_terms': ['governance review'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Agreement table and widget configuration.',
  'purpose': 'Define agreement metadata table names and steward/agreement widget fields.',
  'symbol_name': 'DataAgreementConfig',
  'use_when': 'Use in 00_env_config to customize 01_agreement metadata and widget behavior.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'metadata_tables, data_steward_widget, data_agreement_widget, and steward_role_options.',
  'returns': 'Validated DataAgreementConfig object.',
  'raises': 'ValueError for blank custom widget field keys.',
  'side_effects': 'None.',
  'fabric_context': 'Agreement rows are written later through configured metadata routing.',
  'ai_verification': 'Confirm table names remain aligned with metadata setup.',
  'glossary_terms': ['data agreement', 'data steward'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Top-level FabricOps framework configuration.',
  'purpose': 'Combine path, governance, data agreement, and audit timezone settings for notebooks.',
  'symbol_name': 'FrameworkConfig',
  'use_when': 'Use in 00_env_config as the single CONFIG object passed to notebook helpers.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'path_config, governance_config, data_agreement_config, and audit_timezone.',
  'returns': 'Validated FrameworkConfig object.',
  'raises': 'ValueError for invalid audit timezone.',
  'side_effects': 'None.',
  'fabric_context': 'Carries configured targets used by metadata and data IO helpers.',
  'ai_verification': 'Confirm audit timezone is an IANA timezone and metadata routing is explicit.',
  'glossary_terms': ['metadata lakehouse'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'One configuration readiness check result.',
  'purpose': 'Represent pass, warning, failure, or skipped readiness check output.',
  'symbol_name': 'ConfigSmokeCheckResult',
  'use_when': 'Inspect setup_notebook validation_results for notebook readiness details.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'name, status, and message.',
  'returns': 'ConfigSmokeCheckResult value object.',
  'raises': 'None.',
  'side_effects': 'None.',
  'fabric_context': 'Created during notebook setup readiness checks.',
  'ai_verification': 'Review non-pass statuses before generating downstream workflow code.',
  'glossary_terms': ['notebook template'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Runtime setup context returned by setup_notebook.',
  'purpose': 'Carry resolved paths, runtime metadata, smoke checks, and readiness status.',
  'symbol_name': 'NotebookSetupContext',
  'use_when': 'Use after setup_notebook to inspect validated runtime context.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'run_id, notebook_name, workspace_name, user_name, environment, paths, validation_results, runtime_metadata, and readiness_status.',
  'returns': 'NotebookSetupContext value object.',
  'raises': 'None.',
  'side_effects': 'None.',
  'fabric_context': 'Includes runtime metadata returned by Fabric when available.',
  'ai_verification': 'Confirm readiness_status before running downstream setup or pipeline code.',
  'glossary_terms': ['notebook template'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},
 {'kind': 'function',
  'module': 'config.get_fabric_context',
  'function_type': 'callable',
  'summary_override': 'Build a Fabric context from explicit values or the active default.',
  'purpose': 'Create a context dictionary for helper context overrides.',
  'symbol_name': 'get_fabric_context',
  'use_when': 'Use when a helper needs an explicit config and env context outside the active notebook default.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'Optional env, config, workspace and lakehouse identifiers, names, and extra values.',
  'returns': 'Fabric context dictionary containing config and env.',
  'raises': 'RuntimeError when config or env cannot be resolved.',
  'side_effects': 'Reads active notebook or builtins context when explicit values are incomplete.',
  'fabric_context': 'Keeps env as the primary environment key for downstream routing.',
  'ai_verification': 'Confirm returned context contains config and env before passing it to IO helpers.',
  'glossary_terms': ['notebook template'],
  'expanded_purpose': 'Supports the public root import contract for FabricOps notebook configuration.',
  'common_failure_causes': ['Required configuration values are missing or invalid.'],
  'return_interpretation': 'Use the returned value as part of the supported FabricOps configuration surface.'},{'kind': 'function',
  'module': 'config.setup_notebook',
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
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
 {'kind': 'function',
  'module': 'config.setup_metadata_tables',
  'function_type': 'callable',
  'summary_override': 'Create or validate all FabricOps metadata tables through one setup action.',
  'symbol_name': 'setup_metadata_tables',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap',
  'use_when': 'Use after setup_notebook in 00_env_config to create or validate the FabricOps '
              'metadata tables required by agreement, profiling, lineage, stability, and '
              'governance workflows.',
  'do_not_use_when': 'Do not use for writing business data or pipeline target tables; use '
                     'write_lakehouse_table or write_warehouse_table for data outputs.',
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
  'glossary_terms': ['metadata lakehouse', 'evidence'],
  'return_interpretation': 'The returned setup status tells you which metadata tables were created '
                           'or validated and whether the environment is ready for workflows that '
                           'write evidence.',
  'common_failure_causes': ['The configured metadata lakehouse ABFSS path is missing or invalid.',
                            'Spark cannot create or inspect metadata tables through the configured '
                            'ABFSS paths.',
                            'The selected environment does not include metadata routing.',
                            'The caller lacks permission to create or update metadata tables.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
 {'kind': 'function',
  'module': 'widgets.widget_render_data_steward',
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
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'widgets.widget_render_data_agreement',
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
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'widgets.widget_render_agreement_evidence',
  'function_type': 'callable',
  'summary_override': 'Render the standalone agreement-evidence widget.',
  'symbol_name': 'widget_render_agreement_evidence',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake',
  'expanded_purpose': 'Renders the supporting-evidence widget for agreement workflows so users can '
                      'record links or files that justify an agreement.',
  'when_to_use': 'Use in 01_agreement when agreement records need supporting evidence that '
                 'downstream users can audit.',
  'glossary_terms': ['notebook template', 'evidence'],
  'return_interpretation': 'The widget records evidence references when saved; review the '
                           'resulting metadata rows before relying on them in handover or audit '
                           'flows.',
  'common_failure_causes': ['Evidence details are incomplete.',
                            'File or URL references are malformed.',
                            'Widget state is reset before saving.',
                            'The configured metadata target is not writable.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
 {'kind': 'function',
  'module': 'widgets.shared',
  'function_type': 'callable',
  'summary_override': 'Return the agreement selected by widget_pipeline_bootstrap.',
  'symbol_name': 'get_selected_agreement',
  'template_notebook': '02_pipeline',
  'template_segment': 'Agreement selection',
  'use_when': 'Use after widget_pipeline_bootstrap(select_agreement=True) to retrieve the selected agreement '
              'record for pipeline logic and evidence binding.',
  'do_not_use_when': 'Do not use before running widget_pipeline_bootstrap(select_agreement=True), or as a '
                     'substitute for querying all agreement metadata.',
  'parameters': 'No required parameters; reads the current in-memory widget selection state.',
  'returns': 'Selected agreement dictionary for the active notebook session.',
  'raises': 'Raises an error when no agreement has been selected in the current session.',
  'side_effects': 'Reads session/widget state only; it does not write metadata, tables, or files.',
  'fabric_context': 'Depends on a prior widget_pipeline_bootstrap(select_agreement=True) call in the same notebook session '
                    'and agreement metadata loaded via 00_env_config routing.',
  'ai_verification': 'Verify the returned agreement has the expected dataset/table identifiers '
                     'before using it to drive reads, writes, or governance evidence.',
  'preferred_example': 'agreement = get_selected_agreement()\n'
                       'dataset_name = agreement["dataset_name"]',
  'related_functions': ['widget_pipeline_bootstrap'],
  'expanded_purpose': 'Returns the agreement chosen by widget_pipeline_bootstrap so downstream cells '
                      'can pass consistent agreement identifiers to pipeline helpers.',
  'when_to_use': 'Use after rendering and completing widget_pipeline_bootstrap when code needs the '
                 'selected agreement values.',
  'glossary_terms': ['notebook template'],
  'return_interpretation': 'A returned dictionary contains the selected agreement fields. A '
                           'missing value means the selector has not been completed in the current '
                           'notebook state.',
  'common_failure_causes': ['widget_pipeline_bootstrap(select_agreement=True) has not been run.',
                            'The user has not selected an agreement.',
                            'Notebook state was reset.',
                            'The selected row is no longer present in metadata.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a Delta table from a configured Fabric lakehouse target.',
  'symbol_name': 'read_lakehouse_table',
  'template_notebook': '02_pipeline / 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading managed Delta tables from configured Lakehouse Tables storage.',
  'do_not_use_when': 'Do not use for lakehouse Files paths or warehouse SQL serving-engine reads.',
  'parameters': 'table_name, target, optional schema, optional spark_session, optional context, and Spark Delta reader options.',
  'returns': 'Spark DataFrame loaded from the configured Lakehouse Delta table path.',
  'raises': 'Raises ValueError for unsafe names or non-lakehouse targets and RuntimeError when Spark is unavailable.',
  'side_effects': 'Reads data only; it does not write metadata, files, or tables.',
  'fabric_context': 'Routes reads through configured FabricOps Lakehouse targets instead of an attached/default lakehouse.',
  'ai_verification': 'Verify the target, schema, and table are intended Lakehouse inputs before generating calls.',
  'preferred_example': 'df_orders = read_lakehouse_table("orders", target="source", schema=SOURCE_SCHEMA, spark_session=spark)',
  'related_functions': ['write_lakehouse_table', 'read_lakehouse_csv', 'read_warehouse_query'],
  'expanded_purpose': 'Resolves the configured Lakehouse Tables path, then delegates to Spark Delta reader with any supplied reader options.',
  'when_to_use': 'Use near the start of a notebook when Spark processing needs a full Lakehouse table DataFrame.',
  'glossary_terms': ['source data', 'metadata lakehouse'],
  'return_interpretation': 'The returned DataFrame represents the resolved Lakehouse table.',
  'common_failure_causes': ['The target or table name is misspelled.', 'The selected environment does not define the requested lakehouse target.', 'Spark cannot access the table.', 'The caller lacks permission to read the lakehouse.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Write a Spark DataFrame to a configured Fabric lakehouse Delta table.',
  'symbol_name': 'write_lakehouse_table',
  'template_notebook': '02_pipeline / examples',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when publishing Spark DataFrames to configured Lakehouse Tables storage.',
  'do_not_use_when': 'Do not use for warehouse publishing or metadata mutation outside configured metadata routing.',
  'parameters': 'df, table_name, target, optional schema, mode, partitioning/repartitioning options, writer options, verbose, and context.',
  'returns': 'None; the DataFrame is written to the configured Lakehouse Delta table path.',
  'raises': 'Raises ValueError for unsafe names, invalid write modes, or non-lakehouse targets.',
  'side_effects': 'Writes data to the configured Lakehouse Delta table path.',
  'fabric_context': 'Routes writes through configured FabricOps Lakehouse targets instead of an attached/default lakehouse.',
  'ai_verification': 'Verify guardrails passed, target/schema/table routing is intentional, and write mode is safe before generating calls.',
  'preferred_example': 'write_lakehouse_table(df_orders, "orders_clean", target="unified", schema=UNIFIED_SCHEMA, mode="overwrite")',
  'related_functions': ['read_lakehouse_table', 'write_warehouse_table', 'run_table_guardrails'],
  'expanded_purpose': 'Resolves the configured Lakehouse Tables path, then delegates to Spark Delta writer with any supplied writer options.',
  'when_to_use': 'Use after transformations and guardrail checks when the destination is a Lakehouse table.',
  'glossary_terms': ['target table', 'guardrails', 'metadata lakehouse'],
  'return_interpretation': 'No value is returned; successful completion means the configured Lakehouse write was submitted.',
  'common_failure_causes': ['Guardrails were skipped before a target write.', 'The target lakehouse is not configured for the environment.', 'The write mode is unsupported for the destination.', 'The caller lacks write permission or Spark cannot create the table.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a CSV file from a configured Fabric-resolved path through Spark CSV.',
  'symbol_name': 'read_lakehouse_csv',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a CSV file from a configured Fabric-resolved path.',
  'do_not_use_when': 'Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL '
                     'tables.',
  'parameters': 'relative_path, target, optional spark_session, optional context, header flag, and Spark CSV reader options.',
  'returns': 'Spark DataFrame loaded from the Fabric-resolved CSV path.',
  'raises': 'Raises ValueError for invalid file paths and configuration/Spark errors when the file '
            'cannot be read.',
  'side_effects': 'Reads from the configured Fabric-resolved path; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify relative_path is a configured Fabric-resolved file path, then check row count and schema '
                     'after reading.',
  'preferred_example': 'df = read_lakehouse_csv('
                       'relative_path="raw/orders/orders.csv", header=True, spark_session=spark)',
  'related_functions': ['read_lakehouse_table', 'read_lakehouse_parquet', 'read_lakehouse_excel'],
  'expanded_purpose': 'Resolves the configured Lakehouse Files path, then delegates to Spark CSV reader with supplied CSV options.',
  'when_to_use': 'Use for file-based source ingestion when the source is CSV and should be '
                 'resolved through configured Fabric targets.',
  'glossary_terms': ['source data', 'notebook template'],
  'return_interpretation': 'The returned DataFrame reflects Spark CSV parsing options; inspect '
                           'schema and sample rows before profiling or writing.',
  'common_failure_causes': ['The file path is wrong or outside the configured Fabric target.',
                            'CSV options do not match the file shape.',
                            'Spark cannot access the file.',
                            'The selected environment is missing the source lakehouse target.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a Parquet path from a configured Fabric-resolved path through Spark Parquet.',
  'symbol_name': 'read_lakehouse_parquet',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a Parquet file or path from a configured Fabric lakehouse Files '
              'path.',
  'do_not_use_when': 'Do not use for Delta tables, CSV files, Excel files, or warehouse SQL '
                     'tables.',
  'parameters': 'relative_path, target, verbose flag, optional spark_session, optional context, and Spark Parquet reader options.',
  'returns': 'Spark DataFrame loaded from the original Parquet path or timestamp-converted '
             'fallback path.',
  'raises': 'Raises ValueError for invalid relative paths and Spark/read errors when the Parquet '
            'path cannot be loaded.',
  'side_effects': 'Reads from the configured Fabric-resolved path and may create a local timestamp-converted fallback '
                  'for single-file Parquet precision issues; it does not write metadata tables.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify the file path is resolved by the Fabric resolver and check row '
                     'count/schema after reading.',
  'preferred_example': 'df = read_lakehouse_parquet('
                       'relative_path="raw/orders/orders.parquet", spark_session=spark)',
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_excel', 'read_lakehouse_table'],
  'expanded_purpose': 'Resolves the configured Lakehouse Files path, then delegates to Spark Parquet reader with supplied options and timestamp fallback reads.',
  'when_to_use': 'Use for file-based source ingestion when the source is Parquet rather than a '
                 'managed table.',
  'glossary_terms': ['source data', 'notebook template'],
  'return_interpretation': 'The returned DataFrame uses the Parquet schema read by Spark; validate '
                           'it before downstream profile or guardrail checks.',
  'common_failure_causes': ['The Parquet path is missing or misspelled.',
                            'The file is not valid Parquet.',
                            'The configured lakehouse target is unavailable.',
                            'The caller lacks read permission.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read an Excel file from a configured Fabric-resolved path through pandas.read_excel.',
  'symbol_name': 'read_lakehouse_excel',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading .xlsx files from a configured Fabric-resolved path, '
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
  'preferred_example': 'mapping_df = read_lakehouse_excel('
                       'relative_path="reference/faculty_mapping.xlsx", sheet_name=0, '
                       'spark_session=spark)',
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_parquet', 'read_lakehouse_table'],
  'expanded_purpose': 'Resolves the configured Lakehouse Files path, reads workbook binary, parses it with pandas.read_excel options, and converts the pandas DataFrame to Spark.',
  'when_to_use': 'Use when source data arrives as an Excel workbook and should still follow '
                 'configured Fabric lakehouse routing.',
  'glossary_terms': ['source data', 'notebook template'],
  'return_interpretation': 'The returned DataFrame depends on workbook sheet and parsing options; '
                           'confirm headers and types before using it as pipeline input.',
  'common_failure_causes': ['The workbook path or sheet name is incorrect.',
                            'Excel parsing dependencies are unavailable.',
                            'The workbook layout does not match expected headers.',
                            'The configured lakehouse target cannot be read.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a table from a configured Fabric warehouse target.',
  'symbol_name': 'read_warehouse_table',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a table from a configured Fabric warehouse target.',
  'do_not_use_when': 'Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or '
                     'Excel paths.',
  'parameters': 'schema, table_name, target, optional spark_session, optional context, and Fabric Warehouse connector reader options.',
  'returns': 'Spark DataFrame loaded from the configured warehouse table.',
  'raises': 'Raises configuration, Spark SQL, or warehouse-read errors when the target/table '
            'cannot be resolved/read.',
  'side_effects': 'Reads from a warehouse table; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify the warehouse target/schema/table are configured and inspect the '
                     'resulting DataFrame schema before downstream use.',
  'preferred_example': 'df = read_warehouse_table('
                       'schema="dbo", table="orders", spark_session=spark)',
  'related_functions': ['write_warehouse_table', 'read_warehouse_query'],
  'expanded_purpose': 'Resolves the configured Warehouse table target, then delegates full-table reads to the Fabric Warehouse Spark connector with supplied connector options.',
  'when_to_use': 'Use when source data lives in a Fabric Warehouse rather than a lakehouse file or '
                 'Delta table.',
  'glossary_terms': ['source data', 'notebook template'],
  'return_interpretation': 'The returned DataFrame represents the warehouse read result; confirm '
                           'filters and row counts before profiling or transformation.',
  'common_failure_causes': ['The warehouse target is not configured.',
                            'The table or SQL text is invalid.',
                            'Warehouse connector context is unavailable.',
                            'The caller lacks warehouse read permission.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.',
  'symbol_name': 'read_warehouse_query',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when projection or filtering should run in the Fabric Warehouse SQL serving engine before Spark receives rows.',
  'do_not_use_when': 'Do not use for lakehouse Delta tables, lakehouse Files paths, or non-SELECT warehouse mutations.',
  'parameters': 'query, target, optional spark_session, optional context, and Fabric Warehouse connector reader options.',
  'returns': 'Spark DataFrame returned by the Fabric warehouse connector.',
  'raises': 'Raises ValueError for blank or non-SELECT SQL and RuntimeError when the Fabric connector is unavailable.',
  'side_effects': 'Reads warehouse rows only; it does not execute mutations or write metadata.',
  'fabric_context': 'Routes through the configured warehouse target from 00_env_config.',
  'ai_verification': 'Prefer selecting only needed columns and rows in SQL, and verify query text is public-safe and read-only.',
  "preferred_example": "df = read_warehouse_query(\"SELECT order_id, status FROM dbo.orders WHERE status = 'OPEN'\", spark_session=spark)",
  'related_functions': ['read_warehouse_table', 'write_warehouse_table'],
  'expanded_purpose': 'Runs pass-through SELECT SQL through the Fabric Warehouse Spark connector using the configured warehouse artifact as the connector database.',
  'when_to_use': 'Use when warehouse data should be filtered or projected before Spark processing.',
  'glossary_terms': ['source data', 'notebook template'],
  'return_interpretation': 'The returned DataFrame contains the query result from the warehouse SQL serving engine.',
  'common_failure_causes': ['The SQL is blank or not a SELECT/CTE.', 'The warehouse target is not configured.', 'The Fabric connector is unavailable.', 'The caller lacks warehouse read permission.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Write a DataFrame to a configured Fabric warehouse target.',
  'symbol_name': 'write_warehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when publishing a Spark DataFrame to a configured Fabric warehouse table.',
  'do_not_use_when': 'Do not use for lakehouse table writes, lakehouse Files writes, or metadata '
                     'evidence writes.',
  'parameters': 'df, schema, table_name, target, write mode, optional Spark repartition_by value, optional connector writer options, and optional context.',
  'returns': 'None; the DataFrame is written to the configured warehouse table.',
  'raises': 'Raises configuration, Spark connector, or warehouse write errors when the '
            'target/table cannot be written.',
  'side_effects': 'Writes data to a Fabric warehouse table using the selected mode.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify guardrails passed, confirm schema/table routing from CONFIG, and '
                     'check the intended write mode before calling.',
  'preferred_example': 'write_warehouse_table(serving_df, '
                       'target="Warehouse", schema="dbo", table="orders_serving", mode="append")',
  'related_functions': ['read_warehouse_table', 'read_warehouse_query', 'stop_if_failed'],
  'expanded_purpose': 'Resolves the configured Warehouse table target, optionally applies Spark repartition_by handling to control write parallelism without creating a physically partitioned Warehouse table, then delegates writes to the Fabric Warehouse Spark connector with supplied writer options.',
  'when_to_use': 'Use for target writes after guardrails pass and the configured output layer is a '
                 'warehouse table.',
  'glossary_terms': ['target table', 'guardrails'],
  'return_interpretation': 'A successful write means the helper submitted the DataFrame write to '
                           'the configured warehouse target; verify downstream table state for '
                           'business checks.',
  'common_failure_causes': ['The warehouse target is missing from configuration.',
                            'The target table name or write mode is invalid.',
                            'Warehouse connector support is unavailable.',
                            'The caller lacks write permission.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Profile a Spark DataFrame for structural and statistical exploration.',
  'symbol_name': 'profile_dataframe',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Profiling',
  'use_when': 'Use to create schema, row-count, null, distinct, min/max, and numeric statistic profiles from a Spark DataFrame.',
  'do_not_use_when': 'Do not use as a data-quality enforcement step or as a persistence helper; it '
                     'builds profile rows but does not approve governance evidence.',
  'parameters': 'df, optional exclude_columns, and approximate_distinct.',
  'returns': 'Spark DataFrame containing one profile row per eligible business column.',
  'raises': 'Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.',
  'side_effects': 'Computes profiling aggregations on the provided DataFrame; it does not write '
                  'metadata, tables, or files.',
  'fabric_context': 'Use after reading source/target data and before metadata persistence or '
                    'governance review workflows that need profiles.',
  'ai_verification': 'Verify the profile row count matches expected business columns and inspect '
                     'key schema/profile fields before writing evidence.',
  'preferred_example': 'profile_rows_df = profile_dataframe(df, exclude_columns=["technical_column"])',
  'related_functions': ['enforce_profile_behavior', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Builds deterministic profiles for a DataFrame, including schema, '
                      'row counts, nulls, distinct counts, numeric statistics, and supported min/max values.',
  'when_to_use': 'Use during exploration, governance review, or guardrail preparation when a table '
                 'needs reproducible profiles.',
  'glossary_terms': ['evidence', 'source data', 'target table'],
  'return_interpretation': 'Each returned profile row describes one eligible source column. Downstream governance and guardrail helpers may use those rows as evidence.',
  'common_failure_causes': ['The DataFrame is empty or missing expected columns.',
                            'Requested statistics are unsupported for a column type.',
                            'Spark actions fail while computing counts or summaries.',
                            'Excluded columns remove fields needed for review.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'},
                     {'title': 'Governance Review',
                      'path': '../../guided-demo/review-guardrails.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Profile top-N value frequencies for selected Spark DataFrame columns.',
  'symbol_name': 'profile_frequency_distribution',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Profiling',
  'use_when': 'Use to inspect value frequencies on exactly the Spark DataFrame supplied by the caller.',
  'do_not_use_when': 'Do not use as a sampling helper, metadata writer, or data-quality enforcement step.',
  'parameters': 'df, optional columns, and top_n.',
  'returns': 'Spark DataFrame containing ranked top-N value frequencies per profiled column.',
  'raises': 'Raises ValueError when top_n is not positive or requested columns do not exist.',
  'side_effects': 'Computes frequency aggregations on the provided DataFrame; it does not write metadata, tables, or files.',
  'fabric_context': 'Use after the caller has intentionally selected the exact DataFrame rows to profile.',
  'ai_verification': 'Verify requested columns and top_n match the intended exploration scope.',
  'preferred_example': 'frequency_df = profile_frequency_distribution(df, columns=["status"], top_n=10)',
  'related_functions': ['profile_dataframe'],
  'expanded_purpose': 'Calculates deterministic top-N value frequencies with counts, percentages, ranks, and profiled row counts for selected scalar columns.',
  'when_to_use': 'Use during exploration or profiling when value distribution details are needed without writing metadata.',
  'glossary_terms': ['source data', 'distinct value'],
  'return_interpretation': 'Each returned row describes one retained value for one source column.',
  'common_failure_causes': ['Requested columns are missing.',
                            'top_n is not greater than zero.',
                            'Spark actions fail while computing frequency counts.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
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
                     'run_table_guardrails for those checks.',
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
  'glossary_terms': ['guardrails', 'can_continue', 'source data', 'target table'],
  'return_interpretation': 'If can_continue is true, the latest freshness value is within the '
                           'allowed lag or the check was skipped. If false, investigate stale data '
                           'before writing outputs.',
  'common_failure_causes': ['The freshness column is missing.',
                            'The max lag value is missing or invalid.',
                            'The latest date is older than the allowed lag.',
                            'Severity is invalid or configured as blocking for stale data.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Enforce static, changing, or skipped profile behavior against accepted '
                      'catalogue profiles.',
  'symbol_name': 'enforce_profile_behavior',
  'template_notebook': '02_pipeline',
  'template_segment': 'Profile behavior enforcement',
  'expanded_purpose': 'This function protects against silent data behavior changes. It compares '
                      'current static_data or changing_data profiles with previous '
                      'approved evidence. If the current profile no longer matches the '
                      'approved baseline, the function returns a failed guardrail result so the '
                      'pipeline can stop before writing data.',
  'use_when': 'Use in 02_pipeline to enforce profile_mode expectations against previous accepted '
              'catalogue profiles.',
  'when_to_use': 'Use this when promoting or running a pipeline that should follow a previously '
                 'approved profile behavior pattern. It is especially useful when full-table '
                 'static data changes unexpectedly or when a previous watermark group changes or '
                 'disappears.',
  'do_not_use_when': 'Do not use for simple schema validation or DQ-rule enforcement; use '
                     'run_table_guardrails for DQ-rule enforcement.',
  'glossary_terms': ['profile behavior',
                     'evidence',
                     'profile',
                     'stage',
                     'profile behavior',
                     'guardrails',
                     'can_continue',
                     'static_data',
                     'changing_data',
                     'skip',
                     'metadata lakehouse'],
  'parameters': {'spark': 'Spark session used to read accepted profiles from the '
                          'configured metadata target.',
                 'dataframe': 'Current source or target DataFrame being checked.',
                 'metadata_table': 'Metadata table that stores accepted catalogue profile '
                                   'evidence.',
                 'dataset_name': 'Dataset name used to find matching evidence.',
                 'table_name': 'Table name used to find matching evidence.',
                 'stage': 'The part of the pipeline being checked, such as source or target.',
                 'run_id': 'Current pipeline run identifier recorded in the generated profile '
                           'evidence.',
                 'profile_mode': 'Profile behavior mode to evaluate: static_data, changing_data, '
                                 'or skip.',
                 'watermark_column': 'Column used to group changing_data profiles when '
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
  'raises': 'Raises Spark or metadata-read errors when baseline profiles cannot be loaded '
            'or compared.',
  'common_failure_causes': ['No accepted profile exists yet.',
                            'The current profile behavior does not match the accepted baseline.',
                            'The configured dataset or table name does not match catalogue '
                            'evidence.',
                            'The configured stage does not match the accepted evidence.',
                            'The metadata lakehouse or catalogue profile table cannot be read.',
                            'The accepted evidence is missing required profile behavior fields.',
                            'The current profile_mode value is invalid or unsupported.',
                            'The accepted evidence is stale or incomplete.'],
  'side_effects': 'Reads baseline profile metadata and computes current profiles; it does '
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
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'},
                     {'title': 'Governance Review',
                      'path': '../../guided-demo/review-guardrails.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
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
                    'or enforce_profile_behavior and before write helpers.',
  'ai_verification': 'Verify the guardrail result shape includes status/can_continue/message '
                     'before passing it to stop_if_failed.',
  'preferred_example': 'guardrail_result = run_table_guardrails(table_configs, context={"config": CONFIG, "env": ENV}, run_id=RUN_ID, spark_session=spark)\n'
                       'stop_if_failed(guardrail_result)',
  'related_functions': ['enforce_freshness', 'enforce_profile_behavior', 'run_table_guardrails'],
  'expanded_purpose': 'Stops or raises for a blocking guardrail result so a notebook does not '
                      'continue into unsafe downstream writes.',
  'when_to_use': 'Use immediately after schema, freshness, profile behavior, or DQ guardrail '
                 'helpers when can_continue controls whether the pipeline should proceed.',
  'glossary_terms': ['guardrails', 'can_continue'],
  'return_interpretation': 'No return value means execution may continue. A blocking result raises '
                           'or exits according to runtime settings.',
  'common_failure_causes': ['The guardrail result is missing can_continue or status fields.',
                            'A blocking guardrail returned can_continue as false.',
                            'Notebook exit behavior is not supported in the current runtime.',
                            'The caller passed a warning result that should not stop execution.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
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
  'related_functions': ['run_table_guardrails', 'read_lakehouse_table'],
  'expanded_purpose': 'Normalizes source and target table configuration dictionaries so pipeline '
                      'guardrail, write, lineage, and evidence helpers receive consistent fields.',
  'when_to_use': 'Use before running table guardrails or writes when notebook-editable table '
                 'configs need package defaults and derived keys.',
  'glossary_terms': ['source data', 'target table', 'stage', 'guardrails'],
  'return_interpretation': 'The returned configs are enriched copies keyed for downstream helpers. '
                           'Confirm each table has the expected stage, key, and write settings.',
  'common_failure_causes': ['A table config is missing key or table_name fields.',
                            'Stage or write settings are inconsistent.',
                            'Source and target config shapes differ from expected dictionaries.',
                            'Defaults in CONFIG do not match the notebook environment.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'},
                     {'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
 {'kind': 'function',
  'module': 'widgets.widget_pipeline_bootstrap',
  'function_type': 'callable',
  'summary_override': 'Bootstrap a guided pipeline notebook run and store runtime defaults.',
  'symbol_name': 'widget_pipeline_bootstrap',
  'template_notebook': '02_pipeline',
  'template_segment': 'runtime context setup / pipeline bootstrap',
  'use_when': 'Use near the top of 02_pipeline to resolve run, agreement, notebook, and pipeline defaults without repeating runtime plumbing.',
  'do_not_use_when': 'Do not use when an advanced custom notebook needs to pass every runtime parameter explicitly to lower-level helpers.',
  'parameters': 'notebook_type, select_agreement, register_notebook, read_only, and optional runtime overrides.',
  'returns': 'Internal runtime context object with run_id, pipeline_name, notebook identity, agreement identity, and Spark context for downstream defaults. The concrete context class is internal and not a primary public API.',
  'side_effects': 'Stores active in-memory context for the current notebook session; renders agreement selection when select_agreement=True and registers only when register_notebook=True.',
  'fabric_context': 'Defaults to RUN_CONTEXT, spark, and METADATA_SCHEMA from 00_env_config.',
  'ai_verification': 'Verify delivery notebooks use register_notebook=True and read-only exploration notebooks use register_notebook=False with read_only=True.',
  'preferred_example': 'PIPELINE = widget_pipeline_bootstrap(notebook_type="02_pipeline", select_agreement=True, register_notebook=True)',
  'related_functions': ['run_table_guardrails', 'write_pipeline_run_summary'],
  'expanded_purpose': 'Resolves runtime and agreement context once so template notebooks can call guardrail and summary helpers with concise defaults.',
  'when_to_use': 'Use near the top of 02_pipeline or read-only exploration notebooks that need agreement-aware runtime defaults.',
  'glossary_terms': ['notebook template', 'data agreement', 'metadata lakehouse'],
  'return_interpretation': 'The returned context can be assigned to PIPELINE for target config and lineage fields while downstream helpers read the same active defaults automatically. The concrete context class is internal and not a primary public API.',
  'common_failure_causes': ['RUN_CONTEXT is unavailable.', 'spark is unavailable.', 'No agreement exists when select_agreement=True.', 'The user has not selected an agreement.'],
  'related_guides': [{'title': 'Templates', 'path': '../../notebook-templates-implementation-guide/index.md'}, {'title': 'Pipeline Execution', 'path': '../../guided-demo/run-pipeline.md'}]},
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
  'parameters': 'table_configs plus context, run_id, spark_session, and agreement/notebook '
                'context.',
  'returns': 'Guardrail result bundle with profiles, schema results, freshness results, stability '
             'results, DQ results, catalogue status, evidence definitions, summary, can_continue, '
             'and failed_tables.',
  'side_effects': 'Profiles DataFrames, reads stability/DQ metadata through configured metadata '
                  'routing, writes evidence, and may update table config DataFrames with '
                  'DQ annotations.',
  'fabric_context': 'Requires CONFIG and env from 00_env_config so metadata operations use the '
                    'configured metadata target.',
  'ai_verification': 'Verify stop_on_failure=True is used before transformation or writes when '
                     'blocking guardrails should stop execution.',
  'preferred_example': 'source_guardrail_results = run_table_guardrails(SOURCE_TABLES, '
                       'config=CONFIG, env=ENV, run_id=RUN_ID, spark_session=spark, '
                       'stop_on_failure=True)',
  'related_functions': ['prepare_pipeline_table_configs', 'write_catalogue_evidence'],
  'expanded_purpose': 'Coordinates profiling, schema, freshness, profile behavior, DQ, and '
                      'evidence checks for a group of pipeline table configs.',
  'when_to_use': 'Use in 02_pipeline before transformations or writes when table configs should be '
                 'validated by the standard guardrail sequence.',
  'glossary_terms': ['guardrails',
                     'can_continue',
                     'source data',
                     'target table',
                     'evidence'],
  'return_interpretation': 'The result groups each guardrail outcome and a summary DataFrame. If '
                           'any blocking result has can_continue false, stop before writing data.',
  'common_failure_causes': ['One of the table configs is incomplete.',
                            'A schema, freshness, profile behavior, or DQ check fails.',
                            'Approved metadata evidence cannot be read.',
                            'Spark cannot profile or validate one of the DataFrames.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Enrich profile rows with guardrail context and write evidence.',
  'symbol_name': 'write_catalogue_evidence',
  'template_notebook': '02_pipeline',
  'template_segment': 'Catalogue evidence',
  'use_when': 'Use after source or target profiles and guardrail results are available to persist '
              'evidence through the configured metadata route.',
  'parameters': 'profiles, dataset definitions, config, env, run_id, agreement context, notebook '
                'context, and optional guardrail results.',
  'returns': 'Dictionary of write statuses keyed by dataset alias.',
  'side_effects': 'Writes METADATA_DATA_CATALOGUE through the configured metadata lakehouse '
                  'target.',
  'related_functions': ['profile_dataframe', 'write_lakehouse_table'],
  'expanded_purpose': 'Writes runtime evidence rows generated by pipeline guardrails to '
                      'the configured metadata target.',
  'when_to_use': 'Use after guardrail evidence is built and before governance or handover '
                 'workflows need the latest runtime evidence.',
  'glossary_terms': ['evidence', 'metadata lakehouse', 'guardrails'],
  'return_interpretation': 'The returned status summarizes which evidence rows were prepared or '
                           'written. Confirm expected table keys appear before relying on '
                           'governance review outputs.',
  'common_failure_causes': ['Evidence definitions are missing required fields.',
                            'The metadata lakehouse cannot be written.',
                            'Spark cannot convert evidence rows to the target schema.',
                            'The caller lacks metadata write permission.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
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
  'glossary_terms': ['source data', 'target table', 'evidence', 'metadata lakehouse'],
  'return_interpretation': 'A successful result indicates lineage rows were prepared for metadata '
                           'persistence; review returned counts against expected transformation '
                           'steps.',
  'common_failure_causes': ['Lineage records are empty or malformed.',
                            'run_id, source, or target identifiers are missing.',
                            'The metadata table cannot be written.',
                            'Audit fields cannot be resolved from configuration.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates-implementation-guide/index.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
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
                        'write_lakehouse_table'],
  'expanded_purpose': 'Writes a compact run-level summary that ties pipeline name, agreement '
                      'context, guardrail results, lineage, and write outcomes together.',
  'when_to_use': 'Use at the end of 02_pipeline when downstream operators need one metadata record '
                 'describing the run outcome.',
  'glossary_terms': ['guardrails', 'can_continue', 'evidence', 'metadata lakehouse'],
  'return_interpretation': 'The returned summary shows what run metadata was assembled or written. '
                           'Compare status and guardrail counts with expected pipeline outcomes.',
  'common_failure_causes': ['Required run identifiers are missing.',
                            'Guardrail result structures are malformed.',
                            'Metadata routing is unavailable.',
                            'The configured summary table cannot be written.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
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
  'glossary_terms': ['guardrails', 'metadata lakehouse', 'can_continue'],
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
  'glossary_terms': ['guardrails', 'notebook template'],
  'return_interpretation': 'Summary and detailed modes return display-friendly rows or Spark '
                           'DataFrames; debug mode returns the raw nested guardrail summary or '
                           'bundle.',
  'common_failure_causes': ['Mode is not summary, detailed, or debug.',
                            'The Spark session cannot create a DataFrame from display rows.',
                            'The result bundle is malformed.',
                            'The caller expects debug internals while using summary mode.']},
 {'kind': 'function',
  'module': 'widgets.widget_enrich_table_metadata',
  'function_type': 'callable',
  'summary_override': 'Render a consolidated column enrichment widget.',
  'symbol_name': 'widget_enrich_table_metadata',
  'template_notebook': '03_governance',
  'template_segment': 'Guardrail governance review',
  'use_when': 'Use in 03_governance after widget_select_guardrail_target to enrich selected catalogue columns with descriptive business context, sensitivity, PII, and configured custom metadata.',
  'parameters': 'See the source docstring for the selected guardrail state, configuration, environment, and Spark session parameters.',
  'returns': 'Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.',
  'related_functions': ['widget_select_guardrail_target', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or catalogue profiles.',
  'when_to_use': 'Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.',
  'do_not_use_when': 'Do not use to author DQ rules or enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.',
  'glossary_terms': ['evidence', 'metadata lakehouse', 'guardrails'],
  'return_interpretation': 'The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT_RULES.',
  'common_failure_causes': ['The selected guardrail target has no column-level evidence.',
                            'Configured custom fields omit a field name.',
                            'Metadata lakehouse writes cannot be routed through 00_env_config.']},
 {'kind': 'function',
  'module': 'widgets.widget_select_guardrail_target',
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
  'expanded_purpose': 'Renders an interactive selector that reads catalogue profiles, '
                      'existing guardrail rules, and table governance policy to create the '
                      'handover state for guardrail authoring or review.',
  'when_to_use': 'Use at the start of 02_pipeline authoring or 03_governance review when a user '
                 'must choose which profiled table to work on.',
  'do_not_use_when': 'Do not use for automatic pipeline enforcement or to write metadata; this '
                     'selector reads metadata and prepares widget state only.',
  'glossary_terms': ['evidence', 'guardrails', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The returned state includes environment, dataset, table, metadata '
                           'keys, profile rows, existing rules, and governance policy values for '
                           'downstream widgets.',
  'common_failure_causes': ['METADATA_DATA_CATALOGUE has no profiles.',
                            'The selected table lacks metadata identity fields.',
                            'Metadata tables cannot be read.',
                            'ipywidgets is unavailable.']},
 {'kind': 'function',
  'module': 'widgets.widget_author_schema_freshness_profile_rules',
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
  'do_not_use_when': 'Do not use to write evidence or runtime outcomes; it writes rule '
                     'intent only to METADATA_GUARDRAIL_RULES when saving.',
  'glossary_terms': ['guardrails', 'profile behavior', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget state exposes controls, preview records, and save actions '
                           'that produce append-only guardrail rule rows under the table policy.',
  'common_failure_causes': ['The handover state is missing columns.',
                            'Changing-data profile behavior has no watermark column.',
                            'Freshness max lag is invalid.',
                            'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'widgets.widget_browse_metadata_catalogue',
  'function_type': 'callable',
  'summary_override': 'Render a searchable metadata catalogue browser.',
  'symbol_name': 'widget_browse_metadata_catalogue',
  'template_notebook': '99_explore',
  'template_segment': 'Browse metadata catalogue',
  'use_when': 'Use in exploration notebooks to browse observed catalogue evidence by logical FabricStore target and table.',
  'parameters': 'See the source docstring for agreement, metadata table, Spark session, and context parameters.',
  'returns': 'Mutable widget state whose dataframe key contains the currently filtered Spark DataFrame.',
  'related_functions': ['read_lakehouse_table', 'profile_dataframe'],
  'expanded_purpose': 'Reads METADATA_DATA_CATALOGUE from the configured metadata target, lets users choose a logical FabricStore target, and exposes catalogue rows for the selected table.',
  'when_to_use': 'Use in 99_explore when notebook authors need searchable, read-only catalogue evidence filtered by the active agreement context.',
  'do_not_use_when': 'Do not use for writing metadata, approving rules, or enforcing guardrails.',
  'glossary_terms': ['metadata catalogue', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The returned state updates as selectors change; read state["dataframe"] for the currently filtered Spark DataFrame.',
  'common_failure_causes': ['No FabricStore targets are configured.',
                            'The metadata catalogue table does not exist yet.',
                            'The selected FabricStore target has no catalogue rows.']},


 {'kind': 'function',
  'module': 'widgets.widget_author_dq_rules',
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
                     'run_table_guardrails for execution and profile helpers for observed evidence.',
  'glossary_terms': ['guardrails', 'evidence', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget returns mutable preview records; '
                           'approved saves write guardrail rule intent to '
                           'METADATA_GUARDRAIL_RULES.',
  'common_failure_causes': ['Rule parameters are invalid for the selected DQ type.',
                            'Rule suggestions cannot be parsed.',
                            'Bypass reason is missing when bypass is requested.',
                            'The metadata target cannot be written.']},


 {'kind': 'function',
  'module': 'widgets.widget_review_guardrail_governance',
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
  'do_not_use_when': 'Do not use for automatic pipeline enforcement or profiles '
                     'generation; it is an interactive governance review widget.',
  'glossary_terms': ['guardrails', 'metadata lakehouse', 'notebook template'],
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
                           'glossary_terms': ['metadata lakehouse', 'evidence'],
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
                                      'glossary_terms': ['notebook template', 'evidence'],
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
 'read_lakehouse_table': {'expanded_purpose': 'Reads a Delta table from the configured Fabric '
                                              'lakehouse target, resolving to '
                                              '{store.root}/Tables/{table} for classic targets or '
                                              '{store.root}/Tables/{schema}/{table} for '
                                              'schema-enabled targets.',
                          'when_to_use': 'Use when notebook code needs a managed lakehouse Delta '
                                         'table by ABFSS path rather than a file path, registered '
                                         'Spark table name, or warehouse SQL query.',
                          'glossary_terms': ['source data', 'metadata lakehouse'],
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
 'write_lakehouse_table': {'expanded_purpose': 'Writes a DataFrame to the configured Fabric '
                                               'lakehouse target, resolving to '
                                               '{store.root}/Tables/{table} for classic targets or '
                                               '{store.root}/Tables/{schema}/{table} for '
                                               'schema-enabled targets.',
                           'when_to_use': 'Use for lakehouse or metadata table writes after '
                                          'guardrails have passed when the destination should be '
                                          'saved by ABFSS Delta path, not saveAsTable or a Spark '
                                          'namespace.',
                           'glossary_terms': ['target table', 'guardrails', 'metadata lakehouse'],
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
                                       'and should be resolved through configured Fabric targets.',
                        'glossary_terms': ['source data', 'notebook template'],
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
                            'glossary_terms': ['source data', 'notebook template'],
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
                          'glossary_terms': ['source data', 'notebook template'],
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
                          'glossary_terms': ['source data', 'notebook template'],
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
                           'glossary_terms': ['target table', 'guardrails'],
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
 'profile_dataframe': {'expanded_purpose': 'Builds deterministic profiles for a DataFrame, '
                                           'including schema, row counts, nulls, distinct counts, '
                                           'numeric statistics, and supported min/max values.',
                       'when_to_use': 'Use during exploration, governance review, or guardrail '
                                      'preparation when a table needs reproducible profile '
                                      'evidence.',
                       'glossary_terms': ['evidence', 'source data', 'target table'],
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
 'profile_frequency_distribution': {'expanded_purpose': 'Calculates deterministic top-N value frequencies with counts, percentages, ranks, and profiled row counts for selected scalar columns.',
                                    'when_to_use': 'Use during exploration or profiling when value distribution details are needed without writing metadata.',
                                    'glossary_terms': ['source data', 'distinct value'],
                                    'return_interpretation': 'Each returned row describes one retained value for one source column.',
                                    'common_failure_causes': ['Requested columns are missing.',
                                                              'top_n is not greater than zero.',
                                                              'Spark actions fail while computing frequency counts.']},
 'enforce_freshness': {'expanded_purpose': 'Checks whether the latest value in a freshness column '
                                           'is recent enough for the configured maximum lag before '
                                           'pipeline writes continue.',
                       'when_to_use': 'Use as a pipeline guardrail when stale source or target '
                                      'data should block or warn before downstream work proceeds.',
                       'glossary_terms': ['guardrails',
                                          'can_continue',
                                          'source data',
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
                                                  'static_data or changing_data profiles '
                                                  'with previous approved evidence. If '
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
                                                 'evidence',
                                                 'profile',
                                                 'stage',
                                                 'profile behavior',
                                                 'guardrails',
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
                              'common_failure_causes': ['No accepted profile exists yet.',
                                                        'The current profile behavior does not '
                                                        'match the accepted baseline.',
                                                        'The configured dataset or table name does '
                                                        'not match evidence.',
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
                    'glossary_terms': ['guardrails', 'can_continue'],
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
 'prepare_pipeline_table_configs': {'expanded_purpose': 'Normalizes source and target table '
                                                        'configuration dictionaries so pipeline '
                                                        'guardrail, write, lineage, and evidence '
                                                        'helpers receive consistent fields.',
                                    'when_to_use': 'Use before running table guardrails or writes '
                                                   'when notebook-editable table configs need '
                                                   'package defaults and derived keys.',
                                    'glossary_terms': ['source data',
                                                       'target table',
                                                       'stage',
                                                       'guardrails'],
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
 'widget_pipeline_bootstrap': {'expanded_purpose': 'Resolves runtime and agreement context once so template notebooks can call guardrail and summary helpers with concise defaults.',
                        'when_to_use': 'Use near the top of 02_pipeline or read-only exploration notebooks that need agreement-aware runtime defaults.',
                        'glossary_terms': ['notebook template', 'data agreement', 'metadata lakehouse'],
                        'return_interpretation': 'The returned context can be assigned to PIPELINE for target config and lineage fields while downstream helpers read the same active defaults automatically. The concrete context class is internal and not a primary public API.',
                        'common_failure_causes': ['RUN_CONTEXT is unavailable.',
                                                  'spark is unavailable.',
                                                  'No agreement exists when select_agreement=True.',
                                                  'The user has not selected an agreement.']},
 'run_table_guardrails': {'expanded_purpose': 'Coordinates profiling, schema, freshness, profile '
                                              'behavior, DQ, and evidence checks for a '
                                              'group of pipeline table configs.',
                          'when_to_use': 'Use in 02_pipeline before transformations or writes when '
                                         'table configs should be validated by the standard '
                                         'guardrail sequence.',
                          'glossary_terms': ['guardrails',
                                             'can_continue',
                                             'source data',
                                             'target table',
                                             'evidence'],
                          'return_interpretation': 'The result groups each guardrail outcome and a '
                                                   'summary DataFrame. If any blocking result has '
                                                   'can_continue false, stop before writing data.',
                          'common_failure_causes': ['One of the table configs is incomplete.',
                                                    'A schema, freshness, profile behavior, or DQ '
                                                    'check fails.',
                                                    'Approved metadata evidence cannot be read.',
                                                    'Spark cannot profile or validate one of the '
                                                    'DataFrames.']},
 'write_catalogue_evidence': {'expanded_purpose': 'Writes runtime evidence rows '
                                                  'generated by pipeline guardrails to the '
                                                  'configured metadata target.',
                              'when_to_use': 'Use after guardrail evidence is built and before '
                                             'governance or handover workflows need the latest '
                                             'runtime evidence.',
                              'glossary_terms': ['evidence',
                                                 'metadata lakehouse',
                                                 'guardrails'],
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
                            'glossary_terms': ['source data',
                                               'target table',
                                               'evidence',
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
                                'glossary_terms': ['guardrails',
                                                   'can_continue',
                                                   'evidence',
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
                            'glossary_terms': ['guardrails', 'metadata lakehouse', 'can_continue'],
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
                               'glossary_terms': ['guardrails', 'notebook template'],
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
                                                        'reads catalogue profiles, '
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
                                    'glossary_terms': ['evidence',
                                                       'guardrails',
                                                       'metadata lakehouse',
                                                       'notebook template'],
                                    'return_interpretation': 'The returned state includes '
                                                             'environment, dataset, table, '
                                                             'metadata keys, profile rows, '
                                                             'existing rules, and governance '
                                                             'policy values for downstream '
                                                             'widgets.',
                                    'common_failure_causes': ['METADATA_DATA_CATALOGUE has no '
                                                              'profiles.',
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
                                                                     'evidence or '
                                                                     'runtime outcomes; it writes '
                                                                     'rule intent only to '
                                                                     'METADATA_GUARDRAIL_RULES '
                                                                     'when saving.',
                                                  'glossary_terms': ['guardrails',
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
                                               'profiling; use run_table_guardrails for execution and '
                                               'profile helpers for observed evidence.',
                            'glossary_terms': ['guardrails',
                                               'evidence',
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
 'widget_review_guardrail_governance': {'expanded_purpose': 'Renders governance review controls '
                                                            'for reviewing '
                                                            'proposed or bypass-active enrichment and guardrail '
                                                            'rules, and applying approve, reject, '
                                                            'or supersede actions.',
                                        'when_to_use': 'Use in 03_governance after selecting a '
                                                       'guardrail target to perform human review '
                                                       'of enrichment and guardrail rule intent.',
                                        'do_not_use_when': 'Do not use for automatic pipeline '
                                                           'enforcement or profiles '
                                                           'generation; it is an interactive '
                                                           'governance review widget.',
                                        'glossary_terms': ['guardrails',
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
 'get_selected_agreement': {'expanded_purpose': 'Returns the agreement chosen by '
                                                'widget_pipeline_bootstrap so downstream cells can '
                                                'pass consistent agreement identifiers to pipeline '
                                                'helpers.',
                            'when_to_use': 'Use after rendering and completing '
                                           'widget_pipeline_bootstrap when code needs the selected '
                                           'agreement values.',
                            'glossary_terms': ['notebook template'],
                            'return_interpretation': 'A returned dictionary contains the selected '
                                                     'agreement fields. A missing value means the '
                                                     'selector has not been completed in the '
                                                     'current notebook state.',
                            'common_failure_causes': ['widget_pipeline_bootstrap(select_agreement=True) has not been run.',
                                                      'The user has not selected an agreement.',
                                                      'Notebook state was reset.',
                                                      'The selected row is no longer present in '
                                                      'metadata.']}}

RELATED_GUIDES_BY_SYMBOL = {'setup_notebook': [{'title': 'Templates',
                     'path': '../../notebook-templates-implementation-guide/index.md'},
                    {'title': 'Metadata Tables',
                     'path': '../../reference/metadata.md'}],
 'setup_metadata_tables': [{'title': 'Templates',
                            'path': '../../notebook-templates-implementation-guide/index.md'},
                           {'title': 'Metadata Tables',
                            'path': '../../reference/metadata.md'}],
 'widget_render_data_steward': [{'title': 'Templates',
                                 'path': '../../notebook-templates-implementation-guide/index.md'}],
 'widget_render_data_agreement': [{'title': 'Templates',
                                   'path': '../../notebook-templates-implementation-guide/index.md'}],
 'widget_render_agreement_evidence': [{'title': 'Templates',
                                       'path': '../../notebook-templates-implementation-guide/index.md'},
                                      {'title': 'Metadata Tables',
                                       'path': '../../reference/metadata.md'}],
 'read_lakehouse_table': [{'title': 'Templates',
                           'path': '../../notebook-templates-implementation-guide/index.md'}],
 'write_lakehouse_table': [{'title': 'Templates',
                            'path': '../../notebook-templates-implementation-guide/index.md'},
                           {'title': 'Metadata Tables',
                            'path': '../../reference/metadata.md'}],
 'read_lakehouse_csv': [{'title': 'Templates',
                         'path': '../../notebook-templates-implementation-guide/index.md'}],
 'read_lakehouse_parquet': [{'title': 'Templates',
                             'path': '../../notebook-templates-implementation-guide/index.md'}],
 'read_lakehouse_excel': [{'title': 'Templates',
                           'path': '../../notebook-templates-implementation-guide/index.md'}],
 'read_warehouse_table': [{'title': 'Templates',
                           'path': '../../notebook-templates-implementation-guide/index.md'}],
 'write_warehouse_table': [{'title': 'Templates',
                            'path': '../../notebook-templates-implementation-guide/index.md'}],
 'profile_dataframe': [{'title': 'Pipeline Execution',
                        'path': '../../guided-demo/run-pipeline.md'},
                       {'title': 'Governance Review',
                        'path': '../../guided-demo/review-guardrails.md'}],
 'enforce_freshness': [{'title': 'Pipeline Execution',
                        'path': '../../guided-demo/run-pipeline.md'}],
 'enforce_profile_behavior': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/run-pipeline.md'},
                              {'title': 'Governance Review',
                               'path': '../../guided-demo/review-guardrails.md'}],
 'stop_if_failed': [{'title': 'Pipeline Execution',
                     'path': '../../guided-demo/run-pipeline.md'}],
 'prepare_pipeline_table_configs': [{'title': 'Templates',
                                     'path': '../../notebook-templates-implementation-guide/index.md'},
                                    {'title': 'Pipeline Execution',
                                     'path': '../../guided-demo/run-pipeline.md'}],
 'run_table_guardrails': [{'title': 'Pipeline Execution',
                           'path': '../../guided-demo/run-pipeline.md'}],
 'write_catalogue_evidence': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/run-pipeline.md'},
                              {'title': 'Metadata Tables',
                               'path': '../../reference/metadata.md'}],
 'write_pipeline_lineage': [{'title': 'Templates',
                             'path': '../../notebook-templates-implementation-guide/index.md'},
                            {'title': 'Metadata Tables',
                             'path': '../../reference/metadata.md'}],
 'write_pipeline_run_summary': [{'title': 'Pipeline Execution',
                                 'path': '../../guided-demo/run-pipeline.md'},
                                {'title': 'Metadata Tables',
                                 'path': '../../reference/metadata.md'}],
 'get_selected_agreement': [{'title': 'Templates',
                             'path': '../../notebook-templates-implementation-guide/index.md'}]}



def _metadata_row(symbol_name: str) -> PublicSymbolDocMetadata:
    """Return metadata for a public symbol."""
    for row in PUBLIC_SYMBOL_DOCS:
        if row["symbol_name"] == symbol_name:
            return row
    raise KeyError(symbol_name)


def related_guides(symbol_name: str) -> list[dict[str, str]]:
    """Return related guides for a public symbol."""
    return RELATED_GUIDES_BY_SYMBOL.get(symbol_name, [])
