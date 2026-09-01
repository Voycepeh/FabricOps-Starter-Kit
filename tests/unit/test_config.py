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
    PathConfig,
    setup_metadata_tables,
    setup_notebook,
)
from fabricops_kit.config import FabricStore
from fabricops_kit.config.shared import (
    get_current_audit_timestamp,
    _validate_audit_timezone,
    validate_framework_config,
    get_default_fabric_context,
    resolve_fabric_context,
    resolve_runtime_context,
)
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
        "metadata_schema: 'str | None' = None, require_active_steward: 'bool' = False, "
        "verbose: 'bool' = True, raise_on_failure: 'bool' = False) -> 'dict[str, Any]'"
    )
    assert setup_notebook.__module__ == "fabricops_kit.config.setup_notebook"
    assert setup_metadata_tables.__module__ == "fabricops_kit.config.setup_metadata_tables"


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


def test_runtime_context_resolver_normalizes_fabric_keys_and_precedence(fake_notebookutils):
    """Canonical runtime identity prefers explicit and active values per field."""
    fake_notebookutils.runtime.context.clear()
    fake_notebookutils.runtime.context.update(
        currentWorkspaceId="live-current-workspace",
        workspaceId="live-fallback-workspace",
        notebookId="live-notebook",
        notebookName="live-notebook-name",
        userId="live-user",
        activityId="live-activity",
    )

    resolved = resolve_runtime_context(
        context={"notebook_id": "explicit-notebook", "workspace_id": "unknown"},
        active_context={
            "runtime_metadata": {
                "workspace_id": "active-workspace",
                "notebook_name": "active-notebook-name",
            }
        },
    )

    assert resolved == {
        "workspace_id": "active-workspace",
        "workspace_name": None,
        "notebook_id": "explicit-notebook",
        "notebook_name": "active-notebook-name",
        "user_name": None,
        "user_id": "live-user",
        "activity_id": "live-activity",
    }


def test_runtime_audit_fields_use_canonical_runtime_resolver(monkeypatch):
    """Audit construction consumes the shared canonical runtime representation."""
    from fabricops_kit.config import audit

    canonical = {
        "workspace_id": "workspace-id",
        "workspace_name": "Workspace",
        "notebook_id": "notebook-id",
        "notebook_name": "Notebook",
        "user_name": "user@example.com",
        "user_id": None,
        "activity_id": "activity-id",
    }
    monkeypatch.setattr(audit, "resolve_runtime_context", lambda **_kwargs: canonical)

    fields = audit.build_runtime_audit_fields(
        committed_at="2026-08-09T00:00:00+00:00",
        metadata_lakehouse_name="Metadata",
    )

    assert fields["_notebook_id"] == "notebook-id"
    assert fields["_workspace_id"] == "workspace-id"
    assert fields["_committed_by"] == "user@example.com"


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


def test_framework_config_uses_simplified_config_sections():
    """Verify FrameworkConfig only exposes active config sections."""
    config = FrameworkConfig(path_config=PathConfig(paths={"dev": {"source": store()}}))

    assert isinstance(config.governance_config, GovernanceConfig)
    assert isinstance(config.data_agreement_config, DataAgreementConfig)
    assert not hasattr(config, "quality_config")
    assert not hasattr(config, "review_workflow_config")
    assert not hasattr(config, "lineage_config")
    assert not hasattr(config, "notebook_runtime_config")


def test_dict_framework_config_defaults_simplified_sections_when_omitted():
    """Verify dict framework config defaults simplified sections when omitted."""
    config = validate_framework_config(
        {
            "path_config": PathConfig(paths={"dev": {"source": store(), "unified": store(name="unified")}}),
        }
    )

    assert isinstance(config.governance_config, GovernanceConfig)
    assert isinstance(config.data_agreement_config, DataAgreementConfig)


def test_removed_config_classes_are_not_exported_from_root():
    """Verify removed config classes are absent from the root public API."""
    import fabricops_kit

    assert not hasattr(fabricops_kit, "QualityConfig")
    assert not hasattr(fabricops_kit, "ReviewWorkflowConfig")
    assert not hasattr(fabricops_kit, "LineageConfig")
    assert not hasattr(fabricops_kit, "NotebookRuntimeConfig")


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


def test_setup_notebook_uses_consolidated_governance_name_contract(fake_notebookutils):
    """Accept 01_governance and reject the removed Governance notebook type."""
    config = framework_config()

    governance = setup_notebook(config=config, env="dev", required_targets=["source"], notebook_name="01_governance_orders")
    legacy = setup_notebook(config=config, env="dev", required_targets=["source"], notebook_name="03_governance_orders")

    governance_check = next(check for check in governance.validation_results if check.name == "notebook_naming")
    legacy_check = next(check for check in legacy.validation_results if check.name == "notebook_naming")
    assert governance_check.status == "pass"
    assert legacy_check.status == "fail"


