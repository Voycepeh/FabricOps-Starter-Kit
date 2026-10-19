"""Regressions for widget-shaped Schema rules through frozen contracts."""
# ruff: noqa: D101, D102, D103, D107

from __future__ import annotations

import importlib
import json
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.io import shared as io_shared
from fabricops_kit.pipeline import shared
from tests.helpers import framework_config
from tests.unit.test_data_contract_resolution import RecordingFrame

pytestmark = pytest.mark.unit


def frozen_contract(required):
    payload = {
        "contract": {"contract_id": "contract-orders", "contract_version": 1},
        "table": {
            "table_id": "orders", "table_name": "orders",
            "processing": {"load_strategy": "overwrite"},
            "columns": [
                {"column_id": "col-id", "column_name": "id", "data_type": "bigint"},
                {"column_id": "col-note", "column_name": "note", "data_type": "string"},
            ],
        },
        "enrichment": {"table": [], "columns": []},
        "guardrails": [{
            "guardrail_rule_id": "schema-orders", "guardrail_version": 2,
            "guardrail_type": "schema", "rule_id": "required_columns",
            "rule_type": "required_columns", "column_id": "",
            "rule_parameters": {"required_columns": required},
            "action": "Block", "is_active": True,
        }],
    }
    return {
        "contract_id": "contract-orders", "contract_version": 1,
        "table_id": "orders", "environment_name": "dev", "status": "frozen",
        "contract_payload_json": json.dumps(payload),
    }


def schema_frame(dtypes):
    # Schema-only double: evaluating rows or null counts is deliberately unsupported.
    return SimpleNamespace(dtypes=dtypes, columns=[name for name, _ in dtypes])


@pytest.mark.parametrize("identifier", ["col-id", "id"])
@pytest.mark.parametrize(
    ("dtypes", "required", "missing", "mismatches", "unexpected"),
    [
        ([("id", "bigint"), ("note", "string")], True, [], [], []),
        ([("note", "string")], True, ["id"], [], []),
        ([("id", "bigint")], True, [], [], []),
        ([("id", "string")], True, [], ["id"], []),
        ([("id", "bigint"), ("note", "bigint")], True, [], ["note"], []),
        ([("id", "bigint"), ("extra", "string")], True, [], [], ["extra"]),
        ([], False, [], [], []),
        ([("note", "bigint")], False, [], ["note"], []),
    ],
    ids=["matching", "missing-required", "missing-unmarked", "required-type",
         "unmarked-type", "additional", "empty-required", "empty-required-type"],
)
def test_adapter_and_evaluator(dtypes, required, missing, mismatches, unexpected, identifier):
    contract = frozen_contract([identifier] if required else [])
    rows = shared.contract_guardrail_rows(contract, environment_name="dev", table_id="orders")
    params = json.loads(rows[0]["rule_parameters_json"])
    assert params["required_columns"] == (["id"] if required else [])
    assert params["data_types"] == {"id": "bigint", "note": "string"}

    result = shared.schema_check_core(
        schema_frame(dtypes), rules_df=rows, table_id="orders", environment_name="dev",
    )

    violation = bool(missing or mismatches)
    status = "failed" if violation else "warning" if unexpected else "passed"
    assert result["status"] == status
    assert result["can_continue"] is (status != "failed")
    assert result["missing_columns"] == missing
    assert [item["column"] for item in result["datatype_mismatches"]] == mismatches
    assert result["unexpected_columns"] == unexpected
    assert result["severity"] == "blocking"
    assert f"validation {status}" in result["message"]


def test_required_is_presence_even_with_null_values():
    rows = shared.contract_guardrail_rows(
        frozen_contract(["col-id"]), environment_name="dev", table_id="orders",
    )
    result = shared.schema_check_core(
        pd.DataFrame({"id": pd.Series([None], dtype="Int64")}),
        rules_df=rows, table_id="orders", environment_name="dev",
    )
    assert result["status"] == "passed"
    assert result["can_continue"] is True


