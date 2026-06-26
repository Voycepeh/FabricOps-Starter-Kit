"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import pytest

from fabricops_kit.config import (
    DataAgreementConfig,
    FrameworkConfig,
    GovernanceConfig,
    LineageConfig,
    NotebookRuntimeConfig,
    PathConfig,
    QualityConfig,
    ReviewWorkflowConfig,
    _current_audit_timestamp,
    _get_active_metadata_tables,
    _validate_audit_timezone,
    _validate_metadata_table_registration,
    get_default_fabric_context,
    get_fabric_context,
    resolve_fabric_context,
    setup_metadata_tables,
    setup_notebook,
)
from fabricops_kit.config import FabricStore
from tests.helpers import framework_config, store

pytestmark = pytest.mark.unit



def test_config_setup_public_api_signatures_match_frozen_contract():
    """Verify config setup public API signatures match the frozen contract."""
    assert str(inspect.signature(setup_notebook)) == (
        "(config: 'FrameworkConfig | dict[str, Any]', env: 'str' = 'Sandbox', "
        "required_targets: 'list[str] | None' = None, notebook_name: 'str | None' = None, "
        "run_id_prefix: 'str' = 'run', local_fallback_name: 'str | None' = None) -> 'NotebookSetupContext'"
    )
    assert str(inspect.signature(setup_metadata_tables)) == (
        "(*, spark: 'Any', config: 'FrameworkConfig | dict[str, Any]', env: 'str', "
        "metadata_schema: 'str | None' = None, require_active_steward: 'bool' = False) -> 'dict[str, Any]'"
    )
    assert setup_notebook.__module__ == "fabricops_kit.config"
    assert setup_metadata_tables.__module__ == "fabricops_kit.config"

def test_get_fabric_context_uses_env_as_primary_key():
    """Verify explicit Fabric contexts expose env as the primary environment key."""
    config = object()

    context = get_fabric_context(env="dev", config=config)

    assert context["env"] == "dev"
    assert context["config"] is config


def test_default_fabric_context_requires_env(monkeypatch):
    """Verify active contexts expose env without legacy aliases."""
    import builtins

    config = object()
    monkeypatch.setattr(builtins, "FABRIC_CONTEXT", {"config": config, "env": "dev"}, raising=False)

    context = get_default_fabric_context()

    assert context["env"] == "dev"
    assert context["config"] is config


def test_resolve_fabric_context_uses_env_only():
    """Verify context resolution uses env as the single environment key."""
    config = object()

    resolved_config, env, context = resolve_fabric_context(context={"config": config, "env": "dev"})

    assert resolved_config is config
    assert env == "dev"
    assert context["env"] == "dev"


def test_governance_config_uses_widget_custom_fields_contract():
    """Verify governance widget additions use custom_fields keyed by key."""
    legacy_context_field = "enrichment_context_extra" + "_fields"
    legacy_classification_field = "enrichment_classification_extra" + "_fields"
    config = GovernanceConfig(
        enrichment_context_widget={"custom_fields": [{"key": "business_owner_notes", "type": "textarea"}]},
        enrichment_classification_widget={"custom_fields": [{"key": "retention_class", "type": "select"}]},
    )

    assert config.enrichment_context_widget["custom_fields"][0]["key"] == "business_owner_notes"
    assert config.enrichment_classification_widget["custom_fields"][0]["key"] == "retention_class"
    assert not hasattr(config, legacy_context_field)
    assert not hasattr(config, legacy_classification_field)


def test_data_agreement_widgets_normalize_custom_fields_contract():
    """Verify data agreement widgets normalize custom field keys consistently."""
    config = DataAgreementConfig(
        data_steward_widget={"custom_fields": [{"key": " steward_note ", "type": "textarea"}]},
        data_agreement_widget={"custom_fields": [{"key": " agreement_note ", "type": "text"}]},
    )

    assert config.data_steward_widget["custom_fields"][0]["key"] == "steward_note"
    assert config.data_agreement_widget["custom_fields"][0]["key"] == "agreement_note"


