import ast
import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import fabricops_kit as kit
from fabricops_kit import stop_if_failed, validate_schema
from fabricops_kit.drift import SchemaDriftError, _check_schema


class _FakeDataFrame:
    def __init__(self, fields):
        self.schema = SimpleNamespace(fields=[SimpleNamespace(name=name, dataType=data_type) for name, data_type in fields])
        self.columns = [name for name, _ in fields]


def _df(extra=()):
    return _FakeDataFrame([
        ("customer_id", "LongType()"),
        ("event_ts", "StringType()"),
        ("amount", "DecimalType(18,2)"),
        *extra,
    ])


EXPECTED = {"customer_id": "bigint", "event_ts": "string", "amount": "decimal(18,2)"}


def test_validate_schema_strict_passes_matching_schema():
    result = validate_schema(_df(), EXPECTED, preset="strict")

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["checks"] == []


def test_validate_schema_strict_rejects_new_columns():
    result = validate_schema(_df([("temporary_value", "StringType()")]), EXPECTED, preset="strict")

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["unexpected_columns"] == ["temporary_value"]


def test_validate_schema_allow_new_columns_permits_and_reports_new_columns():
    result = validate_schema(_df([("temporary_value", "StringType()")]), EXPECTED, preset="allow_new_columns")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["unexpected_columns"] == ["temporary_value"]
    assert next(check for check in result["checks"] if check["check"] == "unexpected_column")["status"] == "warning"


def test_validate_schema_monitor_only_never_blocks():
    result = validate_schema(_df([("temporary_value", "StringType()")]), {**EXPECTED, "missing": "string", "amount": "double"}, preset="monitor_only")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["missing_columns"] == ["missing"]
    assert result["datatype_mismatches"] == [{"column": "amount", "expected": "double", "actual": "decimal(18,2)"}]


def test_validate_schema_invalid_preset_errors():
    with pytest.raises(ValueError, match="preset must be one of"):
        validate_schema(_df(), EXPECTED, preset="loose")


def test_internal_schema_logic_still_normalizes_real_pandas_dataframe_dtypes():
    df = pd.DataFrame(
        {
            "customer_id": pd.Series([1, 2], dtype="int64"),
            "amount": pd.Series([1.5, 2.5], dtype="float64"),
            "label": pd.Series(["a", "b"], dtype="object"),
            "event_ts": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        }
    )

    result = _check_schema(
        df,
        {
            "customer_id": "bigint",
            "amount": "double",
            "label": "string",
            "event_ts": "timestamp",
        },
        action="observe",
    )

    assert result["passed"] is True
    assert result["datatype_mismatches"] == []


def test_stop_if_failed_raises_only_when_can_continue_false():
    stop_if_failed({"status": "passed", "can_continue": True})
    stop_if_failed({"status": "warning", "can_continue": True})
    stop_if_failed({"status": "no_baseline", "can_continue": True})
    stop_if_failed({"result": {"status": "warning", "can_continue": True}})

    with pytest.raises(SchemaDriftError, match="failed"):
        stop_if_failed({"status": "failed", "can_continue": False, "message": "Blocked by policy."})


def test_top_level_public_api_uses_simplified_guardrails():
    assert "validate_schema" in kit.__all__
    assert "monitor_data_changes" in kit.__all__
    assert "stop_if_failed" in kit.__all__
    assert "profile_dataframe" in kit.__all__
    removed = {
        "check_schema",
        "check_profile_drift",
        "load_latest_profile",
        "default_profile_drift_policy",
        "extract_numeric_distribution_bin_edges",
        "extract_categorical_distribution_categories",
        "assert_no_blocking_profile_drift",
    }
    assert removed.isdisjoint(set(kit.__all__))
    for name in removed:
        assert not hasattr(kit, name)


def test_03_pc_uses_simplified_functions_and_guidance_markdown():
    notebook = json.loads(Path("templates/notebooks/03_pc_agreement_pipeline_template.ipynb").read_text(encoding="utf-8"))
    all_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])
    code_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "code")
    markdown_source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "markdown")

    assert "## Choose pipeline checks" in markdown_source
    assert "source_schema_result = validate_schema(" in code_source
    assert "source_change_result = monitor_data_changes(" in code_source
    assert "target_schema_result = validate_schema(" in code_source
    assert "target_change_result = monitor_data_changes(" in code_source
    assert "stop_if_failed(source_schema_result)" in code_source
    assert "stop_if_failed(source_change_result)" in code_source
    assert "stop_if_failed(target_schema_result)" in code_source
    assert "stop_if_failed(target_change_result)" in code_source
    assert 'SOURCE_SCHEMA_CHECK = "allow_new_columns"' in code_source
    assert 'TARGET_SCHEMA_CHECK = "strict"' in code_source
    assert 'SOURCE_DATA_CHANGE_CHECK = "changing_data"' in code_source
    assert 'TARGET_DATA_CHANGE_CHECK = "changing_data"' in code_source
    assert "SOURCE_DATA_CHANGE_OVERRIDES = {}" in code_source
    assert "TARGET_DATA_CHANGE_OVERRIDES = {}" in code_source
    assert code_source.index("source_schema_result = validate_schema(") < code_source.index("source_change_result = monitor_data_changes(")
    assert code_source.index("source_change_result = monitor_data_changes(") < code_source.index("df_transformed = df_source")
    assert code_source.index("target_schema_result = validate_schema(") < code_source.index("target_change_result = monitor_data_changes(")
    assert code_source.index("target_change_result = monitor_data_changes(") < code_source.index("write_lakehouse_table(df_output")
    for helper in [
        "load_latest_profile(",
        "extract_numeric_distribution_bin_edges(",
        "extract_categorical_distribution_categories(",
        "check_profile_drift(",
        "assert_no_blocking_profile_drift(",
        "check_schema(",
    ]:
        assert helper not in all_source


def test_03_pc_code_cells_parse_as_python_ast():
    notebook = json.loads(Path("templates/notebooks/03_pc_agreement_pipeline_template.ipynb").read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell.get("source", []))
        if source.lstrip().startswith("%"):
            continue
        ast.parse(source, filename=f"03_pc_cell_{index}.py")
