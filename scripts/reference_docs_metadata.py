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

METADATA_TABLE_PURPOSES = {
    "METADATA_DATA_STEWARD": "Active and historical data steward records used by agreement intake.",
    "METADATA_DATA_AGREEMENT": "Agreement records that describe approved use, steward, recipient, and lifecycle context.",
    "METADATA_DATA_CONTRACT": "Contract rows reserved for implemented data contract lifecycle evidence.",
    "METADATA_DATA_CATALOGUE": "Observed table and column identities used for governed catalogue review and runtime comparisons.",
    "METADATA_DATA_PROFILED": "Detailed per-column profiling evidence captured from a profiled dataset snapshot.",
    "METADATA_DATA_LINEAGE": "Runtime lineage participation rows that connect a profiled dataset snapshot to a Fabric activity.",
    "METADATA_DATA_ACCESS": "Access-review rows reserved for implemented metadata access evidence.",
    "METADATA_ENRICHMENT": "Append-only enrichment intent and approved business context for governed tables and columns.",
    "METADATA_GUARDRAIL": "Append-only schema, freshness, profile-behavior, and DQ guardrail intent rows.",
    "METADATA_GUARDRAIL_RESULTS": "Runtime guardrail outcomes written by pipeline enforcement.",
}

_UNTRACED_SCHEMA_OWNER = {
    "label": "Implemented schema registry only",
    "reason": "The schema is canonical in metadata_schemas.py, but no current src/fabricops_kit writer was traced for this field.",
}

_UNTRACED_AGREEMENT_STEWARD_OWNER = {
    "label": "No traced writer in current agreement workflow",
    "reason": "The current agreement widget writes steward_id, while the implemented schema exposes provider_steward_id and recipient_steward_id.",
}

