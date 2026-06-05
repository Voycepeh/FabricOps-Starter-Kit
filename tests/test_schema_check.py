import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import fabricops_kit as kit
from fabricops_kit.drift import SchemaDriftError, check_schema


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


def test_check_schema_matching_columns_and_datatypes_pass():
    result = check_schema(_df(), EXPECTED, action="observe")

    assert result["passed"] is True
    assert result["missing_columns"] == []
    assert result["unexpected_columns"] == []
    assert result["datatype_mismatches"] == []


def test_check_schema_normalizes_real_pandas_dataframe_dtypes():
    df = pd.DataFrame(
        {
            "customer_id": pd.Series([1, 2], dtype="int64"),
            "amount": pd.Series([1.5, 2.5], dtype="float64"),
            "label": pd.Series(["a", "b"], dtype="object"),
            "event_ts": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        }
    )

    result = check_schema(
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


def test_check_schema_reports_missing_columns():
    result = check_schema(_FakeDataFrame([("customer_id", "LongType()")]), EXPECTED, action="observe")

    assert result["passed"] is False
    assert result["missing_columns"] == ["event_ts", "amount"]


def test_check_schema_reports_unexpected_columns():
    result = check_schema(_df([("temporary_value", "StringType()")]), EXPECTED, action="observe")

    assert result["passed"] is False
    assert result["unexpected_columns"] == ["temporary_value"]


def test_check_schema_allows_extra_columns_when_configured():
    result = check_schema(_df([("temporary_value", "StringType()")]), EXPECTED, allow_extra_columns=True, action="observe")

    assert result["passed"] is True
    assert result["unexpected_columns"] == []


def test_check_schema_reports_datatype_mismatches():
    result = check_schema(_df(), {**EXPECTED, "amount": "double"}, action="observe")

    assert result["passed"] is False
    assert result["datatype_mismatches"] == [{"column": "amount", "expected": "double", "actual": "decimal(18,2)"}]


def test_check_schema_check_types_false_skips_datatype_comparison():
    result = check_schema(_df(), {**EXPECTED, "amount": "double"}, check_types=False, action="observe")

    assert result["passed"] is True
    assert result["datatype_mismatches"] == []


def test_check_schema_observe_returns_failed_result():
    result = check_schema(_df(), {**EXPECTED, "missing": "string"}, action="observe")

    assert result["passed"] is False
    assert "missing" in result["missing_columns"]


def test_check_schema_warn_emits_warning():
    with pytest.warns(UserWarning, match="Schema check failed"):
        result = check_schema(_df(), {**EXPECTED, "missing": "string"}, action="warn")

    assert result["passed"] is False


def test_check_schema_fail_raises_schema_drift_error():
    with pytest.raises(SchemaDriftError, match="Schema check failed"):
        check_schema(_df(), {**EXPECTED, "missing": "string"}, action="fail")


def test_03_pc_calls_check_schema_for_source_and_target():
    notebook = json.loads(Path("templates/notebooks/03_pc_agreement_pipeline_template.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "check_schema," in source
    assert "source_schema_result = check_schema(" in source
    assert "target_schema_result = check_schema(" in source
    assert "EXPECTED_SOURCE_COLUMNS" in source
    assert "EXPECTED_TARGET_COLUMNS" in source


def test_03_pc_target_schema_check_happens_before_runtime_audit_columns():
    notebook = json.loads(Path("templates/notebooks/03_pc_agreement_pipeline_template.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert source.index("target_schema_result = check_schema(") < source.index("audit_fields = build_runtime_audit_fields")
    assert source.index("source_schema_result = check_schema(") < source.index("df_transformed = df_source")


def test_obsolete_schema_drift_exports_and_references_are_removed():
    obsolete = {
        "build_schema_snapshot",
        "compare_schema_snapshots",
        "assert_no_blocking_schema_drift",
        "check_" + "schema_drift",
        "default_schema_drift_policy",
    }

    assert "check_schema" in kit.__all__
    assert "SchemaDriftError" in kit.__all__
    assert obsolete.isdisjoint(set(kit.__all__))
    for name in obsolete:
        assert not hasattr(kit, name)

    searched_paths = [Path("src/fabricops_kit"), Path("tests"), Path("templates")]
    references = []
    for base in searched_paths:
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".ipynb", ".md"} and path.name != Path(__file__).name:
                text = path.read_text(encoding="utf-8")
                for name in obsolete:
                    if name in text:
                        references.append(f"{path}:{name}")
    assert references == []


def test_03_pc_runs_source_and_target_profile_drift_guardrails():
    notebook = json.loads(Path("templates/notebooks/03_pc_agreement_pipeline_template.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "code")

    assert "ENABLE_DATA_DRIFT = True" in source
    assert 'SOURCE_BEHAVIOUR = "evolving"' in source
    assert 'PROFILE_BASELINE_MODE = "latest_successful"' in source
    assert "ENABLE_SOURCE_CHANGE_CHECK = False" in source
    assert "SOURCE_CHANGE_STRATEGY = None" in source
    assert "DATA_DRIFT_COLUMNS = None" in source
    assert "EXECUTION_TIMESTAMP = datetime.now(timezone.utc).strftime" in source
    assert 'RUN_ID = f"{PIPELINE_NAME}_{ENV_NAME}_{EXECUTION_TIMESTAMP}"' in source
    assert "SOURCE_BEHAVIOUR must be one of: evolving, stable" in source
    assert "PROFILE_BASELINE_MODE must be one of: latest_successful, approved" in source
    assert "source_baseline_profile = load_latest_profile(" in source
    assert "baseline_mode=PROFILE_BASELINE_MODE" in source
    assert 'profile_stage="source"' in source
    assert "source_drift = check_profile_drift(" in source
    assert "assert_no_blocking_profile_drift(source_drift)" in source
    assert "target_baseline_profile = load_latest_profile(" in source
    assert 'profile_stage="target"' in source
    assert "target_drift = check_profile_drift(" in source
    assert "assert_no_blocking_profile_drift(target_drift)" in source
    assert "extract_categorical_distribution_categories(source_baseline_profile)" in source
    assert 'SOURCE_BEHAVIOUR == "evolving"' in source
    assert "skipped_no_source_change" in source
    assert "BASELINE_STATUS" in source
    assert "approved" in source
    assert source.index("source_drift = check_profile_drift(") < source.index("write_lakehouse_table(\n    source_catalogue_evidence")
    assert source.index("target_drift = check_profile_drift(") < source.index("write_lakehouse_table(df_output")
    assert source.index("target_drift = check_profile_drift(") < source.index("write_lakehouse_table(\n    output_catalogue_evidence")
