"""Focused tests for the governed single-table Data Agent flow."""

# ruff: noqa: D103

from types import SimpleNamespace

import pytest

from fabricops_kit.data_agent import shared


def _config(kind="lakehouse"):
    store = SimpleNamespace(workspace_id="source-workspace", item_id="source-item", kind=kind)
    return SimpleNamespace(path_config=SimpleNamespace(paths={"prod": {"Production": store}}))


def _contract():
    return {
        "contract_id": "contract-1", "contract_version": 2,
        "agreement_id": "agreement-1", "agreement_version": "3",
        "contract_payload": {
            "table": {
                "table_id": "orders-id", "columns": [
                    {"column_id": "orders-id||customer", "column_name": "customer", "data_type": "string"},
                    {"column_id": "orders-id||order_id", "column_name": "order_id", "data_type": "long"},
                ],
                "scheduled_refresh": {"status": "configured", "schedules": [{"frequency": "Daily"}]},
            },
            "enrichment": {
                "table": [
                    {"enrichment_type": "Description", "value": "Approved customer orders"},
                    {"enrichment_type": "Grain", "value": "One row per order"},
                ],
                "columns": [
                    {"column_id": "orders-id||order_id", "enrichment_type": "Description", "value": "Stable order key"},
                    {"column_id": "orders-id||customer", "enrichment_type": "Sensitive Data", "value": "Confidential"},
                ],
            },
            "guardrails": [{"guardrail_type": "Data Quality", "rule_id": "unique-order", "rule_type": "uniqueness", "column_id": "orders-id||order_id", "is_active": True}],
        },
    }


@pytest.fixture
def governed(monkeypatch):
    monkeypatch.setattr(shared, "resolve_catalogue_table_identity", lambda *_a, **_k: {
        "table_id": "orders-id", "layer": "Gold", "store_type": "lakehouse",
        "schema": "dbo", "table_name": "orders",
    })
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *_a, **_k: _contract())
    monkeypatch.setattr(shared, "get_store", lambda *_a, **_k: SimpleNamespace(
        workspace_id="source-workspace", item_id="source-item", kind="lakehouse"
    ))


def test_context_is_deterministic_and_projects_safe_governed_values(governed):
    first = shared.consumer_context(_config(), "orders-id")
    second = shared.consumer_context(_config(), "orders-id")
    assert first == second
    assert first["description"] == "Approved customer orders"
    assert first["grain"] == "One row per order"
    assert [column["name"] for column in first["columns"]] == ["customer", "order_id"]
    assert first["columns"][1]["description"] == "Stable order key"
    serialized = repr(first).casefold()
    assert "token" not in serialized
    assert "example_values" not in serialized
    assert "min_value" not in serialized


def test_context_rejects_missing_table(monkeypatch):
    monkeypatch.setattr(shared, "resolve_catalogue_table_identity", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("missing table")))
    with pytest.raises(ValueError, match="missing table"):
        shared.consumer_context(_config(), "missing")


def test_context_rejects_missing_active_contract(monkeypatch):
    monkeypatch.setattr(shared, "resolve_catalogue_table_identity", lambda *_a, **_k: {"table_id": "x", "layer": "Production", "store_type": "lakehouse", "table_name": "x"})
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("No active Data Contract")))
    with pytest.raises(ValueError, match="No active Data Contract"):
        shared.consumer_context(_config(), "x")


def test_context_rejects_invalid_source(monkeypatch):
    monkeypatch.setattr(shared, "resolve_catalogue_table_identity", lambda *_a, **_k: {"table_id": "orders-id", "layer": "Unsupported", "store_type": "eventhouse", "table_name": "orders"})
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *_a, **_k: _contract())
    monkeypatch.setattr(shared, "get_store", lambda *_a, **_k: SimpleNamespace(workspace_id="w", item_id="i", kind="eventhouse"))
    with pytest.raises(ValueError, match="unsupported"):
        shared.consumer_context(_config(), "orders-id")


def test_renderer_is_stable_and_omits_absent_optional_values(governed):
    context = shared.consumer_context(_config(), "orders-id")
    assert shared.instruction_text(context) == shared.instruction_text(context)
    rendered = shared.instruction_text(context)
    assert "dbo.orders" in rendered["datasource"]
    assert "Stable order key" in rendered["datasource"]
    assert "access token" not in rendered["datasource"].casefold()
    assert "Handling ambiguity" in rendered["agent"]
    assert "Never silently choose" in rendered["agent"]
    minimal = shared.instruction_text({"source": {"table": "x", "schema": None}, "columns": []})
    assert "Purpose:" not in minimal["datasource"]


def test_renderer_surfaces_datetime_ambiguity_without_inventing_default_semantics():
    context = {
        "source": {"table": "orders", "schema": "dbo"},
        "columns": [
            {"name": "order_date", "data_type": "date", "description": "Date the order was placed"},
            {"name": "ship_date", "data_type": "timestamp", "description": "Date and time the order was shipped"},
            {"name": "amount", "data_type": "decimal"},
        ],
    }
    rendered = shared.instruction_text(context)
    datasource = rendered["datasource"]
    assert "## Date and time interpretation" in datasource
    assert "- order_date: Date the order was placed" in datasource
    assert "- ship_date: Date and time the order was shipped" in datasource
    assert "ask which field they want" in datasource
    assert "default date" not in datasource.casefold()


