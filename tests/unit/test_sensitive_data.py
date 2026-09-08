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

    def mapping(df, *, table_id, column_id, original_column, token_column, context):
        del context
        from pyspark.sql import functions as F
        return df.select(
            F.lit(table_id).alias("table_id"), F.lit(column_id).alias("column_id"),
            F.col(original_column).cast("string").alias("original_value"),
            F.col(token_column).cast("string").alias("token_value"),
        ).dropDuplicates()
    monkeypatch.setattr(module, "build_token_map_frame", mapping)


def test_tokenize_is_deterministic_null_preserving_and_caller_owned(monkeypatch, spark_session):
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
