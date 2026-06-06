from __future__ import annotations

import pytest

from fabricops_kit import governance_review as gov


def _profile_rows(run="run-2"):
    return [
        {
            "metadata_table_key": "table-key",
            "metadata_column_key": "col-order",
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "order_id",
            "layer": "product",
            "asset_kind": "table",
            "profile_run_id": run,
            "profile_stage": "target",
            "profile_status": "success",
            "data_type": "string",
            "row_count": 10,
            "null_count": 0,
            "distinct_count": 10,
            "profiled_at": "2026-01-02T00:00:00Z",
        },
        {
            "metadata_table_key": "table-key",
            "metadata_column_key": "col-amount",
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "amount",
            "layer": "product",
            "asset_kind": "table",
            "profile_run_id": run,
            "profile_stage": "target",
            "profile_status": "success",
            "data_type": "double",
            "row_count": 10,
            "null_count": 1,
            "distinct_count": 8,
            "profiled_at": "2026-01-02T00:00:00Z",
        },
    ]


def test_catalogue_selector_returns_one_logical_table_per_latest_successful_profile():
    rows = [
        {**_profile_rows("run-1")[0], "profiled_at": "2026-01-01T00:00:00Z"},
        *_profile_rows("run-2"),
        {**_profile_rows("run-3")[0], "profile_status": "failed", "profiled_at": "2026-01-03T00:00:00Z"},
        {**_profile_rows("run-x")[0], "dataset_name": "finance", "table_name": "ledger", "profiled_at": "2026-01-04T00:00:00Z"},
    ]
    options = gov.catalogue_table_options(rows)
    assert len(options) == 2
    orders = next(o for o in options if o["table_name"] == "orders")
    assert orders["profile_run_id"] == "run-2"
    assert orders["metadata_table_key"] == "table-key"


def test_catalogue_selector_clear_errors_for_missing_and_no_success():
    with pytest.raises(ValueError, match="no rows"):
        gov.catalogue_table_options([])
    with pytest.raises(ValueError, match="no successful"):
        gov.catalogue_table_options([{**_profile_rows()[0], "profile_status": "failed"}])


def test_business_context_requires_explicit_human_commit_and_preserves_keys():
    rows = gov.build_column_context_records(
        _profile_rows(),
        [
            {"column_name": "order_id", "business_context": "AI suggestion only", "review_status": "approved"},
            {"column_name": "amount", "business_context": "Approved order amount", "review_status": "approved", "commit": True},
        ],
        approved_by="reviewer@example.com",
    )
    assert len(rows) == 1
    assert rows[0]["metadata_column_key"] == "col-amount"
    assert rows[0]["metadata_table_key"] == "table-key"
    assert rows[0]["approved_by"] == "reviewer@example.com"


def test_ai_suggestions_are_not_persisted_automatically_when_fabric_ai_unavailable():
    class NoAiFrame:
        pass

    assert gov.optional_ai_generate_response(NoAiFrame(), prompt="x") is None
    assert gov.build_column_context_records(_profile_rows(), [{"column_name": "amount", "business_context": "suggested", "ai_suggestion": {"text": "AI"}, "review_status": "approved"}]) == []


def test_dq_rules_are_written_only_after_approval_and_keep_append_only_records():
    reviewed = [
        {"rule_id": "orders.amount.range", "column_name": "amount", "rule_type": "value_range", "rule_parameters": {"min": 0}, "review_status": "pending", "commit": True},
        {"rule_id": "orders.order_id.not_null", "column_name": "order_id", "rule_type": "not_null", "rule_parameters": {}, "review_status": "approved", "commit": True},
    ]
    first = gov.build_dq_rule_records(_profile_rows(), reviewed, approved_by="human")
    second = gov.build_dq_rule_records(_profile_rows(), reviewed[1:], approved_by="human")
    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["rule_id"] == second[0]["rule_id"]
    assert first[0]["rule_key"] == second[0]["rule_key"]
    assert first is not second


def test_classification_rows_are_written_only_after_approval_and_valid_values():
    rows = gov.build_classification_records(
        _profile_rows(),
        [
            {"column_name": "order_id", "sensitivity_label": "confidential", "personal_data_classification": "indirect_identifier", "review_status": "approved", "commit": True},
            {"column_name": "amount", "sensitivity_label": "public", "personal_data_classification": "not_personal_data", "review_status": "approved"},
        ],
    )
    assert len(rows) == 1
    assert rows[0]["metadata_column_key"] == "col-order"
    with pytest.raises(ValueError, match="Unsupported sensitivity"):
        gov.build_classification_records(_profile_rows(), [{"column_name": "order_id", "sensitivity_label": "secret", "personal_data_classification": "unknown", "review_status": "approved", "commit": True}])


