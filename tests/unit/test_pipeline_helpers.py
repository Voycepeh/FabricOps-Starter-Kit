"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path

import pytest

import fabricops_kit
from fabricops_kit import pipeline
pipeline_bootstrap_module = importlib.import_module("fabricops_kit.widgets.widget_pipeline_bootstrap")
widgets_shared_module = importlib.import_module("fabricops_kit.widgets.shared")
from tests.helpers import framework_config

pytestmark = pytest.mark.unit


class FakeSpark:
    """Fakespark test double."""

    def __init__(self):
        """Initialize the test helper."""
        self.created = []

    def createDataFrame(self, rows, schema=None):
        """Return createDataFrame."""
        self.created.append((rows, schema))
        return {"rows": rows, "schema": schema}


def test_public_pipeline_helpers_are_exported_without_wrapper_bloat():
    """Verify public pipeline helpers are exported without wrapper bloat."""
    assert "prepare_pipeline_table_configs" in fabricops_kit.__all__
    assert "run_table_guardrails" in fabricops_kit.__all__
    assert "write_catalogue_evidence" not in fabricops_kit.__all__
    assert "write_pipeline_lineage" in fabricops_kit.__all__
    assert "write_pipeline_run_summary" in fabricops_kit.__all__
    for removed_name in {
        "prepare_source_table_configs",
        "prepare_target_table_configs",
        "write_target_tables",
        "build_guardrail_evidence_definitions",
        "guardrail_summary",
        "stop_if_any_guardrail_failed",
        "read_pipeline_sources",
        "profile_pipeline_datasets",
        "run_schema_guardrails",
        "run_source_stability_guardrails",
        "run_dq_guardrails",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
    }:
        assert removed_name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, removed_name)

    for private_source_reader in {"_load_source_dataframe", "_read_source_dataframe", "_source_read_type"}:
        assert not hasattr(fabricops_kit, private_source_reader)


class FakeDataFrame:
    """Fakedataframe test double."""

    def __init__(self, name="df"):
        """Initialize the test helper."""
        self.name = name
        self.with_columns = []

    def withColumn(self, name, value):
        """Return withColumn."""
        self.with_columns.append((name, value))
        return self


def _install_fake_pyspark_functions(monkeypatch):
    fake_functions = types.SimpleNamespace(lit=lambda value: ("lit", value))
    fake_sql = types.ModuleType("pyspark.sql")
    fake_sql.functions = fake_functions
    fake_pyspark = types.ModuleType("pyspark")
    fake_pyspark.sql = fake_sql
    monkeypatch.setitem(sys.modules, "pyspark", fake_pyspark)
    monkeypatch.setitem(sys.modules, "pyspark.sql", fake_sql)
    monkeypatch.setitem(sys.modules, "pyspark.sql.functions", fake_functions)


def test_prepare_pipeline_table_configs_source_role_derives_defaults_from_preloaded_dataframe():
    """Verify prepare pipeline table configs source role derives defaults from preloaded dataframe."""
    source_df = FakeDataFrame("source")

    enriched, by_key = pipeline.prepare_pipeline_table_configs(
        [
            {
                "key": "source_01",
                "df": source_df,
                "layer": "source",
                "table_name": "orders_raw",
                "watermark_column": "business_date",
            }
        ],
        {
            "schema_preset": "allow_new_columns",
            "profile_mode": "changing_data",
        },
        table_role="source",
    )

    assert enriched == [
        {
            "schema_preset": "allow_new_columns",
            "profile_mode": "changing_data",
            "key": "source_01",
            "df": source_df,
            "layer": "source",
            "table_name": "orders_raw",
            "watermark_column": "business_date",
            "dataset_name": "orders_raw",
            "stage": "source",
        }
    ]
    assert by_key["source_01"] is enriched[0]


def test_prepare_pipeline_table_configs_source_role_requires_preloaded_dataframe():
    """Verify prepare pipeline table configs source role requires preloaded dataframe."""
    with pytest.raises(ValueError, match="must include a pre-loaded DataFrame"):
        pipeline.prepare_pipeline_table_configs(
            [{"key": "source_01", "layer": "source", "table_name": "orders_raw"}],
            {},
            table_role="source",
        )


def test_pipeline_module_does_not_expose_source_read_routing_wrappers():
    """Verify pipeline module does not expose source read routing wrappers."""
    assert not hasattr(pipeline, "_load_source_dataframe")
    assert not hasattr(pipeline, "_read_source_dataframe")
    assert not hasattr(pipeline, "_source_read_type")




