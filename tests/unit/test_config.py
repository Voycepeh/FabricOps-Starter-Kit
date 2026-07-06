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
    get_fabric_context,
    setup_metadata_tables,
    setup_notebook,
)
from fabricops_kit.config import FabricStore
from fabricops_kit.config.shared import (
    get_current_audit_timestamp,
    _get_active_metadata_tables,
    _validate_audit_timezone,
    validate_framework_config,
    _validate_metadata_table_registration,
    get_default_fabric_context,
    resolve_fabric_context,
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
        "metadata_schema: 'str | None' = None, require_active_steward: 'bool' = False) -> 'dict[str, Any]'"
    )
    assert setup_notebook.__module__ == "fabricops_kit.config.setup_notebook"
    assert setup_metadata_tables.__module__ == "fabricops_kit.config.setup_metadata_tables"


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

        def count(self):
            return 1

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
        assert options == {"overwriteSchema": "true"}
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

        def count(self):
            return 0

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

        def count(self):
            return 1

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

        def count(self):
            return 1

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

        def count(self):
            return 1

    def read_table(table_name, **_kwargs):
        return Table(registry[table_name].fieldNames())

    def write_table(*_args, **_kwargs):
        raise AssertionError("schema-compliant tables must not be rewritten")

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["created_tables"] == []


def test_setup_metadata_tables_migrates_catalogue_missing_nullable_fabric_store_target(monkeypatch):
    """Verify setup metadata tables adds nullable fabric_store_target without data loss."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()
    catalogue_columns = [
        name for name in registry["METADATA_DATA_CATALOGUE"].fieldNames() if name != "fabric_store_target"
    ]
    rows = [{"metadata_table_key": "orders", "table_name": "orders"}]
    writes = []

    class Table:
        def __init__(self, columns, rows=None):
            self.columns = list(columns)
            self.rows = list(rows or [])

        def withColumn(self, name, _value):  # noqa: N802
            return Table([*self.columns, name], [{**row, name: None} for row in self.rows])

        def select(self, *columns):
            return Table(list(columns), [{column: row.get(column) for column in columns} for row in self.rows])

        def where(self, _expr):
            return self

        def count(self):
            return 1

    tables = {name: Table(schema.fieldNames()) for name, schema in registry.items()}
    tables["METADATA_DATA_CATALOGUE"] = Table(catalogue_columns, rows)

    def read_table(table_name, **_kwargs):
        return tables[table_name]

    def write_table(df, table_name, **kwargs):
        writes.append((table_name, df, kwargs))
        tables[table_name] = df

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")

    migrated = tables["METADATA_DATA_CATALOGUE"]
    assert result["status"] == "ready"
    assert [write[0] for write in writes] == ["METADATA_DATA_CATALOGUE"]
    assert migrated.columns == registry["METADATA_DATA_CATALOGUE"].fieldNames()
    assert migrated.rows[0]["metadata_table_key"] == "orders"
    assert migrated.rows[0]["table_name"] == "orders"
    assert migrated.rows[0]["fabric_store_target"] is None
    assert writes[0][2]["mode"] == "overwrite"
    assert writes[0][2]["options"] == {"overwriteSchema": "true"}


def test_setup_metadata_tables_migrates_multiple_nullable_columns(monkeypatch):
    """Verify setup metadata tables adds multiple missing nullable columns."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])
    registry = metadata_table_schema_registry()
    missing = {"fabric_store_target", "asset_kind"}
    catalogue_columns = [name for name in registry["METADATA_DATA_CATALOGUE"].fieldNames() if name not in missing]
    writes = []

    class Table:
        def __init__(self, columns):
            self.columns = list(columns)

        def withColumn(self, name, _value):  # noqa: N802
            return Table([*self.columns, name])

        def select(self, *columns):
            return Table(list(columns))

        def where(self, _expr):
            return self

        def count(self):
            return 1

    tables = {name: Table(schema.fieldNames()) for name, schema in registry.items()}
    tables["METADATA_DATA_CATALOGUE"] = Table(catalogue_columns)
    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", lambda table_name, **_kwargs: tables[table_name])

    def write_table(df, table_name, **_kwargs):
        writes.append(table_name)
        tables[table_name] = df

    monkeypatch.setattr(setup_module, "write_lakehouse_table_core", write_table)

    setup_metadata_tables(spark=object(), config=framework_config(), env="dev")

    assert writes == ["METADATA_DATA_CATALOGUE"]
    assert tables["METADATA_DATA_CATALOGUE"].columns == registry["METADATA_DATA_CATALOGUE"].fieldNames()


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
            return Table([name for name in registry[table_name].fieldNames() if name != "fabric_store_target"])
        return Table(registry[table_name].fieldNames())

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)

    with pytest.raises(
        ValueError, match=r"METADATA_DATA_CATALOGUE is missing required column\(s\): fabric_store_target"
    ):
        setup_metadata_tables(spark=object(), config=framework_config(), env="dev")


