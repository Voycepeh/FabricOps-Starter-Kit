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

CATALOGUE_WIDGET_USAGE_NOTE = """Catalogue viewer widgets let users select governed datasets and load catalogue and profile Spark DataFrames for native Fabric notebook rendering.

They are read-only selectors and do not modify metadata."""

SETUP_NOTEBOOK_USAGE_NOTE = """Use this in the setup notebook to capture and render the key runtime information required by downstream Starter Kit notebooks.

This helps confirm the active environment, configured stores, notebook context, and runtime values before later notebooks depend on them."""

SETUP_METADATA_USAGE_NOTE = """Use this during setup to create the required metadata tables in the configured metadata lakehouse using predefined Starter Kit schemas.

This prepares the metadata store so downstream notebooks, widgets, lineage logging, evidence capture, and governance steps can write to the expected tables."""

CONFIG_USAGE_NOTE = """Use config helpers when notebook setup or downstream helpers need consistent runtime configuration, configured stores, paths, or audit context.

This keeps Starter Kit notebooks aligned on the same environment and config contract instead of each notebook calculating those values differently."""

PIPELINE_USAGE_NOTE = """Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries."""

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

METADATA_REFERENCE_AGREEMENT_CONTRACT_EXPLANATION = (
    "## Data Agreement versus Data Contract\n\n"
    "A Data Agreement is the overarching governance agreement between the accountable data producer and consumer parties, represented by their data stewards. It defines why the data may be shared, who is accountable, the permitted purpose and scope, usage conditions, and the agreement’s review period.\n\n"
    "A Data Contract is the complete, immutable, versioned governed definition of one table under one exact Data Agreement version. Its canonical FabricOps payload freezes the agreement, stewardship, catalogue structure, enrichment, active Guardrail expectations, and narrowed approved usages needed for later approval and export.\n\n"
    "One Data Agreement can govern multiple Data Contracts.\n\n"
    "The agreement answers: Why and under what governance arrangement may this data be shared?\n\n"
    "The contract answers: Exactly what data will be delivered, in what structure, at what quality, and how reliably?"
)

METADATA_REFERENCE_MODEL_DIAGRAM = "![FabricOps metadata model](../assets/fabricops-metadata-model.png)"

METADATA_REFERENCE_MODEL_DIAGRAM_CAPTION = (
    "The diagram below shows how the FabricOps metadata tables relate to one another across agreement, "
    "profiling, guardrail, lineage, and pipeline-run evidence."
)