def test_prepare_pipeline_table_configs_target_role_adds_audit_columns_and_derives_write_defaults(monkeypatch):
    """Verify prepare pipeline table configs target role adds audit columns and derives write defaults."""
    _install_fake_pyspark_functions(monkeypatch)
    df = FakeDataFrame("target")

    enriched, by_key = pipeline.prepare_pipeline_table_configs(
        [
            {
                "key": "target_01",
                "df": df,
                "layer": "unified",
                "table_name": "orders_curated",
            }
        ],
        {
            "schema_preset": "allow_new_columns",
            "write_mode": "overwrite",
            "target_kind": "lakehouse",
        },
        table_role="target",
        run_id="run-1",
        pipeline_name="pipeline-1",
    )

    target = enriched[0]
    assert target["dataset_name"] == "orders_curated"
    assert target["stage"] == "unified"
    assert target["target_layer"] == "unified"
    assert target["target_name"] == "orders_curated"
    assert target["target_kind"] == "lakehouse"
    assert by_key["target_01"] is target
    assert [name for name, _value in df.with_columns] == [
        "_fabricops_run_id",
        "_fabricops_pipeline_name",
        "_fabricops_created_at",
    ]

    created_at = dict(df.with_columns)["_fabricops_created_at"][1]
    assert created_at.endswith("+00:00")


def test_prepare_pipeline_table_configs_target_role_uses_configured_audit_timezone(monkeypatch):
    """Verify target audit columns use configured audit timezone."""
    _install_fake_pyspark_functions(monkeypatch)
    df = FakeDataFrame("target")
    config = framework_config()
    object.__setattr__(config, "audit_timezone", "Asia/Singapore")

    enriched, _by_key = pipeline.prepare_pipeline_table_configs(
        [
            {
                "key": "target_01",
                "df": df,
                "layer": "unified",
                "table_name": "orders_curated",
                "config": config,
            }
        ],
        {},
        table_role="target",
        run_id="run-1",
        pipeline_name="pipeline-1",
    )

    assert enriched[0]["df"] is df
    assert [name for name, _value in df.with_columns] == [
        "_fabricops_run_id",
        "_fabricops_pipeline_name",
        "_fabricops_created_at",
    ]
    created_at = dict(df.with_columns)["_fabricops_created_at"][1]
    assert created_at.endswith("+08:00")


def test_write_pipeline_lineage_supports_many_to_many_relationships(monkeypatch):
    """Verify write pipeline lineage supports many to many relationships."""
    writes = []

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((df, context["env"], target, table, kwargs))

    monkeypatch.setattr(pipeline, "write_lakehouse_table_core", write_table)

    result = pipeline.write_pipeline_lineage(
        spark=FakeSpark(),
        context={"config": {}, "env": "dev"},
        run_id="run-1",
        source_definitions={"s1": {"table_name": "source_one"}, "s2": {"table_name": "source_two"}},
        target_definitions={"t1": {"table_name": "target_one"}, "t2": {"table_name": "target_two"}},
        relationships=[{"sources": ["s1", "s2"], "targets": ["t1", "t2"], "operation": "join"}],
        dataset_name="sales",
    )

    assert result["row_count"] == 4
    assert writes[0][2:4] == ("metadata", "METADATA_DATA_LINEAGE_TABLE")
    payload = json.loads(result["rows"][0]["transformation_steps_json"])
    assert payload["operation"] == "join"


def test_write_pipeline_run_summary_writes_metadata_table(monkeypatch):
    """Verify write pipeline run summary writes metadata table."""
    writes = []
    fake_spark = FakeSpark()

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((df, context["env"], target, table, kwargs))

    monkeypatch.setattr(pipeline, "write_lakehouse_table_core", write_table)

    row = pipeline.write_pipeline_run_summary(
        spark=fake_spark,
        context={"config": {}, "env": "dev"},
        run_id="run-1",
        source_definitions={"s1": {"table_name": "source_one"}, "s2": {"table_name": "source_two"}},
        target_definitions={"t1": {"table_name": "target_one"}, "t2": {"table_name": "target_two"}},
        source_schema_results={"s1": {"status": "passed"}},
        target_schema_results={"t1": {"status": "passed"}},
        source_dq_results={"s1": {"status": "passed"}},
        target_dq_results={"t1": {"status": "warning"}},
    )

    assert row["source_count"] == 2
    assert row["target_count"] == 2
    assert row["dq_status"] == "warning"
    assert writes[0][2:4] == ("metadata", "METADATA_PIPELINE_RUNS")
    assert writes[0][4]["mode"] == "append"


