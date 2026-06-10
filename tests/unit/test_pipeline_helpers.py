from __future__ import annotations

import json
import sys
import types

import pytest

import fabricops_kit
from fabricops_kit import pipeline

pytestmark = pytest.mark.unit


class FakeSpark:
    def __init__(self):
        self.created = []

    def createDataFrame(self, rows, schema=None):
        self.created.append((rows, schema))
        return {"rows": rows, "schema": schema}


def test_public_pipeline_helpers_are_exported_without_wrapper_bloat():
    assert "prepare_source_table_configs" in fabricops_kit.__all__
    assert "prepare_target_table_configs" in fabricops_kit.__all__
    assert "write_target_tables" in fabricops_kit.__all__
    assert "build_guardrail_evidence_definitions" in fabricops_kit.__all__
    assert "run_table_guardrails" in fabricops_kit.__all__
    assert "guardrail_summary" in fabricops_kit.__all__
    assert "stop_if_any_guardrail_failed" in fabricops_kit.__all__
    assert "write_catalogue_evidence" in fabricops_kit.__all__
    assert "write_pipeline_lineage" in fabricops_kit.__all__
    assert "write_pipeline_run_summary" in fabricops_kit.__all__
    for removed_name in {
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


class FakeDataFrame:
    def __init__(self, name="df"):
        self.name = name
        self.with_columns = []

    def withColumn(self, name, value):
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


def test_prepare_source_table_configs_derives_defaults_and_reads_lakehouse_table(monkeypatch):
    calls = []

    def fake_read(config, env, layer, table, *, spark_session=None):
        calls.append((config, env, layer, table, spark_session))
        return "loaded_df"

    monkeypatch.setattr(pipeline, "read_lakehouse_table", fake_read)

    enriched, by_key = pipeline.prepare_source_table_configs(
        [
            {
                "key": "source_01",
                "layer": "source",
                "table_name": "orders_raw",
                "watermark_column": "business_date",
            }
        ],
        {
            "schema_preset": "allow_new_columns",
            "data_behavior": "changing",
            "watermark_value": "default_should_be_overridden",
        },
        config={"config": True},
        env="dev",
        spark_session="spark",
    )

    assert calls == [({"config": True}, "dev", "source", "orders_raw", "spark")]
    assert enriched == [
        {
            "schema_preset": "allow_new_columns",
            "data_behavior": "changing",
            "watermark_value": None,
            "key": "source_01",
            "layer": "source",
            "table_name": "orders_raw",
            "watermark_column": "business_date",
            "dataset_name": "orders_raw",
            "stage": "source",
            "df": "loaded_df",
        }
    ]
    assert by_key["source_01"] is enriched[0]


def test_prepare_source_table_configs_supports_explicit_read_patterns(monkeypatch):
    calls = []

    monkeypatch.setattr(pipeline, "read_lakehouse_csv", lambda *args, **kwargs: calls.append(("csv", args, kwargs)) or "csv_df")
    monkeypatch.setattr(pipeline, "read_lakehouse_parquet", lambda *args, **kwargs: calls.append(("parquet", args, kwargs)) or "parquet_df")
    monkeypatch.setattr(pipeline, "read_lakehouse_excel", lambda *args, **kwargs: calls.append(("excel", args, kwargs)) or "excel_df")
    monkeypatch.setattr(pipeline, "read_warehouse_table", lambda *args, **kwargs: calls.append(("warehouse", args, kwargs)) or "warehouse_df")

    class FakeReader:
        def table(self, table_name):
            calls.append(("spark_table", table_name))
            return "spark_table_df"

    fake_spark = types.SimpleNamespace(read=FakeReader())
    configs = [
        {"key": "csv", "layer": "source", "table_name": "csv_t", "read_type": "csv", "relative_path": "raw/orders.csv"},
        {"key": "parquet", "layer": "source", "table_name": "parquet_t", "read_type": "parquet", "relative_path": "raw/orders.parquet"},
        {"key": "excel", "layer": "source", "table_name": "excel_t", "read_type": "excel", "relative_path": "raw/orders.xlsx", "sheet_name": "Sheet1"},
        {"key": "wh", "layer": "warehouse", "table_name": "orders", "read_type": "warehouse", "schema": "sales", "warehouse_target": "product"},
        {"key": "spark", "layer": "source", "table_name": "orders", "read_type": "spark_table", "spark_table": "db.orders"},
    ]

    enriched, by_key = pipeline.prepare_source_table_configs(configs, {}, {}, "dev", fake_spark)

    assert [config["df"] for config in enriched] == ["csv_df", "parquet_df", "excel_df", "warehouse_df", "spark_table_df"]
    assert by_key["spark"]["dataset_name"] == "orders"
    assert calls[0][0] == "csv"
    assert calls[1][0] == "parquet"
    assert calls[2][0] == "excel"
    assert calls[3][0] == "warehouse"
    assert calls[4] == ("spark_table", "db.orders")


def test_prepare_target_table_configs_adds_audit_columns_and_derives_write_defaults(monkeypatch):
    _install_fake_pyspark_functions(monkeypatch)
    df = FakeDataFrame("target")

    enriched, by_key = pipeline.prepare_target_table_configs(
        [
            {
                "key": "target_01",
                "df": df,
                "layer": "unified",
                "table_name": "orders_curated",
            }
        ],
        {"schema_preset": "allow_new_columns", "write_mode": "overwrite", "target_kind": "lakehouse"},
        run_id="run-1",
        pipeline_name="pipeline-1",
    )

    target = enriched[0]
    assert target["dataset_name"] == "orders_curated"
    assert target["stage"] == "unified"
    assert target["target_layer"] == "unified"
    assert target["target_name"] == "orders_curated"
    assert target["target_kind"] == "lakehouse"
    assert target["watermark_value"] is None
    assert by_key["target_01"] is target
    assert [name for name, _value in df.with_columns] == [
        "_fabricops_run_id",
        "_fabricops_pipeline_name",
        "_fabricops_created_at",
    ]


def test_write_target_tables_writes_lakehouse_and_warehouse_targets(monkeypatch):
    calls = []
    monkeypatch.setattr(pipeline, "write_lakehouse_table", lambda *args, **kwargs: calls.append(("lakehouse", args, kwargs)))
    monkeypatch.setattr(pipeline, "write_warehouse_table", lambda *args, **kwargs: calls.append(("warehouse", args, kwargs)))

    status = pipeline.write_target_tables(
        [
            {
                "key": "lake",
                "df": "lake_df",
                "target_kind": "lakehouse",
                "target_layer": "unified",
                "target_name": "orders",
                "write_mode": "overwrite",
                "partition_by": ["business_date"],
                "repartition_by": ["customer_id"],
                "overwrite_schema": True,
            },
            {
                "key": "wh",
                "df": "warehouse_df",
                "target_kind": "warehouse",
                "target_layer": "product",
                "schema": "sales",
                "target_name": "orders_product",
                "mode": "append",
            },
        ],
        config={"config": True},
        env="dev",
    )

    assert status == {"lake": "written", "wh": "written"}
    assert calls[0] == (
        "lakehouse",
        ("lake_df", {"config": True}, "dev", "unified", "orders"),
        {
            "mode": "overwrite",
            "partition_by": ["business_date"],
            "repartition_by": ["customer_id"],
            "overwrite_schema": True,
        },
    )
    assert calls[1] == (
        "warehouse",
        ("warehouse_df", {"config": True}, "dev", "product", "sales", "orders_product"),
        {"mode": "append"},
    )


def test_write_target_tables_rejects_unsupported_target_kind():
    with pytest.raises(ValueError, match="Unsupported target kind for bad: file"):
        pipeline.write_target_tables([{"key": "bad", "df": object(), "target_kind": "file"}], {}, "dev")


def test_write_pipeline_lineage_supports_many_to_many_relationships(monkeypatch):
    writes = []
    monkeypatch.setattr(pipeline, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    result = pipeline.write_pipeline_lineage(
        spark=FakeSpark(),
        config={},
        env="dev",
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
    writes = []
    fake_spark = FakeSpark()
    monkeypatch.setattr(pipeline, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    row = pipeline.write_pipeline_run_summary(
        spark=fake_spark,
        config={},
        env="dev",
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
    assert pipeline._summary_status({"s1": {"status": "baseline_created"}}) == "passed"
    assert pipeline._summary_status({"s1": {"status": "skipped"}}) == "skipped"
    assert pipeline._summary_status({"s1": {"status": "passed"}, "s2": {"status": "skipped"}}) == "passed"



def test_build_guardrail_evidence_definitions_excludes_dataframes_and_resolves_target_fields():
    definitions = pipeline.build_guardrail_evidence_definitions(
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


def test_run_table_guardrails_collects_results_before_reporting_failures(monkeypatch):
    calls = []
    catalogue_calls = []

    def fake_profile(dataframe, *, table_name, exclude_columns=None, include_distributions=True, distribution_columns=None):
        calls.append(("profile", table_name))
        return {"profile_for": table_name, "df": dataframe}

    def fake_validate(dataframe, expected_schema, *, preset="strict"):
        calls.append(("schema", dataframe))
        return {"status": "failed" if dataframe == "df_bad" else "passed", "can_continue": dataframe != "df_bad"}

    def fake_stability(*args, **kwargs):
        calls.append(("stability", args[4]))
        return {"status": "passed", "can_continue": True}

    def fake_dq(dataframe, config, env, dataset_name, table_name, *, spark_session=None):
        calls.append(("dq", table_name))
        result = {"status": "passed", "can_continue": True, "checks": []}
        if table_name == "orders_good":
            result["dataframe"] = "df_good_checked"
        return result

    def fake_catalogue(profiles, definitions, **kwargs):
        catalogue_calls.append((profiles, definitions, kwargs))
        return {"status": "written"}

    monkeypatch.setattr(pipeline, "profile_dataframe", fake_profile)
    monkeypatch.setattr(pipeline, "validate_schema", fake_validate)
    monkeypatch.setattr(pipeline, "enforce_catalogue_stability", fake_stability)
    monkeypatch.setattr(pipeline, "enforce_dq_rules", fake_dq)
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
        config={"config": True},
        env="dev",
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
    assert set(result["stability_results"]) == {"good", "bad"}
    assert result["dq_results"]["bad"]["status"] == "skipped"
    assert table_configs[0]["df"] == "df_good_checked"
    assert ("profile", "orders_bad") in calls
    assert ("stability", "orders_bad") in calls
    assert catalogue_calls
    assert catalogue_calls[0][2]["schema_results"] == result["schema_results"]


def test_guardrail_summary_returns_concise_display_fields():
    result = {
        "schema_results": {"t": {"status": "passed"}},
        "stability_results": {"t": {"status": "passed"}},
        "dq_results": {"t": {"status": "passed"}},
        "catalogue_status": {"status": "written"},
        "failed_tables": [],
        "profiles": {"t": object()},
    }

    assert pipeline.guardrail_summary(result) == {
        "schema_results": result["schema_results"],
        "stability_results": result["stability_results"],
        "dq_results": result["dq_results"],
        "catalogue_status": result["catalogue_status"],
        "failed_tables": [],
    }


def test_stop_if_any_guardrail_failed_delegates_to_standard_stopper(monkeypatch):
    stopped = []
    monkeypatch.setattr(pipeline, "stop_if_failed", lambda result: stopped.append(result))

    pipeline.stop_if_any_guardrail_failed({"can_continue": True, "failed_tables": []})
    assert stopped == []

    pipeline.stop_if_any_guardrail_failed({"can_continue": False, "failed_tables": ["orders"]})
    assert stopped[0]["status"] == "failed"
    assert stopped[0]["can_continue"] is False
    assert stopped[0]["failed_tables"] == ["orders"]
