from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

import pytest

import fabricops_kit.data_agreement as data_agreement
from fabricops_kit.config import DataAgreementConfig
from fabricops_kit.data_agreement import DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE
from fabricops_kit.fabric_input_output import FabricStore


def _config(*, metadata_tables=None):
    store = FabricStore(env="dev", workspace_id="workspace", item_id="metadata-item", name="lh_metadata_dev", kind="lakehouse")
    intake = DataAgreementConfig(
        metadata_tables=metadata_tables or {"data_steward": DATA_STEWARD_TABLE, "data_agreement": DATA_AGREEMENT_TABLE},
        data_steward_widget={
            "visible_columns": ["steward_id", "steward_name", "steward_role", "contact", "effective_from", "effective_to", "is_active", "custom_fields_json", "_activity_id"],
            "custom_fields": [{"key": "group", "label": "Group", "type": "text", "required": False}],
        },
        data_agreement_widget={
            "visible_columns": ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "start_date", "expiry_date", "business_purpose", "approved_usage", "custom_fields_json", "_committed_by"],
            "custom_fields": [{"key": "consumer_group", "label": "Consumer group", "type": "select", "options": ["ODI", "Faculty"]}],
        },
    )
    return SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"metadata": store}}), data_agreement_config=intake)


def _steward(**overrides):
    return {"steward_id": "steward-001", "steward_name": "Configured Steward", "steward_role": "Data Steward", "contact": "steward@example.com", "effective_from": "2026-01-01", "effective_to": "", "is_active": True, **overrides}


def _agreement(**overrides):
    return {"agreement_name": "Orders Agreement", "domain": "Operations", "steward_id": "steward-001", "start_date": "2026-01-01", "expiry_date": "2026-12-31", "business_purpose": "Governed reporting", "approved_usage": "Approved reporting only", **overrides}


