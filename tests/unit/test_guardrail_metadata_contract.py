"""Stage 4A contracts for normalized Guardrail metadata."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from fabricops_kit.pipeline import guardrail_shared, guardrails_shared
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit

_AUDIT_COLUMNS = [name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS]

_GUARDRAIL_COLUMNS = [
    "guardrail_rule_id",
    "guardrail_version",
    "table_id",
    "column_id",
    "environment_name",
    "guardrail_type",
    "rule_id",
    "rule_type",
    "rule_parameters_json",
    "severity",
    "is_active",
    *_AUDIT_COLUMNS,
]

_RESULT_COLUMNS = [
    "guardrail_result_id",
    "guardrail_rule_id",
    "guardrail_version",
    "run_id",
    "environment_name",
    "status",
    "can_continue",
    "severity",
    "reason",
    "result_payload_json",
    *_AUDIT_COLUMNS,
]

_ROW_RESULT_COLUMNS = [
    "guardrail_row_result_id",
    "guardrail_result_id",
    "row_identity",
    "involved_columns_json",
    "failed_values_json",
    "failure_reason",
    *_AUDIT_COLUMNS,
]

_SOURCE_OBSERVATION_COLUMNS = [
    "observation_id",
    "table_id",
    "environment_name",
    "partition_value",
    "row_count",
    "min_change_value",
    "max_change_value",
    "is_present",
    *_AUDIT_COLUMNS,
]


def _field_names(table_name: str) -> list[str]:
    return metadata_table_schema_registry()[table_name].fieldNames()


def _audit() -> dict[str, object]:
    return {
        "_committed_by": "tester@example.com",
        "_committed_at": datetime(2026, 8, 18, 12, 0, 0),
        "_workspace_id": "workspace-id",
        "_workspace_name": "workspace-name",
        "_notebook_id": "notebook-id",
        "_notebook_name": "02_pipeline",
        "_metadata_lakehouse_name": "metadata",
        "_activity_id": "activity-id",
    }


def test_guardrail_metadata_tables_have_exact_stage4a_columns() -> None:
    """Lock the exact physical columns of all three normalized Guardrail tables."""
    assert _field_names("METADATA_GUARDRAIL") == _GUARDRAIL_COLUMNS
    assert _field_names("METADATA_GUARDRAIL_RESULTS") == _RESULT_COLUMNS
    assert _field_names("METADATA_GUARDRAIL_ROW_RESULTS") == _ROW_RESULT_COLUMNS


def test_guardrail_metadata_uses_canonical_parent_identities() -> None:
    """Verify each metadata layer stores only the relational identity it owns."""
    guardrail_fields = set(_field_names("METADATA_GUARDRAIL"))
    result_fields = set(_field_names("METADATA_GUARDRAIL_RESULTS"))
    row_result_fields = set(_field_names("METADATA_GUARDRAIL_ROW_RESULTS"))

    assert {"table_id", "column_id"} <= guardrail_fields
    assert {"guardrail_rule_id", "guardrail_version"} <= result_fields
    assert "guardrail_result_id" in row_result_fields
    assert "guardrail_rule_id" not in row_result_fields
    assert "table_id" not in result_fields | row_result_fields
    assert "column_id" not in result_fields | row_result_fields
    assert "run_id" not in row_result_fields


def test_obsolete_guardrail_identity_and_review_fields_are_absent() -> None:
    """Verify Stage 4A removes duplicated identity and obsolete review workflow fields."""
    obsolete = {
        "configuration_version",
        "metadata_table_key",
        "metadata_column_key",
        "dataset_name",
        "table_name",
        "column_name",
        "rule_key",
        "result_id",
        "review_status",
        "review_state",
        "reviewed_by",
        "reviewed_at",
        "review_decision",
        "review_comment",
        "approval_required",
        "approval_bypassed",
        "requires_governance_review",
        "requires_post_review",
        "bypass_reason",
        "governance_mode",
        "approval_policy",
        "supersedes_rule_id",
        "action_type",
        "source_notebook_type",
        "created_by_role",
    }
    for table_name in (
        "METADATA_GUARDRAIL",
        "METADATA_GUARDRAIL_RESULTS",
        "METADATA_GUARDRAIL_ROW_RESULTS",
    ):
        assert obsolete.isdisjoint(_field_names(table_name))


def test_standard_eight_audit_fields_are_present_on_all_guardrail_tables() -> None:
    """Verify every normalized Guardrail table ends with the standard audit contract."""
    assert len(_AUDIT_COLUMNS) == 8
    for table_name in (
        "METADATA_GUARDRAIL",
        "METADATA_GUARDRAIL_RESULTS",
        "METADATA_GUARDRAIL_ROW_RESULTS",
    ):
        assert _field_names(table_name)[-8:] == _AUDIT_COLUMNS


def test_canonical_rule_writer_emits_only_physical_contract_and_stable_json(monkeypatch) -> None:
    """Verify authored rule rows are normalized and rule JSON is deterministic."""
    monkeypatch.setattr(guardrail_shared, "build_runtime_audit_fields", lambda **_kwargs: _audit())
    source = {
        "guardrail_rule_id": "rule-1",
        "guardrail_version": 3,
        "table_id": "table-id",
        "column_id": "column-id",
        "metadata_table_key": "legacy-table-id",
        "metadata_column_key": "legacy-column-id",
        "environment_name": "dev",
        "guardrail_type": "dq",
        "rule_id": "missing_values",
        "rule_type": "missing_values",
        "rule_parameters_json": '{"z":2,"maximum_null_percent":0,"a":1}',
        "severity": "warning",
        "is_active": True,
        "review_status": "approved",
        "table_name": "orders",
    }

    row = guardrail_shared.canonical_guardrail_rule_record(source, config=framework_config(), env="dev")

    assert list(row) == _GUARDRAIL_COLUMNS
    assert row["guardrail_version"] == 3
    assert row["table_id"] == "table-id"
    assert row["column_id"] == "column-id"
    assert row["rule_parameters_json"] == '{"a":1,"maximum_null_percent":0,"z":2}'
    assert json.loads(row["rule_parameters_json"])["maximum_null_percent"] == 0
    assert "configuration_version" not in row
    assert "metadata_table_key" not in row
    assert "metadata_column_key" not in row
    assert "review_status" not in row
    assert "table_name" not in row


def test_runtime_result_writer_records_exact_guardrail_revision(monkeypatch) -> None:
    """Verify runtime result persistence identifies the exact Guardrail revision."""
    writes = []
    monkeypatch.setattr(guardrails_shared, "build_runtime_audit_fields", lambda **_kwargs: _audit())
    monkeypatch.setattr(guardrails_shared, "configured_lakehouse_schema", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        guardrails_shared,
        "write_lakehouse_table_core",
        lambda frame, table, **_kwargs: writes.append((table, frame.rows[0])),
    )

    guardrails_shared.write_guardrail_result_row(
        spark_session=FakeSpark(),
        config=framework_config(),
        env="dev",
        run_id="run-1",
        dataset_name="ignored",
        table_name="ignored",
        store_type="lakehouse",
        layer="raw",
        schema_name=None,
        guardrail_type="schema",
        rule_type="minimum_required",
        result={
            "guardrail_rule_id": "rule-1",
            "guardrail_version": 3,
            "status": "passed",
            "can_continue": True,
            "severity": "blocking",
            "reason": "Rule passed.",
            "expected": {"b": 2, "a": 1},
        },
    )

    table_name, row = writes[0]
    assert table_name == "METADATA_GUARDRAIL_RESULTS"
    assert list(row) == _RESULT_COLUMNS
    assert row["guardrail_rule_id"] == "rule-1"
    assert row["guardrail_version"] == 3
    assert row["run_id"] == "run-1"
    assert json.loads(row["result_payload_json"])["expected"] == {"a": 1, "b": 2}
    assert "metadata_table_key" not in row
    assert "rule_key" not in row


def test_runtime_result_writer_rejects_missing_guardrail_version(monkeypatch) -> None:
    """Every persisted result must identify one exact Guardrail revision."""
    monkeypatch.setattr(guardrails_shared, "build_runtime_audit_fields", lambda **_kwargs: _audit())

    with pytest.raises(ValueError, match="guardrail_version is required"):
        guardrails_shared.write_guardrail_result_row(
            spark_session=FakeSpark(),
            config=framework_config(),
            env="dev",
            run_id="run-1",
            dataset_name="",
            table_name="",
            store_type="",
            layer="",
            guardrail_type="schema",
            rule_type="minimum_required",
            result={"guardrail_rule_id": "rule-1", "status": "passed"},
        )


def test_source_observation_uses_standard_audit_timestamp_only() -> None:
    """Source Observation no longer duplicates _committed_at as observed_at."""
    assert _field_names("METADATA_SOURCE_OBSERVATION") == _SOURCE_OBSERVATION_COLUMNS
    assert "observed_at" not in _SOURCE_OBSERVATION_COLUMNS
    assert "_committed_at" in _SOURCE_OBSERVATION_COLUMNS