def test_data_agreement_widgets_reject_blank_custom_field_keys():
    """Verify data agreement widgets reject blank custom field keys."""
    with pytest.raises(ValueError, match="Governance custom fields require a key"):
        DataAgreementConfig(data_steward_widget={"custom_fields": [{"key": " "}]})

def test_env_config_template_does_not_expose_prompt_boilerplate_or_unused_defaults():
    """Verify env config template does not expose prompt boilerplate or unused defaults."""
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "AIPromptConfig" not in source
    assert "ai_prompt_config" not in source
    assert "DQ_RULE_SUGGESTION_PROMPT_TEMPLATE =" not in source
    assert "GOVERNANCE_CANDIDATE_PROMPT_TEMPLATE" not in source
    assert "GOVERNANCE_REVIEW_PROMPT_TEMPLATE" not in source
    assert "QUALITY_CONFIG = QualityConfig()" not in source
    assert "GOVERNANCE_CONFIG = GovernanceConfig()" not in source
    assert "REVIEW_WORKFLOW_CONFIG = ReviewWorkflowConfig()" not in source
    assert "LINEAGE_CONFIG = LineageConfig()" not in source


def test_framework_config_defaults_framework_only_sections_when_omitted():
    """Verify framework config defaults framework only sections when omitted."""
    config = FrameworkConfig(
        path_config=PathConfig(paths={"dev": {"source": store()}}),
        notebook_runtime_config=NotebookRuntimeConfig(),
    )

    assert isinstance(config.quality_config, QualityConfig)
    assert isinstance(config.governance_config, GovernanceConfig)
    assert isinstance(config.review_workflow_config, ReviewWorkflowConfig)
    assert isinstance(config.lineage_config, LineageConfig)


def test_dict_framework_config_defaults_framework_only_sections_when_omitted():
    """Verify dict framework config defaults framework only sections when omitted."""
    config = setup_notebook.__globals__["_validate_framework_config"]({
        "path_config": PathConfig(paths={"dev": {"source": store(), "unified": store(name="unified")}}),
        "notebook_runtime_config": NotebookRuntimeConfig(),
    })

    assert isinstance(config.quality_config, QualityConfig)
    assert isinstance(config.governance_config, GovernanceConfig)
    assert isinstance(config.review_workflow_config, ReviewWorkflowConfig)
    assert isinstance(config.lineage_config, LineageConfig)


def test_framework_config_keeps_type_validation_for_present_defaulted_sections():
    """Verify framework config keeps type validation for present defaulted sections."""
    with pytest.raises(ValueError, match="quality_config must be a QualityConfig object"):
        setup_notebook.__globals__["_validate_framework_config"]({
            "path_config": PathConfig(paths={"dev": {"source": store()}}),
            "notebook_runtime_config": NotebookRuntimeConfig(),
                "quality_config": object(),
        })


def test_setup_notebook_resolves_environment_paths_and_reports_invalid_targets(fake_notebookutils):
    """Verify setup notebook resolves environment paths and reports invalid targets."""
    config = framework_config()

    required_targets = ["source", "unified", "product", "metadata"]
    context = setup_notebook(
        config=config, env="dev", required_targets=required_targets, notebook_name="99_explore_orders"
    )

    assert context.environment == "dev"
    assert set(context.paths) == set(required_targets)
    assert context.paths["source"].name == "lh_source_dev"
    assert context.paths["unified"].name == "lh_unified_dev"
    assert context.paths["product"].name == "wh_product_dev"
    assert context.paths["metadata"].name == "lh_metadata_dev"
    assert context.readiness_status in {"ready", "not_ready"}
    with pytest.raises(ValueError, match="Target 'missing' was not found"):
        setup_notebook(config=config, env="dev", required_targets=["missing"])


