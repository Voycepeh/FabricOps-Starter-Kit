"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path

import pytest

import fabricops_kit
import fabricops_kit.pipeline as pipeline
from fabricops_kit.pipeline import shared as pipeline_shared
widgets_shared_module = importlib.import_module("fabricops_kit.widgets.shared")
from tests.helpers import framework_config

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _canonical_audit(monkeypatch):
    """Provide deterministic canonical audit fields for pipeline helper tests."""
    audit = {
        "_workspace_id": "workspace-id",
        "_workspace_name": "workspace",
        "_notebook_id": "notebook-id",
        "_notebook_name": "02_pipeline",
        "_activity_id": "activity-id",
        "_committed_by": "user",
        "_committed_at": "2026-01-01T00:00:00+00:00",
        "_metadata_lakehouse_name": "lh_metadata_dev",
    }
    monkeypatch.setattr(pipeline_shared, "_runtime_audit_fields", lambda *args, **kwargs: dict(audit))



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
    assert "write_pipeline_lineage" not in fabricops_kit.__all__
    assert "write_pipeline_run_summary" not in fabricops_kit.__all__
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
                "fabric_store_target": "source",
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
            "fabric_store_target": "source",
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


def test_prepare_pipeline_table_configs_requires_explicit_fabric_store_target(monkeypatch):
    """Verify prepare pipeline table configs does not infer FabricStore target from layer fields."""
    _install_fake_pyspark_functions(monkeypatch)
    with pytest.raises(ValueError, match="Table config 'source_01' must define a non-empty fabric_store_target"):
        pipeline.prepare_pipeline_table_configs(
            [{"key": "source_01", "df": FakeDataFrame("source"), "layer": "source", "table_name": "orders_raw"}],
            {},
            table_role="source",
        )
    with pytest.raises(ValueError, match="Table config 'target_01' must define a non-empty fabric_store_target"):
        pipeline.prepare_pipeline_table_configs(
            [{"key": "target_01", "df": FakeDataFrame("target"), "layer": "product", "table_name": "orders"}],
            {},
            table_role="target",
            run_id="run-1",
            pipeline_name="pipeline-1",
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
                "fabric_store_target": "unified",
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
    assert target["fabric_store_target"] == "unified"
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
                "fabric_store_target": "unified",
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


def test_summary_status_treats_baseline_created_as_passed_and_skipped_as_nonblocking():
    """Verify summary status treats baseline created as passed and skipped as nonblocking."""
    assert pipeline_shared._summary_status({"s1": {"status": "baseline_created"}}) == "passed"
    assert pipeline_shared._summary_status({"s1": {"status": "skipped"}}) == "skipped"
    assert pipeline_shared._summary_status({"s1": {"status": "passed"}, "s2": {"status": "skipped"}}) == "passed"


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

    normalized = pipeline_shared._normalize_catalogue_evidence_types(evidence)
    dtypes = dict(normalized.dtypes)

    for column_name in ["row_count", "null_count", "distinct_count"]:
        assert dtypes[column_name] == "bigint"
    for column_name in ["null_percent", "distinct_percent"]:
        assert dtypes[column_name] == "double"
    assert dtypes["run_timestamp"] == "timestamp"
    assert dtypes["dataset_name"] == "string"



def test_private_guardrail_evidence_definitions_excludes_dataframes_and_resolves_target_fields():
    """Verify private guardrail evidence definitions excludes dataframes and resolves target fields."""
    definitions = pipeline_shared._build_guardrail_evidence_definitions(
        [
            {
                "key": "target_01",
                "df": object(),
                "table_name": "orders_curated",
                "stage": "target",
                "target_layer": "product",
                "target_kind": "warehouse",
                "write_mode": "overwrite",
                "fabric_store_target": "product",
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
            "fabric_store_target": "product",
            "layer": "product",
            "kind": "warehouse",
            "mode": "overwrite",
        }
    }


def test_private_guardrail_evidence_definitions_defaults_fabric_store_target():
    """Verify missing FabricStore target defaults to source for evidence."""
    definitions = pipeline_shared._build_guardrail_evidence_definitions([{"key": "source_01", "table_name": "orders"}])
    assert definitions["source_01"]["fabric_store_target"] == "source"


def test_run_table_guardrails_collects_results_and_returns_summary_before_reporting_failures(monkeypatch):
    """Verify run table guardrails collects results and returns summary before reporting failures."""
    calls = []
    catalogue_calls = []

    def fake_profile(dataframe, *, exclude_columns=None, **kwargs):
        calls.append(("profile", dataframe))
        return {"profile_for": dataframe, "df": dataframe}

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

    monkeypatch.setattr(pipeline_shared, "build_profile_dataframe", fake_profile)
    monkeypatch.setattr(pipeline_shared, "_check_schema_runtime", fake_validate)
    monkeypatch.setattr(pipeline_shared, "enforce_freshness", fake_freshness)
    monkeypatch.setattr(pipeline_shared, "enforce_profile_behavior", fake_stability)
    monkeypatch.setattr(pipeline_shared, "_run_active_dq_guardrail", fake_dq)
    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", fake_catalogue)

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
        agreement_version="v1",
    )

    assert result["can_continue"] is False
    assert result["failed_tables"] == ["bad"]
    assert set(result["profiles"]) == {"good", "bad"}
    assert set(result["metadata_table_keys"]) == {"good", "bad"}
    assert all(result["metadata_table_keys"].values())
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
    assert ("profile", "df_bad") in calls
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

    monkeypatch.setattr(pipeline_shared, "build_profile_dataframe", lambda dataframe, **kwargs: {"profile_for": dataframe})
    monkeypatch.setattr(pipeline_shared, "_check_schema_runtime", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "enforce_freshness", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "enforce_profile_behavior", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "_run_active_dq_guardrail", lambda *args, **kwargs: {"status": "passed", "can_continue": True, "checks": []})
    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", lambda *args, **kwargs: {"orders": "written"})

    def fake_result_writer(**kwargs):
        result_writes.append(kwargs)

    monkeypatch.setattr(pipeline_shared, "_write_guardrail_result_row", fake_result_writer)

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
    assert all("run_id" not in write for write in result_writes)

def test_run_table_guardrails_profile_mode_defaults_and_explicit_modes(monkeypatch):
    """Verify profile behavior config uses clean profile_mode values only."""
    stability_calls = []

    monkeypatch.setattr(pipeline_shared, "build_profile_dataframe", lambda dataframe, **kwargs: {"profile_for": dataframe})
    monkeypatch.setattr(pipeline_shared, "_check_schema_runtime", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "enforce_freshness", lambda *args, **kwargs: {"status": "skipped", "can_continue": True})

    def fake_stability(*args, **kwargs):
        stability_calls.append(kwargs)
        return {"status": "passed", "can_continue": True}

    monkeypatch.setattr(pipeline_shared, "enforce_profile_behavior", fake_stability)
    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", lambda *args, **kwargs: {"status": "written"})

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

    monkeypatch.setattr(pipeline_shared, "build_profile_dataframe", lambda dataframe, **kwargs: {"profile_for": dataframe})
    monkeypatch.setattr(pipeline_shared, "_check_schema_runtime", lambda dataframe, expected_schema, *, preset="strict": {"status": "failed", "can_continue": False})
    monkeypatch.setattr(pipeline_shared, "enforce_freshness", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "enforce_profile_behavior", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", lambda *args, **kwargs: {"status": "written"})
    monkeypatch.setattr(pipeline_shared, "stop_if_failed", lambda result: stopped.append(result))

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
    from fabricops_kit.pipeline.guardrails_shared import _check_schema_runtime

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
    from fabricops_kit.pipeline.guardrails_shared import enforce_freshness

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
        pipeline_shared,
        "build_profile_dataframe",
        lambda dataframe, **kwargs: [
            {
                "column_name": "business_date",
                "row_count": dataframe.count(),
                "min_value": "2026-06-01",
                "max_value": "2026-06-01",
            }
        ],
    )
    monkeypatch.setattr(
        pipeline_shared,
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
        pipeline_shared,
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
        pipeline_shared,
        "_run_active_dq_guardrail",
        lambda *args, **kwargs: {"status": "failed", "can_continue": False, "checks": [{"rule_id": "id_required", "status": "failed"}]},
    )
    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", lambda *args, **kwargs: {"orders": "written"})
    monkeypatch.setattr(pipeline_shared, "_write_guardrail_result_row", lambda **kwargs: None)

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
        pipeline_shared,
        "build_profile_dataframe",
        lambda dataframe, **kwargs: [{"column_name": "id", "row_count": dataframe.count()}],
    )
    monkeypatch.setattr(pipeline_shared, "enforce_profile_behavior", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", lambda *args, **kwargs: {"orders": "written"})
    monkeypatch.setattr(pipeline_shared, "_write_guardrail_result_row", lambda **kwargs: None)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("dq_preset='skip' should not call _run_active_dq_guardrail")

    monkeypatch.setattr(pipeline_shared, "_run_active_dq_guardrail", fail_if_called)

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



def test_run_table_guardrails_uses_active_context_defaults(monkeypatch):
    """Verify run_table_guardrails derives omitted runtime parameters from context."""
    spark = FakeSpark()
    active = widgets_shared_module.PipelineRunContext(
        run_id="run-123",
        pipeline_started_at="2026-01-01T00:00:00Z",
        pipeline_name="demo_pipeline",
        spark_session=spark,
        agreement_id="agreement-1",
        agreement_version="2",
        context={"config": "config", "env": "dev"},
    )
    monkeypatch.setattr(widgets_shared_module, "_ACTIVE_PIPELINE_CONTEXT", active)
    monkeypatch.setattr(pipeline_shared, "resolve_fabric_context", lambda context=None: ("config", "dev", context))
    monkeypatch.setattr(pipeline_shared, "build_profile_dataframe", lambda *args, **kwargs: FakeDataFrame("profile"))
    monkeypatch.setattr(pipeline_shared, "_check_schema_runtime", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "enforce_freshness", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    captured = {}
    monkeypatch.setattr(
        pipeline_shared,
        "enforce_profile_behavior",
        lambda spark_session, dataframe, catalogue_table, dataset_name, table_name, **kwargs: captured.setdefault(
            "profile_behavior",
            {"spark_session": spark_session, "activity_id": "activity-id"},
        ) or {"status": "passed", "can_continue": True},
    )
    monkeypatch.setattr(pipeline_shared, "_run_active_dq_guardrail", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(pipeline_shared, "_write_guardrail_result_row", lambda **kwargs: None)

    def fake_write_catalogue_evidence(profiles, definitions, **kwargs):
        captured["catalogue"] = kwargs
        return {"orders": "written"}

    monkeypatch.setattr(pipeline_shared, "write_catalogue_evidence", fake_write_catalogue_evidence)
    table_configs = [{"key": "orders", "df": FakeDataFrame("orders"), "expected_schema": {}}]

    result = pipeline.run_table_guardrails(table_configs, table_role="source", mode="profile")

    assert result["can_continue"] is True
    assert captured["profile_behavior"] == {"spark_session": spark, "activity_id": "activity-id"}
    assert captured["catalogue"]["run_id"] == "run-123"
    assert "pipeline_name" not in captured["catalogue"]
    assert "notebook_id" not in captured["catalogue"]
    assert "notebook_registry_id" not in captured["catalogue"]
    assert captured["catalogue"]["agreement_id"] == "agreement-1"
    assert captured["catalogue"]["agreement_version"] == "2"
    assert active.source_definitions["orders"]["fabric_store_target"] == "source"

