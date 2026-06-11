from __future__ import annotations

import json
from pathlib import Path

import pytest

from fabricops_kit.config import (
    AIPromptConfig,
    DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE,
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
    setup_metadata_tables,
    setup_notebook,
)
from tests.helpers import framework_config, store

pytestmark = pytest.mark.unit


def test_dq_ai_suggestion_prompt_guidance_stays_in_package_defaults():
    from fabricops_kit.governance_review import DQ_RULE_TYPES

    prompt = DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE
    required_strings = [
        "23",
        "FabricOps-native DQ rule types",
        "unique_combination",
        "accepted_values",
        "regex_match",
        "value_when",
        "expression_true",
        "Custom expression",
        "Rule selection principles",
        "Data type / constraint-shape guidance",
        "required parameters for all 23 rule types",
        "Priority guide",
        "Evidence guidance",
        "Do not invent rule types",
        "Do not invent columns",
        "Return valid JSON only",
        "Schema guardrails and profile behavior guardrails are separate FabricOps layers",
    ]

    for required in required_strings:
        assert required in prompt, f"package DQ prompt missing {required!r}"
    for rule_type in DQ_RULE_TYPES:
        assert rule_type in prompt, f"package DQ prompt missing rule_type {rule_type!r}"


def test_ai_prompt_config_uses_only_implemented_prompt_defaults():
    prompts = AIPromptConfig()

    assert prompts.business_context_prompt_template.strip()
    assert prompts.dq_rule_suggestion_prompt_template == DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE
    assert prompts.governance_personal_identifier_prompt_template.strip()
    assert not hasattr(prompts, "governance_candidate_prompt_template")
    assert not hasattr(prompts, "governance_review_prompt_template")


def test_env_config_template_does_not_expose_prompt_boilerplate_or_unused_defaults():
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "AI_PROMPTS = AIPromptConfig()" in source
    assert "DQ_RULE_SUGGESTION_PROMPT_TEMPLATE =" not in source
    assert "GOVERNANCE_CANDIDATE_PROMPT_TEMPLATE" not in source
    assert "GOVERNANCE_REVIEW_PROMPT_TEMPLATE" not in source
    assert "QUALITY_CONFIG = QualityConfig()" not in source
    assert "GOVERNANCE_CONFIG = GovernanceConfig()" not in source
    assert "REVIEW_WORKFLOW_CONFIG = ReviewWorkflowConfig()" not in source
    assert "LINEAGE_CONFIG = LineageConfig()" not in source


def test_framework_config_defaults_framework_only_sections_when_omitted():
    config = FrameworkConfig(
        path_config=PathConfig(paths={"dev": {"source": store()}}),
        notebook_runtime_config=NotebookRuntimeConfig(),
        ai_prompt_config=AIPromptConfig(),
    )

    assert isinstance(config.quality_config, QualityConfig)
    assert isinstance(config.governance_config, GovernanceConfig)
    assert isinstance(config.review_workflow_config, ReviewWorkflowConfig)
    assert isinstance(config.lineage_config, LineageConfig)


def test_dict_framework_config_defaults_framework_only_sections_when_omitted():
    config = setup_notebook.__globals__["_validate_framework_config"]({
        "path_config": PathConfig(paths={"dev": {"source": store(), "unified": store(name="unified")}}),
        "notebook_runtime_config": NotebookRuntimeConfig(),
        "ai_prompt_config": AIPromptConfig(),
    })

    assert isinstance(config.quality_config, QualityConfig)
    assert isinstance(config.governance_config, GovernanceConfig)
    assert isinstance(config.review_workflow_config, ReviewWorkflowConfig)
    assert isinstance(config.lineage_config, LineageConfig)


def test_framework_config_keeps_type_validation_for_present_defaulted_sections():
    with pytest.raises(ValueError, match="quality_config must be a QualityConfig object"):
        setup_notebook.__globals__["_validate_framework_config"]({
            "path_config": PathConfig(paths={"dev": {"source": store()}}),
            "notebook_runtime_config": NotebookRuntimeConfig(),
            "ai_prompt_config": AIPromptConfig(),
            "quality_config": object(),
        })


def test_setup_notebook_resolves_environment_paths_and_reports_invalid_targets(fake_notebookutils):
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


def test_setup_metadata_tables_delegates_v1_metadata_setup(monkeypatch):
    calls = []

    def data_agreement_setup(**kwargs):
        calls.append(("data_agreement", kwargs))
        return {"status": "ready", "created_tables": []}

    def notebook_registry_setup(**kwargs):
        calls.append(("notebook_registry", kwargs))
        return {"status": "ready", "created_tables": []}

    def governance_setup(**kwargs):
        calls.append(("governance", kwargs))
        return {"status": "ready", "created_tables": []}

    monkeypatch.setattr("fabricops_kit.data_agreement._setup_data_agreement_tables", data_agreement_setup)
    monkeypatch.setattr("fabricops_kit.metadata._setup_notebook_registry_table", notebook_registry_setup)
    monkeypatch.setattr("fabricops_kit.governance_review._setup_governance_metadata_tables", governance_setup)
    monkeypatch.setattr("fabricops_kit.config._get_active_metadata_tables", lambda config: ["METADATA_DATA_STEWARD"])
    monkeypatch.setattr(
        "fabricops_kit.config._validate_metadata_table_registration",
        lambda **kwargs: {"status": "ready", "missing_tables": [], "expected_tables": kwargs["expected_tables"]},
    )

    config = framework_config()
    spark = object()
    result = setup_metadata_tables(spark=spark, config=config, env="dev", require_active_steward=True)

    assert result["status"] == "ready"
    assert [name for name, _ in calls] == ["data_agreement", "notebook_registry", "governance"]
    assert calls[0][1] == {"spark": spark, "config": config, "env": "dev", "require_active_steward": True}
    assert calls[1][1] == {"spark": spark, "config": config, "env": "dev"}
    assert calls[2][1] == {"spark": spark, "config": config, "env": "dev"}
    assert result["active_metadata_tables"] == ["METADATA_DATA_STEWARD"]
    assert result["registration_validation"]["status"] == "ready"