def test_setup_metadata_tables_non_missing_read_error_includes_original_exception(monkeypatch):
    """Verify corrupt metadata tables fail with the original read exception details."""
    setup_module = __import__("fabricops_kit.config.setup_metadata_tables", fromlist=["setup_metadata_tables"])

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            raise AssertionError("corrupt table reads must not create replacement tables")

    def read_table(_table_name, **_kwargs):
        raise ValueError("Delta log is corrupt")

    monkeypatch.setattr(setup_module, "read_lakehouse_table_core", read_table)
    with pytest.raises(RuntimeError, match="Original ValueError: Delta log is corrupt"):
        setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev")


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
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    fields = set(metadata_table_schema_registry()["METADATA_DATA_CATALOGUE"].fieldNames())

    assert "profile_mode" in fields
    assert "fabric_store_target" in fields
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
    pipeline_helper_source = Path("src/fabricops_kit/widgets/widget_pipeline_bootstrap.py").read_text(encoding="utf-8")
    assert "PIPELINE = widget_pipeline_bootstrap(" in pipeline_source
    assert "_current_audit_timestamp" not in pipeline_source
    assert "PIPELINE_STARTED_AT" not in pipeline_source
    assert "pipeline_started_at=get_current_audit_timestamp()" in pipeline_helper_source


def test_config_workflow_role_boundaries_do_not_reference_removed_metadata_workflow():
    """Verify removed metadata workflow no longer participates in role metadata."""
    from scripts.generate_individual_function_reference_pages import ROLE_TAGS_BY_NAME

    assert "_setup_metadata_tables_workflow" not in ROLE_TAGS_BY_NAME
    assert "_setup_notebook_workflow" not in ROLE_TAGS_BY_NAME
    assert ROLE_TAGS_BY_NAME["_setup_metadata_table_registry"][0] == "internal_adapter"
    assert ROLE_TAGS_BY_NAME["_validate_metadata_table_registration"][0] == "internal_validator"


def test_data_agreement_widget_role_hints_keep_orchestration_as_workflow():
    """Verify agreement widget orchestration is not misclassified as an adapter."""
    from scripts.generate_individual_function_reference_pages import ROLE_TAGS_BY_NAME, _role_dependency_signals

    shared_roles = ROLE_TAGS_BY_NAME["render_maintenance_widget_shared_workflow"]

    assert shared_roles[:2] == ["internal_workflow", "shared_widget_rendering_workflow"]
    assert "internal_adapter" not in shared_roles
    assert "widget_rendering_adapter" not in shared_roles
    assert "_render_maintenance_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_data_steward_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert "_render_data_agreement_widget_workflow" not in ROLE_TAGS_BY_NAME
    assert _role_dependency_signals("public_api_entrypoint", shared_roles[0]) == ["allowed_internal_role_call"]