def _install_widget_stubs(monkeypatch):
    class Widget:
        def __init__(self, value=None, options=(), **kwargs):
            self.value = value
            self.options = options
            self.description = kwargs.get("description", "")
            self.style = kwargs.get("style", {})
            self.layout = kwargs.get("layout")
            self.callbacks = []
        def observe(self, callback, names=None): self.callbacks.append(callback)
        def on_click(self, callback): self.callbacks.append(callback)
    class Output(Widget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.clear_calls = []
        def clear_output(self, **kwargs): self.clear_calls.append(kwargs)
        def __enter__(self): return self
        def __exit__(self, *args): return False
    widgets = ModuleType("ipywidgets")
    for name in ("Text", "Textarea", "Dropdown", "SelectMultiple", "DatePicker", "Checkbox", "Button", "HTML"):
        setattr(widgets, name, Widget)
    widgets.Output = Output
    widgets.Layout = lambda **kwargs: SimpleNamespace(**kwargs)
    widgets.VBox = lambda values: values
    display = ModuleType("IPython.display")
    display.display = lambda *args, **kwargs: None
    ipython = ModuleType("IPython")
    ipython.display = display
    monkeypatch.setitem(sys.modules, "ipywidgets", widgets)
    monkeypatch.setitem(sys.modules, "IPython", ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", display)


def test_schemas_remain_lightweight_and_include_runtime_audit_columns():
    audit = data_agreement._get_standard_runtime_audit_columns()
    assert data_agreement._get_data_steward_schema() == ["steward_id", "steward_name", "steward_role", "contact", "effective_from", "effective_to", "is_active", "custom_fields_json", *audit]
    assert data_agreement._get_data_agreement_schema() == ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "start_date", "expiry_date", "business_purpose", "approved_usage", "custom_fields_json", *audit]
    for physical_column in ("department", "faculty", "expected_output", "restricted_usage", "source_system", "refresh_frequency", "renewal_required"):
        assert physical_column not in data_agreement._get_data_steward_schema()
        assert physical_column not in data_agreement._get_data_agreement_schema()


def test_widget_visible_fields_hide_audit_json_and_generated_agreement_ids():
    config = _config()
    steward_fields = data_agreement._get_widget_visible_fields(config, "data_steward_widget")
    agreement_fields = data_agreement._get_widget_visible_fields(config, "data_agreement_widget")
    assert "_activity_id" not in steward_fields
    assert "_committed_by" not in agreement_fields
    assert "custom_fields_json" not in steward_fields + agreement_fields
    assert "agreement_id" not in agreement_fields
    assert "contract_version" not in agreement_fields


def test_custom_text_and_select_fields_render_and_round_trip_json(monkeypatch):
    _install_widget_stubs(monkeypatch)
    config = _config().data_agreement_config
    steward_widgets = data_agreement._render_custom_fields(config.data_steward_widget, values={"group": "Shared Services"})
    agreement_widgets = data_agreement._render_custom_fields(config.data_agreement_widget, values={"consumer_group": "Faculty"})
    assert steward_widgets["group"].value == "Shared Services"
    assert list(agreement_widgets["consumer_group"].options) == ["ODI", "Faculty"]
    encoded = data_agreement._serialize_custom_fields({"consumer_group": "ODI", "review_date": date(2026, 6, 2)})
    assert data_agreement._deserialize_custom_fields(encoded) == {"consumer_group": "ODI", "review_date": "2026-06-02"}


def test_setup_tables_is_idempotent_and_does_not_seed_fake_stewards(monkeypatch):
    reads, writes, source_rows = [], [], []
    schemas = {DATA_STEWARD_TABLE: data_agreement._get_data_steward_schema(), DATA_AGREEMENT_TABLE: data_agreement._get_data_agreement_schema()}
    attempts = {table: 0 for table in schemas}
    class Frame:
        def limit(self, count):
            assert count == 0
            return self
    class Spark:
        def createDataFrame(self, rows):
            source_rows.append(rows)
            return Frame()
    def read_table(config, env, target, table, **kwargs):
        reads.append((env, target, table))
        attempts[table] += 1
        if attempts[table] == 1:
            raise RuntimeError("missing")
        return [dict.fromkeys(schemas[table], "")]
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", read_table)
    monkeypatch.setattr(data_agreement, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((env, target, table, kwargs)))
    first = data_agreement._ensure_metadata_tables(_config(), "dev", spark=Spark())
    second = data_agreement._ensure_metadata_tables(_config(), "dev", spark=Spark())
    assert first["created_tables"] == [DATA_STEWARD_TABLE, DATA_AGREEMENT_TABLE]
    assert second["created_tables"] == []
    assert writes == [("dev", "metadata", DATA_STEWARD_TABLE, {"mode": "ignore", "overwrite_schema": True}), ("dev", "metadata", DATA_AGREEMENT_TABLE, {"mode": "ignore", "overwrite_schema": True})]
    assert source_rows == [[{field: "" for field in schemas[DATA_STEWARD_TABLE]}], [{field: "" for field in schemas[DATA_AGREEMENT_TABLE]}]]
    assert all(not any(row.values()) for rows in source_rows for row in rows)


def test_active_steward_filter_excludes_inactive_future_and_expired_rows(monkeypatch):
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [
        _steward(steward_id="active"),
        _steward(steward_id="inactive", is_active=False),
        _steward(steward_id="future", effective_from="2099-01-01"),
        _steward(steward_id="expired", effective_to="2000-01-01"),
    ])
    assert [row["steward_id"] for row in data_agreement._list_data_stewards(_config(), "dev")] == ["active"]


def test_steward_create_update_use_runtime_audit_helper_and_configured_route(monkeypatch):
    calls, writes = [], []
    monkeypatch.setattr(data_agreement, "build_runtime_audit_fields", lambda **kwargs: calls.append(kwargs) or {field: f"audit:{field}" for field in data_agreement._get_standard_runtime_audit_columns()})
    class Spark:
        def createDataFrame(self, rows): return rows
    monkeypatch.setattr(data_agreement, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))
    config = _config(metadata_tables={"data_steward": "CUSTOM_STEWARD", "data_agreement": "CUSTOM_AGREEMENT"})
    row = data_agreement._create_or_update_data_steward(spark=Spark(), config=config, env_name="dev", values=_steward(), custom_fields={"group": "Shared Services"})
    assert len(calls) == 1
    assert all(row[field] == f"audit:{field}" for field in data_agreement._get_standard_runtime_audit_columns())
    assert writes[0][1:] == ("dev", "metadata", "CUSTOM_STEWARD", {"mode": "append"})