METADATA_COLUMN_OWNERS = {
    "METADATA_DATA_STEWARD": {
        "__default__": [
            "fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward",
            "fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "steward_id": [
            "fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward",
            "fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward",
            "fabricops_kit.widgets.widget_render_data_steward._generate_steward_id",
        ],
        "effective_from": [
            "fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward",
            "fabricops_kit.widgets.shared.parse_iso_date",
        ],
        "effective_to": [
            "fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward",
            "fabricops_kit.widgets.shared.parse_iso_date",
        ],
        "is_active": [
            "fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward",
            "fabricops_kit.widgets.shared.active_steward",
        ],
        "custom_fields_json": [
            "fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward",
            "fabricops_kit.widgets.shared.serialize_custom_fields",
        ],
    },
    "METADATA_DATA_AGREEMENT": {
        "__default__": [
            "fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement",
            "fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "agreement_id": [
            "fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement",
            "fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement",
            "fabricops_kit.widgets.widget_render_data_agreement._generate_agreement_id",
        ],
        "agreement_version": [
            "fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement",
            "fabricops_kit.widgets.widget_render_data_agreement._next_minor_version",
        ],
        "provider_steward_id": [_UNTRACED_AGREEMENT_STEWARD_OWNER],
        "recipient_steward_id": [_UNTRACED_AGREEMENT_STEWARD_OWNER],
        "start_date": [
            "fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement",
            "fabricops_kit.widgets.shared.parse_iso_date",
        ],
        "expiry_date": [
            "fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement",
            "fabricops_kit.widgets.shared.parse_iso_date",
        ],
        "custom_fields_json": [
            "fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement",
            "fabricops_kit.widgets.shared.serialize_custom_fields",
        ],
    },
    "METADATA_DATA_CONTRACT": {
        "__default__": [_UNTRACED_SCHEMA_OWNER],
        "__audit__": [_UNTRACED_SCHEMA_OWNER],
    },
    "METADATA_DATA_CATALOGUE": {
        "__default__": [
            "fabricops_kit.pipeline.profile_and_register_table.profile_and_register_table",
            "fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled",
        ],
        "__audit__": ["fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns"],
        "metadata_table_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.metadata_keys._build_metadata_table_key",
        ],
        "metadata_column_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.metadata_keys._build_metadata_column_key",
        ],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint",
        ],
    },
    "METADATA_DATA_PROFILED": {
        "__default__": [
            "fabricops_kit.pipeline.profile_and_register_table.profile_and_register_table",
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
        ],
        "__audit__": ["fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns"],
        "metadata_table_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.metadata_keys._build_metadata_table_key",
        ],
        "metadata_column_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.metadata_keys._build_metadata_column_key",
        ],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint",
        ],
        "frequency_json": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._frequency_json_dataframe",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns",
        ],
    },
    "METADATA_DATA_LINEAGE": {
        "__default__": [
            "fabricops_kit.pipeline.profile_and_register_table.profile_and_register_table",
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "lineage_event_id": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.pipeline.profile_and_register_table._lineage_event_id",
        ],
        "activity_id": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
        "notebook_id": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
        "notebook_name": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
        "workspace_id": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
        "workspace_name": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
        "metadata_table_key": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.metadata_keys._build_metadata_table_key",
        ],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
        ],
        "committed_by": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
        "metadata_lakehouse_name": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.audit.build_runtime_audit_fields",
        ],
    },
    "METADATA_DATA_ACCESS": {
        "__default__": [_UNTRACED_SCHEMA_OWNER],
        "__audit__": [_UNTRACED_SCHEMA_OWNER],
    },
    "METADATA_ENRICHMENT": {
        "__default__": [
            "fabricops_kit.widgets.widget_enrich_table_metadata.widget_enrich_table_metadata",
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "metadata_table_key": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._approved_column_identity",
        ],
        "metadata_column_key": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._approved_column_identity",
        ],
        "enrichment_rule_key": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.config.metadata_keys._build_dq_rule_key",
        ],
        "enrichment_payload_json": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "business_name": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "business_description": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "business_meaning": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "column_description": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "classification": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "sensitivity_label": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "pii_flag": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "pii_type": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "data_domain": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "data_owner": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "data_steward": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "usage_notes": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "quality_notes": [
            "fabricops_kit.widgets.shared.build_enrichment_rule_records",
            "fabricops_kit.widgets.shared._enrichment_payload_from_review",
        ],
        "reviewed_by": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
        "reviewed_at": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
        "review_decision": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
        "review_comment": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
    },
    "METADATA_GUARDRAIL": {
        "__default__": [
            "fabricops_kit.widgets.widget_author_schema_freshness_profile_rules.widget_author_schema_freshness_profile_rules",
            "fabricops_kit.widgets.widget_author_dq_rules.widget_author_dq_rules",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_rule_id": [
            "fabricops_kit.widgets.shared._base_guardrail_rule_record",
            "fabricops_kit.widgets.shared._build_dq_rule_records",
        ],
        "rule_key": [
            "fabricops_kit.widgets.shared._base_guardrail_rule_record",
            "fabricops_kit.widgets.shared._build_dq_rule_records",
            "fabricops_kit.config.metadata_keys._build_dq_rule_key",
        ],
        "metadata_column_key": [
            "fabricops_kit.widgets.shared._base_guardrail_rule_record",
            "fabricops_kit.widgets.shared._build_dq_rule_records",
        ],
        "metadata_table_key": [
            "fabricops_kit.widgets.shared._base_guardrail_rule_record",
            "fabricops_kit.widgets.shared._build_dq_rule_records",
        ],
        "rule_parameters_json": [
            "fabricops_kit.widgets.shared._schema_freshness_profile_records_from_selection",
            "fabricops_kit.widgets.shared._build_dq_rule_records",
        ],
        "reviewed_by": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
        "reviewed_at": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
        "review_decision": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
        "review_comment": [
            "fabricops_kit.widgets.widget_review_guardrail_governance.widget_review_guardrail_governance",
            "fabricops_kit.widgets.shared.record_table_governance",
        ],
    },
    "METADATA_GUARDRAIL_RESULTS": {
        "__default__": [
            "fabricops_kit.pipeline.run_table_guardrails.run_table_guardrails",
            "fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_result_id": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
        "result_id": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
        "rule_key": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
        "metadata_table_key": [
            "fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row",
            "fabricops_kit.config.metadata_keys._build_metadata_table_key",
        ],
        "expected_value_json": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
        "actual_value_json": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
        "result_payload_json": ["fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row"],
    },
}

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
  'segment_intro': 'Standalone steward and agreement widgets for Fabric stability.',
  'segments': [{'symbols': ['widget_render_data_steward',
                            'widget_render_data_agreement',
                            'widget_view_data_contract'],
                'title': 'Agreement intake'}],
  'template_path': 'templates/notebooks/01_agreement.ipynb'},
 {'notebook_key': '02_pipeline',
  'notebook_label': '`02_pipeline`',
  'segment_intro': 'Simple v0.2 Lakehouse-first pipeline with complete-table Warehouse read and '
                   'write alternatives.',
  'segments': [{'symbols': ['read_warehouse_table',
                            'read_warehouse_query',
                            'read_lakehouse_table',
                            'profile_and_register_table',
                            'write_lakehouse_table',
                            'write_warehouse_table',
                            'widget_view_data_contract'],
                'title': 'Pipeline run'}],
  'template_path': 'templates/notebooks/02_pipeline.ipynb'},
 {'notebook_key': '03_review',
  'notebook_label': '`03_review`',
  'segment_intro': 'Guardrail governance review using the current supported review widget flow.',
  'segments': [{'symbols': ['widget_select_guardrail_target',
                            'widget_author_schema_freshness_profile_rules',
                            'widget_author_dq_rules',
                            'widget_enrich_table_metadata',
                            'widget_review_guardrail_governance',
                            'widget_view_data_contract'],
                'title': 'Guardrail governance review'}],
  'template_path': 'templates/notebooks/03_review.ipynb'},
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
                            'widget_view_data_contract'],
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
                      'path': '../../notebook-templates.md'},
                     {'title': 'Metadata Tables',
                      'path': '../../reference/metadata.md'}]},
 {'kind': 'function',
  'module': 'config.setup_metadata_tables',
  'function_type': 'callable',
  'summary_override': 'Create missing FabricOps metadata tables and check existing table columns and Spark data types.',
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
                      'path': '../../notebook-templates.md'},
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
  'returns': 'Notebook widget state or rendered widget result used to save steward details to METADATA_DATA_STEWARD.',
  'raises': 'Raises widget, validation, or metadata routing errors when required steward fields are missing or the metadata table cannot be written.',
  'return_interpretation': 'The widget itself is the user interface; saved steward values are '
                           'available to downstream agreement workflows only after the user '
                           'completes the widget action.',
  'common_failure_causes': ['ipywidgets is not available in the runtime.',
                            'Required steward fields are left blank.',
                            'Widget state is cleared by rerunning cells out of order.',
                            'Metadata routing is unavailable when the widget tries to persist '
                            'records.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates.md'}]},
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
  'returns': 'Notebook widget state or rendered widget result used to save agreement details to METADATA_DATA_AGREEMENT.',
  'raises': 'Raises widget, validation, or metadata routing errors when required agreement fields are missing or the metadata table cannot be written.',
  'return_interpretation': 'The rendered widget collects agreement input; downstream helpers can '
                           'only use the agreement after the user saves valid values.',
  'common_failure_causes': ['ipywidgets is not available in the runtime.',
                            'Required agreement fields are missing.',
                            'Agreement identifiers conflict with existing metadata.',
                            'The metadata target cannot be written.'],
  'related_guides': [{'title': 'Templates',
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
                      'path': '../../notebook-templates.md'}]},
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
  'summary_override': 'Profile exact value frequencies for eligible Spark DataFrame columns.',
  'symbol_name': 'profile_frequency_distribution',
  'template_notebook': '02_pipeline / optional 99_explore',
  'template_segment': 'Profiling',
  'use_when': 'Use to inspect value frequencies on exactly the Spark DataFrame supplied by the caller.',
  'do_not_use_when': 'Do not use as a sampling helper, metadata writer, or data-quality enforcement step.',
  'parameters': 'df, optional columns, and top_n.',
  'returns': 'Spark DataFrame containing ranked value frequencies per profiled column; every distinct value is returned unless top_n is supplied.',
  'raises': 'Raises ValueError when supplied top_n is not positive or requested columns do not exist.',
  'side_effects': 'Computes frequency aggregations on the provided DataFrame; it does not write metadata, tables, or files.',
  'fabric_context': 'Use after the caller has intentionally selected the exact DataFrame rows to profile.',
  'ai_verification': 'Verify requested columns and top_n match the intended exploration scope.',
  'preferred_example': 'frequency_df = profile_frequency_distribution(df)',
  'related_functions': ['profile_dataframe'],
  'expanded_purpose': 'Calculates deterministic exact value frequencies with counts, percentages, ranks, and profiled row counts for selected scalar columns.',
  'when_to_use': 'Use during exploration or profiling when value distribution details are needed without writing metadata.',
  'glossary_terms': ['source data', 'distinct value'],
  'return_interpretation': 'Each returned row describes one retained value for one source column.',
  'common_failure_causes': ['Requested columns are missing.',
                            'top_n is not greater than zero when supplied.',
                            'Spark actions fail while computing frequency counts.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Profile a Spark DataFrame, save a profiling snapshot, update catalogue records, and record source or target activity.',
  'symbol_name': 'profile_and_register_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Profiling',
  'use_when': 'Use when a notebook needs to profile a source or target DataFrame and save the FabricOps metadata records that describe that observed table.',
  'do_not_use_when': 'Do not use to write the business DataFrame itself, run guardrails, or sample the input data.',
  'parameters': 'df, profile_role, target, table_name, optional schema, optional frequency_columns, frequency_top_n, and frequency_max_distinct_percent.',
  'returns': 'Spark DataFrame containing one profiling result row for each eligible column in the supplied DataFrame.',
  'raises': 'Raises ValueError for an unsupported profile_role, unknown target, unsupported configured store kind, or invalid table or schema identity.',
  'side_effects': 'Saves a new profiling snapshot to METADATA_DATA_PROFILED, updates or adds table and column records in METADATA_DATA_CATALOGUE, and records source or target activity in METADATA_DATA_LINEAGE.',
  'fabric_context': 'Requires 00_env_config so FabricOps can find the metadata lakehouse configured for the selected environment.',
  'ai_verification': 'Verify the physical asset identity, execution participation role, optional frequency columns, frequency threshold, and append-only profiled evidence write and catalogue identity upsert before running; the role is not stored in METADATA_DATA_PROFILED or METADATA_DATA_CATALOGUE.',
  'preferred_example': 'profiled_df = profile_and_register_table(df_customer, profile_role="source", target="source", schema=SOURCE_SCHEMA, table_name="customer")',
  'related_functions': ['profile_dataframe', 'profile_frequency_distribution', 'run_table_guardrails'],
  'expanded_purpose': 'Orchestrates DataFrame profiling, threshold-guarded default frequency evidence, canonical profiled schema mapping, catalogue identity derivation, deterministic key creation, and append-only profiled evidence registration and catalogue identity upsert while accepting profile_role as execution participation context. The role is validated but not stored in METADATA_DATA_PROFILED or METADATA_DATA_CATALOGUE; automatic lineage registration follows separately.',
  'when_to_use': 'Use in 02_pipeline once for each DataFrame that should produce profiled evidence and catalogue identity. Pass profile_role as execution participation context; automatic lineage registration follows separately and will record the role outside the catalogue.',
  'glossary_terms': ['evidence', 'source data', 'target table'],
  'return_interpretation': 'The returned rows are exactly the catalogue snapshot submitted to the metadata writer for the supplied DataFrame.',
  'common_failure_causes': ['00_env_config has not been run.',
                            'profile_role or the configured target store kind is unsupported.',
                            'The target, table name, or required schema is blank.',
                            'Requested frequency columns are missing from the DataFrame.'],
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
                      'profiled evidence.',
  'symbol_name': 'enforce_profile_behavior',
  'template_notebook': '02_pipeline',
  'template_segment': 'Profile behavior enforcement',
  'expanded_purpose': 'This function protects against silent data behavior changes. It compares '
                      'current static_data or changing_data profiles with previous '
                      'approved evidence. If the current profile no longer matches the '
                      'approved baseline, the function returns a failed guardrail result so the '
                      'pipeline can stop before writing data.',
  'use_when': 'Use in 02_pipeline to enforce profile_mode expectations against previous accepted '
              'profiled evidence.',
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
                            'The metadata lakehouse or profiled evidence table cannot be read.',
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
                       '    metadata_table="METADATA_DATA_PROFILED",\n'
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
  'parameters': {'table_configs': 'List of source or target table configuration dictionaries supplied by the notebook.', 'default_settings': 'Default settings to apply when an individual table config omits them.', 'table_role': 'Use "source" for input tables or "target" for output tables so FabricOps can apply the right required fields.', 'run_id': 'Optional run identifier used for target audit fields.', 'pipeline_name': 'Optional pipeline name used for target audit fields.'},
  'returns': 'Enriched table configs and a dictionary keyed by table key.',
  'raises': 'Raises ValueError when required configuration fields are missing, table_role is unsupported, or target audit columns cannot be added.',
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
                      'path': '../../notebook-templates.md'},
                     {'title': 'Pipeline Execution',
                      'path': '../../guided-demo/run-pipeline.md'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Run approved table checks and return whether the pipeline may continue.',
  'symbol_name': 'run_table_guardrails',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail orchestration',
  'use_when': 'Use in 02_pipeline to run source guardrails before transformation and target '
              'guardrails before writes while keeping per-table results separated.',
  'do_not_use_when': 'Do not use as a replacement for individual helper calls when debugging one '
                     'specific guardrail interactively.',
  'parameters': {'table_configs': 'Prepared source or target table configuration dictionaries. Each item supplies the DataFrame to check plus table identity, expected schema, freshness, profile-behavior, and DQ settings. Call prepare_pipeline_table_configs first when starting from notebook-editable source or target definitions.',
                 'run_id': 'Pipeline run identifier written with saved results and used to group in-memory profiles. Omit only when an active pipeline context already provides it.',
                 'context': 'FabricOps runtime context, usually {"config": CONFIG, "env": ENV}. Omit when 00_env_config or an active pipeline context already provides the context.',
                 'spark_session': 'Spark session used for profiling, metadata reads, DQ checks, and result writes. Omit only when an active pipeline context already provides it.',
                 'agreement_id': 'Optional data agreement identifier to attach to saved profiling and catalogue results. Omit when the active pipeline context supplies it or when no agreement context is needed.',
                 'agreement_version': 'Optional data agreement version to attach to saved profiling and catalogue results. Omit when the active pipeline context supplies it or when no agreement context is needed.',
                 'table_role': 'Optional role for the supplied configurations, usually "source" or "target". Use it when the active pipeline context should remember these definitions for summaries.',
                 'mode': 'Run mode. "profile" is the default review-oriented mode; "enforce" defaults stop_on_failure to True so blocking failures stop the notebook.',
                 'stop_on_failure': 'Whether to stop notebook execution after all table checks have been collected when any table has a blocking failure. Omit to use the default for mode.'},
  'returns': 'Guardrail result bundle with profiles, schema results, freshness results, stability '
             'results, DQ results, catalogue status, evidence definitions, summary, can_continue, '
             'and failed_tables.',
  'raises': 'Raises ValueError when required runtime context such as spark_session or run_id is missing, when mode is unsupported, or when table configs are invalid. With stop_on_failure=True, raises or exits after all checks are collected if blocking failures exist.',
  'side_effects': 'Profiles DataFrames, reads stability/DQ metadata through configured metadata '
                  'routing, writes evidence, and may update table config DataFrames with '
                  'DQ annotations.',
  'fabric_context': 'Requires CONFIG and env from 00_env_config so metadata operations use the '
                    'configured metadata target.',
  'ai_verification': 'Verify stop_on_failure=True is used before transformation or writes when '
                     'blocking guardrails should stop execution.',
  'preferred_example': 'source_guardrail_results = run_table_guardrails(SOURCE_TABLES, '
                       'run_id=RUN_ID, context={"config": CONFIG, "env": ENV}, '
                       'spark_session=spark, stop_on_failure=True)',
  'related_functions': ['prepare_pipeline_table_configs', 'write_catalogue_evidence'],
  'expanded_purpose': 'Runs the approved checks for each configured source or target table. It '
                      'can check schema, data freshness, profile changes, and data-quality rules, '
                      'then returns a combined result showing whether the pipeline may continue.',
  'when_to_use': 'Use in 02_pipeline before transformations or writes when table configs should be '
                 'validated by the standard guardrail sequence.',
  'glossary_terms': ['guardrails',
                     'can_continue',
                     'source data',
                     'target table',
                     'evidence'],
  'return_interpretation': 'Review per-table profiles, schema results, freshness results, '
                           'profile-behavior results, DQ results, catalogue status, the overall '
                           'summary, can_continue, and failed_tables. True can_continue means no '
                           'blocking guardrail result requires the pipeline to stop. False means '
                           'the notebook should stop before writing the affected output.',
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
  'side_effects': 'Writes METADATA_DATA_PROFILED through the configured metadata lakehouse '
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
  'summary_override': 'Evaluate freshness using an active metadata-backed freshness guardrail '
                      'rule.',
  'symbol_name': 'enforce_freshness_rule',
  'template_notebook': '02_pipeline',
  'template_segment': 'Guardrail enforcement',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': {'result_bundle': 'Guardrail result bundle returned by run_table_guardrails.', 'mode': 'Display mode: "summary" for the main outcome table, "detailed" for detailed rows, or "debug" for raw nested values.', 'spark_session': 'Optional Spark session used to convert display rows to Spark DataFrames when available.'},
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Evaluates freshness using a metadata-backed guardrail rule so active '
                      'freshness intent from governance is enforced during pipeline execution.',
  'when_to_use': 'Use in 02_pipeline when active freshness rules from METADATA_GUARDRAIL '
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
  'parameters': {'result_bundle': 'Guardrail result bundle returned by run_table_guardrails.', 'mode': 'Display mode: summary, detailed, or debug.', 'spark_session': 'Optional Spark session used to build Spark DataFrames for display rows.'},
  'returns': 'Display-friendly summary rows, detailed rows, debug data, or Spark DataFrames depending on mode and Spark availability.',
  'raises': 'Raises ValueError when mode is unsupported or the result bundle cannot be displayed.',
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
  'template_notebook': '03_review',
  'template_segment': 'Guardrail governance review',
  'use_when': 'Use in 03_review after widget_select_guardrail_target to enrich selected catalogue columns with descriptive business context, sensitivity, PII, and configured custom metadata.',
  'parameters': 'See the source docstring for the selected guardrail state, configuration, environment, and Spark session parameters.',
  'returns': 'Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.',
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when selected target state is incomplete or the configured metadata lakehouse cannot be written.',
  'related_functions': ['widget_select_guardrail_target', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or profiled evidence.',
  'when_to_use': 'Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.',
  'do_not_use_when': 'Do not use to author DQ rules or enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.',
  'glossary_terms': ['evidence', 'metadata lakehouse', 'guardrails'],
  'return_interpretation': 'The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT.',
  'common_failure_causes': ['The selected guardrail target has no column-level evidence.',
                            'Configured custom fields omit a field name.',
                            'Metadata lakehouse writes cannot be routed through 00_env_config.']},
 {'kind': 'function',
  'module': 'widgets.widget_select_guardrail_target',
  'function_type': 'callable',
  'summary_override': 'Render an interactive target selector for guardrail authoring and '
                      'governance review.',
  'symbol_name': 'widget_select_guardrail_target',
  'template_notebook': '02_pipeline / 03_review',
  'template_segment': 'Guardrail authoring',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders an interactive selector that reads profiled evidence, '
                      'existing guardrail rules, and table governance policy to create the '
                      'handover state for guardrail authoring or review.',
  'when_to_use': 'Use at the start of 02_pipeline authoring or 03_review when a user '
                 'must choose which profiled table to work on.',
  'do_not_use_when': 'Do not use for automatic pipeline enforcement or to write metadata; this '
                     'selector reads metadata and prepares widget state only.',
  'glossary_terms': ['evidence', 'guardrails', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The returned state includes environment, dataset, table, metadata '
                           'keys, profile rows, existing rules, and governance policy values for '
                           'downstream widgets.',
  'common_failure_causes': ['METADATA_DATA_PROFILED has no profiles.',
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
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders interactive controls for authoring schema, freshness, and '
                      'profile-behavior guardrail rule intent while applying the selected table '
                      'governance policy.',
  'when_to_use': 'Use in 02_pipeline after selecting a guardrail target to save active '
                 'self-approved rules, submit proposed rules, or bypass approval with a required '
                 'reason.',
  'do_not_use_when': 'Do not use to write evidence or runtime outcomes; it writes rule '
                     'intent only to METADATA_GUARDRAIL when saving.',
  'glossary_terms': ['guardrails', 'profile behavior', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget state exposes controls, preview records, and save actions '
                           'that produce append-only guardrail rule rows under the table policy.',
  'common_failure_causes': ['The handover state is missing columns.',
                            'Changing-data profile behavior has no watermark column.',
                            'Freshness max lag is invalid.',
                            'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'widgets.widget_view_data_contract',
  'function_type': 'callable',
  'summary_override': 'Render the canonical metadata trace for one registered dataset.',
  'symbol_name': 'widget_view_data_contract',
  'template_notebook': '99_explore',
  'template_segment': 'View data contract',
  'use_when': 'Use across agreement, pipeline, governance-review, and exploration notebooks for a consistent read-only metadata trace of one registered dataset.',
  'parameters': 'See the source docstring for optional agreement, direct or restricted metadata identities, current-notebook pipeline scope with metadata-ID fallback, metadata target, Spark session, and context parameters.',
  'returns': 'Mutable widget state whose get_views callable returns the selection and ten raw, filtered canonical metadata DataFrames.',
  'raises': 'Raises Spark or metadata routing errors when metadata cannot be read. A missing optional widget dependency returns a non-breaking error state.',
  'related_functions': ['read_lakehouse_table', 'profile_dataframe'],
  'expanded_purpose': 'Resolves one metadata_table_key through discovery, direct, agreement-linked, explicit restricted, or historical current-notebook lineage scope; preserves an explicit agreement scope or includes every linked agreement and steward when none is supplied; and returns all ten canonical metadata tables separately without presentation joins.',
  'when_to_use': 'Use near the end of 01_agreement, 02_pipeline, and 03_review for role-specific validation, or in 99_explore for unrestricted browsing.',
  'do_not_use_when': 'Do not use for writing metadata, approving rules, or enforcing guardrails.',
  'glossary_terms': ['metadata catalogue', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The returned state updates as selectors change; call state["get_views"] to retrieve selection details and the ten raw metadata-history DataFrames ordered newest commit first.',
  'common_failure_causes': ['No FabricStore targets are configured.',
                            'The metadata catalogue table does not exist yet.',
                            'The selected FabricStore target has no catalogue rows.']},

 {'kind': 'function',
  'module': 'widgets.widget_register_data_contract',
  'function_type': 'callable',
  'summary_override': 'Register authoritative agreement-to-logical-dataset membership.',
  'symbol_name': 'widget_register_data_contract',
  'template_notebook': '01_agreement',
  'template_segment': 'Agreement intake',
  'use_when': 'Use in 01_agreement after selecting an agreement and registered logical datasets.',
  'parameters': 'See the source docstring for agreement resolution, initial metadata identities, metadata target, Spark session, and context parameters.',
  'returns': 'Mutable widget state with selection and save results plus a get_rows callable for the selected agreement.',
  'raises': 'Raises when an agreement ID cannot be resolved or configured metadata cannot be read or safely written.',
  'related_functions': ['widget_render_data_agreement', 'widget_view_data_contract'],
  'expanded_purpose': 'Writes minimal draft METADATA_DATA_CONTRACT rows linking one agreement to environment-independent metadata_table_key values discovered in the active environment.',
  'when_to_use': 'Use to create or replace draft logical dataset membership for one Data Agreement.',
  'do_not_use_when': 'Do not use for review, approval, promotion, cross-environment authoring, or pipeline inspection.',
  'glossary_terms': ['metadata catalogue', 'metadata lakehouse', 'data contract'],
  'return_interpretation': 'Saved identities are the authoritative draft membership selected for the agreement; unknown initial identities remain non-writable.',
  'common_failure_causes': ['No agreement ID is selected.',
                            'The active environment has no registered catalogue datasets.',
                            'The metadata target cannot be written.']},


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
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
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
                           'METADATA_GUARDRAIL.',
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
  'template_notebook': '03_review',
  'template_segment': 'Governance review',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
  'related_functions': ['run_table_guardrails', 'widget_review_guardrail_governance'],
  'expanded_purpose': 'Renders governance review controls for reviewing '
                      'proposed or bypass-active enrichment and guardrail rules, and applying approve, reject, or '
                      'supersede actions.',
  'when_to_use': 'Use in 03_review after selecting a guardrail target to perform human review '
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

FOCUSED_FUNCTION_DOC_UPDATES = {
    "setup_metadata_tables": {
        "expanded_purpose": "Creates or validates the FabricOps metadata tables required by the framework in the configured metadata lakehouse. It establishes the physical metadata layer that later pipeline, profiling, guardrail, enrichment, and governance workflows read from and write to; it does not populate business metadata or register pipeline datasets.",
        "when_to_use": "Run during initial environment setup, after deploying a FabricOps version with metadata schema changes, or when recreating a development metadata environment. Do not use it as a substitute for setup_notebook, which resolves notebook execution context and configuration.",
        "parameters": "spark is the Spark session used for metadata DDL/table-write operations; config is the FabricOps configuration used to resolve the selected env and metadata lakehouse target; env selects the environment; metadata_schema optionally qualifies schema-enabled metadata lakehouse tables; require_active_steward enforces existing active steward readiness; verbose controls setup output; raise_on_failure raises after all tables are processed if any table fails.",
        "returns": "dict[str, Any] setup report after all managed metadata tables have been created or validated, including status, metadata_schema, fully_qualified_tables, created_tables, validated_tables, failed_tables, table_results, data_agreement, governance, and active metadata counts.",
        "side_effects": "Performs metadata-layer table creation and schema validation in the configured metadata lakehouse. Missing tables are created as empty Delta tables; existing tables are validated and are not silently accepted when incompatible.",
        "return_interpretation": "Use the returned status and per-table results to confirm that the physical metadata layer is ready. The function is primarily used for table-creation and validation side effects, not for registering business datasets.",
        "common_failure_causes": ["Missing or invalid metadata target configuration.", "Spark or Fabric lakehouse context is unavailable.", "The caller lacks permission to create or inspect metadata tables.", "An existing table is missing a required field or has an incompatible Spark field type.", "Nullability and field order are not validated; required field names and Spark data types are validated.", "One table can fail while later tables are still processed; raise_on_failure raises only after processing all tables."],
        "preferred_example": "setup_result = setup_metadata_tables(spark=spark, config=CONFIG, env=ENVIRONMENT_NAME, metadata_schema=METADATA_SCHEMA)",
    },
    "setup_notebook": {
        "expanded_purpose": "Prepares a Fabric notebook to use FabricOps consistently by validating environment configuration, resolving required data and metadata targets, collecting runtime identity, and returning a normalized NotebookSetupContext for downstream cells.",
        "when_to_use": "Call near the beginning of an operational FabricOps notebook after loading environment configuration and before source reads, metadata setup, profiling, guardrails, or writes. It is normally called once per notebook execution and does not replace setup_metadata_tables.",
        "parameters": "config supplies the FabricOps framework configuration; env selects the environment; required_targets identifies the configured data or metadata targets that must resolve; notebook_name overrides automatic runtime notebook-name resolution; run_id_prefix is used only when Fabric does not provide a run id; local_fallback_name supports local tests when Fabric runtime context is unavailable.",
        "returns": "NotebookSetupContext with run_id, notebook_name, workspace_name, user_name, environment, paths, validation_results, runtime_metadata, and readiness_status.",
        "side_effects": "Validates configuration and runtime context only. It does not read or write business data, create Fabric resources, or persist metadata.",
        "return_interpretation": "A ready context means required targets resolved and startup checks did not fail. Review validation_results when readiness_status is not ready before running downstream notebook cells.",
        "common_failure_causes": ["Missing required configuration sections or target names.", "No active Spark session, which is reported as a warning for local fallback mode.", "Fabric notebook runtime utilities are unavailable outside Fabric.", "Workspace, lakehouse, warehouse, or notebook context cannot be resolved.", "Invalid target names or required store identity fields.", "Explicit notebook_name or local_fallback_name is needed when automatic Fabric context is not available."],
        "preferred_example": 'CONTEXT = setup_notebook(CONFIG, env=ENVIRONMENT_NAME, required_targets=["Source", "Unified", "metadata"])',
    },
    "read_lakehouse_csv": {
        "expanded_purpose": "Reads one CSV file or a compatible collection of CSV files from a Fabric lakehouse Files location into a Spark DataFrame using FabricOps target and path resolution. It does not profile, register, display, cache, or write the data automatically.",
        "when_to_use": "Use when source data is stored as CSV under a lakehouse Files path. Use read_lakehouse_table for registered Delta tables, read_lakehouse_parquet for Parquet files, and read_lakehouse_excel for Excel workbooks.",
        "parameters": "relative_path is the file, folder, or wildcard-style Lakehouse Files path resolved under target; target is the logical lakehouse target; header controls first-row column names; spark_session overrides notebook global spark; context can provide resolved FabricOps config/env; additional keyword options are passed to Spark CSV reader, including inferSchema, sep, encoding, schema-related options, recursiveFileLookup, and malformed-row handling.",
        "returns": "Spark DataFrame representing rows parsed from the selected CSV file or files. Columns and data types depend on the supplied schema and CSV reader options.",
        "side_effects": "Constructs a Spark CSV read plan only; it does not write files, tables, or metadata.",
        "return_interpretation": "The returned DataFrame is a normal lazy Spark DataFrame until an action such as count, display, collect, or write is executed.",
        "common_failure_causes": ["The lakehouse target or Files path cannot be resolved.", "The path is missing or the caller lacks read permission.", "Malformed rows, inconsistent files in a folder, absent headers, or empty files do not match the requested Spark CSV options.", "Schema inference can produce unexpected types; an explicit schema can mismatch source values.", "Some Spark failures appear only when a downstream action evaluates the DataFrame."],
        "preferred_example": 'source_df = read_lakehouse_csv("Files/inbound/student_enrolment/*.csv", target="source", header=True, inferSchema=True, spark_session=spark)',
    },
    "read_lakehouse_parquet": {
        "expanded_purpose": "Reads Parquet data from a Fabric lakehouse Files location into a Spark DataFrame while resolving the logical FabricOps lakehouse target and path. It preserves Parquet schema metadata where Spark can infer it and does not register, profile, or write a new table.",
        "when_to_use": "Use for Parquet files or partitioned Parquet folders stored under lakehouse Files. Use read_lakehouse_table for registered Delta tables and read_lakehouse_csv for CSV input.",
        "returns": "Spark DataFrame backed by the selected Parquet file or folder. One DataFrame row represents one source record; partition columns may be added by Spark when reading partitioned folders.",
        "return_interpretation": "The function verifies decodability with a one-row Spark action before returning, then downstream transformations remain normal Spark DataFrame operations.",
        "common_failure_causes": ["The path is missing, inaccessible, empty, corrupt, or not Parquet.", "Schemas are incompatible across files unless Spark options such as mergeSchema are appropriate.", "Schema merging can be expensive on large partitioned folders.", "The configured target cannot be resolved or read.", "Failures can occur during the initial validation action or later Spark evaluation."],
        "preferred_example": 'source_df = read_lakehouse_parquet("Files/curated/student_enrolment/", target="source", spark_session=spark)',
    },
    "read_lakehouse_table": {
        "expanded_purpose": "Loads a registered lakehouse Delta table into a Spark DataFrame using FabricOps target, schema, and table-name resolution so notebooks do not hardcode fully qualified table paths.",
        "when_to_use": "Use for Delta tables registered in a Fabric lakehouse. Use file readers for CSV, Parquet, or Excel files, and read_warehouse_table for Fabric Warehouse tables.",
        "parameters": "table_name is the logical table name, not a qualified schema.table string; target selects the configured lakehouse; schema optionally qualifies schema-enabled lakehouses; spark_session overrides notebook global spark; context supplies reusable FabricOps config/env; reader options are passed to Spark Delta reader.",
        "returns": "Spark DataFrame containing the current rows and columns of the resolved lakehouse table. The DataFrame preserves the table Spark schema and remains lazy until an action is executed.",
        "common_failure_causes": ["The target cannot be resolved or is not a lakehouse.", "The table is not found, exists under another lakehouse or schema, or the schema argument is incorrect.", "The caller lacks read permissions or no Spark session is available.", "Spark Delta read failures may be deferred until an action evaluates the DataFrame."],
        "preferred_example": 'catalogue_df = read_lakehouse_table("METADATA_DATA_CATALOGUE", target="metadata", schema=METADATA_SCHEMA, spark_session=spark)',
    },
    "read_warehouse_query": {
        "expanded_purpose": "Executes caller-supplied read-only SQL against a Fabric Warehouse and returns the result as a Spark DataFrame. Filtering, joins, grouping, and projection run in the Warehouse before rows are transferred to Spark.",
        "when_to_use": "Use when the Warehouse dataset is best expressed as SQL, especially when joins, filters, aggregations, or projections should execute before transfer. Use read_warehouse_table for a straightforward full-table read.",
        "parameters": "query is a read-only SELECT statement or WITH CTE ending in SELECT; target resolves the configured Warehouse connection; spark_session overrides notebook global spark; context supplies reusable FabricOps config/env; options are passed to the Fabric Warehouse Spark connector. Parameter binding is not implemented, so do not interpolate untrusted values.",
        "returns": "Spark DataFrame containing the rows and columns produced by the Warehouse query. The output schema is determined by the SQL projection and Warehouse result types.",
        "common_failure_causes": ["Invalid, blank, or non-read-only SQL.", "Unknown tables or columns, unresolved Warehouse connection, or permission failure.", "Unsupported Warehouse-to-Spark type conversion.", "Very large result transfers can be slow or fail; empty result sets are successful DataFrames with zero rows."],
        "usage_notes": "Apply selective filters, projections, joins, and aggregations in the SQL query where practical so the Warehouse processes them before rows are transferred into Spark. Avoid SELECT * for very large tables when only a subset of fields is required.",
        "preferred_example": 'active_students_df = read_warehouse_query("SELECT student_id, programme_code, enrolment_status FROM dbo.student_enrolment WHERE enrolment_status = \'Active\'", target="warehouse", spark_session=spark)',
    },
    "read_warehouse_table": {
        "expanded_purpose": "Reads a complete Fabric Warehouse table into a Spark DataFrame using the configured Warehouse connection, schema, and table identity. The table remains owned by the Warehouse and is not copied, profiled, registered, or modified.",
        "when_to_use": "Use for a straightforward read of one Warehouse table. Use read_warehouse_query when columns, rows, joins, or aggregations should be reduced in the Warehouse before transfer to Spark.",
        "parameters": "schema is the physical Warehouse schema; table_name is the physical table; target resolves the configured Warehouse; spark_session overrides notebook global spark; context supplies FabricOps config/env; options are passed to the Fabric Warehouse Spark connector.",
        "returns": "Spark DataFrame containing the rows and columns of the resolved Warehouse table.",
        "common_failure_causes": ["The Warehouse connection cannot be resolved.", "The schema or table is not found, the caller lacks permission, or identifiers are invalid.", "The table contains unsupported data types for transfer to Spark.", "Complete-table reads may transfer large datasets; an empty table returns a valid zero-row DataFrame."],
        "usage_notes": "A complete-table read may transfer a large dataset from the Warehouse into Spark. Use read_warehouse_query when the workload can be reduced through SQL projection, filtering, joins, or aggregation.",
        "preferred_example": 'student_df = read_warehouse_table("dbo", "student_enrolment", target="warehouse", spark_session=spark)',
    },
    "write_lakehouse_table": {
        "expanded_purpose": "Writes a Spark DataFrame to a Fabric lakehouse table using the configured FabricOps target, schema, table name, and write settings. Spark-side repartitioning can be applied before the physical Delta write so large datasets can be processed by multiple Spark tasks concurrently; physical Delta partitioning is separate and only occurs when partition_by is supplied.",
        "when_to_use": "Use after a pipeline DataFrame has been prepared and passed required validation or guardrail checks. Small datasets usually need the default write path; large datasets may use repartition_by for additional Spark write parallelism. Use partition_by only for persisted Delta layout based on stable, commonly filtered columns.",
        "parameters": "df is the Spark DataFrame to write and is not mutated; table_name is the unqualified Lakehouse table; target resolves the lakehouse; schema optionally qualifies schema-enabled lakehouses; mode controls append/overwrite/errorifexists/ignore behavior; partition_by physically partitions Delta files and folders; repartition_by accepts a positive integer, one column name, a non-empty string-only list/tuple of column names, or a list/tuple beginning with a positive integer followed by column names and calls Spark repartitioning before writing; options are forwarded to the Delta writer; verbose prints the resolved path; context supplies FabricOps config/env.",
        "returns": "None. The function validates routing and write settings, optionally repartitions the DataFrame, performs the Spark Delta write, and returns after the write completes or Spark raises an error.",
        "common_failure_causes": ["Zero or negative repartition counts, unsupported repartition_by types, empty lists/tuples, non-string column values after any leading partition count, or missing repartition columns.", "Invalid partition_by columns, schema mismatch, append-versus-overwrite conflicts, or unintended destructive overwrite.", "Insufficient write permissions, concurrent writes to the same target table, partial or failed Delta commits, empty DataFrame handling, small-file risk, or Spark shuffle failure."],
        "usage_notes": "Parallel processing is Spark distributed execution over DataFrame partitions, not Python threading, multiprocessing, parallel submission of separate tables, or a separate orchestration helper. repartition_by changes Spark execution partitions for the current write; partition_by changes the persisted Delta layout.",
        "preferred_example": 'write_lakehouse_table(enrolment_df, "STUDENT_ENROLMENT_HISTORY", target="data", schema=DATA_SCHEMA, mode="overwrite", repartition_by=48, partition_by=["academic_year"])',
    },
    "write_warehouse_table": {
        "expanded_purpose": "Writes a Spark DataFrame to a Fabric Warehouse table through the configured Warehouse write path. Spark-side repartitioning can be applied before connector transfer so large datasets can use multiple Spark tasks concurrently; it does not create physical Warehouse table partitions.",
        "when_to_use": "Use when a prepared and validated Spark DataFrame must be stored in a Fabric Warehouse. Small datasets normally use the default write path; large datasets may use repartition_by when the DataFrame has too few partitions or needs more balanced Spark-side write concurrency. Use write_lakehouse_table for Delta lakehouse targets or physical Delta partitioning.",
        "parameters": "df is the Spark DataFrame to transfer and is not mutated; schema is the Warehouse schema such as dbo; table_name is the Warehouse table; target resolves the Warehouse connection; mode is passed to the connector; repartition_by accepts a positive integer, one column name, a non-empty string-only list/tuple of column names, or a list/tuple beginning with a positive integer followed by column names and calls Spark repartitioning before connector transfer; options are forwarded to the connector after required identity options; context supplies FabricOps config/env. No partition_by parameter exists for Warehouse writes.",
        "returns": "None. The function validates repartitioning, optionally writes a repartitioned DataFrame through the Warehouse connector, and returns after connector execution completes or raises an error.",
        "common_failure_causes": ["Zero or negative repartition counts, missing repartition columns, unsupported repartition_by value types, empty lists/tuples, or non-string column values after any leading partition count.", "Schema or table not found, unsupported write mode, authentication or connector failure, Warehouse permission failure, or unsupported Spark-to-Warehouse type conversion.", "Connector-managed transfer or staging failure, transaction or lock conflict, empty DataFrame behaviour, large transfer timeout/resource exhaustion, or accidentally writing the original DataFrame instead of the repartitioned one."],
        "usage_notes": "Parallel Spark tasks within one write_warehouse_table call are not the same as several notebooks or jobs writing to the same Warehouse table concurrently. The function does not coordinate independent writers or guarantee safe simultaneous overwrite operations, and it must not be documented with lakehouse-style partition_by behaviour.",
        "preferred_example": 'write_warehouse_table(transaction_df, "dbo", "FACT_TRANSACTIONS", target="warehouse", mode="append", repartition_by=48)',
    },
    "profile_dataframe": {
        "expanded_purpose": "Calculates column-level profiling statistics for a Spark DataFrame, including row counts, null counts and percentages, distinct counts and percentages, numeric summary statistics, percentiles, and min/max values for each eligible column.",
        "when_to_use": "Use for exploratory or governed profiling when you need a reusable profile DataFrame but do not want to write metadata. Use profile_and_register_table when the profile must be persisted as FabricOps evidence.",
        "returns": "Spark DataFrame with one profiling row per eligible input column and columns COLUMN_NAME, DATA_TYPE, ROW_COUNT, NON_NULL_COUNT, NULL_COUNT, NULL_PERCENT, DISTINCT_COUNT, DISTINCT_PERCENT, MEAN, STDDEV, MIN_VALUE, PERCENTILE_25, MEDIAN, PERCENTILE_75, and MAX_VALUE.",
        "return_interpretation": "Each returned row describes one eligible source column, not one input record. Counts and percentages describe exactly the DataFrame supplied by the caller.",
        "common_failure_causes": ["No eligible non-technical columns remain after exclusions.", "Unsupported complex types or Spark expression limitations can prevent specific statistics.", "Exact distinct counts are more expensive when approximate_distinct is False.", "Spark actions can fail while computing counts, summaries, or percentiles."],
        "preferred_example": 'profile_rows_df = profile_dataframe(source_df, exclude_columns=["_ingested_at"], approximate_distinct=True)',
    },
    "profile_frequency_distribution": {
        "expanded_purpose": "Calculates exact value frequency distributions for eligible Spark DataFrame columns, returning counts, percentages, ranks, source data type, total row count, and non-null count. By default, it profiles every eligible non-technical scalar column and returns every distinct value. It does not sample or write metadata.",
        "when_to_use": "Use when categorical or low-to-medium-cardinality value distribution details are needed for exploration or profiling. Avoid identifiers, UUIDs, free text, timestamps, and columns where nearly every value is unique unless that cost is intentional.",
        "returns": "Spark DataFrame containing ranked frequency rows per profiled column. Null is included as a value, non-null counts are reported separately, and top_n restricts output only when supplied.",
        "common_failure_causes": ["top_n is not greater than zero when supplied.", "Requested columns are missing.", "No eligible scalar columns are available when columns is omitted.", "High-cardinality columns can produce expensive full frequency output; top_n limits only returned rows when supplied."],
        "preferred_example": 'frequency_df = profile_frequency_distribution(source_df)',
    },
    "profile_and_register_table": {
        "expanded_purpose": "Profiles the supplied Spark DataFrame exactly as provided for statistical, schema, catalogue, and lineage evidence; saves a new snapshot to METADATA_DATA_PROFILED; updates matching table and column records or adds new ones in METADATA_DATA_CATALOGUE; records source or target activity in METADATA_DATA_LINEAGE through the configured metadata lakehouse; applies an automatic 80% distinct-per-non-null safeguard to default frequency JSON generation; and can use a caller-provided DataFrame only for frequency distribution evidence.",
        "when_to_use": "Use once for each source or target DataFrame that should produce persisted profiling evidence and catalogue identity in a pipeline run. Use profile_dataframe alone when you only need an in-memory profile. Pass explicit frequency_columns to override the default high-cardinality safeguard, [] to disable frequency evidence, frequency_max_distinct_percent=None to disable automatic threshold filtering, or frequency_profile_df when an upstream workflow has prepared the DataFrame that frequency counts should describe.",
        "returns": "Spark DataFrame containing one detailed profiling row for each eligible column appended to METADATA_DATA_PROFILED, including stable table and column IDs, complete-DataFrame statistical metrics, frequency_json where enabled, schema fingerprint, and runtime audit fields.",
        "return_interpretation": "The returned rows are the detailed profile results for eligible columns. Statistical metrics always describe the complete supplied DataFrame. Frequency counts and percentages describe the complete source by default or the caller-provided frequency_profile_df when supplied; frequency_json discloses source_row_count, profiled_row_count, profiled_non_null_count, and frequency_scope. Catalogue rows and source or target activity records are saved as side effects and are not returned.",
        "common_failure_causes": ["profile_role must be source or target, or the configured target store kind is unsupported.", "target or table_name is blank, or a schema-enabled store has no explicit or configured schema.", "frequency_profile_df is not Spark DataFrame-like, uses an incompatible Spark session, or is missing selected frequency columns.", "The configured metadata target cannot be resolved or written.", "Requested frequency columns are missing or expensive to group; frequency_top_n limits returned values only and does not reduce grouping cost.", "If lineage registration fails after profile and catalogue writes succeed, RuntimeError is raised and earlier writes remain completed."],
        "preferred_example": 'profiled_df = profile_and_register_table(source_df, profile_role="source", target="source", schema=SOURCE_SCHEMA, table_name="student_enrolment", frequency_profile_df=profile_sample_df)',
    },
}

for _row in PUBLIC_SYMBOL_DOCS:
    _update = FOCUSED_FUNCTION_DOC_UPDATES.get(_row.get("symbol_name"))
    if _update:
        _row.update(_update)


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
                                                         'downstream agreement workflows only after '
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
 'profile_frequency_distribution': {'expanded_purpose': 'Calculates exact value frequencies for selected scalar columns, including counts, percentages using the profiled row count as the denominator, ranks, and the total profiled row count.',
                                    'when_to_use': 'Use during exploration or profiling when value distribution details are needed without writing metadata.',
                                    'glossary_terms': ['source data', 'distinct value'],
                                    'return_interpretation': 'Each returned row describes one retained value for one source column.',
                                    'common_failure_causes': ['Requested columns are missing.',
                                                              'top_n is not greater than zero when supplied.',
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

 'enforce_freshness_rule': {'expanded_purpose': 'Evaluates freshness using a metadata-backed '
                                                'guardrail rule so active freshness intent from '
                                                'governance is enforced during pipeline execution.',
                            'when_to_use': 'Use in 02_pipeline when active freshness rules from '
                                           'METADATA_GUARDRAIL should determine the '
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
 'display_guardrail_results': {'parameters': {'result_bundle': 'Guardrail result bundle returned by run_table_guardrails.', 'mode': 'Display mode: summary, detailed, or debug.', 'spark_session': 'Optional Spark session used to build Spark DataFrames for display rows.'},
                               'raises': 'Raises ValueError when mode is unsupported or the result bundle cannot be displayed.',
                               'expanded_purpose': 'Returns summary, detailed, or debug guardrail '
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
                                                        'reads profiled evidence, '
                                                        'existing guardrail rules, and table '
                                                        'governance policy to create the handover '
                                                        'state for guardrail authoring or review.',
                                    'when_to_use': 'Use at the start of 02_pipeline authoring or '
                                                   '03_review when a user must choose '
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
                                    'common_failure_causes': ['METADATA_DATA_PROFILED has no '
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
                                                                     'METADATA_GUARDRAIL '
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
                                                     'METADATA_GUARDRAIL.',
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
                                        'when_to_use': 'Use in 03_review after selecting a '
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
                                                                  'written.']},}

RELATED_GUIDES_BY_SYMBOL = {'setup_notebook': [{'title': 'Templates',
                     'path': '../../notebook-templates.md'},
                    {'title': 'Metadata Tables',
                     'path': '../../reference/metadata.md'}],
 'setup_metadata_tables': [{'title': 'Templates',
                            'path': '../../notebook-templates.md'},
                           {'title': 'Metadata Tables',
                            'path': '../../reference/metadata.md'}],
 'widget_render_data_steward': [{'title': 'Templates',
                                 'path': '../../notebook-templates.md'}],
 'widget_render_data_agreement': [{'title': 'Templates',
                                   'path': '../../notebook-templates.md'}],
 'read_lakehouse_table': [{'title': 'Templates',
                           'path': '../../notebook-templates.md'}],
 'write_lakehouse_table': [{'title': 'Templates',
                            'path': '../../notebook-templates.md'},
                           {'title': 'Metadata Tables',
                            'path': '../../reference/metadata.md'}],
 'read_lakehouse_csv': [{'title': 'Templates',
                         'path': '../../notebook-templates.md'}],
 'read_lakehouse_parquet': [{'title': 'Templates',
                             'path': '../../notebook-templates.md'}],
 'read_lakehouse_excel': [{'title': 'Templates',
                           'path': '../../notebook-templates.md'}],
 'read_warehouse_table': [{'title': 'Templates',
                           'path': '../../notebook-templates.md'}],
 'write_warehouse_table': [{'title': 'Templates',
                            'path': '../../notebook-templates.md'}],
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
                                     'path': '../../notebook-templates.md'},
                                    {'title': 'Pipeline Execution',
                                     'path': '../../guided-demo/run-pipeline.md'}],
 'run_table_guardrails': [{'title': 'Pipeline Execution',
                           'path': '../../guided-demo/run-pipeline.md'}],
 'write_catalogue_evidence': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/run-pipeline.md'},
                              {'title': 'Metadata Tables',
                               'path': '../../reference/metadata.md'}],}



def _metadata_row(symbol_name: str) -> PublicSymbolDocMetadata:
    """Return metadata for a public symbol."""
    for row in PUBLIC_SYMBOL_DOCS:
        if row["symbol_name"] == symbol_name:
            return row
    raise KeyError(symbol_name)


def related_guides(symbol_name: str) -> list[dict[str, str]]:
    """Return related guides for a public symbol."""
    return RELATED_GUIDES_BY_SYMBOL.get(symbol_name, [])