def test_config_objects_copy_nested_agreement_defaults_and_validate_paths():
    """Verify config objects copy nested agreement defaults and validate paths."""
    source = {"visible_columns": ["steward_name"], "custom_fields": [{"key": "group", "options": ["A"]}]}
    config = DataAgreementConfig(data_steward_widget=source)
    source["custom_fields"][0]["options"].append("B")

    assert config.data_steward_widget["custom_fields"][0]["options"] == ["A"]
    assert "data_agreement_evidence" in config.metadata_tables
    assert {"recipient", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}.issubset(
        set(config.data_agreement_widget["visible_columns"])
    )
    with pytest.raises(ValueError, match="paths must be a non-empty mapping"):
        PathConfig(paths={})


def test_setup_metadata_tables_creates_missing_tables_with_write_helper(monkeypatch):
    """Verify setup metadata tables creates missing tables with write helper."""
    from fabricops_kit.data_agreement import DATA_AGREEMENT_EVIDENCE_TABLE, DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE
    from fabricops_kit.metadata import NOTEBOOK_REGISTRY_TABLE
    import fabricops_kit.io.shared as io
    import fabricops_kit.governance_review as governance

    class Schema:
        def __init__(self, fields):
            self._fields = fields

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return list(self._fields)

    class Table:
        def __init__(self, fields):
            self.columns = list(fields)

    class Spark:
        def __init__(self):
            self.created_dataframes = []

        def createDataFrame(self, rows, schema=None):  # noqa: N802 - mirrors Spark API
            self.created_dataframes.append((list(rows), schema.fieldNames()))
            return object()

        def sql(self, statement):
            raise AssertionError(f"metadata setup must not call spark.sql: {statement}")

    schemas = {
        DATA_STEWARD_TABLE: Schema(["steward_id"]),
        DATA_AGREEMENT_TABLE: Schema(["agreement_id"]),
        DATA_AGREEMENT_EVIDENCE_TABLE: Schema(["agreement_id", "file_path"]),
        NOTEBOOK_REGISTRY_TABLE: Schema(["agreement_id", "registration_id"]),
        "METADATA_GUARDRAIL_RULES": Schema(["rule_id"]),
    }
    reads = {table: 0 for table in schemas}
    writes = []

    def read_table(table, *, target, context, schema=None, spark_session=None):
        assert target == "metadata"
        assert context["env"] == "dev"
        assert schema is None
        reads[table] += 1
        if reads[table] == 1:
            raise RuntimeError("table does not exist")
        return Table(schemas[table].fieldNames())

    monkeypatch.setattr("fabricops_kit.config._get_metadata_table_schema_registry", lambda config: schemas)
    monkeypatch.setattr(governance, "_get_governance_metadata_schemas", lambda: {"METADATA_GUARDRAIL_RULES": schemas["METADATA_GUARDRAIL_RULES"]})
    monkeypatch.setattr(io, "read_lakehouse_table_core", read_table)
    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((context["env"], target, table, kwargs))

    monkeypatch.setattr(io, "write_lakehouse_table_core", write_table)
    monkeypatch.setattr("fabricops_kit.data_agreement._list_data_stewards", lambda *args, **kwargs: [{"steward_id": "s1"}])

    spark = Spark()
    result = setup_metadata_tables(spark=spark, config=framework_config(), env="dev", require_active_steward=True)

    assert result["status"] == "ready"
    assert result["data_agreement"]["status"] == "ready"
    assert result["notebook_registry"]["created"] is True
    assert result["governance"]["created_tables"] == ["METADATA_GUARDRAIL_RULES"]
    assert result["tables"] == list(schemas)
    assert result["created_tables"] == list(schemas)
    assert result["warnings"] == []
    assert result["active_metadata_tables"] == list(schemas)
    assert [table for _, _, table, _ in writes] == list(schemas)
    assert all(target == "metadata" for _, target, _, _ in writes)
    assert all(kwargs == {"schema": None, "mode": "overwrite", "options": {"overwriteSchema": "true"}} for *_, kwargs in writes)
    assert result["metadata_schema"] is None
    assert result["fully_qualified_tables"] == list(schemas)
    assert spark.created_dataframes == [([], schema.fieldNames()) for schema in schemas.values()]