def test_agreement_create_update_generate_append_only_identity_and_audit(monkeypatch):
    calls, writes = [], []
    monkeypatch.setattr(data_agreement, "build_runtime_audit_fields", lambda **kwargs: calls.append(kwargs) or {field: f"audit:{field}" for field in data_agreement._get_standard_runtime_audit_columns()})
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs))
    monkeypatch.setattr(data_agreement, "_generate_agreement_id", lambda: "DA-GENERATED")
    config = _config(metadata_tables={"data_steward": "CUSTOM_STEWARD", "data_agreement": "CUSTOM_AGREEMENT"})
    created = data_agreement._create_or_update_data_agreement(spark=object(), config=config, env_name="dev", values=_agreement(), custom_fields={"consumer_group": "ODI"})
    updated = data_agreement._create_or_update_data_agreement(spark=object(), config=config, env_name="dev", values=_agreement(), selected_agreement=created, custom_fields={"consumer_group": "Faculty"})
    assert (created["agreement_id"], created["contract_version"]) == ("DA-GENERATED", "1.0.0")
    assert (updated["agreement_id"], updated["contract_version"]) == ("DA-GENERATED", "1.1.0")
    assert len(calls) == len(writes) == 2
    assert all(write["table"] == "CUSTOM_AGREEMENT" for write in writes)
    assert all(updated[field] == f"audit:{field}" for field in data_agreement._get_standard_runtime_audit_columns())
    assert data_agreement._deserialize_custom_fields(updated["custom_fields_json"]) == {"consumer_group": "Faculty"}


@pytest.mark.parametrize(("factory", "values", "message"), [
    (data_agreement._create_or_update_data_steward, _steward(steward_name=""), "steward_name"),
    (data_agreement._create_or_update_data_steward, _steward(effective_from="not-a-date"), "effective_from must be a valid ISO date"),
    (data_agreement._create_or_update_data_agreement, _agreement(domain=""), "domain"),
    (data_agreement._create_or_update_data_agreement, _agreement(expiry_date="not-a-date"), "expiry_date must be a valid ISO date"),
])
def test_create_update_validation_fails_clearly(monkeypatch, factory, values, message):
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: None)
    with pytest.raises(ValueError, match=message):
        factory(spark=object(), config=_config(), env_name="dev", values=values)


def test_widget_entrypoints_and_app_render_two_widgets(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_render_maintenance_widget", lambda **kwargs: kwargs["kind"])
    assert data_agreement.render_data_steward_widget(_config(), "dev", spark="spark") == "data_steward_widget"
    assert data_agreement.render_data_agreement_widget(_config(), "dev", spark="spark") == "data_agreement_widget"
    assert data_agreement.render_agreement_intake_app(spark="spark", config=_config(), env="dev") == {"data_steward": "data_steward_widget", "data_agreement": "data_agreement_widget"}


def test_standard_dropdown_tuple_options_use_scalar_value_and_preserve_existing_value(monkeypatch):
    _install_widget_stubs(monkeypatch)
    options = [("Configured Steward (steward-001)", "steward-001"), ("Second Steward (steward-002)", "steward-002")]
    assert data_agreement._standard_widget("steward_id", options=options).value == "steward-001"
    assert data_agreement._standard_widget("steward_id", value="steward-002", options=options).value == "steward-002"


def test_widget_record_selector_uses_ids_and_friendly_labels(monkeypatch):
    _install_widget_stubs(monkeypatch)
    steward = _steward()
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [steward])
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    assert list(widget["existing_record"].options) == [
        ("Create new steward", None),
        ("Configured Steward | Data Steward | steward@example.com", "steward-001"),
    ]
    assert widget["record_lookup"] == {"steward-001": steward}
    assert all(not isinstance(value, dict) for _, value in widget["existing_record"].options)
    widget["existing_record"].callbacks[0]({"new": "steward-001"})
    assert widget["fields"]["steward_name"].value == "Configured Steward"