def test_summary_status_treats_baseline_created_as_passed_and_skipped_as_nonblocking():
    """Verify summary status treats baseline created as passed and skipped as nonblocking."""
    assert pipeline._summary_status({"s1": {"status": "baseline_created"}}) == "passed"
    assert pipeline._summary_status({"s1": {"status": "skipped"}}) == "skipped"
    assert pipeline._summary_status({"s1": {"status": "passed"}, "s2": {"status": "skipped"}}) == "passed"


def test_normalize_catalogue_evidence_types_casts_numeric_percent_timestamp_and_boolean_columns(spark_session):
    """Verify normalize catalogue evidence types casts only catalogue-owned fields."""
    evidence = spark_session.createDataFrame(
        [
            {
                "row_count": 3,
                "null_count": 0,
                "distinct_count": 3,
                "null_percent": 0,
                "distinct_percent": 100,
                "run_timestamp": "2026-01-01T00:00:00",
                "dataset_name": "orders",
            }
        ]
    )

    normalized = pipeline._normalize_catalogue_evidence_types(evidence)
    dtypes = dict(normalized.dtypes)

    for column_name in ["row_count", "null_count", "distinct_count"]:
        assert dtypes[column_name] == "bigint"
    for column_name in ["null_percent", "distinct_percent"]:
        assert dtypes[column_name] == "double"
    assert dtypes["run_timestamp"] == "timestamp"
    assert dtypes["dataset_name"] == "string"



def test_private_guardrail_evidence_definitions_excludes_dataframes_and_resolves_target_fields():
    """Verify private guardrail evidence definitions excludes dataframes and resolves target fields."""
    definitions = pipeline._build_guardrail_evidence_definitions(
        [
            {
                "key": "target_01",
                "df": object(),
                "table_name": "orders_curated",
                "stage": "target",
                "target_layer": "product",
                "target_kind": "warehouse",
                "write_mode": "overwrite",
            }
        ]
    )

    assert definitions == {
        "target_01": {
            "key": "target_01",
            "table_name": "orders_curated",
            "stage": "target",
            "target_layer": "product",
            "target_kind": "warehouse",
            "write_mode": "overwrite",
            "layer": "product",
            "kind": "warehouse",
            "mode": "overwrite",
        }
    }