METADATA_TABLE_MODELS = {
    "METADATA_DATA_STEWARD": {
        "purpose": "Know who is responsible for the data.",
        "grain": "One registered Data Steward.",
        "primary_key": ["steward_id"],
        "foreign_keys": [],
        "relationships": [
            {"cardinality": "1:N", "statement": "One Data Steward can appear as the provider steward on many Data Agreement versions."},
            {"cardinality": "1:N", "statement": "One Data Steward can appear as the recipient steward on many Data Agreement versions."},
        ],
    },
    "METADATA_DATA_AGREEMENT": {
        "purpose": "Define why the data is shared, with whom, and under what conditions.",
        "grain": "One version of one Data Agreement.",
        "primary_key": ["agreement_id", "agreement_version"],
        "foreign_keys": [
            {"local_field": "provider_steward_id", "referenced_table": "METADATA_DATA_STEWARD", "referenced_field": "steward_id", "cardinality": "N:1", "statement": "Each Data Agreement version has one provider steward; one steward can provide many agreement versions."},
            {"local_field": "recipient_steward_id", "referenced_table": "METADATA_DATA_STEWARD", "referenced_field": "steward_id", "cardinality": "N:1", "statement": "Each Data Agreement version has one recipient steward; one steward can receive many agreement versions."},
        ],
        "relationships": [
            {"cardinality": "1:N", "statement": "One Data Agreement lifecycle can govern many Data Contract rows through agreement_id."},
        ],
    },
    "METADATA_DATA_CONTRACT": {
        "purpose": "Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement.",
        "grain": "One immutable Data Contract version for one governed table under one exact Data Agreement version.",
        "primary_key": ["contract_id", "contract_version"],
        "foreign_keys": [
            {"local_field": "agreement_id", "referenced_table": "METADATA_DATA_AGREEMENT", "referenced_field": "agreement_id", "cardinality": "N:1", "statement": "Together with agreement_version, identifies the exact parent Data Agreement version."},
            {"local_field": "agreement_version", "referenced_table": "METADATA_DATA_AGREEMENT", "referenced_field": "agreement_version", "cardinality": "N:1", "statement": "Together with agreement_id, identifies the exact parent Data Agreement version."},
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Each Data Contract governs one logical Catalogue table."},
        ],
        "relationships": [{"cardinality": "1:N", "statement": "One stable contract_id has monotonically increasing immutable contract_version rows."}],
    },
    "METADATA_DATA_CATALOGUE": {
        "purpose": "The current structural registry of known table and column assets. table_id identifies the logical table, and column_id identifies the logical column while its normalized column name remains the same. data_type stores the current structural datatype, and is_active indicates whether the asset currently exists. Datatype changes preserve column_id, removed columns become inactive, and returning columns reuse their deterministic ID. METADATA_DATA_PROFILED retains historical observations.",
        "grain": "One table or column asset in one environment.",
        "primary_key": ["environment_name", "table_id", "column_id"],
        "foreign_keys": [],
        "relationships": [
            {"cardinality": "1:N", "statement": "A Catalogue table identity can be referenced by many Profile, Lineage, Source Observation, Enrichment, Access and Guardrail rows over time."},
        ],
    },
    "METADATA_SOURCE_OBSERVATION": {
        "purpose": "See what FabricOps previously observed about the source data.",
        "grain": "One partition observation within one source-table observation.",
        "primary_key": ["observation_id", "partition_value"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many source observations can belong to one logical Catalogue table identity in an environment."},
        ],
        "relationships": [],
    },
    "METADATA_SOURCE_WATERMARK_CHECKPOINT": {
        "purpose": "Record how far a successfully completed watermark pipeline has processed.",
        "grain": "One successfully committed watermark for one source table and watermark column.",
        "primary_key": ["environment_name", "table_id", "watermark_column", "_committed_at"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many successful checkpoint revisions can belong to one logical source table identity."},
        ],
        "relationships": [],
    },
    "METADATA_DATA_PROFILED": {
        "purpose": "See the column-level profile metrics captured for a dataset snapshot.",
        "grain": "One observed column in one profiling snapshot.",
        "primary_key": ["profile_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many column profile snapshots can describe the same logical Catalogue table over time."},
            {"local_field": "column_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "column_id", "cardinality": "N:1", "statement": "Many profile snapshots can describe the same logical Catalogue column over time."},
        ],
        "relationships": [
            {"related_table": "METADATA_DATA_PROFILED_FREQUENCY", "fields": ["profile_id", "profile_snapshot_id"], "cardinality": "1:1", "statement": "One logical column Profile has one corresponding frequency distribution. The distribution is stored separately and flattened into multiple physical Frequency rows to avoid a large JSON payload in the Profile row."},
        ],
    },
    "METADATA_DATA_PROFILED_FREQUENCY": {
        "purpose": "See the frequency distribution captured for a profiled column.",
        "grain": "One flattened ranked value within one logical frequency distribution for a column Profile.",
        "primary_key": ["frequency_id"],
        "foreign_keys": [
            {"local_field": "profile_id", "referenced_table": "METADATA_DATA_PROFILED", "referenced_field": "profile_id", "cardinality": "N:1", "statement": "Physical Frequency rows link back to the Profile that owns the logical distribution through profile_id."},
            {"local_field": "profile_snapshot_id", "referenced_table": "METADATA_DATA_PROFILED", "referenced_field": "profile_snapshot_id", "cardinality": "N:1", "statement": "Profile and Frequency are produced together in the same profiling snapshot."},
        ],
        "relationships": [
            {"related_table": "METADATA_DATA_PROFILED", "fields": ["profile_id", "profile_snapshot_id"], "cardinality": "1:1", "statement": "Logically this table stores the one frequency distribution belonging to a Profile; that distribution is physically flattened into multiple rows for storage."},
        ],
    },
    "METADATA_DATA_LINEAGE": {
        "purpose": "See where the data came from and where it ends up.",
        "grain": "One table participating as a source or target in one pipeline/profiling execution.",
        "primary_key": ["lineage_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many lineage participation records can refer to the same logical Catalogue table identity."},
            {"local_field": "profile_snapshot_id", "referenced_table": "METADATA_DATA_PROFILED", "referenced_field": "profile_snapshot_id", "cardinality": "N:1", "statement": "The lineage participation is recorded for the same profiling execution identified by profile_snapshot_id."},
        ],
        "relationships": [],
    },
    "METADATA_ENRICHMENT": {
        "purpose": "Add business and governance context to the data.",
        "grain": "One appended enrichment value for one table or column identity in one environment.",
        "primary_key": ["enrichment_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many table- or column-level enrichment rows can reference the same logical Catalogue table identity in an environment."},
            {"local_field": "column_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "column_id", "cardinality": "N:1", "statement": "Column-level enrichment references the Catalogue column through column_id while retaining its parent table_id; table-level enrichment leaves column_id empty."},
        ],
        "relationships": [],
    },
    "METADATA_DATA_ACCESS": {
        "purpose": "See who has row-level access to the data.",
        "grain": "One RLS assignment for one user and one Catalogue table in one environment.",
        "primary_key": ["access_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many RLS assignments can reference the same logical Catalogue table identity in an environment."},
        ],
        "relationships": [],
    },
    "METADATA_GUARDRAIL": {
        "purpose": "Define the expectations the data used in the ETL pipeline should meet.",
        "grain": "One configured Guardrail rule for one Catalogue table or column in one environment.",
        "primary_key": ["guardrail_rule_id", "guardrail_version"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many Guardrail rules can belong to one logical Catalogue table identity in an environment."},
            {"local_field": "column_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "column_id", "cardinality": "N:1", "statement": "Column-level Guardrail rules reference the Catalogue column through column_id; table-level rules leave column_id empty."},
        ],
        "relationships": [
            {"cardinality": "1:N", "statement": "One Guardrail revision can produce many Guardrail Results across pipeline runs through guardrail_rule_id and guardrail_version."},
        ],
    },
    "METADATA_GUARDRAIL_RESULTS": {
        "purpose": "See whether the expectations of the data in the ETL pipeline run are met.",
        "grain": "One runtime outcome for one Guardrail rule in one pipeline run.",
        "primary_key": ["guardrail_result_id"],
        "foreign_keys": [
            {"local_field": "guardrail_rule_id", "referenced_table": "METADATA_GUARDRAIL", "referenced_field": "guardrail_rule_id", "cardinality": "N:1", "statement": "Many runtime outcomes can come from one configured Guardrail rule."},
        ],
        "relationships": [
            {"cardinality": "1:N", "statement": "One Guardrail Result can have many failed-record Guardrail Row Results through guardrail_result_id."},
        ],
    },
    "METADATA_GUARDRAIL_ROW_RESULTS": {
        "purpose": "See the individual records that failed a Data Quality rule.",
        "grain": "One failed record belonging to one Guardrail Result.",
        "primary_key": ["guardrail_row_result_id"],
        "foreign_keys": [
            {"local_field": "guardrail_result_id", "referenced_table": "METADATA_GUARDRAIL_RESULTS", "referenced_field": "guardrail_result_id", "cardinality": "N:1", "statement": "Many failed records can belong to one Guardrail Result."},
        ],
        "relationships": [],
    },


}