def test_agreement_widget_uses_scalar_steward_id_friendly_labels_and_wide_layout(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    assert widget["fields"]["steward_id"].value == "steward-001"
    assert widget["fields"]["steward_id"].description == "Steward ID"
    assert widget["fields"]["business_purpose"].description == "Business Purpose"
    assert widget["fields"]["business_purpose"].style == {"description_width": "150px"}
    assert widget["fields"]["business_purpose"].layout.width == "600px"
    assert widget["fields"]["business_purpose"].layout.height == "80px"


def test_steward_save_clears_output_and_refreshes_agreement_steward_options(monkeypatch):
    _install_widget_stubs(monkeypatch)
    stewards = []
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: list(stewards))
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        data_agreement,
        "_create_or_update_data_steward",
        lambda **kwargs: stewards.append({"steward_id": "steward-001", **kwargs["values"]}) or stewards[-1],
    )
    app = data_agreement.render_agreement_intake_app(spark=object(), config=_config(), env="dev")
    steward_widget = app["data_steward"]
    agreement_widget = app["data_agreement"]
    values = _steward()
    for field, control in steward_widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    steward_widget["save_button"].callbacks[0](None)
    assert steward_widget["output"].clear_calls == [{"wait": True}]
    assert list(agreement_widget["fields"]["steward_id"].options) == [
        ("Configured Steward | Data Steward | steward@example.com", "steward-001")
    ]
    assert agreement_widget["fields"]["steward_id"].value == "steward-001"


def test_agreement_save_selects_saved_id_updates_context_and_clears_output(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    saved = {"agreement_id": "DA-001", "contract_version": "1.0.0", **_agreement()}
    monkeypatch.setattr(data_agreement, "_create_or_update_data_agreement", lambda **kwargs: saved)
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    values = _agreement()
    for field, control in widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field in {"start_date", "expiry_date"} else values[field]
    widget["save_button"].callbacks[0](None)
    assert widget["output"].clear_calls == [{"wait": True}]
    assert widget["existing_record"].value == "DA-001"
    assert widget["identity_context"].value == (
        "Agreement ID: DA-001 | Current version: 1.0.0 | Next version on save: 1.1.0"
    )
    assert list(widget["existing_record"].options) == [
        ("Create new agreement", None), ("Orders Agreement (DA-001 / v1.0.0)", "DA-001")
    ]


def test_metadata_table_documentation_explains_generated_ids_json_extension_and_hidden_audit_fields():
    docs = Path("docs/how-fabricops-works/metadata-tables.md").read_text(encoding="utf-8")
    assert "## Lightweight `01_da` intake" in docs
    assert "stored in backend tables but hidden from normal widget users" in docs
    assert "`custom_fields_json`" in docs
    assert "Do not add a physical column for each local intake concept" in docs


def test_agreement_widget_hides_generated_ids_and_shows_read_only_context(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    assert "agreement_id" not in widget["fields"]
    assert "contract_version" not in widget["fields"]
    assert widget["identity_context"].value == "Agreement ID and version are generated when saved."


def test_select_agreement_loads_configured_rows_for_downstream_notebooks(monkeypatch):
    _install_widget_stubs(monkeypatch)
    calls = []
    monkeypatch.setattr(data_agreement, "_load_agreements", lambda config, env, spark_session=None: calls.append((config, env, spark_session)) or [{"agreement_id": "DA-001", "contract_version": "1.0.0", "agreement_name": "Orders", "domain": "Operations"}])
    config = _config()
    dropdown = data_agreement.select_agreement(config, "dev", spark_session="spark")
    assert calls == [(config, "dev", "spark")]
    assert dropdown is not None
    assert data_agreement.get_selected_agreement() == {"agreement_id": "DA-001", "contract_version": "1.0.0", "agreement_name": "Orders", "domain": "Operations"}


@pytest.mark.parametrize(("value", "expected"), [
    (True, True), (False, False), ("true", True), ("false", False),
    (1, True), (0, False), ("yes", True), ("no", False),
    ("y", True), ("n", False), ("", False), (None, False),
])
def test_to_bool_normalizes_supported_notebook_values(value, expected):
    assert data_agreement._to_bool(value) is expected


def test_steward_save_derives_activity_from_effective_dates(monkeypatch):
    rows = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: rows.append(kwargs["row"]))
    active = data_agreement._create_or_update_data_steward(
        spark=object(), config=_config(), env_name="dev", values=_steward(is_active=False)
    )
    future = data_agreement._create_or_update_data_steward(
        spark=object(), config=_config(), env_name="dev", values=_steward(steward_id="future", effective_from="2099-01-01")
    )
    assert active["is_active"] == "true"
    assert future["is_active"] == "false"


def test_active_steward_filter_uses_dates_and_optional_backend_override(monkeypatch):
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [
        _steward(steward_id="active", is_active=""),
        _steward(steward_id="disabled", is_active=False),
        _steward(steward_id="future", effective_from="2099-01-01"),
        _steward(steward_id="expired", effective_to="2000-01-01"),
    ])
    assert [row["steward_id"] for row in data_agreement._list_data_stewards(_config(), "dev")] == ["active"]


