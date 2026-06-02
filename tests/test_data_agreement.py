from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

import fabricops_kit.data_agreement as data_agreement
from fabricops_kit.config import DataAgreementConfig
from fabricops_kit.data_agreement import (
    DATA_AGREEMENT_TABLE,
    DATA_STEWARD_TABLE,
    create_or_update_data_agreement,
    create_or_update_data_steward,
    deserialize_custom_fields,
    ensure_metadata_tables,
    get_data_agreement_schema,
    get_data_steward_schema,
    get_standard_runtime_audit_columns,
    get_widget_visible_fields,
    list_data_stewards,
    render_custom_fields,
    serialize_custom_fields,
)
from fabricops_kit.fabric_input_output import FabricStore


def _config():
    store = FabricStore(env="dev", workspace_id="workspace", item_id="metadata-item", name="lh_metadata_dev", kind="lakehouse")
    intake = DataAgreementConfig(
        data_steward_widget={
            "visible_columns": ["steward_id", "steward_name", "steward_role", "contact", "effective_from", "effective_to", "is_active", "_activity_id"],
            "custom_fields": [{"key": "group", "label": "Group", "type": "text", "required": False}],
        },
        data_agreement_widget={
            "visible_columns": ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "start_date", "expiry_date", "business_purpose", "approved_usage", "_committed_by"],
            "custom_fields": [{"key": "expected_output", "label": "Expected output", "type": "select", "options": ["Dashboard", "Report"]}],
        },
    )
    return SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"metadata": store}}), data_agreement_config=intake)


def _steward(**overrides):
    return {"steward_id": "steward-001", "steward_name": "Configured Steward", "steward_role": "Data Steward", "contact": "steward@example.com", "effective_from": "2026-01-01", "effective_to": "", "is_active": True, **overrides}


def _agreement(**overrides):
    return {"agreement_id": "DA-001", "contract_version": "1.0.0", "agreement_name": "Orders Agreement", "domain": "Operations", "steward_id": "steward-001", "start_date": "2026-01-01", "expiry_date": "2026-12-31", "business_purpose": "Governed reporting", "approved_usage": "Approved reporting only", **overrides}


def test_schemas_include_lightweight_fields_and_runtime_audit_columns():
    audit = get_standard_runtime_audit_columns()
    assert get_data_steward_schema() == ["steward_id", "steward_name", "steward_role", "contact", "effective_from", "effective_to", "is_active", "custom_fields_json", *audit]
    assert get_data_agreement_schema() == ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "start_date", "expiry_date", "business_purpose", "approved_usage", "custom_fields_json", *audit]
    assert "department" not in get_data_steward_schema()
    assert "faculty" not in get_data_steward_schema()
    assert "expected_output" not in get_data_agreement_schema()


def test_widget_visible_fields_always_hide_backend_audit_columns():
    config = _config()
    assert "_activity_id" not in get_widget_visible_fields(config, "data_steward_widget")
    assert "_committed_by" not in get_widget_visible_fields(config, "data_agreement_widget")


def test_custom_text_and_select_fields_render_and_round_trip_json(monkeypatch):
    class Widget:
        def __init__(self, value=None, options=(), **kwargs):
            self.value = value
            self.options = options
    widgets = ModuleType("ipywidgets")
    for name in ("Text", "Textarea", "Dropdown", "SelectMultiple", "DatePicker", "Checkbox"):
        setattr(widgets, name, Widget)
    monkeypatch.setitem(sys.modules, "ipywidgets", widgets)
    config = _config().data_agreement_config
    steward_widgets = render_custom_fields(config.data_steward_widget, values={"group": "Shared Services"})
    agreement_widgets = render_custom_fields(config.data_agreement_widget, values={"expected_output": "Report"})
    assert steward_widgets["group"].value == "Shared Services"
    assert list(agreement_widgets["expected_output"].options) == ["Dashboard", "Report"]
    encoded = serialize_custom_fields({"expected_output": "Dashboard", "review_date": date(2026, 6, 2)})
    assert deserialize_custom_fields(encoded) == {"expected_output": "Dashboard", "review_date": "2026-06-02"}


def test_ensure_metadata_tables_is_idempotent(monkeypatch):
    reads = []
    tables = {DATA_STEWARD_TABLE: get_data_steward_schema(), DATA_AGREEMENT_TABLE: get_data_agreement_schema()}
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda config, env, target, table, **kwargs: reads.append((env, target, table)) or [dict.fromkeys(tables[table], "")])
    class Spark:
        def createDataFrame(self, rows): raise AssertionError("existing tables must not be recreated")
    first = ensure_metadata_tables(_config(), "dev", spark=Spark())
    second = ensure_metadata_tables(_config(), "dev", spark=Spark())
    assert first == second == {"status": "ready", "tables": [DATA_STEWARD_TABLE, DATA_AGREEMENT_TABLE], "created_tables": []}
    assert reads == [("dev", "metadata", DATA_STEWARD_TABLE), ("dev", "metadata", DATA_AGREEMENT_TABLE)] * 2


def test_list_data_stewards_returns_only_latest_active_rows(monkeypatch):
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [
        _steward(is_active=True, _committed_at="2026-01-01T00:00:00+00:00"),
        _steward(is_active=False, _committed_at="2026-02-01T00:00:00+00:00"),
        _steward(steward_id="steward-002", _committed_at="2026-02-01T00:00:00+00:00"),
    ])
    assert [row["steward_id"] for row in list_data_stewards(_config(), "dev")] == ["steward-002"]


def test_create_and_update_steward_append_audited_rows(monkeypatch):
    writes = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs))
    kwargs = {"spark": object(), "config": _config(), "env_name": "dev", "values": _steward(), "custom_fields": {"group": "Shared Services"}, "committed_by": "user@example.com", "committed_at": "2026-06-02T00:00:00+00:00"}
    created = create_or_update_data_steward(**kwargs)
    updated = create_or_update_data_steward(**{**kwargs, "values": _steward(steward_name="Updated Steward")})
    assert len(writes) == 2
    assert created["_committed_by"] == updated["_committed_by"] == "user@example.com"
    assert deserialize_custom_fields(updated["custom_fields_json"]) == {"group": "Shared Services"}


def test_create_and_update_agreement_append_versions_and_require_active_steward(monkeypatch):
    writes = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs))
    monkeypatch.setattr(data_agreement, "list_data_stewards", lambda *args, **kwargs: [_steward()])
    kwargs = {"spark": object(), "config": _config(), "env_name": "dev", "values": _agreement(), "custom_fields": {"expected_output": "Dashboard"}, "committed_by": "user@example.com", "committed_at": "2026-06-02T00:00:00+00:00"}
    created = create_or_update_data_agreement(**kwargs)
    updated = create_or_update_data_agreement(**{**kwargs, "selected_agreement": created})
    assert len(writes) == 2
    assert updated["agreement_id"] == created["agreement_id"] == "DA-001"
    assert updated["contract_version"] == "1.1.0"
    assert updated["_committed_by"] == "user@example.com"
    assert deserialize_custom_fields(updated["custom_fields_json"]) == {"expected_output": "Dashboard"}


def test_metadata_table_documentation_explains_json_extension_and_hidden_audit_fields():
    docs = Path("docs/how-fabricops-works/metadata-tables.md").read_text(encoding="utf-8")
    assert "## Lightweight `01_da` intake" in docs
    assert "stored in backend tables but hidden from normal widget users" in docs
    assert "`custom_fields_json`" in docs
    assert "Do not add a physical column for each local intake concept" in docs