def test_config_objects_copy_nested_agreement_defaults_and_validate_paths():
    """Verify config objects copy nested agreement defaults and validate paths."""
    source = {"visible_columns": ["steward_name"], "custom_fields": [{"key": "group", "options": ["A"]}]}
    config = DataAgreementConfig(data_steward_widget=source)
    source["custom_fields"][0]["options"].append("B")

    assert config.data_steward_widget["custom_fields"][0]["options"] == ["A"]
    assert "data_agreement_evidence" not in config.metadata_tables
    visible_columns = set(config.data_agreement_widget["visible_columns"])
    assert {"business_purpose", "provider_steward_id", "recipient_steward_id"}.issubset(visible_columns)
    assert "recipient" not in visible_columns
    assert not any(field.startswith("approved_usage_") for field in config.data_agreement_widget["visible_columns"])
    with pytest.raises(ValueError, match="paths must be a non-empty mapping"):
        PathConfig(paths={})


def test_setup_metadata_tables_directly_bootstraps_canonical_tables(monkeypatch):
    """Verify setup metadata tables routes bootstrap writes through Lakehouse IO."""
    from fabricops_kit.config.metadata_schemas import (
        CANONICAL_METADATA_TABLES,
        metadata_table_schema_registry,
        metadata_table_schema_rows,
    )

    class DataFrame:
        def __init__(self, spark, columns):
            self.spark = spark
            self.columns = columns

    class Table:
        def __init__(self, columns):
            self.columns = columns

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    class Spark:
        def __init__(self):
            self.tables = {}
            self.created_tables = []
            self.pending_columns = []
            self.created_schemas = {}
            self.pending_schema = None

        def createDataFrame(self, rows, schema=None):  # noqa: N802
            assert rows == []
            self.pending_schema = schema
            self.pending_columns = schema.fieldNames()
            return DataFrame(self, self.pending_columns)

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])

    def read_table(table_name, *, target, schema=None, spark_session=None, context=None):
        assert target == "metadata"
        assert schema is None
        assert context["env"] == "dev"
        if table_name not in spark.tables:
            raise RuntimeError(f"Table {table_name} does not exist")
        return Table(spark.tables[table_name])

    def write_table(
        df, table_name, *, target, schema=None, mode="append", options=None, verbose=True, context=None, **_kwargs
    ):
        assert target == "metadata"
        assert schema is None
        assert mode == "overwrite"
        assert options is None
        assert verbose is False
        spark.created_tables.append(table_name)
        spark.tables[table_name] = spark.pending_columns
        spark.created_schemas[table_name] = spark.pending_schema

    spark = Spark()
    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)
    result = setup_metadata_tables(spark=spark, config=framework_config(), env="dev", require_active_steward=True)

    assert result["status"] == "ready"
    assert result["tables"] == CANONICAL_METADATA_TABLES
    assert result["created_tables"] == CANONICAL_METADATA_TABLES
    assert spark.created_tables == CANONICAL_METADATA_TABLES
    expected_registry = metadata_table_schema_registry()
    assert {table: metadata_table_schema_rows(schema) for table, schema in spark.created_schemas.items()} == {
        table: metadata_table_schema_rows(schema) for table, schema in expected_registry.items()
    }


