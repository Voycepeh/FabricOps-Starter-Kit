"""Workspace isolation and global Contract structural invariants."""
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline import shared as pipeline


def observation(workspace, table, columns):
    """Build one current physical observation without requiring any profile."""
    base = {"workspace_id": workspace, "table_id": table, "is_active": True, "_committed_at": "2026-10-27T00:00:00Z"}
    return [{**base, "metadata_level": "table", "table_name": table}, *[
        {**base, "metadata_level": "column", "column_id": name, "column_name": name, "data_type": datatype}
        for name, datatype in columns]]


def test_bidirectional_observation_choices():
    """Either selector constrains the other without selecting a default."""
    rows = observation("A", "customer", []) + observation("A", "orders", []) + observation("B", "customer", []) + observation("B", "inventory", [])
    assert contracts.observation_selector_options(rows, workspace_id="A")["tables"] == ["customer", "orders"]
    assert contracts.observation_selector_options(rows, table_id="inventory")["workspaces"] == ["B"]
    assert contracts.observation_selector_options(rows, table_id="customer")["workspaces"] == ["A", "B"]


def test_inactive_latest_column_never_revives_historical_column():
    """Latest tombstones win before filtering active rows."""
    rows = observation("A", "customer", [("removed", "int"), ("current", "string")])
    rows.append({**rows[1], "is_active": False, "_committed_at": "2026-10-27T01:00:00Z"})
    current = contracts.current_catalogue_observations(rows)
    assert {row.get("column_id") for row in current} == {None, "current"}


@pytest.mark.parametrize("actual,passed", [
    ([("A", "string"), ("B", "int"), ("C", "string")], True),
    ([("A", "string"), ("B", "int")], True),
    ([("A", "string")], False),
    ([("A", "string"), ("B", "int"), ("D", "string")], False),
    ([("A", "string"), ("B", "bigint")], False),
    ([("A", "string"), ("B", "string")], False),
])
def test_contract_columns_supply_mandatory_strict_schema(actual, passed):
    """Presence is distinct from nullability and no authored schema rule is needed."""
    payload = {"table": {"columns": [
        {"column_id": "A", "column_name": "A", "data_type": "string", "nullable": True},
        {"column_id": "B", "column_name": "B", "data_type": "int"},
        {"column_id": "C", "column_name": "C", "data_type": "string", "presence": "optional"},
    ]}, "guardrails": []}
    record = {"contract_id": "global-customer", "contract_version": 3, "contract_payload": payload}
    original = deepcopy(record)
    rules = pipeline.contract_guardrail_rows(record, workspace_id="B", table_id="customer")
    result = pipeline.schema_check_core(SimpleNamespace(dtypes=actual, columns=[name for name, _ in actual]),
        rules_df=rules, workspace_id="B", table_id="customer")
    assert result["can_continue"] is passed
    assert result["status"] == ("passed" if passed else "failed")
    assert record == original


def test_draft_is_global_captures_current_workspace_and_keeps_observed_types(monkeypatch):
    """Another workspace reopens the same draft; removed columns are not inherited."""
    table = "customer"
    lifecycle = contracts.contract_lifecycle_id(table)
    previous = {"contract_id": lifecycle, "contract_version": 3, "table_id": table, "status": "frozen",
        "contract_payload_json": json.dumps({"table": {"table_id": table, "columns": [
            {"column_id": "A", "column_name": "A", "data_type": "int"},
            {"column_id": "removed", "column_name": "removed", "data_type": "int"}],
            "processing": {"load_strategy": "overwrite"}}, "guardrails": [],
            "enrichment": {"table": [], "columns": []}})}
    rows = [previous]
    catalogue = observation("A", table, [("A", "bigint"), ("new", "string")]) + observation("B", table, [("A", "int")])
    monkeypatch.setattr(contracts, "read_lakehouse_table", lambda name, **kw: catalogue if name == "METADATA_DATA_CATALOGUE" else rows)
    monkeypatch.setattr(contracts, "build_runtime_audit_fields", lambda **kw: {})
    monkeypatch.setattr(contracts, "coerce_metadata_row_types", lambda name, row: row)
    monkeypatch.setattr(contracts, "write_lakehouse_table", lambda frame, *args, **kw: rows.extend(frame))
    spark = SimpleNamespace(createDataFrame=lambda values, schema: values)
    draft = contracts.create_contract_draft(table_id=table, config={}, active_workspace_id="A", spark_session=spark)
    columns = json.loads(draft["contract_payload_json"])["table"]["columns"]
    assert [(c["column_name"], c["data_type"], c["presence"]) for c in columns] == [("A", "bigint", "required"), ("new", "string", "required")]
    assert draft["contract_version"] == 4 and draft["evidence_workspace_id"] == "A"
    assert contracts.create_contract_draft(table_id=table, config={}, active_workspace_id="B", spark_session=spark) == draft


@pytest.mark.parametrize("workspace,has_observation", [("A", True), ("B", False)])
def test_later_observation_cannot_change_captured_draft_columns(workspace, has_observation):
    """Saving after a scan keeps the draft schema and datatype captured at creation."""
    captured = {"table_id": "customer", "columns": [{"column_id": "A", "column_name": "A", "data_type": "int", "presence": "required"}],
                "processing": {"load_strategy": "overwrite"}, "processing_source": "default",
                "writer": {"notebook_id": "original-writer", "notebook_name": "Original"}}
    draft = {"contract_id": "global-customer", "contract_version": 4, "table_id": "customer", "status": "draft",
             "evidence_workspace_id": "A", "contract_payload_json": json.dumps({"table": captured})}
    original = deepcopy(draft)
    rows = observation("A", "customer", [("A", "string"), ("later", "int")]) if has_observation else []
    payload, _ = contracts.assemble_contract_payload(draft=draft, catalogue_rows=rows,
        enrichment_rows=[], guardrail_rows=[], workspace_id=workspace)
    assert payload["table"]["columns"] == captured["columns"]
    assert payload["table"]["writer"] == captured["writer"]
    assert draft == original
