"""Verify DQ result consistency and bounded distributed work with native Spark data."""

from collections import Counter

import pytest

from fabricops_kit.pipeline import shared
from tests.helpers import framework_config
from tests.integration.test_spark_flows import resolved_runtime_context

pytestmark = pytest.mark.spark


def _rule(kind, columns, **parameters):
    """Build a canonical active rule with independent reporting identity."""
    rule = {
        "rule_id": kind, "guardrail_rule_id": f"gr-{kind}", "guardrail_version": 1,
        "rule_key": kind, "rule_type": kind, "columns": columns, "severity": "warning",
        **parameters,
    }
    return shared._validate_dq_rules([rule])[0]


def _runtime(monkeypatch, frame, rules):
    """Run the real DQ runtime with only metadata transport replaced."""
    writes = []
    monkeypatch.setattr(shared, "_load_active_dq_rules", lambda *_args, **_kwargs: rules)
    monkeypatch.setattr(shared, "write_lakehouse_table", lambda frame, table, **kwargs: writes.append(table))
    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(activity_id="dq-evaluation-test"),
    )
    result = shared.check_dq_runtime(
        frame, framework_config(), "dev", "orders", table_id="orders", store="Bronze",
        store_type="lakehouse", schema_name=None, run_id="dq-test", rules_df=[{}],
        row_identity_columns=["row_id"],
    )
    assert writes == ["METADATA_GUARDRAIL_RESULTS"]
    return result


def _action_counts(monkeypatch):
    """Track explicit DQ actions and prevent hidden per-rule counts."""
    from pyspark.sql.classic.dataframe import DataFrame

    counts = Counter()
    original = DataFrame.first
    original_expression = shared._dq_failed_expression

    def first(frame):
        counts["aggregations"] += 1
        return original(frame)

    def unexpected_count(_frame):
        pytest.fail("DQ must not execute a per-rule count() action")

    def expression(frame, rule):
        counts["predicates"] += 1
        return original_expression(frame, rule)

    monkeypatch.setattr(DataFrame, "first", first)
    monkeypatch.setattr(DataFrame, "count", unexpected_count)
    monkeypatch.setattr(shared, "_dq_failed_expression", expression)
    return counts


def test_full_runtime_uniqueness_matches_summary_tags_and_native_details(spark_session, monkeypatch):
    """A failed uniqueness window works throughout the complete runtime path."""
    frame = spark_session.sql("SELECT * FROM VALUES (1, 'A'), (2, 'A'), (3, 'B') AS t(row_id, value)")
    counts = _action_counts(monkeypatch)
    result = _runtime(monkeypatch, frame, [_rule("uniqueness", ["value"], severity="error")])
    assert result["can_continue"] is False
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 2
    assert counts == {"aggregations": 1, "predicates": 1}
    tags = {row.row_id: row._dq_check_status for row in result["dataframe"].collect()}
    assert tags == {1: "failed", 2: "failed", 3: "passed"}
    details = result["failed_values"]
    assert details.schema == shared._dq_failed_value_schema()
    assert len(details.collect()) == 2
    assert "Union" not in details._jdf.queryExecution().optimizedPlan().toString()
    assert "Python" not in details._jdf.queryExecution().executedPlan().toString()
    assert counts == {"aggregations": 1, "predicates": 1}
    assert frame.columns == ["row_id", "value"]
    assert result["dataframe"].columns == ["row_id", "value", "_dq_failed_rules", "_dq_check_status"]