METADATA_REFERENCE_ORDER = [
    "METADATA_DATA_STEWARD",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_CONTRACT",
    "METADATA_DATA_CATALOGUE",
    "METADATA_SOURCE_OBSERVATION",
    "METADATA_SOURCE_WATERMARK_CHECKPOINT",
    "METADATA_DATA_PROFILED",
    "METADATA_DATA_PROFILED_FREQUENCY",
    "METADATA_DATA_LINEAGE",
    "METADATA_ENRICHMENT",
    "METADATA_DATA_ACCESS",
    "METADATA_GUARDRAIL",
    "METADATA_GUARDRAIL_RESULTS",
    "METADATA_GUARDRAIL_ROW_RESULTS",
]

METADATA_TABLE_PURPOSES = {
    table_name: str(model["purpose"])
    for table_name, model in METADATA_TABLE_MODELS.items()
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
        "__default__": ["fabricops_kit.widgets.widget_register_data_contract.widget_register_data_contract", "fabricops_kit.widgets.widget_activate_data_contract.widget_activate_data_contract"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
    },
    "METADATA_DATA_CATALOGUE": {
        "__default__": [
            "fabricops_kit.pipeline.profile_and_register_table.profile_and_register_table",
            "fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled",
        ],
        "__audit__": ["fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns"],
        "data_type": ["fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled"],
        "metadata_table_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_metadata_table_key",
        ],
        "metadata_column_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_metadata_column_key",
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
            "fabricops_kit.config.shared.build_metadata_table_key",
        ],
        "metadata_column_key": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_metadata_column_key",
        ],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns",
        ],
    },
    "METADATA_DATA_PROFILED_FREQUENCY": {
        "__default__": [
            "fabricops_kit.pipeline.profile_and_register_table.profile_and_register_table",
            "fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe",
            "fabricops_kit.pipeline.profile_frequency_distribution.profile_frequency_distribution",
        ],
        "__audit__": ["fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns"],
        "metadata_column_key": [
            "fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
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
        "metadata_table_key": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.config.shared.build_metadata_table_key",
        ],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
            "fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation",
        ],
    },
    "METADATA_DATA_ACCESS": {
        "__default__": [_UNTRACED_SCHEMA_OWNER],
        "__audit__": [_UNTRACED_SCHEMA_OWNER],
    },
    "METADATA_ENRICHMENT": {
        "__default__": [
            "fabricops_kit.widgets.widget_enrich_table_metadata.widget_enrich_table_metadata",
            "fabricops_kit.widgets.enrichment_shared.build_enrichment_records",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "enrichment_id": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
        "table_id": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
        "column_id": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
        "environment_name": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
        "enrichment_level": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
        "enrichment_type": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
        "value": ["fabricops_kit.widgets.enrichment_shared.build_enrichment_records"],
    },
    "METADATA_GUARDRAIL": {
        "__default__": [
            "fabricops_kit.widgets.widget_author_guardrails.widget_author_guardrails",
            "fabricops_kit.widgets.widget_author_dq_rules.widget_author_dq_rules",
            "fabricops_kit.pipeline.shared.canonical_guardrail_rule_record",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "guardrail_version": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "table_id": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "column_id": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "environment_name": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "guardrail_type": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "rule_id": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "rule_type": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "rule_parameters_json": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "severity": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
        "is_active": ["fabricops_kit.pipeline.shared.canonical_guardrail_rule_record"],
    },
    "METADATA_GUARDRAIL_RESULTS": {
        "__default__": [
            "fabricops_kit.pipeline.check_schema.check_schema",
            "fabricops_kit.pipeline.check_freshness.check_freshness",
            "fabricops_kit.pipeline.check_changes.check_changes",
            "fabricops_kit.pipeline.check_dq.check_dq",
            "fabricops_kit.pipeline.shared.write_guardrail_result_row",
            "fabricops_kit.pipeline.shared.check_dq_runtime",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_result_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "run_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "environment_name": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "status": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "can_continue": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "severity": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "reason": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "result_payload_json": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
    },
    "METADATA_GUARDRAIL_ROW_RESULTS": {
        "__default__": [
            "fabricops_kit.pipeline.check_dq.check_dq",
            "fabricops_kit.pipeline.shared.check_dq_runtime",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_row_result_id": ["fabricops_kit.pipeline.shared.check_dq_runtime"],
        "guardrail_result_id": ["fabricops_kit.pipeline.shared.check_dq_runtime"],
        "row_identity": ["fabricops_kit.pipeline.shared.check_dq_runtime"],
        "involved_columns_json": ["fabricops_kit.pipeline.shared.check_dq_runtime"],
        "failed_values_json": ["fabricops_kit.pipeline.shared.check_dq_runtime"],
        "failure_reason": ["fabricops_kit.pipeline.shared.check_dq_runtime"],
    },
    "METADATA_SOURCE_OBSERVATION": {
        "__default__": ["fabricops_kit.pipeline.observe_table._observe_table_core"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "metadata_table_key": [
            "fabricops_kit.pipeline.observe_table._observe_table_core",
            "fabricops_kit.config.shared.build_metadata_table_key",
        ],
    },
    "METADATA_SOURCE_WATERMARK_CHECKPOINT": {
        "__default__": ["fabricops_kit.pipeline.read_pipeline_prep._checkpoint_value"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
    },
}

USAGE_NOTE_BY_FUNCTION = {
    "setup_notebook": SETUP_NOTEBOOK_USAGE_NOTE,
    "setup_metadata_tables": SETUP_METADATA_USAGE_NOTE,
    "widget_view_catalogue": CATALOGUE_WIDGET_USAGE_NOTE,
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

 {'module_name': 'widgets.widget_author_guardrails',
  'visibility': 'public',
  'module_summary': 'Owns versioned Schema, Freshness, and Changes guardrail authoring.',
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
 {'notebook_key': '01_governance',
  'notebook_label': '`01_governance`',
  'segment_intro': 'Persistent Governance lifecycle before and after Engineering evidence production.',
  'segments': [{'symbols': ['widget_render_data_steward',
                            'widget_render_data_agreement',
                            'widget_register_data_contract',
                            'widget_view_catalogue',
                            'widget_enrich_table_metadata',
                            'widget_author_guardrails',
                            'widget_author_dq_rules'],
                'title': 'Agreement, contract, evidence, enrichment, and guardrails'}],
  'template_path': 'templates/notebooks/01_governance.ipynb'},
 {'notebook_key': '02_pipeline',
  'notebook_label': '`02_pipeline`',
  'segment_intro': 'Simple v0.2 Lakehouse-first pipeline with complete-table Warehouse read and '
                   'write alternatives.',
  'segments': [{'symbols': ['widget_select_data_contract', 'read_pipeline_prep', 'check_schema', 'check_freshness', 'check_changes', 'check_dq'],
                'title': 'Observe and check source cheaply'},
               {'symbols': ['read_lakehouse_csv',
                            'read_lakehouse_excel',
                            'read_lakehouse_parquet',
                            'read_lakehouse_table',
                            'read_warehouse_query',
                            'read_warehouse_table'],
                'title': 'Read source data'},
               {'symbols': ['profile_dataframe',
                            'profile_frequency_distribution',
                            'profile_and_register_table'],
                'title': 'Profile and register data'},
               {'symbols': ['write_lakehouse_table', 'write_warehouse_table'],
                'title': 'Write target data'},
               {'symbols': ['widget_view_catalogue'],
                'title': 'Review registered metadata'}],
  'template_path': 'templates/notebooks/02_pipeline.ipynb'},
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
                            'widget_view_catalogue'],
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
  'segments': [{'symbols': ['write_lakehouse_table'],
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
  'use_when': 'Use in 00_env_config to customize 01_governance metadata and widget behavior.',
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
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Check observed table schema against direct or approved schema intent.',
  'symbol_name': 'check_schema',
  'template_notebook': '02_pipeline',
  'template_segment': 'Source guardrails',
  'use_when': 'Use directly for targeted schema validation or through run_table_guardrails.',
  'do_not_use_when': 'Do not use to infer or author expected schema rules.',
  'parameters': 'dataframe, optional expected_schema and preset, or approved rules_df with table identity.',
  'returns': 'Structured schema guardrail status, continuation decision, checks, and differences.',
  'side_effects': 'None. The orchestrator records execution evidence when configured.',
  'preferred_example': 'schema_result = check_schema(df, {"order_id": "bigint"})',
  'related_functions': ['check_freshness', 'check_changes']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Check whether source timing satisfies direct or approved freshness intent.',
  'symbol_name': 'check_freshness',
  'template_notebook': '02_pipeline',
  'template_segment': 'Source guardrails',
  'use_when': 'Use directly for targeted freshness validation or through run_table_guardrails.',
  'do_not_use_when': 'Do not use for schema or row-content changes.',
  'parameters': 'dataframe, freshness column, maximum lag, severity, reference date, or approved rule context.',
  'returns': 'Structured freshness evidence and continuation decision.',
  'side_effects': 'None. The orchestrator records execution evidence when configured.',
  'preferred_example': 'freshness_result = check_freshness(df, "business_date", 2)',
  'related_functions': ['check_schema', 'check_changes', 'enforce_freshness']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Describe deterministic partition and logical-row source changes.',
  'symbol_name': 'check_changes',
  'template_notebook': '02_pipeline',
  'template_segment': 'Source guardrails',
  'use_when': 'Use after schema and freshness checks to compare current and previous source observations.',
  'do_not_use_when': 'Do not use as target merge policy or a persistent CDC framework.',
  'parameters': 'current and previous data, partition and logical key columns, range configuration, source pattern, comparison scope, mutable window, and an explicit version column for versioned sources.',
  'returns': 'Structured change counts, partition fingerprints, recent and historical classifications, and observed ranges.',
  'side_effects': 'None. It does not merge or write target data.',
 'preferred_example': 'change_result = check_changes(current_df, previous_df, key_columns=["order_id"])',
 'related_functions': ['check_schema', 'check_freshness', 'read_pipeline_prep']},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Evaluate current active governed DQ rules and persist linked rule and failed-row evidence.',
  'symbol_name': 'check_dq',
  'template_notebook': '02_pipeline',
  'template_segment': 'Source guardrails',
  'use_when': 'Use after reading source or target rows and before a governed write proceeds.',
  'do_not_use_when': 'Do not use to author rules or copy complete failed source rows into metadata.',
  'parameters': 'DataFrame, table and configured target identity, optional dataset/run identity, and optional business row-identity columns.',
  'returns': 'Overall DQ status, continuation decision, per-rule checks, aggregate counts, and a tagged DataFrame.',
  'side_effects': 'Appends one rule/run summary per evaluated rule and compact evidence for failed row/rule pairs.',
  'preferred_example': 'dq_result = check_dq(source_df, "orders", row_identity_columns=["order_id"])',
  'related_functions': ['check_schema', 'check_freshness', 'check_changes']},
 {'kind': 'function',
  'module': 'pipeline.read_pipeline_prep',
  'function_type': 'callable',
  'summary_override': 'Prepare governed source observation and read scope without reading business data.',
  'symbol_name': 'read_pipeline_prep',
  'template_notebook': '02_pipeline',
  'template_segment': 'Source preparation',
  'use_when': 'Use before the visible source reader to resolve observation evidence and one governed processing scope.',
  'do_not_use_when': 'Do not use as a replacement for the physical Lakehouse or Warehouse reader.',
  'parameters': 'Source and target identities plus the current Development-authored load strategy and parameters.',
  'returns': 'Observation and change evidence, canonical processing, and skip, full, or incremental read scope.',
  'side_effects': 'Persists compact source observation and change evidence; it does not read business rows or write the target.',
  'preferred_example': 'read_prep = read_pipeline_prep("orders", "orders_curated", load_strategy="append")',
  'related_functions': ['check_changes', 'write_pipeline_prep', 'read_lakehouse_table']},
 {'kind': 'function',
  'module': 'pipeline.write_pipeline_prep',
  'function_type': 'callable',
  'summary_override': 'Prepare governed target write inputs and technical fields without physically writing.',
  'symbol_name': 'write_pipeline_prep',
  'template_notebook': '02_pipeline',
  'template_segment': 'Target preparation',
  'use_when': 'Use after target Guardrails and immediately before the visible target writer.',
  'do_not_use_when': 'Do not use as a replacement for write_lakehouse_table or write_warehouse_table.',
  'parameters': 'Validated business DataFrame, exact read preparation result, and configured target.',
  'returns': 'Audited DataFrame, writer mode/options, canonical processing, and prepared execution scope.',
  'side_effects': 'Resolves run audit context and transforms the DataFrame lazily; it does not physically write.',
  'preferred_example': 'write_prep = write_pipeline_prep(transformed_df, read_prep, target="unified")',
  'related_functions': ['read_pipeline_prep', 'write_lakehouse_table', 'write_warehouse_table']},
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
  'related_functions': ['setup_notebook'],
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
  'template_notebook': '01_governance',
  'template_segment': 'Agreement intake',
  'expanded_purpose': 'Renders the data steward intake widget so a notebook user can capture '
                      'steward contact and ownership details for an agreement workflow.',
  'when_to_use': 'Use in 01_governance when collecting or updating data steward details before '
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
  'template_notebook': '01_governance',
  'template_segment': 'Agreement intake',
  'expanded_purpose': 'Renders the data agreement intake widget used to capture the overarching '
                      'governance arrangement between accountable producer and consumer stewards, including purpose, scope, permitted use, and review context.',
  'when_to_use': 'Use in 01_governance after steward context exists to establish the parent governance agreement before technical Data Contracts are registered.',
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
  'related_functions': ['read_lakehouse_table', 'write_warehouse_table'],
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
  'parameters': 'df and optional exclude_columns.',
  'returns': 'Spark DataFrame containing one profile row per eligible business column.',
  'raises': 'Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.',
  'side_effects': 'Computes profiling aggregations on the provided DataFrame; it does not write '
                  'metadata, tables, or files.',
  'fabric_context': 'Use after reading source/target data and before metadata persistence or '
                    'governance review workflows that need profiles.',
  'ai_verification': 'Verify the profile row count matches expected business columns and inspect '
                     'key schema/profile fields before writing evidence.',
  'preferred_example': 'profile_rows_df = profile_dataframe(df, exclude_columns=["technical_column"])',
  'related_functions': ['enforce_profile_behavior'],
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
                      'path': '../../guided-demo/02-run-pipeline.md'},
                     {'title': 'Governance Review',
                      'path': '../../guided-demo/03-enrich-guardrails.md'}]},
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
                      'path': '../../guided-demo/02-run-pipeline.md'}]},
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
  'related_functions': ['profile_dataframe', 'profile_frequency_distribution'],
  'expanded_purpose': 'Orchestrates DataFrame profiling, threshold-guarded default frequency evidence, canonical profiled schema mapping, catalogue identity derivation, deterministic key creation, and append-only profiled evidence registration and catalogue identity upsert while accepting profile_role as execution participation context. The role is validated but not stored in METADATA_DATA_PROFILED or METADATA_DATA_CATALOGUE; automatic lineage registration follows separately.',
  'when_to_use': 'Use in 02_pipeline once for each DataFrame that should produce profiled evidence and catalogue identity. Pass profile_role as execution participation context; automatic lineage registration follows separately and will record the role outside the catalogue.',
  'glossary_terms': ['evidence', 'source data', 'target table'],
  'return_interpretation': 'The returned rows are exactly the catalogue snapshot submitted to the metadata writer for the supplied DataFrame.',
  'common_failure_causes': ['00_env_config has not been run.',
                            'profile_role or the configured target store kind is unsupported.',
                            'The target, table name, or required schema is blank.',
                            'Requested frequency columns are missing from the DataFrame.'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/02-run-pipeline.md'}]},
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
                      'path': '../../guided-demo/02-run-pipeline.md'}]},
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
                      'path': '../../guided-demo/02-run-pipeline.md'},
                     {'title': 'Governance Review',
                      'path': '../../guided-demo/03-enrich-guardrails.md'}]},
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
  'related_functions': ['enforce_freshness', 'enforce_profile_behavior'],
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
                      'path': '../../guided-demo/02-run-pipeline.md'}]},
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
                      'path': '../../guided-demo/02-run-pipeline.md'},
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
  'related_functions': [],
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
  'module': 'widgets.widget_enrich_table_metadata',
  'function_type': 'callable',
  'summary_override': 'Browse catalogue history and maintain metadata enrichment.',
  'symbol_name': 'widget_enrich_table_metadata',
  'template_notebook': '01_governance',
  'template_segment': 'Guardrail governance review',
  'use_when': 'Select a logical table in the active environment, browse its current and historical columns, and maintain table- or column-level enrichment.',
  'parameters': 'See the source docstring for the Spark session and optional active Fabric context.',
  'returns': 'Standalone three-pane browser state with table and column selectors, draft-aware detail controls, record building, and a save callback.',
  'raises': 'Raises clear catalogue identity, metadata read, or metadata routing errors when canonical catalogue evidence is unavailable.',
  'related_functions': ['widget_view_catalogue'],
  'expanded_purpose': 'Uses the environment-specific Catalogue table_id and column_id identities to distinguish editable current columns from grey, read-only historically removed columns with their last-observed dates. It maintains Description and Classification for tables and those values plus Personal_identifier for columns.',
  'when_to_use': 'Use when notebook users need an independent, landscape-oriented metadata catalogue browser and enrichment editor without first selecting a guardrail target.',
  'do_not_use_when': 'Do not use to author DQ rules, edit data-contract membership, or change removed-column enrichment.',
  'glossary_terms': ['evidence', 'metadata lakehouse', 'metadata catalogue'],
  'return_interpretation': 'Only non-empty changed values are appended to METADATA_ENRICHMENT for the active environment; repeated unchanged saves produce no write.',
  'common_failure_causes': ['The active environment has no logical tables in the metadata catalogue.',
                            'A selected table lacks table_id or a current column lacks column_id.',
                            'Metadata lakehouse reads or writes cannot be routed through 00_env_config.']},

 {'kind': 'function',
  'module': 'widgets.widget_author_guardrails',
  'function_type': 'callable',
  'summary_override': 'Render versioned table-level Schema, Freshness, and Changes guardrail controls.',
  'symbol_name': 'widget_author_guardrails',
  'template_notebook': '01_governance',
  'template_segment': 'Guardrail authoring',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the notebook runtime, Spark session, state, and '
                'record parameters accepted by this helper.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
  'related_functions': ['widget_author_dq_rules'],
  'expanded_purpose': 'Renders one lightweight form for versioned table-level Schema, Freshness, and Changes guardrail intent.',
  'when_to_use': 'Use in 01_governance after selecting a table to append a new guardrail configuration version.',
  'do_not_use_when': 'Do not use to write evidence or runtime outcomes; it writes rule '
                     'intent only to METADATA_GUARDRAIL when saving.',
  'glossary_terms': ['guardrails', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget state exposes controls, preview records, and save actions '
                           'that produce append-only guardrail rule rows under the table policy.',
  'common_failure_causes': ['The selected table state is missing columns or its canonical key.',
                            'Freshness maximum age is invalid.',
                            'The metadata target cannot be written.']},
 {'kind': 'function',
  'module': 'widgets.widget_view_catalogue',
  'function_type': 'callable',
  'summary_override': 'Select catalogue evidence through an explicit pipeline, agreement, or explore dataset scope.',
  'symbol_name': 'widget_view_catalogue',
  'template_notebook': '01_governance, 02_pipeline, 99_explore',
  'template_segment': 'Catalogue review',
  'use_when': 'Use with mode pipeline for current-notebook lineage, agreement for selected-agreement contracts, or explore for direct current-environment browsing.',
  'related_functions': ['profile_and_register_table', 'widget_register_data_contract'],
  'return_interpretation': 'Call state["get_views"]() to receive exactly catalogue, profile, frequency, guardrail_results, and guardrail_row_results for the selected metadata_table_key.'},

 {'kind': 'function',
  'module': 'widgets.widget_register_data_contract',
  'function_type': 'callable',
  'summary_override': 'Assemble and save a versioned Data Contract for one governed table.',
  'symbol_name': 'widget_register_data_contract',
  'template_notebook': '01_governance',
  'template_segment': 'Contract registration',
  'use_when': 'Use in 01_governance after an Agreement version is saved and governed table metadata is ready for contract review.',
  'parameters': 'See the source docstring for exact Agreement and table selection, approved usages, metadata target, Spark session, and context parameters.',
  'returns': 'Mutable contract review state with structured governance context, completeness warnings, and an explicit save action.',
  'raises': 'Raises when an agreement ID cannot be resolved or configured metadata cannot be read or safely written.',
  'related_functions': ['widget_render_data_agreement', 'widget_view_catalogue', 'widget_enrich_table_metadata'],
  'expanded_purpose': 'Assembles one self-contained canonical FabricOps contract payload from the exact Agreement version, its stewards, one active Catalogue table and columns, current enrichment, and active Guardrail expectations. Each explicit save appends the next immutable draft version; runtime Guardrail results are excluded.',
  'when_to_use': 'Use to review governed metadata and explicitly freeze a new draft contract version for one table before a later approval workflow.',
  'do_not_use_when': 'Do not use to edit enrichment, descriptions, classifications, personal-identifier values, guardrails, or agreement metadata.',
  'glossary_terms': ['metadata catalogue', 'metadata lakehouse', 'data contract'],
  'return_interpretation': 'review exposes the assembled governance context without HTML parsing; save appends exactly one draft contract version and does not mutate history.',
 'common_failure_causes': ['No exact saved Agreement version is selected.',
                            'The active environment has no active governed Catalogue tables.',
                            'The metadata target cannot be written.']},

 {'kind': 'function',
  'module': 'widgets.widget_activate_data_contract',
  'function_type': 'callable',
  'summary_override': 'Manually select the frozen Data Contract version used by Production.',
  'symbol_name': 'widget_activate_data_contract',
  'template_notebook': '01_governance',
  'template_segment': 'Contract activation',
  'use_when': 'Use after saving a Data Contract version to make that exact frozen definition active for its governed table.',
  'related_functions': ['widget_register_data_contract', 'check_schema', 'check_freshness', 'check_changes', 'check_dq'],
  'return_interpretation': 'review is derived only from the frozen payload; activate updates lifecycle fields and reports whether a write occurred.',
  'common_failure_causes': ['The selected version does not exist or belongs to another table.',
                            'The selected contract is rejected or its frozen payload is invalid.',
                            'The metadata table contains multiple active versions.']},

 {'kind': 'function',
  'module': 'widgets.widget_select_data_contract',
  'function_type': 'callable',
  'summary_override': 'Choose whether Development Guardrail checks use current authoring rules or one exact frozen Data Contract version.',
  'symbol_name': 'widget_select_data_contract',
  'template_notebook': '02_pipeline',
  'template_segment': 'Source validation selection',
  'use_when': 'Use once before source Guardrail checks when Development engineers need to test current authoring Guardrails or an exact frozen contract version.',
  'related_functions': ['widget_activate_data_contract', 'check_schema', 'check_freshness', 'check_changes', 'check_dq'],
  'return_interpretation': 'The default clears this table’s Development override; an exact selection stores its contract ID and version under the canonical table ID in the active Fabric context.',
  'expanded_purpose': 'This read-only Development testing tool does not activate contracts. Current authoring Guardrails are the default, while Production uses the active Data Contract automatically.',
  'common_failure_causes': ['The configured physical table has no canonical active Catalogue table identity.',
                            'The selected version is rejected or belongs to another table.',
                            'The frozen contract payload is invalid.']},


 {'kind': 'function',
  'module': 'widgets.widget_author_dq_rules',
  'function_type': 'callable',
  'summary_override': 'Render interactive manual DQ guardrail authoring controls.',
  'symbol_name': 'widget_author_dq_rules',
  'template_notebook': '01_governance',
  'template_segment': 'Guardrail authoring',
  'use_when': 'Use this public FabricOps helper from the matching notebook workflow when that '
              'guardrail authoring, governance, or display step is required.',
  'parameters': 'See the source docstring for the Spark session and optional initial rule controls.',
  'returns': 'Notebook-facing state, records, display rows, or persisted metadata rows produced by '
             'the helper.',
  'raises': 'Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.',
  'related_functions': [],
  'expanded_purpose': 'Renders standalone structured DQ authoring controls with integrated profiled-target selection.',
  'when_to_use': 'Use in 01_governance to select a profiled table and submit structured DQ rule intent.',
  'do_not_use_when': 'Do not use for runtime DQ enforcement or catalogue profiling.',
  'glossary_terms': ['guardrails', 'evidence', 'metadata lakehouse', 'notebook template'],
  'return_interpretation': 'The widget returns mutable preview records; '
                           'approved saves write guardrail rule intent to '
                           'METADATA_GUARDRAIL.',
  'common_failure_causes': ['Rule parameters are invalid for the selected DQ type.',
                            'No applicable column is selected.',
                            'The metadata target cannot be written.']},


 ]

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
        "common_failure_causes": ["No eligible non-technical columns remain after exclusions.", "Unsupported complex types or Spark expression limitations can prevent specific statistics.", "Exact distinct counts can be expensive for high-cardinality columns.", "Spark actions can fail while computing counts, summaries, or percentiles."],
        "preferred_example": 'profile_rows_df = profile_dataframe(source_df, exclude_columns=["_ingested_at"])',
    },
    "profile_frequency_distribution": {
        "expanded_purpose": "Calculates exact value frequency distributions for eligible Spark DataFrame columns, returning counts, percentages, ranks, source data type, total row count, and non-null count. By default, it profiles every eligible non-technical scalar column and returns every distinct value. It does not sample or write metadata.",
        "when_to_use": "Use when categorical or low-to-medium-cardinality value distribution details are needed for exploration or profiling. Avoid identifiers, UUIDs, free text, timestamps, and columns where nearly every value is unique unless that cost is intentional.",
        "returns": "Spark DataFrame containing ranked frequency rows per profiled column. Null is included as a value, non-null counts are reported separately, and top_n restricts output only when supplied.",
        "common_failure_causes": ["top_n is not greater than zero when supplied.", "Requested columns are missing.", "No eligible scalar columns are available when columns is omitted.", "High-cardinality columns can produce expensive full frequency output; top_n limits only returned rows when supplied."],
        "preferred_example": 'frequency_df = profile_frequency_distribution(source_df)',
    },
    "profile_and_register_table": {
        "expanded_purpose": "Profiles the supplied Spark DataFrame exactly as provided; saves compact summary rows to METADATA_DATA_PROFILED; reuses profile_frequency_distribution to replace normalized rows in METADATA_DATA_PROFILED_FREQUENCY; updates catalogue identities; and records source or target lineage through the configured metadata lakehouse.",
        "when_to_use": "Use once for each source or target DataFrame that should produce persisted profiling evidence and catalogue identity in a pipeline run. Use profile_dataframe alone when you only need an in-memory profile. Pass explicit frequency_columns to override the default high-cardinality safeguard, [] to disable frequency evidence, frequency_max_distinct_percent=None to disable automatic threshold filtering, or frequency_profile_df when an upstream workflow has prepared the DataFrame that frequency counts should describe.",
        "returns": "Spark DataFrame containing one compact profiling summary row for each eligible column appended to METADATA_DATA_PROFILED, including profile_id, profile_snapshot_id, stable table_id and column_id identities, environment_name, complete-DataFrame statistics, profiling timestamp, and runtime audit fields.",
        "return_interpretation": "The returned rows are the compact parent summaries. Flattened frequency rows are written separately to METADATA_DATA_PROFILED_FREQUENCY, link to their parent through profile_id, and share the same profile_snapshot_id; frequency, catalogue, and lineage rows are side effects and are not returned.",
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
                                'when_to_use': 'Use in 01_governance when collecting or updating '
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
                                                      'used to capture the overarching governance '
                                                      'arrangement between accountable producer and '
                                                      'consumer stewards, including purpose, scope, '
                                                      'permitted use, and review context.',
                                  'when_to_use': 'Use in 01_governance after steward context exists '
                                                 'to establish the parent governance agreement '
                                                 'before technical Data Contracts are registered.',
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

 'widget_author_guardrails': {'expanded_purpose': 'Renders interactive '
                                                                      'controls for authoring '
                                                                      'versioned table-level Schema, '
                                                                      'Freshness, and Changes guardrail intent.',
                                                  'when_to_use': 'Use in 01_governance after selecting a table to append a new guardrail configuration version.',
                                                  'do_not_use_when': 'Do not use to write '
                                                                     'evidence or '
                                                                     'runtime outcomes; it writes '
                                                                     'rule intent only to '
                                                                     'METADATA_GUARDRAIL '
                                                                     'when saving.',
                                                  'glossary_terms': ['guardrails',
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
                                                  'common_failure_causes': ['The selected table state is missing columns or its canonical key.',
                                                                            'Freshness maximum age is invalid.',
                                                                            'The metadata target '
                                                                            'cannot be written.']},
 'widget_author_dq_rules': {'expanded_purpose': 'Renders standalone structured DQ authoring controls with integrated profiled-target selection.',
                            'when_to_use': 'Use in 01_governance to select a profiled table and submit structured DQ rule intent.',
                            'do_not_use_when': 'Do not use for runtime DQ enforcement or catalogue profiling.',
                            'glossary_terms': ['guardrails',
                                               'evidence',
                                               'metadata lakehouse',
                                               'notebook template'],
                            'return_interpretation': 'The widget returns mutable preview records; explicit saves write guardrail rule intent to METADATA_GUARDRAIL.',
                            'common_failure_causes': ['Rule parameters are invalid for the selected DQ type.',
                                                      'No applicable column is selected.',
                                                      'The metadata target cannot be written.']},
 }

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
                        'path': '../../guided-demo/02-run-pipeline.md'},
                       {'title': 'Governance Review',
                        'path': '../../guided-demo/03-enrich-guardrails.md'}],
 'enforce_freshness': [{'title': 'Pipeline Execution',
                        'path': '../../guided-demo/02-run-pipeline.md'}],
 'enforce_profile_behavior': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/02-run-pipeline.md'},
                              {'title': 'Governance Review',
                               'path': '../../guided-demo/03-enrich-guardrails.md'}],
 'stop_if_failed': [{'title': 'Pipeline Execution',
                     'path': '../../guided-demo/02-run-pipeline.md'}],
 'write_catalogue_evidence': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/02-run-pipeline.md'},
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