def test_run_table_guardrails_collects_results_and_returns_summary_before_reporting_failures(monkeypatch):
    """Verify run table guardrails collects results and returns summary before reporting failures."""
    calls = []
    catalogue_calls = []

    def fake_profile(dataframe, *, table_name, exclude_columns=None, include_distributions=True, distribution_columns=None, **kwargs):
        calls.append(("profile", table_name))
        return {"profile_for": table_name, "df": dataframe}

    def fake_validate(dataframe, expected_schema, *, preset="strict"):
        calls.append(("schema", dataframe))
        return {"status": "failed" if dataframe == "df_bad" else "passed", "can_continue": dataframe != "df_bad"}

    def fake_freshness(dataframe, freshness_column, max_lag_days, severity="blocking", **kwargs):
        calls.append(("freshness", dataframe))
        return {"status": "passed", "can_continue": True}

    def fake_stability(*args, **kwargs):
        calls.append(("stability", args[4], kwargs.get("current_profile")))
        return {"status": "passed", "can_continue": True}

    def fake_dq(dataframe, config, env, dataset_name, table_name, **kwargs):
        calls.append(("dq", table_name))
        result = {"status": "passed", "can_continue": True, "checks": []}
        if table_name == "orders_good":
            result["dataframe"] = "df_good_checked"
        return result

    def fake_catalogue(profiles, definitions, **kwargs):
        catalogue_calls.append((profiles, definitions, kwargs))
        return {"status": "written"}

    monkeypatch.setattr(pipeline, "profile_dataframe_core", fake_profile)
    monkeypatch.setattr(pipeline, "_check_schema_runtime", fake_validate)
    monkeypatch.setattr(pipeline, "enforce_freshness", fake_freshness)
    monkeypatch.setattr(pipeline, "enforce_profile_behavior", fake_stability)
    monkeypatch.setattr(pipeline, "_run_active_dq_guardrail", fake_dq)
    monkeypatch.setattr(pipeline, "write_catalogue_evidence", fake_catalogue)

    table_configs = [
        {
            "key": "good",
            "df": "df_good",
            "table_name": "orders_good",
            "dataset_name": "orders",
            "stage": "source",
            "expected_schema": {"id": "bigint"},
            "watermark_column": "business_date",
        },
        {
            "key": "bad",
            "df": "df_bad",
            "table_name": "orders_bad",
            "stage": "source",
            "expected_schema": {"id": "bigint"},
            "watermark_column": "business_date",
            "dq_preset": "skip",
        },
    ]

    result = pipeline.run_table_guardrails(
        table_configs,
        context={"config": {"config": True}, "env": "dev"},
        run_id="run-1",
        spark_session="spark",
        agreement_id="agreement-1",
        agreement_contract_version="v1",
        notebook_registry_id="notebook-registry-1",
        notebook_id="notebook-1",
        pipeline_name="pipeline-1",
    )

    assert result["can_continue"] is False
    assert result["failed_tables"] == ["bad"]
    assert set(result["profiles"]) == {"good", "bad"}
    assert set(result["schema_results"]) == {"good", "bad"}
    assert set(result["freshness_results"]) == {"good", "bad"}
    assert set(result["stability_results"]) == {"good", "bad"}
    assert result["dq_results"]["bad"]["status"] == "skipped"
    assert result["summary"] == {
        "schema_results": result["schema_results"],
        "freshness_results": result["freshness_results"],
        "stability_results": result["stability_results"],
        "dq_results": result["dq_results"],
        "catalogue_status": result["catalogue_status"],
        "failed_tables": ["bad"],
    }
    assert table_configs[0]["df"] == "df_good_checked"
    assert ("profile", "orders_bad") in calls
    assert ("freshness", "df_bad") in calls
    assert ("stability", "orders_bad", result["profiles"]["bad"]) in calls
    assert catalogue_calls
    assert catalogue_calls[0][2]["schema_results"] == result["schema_results"]
    assert catalogue_calls[0][2]["freshness_results"] == result["freshness_results"]




def test_run_table_guardrails_writes_schema_freshness_and_dq_results(monkeypatch):
    """Verify run table guardrails writes runtime outcomes to results metadata."""
    result_writes = []

    class Spark:
        def createDataFrame(self, rows):
            return rows

    monkeypatch.setattr(pipeline, "profile_dataframe_core", lambda dataframe, **kwargs: {"profile_for": kwargs["table_name"]})
    monkeypatch.setattr(pipeline, "_check_schema_runtime", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "enforce_freshness", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "enforce_profile_behavior", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "_run_active_dq_guardrail", lambda *args, **kwargs: {"status": "passed", "can_continue": True, "checks": []})
    monkeypatch.setattr(pipeline, "write_catalogue_evidence", lambda *args, **kwargs: {"orders": "written"})

    def fake_result_writer(**kwargs):
        result_writes.append(kwargs)

    monkeypatch.setattr(pipeline, "_write_guardrail_result_row", fake_result_writer)

    pipeline.run_table_guardrails(
        [{
            "key": "orders",
            "df": "df",
            "table_name": "orders",
            "stage": "source",
            "expected_schema": {"id": "bigint"},
            "dq_preset": "active_rules",
        }],
        context={"config": {}, "env": "dev"},
        run_id="run-1",
        spark_session=Spark(),
    )

    assert [write["guardrail_type"] for write in result_writes] == ["schema", "freshness", "dq"]
    assert {write["run_id"] for write in result_writes} == {"run-1"}

