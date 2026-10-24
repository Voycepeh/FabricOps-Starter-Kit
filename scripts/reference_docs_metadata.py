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

SETUP_NOTEBOOK_USAGE_NOTE = """Use this at notebook startup to load configuration for the current workspace and capture the runtime information required by downstream Starter Kit notebooks.

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

METADATA_REFERENCE_OVERVIEW_INTRO = """FabricOps metadata is stored in one Metadata Lakehouse with two physical schemas:

- **Governance** stores authored governance definitions.
- **Engineering** stores technical observations, profiling, lineage, access observations, and runtime results.

`table_id` connects the same governed asset across both schemas. `contract_id` and `contract_version` identify one exact Data Contract version."""

METADATA_REFERENCE_AGREEMENT_CONTRACT_EXPLANATION = (
    "## Data Agreement versus Data Contract\n\n"
    "A Data Agreement is the overarching governance agreement between the accountable data producer and consumer parties, represented by their data stewards. It defines why the data may be shared, who is accountable, the permitted purpose and scope, usage conditions, and the agreement’s review period.\n\n"
    "A Data Contract is the immutable, versioned governed definition of one table. Authoring freezes its table identity, catalogue structure, processing definition, Enrichment, and active Guardrail expectations without an Agreement linkage. An Activated Pipeline links a complete successful Testing candidate to one exact Data Agreement version. Its manifest embeds reusable exact frozen contracts.\n\n"
    "One Data Agreement can govern multiple Activated Pipelines, each reusing frozen contracts.\n\n"
    "The agreement answers: Why and under what governance arrangement may this data be shared?\n\n"
    "The contract answers: Exactly what data will be delivered, in what structure, at what quality, and how reliably?"
)

METADATA_REFERENCE_MODEL_DIAGRAM_CAPTION = (
    "`METADATA_DATA_CONTRACT.contract_payload_json` is the JSON string column "
    "containing authored Guardrails, Enrichment and profiling policies for each contract version."
)

METADATA_TABLE_MODELS = {
    "METADATA_PIPELINE_REGISTRY": {
        "purpose": "Permanent UUIDv4 identity and environment-specific notebook bindings; registration never authorizes Live. A seeded Authority control row serializes binding transactions in this same table.",
        "grain": "One logical pipeline per environment, plus one serialization control row (central, *).",
        "primary_key": ["pipeline_id", "environment_name"], "foreign_keys": [],
        "relationships": [
            {"related_table": "METADATA_PIPELINE_RUN", "fields": ["pipeline_id", "environment_name"], "cardinality": "1:N", "statement": "One environment registration has many Pipeline Runs."},
            {"logical_entity": "Activated Pipeline", "cardinality": "1:N", "statement": "One registered Pipeline UUID has many immutable releases inside governance.METADATA_ACTIVATION_STATE; Activated Pipeline is a logical entity, not a separate Delta table."},
        ],
    },
    "METADATA_PIPELINE_RUN": {
        "purpose": "One complete logical run, exact table mappings, operation results, per-table profiling activity outcomes, warnings and pinned activation revision. Profiling completion joins persisted result snapshots; Grain Discovery and empty Frequency Profiling use minimal success markers in operation_summary_json.",
        "grain": "One Live pipeline execution attempt. Test results remain in memory.", "primary_key": ["run_id"],
        "foreign_keys": [{"local_field": "pipeline_id", "referenced_table": "METADATA_PIPELINE_REGISTRY", "referenced_field": "pipeline_id", "cardinality": "N:1", "statement": "Each run references one registered logical Pipeline UUID in its environment."}],
        "relationships": [{"cardinality": "N:1", "statement": "Each Live run references an approved Activated Pipeline release inside METADATA_ACTIVATION_STATE."}],
    },
    "METADATA_ACTIVATION_STATE": {
        "purpose": "Single atomic central authority for environment activation revisions, immutable approval history, table contracts, writer ownership, running execution reservations, transient notebook-rebind barriers and renewable profiling claims.",
        "grain": "One central authority row containing environment snapshots.",
        "primary_key": ["authority_id"], "foreign_keys": [],
        "relationships": [{"logical_entity": "Activated Pipeline", "cardinality": "1:N", "statement": "Each registered Pipeline UUID can have many immutable Activated Pipeline releases in the environment history. Activated Pipeline is a logical entity in snapshot_json, not a separate Delta table."},
                          {"logical_entity": "Live Pipeline Run", "cardinality": "1:N", "statement": "Each approved Activated Pipeline release authorizes many Live Pipeline Runs; registration alone never authorizes execution."}],
    },
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
            {"cardinality": "1:N", "statement": "One exact Data Agreement version can govern many Activated Pipeline versions."},
        ],
    },
    "METADATA_DATA_CONTRACT": {
        "purpose": "Reusable immutable frozen table definition with Enrichment, executable Guardrails and independent profiling policies. Agreement linkage belongs to Activated Pipeline.",
        "grain": "One Draft or Frozen version of one table contract; Frozen contents are immutable.",
        "primary_key": ["contract_id", "contract_version"],
        "foreign_keys": [{"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "A contract defines one Catalogue table."}],
        "relationships": [{"cardinality": "N:M", "related_table": "METADATA_ACTIVATION_STATE", "statement": "Many activated manifests may reuse this exact frozen contract; manifest references are not scalar foreign keys."}],
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
        "purpose": "Store source evidence observed by one logical pipeline for one governed target, including source_table_name and target_table_name captured for that observation. run_id joins METADATA_PIPELINE_RUN.run_id for planned executions; _activity_id retains the actual Fabric activity shared by different attempts. Legacy and standalone observations may have no run_id. observation_status=observed means the run captured the evidence but has not accepted it; observation_status=committed records accepted incremental progress, and drift_committed records the Source Drift baseline. Warehouse publication_observed and publication_committed rows store target-only retry receipts with empty source identity and no watermark; they also cover Full Read and source-free writes.",
        "grain": "One observed or committed partition-state row within one logical notebook, source table, target table, and observation; target-only Warehouse publication receipt rows have an empty source identity.",
        "primary_key": ["observation_id", "partition_value", "observation_status"],
        "foreign_keys": [
            {"local_field": "run_id", "referenced_table": "METADATA_PIPELINE_RUN", "referenced_field": "run_id", "cardinality": "N:1", "statement": "Planned source observations belong to the same logical pipeline attempt as run evidence; legacy and standalone observations may have no run record."},
            {"local_field": "source_table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "The source identity consumed by the successful write; empty for target-only Warehouse publication receipts."},
            {"local_field": "target_table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "The governed target whose successful write accepted the source state."},
        ],
        "relationships": [],
    },
    "METADATA_DATA_PROFILED": {
        "purpose": "See column-level profile metrics for a dataset snapshot. table_name and column_name record the names observed when written and do not follow later Catalogue renames.",
        "grain": "One observed column in one profiling snapshot.",
        "primary_key": ["profile_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many column profile snapshots can describe the same logical Catalogue table over time."},
            {"local_field": "column_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "column_id", "cardinality": "N:1", "statement": "Many profile snapshots can describe the same logical Catalogue column over time."},
        ],
        "relationships": [
            {"related_table": "METADATA_DATA_PROFILED_FREQUENCY", "fields": ["profile_id"], "cardinality": "1:N", "statement": "A combined standalone statistical Profile may link multiple ranked frequency-value rows through profile_id. Independently scheduled Frequency Profiling has its own snapshot and leaves profile_id null."},
        ],
    },
    "METADATA_DATA_PROFILED_FREQUENCY": {
        "purpose": "Frequency distributions retain Table ID, Column ID, environment, captured names and datatype. Independently scheduled Frequency Profiling owns its activity snapshot and leaves profile_id null; combined standalone profiling may link a statistical Profile. Captured names do not follow later renames.",
        "grain": "One ranked value for a column and frequency activity snapshot. The statistical Profile reference is optional.",
        "primary_key": ["frequency_id"],
        "foreign_keys": [
            {"local_field": "profile_id", "referenced_table": "METADATA_DATA_PROFILED", "referenced_field": "profile_id", "cardinality": "N:1", "statement": "Combined standalone profiling links Frequency rows to their parent statistical Profile through profile_id. Independently scheduled Frequency Profiling leaves profile_id null and retains Table ID, Column ID and its own activity snapshot."},
        ],
        "relationships": [
            {"related_table": "METADATA_DATA_PROFILED", "fields": ["profile_id"], "cardinality": "N:1", "statement": "Combined standalone distributions optionally reference their statistical Profile. Independent scheduled distributions leave that reference null."},
        ],
    },
    "METADATA_DATA_LINEAGE": {
        "purpose": "See which registered tables participated as sources and targets in pipeline activities; table_name records the name at the participation write while table_id remains stable. The current notebook's Lineage defines Data Contract resolution scope.",
        "grain": "One registered table participating as a source or target in one pipeline activity.",
        "primary_key": ["lineage_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many lineage participation records can refer to the same logical Catalogue table identity."},
        ],
        "relationships": [],
    },
    "METADATA_DATA_ACCESS": {
        "purpose": "See observable Workspace, OneLake Security, and SQL access for registered governed physical tables across configured Fabric data items; table_name records the Catalogue name matched at scan time. This is not an effective-access resolver.",
        "grain": "One observed access grant for one principal or access selector and one governed table within one access snapshot.",
        "primary_key": ["access_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many observed SQL permission rows can reference the same logical Catalogue table identity in an environment."},
        ],
        "relationships": [],
    },
    "METADATA_GUARDRAIL_RESULTS": {
        "purpose": "Store aggregate Live Guardrail summaries for exact participating contract versions, captured table name, readable rule context, and continuation decisions; caller-owned failed business rows are not persisted here. Captured context does not follow later table or rule changes.",
        "grain": "One persisted Live Guardrail outcome for one exact Data Contract version; Testing returns outcomes in memory only.",
        "primary_key": ["guardrail_result_id"],
        "foreign_keys": [
            {"local_field": "run_id", "referenced_table": "METADATA_PIPELINE_RUN", "referenced_field": "run_id", "cardinality": "N:1", "statement": "Planned execution results belong to one logical pipeline run; standalone historical results may have no run record."},
            {"local_field": "contract_id", "referenced_table": "METADATA_DATA_CONTRACT", "referenced_field": "contract_id", "cardinality": "N:1", "statement": "Together with contract_version, identifies the immutable payload containing the evaluated guardrail_rule_id and guardrail_version."},
            {"local_field": "contract_version", "referenced_table": "METADATA_DATA_CONTRACT", "referenced_field": "contract_version", "cardinality": "N:1", "statement": "Results retain the exact evaluated contract version and rule revision even after a new draft is authored."},
        ],
        "relationships": [],
    },
}

# Public entrypoints known to cause persisted metadata writes. Some entrypoints
# delegate the physical Delta write to internal helpers. Keep this separate from
# per-column provenance; do not list read-only access resolution as a writer.
METADATA_EXPLORER_WRITE_ENTRYPOINTS = {
    "METADATA_DATA_STEWARD": ["widget_render_data_steward"],
    "METADATA_DATA_AGREEMENT": ["widget_render_data_agreement"],
    "METADATA_DATA_CONTRACT": ["widget_data_contract"],
    "METADATA_ACTIVATION_STATE": ["widget_activate_pipeline", "setup_pipeline", "finalize_pipeline"],
    "METADATA_PIPELINE_REGISTRY": ["setup_pipeline"],
    "METADATA_PIPELINE_RUN": ["finalize_pipeline"],
    "METADATA_DATA_CATALOGUE": ["orchestrate_read", "orchestrate_write", "profile_table"],
    "METADATA_DATA_PROFILED": ["orchestrate_read", "orchestrate_write", "profile_table"],
    "METADATA_DATA_PROFILED_FREQUENCY": ["orchestrate_read", "orchestrate_write", "profile_table"],
    "METADATA_DATA_LINEAGE": ["orchestrate_read", "orchestrate_write", "pipeline_read"],
    "METADATA_SOURCE_OBSERVATION": ["orchestrate_read", "orchestrate_write"],
    "METADATA_GUARDRAIL_RESULTS": ["orchestrate_read", "orchestrate_write"],
    "METADATA_DATA_ACCESS": ["scan_workspace_access", "scan_onelake_access", "scan_sql_access"],
}

METADATA_REFERENCE_ORDER = [
    "METADATA_PIPELINE_REGISTRY",
    "METADATA_PIPELINE_RUN",
    "METADATA_DATA_STEWARD",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_CONTRACT",
    "METADATA_ACTIVATION_STATE",
    "METADATA_DATA_CATALOGUE",
    "METADATA_SOURCE_OBSERVATION",
    "METADATA_DATA_PROFILED",
    "METADATA_DATA_PROFILED_FREQUENCY",
    "METADATA_DATA_LINEAGE",
    "METADATA_DATA_ACCESS",
    "METADATA_GUARDRAIL_RESULTS",
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
        "table_name": ["fabricops_kit.data_contract.shared.create_contract_draft", "fabricops_kit.data_contract.shared.freeze_contract"],
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
        "__default__": ["fabricops_kit.widgets.widget_data_contract.widget_data_contract", "fabricops_kit.data_contract.shared.create_contract_draft", "fabricops_kit.data_contract.shared.save_contract_draft", "fabricops_kit.data_contract.shared.freeze_contract"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
    },
    "METADATA_ACTIVATION_STATE": {
        "__default__": ["fabricops_kit.activated_pipeline.shared.commit_activation_state"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
    },
    "METADATA_DATA_CATALOGUE": {
        "__default__": [
            "fabricops_kit.pipeline.shared.execute_table_profile",
            "fabricops_kit.pipeline.shared._catalogue_dataframe_from_profiled",
        ],
        "__audit__": ["fabricops_kit.pipeline.shared._audit_literal_columns", "fabricops_kit.pipeline.shared._persist_grain_candidates"],
        "profile_key_candidates_json": ["fabricops_kit.pipeline.shared._catalogue_dataframe_from_profiled", "fabricops_kit.pipeline.shared._persist_grain_candidates"],
        "data_type": ["fabricops_kit.pipeline.shared._catalogue_dataframe_from_profiled"],
        "table_id": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_table_id",
        ],
        "column_id": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_column_id",
        ],
        "table_name": ["fabricops_kit.pipeline.shared._canonical_profiled_dataframe"],
        "column_name": ["fabricops_kit.pipeline.shared._canonical_profiled_dataframe"],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
        ],
    },
    "METADATA_DATA_PROFILED": {
        "__default__": [
            "fabricops_kit.pipeline.shared.execute_table_profile",
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
        ],
        "__audit__": ["fabricops_kit.pipeline.shared._audit_literal_columns"],
        "table_id": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_table_id",
        ],
        "column_id": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
            "fabricops_kit.config.shared.build_column_id",
        ],
        "table_name": ["fabricops_kit.pipeline.shared._frequency_metadata_dataframe"],
        "column_name": ["fabricops_kit.pipeline.shared._frequency_metadata_dataframe"],
        "data_type": ["fabricops_kit.pipeline.shared._frequency_metadata_dataframe"],
        "environment_name": ["fabricops_kit.pipeline.shared._frequency_metadata_dataframe"],
        "schema_fingerprint": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
            "fabricops_kit.pipeline.shared._audit_literal_columns",
        ],
    },
    "METADATA_DATA_PROFILED_FREQUENCY": {
        "__default__": [
            "fabricops_kit.pipeline.shared.execute_table_profile",
            "fabricops_kit.pipeline.shared._frequency_metadata_dataframe",
            "fabricops_kit.pipeline.shared.execute_table_profile",
        ],
        "__audit__": ["fabricops_kit.pipeline.shared._audit_literal_columns"],
        "table_id": ["fabricops_kit.pipeline.shared._frequency_metadata_dataframe"],
        "column_id": [
            "fabricops_kit.pipeline.shared._frequency_metadata_dataframe",
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
        ],
        "profiled_at": [
            "fabricops_kit.pipeline.shared._frequency_metadata_dataframe",
            "fabricops_kit.pipeline.shared._canonical_profiled_dataframe",
        ],
    },
    "METADATA_DATA_LINEAGE": {
        "__default__": [
            "fabricops_kit.pipeline.orchestrate_read.orchestrate_read",
            "fabricops_kit.pipeline.orchestrate_write.orchestrate_write",
            "fabricops_kit.pipeline.shared.persist_lineage_participation",
            "fabricops_kit.pipeline.pipeline_read.pipeline_read",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "lineage_id": ["fabricops_kit.pipeline.shared.lineage_id"],
        "table_id": ["fabricops_kit.pipeline.shared.persist_lineage_participation"],
        "table_name": ["fabricops_kit.pipeline.shared.persist_lineage_participation"],
        "pipeline_role": ["fabricops_kit.pipeline.shared.persist_lineage_participation"],
    },
    "METADATA_DATA_ACCESS": {
        "__default__": [
            "fabricops_kit.access_scanner.scan_workspace_access.scan_workspace_access",
            "fabricops_kit.access_scanner.scan_workspace_access._access_rows",
            "fabricops_kit.access_scanner.scan_onelake_access.scan_onelake_access",
            "fabricops_kit.access_scanner.scan_onelake_access._access_rows",
            "fabricops_kit.access_scanner.scan_sql_access.scan_sql_access",
            "fabricops_kit.access_scanner.scan_sql_access._access_rows",
            "fabricops_kit.access_scanner.shared.persist_access_rows",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "access_id": [
            "fabricops_kit.access_scanner.scan_workspace_access._access_rows",
            "fabricops_kit.access_scanner.scan_onelake_access._access_rows",
            "fabricops_kit.access_scanner.scan_sql_access._access_rows",
        ],
        "table_id": [
            "fabricops_kit.access_scanner.scan_workspace_access._map_to_catalogue",
            "fabricops_kit.access_scanner.scan_onelake_access._map_to_catalogue",
            "fabricops_kit.access_scanner.scan_sql_access._map_to_catalogue",
        ],
        "table_name": ["fabricops_kit.access_scanner.scan_workspace_access._access_rows", "fabricops_kit.access_scanner.scan_onelake_access._access_rows", "fabricops_kit.access_scanner.scan_sql_access._access_rows"],
        "access_snapshot_id": [
            "fabricops_kit.access_scanner.scan_workspace_access.scan_workspace_access",
            "fabricops_kit.access_scanner.scan_onelake_access.scan_onelake_access",
            "fabricops_kit.access_scanner.scan_sql_access.scan_sql_access",
        ],
        "permission_source": [
            "fabricops_kit.access_scanner.shared.workspace_role_observations",
            "fabricops_kit.access_scanner.shared.onelake_role_observations",
            "fabricops_kit.access_scanner.scan_sql_access._scan_targets",
        ],
        "database_name": [
            "fabricops_kit.access_scanner.scan_workspace_access._access_rows",
            "fabricops_kit.access_scanner.scan_onelake_access._access_rows",
            "fabricops_kit.access_scanner.scan_sql_access._scan_targets",
        ],
        "schema_name": [
            "fabricops_kit.access_scanner.scan_workspace_access._access_rows",
            "fabricops_kit.access_scanner.scan_onelake_access._access_rows",
            "fabricops_kit.access_scanner.scan_sql_access._scan_targets",
        ],
        "object_name": [
            "fabricops_kit.access_scanner.scan_workspace_access._access_rows",
            "fabricops_kit.access_scanner.scan_onelake_access._access_rows",
            "fabricops_kit.access_scanner.scan_sql_access._scan_targets",
        ],
        "object_type": [
            "fabricops_kit.access_scanner.scan_workspace_access._access_rows",
            "fabricops_kit.access_scanner.scan_onelake_access._access_rows",
            "fabricops_kit.access_scanner.scan_sql_access._scan_targets",
        ],
    },
    "METADATA_GUARDRAIL_RESULTS": {
        "__default__": [
            "fabricops_kit.pipeline.orchestrate_read.orchestrate_read",
            "fabricops_kit.pipeline.orchestrate_write.orchestrate_write",
            "fabricops_kit.pipeline.check_schema.check_schema",
            "fabricops_kit.pipeline.check_freshness.check_freshness",
            "fabricops_kit.pipeline.check_source_drift.check_source_drift",
            "fabricops_kit.pipeline.check_dq.check_dq",
            "fabricops_kit.pipeline.shared.write_guardrail_result_row",
            "fabricops_kit.pipeline.shared.check_dq_runtime",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_result_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "table_name": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "guardrail_type": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "rule_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "rule_type": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "action": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "run_id": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "environment_name": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "status": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "can_continue": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "severity": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "reason": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
        "result_payload_json": ["fabricops_kit.pipeline.shared.write_guardrail_result_row", "fabricops_kit.pipeline.shared.check_dq_runtime"],
    },
    "METADATA_PIPELINE_RUN": {
        "__default__": ["fabricops_kit.pipeline.shared.persist_pipeline_run"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
    },
    "METADATA_SOURCE_OBSERVATION": {
        "__default__": [
            "fabricops_kit.pipeline.orchestrate_read.orchestrate_read",
            "fabricops_kit.pipeline.orchestrate_write.orchestrate_write",
            "fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "run_id": ["fabricops_kit.pipeline.shared.capture_source_observation", "fabricops_kit.pipeline.shared.stage_pipeline_write_observations", "fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
        "source_table_id": [
            "fabricops_kit.pipeline.shared.commit_pipeline_write_success",
            "fabricops_kit.config.shared.build_table_id",
        ],
        "target_table_id": ["fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
        "source_table_name": ["fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
        "target_table_name": ["fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
        "observation_status": ["fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
        "publication_payload_json": ["fabricops_kit.pipeline.shared.stage_pipeline_write_observations", "fabricops_kit.pipeline.shared.commit_pipeline_write_success"],
    },
}

USAGE_NOTE_BY_FUNCTION = {
    "setup_notebook": SETUP_NOTEBOOK_USAGE_NOTE,
    "setup_metadata_tables": SETUP_METADATA_USAGE_NOTE,
}


MODULE_DOCS_METADATA = [
 {'module_name': 'consumption.create_data_agent', 'visibility': 'public', 'module_summary': 'Creates and configures a native single-table Microsoft Fabric Data Agent from governed context.', 'sidebar_group': '7. Consumption', 'sidebar_include': False},
 {'module_name': 'config',
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

 {'module_name': 'widgets.widget_data_contract',
  'visibility': 'public',
  'module_summary': 'Owns the unified Data Contract authoring experience.',
  'sidebar_group': '1. Governance steward',
  'sidebar_include': False},
 {'module_name': 'access',
  'visibility': 'public',
  'module_summary': 'Owns observed SQL permission inventory and Catalogue table linkage.',
  'sidebar_group': '3. Data engineer',
  'sidebar_include': True},
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
  'segments': [{'symbols': ['FabricStore', 'PathConfig', 'GovernanceConfig', 'DataAgreementConfig', 'FrameworkConfig', 'setup_metadata_tables'],
                'title': 'Environment setup'}],
  'template_path': 'templates/notebooks/00_env_config.ipynb'},
 {'notebook_key': '00C_demo_setup',
  'notebook_label': '`00C_demo_setup`',
  'segment_intro': 'Guided Demo setup that demonstrates the public FabricOps I/O helpers and seeds managed source tables.',
  'segments': [{'symbols': ['read_lakehouse_csv',
                            'read_lakehouse_excel',
                            'read_lakehouse_json',
                            'read_lakehouse_parquet',
                            'read_lakehouse_table',
                            'read_warehouse_query',
                            'read_warehouse_table',
                            'write_lakehouse_table',
                            'write_warehouse_table'],
                'title': 'Prepare Guided Demo data with FabricOps I/O'}],
  'template_path': 'templates/DemoData/00C_demo_setup.ipynb'},
 {'notebook_key': '01_governance',
  'notebook_label': '`01_governance`',
  'segment_intro': 'Persistent Governance lifecycle before and after Engineering evidence production.',
  'segments': [{'symbols': ['setup_notebook', 'widget_render_data_steward',
                            'widget_render_data_agreement',
                            'widget_data_contract'],
                'title': 'Agreement, Data Contract authoring, and activation'}],
  'template_path': 'templates/notebooks/01_governance.ipynb'},
 {'notebook_key': '02_pipeline',
  'notebook_label': '`02_pipeline`',
  'segment_intro': 'Simple v0.2 Lakehouse-first pipeline with complete-table SQL endpoint read and '
                   'write alternatives.',
  'segments': [{'symbols': ['orchestrate_read'],
                'title': 'Run the standard governed Read lifecycle'},
               {'symbols': ['orchestrate_write'],
                'title': 'Run the standard governed Write lifecycle'}],
  'template_path': 'templates/notebooks/02_pipeline.ipynb'},
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
 {'kind': 'function', 'module': 'consumption.create_data_agent', 'function_type': 'callable',
  'symbol_name': 'create_data_agent', 'template_notebook': '', 'template_segment': 'Create Data Agent',
  'summary_override': 'Create and configure one native Fabric Data Agent from an activated Production table.',
  'purpose': 'Complete the governed single-table Step 7 handoff without manually composing context or instructions.', 'use_when': 'Use to create a Data Agent from one activated Production table.',
  'do_not_use_when': 'Do not use for multi-table agents, relationship authoring, evaluation, or automatic publication.',
  'parameters': 'table_id, target_workspace_id, display_name, and optional description and Fabric runtime dependencies.',
  'returns': 'Agent and datasource identities plus useful configuration status.', 'raises': 'Raises for invalid governed sources, authentication, permission, REST, malformed response, and LRO failures.',
  'side_effects': 'Creates a staging Data Agent and datasource, selects one table, and applies instructions.',
  'fabric_context': 'Requires supported Fabric capacity, source access, target workspace access, Data Agent create/configure permission, and the Preview Data Agent REST API.',
  'ai_verification': 'Review the deterministic instructions and test the native agent before publication.',
  'preferred_example': 'result = create_data_agent(table_id, target_workspace_id=workspace_id, display_name="Governed orders")',
  'related_functions': []},
 {'kind': 'function',
  'module': 'access_scanner.scan_effective_access',
  'function_type': 'callable',
  'summary_override': 'Discover visible Fabric data items and resolve effective table access to individual users.',
  'purpose': 'Answer which actual person can access which discovered Fabric table, through which supported permission surface, and why.',
  'symbol_name': 'scan_effective_access',
  'template_notebook': 'ad hoc Fabric notebook',
  'template_segment': 'Effective data access',
  'use_when': 'Use when you have caller-supplied identity and group-membership mappings and need a read-only person-level Workspace, SQL, and OneLake access report.',
  'do_not_use_when': 'Do not treat UNVERIFIED observations or an empty access result as proof of effective access or denial; always inspect coverage.',
  'parameters': 'identity_map_df with Object ID and readable identity fields, and group_membership_df with group-to-member Object ID edges.',
  'returns': 'Dictionary with person/table/surface observations labelled CONFIRMED, UNVERIFIED, or NOT_EFFECTIVE, plus explicit coverage limitations.',
  'raises': 'Raises ValueError for invalid mapping DataFrame schemas or mismatched Spark sessions; platform discovery failures are returned in coverage.',
  'side_effects': 'Reads visible Fabric REST and SQL permission metadata only; it does not change permissions or persist results.',
  'fabric_context': 'Runs in Microsoft Fabric Spark with the caller identity and its existing permissions; no Graph token, metadata initialization, persistence target, or Fabric Admin API is required.',
  'ai_verification': 'Use only CONFIRMED effective permissions as established access; review UNVERIFIED observations with coverage and preserve SQL and OneLake as distinct surfaces.',
  'preferred_example': 'result = scan_effective_access(identity_map_df=identity_map_df, group_membership_df=group_membership_df)',
  'related_functions': ['scan_workspace_access', 'scan_sql_access', 'scan_onelake_access'],
  'expanded_purpose': 'Uses caller-scoped Workspace and Catalog Search APIs to discover visible and directly shared Lakehouses, Warehouses, and tables; combines item access with Workspace, SQL, and OneLake data permissions; distinguishes SQL authorization modes; recursively expands security groups; applies denies conservatively; and preserves every contributing path.',
  'when_to_use': 'Use for an auditable, non-persisted effective data access review based on the scopes visible to the caller.',
  'glossary_terms': ['effective data access', 'data access', 'access control'],
  'return_interpretation': 'Filter result["access"] to access_verification_status == "CONFIRMED" for established effective permissions; review UNVERIFIED and NOT_EFFECTIVE observations with result["coverage"].',
  'common_failure_causes': ['The caller cannot list workspace role assignments or OneLake roles.', 'Direct item assignments or the SQL endpoint access mode cannot be established through supported read-only interfaces.', 'The identity or membership mapping is incomplete.', 'DefaultReader differs from its assumed baseline or a permission is restricted.'],
  'related_guides': [{'title': 'Scan Effective Data Access', 'path': '../../solutions/effective-data-access.md'}]},
 {'kind': 'function',
  'module': 'access_scanner.scan_workspace_access',
  'function_type': 'callable',
  'summary_override': 'Scan Fabric workspace role assignments and expand them across registered governed tables.',
  'purpose': 'Observe table access inherited from Admin, Member, Contributor, and Viewer workspace roles.',
  'symbol_name': 'scan_workspace_access',
  'template_notebook': '90_access_inventory (planned)',
  'template_segment': 'Access inventory',
  'use_when': 'Use when you need the workspace-role path into governed table access for configured Fabric items.',
  'do_not_use_when': 'Do not use as an effective-access resolver; OneLake and SQL access are scanned separately.',
  'parameters': 'catalogue_df, configured target keys, optional environment_name, optional access_snapshot_id, optional access_token, persist flag, and optional FabricOps context.',
  'returns': 'Dictionary with raw workspace observations, normalized METADATA_DATA_ACCESS rows, and unmatched role assignments.',
  'raises': 'Raises for invalid targets, Fabric REST authentication or permission failures, and Spark mapping or persistence failures.',
  'side_effects': 'Reads Fabric workspace role assignments and appends normalized rows to METADATA_DATA_ACCESS by default; it never changes workspace permissions.',
  'fabric_context': 'Requires Member or higher access to scanned workspaces plus a Fabric REST token with the required Workspace scope.',
  'ai_verification': 'Confirm the configured targets belong to the intended workspaces and use one shared access_snapshot_id when combining this scan with OneLake and SQL scans.',
  'preferred_example': 'result = scan_workspace_access(catalogue_df, targets=["Silver", "Gold"])',
  'related_functions': ['scan_onelake_access', 'scan_sql_access'],
  'expanded_purpose': 'Scans each unique configured workspace once, preserves the original workspace role, normalizes Viewer to READ and Admin/Member/Contributor to READWRITE, and expands that access across active registered tables in scanned items.',
  'when_to_use': 'Use for repeatable workspace-role access inventory snapshots.',
  'glossary_terms': ['data access', 'metadata catalogue'],
  'return_interpretation': 'Use result["access"] as the normalized workspace-derived table access snapshot and result["unmatched"] to identify role assignments with no registered scanned table.',
  'common_failure_causes': ['The caller is below Workspace Member.', 'The token lacks Workspace.Read.All or Workspace.ReadWrite.All.', 'Configured targets do not match active Catalogue physical identities.'],
  'related_guides': [{'title': 'Metadata reference', 'path': '../../reference/metadata/metadata_data_access.md'}]},
 {'kind': 'function',
  'module': 'access_scanner.scan_onelake_access',
  'function_type': 'callable',
  'summary_override': 'Scan OneLake Security roles and map Lakehouse table access to canonical FabricOps table identities.',
  'purpose': 'Observe table access granted through OneLake Security roles for configured Lakehouses.',
  'symbol_name': 'scan_onelake_access',
  'template_notebook': '90_access_inventory (planned)',
  'template_segment': 'Access inventory',
  'use_when': 'Use when you need the OneLake Security path into governed Lakehouse table access.',
  'do_not_use_when': 'Do not use for Warehouse targets or as a full effective-access resolver.',
  'parameters': 'catalogue_df, configured Lakehouse target keys, optional environment_name, optional access_snapshot_id, optional access_token, persist flag, and optional FabricOps context.',
  'returns': 'Dictionary with raw OneLake observations, normalized METADATA_DATA_ACCESS rows, and unmatched paths.',
  'raises': 'Raises for non-Lakehouse targets, Fabric REST authentication or permission failures, unsafe continuation hosts, and Spark mapping or persistence failures.',
  'side_effects': 'Reads OneLake Security role definitions and appends normalized rows to METADATA_DATA_ACCESS by default; it never changes OneLake permissions.',
  'fabric_context': 'Requires configured Lakehouse targets and a Fabric REST token with the required OneLake scope.',
  'ai_verification': 'Inspect automatic Fabric item-access selectors separately from explicit Entra members and use one shared access_snapshot_id when combining scans.',
  'preferred_example': 'result = scan_onelake_access(catalogue_df, targets="Silver")',
  'related_functions': ['scan_workspace_access', 'scan_sql_access'],
  'expanded_purpose': 'Preserves explicit Entra members and automatic item-access selectors, expands supported OneLake table and schema paths to registered table_id values, and keeps unmatched Files or unknown paths visible.',
  'when_to_use': 'Use for repeatable OneLake Security access inventory snapshots.',
  'glossary_terms': ['data access', 'metadata catalogue'],
  'return_interpretation': 'Use result["access"] as the normalized OneLake table-level snapshot, result["observations"] for raw role detail, and result["unmatched"] for paths outside registered governed tables.',
  'common_failure_causes': ['A target is not a Lakehouse.', 'The token lacks OneLake.Read.All or OneLake.ReadWrite.All.', 'A role path does not map to an active registered table.'],
  'related_guides': [{'title': 'Metadata reference', 'path': '../../reference/metadata/metadata_data_access.md'}]},
 {'kind': 'function',
  'module': 'access_scanner.scan_sql_access',
  'function_type': 'callable',
  'summary_override': 'Scan observable SQL permissions for registered governed physical tables across configured Fabric workspace data items.',
  'purpose': 'Collect direct and explicit role-based SQL permission evidence and resolve it to canonical FabricOps table_id values.',
  'symbol_name': 'scan_sql_access',
  'template_notebook': '90_access_inventory (planned)',
  'template_segment': 'Access inventory',
  'use_when': 'Use when you need the SQL endpoint path into governed table access for registered Warehouse or Lakehouse tables.',
  'do_not_use_when': 'Do not use as a complete Fabric authorization inventory; workspace and OneLake access are scanned separately.',
  'parameters': 'catalogue_df, one or more configured workspace data item target keys, optional environment_name, optional access_snapshot_id, optional spark_session, persist flag, and optional FabricOps context.',
  'returns': 'Dictionary with normalized METADATA_DATA_ACCESS rows and unmatched observed SQL permissions.',
  'raises': 'Raises ValueError when no valid workspace data item target is supplied and propagates configured SQL endpoint read, Spark, or persistence errors.',
  'side_effects': 'Reads SQL permission catalogue views and appends normalized rows to METADATA_DATA_ACCESS by default; it never changes SQL permissions.',
  'fabric_context': 'Requires configured workspace data item targets and a Catalogue DataFrame for the same FabricOps environment.',
  'ai_verification': 'Confirm configured targets resolve to the physical items represented by canonical Catalogue table_id values, inspect unmatched observations, and use one shared access_snapshot_id when combining scans.',
  'preferred_example': 'result = scan_sql_access(catalogue_df, targets="warehouse", spark_session=spark)',
  'related_functions': ['scan_workspace_access', 'scan_onelake_access', 'read_warehouse_query'],
  'expanded_purpose': 'Uses configured Warehouse and Lakehouse SQL analytics endpoints, preserves direct versus role-based permission evidence, expands schema/database scope across registered tables, and keeps unresolved observations visible.',
  'when_to_use': 'Use for repeatable SQL permission inventory snapshots that should link back to governed FabricOps table identities.',
  'glossary_terms': ['data access', 'metadata catalogue'],
  'return_interpretation': 'Use result["access"] as the governed table-level snapshot and review result["unmatched"] for observed SQL permissions that were not registered in the Catalogue.',
  'common_failure_causes': ['A workspace data item target is not configured or accessible.', 'Canonical Catalogue physical identity does not match the observed SQL object.', 'The scanning identity cannot read the SQL permission catalogue views.'],
  'related_guides': [{'title': 'Metadata reference', 'path': '../../reference/metadata/metadata_data_access.md'}]},
 {'kind': 'class',
  'module': 'config.shared',
  'function_type': 'class',
  'summary_override': 'Configured Fabric lakehouse or warehouse connection details.',
  'purpose': 'Describe one configured Fabric store used by path routing.',
  'symbol_name': 'FabricStore',
  'use_when': 'Use in 00_env_config path mappings to define lakehouse or warehouse targets.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'env, workspace_id, item_id, kind, schema_enabled, schema, and optional keyword-only name (physical Fabric item name; defaults to the logical alias for Warehouse execution).',
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
  'purpose': 'Define information-classification labels, AI Enrichment options, and enrichment widget custom fields.',
  'symbol_name': 'GovernanceConfig',
  'use_when': 'Use in 00_env_config to customize governance review options.',
  'when_to_use': ['Use through the supported FabricOps root import surface.'],
  'parameters': 'required_classification, information-classification labels, optional AI Enrichment prompts, and enrichment widgets.',
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
 'module': 'pipeline.pipeline_read',
 'function_type': 'callable',
 'summary_override': 'Read one governed pipeline source through its configured Fabric store.',
 'symbol_name': 'pipeline_read',
 'template_notebook': '02_pipeline',
 'template_segment': 'Source read capability',
 'use_when': 'Use for an explicit full source read or a target-aware incremental source read.',
 'do_not_use_when': 'Use orchestrate_read for the standard governed Read lifecycle, including Guardrails; use foundational file readers for raw Lakehouse Files.',
 'parameters': 'Canonical source table_id or configured store, schema, and table_name; explicit read_mode; target_table_id required for incremental mode; optional full-read Warehouse query.',
 'returns': 'DataFrame, canonical source table_id, read mode, custom-query and contract signals, has_data/should_process, and a compact resolved scope summary.',
 'side_effects': 'Captures current Source Observation state for governed full reads and stages target-specific incremental state; accepted progress advances only after successful target publication.',
 'preferred_example': 'source = pipeline_read(store="Bronze", schema="demo", table_name="orders")',
 'related_functions': ['orchestrate_read', 'read_lakehouse_table', 'read_warehouse_table', 'read_warehouse_query']},
 {'kind': 'function',
 'module': 'pipeline.orchestrate_read',
 'function_type': 'callable',
 'summary_override': 'Run the observable standard governed source lifecycle.',
 'symbol_name': 'orchestrate_read',
 'template_notebook': '02_pipeline',
 'template_segment': 'Standard Read orchestration',
 'use_when': 'Use for the normal governed Read path before project PySpark transformation.',
 'do_not_use_when': 'Use lower-level capabilities directly when intentionally composing a non-standard lifecycle.',
 'parameters': 'Source coordinates, read strategy and query options; execution context is internal.',
 'returns': 'Governed source DataFrame and table identity together with every stage result.',
 'side_effects': 'Test retains diagnostics in memory until finalize_pipeline returns in-memory Test results; business publication remains disabled. Live commits Guardrail Results and full-read '
                 'Catalogue/Profile metadata.',
 'preferred_example': 'source = orchestrate_read(store="Bronze", schema="demo", '
                      'table_name="orders")',
 'related_functions': ['orchestrate_write', 'profile_table']},
 {'kind': 'function',
 'module': 'pipeline.orchestrate_write',
 'function_type': 'callable',
 'summary_override': 'Run the observable standard governed target lifecycle.',
 'symbol_name': 'orchestrate_write',
 'template_notebook': '02_pipeline',
 'template_segment': 'Standard Write orchestration',
 'use_when': 'Use for the normal governed publication path after project PySpark transformation.',
 'do_not_use_when': 'Use lower-level capabilities directly when intentionally composing a non-standard lifecycle.',
 'parameters': 'Transformed DataFrame, target coordinates '
               'and strategy.',
 'returns': 'Prepared input, Guardrail outcomes, execution mode and actual publication/persistence status.',
 'side_effects': 'Test retains diagnostics in memory, including after finalize_pipeline. Live publishes and commits metadata at existing '
                 'lifecycle boundaries.',
 'preferred_example': 'result = orchestrate_write(transformed_df, '
                      'store="Silver", schema="demo", table_name="orders", write_mode="overwrite")',
 'related_functions': ['orchestrate_read', 'profile_table']},
 {'kind': 'function',
  'module': 'pipeline.resolve_table_id',
  'function_type': 'callable',
  'summary_override': 'Resolve deterministic target identity before its first Development write.',
  'symbol_name': 'resolve_table_id',
  'template_notebook': '02_pipeline',
  'template_segment': 'Target configuration',
  'use_when': 'Use when target Guardrails need canonical target identity before the physical target exists.',
  'do_not_use_when': 'Do not use it to register a target, resolve governed processing, or perform physical IO.',
  'parameters': 'Configured physical target, optional schema, and table name.',
  'returns': 'Deterministic canonical table_id for the configured physical identity.',
  'side_effects': 'None; it reads active Fabric configuration without requiring Catalogue or Data Contract records.',
  'preferred_example': 'table_id = resolve_table_id(store="Silver", schema="dbo", table_name="orders")',
  'related_functions': ['orchestrate_write', 'orchestrate_read']},
 {'kind': 'function',
  'module': 'config.setup_notebook',
  'function_type': 'callable',
  'summary_override': 'Shared environment setup and runtime validation for notebook templates.',
  'purpose': 'Prepare a FabricOps notebook by validating configuration, resolving environment '
             'targets, and returning reusable runtime context.',
  'symbol_name': 'setup_notebook',
  'template_notebook': '00_env_config',
  'template_segment': 'Environment bootstrap',
  'use_when': 'Use at the start of a Governance notebook to load and validate FabricOps '
              'configuration, resolve required targets, and capture runtime context before other '
              'helpers run.',
  'when_to_use': ['Starting a FabricOps notebook with workspace configuration',
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
  'fabric_context': 'Automatic setup requires Fabric currentWorkspaceId and access to 00_env_config. '
                    'config_workspace_id optionally selects a remote notebook workspace; loading defaults locally.',
  'ai_verification': 'Verify the returned context is ready before generating downstream notebook '
                     'code and confirm required targets resolve for the selected env.',
  'preferred_example': 'context = setup_notebook(CONFIG, env="Sandbox", '
                       'required_targets=["Bronze", "Silver", "Gold", "Metadata"], notebook_name="00_env_config")',
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'},
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'},
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a Delta table from a configured Fabric lakehouse target.',
  'symbol_name': 'read_lakehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading managed Delta tables from configured Lakehouse Tables storage.',
  'do_not_use_when': 'Do not use for lakehouse Files paths or warehouse SQL serving-engine reads.',
  'parameters': 'table_name, store, optional schema, optional spark_session, optional context, and Spark Delta reader options.',
  'returns': 'Spark DataFrame loaded from the configured Lakehouse Delta table path.',
  'raises': 'Raises ValueError for unsafe names or non-lakehouse targets and RuntimeError when Spark is unavailable.',
  'side_effects': 'Reads data only; it does not write metadata, files, or tables.',
  'fabric_context': 'Routes reads through configured FabricOps Lakehouse targets instead of an attached/default lakehouse.',
  'ai_verification': 'Verify the target, schema, and table are intended Lakehouse inputs before generating calls.',
  'preferred_example': 'orders_df = read_lakehouse_table("orders", store="Bronze", schema="demo")',
  'related_functions': ['write_lakehouse_table', 'read_lakehouse_csv', 'read_warehouse_query'],
  'expanded_purpose': 'Resolves the configured Lakehouse Tables path, then delegates to Spark Delta reader with any supplied reader options.',
  'when_to_use': 'Use near the start of a notebook when Spark processing needs a full Lakehouse table DataFrame.',
  'glossary_terms': ['source data', 'metadata lakehouse'],
  'return_interpretation': 'The returned DataFrame represents the resolved Lakehouse table.',
  'common_failure_causes': ['The target or table name is misspelled.', 'The selected environment does not define the requested lakehouse target.', 'Spark cannot access the table.', 'The caller lacks permission to read the lakehouse.'],
  'related_guides': [{'title': 'Templates',
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Write a Spark DataFrame to a configured Fabric lakehouse Delta table.',
  'symbol_name': 'write_lakehouse_table',
  'template_notebook': '02_pipeline / examples',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when publishing Spark DataFrames to configured Lakehouse Tables storage.',
  'do_not_use_when': 'Do not use for warehouse publishing or metadata mutation outside configured metadata routing.',
  'parameters': 'df, table_name, store, optional schema, mode, partitioning/repartitioning options, writer options, verbose, and context.',
  'returns': 'None; the DataFrame is written to the configured Lakehouse Delta table path.',
  'raises': 'Raises ValueError for unsafe names, invalid write modes, or non-lakehouse targets.',
  'side_effects': 'Writes data to the configured Lakehouse Delta table path.',
  'fabric_context': 'Routes writes through configured FabricOps Lakehouse targets instead of an attached/default lakehouse.',
  'ai_verification': 'Verify guardrails passed, target/schema/table routing is intentional, and write mode is safe before generating calls.',
  'preferred_example': 'write_lakehouse_table(orders_df, "orders_clean", store="Silver", schema="demo", mode="overwrite")',
  'related_functions': ['read_lakehouse_table', 'write_warehouse_table'],
  'expanded_purpose': 'Resolves the configured Lakehouse Tables path, then delegates to Spark Delta writer with any supplied writer options.',
  'when_to_use': 'Use after transformations and guardrail checks when the destination is a Lakehouse table.',
  'glossary_terms': ['target table', 'guardrails', 'metadata lakehouse'],
  'return_interpretation': 'No value is returned; successful completion means the configured Lakehouse write was submitted.',
  'common_failure_causes': ['Guardrails were skipped before a target write.', 'The target lakehouse is not configured for the environment.', 'The write mode is unsupported for the destination.', 'The caller lacks write permission or Spark cannot create the table.'],
  'related_guides': [{'title': 'Templates',
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a CSV file from a configured Fabric-resolved path through Spark CSV.',
  'symbol_name': 'read_lakehouse_csv',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a CSV file from a configured Fabric-resolved path.',
  'do_not_use_when': 'Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL '
                     'tables.',
  'parameters': 'relative_path, store, optional spark_session, optional context, header flag, and Spark CSV reader options.',
  'returns': 'Spark DataFrame loaded from the Fabric-resolved CSV path.',
  'raises': 'Raises ValueError for invalid file paths and configuration/Spark errors when the file '
            'cannot be read.',
  'side_effects': 'Reads from the configured Fabric-resolved path; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify relative_path is a configured Fabric-resolved file path, then check row count and schema '
                     'after reading.',
  'preferred_example': 'orders_df = read_lakehouse_csv("incoming/orders.csv", inferSchema=True)',
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read JSON data from a configured Lakehouse Files path through Spark JSON.',
  'symbol_name': 'read_lakehouse_json',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading JSON files or folders from a configured Lakehouse Files path.',
  'do_not_use_when': 'Do not use for managed Delta tables, CSV files, Excel files, Parquet files, or warehouse SQL tables.',
  'parameters': 'relative_path, store, optional spark_session, optional context, and Spark JSON reader options.',
  'returns': 'Lazy Spark DataFrame backed by the Fabric-resolved JSON path.',
  'raises': 'Raises ValueError for invalid file paths and configuration/Spark errors when the path cannot be read.',
  'side_effects': 'Constructs a Spark JSON read plan; it does not write metadata, tables, or files.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name.',
  'ai_verification': 'Verify the configured target and relative path, then check schema and rows when an action evaluates the DataFrame.',
  'preferred_example': 'df = read_lakehouse_json(relative_path="incoming/events.json", store="Bronze", multiLine=True, spark_session=spark)',
  'related_functions': ['read_lakehouse_csv', 'read_lakehouse_parquet', 'read_lakehouse_table'],
  'expanded_purpose': 'Resolves the configured Lakehouse Files path, then delegates file or folder parsing and all JSON reader options to Spark.',
  'when_to_use': 'Use for JSON Lines or multi-line JSON source ingestion that should follow configured Fabric target routing.',
  'glossary_terms': ['source data', 'notebook template'],
  'return_interpretation': 'The returned DataFrame is lazy and reflects Spark JSON parsing behavior and supplied options.',
  'common_failure_causes': ['The path is missing or inaccessible.', 'JSON content does not match the supplied Spark options.', 'The configured Lakehouse target is unavailable.', 'Some Spark errors are deferred until an action evaluates the DataFrame.'],
  'related_guides': [{'title': 'Templates', 'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a Parquet path from a configured Fabric-resolved path through Spark Parquet.',
  'symbol_name': 'read_lakehouse_parquet',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a Parquet file or path from a configured Fabric lakehouse Files '
              'path.',
  'do_not_use_when': 'Do not use for Delta tables, CSV files, Excel files, or warehouse SQL '
                     'tables.',
  'parameters': 'relative_path, store, verbose flag, optional spark_session, optional context, and Spark Parquet reader options.',
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
  'preferred_example': 'orders_df = read_lakehouse_parquet("curated/orders/", spark_session=spark)',
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read an Excel file from a configured Fabric-resolved path through pandas.read_excel.',
  'symbol_name': 'read_lakehouse_excel',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading .xlsx files from a configured Fabric-resolved path, '
              'especially small reference files, mapping tables, or manually maintained business '
              'inputs.',
  'do_not_use_when': 'Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL '
                     'tables.',
  'parameters': 'config, env, store, relative_path, optional sheet_name, optional spark_session, '
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read a table from a configured Fabric warehouse target.',
  'symbol_name': 'read_warehouse_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when reading a table from a configured Fabric warehouse target.',
  'do_not_use_when': 'Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or '
                     'Excel paths.',
  'parameters': 'schema, table_name, store, optional spark_session, optional context, and Fabric Warehouse connector reader options.',
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'io',
  'function_type': 'callable',
  'summary_override': 'Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.',
  'symbol_name': 'read_warehouse_query',
  'template_notebook': '02_pipeline',
  'template_segment': 'Fabric IO',
  'use_when': 'Use when projection or filtering should run in the Fabric Warehouse SQL serving engine before Spark receives rows.',
  'do_not_use_when': 'Do not use for lakehouse Delta tables, lakehouse Files paths, or non-SELECT warehouse mutations.',
  'parameters': 'query, store, optional spark_session, optional context, and Fabric Warehouse connector reader options.',
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
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
  'parameters': 'df, schema, table_name, store, write mode, optional Spark repartition_by value, optional connector writer options, and optional context.',
  'returns': 'None; the DataFrame is written to the configured warehouse table.',
  'raises': 'Raises configuration, Spark connector, or warehouse write errors when the '
            'target/table cannot be written.',
  'side_effects': 'Writes data to a Fabric warehouse table using the selected mode.',
  'fabric_context': 'Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the '
                    'intended env name; never hardcode Fabric workspace or item identifiers.',
  'ai_verification': 'Verify guardrails passed, confirm schema/table routing from CONFIG, and '
                     'check the intended write mode before calling.',
  'preferred_example': 'write_warehouse_table(orders_df, "dbo", "orders", mode="append")',
  'related_functions': ['read_warehouse_table', 'read_warehouse_query'],
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
                      'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}]},
 {'kind': 'function',
  'module': 'pipeline',
  'function_type': 'callable',
  'summary_override': 'Profile a Spark DataFrame or complete governed table and return statistical and frequency results.',
  'symbol_name': 'profile_table',
  'template_notebook': '02_pipeline',
  'template_segment': 'Profiling',
  'use_when': 'Use for non-persistent DataFrame profiling or governed table profiling and metadata persistence.',
  'do_not_use_when': 'Do not associate a partial incremental batch with a complete-source governed profile.',
  'parameters': 'keyword-only dataframe or governed identity, plus optional frequency controls.',
  'returns': 'Dictionary with profile (statistical Spark DataFrame) and frequency_profile (frequency Spark DataFrame or None).',
  'raises': 'Raises ValueError for missing or conflicting identity inputs and invalid frequency settings.',
  'side_effects': 'Writes METADATA_DATA_CATALOGUE, METADATA_DATA_PROFILED, and METADATA_DATA_PROFILED_FREQUENCY only when governed identity is supplied.',
  'fabric_context': 'Governed mode requires 00_env_config; DataFrame-only mode does not resolve or write metadata.',
  'ai_verification': 'Verify whether persistence is intended and provide table_id explicitly when associating a supplied DataFrame with a governed table.',
  'preferred_example': 'result = profile_table(dataframe=orders_df)\nstatistical_profile = result["profile"]',
  'related_functions': ['orchestrate_read', 'orchestrate_write'],
  'expanded_purpose': 'Profiles an exact supplied DataFrame or complete physical table. Governed identities persist METADATA_DATA_CATALOGUE, METADATA_DATA_PROFILED, and METADATA_DATA_PROFILED_FREQUENCY; DataFrame-only calls remain in memory.',
  'when_to_use': 'Use dataframe= for exploration without persistence, or supply governed identity to register and persist a complete table profile. Use frequency_columns=[] to skip frequency calculations.',
  'glossary_terms': ['Data Catalogue', 'Profile', 'source table', 'target table'],
  'return_interpretation': 'Use result["profile"] for statistical rows and result["frequency_profile"] for selected frequency distributions. Governed rows include snapshot identities and audit fields; DataFrame-only calls do not write metadata.',
  'common_failure_causes': ['Supply dataframe or a complete governed identity; do not mix table_id and physical coordinates.', 'Selected frequency columns must exist. frequency_top_n limits retained values, not grouping cost.', 'Governed profiling requires configured metadata routing, write permission, and Delta support.'],
  'related_guides': [{'title': 'Pipeline Execution', 'path': '../../guided-demo/02-build-and-run-etl.md'}]},
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
                       'severity="blocking")',
  'related_functions': ['enforce_profile_behavior'],
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
                      'path': '../../guided-demo/02-build-and-run-etl.md'}]},
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
                     'downstream writes.',
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
                       ')',
  'related_functions': ['profile_table',
                        'enforce_freshness'],
  'related_guides': [{'title': 'Pipeline Execution',
                      'path': '../../guided-demo/02-build-and-run-etl.md'},
                     {'title': 'Governance Review',
                      'path': '../../guided-demo/03-author-and-freeze-data-contract.md'}]},
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
  'related_functions': ['profile_table', 'write_lakehouse_table'],
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
                      'path': '../../guided-demo/02-build-and-run-etl.md'},
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
  'when_to_use': 'Use in 02_pipeline when active freshness rules from the Data Contract payload '
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
  'module': 'widgets.widget_data_contract',
  'function_type': 'callable',
  'summary_override': 'Create or reopen and author one agreement-free, table-centric Data Contract draft.',
  'symbol_name': 'widget_data_contract',
  'template_notebook': '01_governance',
  'template_segment': 'Data Contract authoring',
  'use_when': 'Use as the primary UX for preparing and freezing one governed table’s next Data Contract version.',
  'parameters': 'Canonical table_id, a Fabric Spark session, and an optional active Fabric context.',
  'returns': 'Exact-version state, compact controls, the displayed UI, and validation and freeze actions.',
  'raises': 'Raises validation, widget, Spark, or configured metadata routing errors.',
  'related_functions': ['setup_pipeline'],
  'expanded_purpose': 'Provides one four-tab governance experience for table and column authoring, Advanced rules, canonical manifest review, freezing, and activation.',
  'when_to_use': 'Use after Engineering registers a table to create or reopen its agreement-free draft and author descriptive Enrichment plus normalized Schema, Grain, Freshness, Source Drift, Data Quality, and Sensitive Data Guardrails.',
  'do_not_use_when': 'Do not use for pipeline-time immutable contract selection; use setup_pipeline.',
  'glossary_terms': ['data contract', 'guardrails', 'enrichment', 'metadata lakehouse'],
  'return_interpretation': 'The returned state remains pinned to the draft created or reopened for the requested table_id and active environment; saves delegate to contract-authoring services.',
  'common_failure_causes': ['The table_id has no active Catalogue row.',
                            'The metadata target cannot be read or written.',
                            'A subtype-specific Guardrail value is invalid.']},
 {'kind': 'function', 'module': 'widgets.widget_activate_pipeline', 'function_type': 'callable',
  'summary_override': 'Review complete persisted Testing and activate an exact whole pipeline.',
  'symbol_name': 'widget_activate_pipeline', 'template_notebook': '01_governance', 'template_segment': 'Pipeline activation',
  'use_when': 'Use after finalize_pipeline returns complete successful governed Test results.',
  'expanded_purpose': 'Shows exact contracts/rules and processing configuration identity, diagnostics, warnings, Agreement and fingerprint before explicit Governance confirmation. Activation neither deploys nor publishes.',
  'related_functions': ['setup_pipeline']},






 {'kind': 'function',
 'module': 'pipeline.setup_pipeline',
 'function_type': 'callable',
 'summary_override': 'Prepare Testing or resolve an approved environment configuration for Live.',
 'symbol_name': 'setup_pipeline', 'template_notebook': '02_pipeline',
 'template_segment': 'Configure the pipeline and whole-run boundary',
 'use_when': 'Use once before Read, Transform and Write with pipeline_id and pipeline_mode.',
 'related_functions': ['finalize_pipeline', 'widget_data_contract', 'orchestrate_read', 'orchestrate_write'],
 'return_interpretation': 'Returns a context-local execution session with contract selection and automatic reporting; finalize_pipeline records completion and returns Test results; interrupted runs remain incomplete.',
 'expanded_purpose': 'Select a frozen contract or No Contract independently for each Testing participant. Live resolves and pins one approved revision from the central authority.',
 'common_failure_causes': ['Missing explicit table choices or invalid frozen contract selections.', 'Unsafe Testing write destination.', 'Missing complete governed Testing for activation or approved Live configuration.']},




 ]

FOCUSED_FUNCTION_DOC_UPDATES = {
    "setup_metadata_tables": {
        "expanded_purpose": "Creates, additively evolves, or validates the FabricOps metadata tables required by the framework in the configured metadata lakehouse. Missing canonical columns are added without rewriting existing rows, while incompatible canonical types and known legacy schemas still fail validation. Physical nullability is not compared or migrated.",
        "when_to_use": "Run during initial environment setup, after deploying a FabricOps version with metadata schema changes, or when recreating a development metadata environment. Do not use it as a substitute for setup_notebook, which resolves notebook execution context and configuration.",
        "parameters": "spark is the Spark session used for metadata DDL/table-write operations; config is the FabricOps configuration used to resolve the selected env, metadata lakehouse target, governance metadata schema, and engineering metadata schema; env selects the environment; require_active_steward enforces existing active steward readiness; verbose controls setup output; raise_on_failure raises after all tables are processed if any table fails.",
        "returns": "dict[str, Any] setup report after all managed metadata tables have been created, additively evolved, or validated, including status, metadata_schemas, fully_qualified_tables, created_tables, evolved_tables, validated_tables, failed_tables, table_results, data_agreement, governance, engineering, and active metadata counts.",
        "side_effects": "Performs metadata-layer table creation, additive missing-column evolution, and schema validation in the configured metadata lakehouse. Missing tables are created as empty Delta tables; missing canonical columns are added through an empty append with Delta mergeSchema; existing rows and extra physical columns are preserved.",
        "return_interpretation": "Use the returned status and per-table results to confirm that the physical metadata layer is ready and to distinguish tables that were created, evolved, validated, or failed. The function does not register business datasets.",
        "common_failure_causes": ["Missing, invalid, or non-schema-enabled Metadata Lakehouse configuration.", "Spark or Fabric lakehouse context is unavailable.", "The caller lacks permission to create or inspect metadata tables.", "An existing canonical field has an incompatible Spark field type or a known legacy schema requires explicit migration.", "Missing canonical fields are added automatically; nullability and field order are not validated.", "One table can fail while later tables are still processed; raise_on_failure raises only after processing all tables."],
        "preferred_example": "setup_result = setup_metadata_tables(spark=spark, config=CONFIG, env=ENVIRONMENT_NAME)",
    },
    "setup_notebook": {
        "expanded_purpose": "Prepares a Fabric notebook to use FabricOps consistently by validating environment configuration, resolving required data and metadata targets, collecting runtime identity, and returning a normalized NotebookSetupContext for downstream cells.",
        "when_to_use": "Call near the beginning of an operational FabricOps notebook to load workspace configuration before source reads, metadata setup, profiling, guardrails, or writes. It is normally called once per notebook execution and does not replace setup_metadata_tables.",
        "parameters": "config optionally supplies explicit FabricOps configuration; otherwise the caller workspace selects the environment through 00_env_config. config_workspace_id optionally locates a remote config notebook; otherwise loading uses the current workspace; env applies only to explicit config; required_targets identifies the configured data or metadata targets that must resolve; notebook_name overrides automatic runtime notebook-name resolution; run_id_prefix is used only when Fabric does not provide a run id; local_fallback_name supports local tests when Fabric runtime context is unavailable.",
        "returns": "NotebookSetupContext with run_id, notebook_name, workspace_name, user_name, environment, paths, validation_results, runtime_metadata, and readiness_status.",
        "side_effects": "With no config, runs 00_env_config for the caller workspace, loads JSON, applies the audit timezone and initializes the shared context. Explicit config retains validation-only behavior. It does not write business data, provision resources or persist metadata.",
        "return_interpretation": "A ready context means required targets resolved and startup checks did not fail. Review validation_results when readiness_status is not ready before running downstream notebook cells.",
        "common_failure_causes": ["Missing required configuration sections or target names.", "No active Spark session, which is reported as a warning for local fallback mode.", "Fabric notebook runtime utilities are unavailable outside Fabric.", "Workspace, lakehouse, warehouse, or notebook context cannot be resolved.", "Invalid target names or required store identity fields.", "Explicit notebook_name or local_fallback_name is needed when automatic Fabric context is not available."],
        "preferred_example": 'CONTEXT = setup_notebook()',
    },
    "read_lakehouse_csv": {
        "expanded_purpose": "Reads one CSV file or a compatible collection of CSV files from a Fabric lakehouse Files location into a Spark DataFrame using FabricOps target and path resolution. It does not profile, register, display, cache, or write the data automatically.",
        "when_to_use": "Use when source data is stored as CSV under a lakehouse Files path. Use read_lakehouse_table for registered Delta tables, read_lakehouse_parquet for Parquet files, and read_lakehouse_excel for Excel workbooks.",
        "parameters": "relative_path is the file, folder, or wildcard-style Lakehouse Files path resolved under the store; store is the logical Lakehouse store; header controls first-row column names; spark_session overrides notebook global spark; context can provide resolved FabricOps config/env; additional keyword options are passed to Spark CSV reader, including inferSchema, sep, encoding, schema-related options, recursiveFileLookup, and malformed-row handling.",
        "returns": "Spark DataFrame representing rows parsed from the selected CSV file or files. Columns and data types depend on the supplied schema and CSV reader options.",
        "side_effects": "Constructs a Spark CSV read plan only; it does not write files, tables, or metadata.",
        "return_interpretation": "The returned DataFrame is a normal lazy Spark DataFrame until an action such as count, display, collect, or write is executed.",
        "common_failure_causes": ["The lakehouse target or Files path cannot be resolved.", "The path is missing or the caller lacks read permission.", "Malformed rows, inconsistent files in a folder, absent headers, or empty files do not match the requested Spark CSV options.", "Schema inference can produce unexpected types; an explicit schema can mismatch source values.", "Some Spark failures appear only when a downstream action evaluates the DataFrame."],
        "preferred_example": 'orders_df = read_lakehouse_csv("incoming/orders.csv", inferSchema=True)',
    },
    "read_lakehouse_parquet": {
        "expanded_purpose": "Reads Parquet data from a Fabric lakehouse Files location into a Spark DataFrame while resolving the logical FabricOps lakehouse target and path. It preserves Parquet schema metadata where Spark can infer it and does not register, profile, or write a new table.",
        "when_to_use": "Use for Parquet files or partitioned Parquet folders stored under lakehouse Files. Use read_lakehouse_table for registered Delta tables and read_lakehouse_csv for CSV input.",
        "returns": "Spark DataFrame backed by the selected Parquet file or folder. One DataFrame row represents one source record; partition columns may be added by Spark when reading partitioned folders.",
        "return_interpretation": "The function verifies decodability with a one-row Spark action before returning, then downstream transformations remain normal Spark DataFrame operations.",
        "common_failure_causes": ["The path is missing, inaccessible, empty, corrupt, or not Parquet.", "Schemas are incompatible across files unless Spark options such as mergeSchema are appropriate.", "Schema merging can be expensive on large partitioned folders.", "The configured target cannot be resolved or read.", "Failures can occur during the initial validation action or later Spark evaluation."],
        "preferred_example": 'orders_df = read_lakehouse_parquet("curated/orders/", spark_session=spark)',
    },
    "read_lakehouse_table": {
        "expanded_purpose": "Loads a registered lakehouse Delta table into a Spark DataFrame using FabricOps target, schema, and table-name resolution so notebooks do not hardcode fully qualified table paths.",
        "when_to_use": "Use for Delta tables registered in a Fabric lakehouse. Use file readers for CSV, Parquet, or Excel files, and read_warehouse_table for Fabric Warehouse tables.",
        "parameters": "table_name is the logical table name, not a qualified schema.table string; store selects the configured Lakehouse; schema optionally qualifies schema-enabled lakehouses; spark_session overrides notebook global spark; context supplies reusable FabricOps config/env; reader options are passed to Spark Delta reader.",
        "returns": "Spark DataFrame containing the current rows and columns of the resolved lakehouse table. The DataFrame preserves the table Spark schema and remains lazy until an action is executed.",
        "common_failure_causes": ["The target cannot be resolved or is not a lakehouse.", "The table is not found, exists under another lakehouse or schema, or the schema argument is incorrect.", "The caller lacks read permissions or no Spark session is available.", "Spark Delta read failures may be deferred until an action evaluates the DataFrame."],
        "preferred_example": 'orders_df = read_lakehouse_table("orders", store="Bronze", schema="demo")',
    },
    "read_warehouse_query": {
        "expanded_purpose": "Executes caller-supplied read-only SQL against a Fabric Warehouse and returns the result as a Spark DataFrame. Filtering, joins, grouping, and projection run in the Warehouse before rows are transferred to Spark.",
        "when_to_use": "Use when the Warehouse dataset is best expressed as SQL, especially when joins, filters, aggregations, or projections should execute before transfer. Use read_warehouse_table for a straightforward full-table read.",
        "parameters": "query is a read-only SELECT statement or WITH CTE ending in SELECT; store resolves the configured Warehouse connection; spark_session overrides notebook global spark; context supplies reusable FabricOps config/env; options are passed to the Fabric Warehouse Spark connector. Parameter binding is not implemented, so do not interpolate untrusted values.",
        "returns": "Spark DataFrame containing the rows and columns produced by the Warehouse query. The output schema is determined by the SQL projection and Warehouse result types.",
        "common_failure_causes": ["Invalid, blank, or non-read-only SQL.", "Unknown tables or columns, unresolved Warehouse connection, or permission failure.", "Unsupported Warehouse-to-Spark type conversion.", "Very large result transfers can be slow or fail; empty result sets are successful DataFrames with zero rows."],
        "usage_notes": "Apply selective filters, projections, joins, and aggregations in the SQL query where practical so the Warehouse processes them before rows are transferred into Spark. Avoid SELECT * for very large tables when only a subset of fields is required.",
        "preferred_example": 'active_students_df = read_warehouse_query("SELECT student_id, programme_code, enrolment_status FROM dbo.student_enrolment WHERE enrolment_status = \'Active\'", store="warehouse", spark_session=spark)',
    },
    "read_warehouse_table": {
        "expanded_purpose": "Reads a complete Fabric Warehouse table into a Spark DataFrame using the configured Warehouse connection, schema, and table identity. The table remains owned by the Warehouse and is not copied, profiled, registered, or modified.",
        "when_to_use": "Use for a straightforward read of one Warehouse table. Use read_warehouse_query when columns, rows, joins, or aggregations should be reduced in the Warehouse before transfer to Spark.",
        "parameters": "schema is the physical Warehouse schema; table_name is the physical table; store resolves the configured Warehouse; spark_session overrides notebook global spark; context supplies FabricOps config/env; options are passed to the Fabric Warehouse Spark connector.",
        "returns": "Spark DataFrame containing the rows and columns of the resolved Warehouse table.",
        "common_failure_causes": ["The Warehouse connection cannot be resolved.", "The schema or table is not found, the caller lacks permission, or identifiers are invalid.", "The table contains unsupported data types for transfer to Spark.", "Complete-table reads may transfer large datasets; an empty table returns a valid zero-row DataFrame."],
        "usage_notes": "A complete-table read may transfer a large dataset from the Warehouse into Spark. Use read_warehouse_query when the workload can be reduced through SQL projection, filtering, joins, or aggregation.",
        "preferred_example": 'student_df = read_warehouse_table("dbo", "student_enrolment", store="warehouse", spark_session=spark)',
    },
    "write_lakehouse_table": {
        "expanded_purpose": "Writes a Spark DataFrame to a Fabric lakehouse table using the configured FabricOps target, schema, table name, and write settings. Spark-side repartitioning can be applied before the physical Delta write so large datasets can be processed by multiple Spark tasks concurrently; physical Delta partitioning is separate and only occurs when partition_by is supplied.",
        "when_to_use": "Use after a pipeline DataFrame has been prepared and passed required validation or guardrail checks. Small datasets usually need the default write path; large datasets may use repartition_by for additional Spark write parallelism. Use partition_by only for persisted Delta layout based on stable, commonly filtered columns.",
        "parameters": "df is the Spark DataFrame to write and is not mutated; table_name is the unqualified Lakehouse table; store resolves the Lakehouse; schema optionally qualifies schema-enabled lakehouses; mode controls append/overwrite/errorifexists/ignore behavior; partition_by physically partitions Delta files and folders; repartition_by accepts a positive integer, one column name, a non-empty string-only list/tuple of column names, or a list/tuple beginning with a positive integer followed by column names and calls Spark repartitioning before writing; options are forwarded to the Delta writer; verbose prints the resolved path; context supplies FabricOps config/env.",
        "returns": "None. The function validates routing and write settings, optionally repartitions the DataFrame, performs the Spark Delta write, and returns after the write completes or Spark raises an error.",
        "common_failure_causes": ["Zero or negative repartition counts, unsupported repartition_by types, empty lists/tuples, non-string column values after any leading partition count, or missing repartition columns.", "Invalid partition_by columns, schema mismatch, append-versus-overwrite conflicts, or unintended destructive overwrite.", "Insufficient write permissions, concurrent writes to the same target table, partial or failed Delta commits, empty DataFrame handling, small-file risk, or Spark shuffle failure."],
        "usage_notes": "Parallel processing is Spark distributed execution over DataFrame partitions, not Python threading, multiprocessing, parallel submission of separate tables, or a separate orchestration helper. repartition_by changes Spark execution partitions for the current write; partition_by changes the persisted Delta layout.",
        "preferred_example": 'write_lakehouse_table(orders_df, "orders_clean", store="Silver", schema="demo", mode="overwrite")',
    },
    "write_warehouse_table": {
        "expanded_purpose": "Writes a Spark DataFrame to a Fabric Warehouse table through the configured Warehouse write path. Spark-side repartitioning can be applied before connector transfer so large datasets can use multiple Spark tasks concurrently; it does not create physical Warehouse table partitions.",
        "when_to_use": "Use when a prepared and validated Spark DataFrame must be stored in a Fabric Warehouse. Small datasets normally use the default write path; large datasets may use repartition_by when the DataFrame has too few partitions or needs more balanced Spark-side write concurrency. Use write_lakehouse_table for Delta lakehouse targets or physical Delta partitioning.",
        "parameters": "df is the Spark DataFrame to transfer and is not mutated; schema is the Warehouse schema such as dbo; table_name is the Warehouse table; store resolves the Warehouse connection; mode is passed to the connector; repartition_by accepts a positive integer, one column name, a non-empty string-only list/tuple of column names, or a list/tuple beginning with a positive integer followed by column names and calls Spark repartitioning before connector transfer; options are forwarded to the connector after required identity options; context supplies FabricOps config/env. No partition_by parameter exists for Warehouse writes.",
        "returns": "None. The function validates repartitioning, optionally writes a repartitioned DataFrame through the Warehouse connector, and returns after connector execution completes or raises an error.",
        "common_failure_causes": ["Zero or negative repartition counts, missing repartition columns, unsupported repartition_by value types, empty lists/tuples, or non-string column values after any leading partition count.", "Schema or table not found, unsupported write mode, authentication or connector failure, Warehouse permission failure, or unsupported Spark-to-Warehouse type conversion.", "Connector-managed transfer or staging failure, transaction or lock conflict, empty DataFrame behaviour, large transfer timeout/resource exhaustion, or accidentally writing the original DataFrame instead of the repartitioned one."],
        "usage_notes": "Parallel Spark tasks within one write_warehouse_table call are not the same as several notebooks or jobs writing to the same Warehouse table concurrently. The function does not coordinate independent writers or guarantee safe simultaneous overwrite operations, and it must not be documented with lakehouse-style partition_by behaviour.",
        "preferred_example": 'write_warehouse_table(orders_df, "dbo", "orders", mode="append")',
    },


    "profile_table": {
        "expanded_purpose": 'Profiles an exact supplied DataFrame or complete physical table. Governed identities persist METADATA_DATA_CATALOGUE, METADATA_DATA_PROFILED, and METADATA_DATA_PROFILED_FREQUENCY; DataFrame-only calls remain in memory.',
        "when_to_use": 'Use dataframe= for exploration without persistence, or supply governed identity to register and persist a complete table profile. Use frequency_columns=[] to skip frequency calculations.',
        "returns": 'Dictionary with profile (statistical Spark DataFrame) and frequency_profile (frequency Spark DataFrame or None).',
        "return_interpretation": 'Use result["profile"] for statistical rows and result["frequency_profile"] for selected frequency distributions. Governed rows include snapshot identities and audit fields; DataFrame-only calls do not write metadata.',
        "common_failure_causes": ['Supply dataframe or a complete governed identity; do not mix table_id and physical coordinates.', 'Selected frequency columns must exist. frequency_top_n limits retained values, not grouping cost.', 'Governed profiling requires configured metadata routing, write permission, and Delta support.'],
        "preferred_example": 'result = profile_table(dataframe=orders_df)\nstatistical_profile = result["profile"]',
    },
}


PUBLIC_SYMBOL_DOCS.append({'kind': 'function', 'module': 'pipeline.finalize_pipeline',
    'function_type': 'callable', 'symbol_name': 'finalize_pipeline',
    'summary_override': 'Complete execution and return Test results or commit the Live outcome.',
    'template_notebook': '02_pipeline', 'template_segment': 'Finalize Pipeline',
    'related_functions': ['setup_pipeline', 'orchestrate_read', 'orchestrate_write'],
    'use_when': 'Call after all Reads, transformations and Writes, including read-only runs.'})

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
 'profile_table': {'expanded_purpose': 'Profiles an exact supplied DataFrame or complete physical table. Governed identities persist METADATA_DATA_CATALOGUE, METADATA_DATA_PROFILED, and METADATA_DATA_PROFILED_FREQUENCY; DataFrame-only calls remain in memory.',
                       'when_to_use': 'Use dataframe= for exploration without persistence, or supply governed identity to register and persist a complete table profile. Use frequency_columns=[] to skip frequency calculations.',
                       'glossary_terms': ['evidence', 'source data', 'target table'],
                       'return_interpretation': 'Use result["profile"] for statistical rows and result["frequency_profile"] for selected frequency distributions. Governed rows include snapshot identities and audit fields; DataFrame-only calls do not write metadata.',
                       'common_failure_causes': ['Supply dataframe or a complete governed identity; do not mix table_id and physical coordinates.', 'Selected frequency columns must exist. frequency_top_n limits retained values, not grouping cost.', 'Governed profiling requires configured metadata routing, write permission, and Delta support.']},

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
                                           'the Data Contract payload should determine the '
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

 }

RELATED_GUIDES_BY_SYMBOL = {'setup_notebook': [{'title': 'Templates',
                     'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'},
                    {'title': 'Metadata Tables',
                     'path': '../../reference/metadata.md'}],
 'setup_metadata_tables': [{'title': 'Templates',
                            'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'},
                           {'title': 'Metadata Tables',
                            'path': '../../reference/metadata.md'}],
 'widget_render_data_steward': [{'title': 'Templates',
                                 'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'widget_render_data_agreement': [{'title': 'Templates',
                                   'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'read_lakehouse_table': [{'title': 'Templates',
                           'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'write_lakehouse_table': [{'title': 'Templates',
                            'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'},
                           {'title': 'Metadata Tables',
                            'path': '../../reference/metadata.md'}],
 'read_lakehouse_csv': [{'title': 'Templates',
                         'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'read_lakehouse_parquet': [{'title': 'Templates',
                             'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'read_lakehouse_excel': [{'title': 'Templates',
                           'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'read_warehouse_table': [{'title': 'Templates',
                           'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'write_warehouse_table': [{'title': 'Templates',
                            'path': 'https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks'}],
 'profile_table': [{'title': 'Pipeline Execution',
                        'path': '../../guided-demo/02-build-and-run-etl.md'},
                       {'title': 'Governance Review',
                        'path': '../../guided-demo/03-author-and-freeze-data-contract.md'}],
 'enforce_freshness': [{'title': 'Pipeline Execution',
                        'path': '../../guided-demo/02-build-and-run-etl.md'}],
 'enforce_profile_behavior': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/02-build-and-run-etl.md'},
                              {'title': 'Governance Review',
                               'path': '../../guided-demo/03-author-and-freeze-data-contract.md'}],
 'write_catalogue_evidence': [{'title': 'Pipeline Execution',
                               'path': '../../guided-demo/02-build-and-run-etl.md'},
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


METADATA_TABLE_PURPOSES["METADATA_PIPELINE_REGISTRY"] = METADATA_TABLE_MODELS["METADATA_PIPELINE_REGISTRY"]["purpose"]
METADATA_COLUMN_OWNERS["METADATA_PIPELINE_REGISTRY"] = {
    name: ["fabricops_kit.pipeline.shared.commit_pipeline_registration", "fabricops_kit.config.setup_metadata_tables.setup_metadata_tables"]
    for name in ("pipeline_id", "environment_name", "workspace_id", "notebook_id", "notebook_name", "registered_at", "registered_by", "updated_at", "registration_status", "registry_token")
}
METADATA_COLUMN_OWNERS["METADATA_PIPELINE_REGISTRY"]["__audit__"] = ["fabricops_kit.config.audit.build_runtime_audit_fields"]

METADATA_COLUMN_OWNERS["METADATA_PIPELINE_REGISTRY"]["__default__"] = [
    "fabricops_kit.pipeline.setup_pipeline.setup_pipeline",
]