def test_latest_approved_values_load_by_column_key():
    latest = gov.latest_by_column([
        {"metadata_column_key": "col-order", "business_context": "old", "review_status": "approved", "approved_at": "2026-01-01"},
        {"metadata_column_key": "col-order", "business_context": "new", "review_status": "approved", "approved_at": "2026-01-02"},
        {"metadata_column_key": "col-amount", "business_context": "draft", "review_status": "pending", "approved_at": "2026-01-03"},
    ])
    assert latest["col-order"]["business_context"] == "new"
    assert "col-amount" not in latest


def test_metadata_schemas_are_prepared_by_env_config_without_data_contract():
    schemas = gov.get_governance_metadata_schemas()
    assert "METADATA_DATA_CATALOGUE" in schemas
    assert "METADATA_COLUMN_CONTEXT" in schemas
    assert "METADATA_DQ_RULES" in schemas
    assert "METADATA_COLUMN_CLASSIFICATION" in schemas
    assert "METADATA_DATA_LINEAGE_TABLE" in schemas
    assert not any("CONTRACT" in name for name in schemas)


def test_governance_metadata_schemas_use_explicit_spark_types():
    from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, TimestampType

    schemas = gov.get_governance_metadata_schemas()
    catalogue = {field.name: field.dataType for field in schemas["METADATA_DATA_CATALOGUE"].fields}
    dq_rules = {field.name: field.dataType for field in schemas["METADATA_DQ_RULES"].fields}

    assert isinstance(catalogue["row_count"], LongType)
    assert isinstance(catalogue["null_count"], LongType)
    assert isinstance(catalogue["distinct_count"], LongType)
    assert isinstance(catalogue["null_percent"], DoubleType)
    assert isinstance(catalogue["RUN_TIMESTAMP"], TimestampType)
    assert isinstance(dq_rules["is_active"], BooleanType)
    assert isinstance(dq_rules["approved_at"], StringType)


def test_load_catalogue_profile_rows_filters_profile_stage_and_table_key(monkeypatch):
    rows = [
        *_profile_rows("run-2"),
        {**_profile_rows("run-2")[0], "profile_stage": "source", "metadata_column_key": "source-col"},
        {**_profile_rows("run-2")[0], "metadata_table_key": "other-table-key", "metadata_column_key": "other-table-col"},
    ]

    monkeypatch.setattr(gov, "read_lakehouse_table", lambda *args, **kwargs: rows)

    selected = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "table-key",
        "profile_run_id": "run-2",
        "profile_stage": "target",
    }
    loaded = gov.load_catalogue_profile_rows("config", "dev", selected, spark_session="spark")

    assert {row["metadata_column_key"] for row in loaded} == {"col-order", "col-amount"}


def test_setup_governance_metadata_tables_creates_only_for_confirmed_missing_tables(monkeypatch):
    class FakeTable:
        def __init__(self, columns):
            self.columns = columns

    class FakeSpark:
        def __init__(self):
            self.created_schemas = []

        def createDataFrame(self, rows, schema=None):
            self.created_schemas.append(schema)
            return FakeTable(schema.fieldNames())

    reads = {table: 0 for table in gov.get_governance_metadata_schemas()}
    writes = []

    def fake_read(config, env, target, table, spark_session=None):
        reads[table] += 1
        if reads[table] == 1:
            raise Exception("[PATH_NOT_FOUND] Path does not exist")
        return FakeTable(gov.get_governance_metadata_schemas()[table].fieldNames())

    def fake_write(df, config, env, target, table, **kwargs):
        writes.append((table, kwargs))

    spark = FakeSpark()
    monkeypatch.setattr(gov, "read_lakehouse_table", fake_read)
    monkeypatch.setattr(gov, "write_lakehouse_table", fake_write)

    result = gov.setup_governance_metadata_tables(spark=spark, config="config", env="dev")

    assert result["created_tables"] == list(gov.get_governance_metadata_schemas())
    assert all(schema is not None for schema in spark.created_schemas)
    assert {kwargs["mode"] for _, kwargs in writes} == {"ignore"}


def test_setup_governance_metadata_tables_does_not_create_for_permission_errors(monkeypatch):
    class FakeSpark:
        def createDataFrame(self, rows, schema=None):  # pragma: no cover - should not be called
            raise AssertionError("createDataFrame should not be called for permission errors")

    monkeypatch.setattr(gov, "read_lakehouse_table", lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError("access denied")))
    monkeypatch.setattr(gov, "write_lakehouse_table", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("write should not be called")))

    with pytest.raises(RuntimeError, match="not a confirmed table-not-found"):
        gov.setup_governance_metadata_tables(spark=FakeSpark(), config="config", env="dev")