def test_run_table_guardrails_profile_mode_defaults_and_explicit_modes(monkeypatch):
    """Verify profile behavior config uses clean profile_mode values only."""
    stability_calls = []

    monkeypatch.setattr(pipeline, "profile_dataframe_core", lambda dataframe, **kwargs: {"profile_for": kwargs["table_name"]})
    monkeypatch.setattr(pipeline, "_check_schema_runtime", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "enforce_freshness", lambda *args, **kwargs: {"status": "skipped", "can_continue": True})

    def fake_stability(*args, **kwargs):
        stability_calls.append(kwargs)
        return {"status": "passed", "can_continue": True}

    monkeypatch.setattr(pipeline, "enforce_profile_behavior", fake_stability)
    monkeypatch.setattr(pipeline, "write_catalogue_evidence", lambda *args, **kwargs: {"status": "written"})

    table_configs = [
        {
            "key": "default_new_model",
            "df": "df-default",
            "table_name": "orders_default",
            "stage": "source",
            "expected_schema": {"id": "bigint"},
            "dq_preset": "skip",
        },
        {
            "key": "static_data",
            "df": "df-static",
            "table_name": "orders_static",
            "stage": "source",
            "expected_schema": {"id": "bigint"},
            "profile_mode": "static_data",
            "dq_preset": "skip",
        },
        {
            "key": "changing_data",
            "df": "df-changing",
            "table_name": "orders_changing",
            "stage": "source",
            "expected_schema": {"id": "bigint"},
            "profile_mode": "changing_data",
            "watermark_column": "business_date",
            "dq_preset": "skip",
        },
    ]

    pipeline.run_table_guardrails(
        table_configs,
        context={"config": {}, "env": "dev"},
        run_id="run-1",
        spark_session="spark",
    )

    assert "load_behavior" not in stability_calls[0]
    assert stability_calls[0]["profile_mode"] is None
    assert stability_calls[1]["profile_mode"] == "static_data"
    assert stability_calls[2]["profile_mode"] == "changing_data"
    assert stability_calls[2]["watermark_column"] == "business_date"


def test_run_table_guardrails_stop_on_failure_delegates_to_standard_stopper(monkeypatch):
    """Verify run table guardrails stop on failure delegates to standard stopper."""
    stopped = []

    monkeypatch.setattr(pipeline, "profile_dataframe_core", lambda dataframe, **kwargs: {"profile_for": kwargs["table_name"]})
    monkeypatch.setattr(pipeline, "_check_schema_runtime", lambda dataframe, expected_schema, *, preset="strict": {"status": "failed", "can_continue": False})
    monkeypatch.setattr(pipeline, "enforce_freshness", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "enforce_profile_behavior", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "write_catalogue_evidence", lambda *args, **kwargs: {"status": "written"})
    monkeypatch.setattr(pipeline, "stop_if_failed", lambda result: stopped.append(result))

    pipeline.run_table_guardrails(
        [
            {
                "key": "target_01",
                "df": "df",
                "table_name": "orders",
                "stage": "target",
                "expected_schema": {"id": "bigint"},
                "dq_preset": "skip",
            }
        ],
        context={"config": {}, "env": "dev"},
        run_id="run-1",
        spark_session="spark",
        stop_on_failure=True,
    )

    assert stopped[0]["status"] == "failed"
    assert stopped[0]["can_continue"] is False
    assert "schema failed" in stopped[0]["message"]
    assert stopped[0]["failed_tables"] == ["target_01"]


def test_schema_guardrail_strict_and_allow_new_columns_behavior(spark_session):
    """Verify schema guardrail strict and allow new columns behavior."""
    from fabricops_kit.guardrails import _check_schema_runtime

    happy_df = spark_session.createDataFrame([(1, "new")], "id int, status string")
    additive_df = spark_session.createDataFrame([(1, "new", "extra")], "id int, status string, source_file string")
    incompatible_df = spark_session.createDataFrame([("1", "new")], "id string, status string")
    expected_schema = {"id": "int", "status": "string"}

    happy = _check_schema_runtime(happy_df, expected_schema, preset="strict")
    assert happy["status"] == "passed"
    assert happy["can_continue"] is True

    strict_additive = _check_schema_runtime(additive_df, expected_schema, preset="strict")
    assert strict_additive["status"] == "failed"
    assert strict_additive["can_continue"] is False
    assert strict_additive["unexpected_columns"] == ["source_file"]

    allowed_additive = _check_schema_runtime(additive_df, expected_schema, preset="allow_new_columns")
    assert allowed_additive["status"] == "warning"
    assert allowed_additive["can_continue"] is True
    assert allowed_additive["unexpected_columns"] == ["source_file"]

    incompatible = _check_schema_runtime(incompatible_df, expected_schema, preset="strict")
    assert incompatible["status"] == "failed"
    assert incompatible["can_continue"] is False
    assert incompatible["datatype_mismatches"] == [{"column": "id", "expected": "int", "actual": "string"}]

    incompatible_allow_new = _check_schema_runtime(incompatible_df, expected_schema, preset="allow_new_columns")
    assert incompatible_allow_new["status"] == "failed"
    assert incompatible_allow_new["can_continue"] is False


