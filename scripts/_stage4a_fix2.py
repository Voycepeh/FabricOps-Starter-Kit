"""One-shot corrections for the Stage 4A completion pass."""

from pathlib import Path


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Expected Stage 4A text not found for {label}: {old}")
    return text.replace(old, new, 1)


def _restore_rule_audit_fields() -> None:
    path = Path("src/fabricops_kit/pipeline/guardrail_metadata.py")
    text = path.read_text()
    text = _replace_once(
        text,
        "    parameters = _parse_parameters(record)\n    return {\n",
        "    audit = build_runtime_audit_fields(config=config, env=env)\n    parameters = _parse_parameters(record)\n    return {\n",
        label="canonical rule audit resolution",
    )
    text = _replace_once(
        text,
        '        "is_active": bool(record.get("is_active", True)),\n    }\n',
        '        "is_active": bool(record.get("is_active", True)),\n        **audit,\n    }\n',
        label="canonical rule audit fields",
    )
    path.write_text(text)


def _restore_shared_guardrail_constants() -> None:
    path = Path("src/fabricops_kit/pipeline/guardrails_shared.py")
    text = path.read_text()
    if "DQ_RULE_TYPES = [" in text:
        return
    marker = "\ndef _is_spark_dataframe(dataframe) -> bool:\n"
    if marker not in text:
        raise RuntimeError("Expected shared guardrail function marker not found")
    constants = '''
_DEFAULT_STABILITY_EXCLUDE_COLUMNS = {
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}
_DEFAULT_STABILITY_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")

_ACTIVE_RULE_REVIEW_STATUSES = {"authored", "self_approved", "governance_approved", "active_pending_governance_review"}
_BYPASS_POST_REVIEW_WARNING = "Rule is active through approval bypass and requires governance post-review."
GUARDRAIL_TABLE = "METADATA_GUARDRAIL"
GUARDRAIL_CHANGE_BEHAVIOURS = ("No changes expected", "Incremental append", "Snapshot overwrite")
_GUARDRAIL_CHANGE_BEHAVIOUR_MAPPING = {
    "No changes expected": ("no_change_required", "snapshot"),
    "Incremental append": ("monitor_only", "incremental_append"),
    "Snapshot overwrite": ("monitor_only", "snapshot"),
}
DQ_RULE_TYPES = [
    "missing_values",
    "blank_text",
    "unique_values",
    "unique_combination",
    "allowed_values",
    "blocked_values",
    "value_range",
    "text_pattern",
    "required_when",
    "conditional_value",
    "compare_columns",
]
DQ_COMPARISON_OPERATORS = ("=", "!=", ">", ">=", "<", "<=")

_SOURCE_PATTERNS = {"snapshot", "incremental_append", "mutable_incremental", "versioned"}
_COMPARISON_SCOPES = {"complete", "partitions", "partial"}

'''
    path.write_text(text.replace(marker, constants + marker, 1))


def _align_writer_test_with_authoritative_module() -> None:
    path = Path("tests/unit/test_guardrail_metadata_contract.py")
    text = path.read_text()
    text = _replace_once(
        text,
        "from fabricops_kit.pipeline import guardrail_metadata\n",
        "from fabricops_kit.pipeline import guardrail_metadata, guardrails_shared\n",
        label="shared writer test import",
    )
    text = _replace_once(
        text,
        '    monkeypatch.setattr(guardrail_metadata, "build_runtime_audit_fields", lambda **_kwargs: _audit())\n    monkeypatch.setattr(guardrail_metadata, "configured_lakehouse_schema", lambda *_args, **_kwargs: None)\n    monkeypatch.setattr(\n        guardrail_metadata,\n        "write_lakehouse_table_core",\n',
        '    monkeypatch.setattr(guardrails_shared, "build_runtime_audit_fields", lambda **_kwargs: _audit())\n    monkeypatch.setattr(guardrails_shared, "configured_lakehouse_schema", lambda *_args, **_kwargs: None)\n    monkeypatch.setattr(\n        guardrails_shared,\n        "write_lakehouse_table_core",\n',
        label="shared writer monkeypatches",
    )
    path.write_text(text)


