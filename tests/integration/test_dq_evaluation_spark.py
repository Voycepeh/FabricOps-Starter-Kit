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


def _runtime(monkeypatch, frame, rules, *, diagnostics="full"):
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
        row_identity_columns=["row_id"], diagnostics=diagnostics,
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
    assert counts["aggregations"] == 1
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 4
    assert result["checks"][0]["failed_count"] == 2
    assert result["checks"][0]["passed"] is True
    tags = {row.row_id: row._dq_failed_rules for row in result["dataframe"].collect()}
    assert tags == {1: "completeness,range,value_set", 2: "completeness", 3: "range,value_set", 4: "value_set"}
    assert {row.rule_type for row in result["failed_values"].collect()} == {"completeness", "range", "value_set"}
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
    assert [check["failed_count"] for check in result["checks"]] == [2, 2]
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 2
    assert counts == {"aggregations": 1, "predicates": 1}
    details = result["failed_values"].collect()
    assert len(details) == 8
    assert {row.rule_id for row in details} == {"uniqueness", "tolerated"}
    assert len({row.failure_event_id for row in details}) == 4
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


def test_evaluation_failure_leaves_no_cached_frames(spark_session, monkeypatch):
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


def test_conditional_tolerance_uses_matching_rows_and_preserves_observed_failures(spark_session, monkeypatch):
    """A large unrelated population must not dilute a conditional rule's percentage."""
    frame = spark_session.sql(
        "SELECT id AS row_id, CASE WHEN id < 10 THEN 'approved' ELSE 'draft' END AS status, "
        "CASE WHEN id < 2 THEN NULL ELSE 'ok' END AS value FROM range(1000)"
    )
    rule = _rule("conditional_completeness", ["status", "value"], condition_operator="=",
                 condition_value="approved", treat_blank_as_missing=False,
                 maximum_missing_percent=20, severity="error")
    result = _runtime(monkeypatch, frame, [rule], diagnostics="none")
    check = result["checks"][0]
    assert (check["failed_count"], check["applicable_count"], check["not_applicable_count"]) == (2, 10, 990)
    assert check["failed_percent"] == 20
    assert check["passed_percent"] == 80
    assert check["passed"] is True
    assert result["can_continue"] is True
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 2
    assert result["summary"]["DQ_CHECKED_ROW_COUNT"] == 10
    assert result["summary"]["DQ_NOT_APPLICABLE_ROW_COUNT"] == 990
    assert result["summary"]["DQ_FAILED_ROW_PERCENT"] == 20
    assert result["failed_values"].collect() == []
    assert result["dataframe"].where("row_id < 2").select("_dq_check_status").first()[0] == "warning"
    rule["maximum_missing_percent"] = 19.9
    assert _runtime(monkeypatch, frame, [rule], diagnostics="none")["can_continue"] is False


def test_nulls_ignored_by_value_checks_are_not_counted_as_passes(spark_session, monkeypatch):
    """The denominator must agree with the row predicate's null handling."""
    frame = spark_session.sql("SELECT * FROM VALUES (1, NULL), (2, -1), (3, 1) AS t(row_id, value)")
    rule = _rule("range", ["value"], minimum=0, maximum_failure_percent=50)
    result = _runtime(monkeypatch, frame, [rule], diagnostics="none")
    check = result["checks"][0]
    assert (check["applicable_count"], check["not_applicable_count"], check["passed_count"]) == (2, 1, 1)
    assert check["failed_percent"] == check["passed_percent"] == 50
    assert check["passed"] is True


def test_sampled_diagnostics_are_bounded_and_do_not_recompute_source(spark_session, monkeypatch):
    """Capture examples alongside metrics; displaying them uses a tiny relation."""
    from pyspark.sql import functions as F

    frame = spark_session.range(1_000_000).select(
        F.col("id").alias("row_id"), F.lit(-1).alias("value"), F.lit("unrelated").alias("other")
    )
    rules = [_rule("range", ["value"], minimum=0, rule_id=f"r-{i}", guardrail_rule_id=f"gr-{i}") for i in range(20)]
    counts = _action_counts(monkeypatch)
    result = _runtime(monkeypatch, frame, rules, diagnostics="sample")
    assert counts == {"aggregations": 1, "predicates": 1}

    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 1_000_000
    assert all(1 <= len(check["failure_examples"]) <= 10 for check in result["checks"])
    assert all(set(example) == {"source_record_id", "row_identity", "values"}
               for check in result["checks"] for example in check["failure_examples"])
    assert all(item["column_name"] == "value" for check in result["checks"]
               for example in check["failure_examples"] for item in example["values"])
    captured = result["failed_values"].collect()
    assert len(captured) <= 200
    assert {row.rule_id for row in captured} == {rule["rule_id"] for rule in rules}
    plan = result["failed_values"]._jdf.queryExecution().optimizedPlan().toString()
    assert "1000000" not in plan and "Window" not in plan
    assert counts == {"aggregations": 1, "predicates": 1}


def test_default_samples_are_saved_in_rule_payload_even_when_within_tolerance(spark_session, monkeypatch):
    """Audit payloads preserve observed percentages and bounded examples together."""
    import json

    frame = spark_session.sql("SELECT * FROM VALUES (1, -1), (2, 1) AS t(row_id, value)")
    stored = []
    original_create = spark_session.createDataFrame

    def capture(data, *args, **kwargs):
        if isinstance(data, list) and data and isinstance(data[0], dict) and "result_payload_json" in data[0]:
            stored.extend(data)
        return original_create(data, *args, **kwargs)

    monkeypatch.setattr(spark_session, "createDataFrame", capture)
    rule = _rule("range", ["value"], minimum=0, maximum_failure_percent=50, severity="error")
    # No diagnostics override: exercise the actual default, not a test-only selection.
    monkeypatch.setattr(shared, "_load_active_dq_rules", lambda *_args, **_kwargs: [rule])
    monkeypatch.setattr(shared, "write_lakehouse_table", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("fabricops_kit.config.audit.resolve_runtime_context",
                        lambda **_kwargs: resolved_runtime_context(activity_id="dq-default-test"))
    result = shared.check_dq_runtime(frame, framework_config(), "dev", "orders", table_id="orders",
                                     store="Bronze", store_type="lakehouse", schema_name=None,
                                     rules_df=[{}], row_identity_columns=["row_id"])
    assert result["diagnostics"]["mode"] == "sample"
    assert result["can_continue"] is True
    payload = json.loads(stored[0]["result_payload_json"])
    assert payload["failed_count"] == 1 and payload["failed_percent"] == 50
    assert payload["passed"] is True
    assert len(payload["failure_examples"]) == 1
    assert result["failed_values"].collect()[0].raw_value == "-1"


def test_uniqueness_tolerance_counts_every_duplicate_member(spark_session, monkeypatch):
    """Use duplicate members, not excess copies, at the authored boundary."""
    frame = spark_session.sql("SELECT id AS row_id, CASE WHEN id < 2 THEN 0 ELSE id END AS key FROM range(100)")
    rules = [_rule("uniqueness", ["key"], maximum_failure_percent=2, severity="error")]
    result = _runtime(monkeypatch, frame, rules)
    check = result["checks"][0]
    assert check["failed_count"] == 2
    assert check["observed_value"] == 2
    assert check["threshold_operator"] == "<="
    assert check["passed"] is True
    rules[0]["maximum_failure_percent"] = 1.99
    assert _runtime(monkeypatch, frame, rules)["checks"][0]["passed"] is False