def test_setup_metadata_tables_ready_without_active_steward_when_not_required(monkeypatch):
    """Verify setup metadata tables ready without active steward when not required."""
    import fabricops_kit.io.shared as io

    class Schema:
        def __init__(self, fields):
            self._fields = fields

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return list(self._fields)

    class Table:
        def __init__(self, fields):
            self.columns = list(fields)

    schemas = {"METADATA_DATA_STEWARD": Schema(["steward_id", "is_active"])}
    reads = []

    def read_table(table, *, target, context, spark_session=None, **kwargs):
        assert context["env"] == "dev"
        assert target == "metadata"
        reads.append((context["env"], target, table, spark_session))
        return Table(schemas[table].fieldNames())

    monkeypatch.setattr("fabricops_kit.config._get_metadata_table_schema_registry", lambda config: schemas)
    monkeypatch.setattr("fabricops_kit.governance_review._get_governance_metadata_schemas", lambda: {})
    monkeypatch.setattr(io, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(io, "write_lakehouse_table_core", lambda *args, **kwargs: pytest.fail("valid existing metadata tables should not be recreated"))
    monkeypatch.setattr("fabricops_kit.data_agreement._list_data_stewards", lambda *args, **kwargs: [])

    spark = object()
    result = setup_metadata_tables(spark=spark, config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["data_agreement"]["status"] == "not_ready"
    assert result["warnings"] == []
    assert result["created_tables"] == []
    assert reads == [("dev", "metadata", "METADATA_DATA_STEWARD", spark), ("dev", "metadata", "METADATA_DATA_STEWARD", spark)]


def test_active_metadata_tables_are_source_driven_and_include_access_context():
    """Verify active metadata tables are source driven and include access context."""
    tables = _get_active_metadata_tables(framework_config())

    assert len(tables) == 11
    assert "METADATA_DATA_STEWARD" in tables
    assert "METADATA_DATA_AGREEMENT" in tables
    assert "METADATA_DATA_AGREEMENT_EVIDENCE" in tables
    assert "METADATA_NOTEBOOK_REGISTRY" in tables
    assert "METADATA_ENRICHMENT_RULES" in tables
    assert "METADATA_COLUMN_CONTEXT" not in tables
    assert "METADATA_COLUMN_CLASSIFICATION" not in tables
    assert "METADATA_GUARDRAIL_RULES" in tables
    assert "METADATA_GUARDRAIL_PROFILES" not in tables
    assert "METADATA_GUARDRAIL_RESULTS" in tables
    assert "METADATA_GUARDRAIL_BASELINE_EVENTS" not in tables
    assert "METADATA_GOVERNANCE_REVIEWS" not in tables
    assert "METADATA_DATA_ACCESS" in tables


def test_metadata_data_catalogue_schema_is_profile_evidence_only():
    """Verify catalogue schema has profile_mode but excludes old result fields."""
    from fabricops_kit.governance_review import CATALOGUE_TABLE, _get_governance_metadata_schemas

    fields = set(_get_governance_metadata_schemas()[CATALOGUE_TABLE].fieldNames())

    assert "profile_mode" in fields
    assert "load_behavior" not in fields
    for result_field in {
        "freshness_status",
        "freshness_can_continue",
        "stability_status",
        "dq_rule_count",
        "dq_failed_rule_count",
        "freshness_message",
        "stability_can_continue",
        "stability_message",
        "source_change_signal_json",
        "profile_baseline_mode",
    }:
        assert result_field not in fields

def test_metadata_registration_validation_reads_configured_metadata_target(monkeypatch):
    """Verify metadata registration validation reads configured metadata target."""
    import fabricops_kit.io.shared as io

    calls = []

    def read_table(table, *, target, context, schema=None, spark_session=None):
        assert context["env"] == "dev"
        assert target == "metadata"
        calls.append((context["env"], target, table, schema, spark_session))
        return object()

    class Spark:
        def sql(self, statement):
            raise AssertionError(f"metadata validation must not call spark.sql: {statement}")

    monkeypatch.setattr(io, "read_lakehouse_table_core", read_table)
    spark = Spark()
    result = _validate_metadata_table_registration(
        spark=spark,
        config=framework_config(),
        env="dev",
        expected_tables=["METADATA_DATA_STEWARD", "METADATA_GUARDRAIL_RULES"],
    )

    assert result["status"] == "ready"
    assert result["missing_tables"] == []
    assert result["expected_table_count"] == 2
    assert result["registered_tables"] == ["METADATA_DATA_STEWARD", "METADATA_GUARDRAIL_RULES"]
    assert result["show_tables_statement"] is None
    assert result["optional_documented_tables"] == []
    assert calls == [
        ("dev", "metadata", "METADATA_DATA_STEWARD", None, spark),
        ("dev", "metadata", "METADATA_GUARDRAIL_RULES", None, spark),
    ]


def test_metadata_registration_validation_warns_for_missing_configured_tables(monkeypatch):
    """Verify metadata registration validation warns for missing configured tables."""
    import fabricops_kit.io.shared as io

    def read_table(table, *, target, context, schema=None, spark_session=None):
        assert context["env"] == "dev"
        assert target == "metadata"
        raise RuntimeError("table does not exist")

    monkeypatch.setattr(io, "read_lakehouse_table_core", read_table)
    result = _validate_metadata_table_registration(
        spark=object(),
        config=framework_config(),
        env="dev",
        expected_tables=["METADATA_DATA_STEWARD"],
    )

    assert result["status"] == "not_ready"
    assert result["missing_tables"] == ["METADATA_DATA_STEWARD"]
    assert "configured metadata target" in result["warnings"][0]


def test_setup_metadata_tables_passes_metadata_schema_to_io_helpers(monkeypatch):
    """Verify setup metadata tables passes metadata schema to io helpers."""
    import fabricops_kit.io.shared as io

    class Schema:
        def __init__(self, fields):
            self._fields = fields
        def fieldNames(self):  # noqa: N802
            return list(self._fields)

    class Table:
        columns = ["id"]

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            return object()

    schemas = {"METADATA_DATA_AGREEMENT": Schema(["id"])}
    reads = []
    writes = []

    def read_table(table, *, target, context, schema=None, spark_session=None):
        assert context["env"] == "dev"
        assert target == "metadata"
        reads.append((table, schema))
        return Table()

    monkeypatch.setattr("fabricops_kit.config._get_metadata_table_schema_registry", lambda config: schemas)
    monkeypatch.setattr("fabricops_kit.config._get_active_metadata_tables", lambda config: list(schemas))
    monkeypatch.setattr("fabricops_kit.governance_review._get_governance_metadata_schemas", lambda: {})
    monkeypatch.setattr(io, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(io, "write_lakehouse_table_core", lambda *args, **kwargs: writes.append(kwargs))
    monkeypatch.setattr("fabricops_kit.data_agreement._list_data_stewards", lambda *args, **kwargs: [{"steward_id": "s1"}])

    result = setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev", metadata_schema="METADATA")

    assert result["metadata_schema"] == "METADATA"
    assert result["fully_qualified_tables"] == ["METADATA.METADATA_DATA_AGREEMENT"]
    assert result["registration_validation"]["metadata_schema"] == "METADATA"
    assert all(schema == "METADATA" for _, schema in reads)
    assert writes == []


def test_setup_metadata_tables_reports_configured_metadata_schema(monkeypatch):
    """Verify setup metadata tables reports configured metadata schema."""
    import fabricops_kit.io.shared as io

    class Schema:
        def fieldNames(self):  # noqa: N802
            return ["id"]

    class Table:
        columns = ["id"]

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            return object()

    cfg = framework_config()
    metadata_store = cfg.path_config.paths["dev"]["metadata"]
    cfg.path_config.paths["dev"]["metadata"] = FabricStore(
        env=metadata_store.env,
        workspace_id=metadata_store.workspace_id,
        item_id=metadata_store.item_id,
        name=metadata_store.name,
        kind=metadata_store.kind,
        schema_enabled=True,
        schema="dbo",
    )
    schemas = {"METADATA_DATA_AGREEMENT": Schema()}

    monkeypatch.setattr("fabricops_kit.config._get_metadata_table_schema_registry", lambda config: schemas)
    monkeypatch.setattr("fabricops_kit.governance_review._get_governance_metadata_schemas", lambda: {})
    monkeypatch.setattr(io, "read_lakehouse_table_core", lambda *args, **kwargs: Table())
    monkeypatch.setattr(io, "write_lakehouse_table_core", lambda *args, **kwargs: None)
    monkeypatch.setattr("fabricops_kit.data_agreement._list_data_stewards", lambda *args, **kwargs: [{"steward_id": "s1"}])

    result = setup_metadata_tables(spark=Spark(), config=cfg, env="dev")

    assert result["metadata_schema"] == "dbo"
    assert result["fully_qualified_tables"] == ["dbo.METADATA_DATA_AGREEMENT"]
    assert result["registration_validation"]["fully_qualified_tables"] == ["dbo.METADATA_DATA_AGREEMENT"]

def test_audit_timezone_defaults_validates_and_fails_clearly():
    """Verify audit timezone defaults validates and fails clearly."""
    assert _validate_audit_timezone(None) == "UTC"
    assert _validate_audit_timezone("Asia/Singapore") == "Asia/Singapore"
    with pytest.raises(ValueError, match='Invalid FABRICOPS_AUDIT_TIMEZONE: "Singapore"'):
        _validate_audit_timezone("Singapore")


def test_framework_config_and_current_audit_timestamp_use_configured_timezone():
    """Verify framework config and current audit timestamp use configured timezone."""
    config = FrameworkConfig(
        **{**framework_config().__dict__, "audit_timezone": "Asia/Singapore"}
    )

    assert config.audit_timezone == "Asia/Singapore"
    assert _current_audit_timestamp(config=config).endswith("+08:00")


def test_env_config_template_exposes_audit_timezone_setting():
    """Verify env config template exposes audit timezone setting."""
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    timezone_assignment = re.search(r'(?m)^FABRICOPS_AUDIT_TIMEZONE = "([^"]+)"$', source)
    assert timezone_assignment is not None
    configured_timezone = timezone_assignment.group(1)
    assert _validate_audit_timezone(configured_timezone) == configured_timezone
    assert "FABRICOPS_AUDIT_TIMEZONE" in source
    assert "_validate_audit_timezone" in source or "audit_timezone=FABRICOPS_AUDIT_TIMEZONE" in source
    assert "audit_timezone=FABRICOPS_AUDIT_TIMEZONE" in source
    assert "UTC is the default and recommended portable option." in source
    assert "valid IANA timezone" in source
    assert "Asia/Singapore" in source


def test_downstream_notebooks_use_config_aware_audit_timestamps_only():
    """Verify downstream notebooks use config aware audit timestamps only."""
    notebook_paths = [
        Path("templates/notebooks/01_agreement.ipynb"),
        Path("templates/notebooks/02_pipeline.ipynb"),
        Path("templates/notebooks/03_governance.ipynb"),
        Path("templates/notebooks/99_explore.ipynb"),
        Path("templates/notebooks/example_pipeline_demo.ipynb"),
        Path("templates/notebooks/example_dq_rule_smoke_test.ipynb"),
    ]

    for path in notebook_paths:
        source = path.read_text(encoding="utf-8")
        assert 'FABRICOPS_AUDIT_TIMEZONE = "UTC"' not in source
        assert 'DEFAULT_AUDIT_TIMEZONE = "UTC"' not in source
        assert "datetime.now(timezone.utc)" not in source
        assert "datetime.utcnow" not in source

    pipeline_source = Path("templates/notebooks/02_pipeline.ipynb").read_text(encoding="utf-8")
    pipeline_helper_source = Path("src/fabricops_kit/pipeline.py").read_text(encoding="utf-8")
    assert "PIPELINE = start_pipeline_run(" in pipeline_source
    assert "_current_audit_timestamp" not in pipeline_source
    assert "PIPELINE_STARTED_AT" not in pipeline_source
    assert "pipeline_started_at=_now_iso()" in pipeline_helper_source
    assert "def _now_iso(config: Any = None) -> str:" in pipeline_helper_source
    assert "return _current_audit_timestamp(config=config)" in pipeline_helper_source


def test_config_workflow_role_boundaries_do_not_add_workflow_to_workflow_signal():
    """Verify config setup role tags avoid workflow-to-workflow architecture signals."""
    from scripts.generate_function_reference import ROLE_TAGS_BY_NAME, _role_dependency_signals

    config_roles = {
        name: tags[0]
        for name, tags in ROLE_TAGS_BY_NAME.items()
        if name in {
            "_setup_notebook_workflow",
            "_setup_metadata_tables_workflow",
            "_setup_metadata_table_registry",
            "_validate_metadata_table_registration",
            "_run_config_smoke_tests",
            "_get_store",
            "_resolve_metadata_schema",
        }
    }

    assert config_roles["_setup_notebook_workflow"] == "internal_workflow"
    assert config_roles["_setup_metadata_tables_workflow"] == "internal_workflow"
    assert config_roles["_setup_metadata_table_registry"] == "internal_adapter"
    assert config_roles["_validate_metadata_table_registration"] == "internal_validator"
    assert config_roles["_run_config_smoke_tests"] == "internal_validator"
    assert (
        _role_dependency_signals(
            config_roles["_setup_metadata_tables_workflow"],
            config_roles["_validate_metadata_table_registration"],
        )
        == ["allowed_internal_role_call"]
    )
    assert (
        _role_dependency_signals(
            config_roles["_setup_metadata_tables_workflow"],
            config_roles["_setup_metadata_table_registry"],
        )
        == ["allowed_internal_role_call"]
    )


def test_data_agreement_widget_role_hints_keep_orchestration_as_workflow():
    """Verify agreement widget orchestration is not misclassified as an adapter."""
    from scripts.generate_function_reference import ROLE_TAGS_BY_NAME, _role_dependency_signals

    shared_roles = ROLE_TAGS_BY_NAME["_render_maintenance_widget_shared_workflow"]

    assert shared_roles[:2] == ["internal_workflow", "shared_widget_rendering_workflow"]
    assert "internal_adapter" not in shared_roles
    assert "widget_rendering_adapter" not in shared_roles
    assert "_render_maintenance_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_data_steward_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_data_agreement_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert (
        _role_dependency_signals("public_api_entrypoint", shared_roles[0])
        == ["allowed_internal_role_call"]
    )


def test_data_agreement_widget_callable_inventory_roles_are_current():
    """Verify generated widget inventory reflects the shared workflow role split."""
    import json

    inventory = json.loads(Path("docs/reference/_data/function-call-graph.json").read_text(encoding="utf-8"))["function_inventory"]
    rows = {row["qualified_name"]: row for row in inventory}
    for qn in [
        "fabricops_kit.data_agreement._render_maintenance_widget_shared_workflow",
        "fabricops_kit.data_agreement._render_agreement_evidence_widget_workflow",
    ]:
        assert rows[qn]["function_type"] == "Private helper"
        assert rows[qn]["layer"] == "private_helper"
    assert rows["fabricops_kit.data_agreement.widget_render_data_steward"]["signals"] == ["allowed_internal_role_call"]
    assert rows["fabricops_kit.data_agreement.widget_render_data_agreement"]["signals"] == ["allowed_internal_role_call"]