def _responses(*responses):
    queue = list(responses)
    calls = []
    def transport(method, url, body, token):
        calls.append((method, url, body, token))
        return queue.pop(0)
    return transport, calls


def _agent_context(source_type="lakehouse"):
    return {"table_id": "orders-id", "source": {"type": source_type, "workspace_id": "source-workspace", "item_id": "source-item", "schema": "dbo", "table": "orders"}, "columns": []}


@pytest.mark.parametrize(("source_type", "expected_type", "reference_name"), [
    ("lakehouse", "LakehouseTables", "lakehouseReference"),
    ("warehouse", "FabricItem", "itemReference"),
])
def test_successful_synchronous_agent_configuration(source_type, expected_type, reference_name):
    transport, calls = _responses(
        shared.FabricResponse(201, {}, {"id": "agent-1"}),
        shared.FabricResponse(201, {}, {"id": "source-1"}),
        shared.FabricResponse(200, {}, {"status": "updated"}),
        shared.FabricResponse(200, {}, {"value": [{"id": "element-1", "type": "Table", "schema": "dbo", "name": "orders"}]}),
        shared.FabricResponse(200, {}, {"status": "updated"}),
        shared.FabricResponse(200, {}, {"status": "configured"}),
    )
    context = _agent_context(source_type)
    result = shared.provision_data_agent(context, target_workspace_id="target", display_name="Orders", description="desc", token_provider=lambda: "secret", transport=transport)
    assert result == {"agent_id": "agent-1", "datasource_id": "source-1", "workspace_id": "target", "display_name": "Orders", "status": "configured", "source_table_id": "orders-id"}
    assert [call[0] for call in calls] == ["POST", "POST", "PATCH", "GET", "PATCH", "PATCH"]
    assert all(call[3] == "secret" for call in calls)
    assert calls[1][2] == {
        "displayName": "orders",
        "type": expected_type,
        reference_name: {
            "referenceType": "ById",
            "workspaceId": "source-workspace",
            "itemId": "source-item",
        },
    }
    assert calls[2][1].endswith("/staging/dataSources/source-1")
    assert calls[2][2] == {"instructions": shared.instruction_text(context)["datasource"]}
    assert calls[3][1].endswith("/staging/dataSources/source-1/elements")
    assert calls[3][2] is None
    assert calls[4][1].endswith("/staging/dataSources/source-1/elements?id=element-1")
    assert calls[4][2] == {"isSelected": True}
    assert calls[5][1].endswith("/staging/settings")
    assert calls[5][2] == {"aiInstructions": shared.instruction_text(context)["agent"]}


def test_asynchronous_creation_obeys_location_and_retry_after():
    transport, calls = _responses(
        shared.FabricResponse(202, {"Location": "https://api.fabric.microsoft.com/v1/operations/op", "Retry-After": "3"}, None),
        shared.FabricResponse(200, {}, {"status": "Succeeded", "result": {"id": "agent-1"}}),
    )
    sleeps = []
    result = shared.fabric_request("POST", "/workspaces/w/dataAgents", {}, token="t", transport=transport, sleep=sleeps.append)
    assert result["id"] == "agent-1"
    assert sleeps == [3.0]
    assert calls[1][1].endswith("/operations/op")


@pytest.mark.parametrize("status,body,match", [
    (403, {"error": "Forbidden"}, "HTTP 403"),
    (200, None, "malformed"),
])
def test_api_errors_are_not_masked(status, body, match):
    if status == 403:
        def transport(*_args):
            raise shared.FabricDataAgentError("Fabric API POST failed with HTTP 403: Forbidden")
    else:
        def transport(*_args):
            return shared.FabricResponse(status, {}, body)
    with pytest.raises(shared.FabricDataAgentError, match=match):
        shared.fabric_request("POST", "/x", {}, token="t", transport=transport)


def test_malformed_create_response_fails():
    transport, _ = _responses(shared.FabricResponse(201, {}, {"name": "missing id"}))
    with pytest.raises(shared.FabricDataAgentError, match="did not include an id"):
        shared.provision_data_agent(_agent_context(), target_workspace_id="target", display_name="Orders", description="", token_provider=lambda: "t", transport=transport)


@pytest.mark.parametrize("elements", [None, [], [{"id": "wrong", "type": "Table", "schema": "dbo", "name": "customers"}]])
def test_datasource_element_discovery_requires_exact_governed_table(elements):
    body = {} if elements is None else {"value": elements}
    transport, _ = _responses(
        shared.FabricResponse(201, {}, {"id": "agent-1"}),
        shared.FabricResponse(201, {}, {"id": "source-1"}),
        shared.FabricResponse(200, {}, {"status": "updated"}),
        shared.FabricResponse(200, {}, body),
    )
    with pytest.raises(shared.FabricDataAgentError, match="value list|exactly one matching"):
        shared.provision_data_agent(
            _agent_context(), target_workspace_id="target", display_name="Orders", description="",
            token_provider=lambda: "t", transport=transport,
        )
