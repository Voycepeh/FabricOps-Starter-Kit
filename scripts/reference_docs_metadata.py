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
    workflow_step: NotRequired[int | str | None]  # Deprecated: retained for backward compatibility only.
    # Preferred function type for the catalogue. `role` is still accepted by the generator for older metadata.
    function_type: NotRequired[str]
    role: NotRequired[str]
    purpose: NotRequired[str]
    summary_override: str | None






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
    {"module_name": "drift", "visibility": "public", "module_summary": "Owns schema/profile/data drift checks as engineering guardrails during pipeline runs.", "sidebar_group": "3. Data engineer", "sidebar_include": True},
    {"module_name": "metadata", "visibility": "public", "module_summary": "Owns metadata evidence persistence, stable keys, notebook registry, catalogue keys, and runtime audit helpers.", "sidebar_group": "5. Metadata store", "sidebar_include": True},
    {"module_name": "governance_review", "visibility": "public", "module_summary": "Owns table-scoped 03_review catalogue selection, business context review, AI-assisted business context drafting, DQ review and internal enforcement helpers, classification review, AI-assisted sensitivity/PII drafting, and approved metadata commit through record_table_governance.", "sidebar_group": "1. Governance steward", "sidebar_include": True},
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
  'segment_intro': 'Production pipeline guardrails, IO, lineage, and publishing.',
  'segments': [{'symbols': ['widget_select_agreement',
                            'get_selected_agreement',
                            'read_lakehouse_table',
                            'read_lakehouse_csv',
                            'read_lakehouse_parquet',
                            'read_lakehouse_excel',
                            'read_warehouse_table',
                            'validate_schema',
                            'monitor_data_changes',
                            'stop_if_failed',
                            'write_lakehouse_table',
                            'write_warehouse_table',
                            'build_lineage_records'],
                'title': 'Pipeline run'}],
  'template_path': 'templates/notebooks/02_pipeline.ipynb'},
 {'notebook_key': '03_review',
  'notebook_label': '`03_review`',
  'segment_intro': 'Table-scoped governance review and approved metadata recording.',
  'segments': [{'symbols': ['widget_select_catalogue_table',
                            'get_selected_catalogue_table',
                            'load_catalogue_profile_rows',
                            'widget_review_column_context',
                            'widget_review_dq_rules',
                            'widget_review_column_classification',
                            'record_table_governance'],
                'title': 'Governance review'}],
  'template_path': 'templates/notebooks/03_review.ipynb'},
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
  'symbol_name': 'setup_notebook',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap'},
 {'kind': 'function',
  'module': 'config',
  'function_type': 'callable',
  'summary_override': 'Create or validate all FabricOps metadata tables through one setup action.',
  'symbol_name': 'setup_metadata_tables',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap'},
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
  'template_segment': 'Agreement selection'},
 {'kind': 'function',
  'module': 'data_agreement',
  'function_type': 'callable',
  'summary_override': 'Return the agreement selected by widget_select_agreement.',
  'symbol_name': 'get_selected_agreement',
  'template_notebook': '02_pipeline',
  'template_segment': 'Agreement selection'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a table from a configured Fabric lakehouse target.',
  'symbol_name': 'read_lakehouse_table',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Write a DataFrame to a configured Fabric lakehouse target.',
  'symbol_name': 'write_lakehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a CSV file from a configured Fabric lakehouse Files path.',
  'symbol_name': 'read_lakehouse_csv',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a Parquet path from a configured Fabric lakehouse Files path.',
  'symbol_name': 'read_lakehouse_parquet',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read an Excel file from a configured Fabric lakehouse Files path.',
  'symbol_name': 'read_lakehouse_excel',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Read a table from a configured Fabric warehouse target.',
  'symbol_name': 'read_warehouse_table',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'fabric_input_output',
  'function_type': 'callable',
  'summary_override': 'Write a DataFrame to a configured Fabric warehouse target.',
  'symbol_name': 'write_warehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO'},
 {'kind': 'function',
  'module': 'data_profiling',
  'function_type': 'callable',
  'summary_override': 'Profile a source or target DataFrame for schema, quality, and catalogue evidence.',
  'symbol_name': 'profile_dataframe',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Profiling'},
 {'kind': 'function',
  'module': 'drift',
  'function_type': 'callable',
  'summary_override': 'Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.',
  'symbol_name': 'validate_schema',
  'template_notebook': '02_pipeline',
  'template_segment': 'Schema validation'},
 {'kind': 'function',
  'module': 'drift',
  'function_type': 'callable',
  'summary_override': 'Profile data, compare against the approved baseline, and return a drift guardrail result.',
  'symbol_name': 'monitor_data_changes',
  'template_notebook': '02_pipeline',
  'template_segment': 'Drift monitoring'},
 {'kind': 'function',
  'module': 'drift',
  'function_type': 'callable',
  'summary_override': 'Stop a notebook only when a schema or data-change guardrail result blocks continuation.',
  'symbol_name': 'stop_if_failed',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail enforcement'},
 {'kind': 'function',
  'module': 'data_lineage',
  'function_type': 'callable',
  'summary_override': 'Build source-to-target lineage evidence records for a pipeline run.',
  'symbol_name': 'build_lineage_records',
  'template_notebook': '02_pipeline',
  'template_segment': 'Lineage evidence'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render a searchable selector for latest successful catalogue profiles.',
  'symbol_name': 'widget_select_catalogue_table',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Return the table selected by widget_select_catalogue_table.',
  'symbol_name': 'get_selected_catalogue_table',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Load column profile rows for the selected catalogue table.',
  'symbol_name': 'load_catalogue_profile_rows',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render standalone business-context review guidance for selected profile rows.',
  'symbol_name': 'widget_review_column_context',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render standalone DQ-rule review guidance for selected profile rows.',
  'symbol_name': 'widget_review_dq_rules',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Render standalone sensitivity and PII classification review guidance for selected profile rows.',
  'symbol_name': 'widget_review_column_classification',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'},
 {'kind': 'function',
  'module': 'governance_review',
  'function_type': 'callable',
  'summary_override': 'Persist approved table-governance context, DQ-rule, and classification evidence in one v1 '
                      'commit action.',
  'symbol_name': 'record_table_governance',
  'template_notebook': '03_review',
  'template_segment': 'Governance review'}]