def test_data_agreement_widget_callable_inventory_roles_are_current():
    """Verify generated v2 callable-flow inventory reflects the widget role split."""
    import json

    flow_data = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    rows = {row["qualified_name"]: row for row in flow_data["defined_functions"]}
    assert (
        rows["fabricops_kit.widgets.shared.render_maintenance_widget_shared_workflow"]["function_type"]
        == "shared_function"
    )
    assert (
        rows["fabricops_kit.widgets.widget_render_agreement_evidence._render_agreement_evidence_widget_workflow"][
            "function_type"
        ]
        == "private_function"
    )
    assert "fabricops_kit.widgets.shared._render_agreement_evidence_widget_workflow" not in rows
    public_functions = {row["qualified_name"]: row for row in flow_data["public_functions"]}
    assert (
        public_functions["fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward"]["flow"][0][
            "function_type"
        ]
        == "public_function"
    )
    assert (
        public_functions["fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement"]["flow"][0][
            "function_type"
        ]
        == "public_function"
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
    assert Path("src/fabricops_kit/config/get_fabric_context.py").exists()
    assert Path("src/fabricops_kit/config/setup_notebook.py").exists()
    assert Path("src/fabricops_kit/config/setup_metadata_tables.py").exists()
    assert Path("src/fabricops_kit/config/shared.py").exists()
    assert config_package.__file__.endswith("config/__init__.py")
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
    assert "from fabricops_kit.config.audit import _audit_timestamp_value, build_runtime_audit_fields" in Path(
        "src/fabricops_kit/pipeline/metadata_evidence.py"
    ).read_text(encoding="utf-8")
    assert "from fabricops_kit.config.shared import build_audit_timestamp_expr, get_audit_timezone" in Path(
        "src/fabricops_kit/pipeline/shared.py"
    ).read_text(encoding="utf-8")


def test_setup_metadata_tables_uses_public_config_validation_helper_only():
    """Verify setup metadata tables avoids cross-file private helper imports."""
    source = Path("src/fabricops_kit/config/setup_metadata_tables.py").read_text(encoding="utf-8")

    assert "from .shared import FrameworkConfig, get_store, validate_framework_config" in source
    assert "_validate_framework_config" not in source
    assert (
        "from .metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_field_names, metadata_table_schema_registry"
        in source
    )


def test_canonical_metadata_schemas_include_audit_and_runtime_python_types():
    """Verify canonical metadata schemas and row coercion align with runtime writer types."""
    from datetime import date, datetime

    from fabricops_kit.config.metadata_schemas import (
        AUDIT_SCHEMA_FIELDS,
        CANONICAL_METADATA_TABLES,
        metadata_table_schema_registry,
    )
    from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types

    audit_columns = {name for name, _kind in AUDIT_SCHEMA_FIELDS}
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
        Path("src/fabricops_kit/pipeline/metadata_evidence.py"),
        Path("src/fabricops_kit/widgets/shared.py"),
        Path("src/fabricops_kit/pipeline/shared.py"),
    ]

    metadata_evidence_source = Path("src/fabricops_kit/pipeline/metadata_evidence.py").read_text(encoding="utf-8")
    assert "from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types" in metadata_evidence_source
    assert "from fabricops_kit.config.setup_metadata_tables" not in metadata_evidence_source
    assert "from .config.setup_metadata_tables" not in metadata_evidence_source

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
    """Verify generated metadata docs reflect setup_metadata_tables schema registry."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, metadata_table_schema_rows

    registry = metadata_table_schema_registry()
    generated_doc_paths = sorted(Path("docs/reference/metadata").glob("metadata_*.md"))

    assert len(generated_doc_paths) == len(registry)
    for table_name, schema in registry.items():
        expected = [
            {
                "name": row["name"],
                "type": row["type"],
                "required": "Nullable" if row["nullable"] else "Required",
            }
            for row in metadata_table_schema_rows(schema)
        ]
        assert _metadata_doc_schema_rows(table_name) == expected


def test_metadata_docs_schema_rows_preserve_non_string_types_and_audit_order():
    """Verify metadata docs render canonical non-string types and audit order."""
    from fabricops_kit.config.metadata_schemas import (
        audit_schema_fields,
        metadata_table_schema_registry,
        metadata_table_schema_rows,
    )

    registry = metadata_table_schema_registry()
    catalogue = {row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_CATALOGUE"])}
    agreement = {row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_AGREEMENT"])}
    evidence = {
        row["name"]: row["type"] for row in metadata_table_schema_rows(registry["METADATA_DATA_AGREEMENT_EVIDENCE"])
    }
    docs_catalogue = {row["name"]: row["type"] for row in _metadata_doc_schema_rows("METADATA_DATA_CATALOGUE")}

    assert agreement["start_date"] == "date"
    assert agreement["approved_usage_internal"] == "boolean"
    assert catalogue["profiled_at"] == "timestamp"
    assert catalogue["fabric_store_target"] == "string"
    assert evidence["file_size"] == "long"
    assert catalogue["null_percent"] == "double"
    assert docs_catalogue["policy_updated_at"] == "timestamp"

    for table_name, schema in registry.items():
        assert [row["name"] for row in metadata_table_schema_rows(schema)][-len(audit_schema_fields()) :] == [
            name for name, _kind in audit_schema_fields()
        ], table_name
