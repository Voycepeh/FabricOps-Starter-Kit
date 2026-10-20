"""Regression coverage for explicit participant selection and exact payload inspection."""

import importlib
import json

import pytest

module = importlib.import_module("fabricops_kit.widgets.widget_select_data_contract")


def _row(version=1, *, table_id="source", active=False):
    columns = [{"column_id": "id", "column_name": "customer_id", "data_type": "decimal(18,4)",
                "precision": 18, "scale": 4, "nullable": False},
               {"column_id": "amount", "column_name": "amount", "data_type": "decimal(20,2)"}]
    rules = [
        {"guardrail_type": "schema", "rule_type": "required_columns", "rule_parameters": {"required_columns": ["id"]}},
        {"guardrail_type": "grain", "rule_type": "uniqueness", "rule_parameters": {"columns": ["customer_id", "amount"], "allow_nulls": False}},
        {"guardrail_type": "data_quality", "rule_type": "range", "column_id": "amount", "rule_parameters": {"minimum": 0, "maximum": version * 100, "maximum_failure_percent": 2}},
        {"guardrail_type": "data_quality", "rule_type": "custom_expression", "is_active": False, "rule_parameters": {"expression": "amount > customer_id"}},
        {"guardrail_type": "freshness", "rule_type": "freshness", "rule_parameters": {"observation_column": "updated", "expected_refresh_frequency": 6, "expected_refresh_unit": "hours", "refresh_expectation": "recurring"}},
        {"guardrail_type": "source_drift", "rule_type": "changes", "rule_parameters": {"partition_column": "day", "change_column": "updated", "comparison_scope": "complete"}},
        {"guardrail_type": "sensitive_data", "rule_type": "mask", "column_id": "id", "rule_parameters": {"treatment": "mask", "preserve_start": 2}},
        {"guardrail_type": "future_kind", "rule_type": "future_rule", "is_active": False, "rule_parameters": {"saved": "must remain visible"}},
    ]
    for index, rule in enumerate(rules):
        rule.update(guardrail_rule_id=f"rule-{index}", action="Block")
        rule.setdefault("is_active", True)
    payload = {"contract": {"contract_id": f"contract-{table_id}", "contract_version": version},
               "table": {"table_id": table_id, "columns": columns, "processing": {"load_strategy": "overwrite"}},
               "guardrails": rules, "enrichment": {"table": [], "columns": []}}
    return {"contract_id": f"contract-{table_id}", "contract_version": version, "table_id": table_id,
            "environment_name": "canary-east", "status": "frozen", "is_active": active,
            "contract_payload_json": json.dumps(payload)}


def _render(monkeypatch, rows, *, interactive=False, metadata_error=None, lineage_state="empty"):
    context = {"config": object(), "env": "canary-east", "notebook_id": "notebook-1"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context_obj["config"], "canary-east", context_obj))
    context_obj = context
    monkeypatch.setattr(module, "get_spark_session", lambda spark=None: object())
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *a: "metadata")
    monkeypatch.setattr(module, "resolve_physical_table_identity", lambda c, e, **kw: {
        **kw, "table_id": kw["table_name"], "store_kind": "lakehouse"})
    reads = []
    def read(name, **kw):
        reads.append(name)
        if name == "METADATA_DATA_LINEAGE" and lineage_state == "missing":
            raise RuntimeError("Lineage table does not exist")
        if metadata_error:
            raise metadata_error
        return type("Frame", (), {"collect": lambda self: rows})()
    monkeypatch.setattr(module, "read_lakehouse_table", read)
    monkeypatch.setattr(module.ip, "display", lambda *a: None)
    if not interactive:
        monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    state = module.widget_select_data_contract(
        sources=[{"store": "Bronze", "schema": "demo", "table_name": "source"}],
        targets=[{"store": "Silver", "schema": "demo", "table_name": "target"}], context=context,
    )
    return context, state, reads