def test_widget_save_hides_backend_steward_fields_and_generates_id(monkeypatch):
    _install_widget_stubs(monkeypatch)
    writes = []
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    assert "steward_id" not in widget["fields"]
    assert "is_active" not in widget["fields"]
    values = _steward()
    for field, control in widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    widget["save_button"].callbacks[0](None)
    assert writes[0]["steward_id"].startswith("STEW-")
    assert writes[0]["is_active"] == "true"


def test_multiselect_custom_field_round_trips_json_to_widget_tuple(monkeypatch):
    _install_widget_stubs(monkeypatch)
    custom_config = {"custom_fields": [{"key": "groups", "label": "Groups", "type": "multiselect", "options": ["ODI", "Faculty"]}]}
    stored = data_agreement._deserialize_custom_fields(data_agreement._serialize_custom_fields({"groups": ["ODI", "Faculty"]}))
    widgets = data_agreement._render_custom_fields(custom_config)
    data_agreement._set_widget_value(widgets["groups"], stored["groups"])
    assert widgets["groups"].value == ("ODI", "Faculty")


def test_metadata_setup_and_steward_writes_use_string_is_active_schema(monkeypatch):
    setup_rows, write_rows = [], []
    schemas = {DATA_STEWARD_TABLE: data_agreement._get_data_steward_schema(), DATA_AGREEMENT_TABLE: data_agreement._get_data_agreement_schema()}
    attempts = {table: 0 for table in schemas}
    class Frame:
        def limit(self, count): return self
    class Spark:
        def createDataFrame(self, rows):
            setup_rows.extend(rows)
            return Frame()
    def read_table(config, env, target, table, **kwargs):
        attempts[table] += 1
        if attempts[table] == 1:
            raise RuntimeError("missing")
        return [dict.fromkeys(schemas[table], "")]
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", read_table)
    monkeypatch.setattr(data_agreement, "write_lakehouse_table", lambda *args, **kwargs: None)
    data_agreement._ensure_metadata_tables(_config(), "dev", spark=Spark())
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: write_rows.append(kwargs["row"]))
    data_agreement._create_or_update_data_steward(spark=object(), config=_config(), env_name="dev", values=_steward(is_active=True))
    assert next(row for row in setup_rows if "is_active" in row)["is_active"] == ""
    assert write_rows[0]["is_active"] == "true"
    assert isinstance(write_rows[0]["is_active"], str)


def test_new_steward_save_generates_stable_id_and_existing_update_reuses_it(monkeypatch):
    writes = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    values = _steward()
    values.pop("steward_id")
    created = data_agreement._create_or_update_data_steward(
        spark=object(), config=_config(), env_name="dev", values=values
    )
    updated = data_agreement._create_or_update_data_steward(
        spark=object(),
        config=_config(),
        env_name="dev",
        values={**values, "steward_id": created["steward_id"], "contact": "new@example.com"},
    )
    assert created["steward_id"].startswith("STEW-")
    assert updated["steward_id"] == created["steward_id"]
    assert len(writes) == 2


def test_build_steward_dropdown_options_uses_friendly_scalar_values_and_fallback():
    assert data_agreement._build_steward_dropdown_options([_steward(), {"steward_id": "fallback"}]) == [
        ("Configured Steward | Data Steward | steward@example.com", "steward-001"),
        ("fallback", "fallback"),
    ]


