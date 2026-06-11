from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from fabricops_kit.config import (
    DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE,
    DataAgreementConfig,
    PathConfig,
    _validate_metadata_table_registration,
    setup_metadata_tables,
    setup_notebook,
)
from tests.helpers import framework_config

pytestmark = pytest.mark.unit


def _notebook_dq_prompt_template() -> str:
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "DQ_RULE_SUGGESTION_PROMPT_TEMPLATE" not in source:
            continue
        tree = ast.parse(source)
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "DQ_RULE_SUGGESTION_PROMPT_TEMPLATE"
                for target in node.targets
            ):
                continue
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "strip"
            ):
                value = node.value.func.value
            else:
                value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value.strip()
    raise AssertionError("DQ_RULE_SUGGESTION_PROMPT_TEMPLATE assignment not found in 00_env_config.ipynb")


def test_dq_ai_suggestion_prompt_guidance_stays_aligned_with_notebook_template():
    from fabricops_kit.governance_review import DQ_RULE_TYPES

    prompts = {
        "package default": DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE,
        "00_env_config notebook": _notebook_dq_prompt_template(),
    }
    assert prompts["package default"] == prompts["00_env_config notebook"]

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
        "Schema guardrails and source stability are separate FabricOps layers",
    ]

    for prompt_name, prompt in prompts.items():
        for required in required_strings:
            assert required in prompt, f"{prompt_name} DQ prompt missing {required!r}"
        for rule_type in DQ_RULE_TYPES:
            assert rule_type in prompt, f"{prompt_name} DQ prompt missing rule_type {rule_type!r}"


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
    assert result["registration_validation"]["status"] == "ready"


def test_metadata_registration_validation_uses_show_tables_against_metadata_lakehouse():
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
    assert "Unidentified" in result["warnings"][0]


def test_governance_review_imports_current_prompt_constants():
    import fabricops_kit.governance_review as governance_review

    assert governance_review.BUSINESS_CONTEXT_PROMPT.strip()
    assert governance_review.PDPA_PERSONAL_IDENTIFIER_PROMPT.strip()