@pytest.mark.parametrize("lineage_state", ["empty", "missing"])
def test_bootstrap_never_requires_lineage_and_no_contract_is_explicit(monkeypatch, lineage_state):
    """An empty contract store does not implicitly choose No Contract or read Lineage."""
    context, state, reads = _render(monkeypatch, [], lineage_state=lineage_state)
    assert state["execution_mode"] == "testing"
    assert all(table["choice"] is None for table in state["tables"].values())
    state["select_contract"]("source", no_contract=True)
    assert state["tables"]["target"]["choice"] is None
    assert reads == ["METADATA_DATA_CONTRACT"]
    assert "data_contract_overrides" not in context


def test_metadata_read_failure_is_not_no_contract(monkeypatch):
    """A permission/read failure must reach the caller."""
    with pytest.raises(RuntimeError, match="permission denied"):
        _render(monkeypatch, [], metadata_error=RuntimeError("permission denied"))


def test_selection_changes_refresh_every_saved_definition_and_isolate_tables(monkeypatch):
    """Version selection drives exact read-only rule details immediately."""
    _, state, _ = _render(monkeypatch, [_row(1), _row(2), _row(table_id="unrelated")], interactive=True)
    state["select_contract"]("source", "contract-source", 1)
    first = state["_controls"]["source"]["inspector"].value
    assert "100" in first and "decimal(18,4)" in first
    state["select_contract"]("source", "contract-source", 2)
    second = state["_controls"]["source"]["inspector"].value
    assert "200" in second and first != second
    assert state["tables"]["target"]["choice"] is None
    assert "unrelated" not in state["tables"]
    with pytest.raises(ValueError, match="participants"):
        state["select_contract"]("unrelated", no_contract=True)


def test_inspector_has_all_columns_rules_parameters_states_and_boundaries():
    """The inspector retains inactive, unknown, composite and non-applicable definitions."""
    row = _row(2)
    review = module._contract_review(row, ["source"])
    assert len(review["columns"]) == 2
    assert review["counts"]["data_quality"] == 2
    assert review["categories"]["grain"][0]["parameters"]["columns"] == ["customer_id", "amount"]
    rendered = module._inspector(row, ["source"])
    for value in ("decimal(18,4)", "decimal(20,2)", "maximum_failure_percent", "custom_expression", "Inactive",
                  "must remain visible", "future_kind", "preserve_start", "Will not run", "hours", "comparison_scope"):
        assert value in rendered
    assert "2 checks · 1 inactive" in rendered
    assert "Raw frozen definition" in rendered


def test_mode_changes_whole_widget_and_preserves_frozen_definition(monkeypatch):
    """Red/green mode changes do not rewrite the inspected JSON."""
    _, state, _ = _render(monkeypatch, [_row(active=True)], interactive=True)
    state["select_contract"]("source", "contract-source", 1)
    before = state["_controls"]["source"]["inspector"].value
    assert "pipeline-testing" in state["widget"]._dom_classes
    state["set_mode"]("live")
    assert "pipeline-live" in state["widget"]._dom_classes
    assert "pipeline-testing" not in state["widget"]._dom_classes
    assert state["_controls"]["source"]["inspector"].value == before
    with pytest.raises(ValueError, match="bypass"):
        state["select_contract"]("source", no_contract=True)


def test_live_rejects_inactive_substitution(monkeypatch):
    """Testing candidates stay selectable; Live only accepts active frozen versions."""
    _, state, _ = _render(monkeypatch, [_row(1, active=True), _row(2)])
    state["select_contract"]("source", "contract-source", 2)
    state["set_mode"]("live")
    assert state["tables"]["source"]["selected"]["contract_version"] == 1
    with pytest.raises(ValueError, match="active frozen"):
        state["select_contract"]("source", "contract-source", 2)


@pytest.mark.parametrize("corruption", ["json", "identity", "multiple_active", "duplicate"])
def test_invalid_contracts_never_become_no_contract(monkeypatch, corruption):
    """Corrupt or ambiguous selected definitions are actionable errors."""
    row = _row(active=True)
    rows = [row]
    if corruption == "json": row["contract_payload_json"] = "{bad"
    if corruption == "identity": row["contract_id"] = "wrong"
    if corruption == "multiple_active": rows.append(_row(2, active=True))
    if corruption == "duplicate": rows = [_row(), _row()]
    with pytest.raises((ValueError, RuntimeError)):
        _render(monkeypatch, rows)