def test_permissive_thresholds_preserve_exact_overlapping_row_counts(spark_session, monkeypatch):
    """Ignore tolerated missing rows without double-counting other failed rules."""
    frame = spark_session.sql(
        "SELECT * FROM VALUES (1, NULL, -1, 'bad'), (2, NULL, 1, 'ok'), "
        "(3, 'ok', -1, 'bad'), (4, 'ok', 1, 'bad') AS t(row_id, value, amount, status)"
    )
    rules = [
        _rule("completeness", ["value"], maximum_missing_percent=50, treat_blank_as_missing=False),
        _rule("range", ["amount"], minimum=0, severity="error"),
        _rule("value_set", ["status"], mode="allow", values=["ok"]),
    ]
    counts = _action_counts(monkeypatch)
    persisted_before = spark_session.sparkContext._jsc.sc().getPersistentRDDs().size()
    result = _runtime(monkeypatch, frame, rules)
    assert counts["aggregations"] == 2
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 3
    assert result["checks"][0]["failed_count"] == 0
    tags = {row.row_id: row._dq_failed_rules for row in result["dataframe"].collect()}
    assert tags == {1: "range,value_set", 2: "", 3: "range,value_set", 4: "value_set"}
    assert {row.rule_type for row in result["failed_values"].collect()} == {"range", "value_set"}
    assert spark_session.sparkContext._jsc.sc().getPersistentRDDs().size() == persisted_before


def test_composite_null_keys_share_metrics_but_keep_threshold_decisions(spark_session, monkeypatch):
    """Count null key combinations exactly and retain each authored outcome."""
    frame = spark_session.sql(
        "SELECT * FROM VALUES (1, NULL, 'A'), (2, NULL, 'A'), (3, 2, 'B') AS t(row_id, id, group_name)"
    )
    rules = [
        _rule("uniqueness", ["id", "group_name"], minimum_unique_percent=100),
        _rule("uniqueness", ["group_name", "id"], minimum_unique_percent=60,
              rule_id="tolerated", guardrail_rule_id="gr-tolerated"),
    ]
    counts = _action_counts(monkeypatch)
    result = _runtime(monkeypatch, frame, rules)
    assert [check["failed_count"] for check in result["checks"]] == [2, 0]
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 2
    assert counts == {"aggregations": 1, "predicates": 1}
    details = result["failed_values"].collect()
    assert len(details) == 4
    assert {row.rule_id for row in details} == {"uniqueness"}
    assert len({row.failure_event_id for row in details}) == 2
    assert result["failed_values"].schema == shared._dq_failed_value_schema()


def test_all_rule_types_share_consistent_runtime_outputs(spark_session, monkeypatch):
    """Exercise every supported rule together, including null and cross-column cases."""
    frame = spark_session.sql(
        "SELECT * FROM VALUES (1, 1, NULL, -1, 'open', NULL, 2, 1), "
        "(2, 1, 'bad', 5, 'closed', 'bad', 1, 2), "
        "(3, 2, 'ok', 10, 'open', 'ok', NULL, NULL) "
        "AS t(row_id, id, text, amount, status, target, a, b)"
    )
    rules = [
        _rule("completeness", ["text"], maximum_missing_percent=0, treat_blank_as_missing=True),
        _rule("uniqueness", ["id"]),
        _rule("value_set", ["text"], mode="allow", values=["ok"]),
        _rule("range", ["amount"], minimum=0, maximum=9),
        _rule("pattern", ["text"], pattern="^ok$"),
        _rule("column_relationship", ["a", "b"], operator=">="),
        _rule("conditional_completeness", ["status", "target"], condition_operator="=",
              condition_value="open", treat_blank_as_missing=True),
        _rule("conditional_values", ["status", "target"], condition_operator="=",
              condition_value="closed", mode="allow", values=["ok"]),
        _rule("custom_expression", [], expression_language="pyspark",
              expression='(F.col("amount") >= 0) & (F.col("amount") <= 9)'),
    ]
    counts = _action_counts(monkeypatch)
    result = _runtime(monkeypatch, frame, rules)
    assert [check["failed_count"] for check in result["checks"]] == [1, 2, 1, 2, 1, 1, 1, 1, 2]
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 3
    assert counts == {"aggregations": 1, "predicates": 9}
    tagged = result["dataframe"].collect()
    assert all(row._dq_check_status == "warning" for row in tagged)
    details = result["failed_values"].collect()
    assert {row.rule_type for row in details} == set(shared.DQ_RULE_TYPES)
    assert counts == {"aggregations": 1, "predicates": 9}