def test_setup_metadata_tables_ready_without_active_steward_when_not_required(monkeypatch):
    """Verify setup metadata tables does not require an active steward by default."""
    from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry

    class Table:
        def __init__(self, columns):
            self.columns = columns

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return []

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    class Spark:
        def __init__(self):
            self.schemas = {name: schema.fieldNames() for name, schema in metadata_table_schema_registry().items()}

    spark = Spark()
    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    monkeypatch.setattr(
        setup_module, "read_lakehouse_table_core", lambda table_name, **_kwargs: Table(spark.schemas[table_name])
    )

    result = setup_metadata_tables(spark=spark, config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["data_agreement"]["status"] == "not_ready"
    assert result["created_tables"] == []
    assert result["tables"] == CANONICAL_METADATA_TABLES


def test_setup_metadata_tables_reports_explicit_metadata_schema(monkeypatch):
    """Verify setup metadata tables reports explicit schema-qualified names."""
    from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry

    class Table:
        def __init__(self, columns):
            self.columns = columns

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    class Spark:
        def __init__(self):
            self.schemas = {name: schema.fieldNames() for name, schema in metadata_table_schema_registry().items()}

    spark = Spark()
    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    monkeypatch.setattr(
        setup_module,
        "read_lakehouse_table_core",
        lambda table_name, *, schema=None, **_kwargs: Table(spark.schemas[table_name]),
    )

    result = setup_metadata_tables(spark=spark, config=framework_config(), env="dev", metadata_schema="METADATA")

    assert result["metadata_schema"] == "METADATA"
    assert result["fully_qualified_tables"] == [f"METADATA.{name}" for name in CANONICAL_METADATA_TABLES]


def test_setup_metadata_tables_reports_configured_metadata_schema(monkeypatch):
    """Verify setup metadata tables reports configured metadata schema."""
    from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry

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

    class Table:
        def __init__(self, columns):
            self.columns = columns

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    class Spark:
        def __init__(self):
            self.schemas = {name: schema.fieldNames() for name, schema in metadata_table_schema_registry().items()}

    spark = Spark()
    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    monkeypatch.setattr(
        setup_module,
        "read_lakehouse_table_core",
        lambda table_name, *, schema=None, **_kwargs: Table(spark.schemas[table_name]),
    )

    result = setup_metadata_tables(spark=spark, config=cfg, env="dev")

    assert result["metadata_schema"] == "dbo"
    assert result["fully_qualified_tables"] == [f"dbo.{name}" for name in CANONICAL_METADATA_TABLES]


def test_setup_metadata_tables_does_not_rewrite_compliant_tables(monkeypatch):
    """Verify setup metadata tables does not rewrite schema-compliant existing tables."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    def read_table(table_name, **_kwargs):
        return Table(registry[table_name].fieldNames())

    def write_table(*_args, **_kwargs):
        raise AssertionError("schema-compliant tables must not be rewritten")

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["created_tables"] == []


def test_setup_metadata_tables_rejects_existing_tables_missing_canonical_columns(monkeypatch):
    """Verify setup does not rewrite existing metadata table schemas in place."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    tables = {name: Table(schema.fieldNames()) for name, schema in registry.items()}
    tables["METADATA_DATA_CATALOGUE"] = Table(
        [name for name in registry["METADATA_DATA_CATALOGUE"].fieldNames() if name != "store_type"]
    )
    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", lambda table_name, **_kwargs: tables[table_name])
    monkeypatch.setattr(
        setup_module,
        "write_lakehouse_table_core",
        lambda *_args, **_kwargs: pytest.fail("existing metadata tables must not be schema-replaced"),
    )

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev", verbose=False)
    assert result["status"] == "partial_failure"
    assert result["failed_tables"] == ["METADATA_DATA_CATALOGUE"]


def test_setup_metadata_tables_unsafe_missing_column_still_raises(monkeypatch):
    """Verify setup metadata tables raises when missing columns cannot be safely added."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

    def read_table(table_name, **_kwargs):
        if table_name == "METADATA_DATA_CATALOGUE":
            return Table([name for name in registry[table_name].fieldNames() if name != "store_type"])
        return Table(registry[table_name].fieldNames())

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev", verbose=False)
    assert result["failed_tables"] == ["METADATA_DATA_CATALOGUE"]
    assert "store_type" in result["table_results"]["METADATA_DATA_CATALOGUE"]["message"]


def test_setup_metadata_tables_accepts_existing_tables_with_nullable_physical_audit_fields(monkeypatch):
    """Verify setup ignores Spark physical nullability for existing tables."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, schema):
            self.schema = schema
            self.columns = schema.fieldNames()

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    def spark_nullable_schema(schema):
        field_type = type(schema.fields[0])
        schema_type = type(schema)
        return schema_type([field_type(field.name, field.dataType, True) for field in schema.fields])

    canonical_activity_field = next(
        field for field in registry["METADATA_DATA_PROFILED"].fields if field.name == "_activity_id"
    )
    assert canonical_activity_field.nullable is False

    tables = {name: Table(spark_nullable_schema(schema)) for name, schema in registry.items()}
    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", lambda table_name, **_kwargs: tables[table_name])
    monkeypatch.setattr(
        setup_module,
        "write_lakehouse_table_core",
        lambda *_args, **_kwargs: pytest.fail("existing metadata tables must not be rewritten"),
    )

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev", verbose=False)
    assert result["status"] == "ready"
    assert result["failed_tables"] == []
    assert "METADATA_DATA_PROFILED" in result["validated_tables"]


def test_setup_metadata_tables_rejects_existing_tables_with_wrong_canonical_type(monkeypatch):
    """Verify setup validates physical data types on existing tables."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    try:
        from pyspark.sql.types import StringType
    except ModuleNotFoundError:
        pytest.skip("pyspark is required to construct a real Spark StringType")

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, schema):
            self.schema = schema
            self.columns = schema.fieldNames()

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    def wrong_type(schema):
        field_type = type(schema.fields[0])
        schema_type = type(schema)
        fields = []
        for field in schema.fields:
            data_type = StringType() if field.name == "row_count" else field.dataType
            fields.append(field_type(field.name, data_type, field.nullable))
        return schema_type(fields)

    tables = {name: Table(schema) for name, schema in registry.items()}
    tables["METADATA_DATA_PROFILED"] = Table(wrong_type(registry["METADATA_DATA_PROFILED"]))
    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", lambda table_name, **_kwargs: tables[table_name])
    monkeypatch.setattr(
        setup_module,
        "write_lakehouse_table_core",
        lambda *_args, **_kwargs: pytest.fail("existing metadata tables must not be rewritten"),
    )

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev", verbose=False)
    assert result["failed_tables"] == ["METADATA_DATA_PROFILED"]
    assert (
        "row_count type expected long but found string" in result["table_results"]["METADATA_DATA_PROFILED"]["message"]
    )


def test_profiled_validation_rejects_only_legacy_frequency_json_addition():
    """Verify the breaking unexpected-column rule is scoped to the profiled parent."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    from fabricops_kit.config.setup_metadata_tables import _validate_existing_metadata_schema

    registry = metadata_table_schema_registry()
    profiled = registry["METADATA_DATA_PROFILED"]
    field_type = type(profiled.fields[0])
    schema_type = type(profiled)
    with_legacy = schema_type(
        [*profiled.fields, field_type("frequency_json", profiled.fields[0].dataType, True)]
    )
    with pytest.raises(ValueError, match="unexpected legacy column: frequency_json"):
        _validate_existing_metadata_schema("METADATA_DATA_PROFILED", with_legacy, profiled)

    catalogue = registry["METADATA_DATA_CATALOGUE"]
    additive_catalogue = schema_type(
        [*catalogue.fields, field_type("consumer_extension", catalogue.fields[0].dataType, True)]
    )
    _validate_existing_metadata_schema("METADATA_DATA_CATALOGUE", additive_catalogue, catalogue)


def test_profiled_frequency_validation_checks_required_columns_and_types():
    """Verify every required normalized child field retains physical column and type validation."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    from fabricops_kit.config.setup_metadata_tables import _validate_existing_metadata_schema

    schema = metadata_table_schema_registry()["METADATA_DATA_PROFILED_FREQUENCY"]
    field_type = type(schema.fields[0])
    schema_type = type(schema)
    missing_value = schema_type([field for field in schema.fields if field.name != "value"])
    with pytest.raises(ValueError, match=r"missing required column\(s\): value"):
        _validate_existing_metadata_schema("METADATA_DATA_PROFILED_FREQUENCY", missing_value, schema)

    string_type = next(field.dataType for field in schema.fields if field.name == "value")
    wrong_type = schema_type(
        [
            field_type(field.name, string_type, field.nullable)
            if field.name == "frequency_count"
            else field
            for field in schema.fields
        ]
    )
    with pytest.raises(ValueError, match="frequency_count type expected long but found string"):
        _validate_existing_metadata_schema("METADATA_DATA_PROFILED_FREQUENCY", wrong_type, schema)


def test_setup_metadata_tables_creates_new_tables_with_canonical_schema(monkeypatch):
    """Verify newly created metadata tables use the canonical schema registry."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()
    created = {}
    existing = {}

    class Frame:
        def __init__(self, schema):
            self.schema = schema
            self.columns = schema.fieldNames()

        def where(self, _expr):
            return self

        def limit(self, value):
            assert value == 1
            return self

        def take(self, value):
            assert value == 1
            return [object()]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            assert rows == []
            return Frame(schema)

    def read_table(table_name, **_kwargs):
        if table_name not in existing:
            raise RuntimeError("table not found")
        return existing[table_name]

    def write_table(frame, table_name, **kwargs):
        assert kwargs.get("mode") == "overwrite"
        created[table_name] = frame.schema
        existing[table_name] = frame

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)

    result = setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev")

    assert result["created_tables"] == list(registry)
    assert created["METADATA_DATA_ACCESS"].fieldNames() == registry["METADATA_DATA_ACCESS"].fieldNames()
    access_fields = {field.name: field for field in created["METADATA_DATA_ACCESS"].fields}
    assert all(not access_fields[field].nullable for field in {"_activity_id", "_committed_at", "_workspace_id"})