def test_freshness_guardrail_blocks_or_warns_by_severity(spark_session):
    """Verify freshness guardrail blocks or warns by severity."""
    from fabricops_kit.guardrails import enforce_freshness

    current_df = spark_session.createDataFrame([("2026-06-14",), ("2026-06-13",)], "business_date string")
    stale_df = spark_session.createDataFrame([("2026-06-01",), ("2026-06-02",)], "business_date string")

    current = enforce_freshness(current_df, "business_date", 1, severity="blocking", reference_date="2026-06-14")
    assert current["status"] == "passed"
    assert current["can_continue"] is True
    assert current["latest_value"] == "2026-06-14"

    stale_blocking = enforce_freshness(stale_df, "business_date", 1, severity="blocking", reference_date="2026-06-14")
    assert stale_blocking["status"] == "failed"
    assert stale_blocking["can_continue"] is False
    assert stale_blocking["required_min_value"] == "2026-06-13"

    stale_warning = enforce_freshness(stale_df, "business_date", 1, severity="warning", reference_date="2026-06-14")
    assert stale_warning["status"] == "warning"
    assert stale_warning["can_continue"] is True


def test_run_table_guardrails_skip_profile_behavior_only_not_schema_freshness_or_dq(monkeypatch, spark_session):
    """Verify run table guardrails skip profile behavior only not schema freshness or dq."""
    df = spark_session.createDataFrame([("not-an-int", "2026-06-01")], "id string, business_date string")

    monkeypatch.setattr(
        pipeline,
        "profile_dataframe_core",
        lambda dataframe, **kwargs: [
            {
                "table_name": kwargs["table_name"],
                "column_name": "business_date",
                "row_count": dataframe.count(),
                "min_value": "2026-06-01",
                "max_value": "2026-06-01",
            }
        ],
    )
    monkeypatch.setattr(
        pipeline,
        "enforce_freshness",
        lambda dataframe, freshness_column, max_lag_days, severity="blocking", **kwargs: {
            "status": "failed",
            "can_continue": False,
            "freshness_column": freshness_column,
            "freshness_max_lag_days": max_lag_days,
            "freshness_severity": severity,
        },
    )
    monkeypatch.setattr(
        pipeline,
        "enforce_profile_behavior",
        lambda *args, **kwargs: {
            "status": "skipped",
            "can_continue": True,
            "stability_status": "skipped",
            "stability_can_continue": True,
            "stability_check_enabled": False,
            "message": "Profile behavior guardrail skipped; other guardrails still apply.",
        },
    )
    monkeypatch.setattr(
        pipeline,
        "_run_active_dq_guardrail",
        lambda *args, **kwargs: {"status": "failed", "can_continue": False, "checks": [{"rule_id": "id_required", "status": "failed"}]},
    )
    monkeypatch.setattr(pipeline, "write_catalogue_evidence", lambda *args, **kwargs: {"orders": "written"})
    monkeypatch.setattr(pipeline, "_write_guardrail_result_row", lambda **kwargs: None)

    result = pipeline.run_table_guardrails(
        [
            {
                "key": "orders",
                "df": df,
                "table_name": "orders",
                "dataset_name": "sales",
                "stage": "source",
                "expected_schema": {"id": "int", "business_date": "string"},
                "schema_preset": "strict",
                "freshness_column": "business_date",
                "freshness_max_lag_days": 1,
                "freshness_severity": "blocking",
                "profile_mode": "skip",
                "dq_preset": "active_rules",
            }
        ],
        context={"config": framework_config(), "env": "dev"},
        run_id="run-1",
        spark_session=spark_session,
    )

    assert result["can_continue"] is False
    assert result["failed_tables"] == ["orders"]
    assert result["schema_results"]["orders"]["status"] == "failed"
    assert result["freshness_results"]["orders"]["status"] == "failed"
    assert result["stability_results"]["orders"]["status"] == "skipped"
    assert result["dq_results"]["orders"]["status"] == "failed"


