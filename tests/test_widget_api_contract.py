"""Focused regression tests for public widget API naming and display usage."""

from __future__ import annotations

import re
from pathlib import Path

import fabricops_kit
import fabricops_kit.data_quality as data_quality

WIDGET_MODULES = [
    Path("src/fabricops_kit/data_agreement.py"),
    Path("src/fabricops_kit/business_context.py"),
    Path("src/fabricops_kit/data_governance.py"),
    Path("src/fabricops_kit/data_quality.py"),
]

RENAMED_WIDGET_EXPORTS = {
    "widget_select_agreement",
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
    "widget_render_agreement_intake_app",
    "widget_review_business_context",
    "widget_review_governance",
    "widget_review_dq_rules",
    "widget_review_dq_rule_deactivations",
}

REMOVED_WIDGET_EXPORTS = {
    "select_agreement",
    "render_data_steward_widget",
    "render_data_agreement_widget",
    "render_agreement_evidence_widget",
    "render_agreement_intake_app",
    "review_business_context",
    "review_governance",
    "review_dq_rules",
    "review_dq_rule_deactivations",
    "run_dq_rule_review_widget",
}

EXPECTED_FABRIC_DISPLAY_CALLS = {
    "03_pc_agreement_pipeline_template.ipynb": {
        "display(registration_context)",
        "display(source_profile)",
        "display(output_profile)",
        "display(run_summary)",
    },
    "04_gov_agreement_dataset_table.ipynb": {"display(metadata_dq_rules)"},
}


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_widget_renamed_exports_are_public() -> None:
    assert RENAMED_WIDGET_EXPORTS <= set(fabricops_kit.__all__)
    for name in RENAMED_WIDGET_EXPORTS:
        assert hasattr(fabricops_kit, name)


def test_old_widget_names_are_not_exported() -> None:
    assert not (REMOVED_WIDGET_EXPORTS & set(fabricops_kit.__all__))
    for name in REMOVED_WIDGET_EXPORTS:
        assert not hasattr(fabricops_kit, name)


def test_run_dq_rule_review_widget_no_longer_exists() -> None:
    assert not hasattr(data_quality, "run_dq_rule_review_widget")
    assert "def run_dq_rule_review_widget" not in _source(Path("src/fabricops_kit/data_quality.py"))


def test_widget_modules_do_not_import_display_function_directly() -> None:
    for path in WIDGET_MODULES:
        text = _source(path)
        assert "from IPython.display import display" not in text
        assert "from IPython import display as ip" in text


def test_widget_modules_do_not_use_legacy_ipython_display_aliases() -> None:
    for path in WIDGET_MODULES:
        text = _source(path)
        assert "ipydisplay" not in text
        assert "ipy_display" not in text


def test_widget_rendering_uses_ip_display() -> None:
    display_calls = []
    for path in WIDGET_MODULES:
        display_calls.extend(re.findall(r"\bip\.display\(", _source(path)))
    assert len(display_calls) >= 7


def test_notebook_dataframe_display_calls_remain_fabric_native() -> None:
    for notebook_name, expected_calls in EXPECTED_FABRIC_DISPLAY_CALLS.items():
        text = _source(Path("templates/notebooks") / notebook_name)
        for expected_call in expected_calls:
            assert expected_call in text