def _align_remaining_stage4a_tests() -> None:
    path = Path("tests/unit/test_observation_guardrails.py")
    text = path.read_text()
    text = text.replace(
        '        "table_name": "orders",\n        "guardrail_type": "change",',
        '        "table_name": "orders",\n        "environment_name": "dev",\n        "guardrail_type": "change",',
        1,
    )
    text = text.replace(
        '        "table_name": "orders",\n        "guardrail_type": "freshness",',
        '        "table_name": "orders",\n        "environment_name": "dev",\n        "guardrail_type": "freshness",',
        1,
    )
    path.write_text(text)

    path = Path("tests/unit/test_dq_rules.py")
    text = path.read_text().replace(
        '{"status", "can_continue", "expected_value_json", "actual_value_json"}.issubset(',
        '{"guardrail_result_id", "guardrail_rule_id", "status", "can_continue", "result_payload_json"}.issubset(',
        1,
    )
    path.write_text(text)

    path = Path("tests/unit/test_guardrail_authoring_model.py")
    text = path.read_text().replace(
        '{"actual_value_json", "result_id", "result_payload_json"}.issubset(result_fields)',
        '{"guardrail_result_id", "guardrail_rule_id", "result_payload_json"}.issubset(result_fields)',
        1,
    )
    path.write_text(text)

    path = Path("tests/unit/test_metadata.py")
    text = path.read_text()
    text = text.replace(
        '            result={"status": "failed"},\n',
        '            result={"guardrail_rule_id": "schema-rule", "status": "failed"},\n',
        1,
    )
    text = text.replace(
        '    expected = config_shared.build_metadata_table_key("lakehouse", "raw", None, "orders")\n\n',
        '',
        1,
    )
    text = text.replace(
        '            result={"status": "passed"},\n',
        '            result={"guardrail_rule_id": "schema-rule", "status": "passed"},\n',
        1,
    )
    text = text.replace(
        '    assert [frame.rows[0]["metadata_table_key"] for frame in writes] == [expected, expected]\n',
        '    assert [frame.rows[0]["guardrail_rule_id"] for frame in writes] == ["schema-rule", "schema-rule"]\n',
        1,
    )
    path.write_text(text)

    path = Path("tests/integration/test_spark_flows.py")
    text = path.read_text()
    old_toggle = '''    assert writes[0][2:4] == ("metadata", "METADATA_GUARDRAIL_RESULTS")
    row = writes[0][0].collect()[0].asDict()
    assert row["guardrail_type"] == "dq"
    assert row["_activity_id"] == "activity-dq-002"
    assert row["status"] == "passed"
'''
    text = text.replace(
        old_toggle,
        '    assert writes == []  # no orphan result is persisted when no governed DQ rule exists\n',
        1,
    )
    text = text.replace(
        '        result={"status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},\n',
        '        result={"guardrail_rule_id": "freshness-rule", "status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},\n',
        1,
    )
    old_written = '''    expected_table_key = build_metadata_table_key("lakehouse", "raw", None, "orders")
    assert written_row["metadata_table_key"] == expected_table_key
    assert written_row["environment_name"] == "dev"
    assert written_row["guardrail_type"] == "freshness"
'''
    text = text.replace(
        old_written,
        '    assert written_row["guardrail_rule_id"] == "freshness-rule"\n    assert written_row["environment_name"] == "dev"\n',
        1,
    )
    path.write_text(text)

    path = Path("tests/unit/test_widget_author_dq_rules.py")
    text = path.read_text().replace(
        '    monkeypatch.setattr(module.shared, "_write_rule_records", lambda records, **kwargs: writes.append(records))\n\n    widget = module.widget_author_dq_rules',
        '    monkeypatch.setattr(module.shared, "_write_rule_records", lambda records, **kwargs: writes.append(records))\n    monkeypatch.setattr(module, "canonical_guardrail_rule_record", lambda record, **_: record)\n\n    widget = module.widget_author_dq_rules',
        1,
    )
    path.write_text(text)

    path = Path("tests/unit/test_widget_author_guardrails.py")
    text = path.read_text().replace(
        '    monkeypatch.setattr(module.shared, "_write_rule_records", lambda records, **_: written.append(records))\n\n    widget = _render_guardrail_authoring(',
        '    monkeypatch.setattr(module.shared, "_write_rule_records", lambda records, **_: written.append(records))\n    monkeypatch.setattr(module, "canonical_guardrail_rule_record", lambda record, **_: record)\n\n    widget = _render_guardrail_authoring(',
        1,
    )
    path.write_text(text)


if __name__ == "__main__":
    _restore_rule_audit_fields()
    _restore_shared_guardrail_constants()
    _align_writer_test_with_authoritative_module()
    _align_remaining_stage4a_tests()
    Path(__file__).unlink()