def test_run_table_guardrails_dq_skip_bypasses_dq_enforcement(monkeypatch, spark_session):
    """Verify run table guardrails dq skip bypasses dq enforcement."""
    df = spark_session.createDataFrame([(1, "2026-06-14")], "id int, business_date string")

    monkeypatch.setattr(
        pipeline,
        "profile_dataframe_core",
        lambda dataframe, **kwargs: [{"table_name": kwargs["table_name"], "column_name": "id", "row_count": dataframe.count()}],
    )
    monkeypatch.setattr(pipeline, "enforce_profile_behavior", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "write_catalogue_evidence", lambda *args, **kwargs: {"orders": "written"})
    monkeypatch.setattr(pipeline, "_write_guardrail_result_row", lambda **kwargs: None)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("dq_preset='skip' should not call _run_active_dq_guardrail")

    monkeypatch.setattr(pipeline, "_run_active_dq_guardrail", fail_if_called)

    result = pipeline.run_table_guardrails(
        [
            {
                "key": "orders",
                "df": df,
                "table_name": "orders",
                "dataset_name": "sales",
                "stage": "source",
                "expected_schema": {"id": "int", "business_date": "string"},
                "freshness_column": "business_date",
                "freshness_max_lag_days": 10000,
                "freshness_severity": "blocking",
                "profile_mode": "changing_data",
                "dq_preset": "skip",
            }
        ],
        context={"config": framework_config(), "env": "dev"},
        run_id="run-1",
        spark_session=spark_session,
    )

    assert result["can_continue"] is True
    assert result["dq_results"]["orders"] == {
        "status": "skipped",
        "can_continue": True,
        "checks": [],
        "message": "DQ guardrail skipped by preset.",
    }



def test_widget_pipeline_bootstrap_public_import_surface():
    """Verify widget_pipeline_bootstrap remains available from public package surfaces."""
    assert fabricops_kit.widget_pipeline_bootstrap is pipeline_bootstrap_module.widget_pipeline_bootstrap
    assert pipeline.widget_pipeline_bootstrap is pipeline_bootstrap_module.widget_pipeline_bootstrap


def test_widget_pipeline_bootstrap_has_no_stale_select_agreement_private_dependency():
    """Verify bootstrap no longer imports the standalone selector private workflow."""
    pipeline_source = Path("src/fabricops_kit/pipeline.py").read_text(encoding="utf-8")
    bootstrap_source = Path("src/fabricops_kit/widgets/widget_pipeline_bootstrap.py").read_text(encoding="utf-8")
    assert "_render_agreement_selector" not in pipeline_source
    assert "_select_agreement_widget_workflow" not in pipeline_source
    assert "_select_agreement_widget_workflow" not in bootstrap_source

def test_widget_pipeline_bootstrap_stores_agreement_context(monkeypatch):
    """Verify widget_pipeline_bootstrap stores agreement and runtime defaults."""
    spark = FakeSpark()
    run_context = types.SimpleNamespace(
        run_id="run-123",
        runtime_metadata={"currentNotebookName": "02_pipeline", "currentNotebookId": "notebook-1"},
    )
    widget_calls = []
    monkeypatch.setattr(pipeline_bootstrap_module, "_render_bootstrap_agreement_selector", lambda **kwargs: widget_calls.append(kwargs))
    monkeypatch.setattr(
        pipeline_bootstrap_module,
        "get_selected_agreement",
        lambda: {"agreement_id": "agreement-1", "contract_version": "2", "registration_id": "registry-1"},
    )

    result = pipeline.widget_pipeline_bootstrap(
        notebook_type="02_pipeline",
        select_agreement=True,
        register_notebook=True,
        run_context=run_context,
        spark_session=spark,
        metadata_schema="metadata_schema",
    )

    assert result.run_id == "run-123"
    assert result.pipeline_name == "02_pipeline"
    assert result.notebook_id == "notebook-1"
    assert result.agreement_id == "agreement-1"
    assert result.agreement_contract_version == "2"
    assert result.notebook_registry_id == "registry-1"
    assert widget_calls == [
        {
            "spark_session": spark,
            "metadata_schema": "metadata_schema",
            "register_notebook": True,
            "notebook_type": "02_pipeline",
            "pipeline_name": "02_pipeline",
            "context": None,
        }
    ]