def test_setup_metadata_tables_non_missing_read_error_includes_original_exception(monkeypatch):
    """Verify corrupt metadata tables fail with the original read exception details."""
    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            raise AssertionError("corrupt table reads must not create replacement tables")

    def read_table(_table_name, **_kwargs):
        raise ValueError("Delta log is corrupt")

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    result = setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev", verbose=False)
    assert result["status"] == "failed"
    assert len(result["failed_tables"]) == 15
    assert "Original ValueError: Delta log is corrupt" in result["table_results"]["METADATA_DATA_STEWARD"]["message"]


def test_metadata_data_catalogue_and_profiled_schema_split():
    """Verify catalogue is narrow identity and profiled keeps detailed evidence."""
    from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry

    registry = metadata_table_schema_registry()
    catalogue = registry["METADATA_DATA_CATALOGUE"]
    profiled = registry["METADATA_DATA_PROFILED"]
    catalogue_names = catalogue.fieldNames()
    profiled_names = profiled.fieldNames()
    profiling_fields = {
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
    }

    assert catalogue_names == [
        "metadata_level",
        "table_id",
        "column_id",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "data_type",
        "load_strategy",
        "load_strategy_parameters_json",
        "first_profiled_at",
        "last_profiled_at",
        "is_active",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    assert (profiling_fields - {"data_type"}).isdisjoint(catalogue_names)
    assert {"metadata_level", "table_id", "column_id", "column_name", "first_profiled_at", "last_profiled_at", "is_active"}.issubset(catalogue_names)
    assert profiling_fields.issubset(profiled_names)
    assert {"profile_id", "profile_snapshot_id", "table_id", "column_id", "environment_name", "data_type"}.issubset(profiled_names)
    assert len(catalogue_names) == len(set(catalogue_names))
    assert len(profiled_names) == len(set(profiled_names))
    audit_names = {name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS}
    assert audit_names.issubset(catalogue_names)
    assert audit_names.issubset(profiled_names)


def test_audit_timezone_defaults_validates_and_fails_clearly():
    """Verify audit timezone defaults validates and fails clearly."""
    assert _validate_audit_timezone(None) == "UTC"
    assert _validate_audit_timezone("Asia/Singapore") == "Asia/Singapore"
    with pytest.raises(ValueError, match='Invalid FABRICOPS_AUDIT_TIMEZONE: "Singapore"'):
        _validate_audit_timezone("Singapore")


def test_framework_config_and_get_current_audit_timestamp_use_configured_timezone():
    """Verify framework config and get current audit timestamp use configured timezone."""
    config = FrameworkConfig(**{**framework_config().__dict__, "audit_timezone": "Asia/Singapore"})

    assert config.audit_timezone == "Asia/Singapore"
    assert get_current_audit_timestamp(config=config).endswith("+08:00")

    with pytest.raises(ValueError, match='Invalid FABRICOPS_AUDIT_TIMEZONE: "Singapore"'):
        get_current_audit_timestamp(timezone_name="Singapore")


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


def test_downstream_notebooks_use_config_aware_audit_timestamps_only():
    """Verify downstream notebooks use config aware audit timestamps only."""
    notebook_paths = sorted(Path("templates/notebooks").glob("*.ipynb"))
    assert notebook_paths, "expected at least one maintained notebook template"

    for path in notebook_paths:
        source = path.read_text(encoding="utf-8")
        assert 'FABRICOPS_AUDIT_TIMEZONE = "UTC"' not in source
        assert 'DEFAULT_AUDIT_TIMEZONE = "UTC"' not in source
        assert "datetime.now(timezone.utc)" not in source
        assert "datetime.utcnow" not in source

    pipeline_source = Path("templates/notebooks/02_pipeline.ipynb").read_text(encoding="utf-8")
    assert "widget_pipeline_bootstrap" not in pipeline_source
    assert "_current_audit_timestamp" not in pipeline_source
    assert "PIPELINE_STARTED_AT" not in pipeline_source


def test_config_workflow_role_boundaries_do_not_reference_removed_metadata_workflow():
    """Verify removed metadata workflow no longer participates in role metadata."""
    from scripts.generate_individual_function_reference_pages import ROLE_TAGS_BY_NAME

    assert "_setup_metadata_tables_workflow" not in ROLE_TAGS_BY_NAME
    assert "_setup_notebook_workflow" not in ROLE_TAGS_BY_NAME
    assert "_setup_metadata_table_registry" not in ROLE_TAGS_BY_NAME
    assert "_validate_metadata_table_registration" not in ROLE_TAGS_BY_NAME


def test_data_agreement_widget_role_hints_do_not_restore_generic_workflow():
    """Verify agreement widgets do not reintroduce generic shared orchestration."""
    from scripts.generate_individual_function_reference_pages import ROLE_TAGS_BY_NAME

    assert "render_maintenance_widget_shared_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_maintenance_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_data_steward_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_data_agreement_widget_workflow" not in ROLE_TAGS_BY_NAME


def test_data_agreement_widget_callable_inventory_roles_are_current():
    """Verify generated v2 callable-flow inventory reflects the widget role split."""
    import json

    flow_data = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    rows = {row["qualified_name"]: row for row in flow_data["defined_functions"]}
    assert "fabricops_kit.widgets.shared.render_maintenance_widget_shared_workflow" not in rows
    assert (
        "fabricops_kit.widgets.widget_render_agreement_evidence._render_agreement_evidence_widget_workflow" not in rows
    )
    assert "fabricops_kit.widgets.shared._render_agreement_evidence_widget_workflow" not in rows
    public_functions = {row["qualified_name"]: row for row in flow_data["public_functions"]}
    assert (
        public_functions["fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward"]["flow"][0][
            "function_type"
        ]
        == "widget_function"
    )
    assert (
        public_functions["fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement"]["flow"][0][
            "function_type"
        ]
        == "widget_function"
    )


def test_config_public_import_contract_and_package_shape():
    """Verify config is a package and public config objects import from supported roots."""
    import fabricops_kit
    import fabricops_kit.config as config_package

    from fabricops_kit import (  # noqa: PLC0415
        DataAgreementConfig as RootDataAgreementConfig,
        FabricStore as RootFabricStore,
        FrameworkConfig as RootFrameworkConfig,
        GovernanceConfig as RootGovernanceConfig,
        PathConfig as RootPathConfig,
        setup_metadata_tables as root_setup_metadata_tables,
        setup_notebook as root_setup_notebook,
    )
    from fabricops_kit.config import FabricStore as ConfigFabricStore, FrameworkConfig as ConfigFrameworkConfig  # noqa: PLC0415

    assert Path("src/fabricops_kit/config.py").exists() is False
    assert Path("src/fabricops_kit/config/__init__.py").exists()
    assert Path("src/fabricops_kit/config/public.py").exists() is False
    assert Path("src/fabricops_kit/config/models.py").exists() is False
    assert not Path("src/fabricops_kit/config/get_fabric_context.py").exists()
    assert Path("src/fabricops_kit/config/setup_notebook.py").exists()
    assert Path("src/fabricops_kit/config/setup_metadata_tables.py").exists()
    assert Path("src/fabricops_kit/config/shared.py").exists()
    assert Path(config_package.__file__).parts[-2:] == ("config", "__init__.py")
    assert RootFabricStore is ConfigFabricStore
    assert RootFrameworkConfig is ConfigFrameworkConfig
    assert RootGovernanceConfig is GovernanceConfig
    assert RootPathConfig is PathConfig
    assert RootDataAgreementConfig is DataAgreementConfig
    assert root_setup_notebook is fabricops_kit.setup_notebook
    assert root_setup_metadata_tables is fabricops_kit.setup_metadata_tables
    assert fabricops_kit.setup_notebook.__module__ == "fabricops_kit.config.setup_notebook"
    assert fabricops_kit.setup_metadata_tables.__module__ == "fabricops_kit.config.setup_metadata_tables"
    assert not hasattr(fabricops_kit, "get_fabric_context")
    assert not hasattr(config_package, "get_fabric_context")


def test_env_config_template_imports_config_from_root_only():
    """Verify 00_env_config imports supported config objects from root only."""
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "from fabricops_kit import (" in source
    assert "from fabricops_kit.config" not in source
    assert "NotebookRuntimeConfig" not in source
    assert "NOTEBOOK_PREFIXES" not in source
    assert "RUNTIME_CONFIG" not in source


def test_internal_modules_import_config_shared_helpers_not_old_module():
    """Verify internals use config.shared for internal helper imports."""
    assert "from fabricops_kit.config.shared import get_store, resolve_fabric_context" in Path(
        "src/fabricops_kit/io/shared.py"
    ).read_text(encoding="utf-8")
    assert "build_runtime_audit_fields" in Path(
        "src/fabricops_kit/pipeline/shared.py"
    ).read_text(encoding="utf-8")
    assert "build_audit_timestamp_expr" not in Path("src/fabricops_kit/pipeline/shared.py").read_text(encoding="utf-8")


def test_setup_metadata_tables_uses_public_config_validation_helper_only():
    """Verify setup metadata tables avoids cross-file private helper imports."""
    source = Path("src/fabricops_kit/config/setup_metadata_tables.py").read_text(encoding="utf-8")

    assert "is_table_not_found_error" in source
    assert "validate_framework_config" in source
    assert "_validate_framework_config" not in source
    assert "CANONICAL_METADATA_TABLES" in source
    assert "metadata_schema_type_name" in source
    assert "metadata_table_field_names" in source
    assert "metadata_table_schema_registry" in source


def test_canonical_metadata_schemas_include_audit_and_runtime_python_types():
    """Verify canonical metadata schemas and row coercion align with runtime writer types."""
    from datetime import date, datetime

    from fabricops_kit.config.metadata_schemas import (
        AUDIT_SCHEMA_FIELDS,
        CANONICAL_METADATA_TABLES,
        metadata_table_schema_registry,
    )
    from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types

    audit_columns = {name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS}
    registry = metadata_table_schema_registry()

    assert list(registry) == CANONICAL_METADATA_TABLES
    for table_name, schema in registry.items():
        fields = {field.name: type(field.dataType).__name__ for field in schema.fields}
        assert audit_columns.issubset(fields)
        sample = {}
        for field_name, type_name in fields.items():
            if type_name == "TimestampType":
                sample[field_name] = "2026-06-29T12:34:56+08:00"
            elif type_name == "DateType":
                sample[field_name] = "2026-06-29"
            elif type_name == "BooleanType":
                sample[field_name] = "true"
            elif type_name == "LongType":
                sample[field_name] = "7"
            elif type_name == "DoubleType":
                sample[field_name] = "7.5"
            else:
                sample[field_name] = "value"
        row = coerce_metadata_row_types(table_name, sample)
        for field_name, type_name in fields.items():
            if type_name == "TimestampType":
                assert isinstance(row[field_name], datetime), f"{table_name}.{field_name} must be datetime"
            elif type_name == "DateType":
                assert isinstance(row[field_name], date) and not isinstance(row[field_name], datetime), (
                    f"{table_name}.{field_name} must be date"
                )
            elif type_name == "BooleanType":
                assert isinstance(row[field_name], bool), f"{table_name}.{field_name} must be bool"
            elif type_name == "LongType":
                assert isinstance(row[field_name], int), f"{table_name}.{field_name} must be int"
            elif type_name == "DoubleType":
                assert isinstance(row[field_name], float), f"{table_name}.{field_name} must be float"


def test_runtime_writers_use_shared_metadata_schema_contract_not_public_owner():
    """Verify runtime metadata writers do not import private setup owner helpers."""
    writer_paths = [
        Path("src/fabricops_kit/widgets/shared.py"),
        Path("src/fabricops_kit/pipeline/shared.py"),
    ]

    pipeline_shared_source = Path("src/fabricops_kit/pipeline/shared.py").read_text(encoding="utf-8")
    assert "coerce_metadata_row_types" in pipeline_shared_source
    assert "from fabricops_kit.config.setup_metadata_tables" not in pipeline_shared_source
    assert "from .config.setup_metadata_tables" not in pipeline_shared_source

    for path in writer_paths:
        source = path.read_text(encoding="utf-8")
        assert "config.setup_metadata_tables import _" not in source
        assert "setup_metadata_tables import _" not in source


def test_metadata_schema_registry_is_shared_source_for_setup_and_runtime_coercion():
    """Verify setup and runtime coercion use the shared schema registry service."""
    setup_source = Path("src/fabricops_kit/config/setup_metadata_tables.py").read_text(encoding="utf-8")
    schema_source = Path("src/fabricops_kit/config/metadata_schemas.py").read_text(encoding="utf-8")

    assert "metadata_table_schema_registry()" in setup_source
    assert "def coerce_metadata_row_types" in schema_source
    assert "def _coerce_metadata_value" in schema_source
    assert "metadata_table_schema_registry().get(table_name)" in schema_source
    assert "def metadata_table_schema_registry" in schema_source
    assert "def _metadata_table_schema_registry" not in schema_source


def _metadata_doc_schema_rows(table_name: str) -> list[dict[str, str]]:
    """Return implemented schema rows parsed from a generated metadata docs page."""
    slug = table_name.lower()
    path = Path("docs/reference/metadata") / f"{slug}.md"
    rows = []
    in_schema = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "## Implemented schema":
            in_schema = True
            continue
        if in_schema and line.startswith("## "):
            break
        if not in_schema or not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(
            {
                "name": cells[0].strip("`"),
                "type": cells[1].strip("`"),
                "required": cells[2],
            }
        )
    return rows


def test_generated_metadata_docs_match_setup_metadata_table_schema_registry():
    """Verify metadata docs generation uses the canonical setup schema registry."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, metadata_table_schema_rows

    registry = metadata_table_schema_registry()
    generated_source = Path("scripts/generate_individual_function_reference_pages.py").read_text(encoding="utf-8")

    assert "metadata_table_schema_registry" in generated_source
    assert registry
    for schema in registry.values():
        rows = metadata_table_schema_rows(schema)
        assert rows
        assert all({"name", "type", "nullable"} <= set(row) for row in rows)


def test_metadata_docs_schema_rows_preserve_non_string_types_and_audit_order():
    """Verify metadata docs render canonical non-string types and audit order."""
    from fabricops_kit.config.metadata_schemas import (
        audit_schema_fields,
        metadata_table_schema_registry,
        metadata_table_schema_rows,
    )

    registry = metadata_table_schema_registry()
    catalogue = {row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_CATALOGUE"])}
    profiled = {row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_PROFILED"])}
    agreement = {row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_AGREEMENT"])}
    contract = {row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_CONTRACT"])}
    docs_catalogue = catalogue

    assert agreement["start_date"] == "date"
    assert "approved_usage_internal" not in agreement
    assert agreement["agreement_version"] == "string"
    assert catalogue["store_type"] == "string"
    assert "profile_role" not in catalogue
    assert catalogue["first_profiled_at"] == "timestamp"
    assert catalogue["last_profiled_at"] == "timestamp"
    assert catalogue["is_active"] == "boolean"
    assert "fabric_store_target" not in catalogue
    assert contract["agreement_id"] == "string"
    assert "contract_snapshot_id" not in contract
    assert "snapshot_saved_at" not in contract
    assert "contract_status" not in contract
    assert "null_percent" not in catalogue
    assert profiled["null_percent"] == "double"
    assert docs_catalogue["_committed_at"] == "timestamp"
    assert "profiled_at" not in docs_catalogue
    assert "policy_updated_at" not in docs_catalogue

    for table_name, schema in registry.items():
        names = [row["name"] for row in metadata_table_schema_rows(schema)]
        if table_name == "METADATA_DATA_CATALOGUE":
            assert names[-len(audit_schema_fields()) :] == [name for name, _kind, _nullable in audit_schema_fields()]
            timestamp_fields = [row["name"] for row in metadata_table_schema_rows(schema) if row["type"] == "timestamp"]
            assert timestamp_fields == ["first_profiled_at", "last_profiled_at", "_committed_at"]
        elif table_name == "METADATA_DATA_PROFILED":
            assert names[-len(audit_schema_fields()) :] == [name for name, _kind, _nullable in audit_schema_fields()]
        else:
            assert names[-len(audit_schema_fields()) :] == [name for name, _kind, _nullable in audit_schema_fields()], (
                table_name
            )


def test_lineage_schema_has_only_lineage_fields_and_canonical_audit_context():
    """Verify the breaking lineage schema has one authoritative execution context."""
    from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry

    schema = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"]
    audit_names = [name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS]
    assert schema.fieldNames() == [
        "lineage_id",
        "table_id",
        "environment_name",
        "pipeline_role",
        *audit_names,
    ]
    assert all(not field.nullable for field in schema.fields if field.name in audit_names)
    assert {
        "activity_id",
        "notebook_id",
        "notebook_name",
        "workspace_id",
        "workspace_name",
        "committed_by",
        "metadata_lakehouse_name",
    }.isdisjoint(schema.fieldNames())


def test_metadata_audit_schema_nullability_contract():
    """Verify canonical metadata audit columns preserve physical nullability."""
    from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry

    audit_names = [name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS]
    registry = metadata_table_schema_registry()
    for table_name, schema in registry.items():
        fields = {field.name: field for field in schema.fields}
        for name in audit_names:
            assert fields[name].nullable is False, table_name
        assert set(audit_names).issubset(fields)

    access_fields = [field.name for field in registry["METADATA_DATA_ACCESS"].fields]
    assert access_fields[:7] == [
        "access_id",
        "user_principal",
        "table_id",
        "environment_name",
        "access_level",
        "access_value",
        "access_state",
    ]


def test_metadata_writer_sources_do_not_replace_schemas():
    """Verify metadata writer code does not use overwriteSchema."""
    from pathlib import Path

    roots = [Path("src/fabricops_kit/config"), Path("src/fabricops_kit/pipeline"), Path("src/fabricops_kit/widgets")]
    offenders = []
    for root in roots:
        for path in root.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "metadata" in text.lower() and "overwriteSchema" in text:
                offenders.append(str(path))
    assert offenders == []


def test_setup_metadata_tables_existing_tables_prints_compact_ready_summary(monkeypatch, capsys):
    """Verify all-valid setup stays compact and uses one-row readiness checks."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, columns, rows=None):
            self.columns = list(columns)
            self.rows = rows if rows is not None else [object()]
            self.limit_values = []
            self.take_values = []

        def where(self, expr):
            assert expr == "is_active = true"
            return self

        def limit(self, value):
            self.limit_values.append(value)
            self.rows = self.rows[:value]
            return self

        def take(self, value):
            self.take_values.append(value)
            return self.rows[:value]

        def count(self):
            raise AssertionError("active steward readiness must not use count")

    steward = Table(registry["METADATA_DATA_STEWARD"].fieldNames())
    tables = {name: Table(schema.fieldNames()) for name, schema in registry.items()}
    tables["METADATA_DATA_STEWARD"] = steward
    read_counts = {name: 0 for name in registry}

    def read_table(table_name, **_kwargs):
        read_counts[table_name] += 1
        return tables[table_name]

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")
    output = capsys.readouterr().out
    total = len(registry)

    assert result["status"] == "ready"
    assert result["failed_tables"] == []
    assert result["data_agreement"]["active_steward_count"] == 1
    assert output == f"\nFabricOps metadata tables ready ({total}/{total}).\nActive steward present: Yes\n"
    assert "Checking" not in output
    assert "Validated" not in output
    assert "Failed tables:" not in output
    assert "Created tables:" not in output
    assert read_counts["METADATA_DATA_STEWARD"] == 1
    assert steward.limit_values == [1]
    assert steward.take_values == [1]


def test_setup_metadata_tables_missing_tables_prints_numbered_created_summary(monkeypatch, capsys):
    """Verify missing metadata tables are recorded and summarized concisely."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()
    names = list(registry)
    missing = set(names[:2])
    created = []

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

        def where(self, _expr):
            return self

        def limit(self, _value):
            return self

        def take(self, _value):
            return [object()]

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            assert rows == []
            return Table(schema.fieldNames())

    tables = {name: Table(schema.fieldNames()) for name, schema in registry.items() if name not in missing}

    def read_table(table_name, **_kwargs):
        if table_name not in tables:
            raise RuntimeError(f"{table_name} does not exist")
        return tables[table_name]

    def write_table(frame, table_name, **_kwargs):
        created.append(table_name)
        tables[table_name] = frame

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)

    result = setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev")
    output = capsys.readouterr().out

    assert result["created_tables"] == names[:2]
    assert created == names[:2]
    assert "Checking" not in output
    assert not any(line.startswith("[") and " Validated " in line for line in output.splitlines())
    assert f"[1/{len(names)}] Created {names[0]}" in output
    assert f"[2/{len(names)}] Created {names[1]}" in output
    assert f"FabricOps metadata setup complete ({len(names)}/{len(names)})." in output
    assert "Created: 2" in output
    assert f"Validated: {len(names) - 2}" in output
    assert f"- {names[0]}" in output


def test_setup_metadata_tables_one_failure_continues_and_reports_details(monkeypatch, capsys):
    """Verify one table failure does not stop later table processing."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()
    names = list(registry)
    failed_name = "METADATA_DATA_CONTRACT"
    read_order = []

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

        def where(self, _expr):
            return self

        def limit(self, _value):
            return self

        def take(self, _value):
            return [object()]

    def read_table(table_name, **_kwargs):
        read_order.append(table_name)
        if table_name == failed_name:
            return Table(["bad_column"])
        return Table(registry[table_name].fieldNames())

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")
    output = capsys.readouterr().out

    assert result["status"] == "partial_failure"
    assert result["failed_tables"] == [failed_name]
    assert read_order[: len(names)] == names
    assert "FabricOps metadata setup completed with failures." in output
    assert f"[{names.index(failed_name) + 1}/{len(names)}] Failed {failed_name}" in output
    assert "Checking" not in output
    assert "Validated" not in output
    assert f"Successful: {len(names) - 1}/{len(names)}" in output
    assert f"Failed: 1/{len(names)}" in output
    assert f"- {failed_name}:" in output
    assert "missing required column" in output


def test_setup_metadata_tables_raise_on_failure_waits_until_all_tables_attempted(monkeypatch):
    """Verify consolidated failure raises after the sequential pass completes."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    names = list(metadata_table_schema_registry())
    attempted = []

    def read_table(table_name, **_kwargs):
        attempted.append(table_name)
        raise ValueError("Delta log is corrupt")

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)

    with pytest.raises(RuntimeError, match=f"FabricOps metadata setup failed for {len(names)} table"):
        setup_metadata_tables(
            spark=object(), config=framework_config(), env="dev", verbose=False, raise_on_failure=True
        )

    assert attempted[: len(names)] == names


def test_setup_metadata_tables_verbose_false_is_silent(monkeypatch, capsys):
    """Verify quiet mode prints nothing while still returning details."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

        def where(self, _expr):
            return self

        def limit(self, _value):
            return self

        def take(self, _value):
            return []

    monkeypatch.setattr(
        setup_module,
        "read_lakehouse_table_core",
        lambda table_name, **_kwargs: Table(registry[table_name].fieldNames()),
    )

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev", verbose=False)

    assert capsys.readouterr().out == ""
    assert result["status"] == "ready"
    assert result["data_agreement"]["active_steward_count"] == 0
