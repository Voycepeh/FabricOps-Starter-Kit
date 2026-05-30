"""Regression checks for copy-ready notebook-template package API usage."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import fabricops_kit

TEMPLATES = Path("templates/notebooks")


def _code(name: str) -> str:
    notebook = json.loads((TEMPLATES / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "code")


def _tree(name: str) -> ast.Module:
    source = "\n".join(line for line in _code(name).splitlines() if not line.lstrip().startswith("%"))
    return ast.parse(source)


def _name(node: ast.AST) -> str | None:
    return node.id if isinstance(node, ast.Name) else node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def test_00_env_config_defines_env_name_alias():
    assert "ENV_NAME = ENV" in _code("00_env_config.ipynb")


def test_02_ex_imports_only_public_fabricops_kit_functions():
    imported = {
        alias.name
        for node in _tree("02_ex_agreement_topic.ipynb").body
        if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit"
        for alias in node.names
    }
    assert imported <= set(fabricops_kit.__all__)
    assert "_build_dq_rule_deactivation_metadata_df" not in imported


def test_02_ex_register_and_source_read_calls_match_public_signatures():
    calls = [node for node in ast.walk(_tree("02_ex_agreement_topic.ipynb")) if isinstance(node, ast.Call)]
    register = next(node for node in calls if _name(node.func) == "register_current_notebook")
    assert "metadata_path" in {keyword.arg for keyword in register.keywords}
    assert "metadata_store" not in {keyword.arg for keyword in register.keywords}

    source_read = next(
        node for node in calls
        if _name(node.func) == "read_lakehouse_table"
        and len(node.args) >= 4
        and _name(node.args[2]) == "source"
        and _name(node.args[3]) == "table_name"
    )
    assert [_name(argument) for argument in source_read.args[:4]] == ["CONFIG", "ENV", "source", "table_name"]
    assert {_name(keyword.value) for keyword in source_read.keywords if keyword.arg == "spark_session"} == {"spark"}


def test_03_pc_warehouse_reads_match_public_signature():
    calls = [node for node in ast.walk(_tree("03_pc_agreement_pipeline_template.ipynb")) if isinstance(node, ast.Call) and _name(node.func) == "read_warehouse_table"]
    assert calls
    for call in calls:
        assert [_name(argument) for argument in call.args[:5]] in (
            ["CONFIG", "ENV_NAME", "SOURCE_LAYER", "dbo", "SOURCE_TABLE"],
            ["CONFIG", "ENV_NAME", "TARGET_LAYER", "dbo", "TARGET_TABLE"],
        )
        assert {_name(keyword.value) for keyword in call.keywords if keyword.arg == "spark_session"} == {"spark"}