@pytest.mark.parametrize("required", [["col-id"], ["id"], []])
def test_save_freeze_runtime_preserves_selections(monkeypatch, required):
    """Use real save/freeze/resolution code with mocked Delta and metadata transport."""
    contract = frozen_contract(required)
    draft = {**contract, "status": "draft"}
    payload = json.loads(contract["contract_payload_json"])
    spark = MagicMock()
    delta = MagicMock()
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=delta))
    monkeypatch.setattr(contracts, "build_runtime_audit_fields", lambda **_kwargs: {})
    monkeypatch.setattr(io_shared, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "mock-path"))
    config = framework_config()
    monkeypatch.setattr(contracts, "read_lakehouse_table", lambda *_a, **_k: [spark.createDataFrame.call_args.args[0][0]])
    saved = contracts.save_contract_draft(
        draft=draft, payload=payload, config=config, env="dev", spark_session=spark,
    )
    delta.forPath.return_value.alias.return_value.merge.return_value.whenMatchedUpdateAll.return_value.execute.assert_called_once()
    written = spark.createDataFrame.call_args.args[0][0]
    assert written["contract_payload_json"] == saved["contract_payload_json"]
    frozen = contracts.freeze_contract_record(draft=saved, audit={})
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *_a, **_k: RecordingFrame([frozen]))
    context = {"data_contract_overrides": {"orders": {"contract_id": "contract-orders", "contract_version": 1}}}
    resolved = shared.resolve_pipeline_data_contract(config, "dev", "orders", context=context)
    assert resolved["contract_payload"]["guardrails"][0]["rule_parameters"] == {"required_columns": required}
    rows = shared.contract_guardrail_rows(resolved, environment_name="dev", table_id="orders")
    result = shared.schema_check_core(schema_frame([]), rules_df=rows, table_id="orders", environment_name="dev")
    assert result["missing_columns"] == (["id"] if required else [])
    assert result["status"] == ("failed" if required else "passed")


@pytest.mark.parametrize("difference", ["matching", "missing", "datatype", "additional"])
def test_public_check_persists_decision_with_catalogue_drift(monkeypatch, difference):
    """Run real resolution, adapter, evaluator and result writer beneath check_schema."""
    module = importlib.import_module("fabricops_kit.pipeline.check_schema")
    config = framework_config()
    context = {"data_contract_overrides": {"orders": {"contract_id": "contract-orders", "contract_version": 1}}}
    frozen = frozen_contract(["col-id"])
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (config, "dev", context))
    # The current Catalogue has drifted to string; the frozen contract remains bigint.
    catalogue = [
        {"table_id": "orders", "table_name": "orders", "metadata_level": "table",
         "environment_name": "dev", "layer": "Bronze", "store_type": "lakehouse", "schema_name": "dbo"},
        {"table_id": "orders", "column_id": "col-id", "column_name": "id",
         "metadata_level": "column", "environment_name": "dev", "data_type": "string"},
    ]
    monkeypatch.setattr(
        shared, "read_lakehouse_table",
        lambda table, **_k: RecordingFrame(catalogue if table == "METADATA_DATA_CATALOGUE" else [frozen]),
    )
    monkeypatch.setattr(module, "resolve_lakehouse_table_location", lambda *_a: ("orders", "dbo", "mock-path"))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **_k: {"_activity_id": "test-run"})
    writes = []
    monkeypatch.setattr(shared, "write_lakehouse_table", lambda frame, table, **kwargs: writes.append((frame, table, kwargs)))
    spark = SimpleNamespace(createDataFrame=lambda rows: RecordingFrame(rows))
    dataframe = schema_frame({
        "matching": [("id", "bigint")],
        "missing": [],
        "datatype": [("id", "string")],
        "additional": [("id", "bigint"), ("extra", "string")],
    }[difference])
    blocking = difference in {"missing", "datatype"}
    arguments = dict(dataframe=dataframe, table_id="orders", spark_session=spark, verbose=False)
    result = module.check_schema(**arguments)
    assert len(writes) == 1
    frame, table, routing = writes[0]
    persisted = frame.rows[0]
    assert table == "METADATA_GUARDRAIL_RESULTS"
    assert routing["store"] == "Metadata"
    expected_status = "failed" if blocking else "warning" if difference == "additional" else "passed"
    assert persisted["status"] == result["status"] == expected_status
    assert persisted["can_continue"] == result["can_continue"] == (not blocking)
    assert persisted["action"] == "Block"
    assert persisted["severity"] == result["severity"]
    assert persisted["reason"] == result["message"]
    assert persisted["contract_id"] == "contract-orders"
    assert persisted["contract_version"] == 1
    assert json.loads(persisted["result_payload_json"])["actual"] == result["actual"]
    if difference == "datatype":
        assert result["datatype_mismatches"] == [{"column": "id", "expected": "bigint", "actual": "string"}]
