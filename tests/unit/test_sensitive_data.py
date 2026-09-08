"""Sensitive Data Guardrail preparation tests."""

from importlib import import_module

import pytest

module = import_module("fabricops_kit.pipeline.check_sensitive_data")


def _rule(*, treatment="tokenize", action="Block", column_name="email", version=2):
    return {
        "guardrail_rule_id": f"sensitive-{version}", "guardrail_version": 1,
        "contract_id": "contract", "contract_version": version,
        "table_id": "table-id", "column_id": "email-id", "column_name": column_name,
        "guardrail_type": "sensitive_data", "rule_parameters_json":
        f'{{"scope":"column","treatment":"{treatment}"}}',
        "action": action, "is_active": True,
    }


def _runtime(monkeypatch, rules, writes):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *_a, **_k: {
        "table_id": "table-id", "table_name": "customers", "store_type": "lakehouse",
        "target": "unified", "schema": "dbo",
    })
    monkeypatch.setattr(module, "load_table_guardrail_rules", lambda *_a, **_k: rules)
    monkeypatch.setattr(module, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs["result"]))

def test_tokenize_is_opaque_null_preserving_and_caller_owned(monkeypatch, spark_session):
    """Tokenization replaces raw values and only returns its one-to-one mapping."""
    writes = []
    _runtime(monkeypatch, [_rule(), {**_rule(), "guardrail_type": "data_quality"}], writes)
    frame = spark_session.createDataFrame([(1, "a@example.test"), (2, "a@example.test"), (3, "b@example.test"), (4, None)], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    values = [row.email for row in result["dataframe"].orderBy("id").collect()]
    assert values[0] == values[1]
    assert values[0] != values[2]
    assert values[3] is None
    assert not {"a@example.test", "b@example.test"}.intersection(value for value in values if value)
    mapping = result["support_mapping"].collect()
    assert {(row.table_id, row.column_id) for row in mapping} == {("table-id", "email-id")}
    assert {row.original_value for row in mapping} == {"a@example.test", "b@example.test"}
    assert len(writes) == 1
    assert all("original_value" not in str(value) for value in writes)


def test_multiple_sensitive_columns_apply_mixed_treatments(monkeypatch, spark_session):
    """All exact-version column rules apply independently in one preparation."""
    rules = [
        _rule(),
        {**_rule(treatment="remove", column_name="phone"),
         "guardrail_rule_id": "sensitive-phone", "column_id": "phone-id"},
    ]
    _runtime(monkeypatch, rules, [])
    frame = spark_session.createDataFrame(
        [(1, "a@example.test", "555-0100"), (2, "a@example.test", None)],
        ["id", "email", "phone"],
    )
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["dataframe"].columns == ["id", "email"]
    assert result["dataframe"].select("email").distinct().count() == 1
    assert {row.column_id for row in result["support_mapping"].collect()} == {"email-id"}
    assert len(result["checks"]) == 2


def test_existing_mapping_preserves_established_token(monkeypatch, spark_session):
    """Caller-supplied persisted mappings retain established assignments."""
    _runtime(monkeypatch, [_rule()], [])
    frame = spark_session.createDataFrame(
        [(1, "a@example.test"), (2, "new@example.test")], ["id", "email"]
    )
    existing = spark_session.createDataFrame(
        [("table-id", "email-id", "a@example.test", "opaque-established")],
        ["table_id", "column_id", "original_value", "token_value"],
    )
    result = module.check_sensitive_data(
        frame, table_id="table-id", existing_mapping=existing
    )
    values = {row.id: row.email for row in result["dataframe"].collect()}
    assert values[1] == "opaque-established"
    assert values[2] != "new@example.test"


def test_remove_drops_only_sensitive_column(monkeypatch, spark_session):
    """Remove has no support mapping and preserves unrelated fields."""
    _runtime(monkeypatch, [_rule(treatment="remove")], [])
    frame = spark_session.createDataFrame([(1, "a@example.test", None), (2, "a@example.test", "x")], ["id", "email", "other"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["dataframe"].columns == ["id", "other"]
    assert [tuple(row) for row in result["dataframe"].orderBy("id").collect()] == [(1, None), (2, "x")]
    assert result["support_mapping"] is None


@pytest.mark.parametrize("action,can_continue,status", [("Warn", True, "warning"), ("Block", False, "failed")])
def test_missing_column_respects_normalized_action(monkeypatch, spark_session, action, can_continue, status):
    """A failed treatment never claims success and only Block stops continuation."""
    writes = []
    _runtime(monkeypatch, [_rule(action=action, column_name="missing")], writes)
    frame = spark_session.createDataFrame([(1, "a@example.test")], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["can_continue"] is can_continue
    assert result["status"] == status
    assert result["dataframe"].collect() == frame.collect()
    assert writes[0]["status"] == status


def test_exact_contract_rules_are_supplied_by_canonical_resolver(monkeypatch, spark_session):
    """Runtime consumes only the exact rules returned by contract resolution."""
    _runtime(monkeypatch, [_rule(treatment="remove", version=3)], [])
    frame = spark_session.createDataFrame([(1, "a@example.test")], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["checks"][0]["contract_version"] == 3