def test_selecting_existing_steward_populates_standard_and_custom_fields(monkeypatch):
    _install_widget_stubs(monkeypatch)
    steward = _steward(custom_fields_json='{"group":"Shared Services"}')
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [steward])
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    widget["existing_record"].callbacks[0]({"new": "steward-001"})
    assert widget["fields"]["steward_name"].value == "Configured Steward"
    assert widget["fields"]["steward_role"].value == "Data Steward"
    assert widget["fields"]["contact"].value == "steward@example.com"
    assert widget["fields"]["effective_from"].value == date(2026, 1, 1)
    assert widget["fields"]["effective_to"].value is None
    assert widget["custom_fields"]["group"].value == "Shared Services"


def test_agreement_selector_lists_latest_version_and_populates_latest_fields(monkeypatch):
    _install_widget_stubs(monkeypatch)
    rows = [
        {
            "agreement_id": "DA-001", "contract_version": "1.0.0",
            "custom_fields_json": '{"consumer_group":"ODI"}', **_agreement(),
        },
        {
            "agreement_id": "DA-001", "contract_version": "1.1.0",
            "custom_fields_json": '{"consumer_group":"Faculty"}', **_agreement(business_purpose="Updated purpose"),
        },
    ]
    monkeypatch.setattr(
        data_agreement, "_list_data_agreements", lambda *args, **kwargs: data_agreement._latest_agreement_versions(rows)
    )
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    assert list(widget["existing_record"].options) == [
        ("Create new agreement", None), ("Orders Agreement (DA-001 / v1.1.0)", "DA-001")
    ]
    widget["existing_record"].callbacks[0]({"new": "DA-001"})
    assert widget["fields"]["business_purpose"].value == "Updated purpose"
    assert widget["custom_fields"]["consumer_group"].value == "Faculty"
    assert widget["identity_context"].value.endswith("Next version on save: 1.2.0")


def test_agreement_update_uses_latest_persisted_version_not_stale_selection(monkeypatch):
    writes = []
    existing = [
        {"agreement_id": "DA-001", "contract_version": "1.0.0", "custom_fields_json": "{}", **_agreement()},
        {
            "agreement_id": "DA-001", "contract_version": "1.1.0", "custom_fields_json": "{}",
            **_agreement(business_purpose="Prior change"),
        },
    ]
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: existing)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    saved = data_agreement._create_or_update_data_agreement(
        spark=object(), config=_config(), env_name="dev",
        values=_agreement(approved_usage="Expanded"), selected_agreement=existing[0],
    )
    assert saved["contract_version"] == "1.2.0"
    assert len(writes) == 1


def test_duplicate_agreement_version_is_blocked(monkeypatch):
    existing = [{"agreement_id": "DA-DUP", "contract_version": "1.0.0", "custom_fields_json": "{}", **_agreement()}]
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: existing)
    monkeypatch.setattr(data_agreement, "_generate_agreement_id", lambda: "DA-DUP")
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(
        data_agreement, "_write_row", lambda **kwargs: pytest.fail("duplicate row must not be appended")
    )
    with pytest.raises(ValueError, match=r"Agreement DA-DUP version 1\.0\.0 already exists"):
        data_agreement._create_or_update_data_agreement(
            spark=object(), config=_config(), env_name="dev", values=_agreement()
        )


def test_repeated_agreement_save_with_no_changes_does_not_append(monkeypatch):
    existing = {"agreement_id": "DA-001", "contract_version": "1.1.0", "custom_fields_json": "{}", **_agreement()}
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [existing])
    monkeypatch.setattr(
        data_agreement, "_write_row", lambda **kwargs: pytest.fail("unchanged row must not be appended")
    )
    saved = data_agreement._create_or_update_data_agreement(
        spark=object(), config=_config(), env_name="dev", values=_agreement(), selected_agreement=existing
    )
    assert saved["agreement_id"] == "DA-001"
    assert saved["contract_version"] == "1.1.0"
    assert saved["_was_appended"] is False


def test_widget_save_button_is_reenabled_after_success_and_failure(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: None)
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    values = _steward()
    for field, control in widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    widget["save_button"].callbacks[0](None)
    assert widget["save_button"].disabled is False
    widget["fields"]["contact"].value = ""
    with pytest.raises(ValueError, match="contact"):
        widget["save_button"].callbacks[0](None)
    assert widget["save_button"].disabled is False