def test_run_table_guardrails_uses_active_context_defaults(monkeypatch):
    """Verify run_table_guardrails derives omitted runtime parameters from context."""
    spark = FakeSpark()
    active = widgets_shared_module.PipelineRunContext(
        run_id="run-123",
        pipeline_started_at="2026-01-01T00:00:00Z",
        pipeline_name="demo_pipeline",
        spark_session=spark,
        notebook_id="notebook-1",
        notebook_registry_id="registry-1",
        agreement_id="agreement-1",
        agreement_contract_version="2",
        context={"config": "config", "env": "dev"},
    )
    monkeypatch.setattr(widgets_shared_module, "_ACTIVE_PIPELINE_CONTEXT", active)
    monkeypatch.setattr(pipeline, "resolve_fabric_context", lambda context=None: ("config", "dev", context))
    monkeypatch.setattr(pipeline, "profile_dataframe_core", lambda *args, **kwargs: FakeDataFrame("profile"))
    monkeypatch.setattr(pipeline, "_check_schema_runtime", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "enforce_freshness", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    captured = {}
    monkeypatch.setattr(
        pipeline,
        "enforce_profile_behavior",
        lambda spark_session, dataframe, catalogue_table, dataset_name, table_name, **kwargs: captured.setdefault(
            "profile_behavior",
            {"spark_session": spark_session, "run_id": kwargs["run_id"]},
        ) or {"status": "passed", "can_continue": True},
    )
    monkeypatch.setattr(pipeline, "_run_active_dq_guardrail", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline, "_write_guardrail_result_row", lambda **kwargs: None)

    def fake_write_catalogue_evidence(profiles, definitions, **kwargs):
        captured["catalogue"] = kwargs
        return {"orders": "written"}

    monkeypatch.setattr(pipeline, "write_catalogue_evidence", fake_write_catalogue_evidence)
    table_configs = [{"key": "orders", "df": FakeDataFrame("orders"), "expected_schema": {}}]

    result = pipeline.run_table_guardrails(table_configs, table_role="source", mode="profile")

    assert result["can_continue"] is True
    assert captured["profile_behavior"] == {"spark_session": spark, "run_id": "run-123"}
    assert captured["catalogue"]["run_id"] == "run-123"
    assert captured["catalogue"]["pipeline_name"] == "demo_pipeline"
    assert captured["catalogue"]["notebook_id"] == "notebook-1"
    assert captured["catalogue"]["notebook_registry_id"] == "registry-1"
    assert captured["catalogue"]["agreement_id"] == "agreement-1"
    assert captured["catalogue"]["agreement_contract_version"] == "2"
    assert active.source_definitions == {"orders": {"key": "orders", "expected_schema": {}, "table_name": "orders", "stage": "target", "layer": "unified", "kind": "lakehouse", "mode": "overwrite"}}


def test_write_pipeline_run_summary_accepts_guardrail_bundles_from_active_context(monkeypatch):
    """Verify summary writer derives context and guardrail result fields."""
    spark = FakeSpark()
    active = widgets_shared_module.PipelineRunContext(
        run_id="run-123",
        pipeline_started_at="2026-01-01T00:00:00Z",
        pipeline_name="demo_pipeline",
        spark_session=spark,
        notebook_id="notebook-1",
        notebook_registry_id="registry-1",
        agreement_id="agreement-1",
        agreement_contract_version="2",
        source_definitions={"orders": {"table_name": "orders"}},
        target_definitions={"curated": {"table_name": "curated"}},
    )
    monkeypatch.setattr(widgets_shared_module, "_ACTIVE_PIPELINE_CONTEXT", active)
    monkeypatch.setattr(pipeline, "resolve_fabric_context", lambda context=None: (framework_config(), "dev", {"config": framework_config(), "env": "dev"}))
    writes = []
    monkeypatch.setattr(pipeline, "write_lakehouse_table_core", lambda *args, **kwargs: writes.append((args, kwargs)))
    source_results = {"can_continue": True, "schema_results": {"orders": {"status": "passed"}}, "catalogue_status": {"orders": "written"}}
    target_results = {"can_continue": False, "dq_results": {"curated": {"status": "failed"}}, "catalogue_status": {"curated": "written"}}

    row = pipeline.write_pipeline_run_summary(
        source_guardrail_results=source_results,
        target_guardrail_results=target_results,
        target_write_status={"curated": "written"},
        lineage_result={"status": "written"},
    )

    assert row["run_id"] == "run-123"
    assert row["status"] == "failed"
    assert row["pipeline_name"] == "demo_pipeline"
    assert row["lineage_status"] == "written"
    assert row["catalogue_status"] == "written"
    assert writes