def test_active_metadata_tables_are_source_driven_and_explain_optional_access_table():
    tables = _get_active_metadata_tables(framework_config())

    assert len(tables) == 11
    assert "METADATA_DATA_STEWARD" in tables
    assert "METADATA_DATA_AGREEMENT" in tables
    assert "METADATA_DATA_AGREEMENT_EVIDENCE" in tables
    assert "METADATA_NOTEBOOK_REGISTRY" in tables
    assert "METADATA_DQ_RULES" in tables
    assert "METADATA_GOVERNANCE_REVIEWS" in tables
    assert "METADATA_DATA_ACCESS" not in tables


def test_metadata_registration_validation_uses_show_tables_against_active_registry():
    class Row(dict):
        def asDict(self, recursive=True):  # noqa: N802 - mirrors Spark API
            return dict(self)

    class Result:
        def collect(self):
            return [Row(tableName="METADATA_DATA_STEWARD"), Row(tableName="METADATA_DQ_RULES")]

    class Spark:
        def __init__(self):
            self.statements = []

        def sql(self, statement):
            self.statements.append(statement)
            return Result()

    spark = Spark()
    result = _validate_metadata_table_registration(
        spark=spark,
        config=framework_config(),
        env="dev",
        expected_tables=["METADATA_DATA_STEWARD", "METADATA_DQ_RULES"],
    )

    assert result["status"] == "ready"
    assert result["missing_tables"] == []
    assert result["expected_table_count"] == 2
    assert result["optional_documented_tables"] == ["METADATA_DATA_ACCESS"]
    assert spark.statements == ["SHOW TABLES IN `lh_metadata_dev`"]


def test_metadata_registration_validation_warns_for_missing_registered_tables():
    class Result:
        def collect(self):
            return []

    class Spark:
        def sql(self, statement):
            return Result()

    result = _validate_metadata_table_registration(
        spark=Spark(),
        config=framework_config(),
        env="dev",
        expected_tables=["METADATA_DATA_STEWARD"],
    )

    assert result["status"] == "not_ready"
    assert result["missing_tables"] == ["METADATA_DATA_STEWARD"]
    assert "SHOW TABLES" in result["warnings"][0]


def test_audit_timezone_defaults_validates_and_fails_clearly():
    assert _validate_audit_timezone(None) == "UTC"
    assert _validate_audit_timezone("Asia/Singapore") == "Asia/Singapore"
    with pytest.raises(ValueError, match='Invalid FABRICOPS_AUDIT_TIMEZONE: "Singapore"'):
        _validate_audit_timezone("Singapore")


def test_framework_config_and_current_audit_timestamp_use_configured_timezone():
    config = FrameworkConfig(
        **{**framework_config().__dict__, "audit_timezone": "Asia/Singapore"}
    )

    assert config.audit_timezone == "Asia/Singapore"
    assert _current_audit_timestamp(config=config).endswith("+08:00")


def test_env_config_template_exposes_audit_timezone_setting():
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert 'FABRICOPS_AUDIT_TIMEZONE = "UTC"' in source
    assert "_validate_audit_timezone(FABRICOPS_AUDIT_TIMEZONE)" in source
    assert "audit_timezone=FABRICOPS_AUDIT_TIMEZONE" in source


def test_downstream_notebooks_use_config_aware_audit_timestamps_only():
    notebook_paths = [
        Path("templates/notebooks/01_agreement.ipynb"),
        Path("templates/notebooks/02_pipeline.ipynb"),
        Path("templates/notebooks/03_governance.ipynb"),
        Path("templates/notebooks/99_explore.ipynb"),
        Path("templates/notebooks/example_pipeline_smoke_test.ipynb"),
        Path("templates/notebooks/example_dq_rule_smoke_test.ipynb"),
    ]

    for path in notebook_paths:
        source = path.read_text(encoding="utf-8")
        assert 'FABRICOPS_AUDIT_TIMEZONE = "UTC"' not in source
        assert 'DEFAULT_AUDIT_TIMEZONE = "UTC"' not in source
        assert "datetime.now(timezone.utc)" not in source
        assert "datetime.utcnow" not in source

    pipeline_source = Path("templates/notebooks/02_pipeline.ipynb").read_text(encoding="utf-8")
    assert "PIPELINE_STARTED_AT = _current_audit_timestamp(config=CONFIG)" in pipeline_source
    assert "completed_at=_current_audit_timestamp(config=CONFIG)" in pipeline_source


def test_governance_review_imports_current_prompt_constants():
    import fabricops_kit.governance_review as governance_review

    assert governance_review.BUSINESS_CONTEXT_PROMPT.strip()
    assert governance_review.PDPA_PERSONAL_IDENTIFIER_PROMPT.strip()