@pytest.mark.parametrize("rows", [1_000, 1_000_000])
@pytest.mark.parametrize("rule_count", [1, 20])
def test_many_checks_on_one_column_keep_one_aggregation(spark_session, monkeypatch, rows, rule_count):
    """Rule growth must not multiply actions, even at a million input rows."""
    from pyspark.sql import functions as F

    frame = spark_session.range(rows).select(
        "id", F.when(F.col("id") % 10 == 0, F.lit(None)).otherwise(F.col("id")).alias("value")
    )
    rules = [
        _rule("completeness", ["value"], maximum_missing_percent=0, treat_blank_as_missing=False,
              rule_id=f"r-{index}", guardrail_rule_id=f"gr-{index}", severity="error" if index % 2 else "warning")
        for index in range(rule_count)
    ]
    counts = _action_counts(monkeypatch)
    result = shared._evaluate_dq_rules(frame, "orders", rules)
    assert len(result["checks"]) == rule_count
    assert all(check["failed_count"] == rows // 10 for check in result["checks"])
    assert result["failed_row_count"] == rows // 10
    assert counts == {"aggregations": 1, "predicates": 1}


def test_empty_batch_has_consistent_passing_outputs(spark_session, monkeypatch):
    """Empty uniqueness and completeness inputs stay passing without null metrics."""
    frame = spark_session.sql("SELECT 1 AS row_id, CAST(NULL AS STRING) AS value WHERE false")
    result = _runtime(monkeypatch, frame, [
        _rule("uniqueness", ["value"]),
        _rule("completeness", ["value"], maximum_missing_percent=0, treat_blank_as_missing=False),
    ])
    assert result["status"] == "passed"
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 0
    assert result["dataframe"].collect() == []
    assert result["failed_values"].schema == shared._dq_failed_value_schema()
    assert result["failed_values"].collect() == []


def test_many_distinct_predicates_and_skewed_keys_share_one_aggregation(spark_session, monkeypatch):
    """Different rules/keys retain exact counts without per-rule actions."""
    from pyspark.sql import functions as F

    frame = spark_session.range(100_000).select(
        "id", (F.col("id") % 1000).alias("key_one"),
        F.when(F.col("id") < 90_000, F.lit(0)).otherwise(F.col("id")).alias("key_two"),
    )
    rules = [
        _rule("uniqueness", ["key_one"], rule_id="key_one"),
        _rule("uniqueness", ["key_two"], rule_id="key_two"),
        *[_rule("range", ["id"], minimum=index * 100, rule_id=f"range-{index}") for index in range(1, 21)],
    ]
    counts = _action_counts(monkeypatch)
    result = shared._evaluate_dq_rules(frame, "orders", rules)
    assert [check["failed_count"] for check in result["checks"]] == [100_000, 90_000, *range(100, 2100, 100)]
    assert result["failed_row_count"] == 100_000
    assert counts == {"aggregations": 1, "predicates": 22}


def test_temporary_flag_cache_is_released_after_evaluation_failure(spark_session, monkeypatch):
    """A failed aggregation must not leak cached DQ flags in the Spark session."""
    from pyspark.sql.classic.dataframe import DataFrame

    frame = spark_session.sql("SELECT 1 AS value, -1 AS amount")
    before = spark_session.sparkContext._jsc.sc().getPersistentRDDs().size()
    monkeypatch.setattr(DataFrame, "first", lambda _frame: (_ for _ in ()).throw(RuntimeError("evaluation failed")))
    with pytest.raises(RuntimeError, match="evaluation failed"):
        shared._evaluate_dq_rules(frame, "orders", [
            _rule("completeness", ["value"], maximum_missing_percent=10, treat_blank_as_missing=False),
            _rule("range", ["amount"], minimum=0),
            _rule("range", ["value"], minimum=2),
        ])
    assert spark_session.sparkContext._jsc.sc().getPersistentRDDs().size() == before
