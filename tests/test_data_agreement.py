from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

import pytest

import fabricops_kit.data_agreement as data_agreement
from fabricops_kit.config import DataAgreementConfig
from fabricops_kit.data_agreement import DATA_AGREEMENT_EVIDENCE_TABLE, DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE
from fabricops_kit.fabric_input_output import FabricStore


def _config(*, metadata_tables=None, steward_role_options=None):
    store = FabricStore(env="dev", workspace_id="workspace", item_id="metadata-item", name="lh_metadata_dev", kind="lakehouse")
    intake = DataAgreementConfig(
        metadata_tables=metadata_tables or {"data_steward": DATA_STEWARD_TABLE, "data_agreement": DATA_AGREEMENT_TABLE, "data_agreement_evidence": DATA_AGREEMENT_EVIDENCE_TABLE},
        data_steward_widget={
            "visible_columns": ["steward_id", "steward_name", "steward_role", "contact", "effective_from", "effective_to", "is_active", "custom_fields_json", "_activity_id"],
            "custom_fields": [{"key": "group", "label": "Group", "type": "text", "required": False}],
        },
        data_agreement_widget={
            "visible_columns": ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research", "custom_fields_json", "_committed_by"],
            "custom_fields": [{"key": "consumer_group", "label": "Consumer group", "type": "select", "options": ["ODI", "Faculty"]}],
        },
        steward_role_options=steward_role_options or ["Data Owner", "Data Steward", "Governance Reviewer"],
    )
    return SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"metadata": store}}), data_agreement_config=intake)


def _steward(**overrides):
    return {"steward_id": "steward-001", "steward_name": "Configured Steward", "steward_role": "Data Steward", "contact": "steward@example.com", "effective_from": "2026-01-01", "effective_to": "", "is_active": True, **overrides}


def _agreement(**overrides):
    return {
        "agreement_name": "Orders Agreement",
        "domain": "Operations",
        "steward_id": "steward-001",
        "recipient": "Internal analytics team",
        "start_date": "2026-01-01",
        "expiry_date": "2026-12-31",
        "business_purpose": "Governed reporting",
        "approved_usage_internal": "Approved internal reporting only",
        "approved_usage_external": "",
        "approved_usage_research": "",
        **overrides,
    }


def _install_widget_stubs(monkeypatch):
    class Widget:
        def __init__(self, value=None, options=(), **kwargs):
            self.value = value
            self.options = options
            self.description = kwargs.get("description", "")
            self.style = kwargs.get("style", {})
            self.layout = kwargs.get("layout")
            self.accept = kwargs.get("accept", "")
            self.multiple = kwargs.get("multiple", False)
            self.children = kwargs.get("children", ())
            self.disabled = kwargs.get("disabled", False)
            self.titles = {}
            self.callbacks = []
        def observe(self, callback, names=None): self.callbacks.append(callback)
        def on_click(self, callback): self.callbacks.append(callback)
        def set_title(self, index, title): self.titles[index] = title
    class Output(Widget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.clear_calls = []
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def clear_output(self, **kwargs): self.clear_calls.append(kwargs)
    class Layout:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)
    widgets = ModuleType("ipywidgets")
    for name in ("Text", "Textarea", "Dropdown", "SelectMultiple", "DatePicker", "Checkbox", "Button", "HTML", "FileUpload", "Tab"):
        setattr(widgets, name, Widget)
    widgets.Output = Output
    widgets.Layout = Layout
    widgets.VBox = lambda values: Widget(children=tuple(values))
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
    assert data_agreement._get_data_agreement_schema() == ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research", "custom_fields_json", *audit]
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
    assert "recipient" in data_agreement.DATA_AGREEMENT_VISIBLE_FIELDS
    assert "approved_usage_internal" in data_agreement.DATA_AGREEMENT_VISIBLE_FIELDS
    assert "approved_usage_external" in data_agreement.DATA_AGREEMENT_VISIBLE_FIELDS
    assert "approved_usage_research" in data_agreement.DATA_AGREEMENT_VISIBLE_FIELDS
    assert "approved_usage" not in data_agreement.DATA_AGREEMENT_VISIBLE_FIELDS
    assert "steward_id" not in steward_fields
    assert "is_active" not in steward_fields


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
    schemas = {
        DATA_STEWARD_TABLE: data_agreement._get_data_steward_schema(),
        DATA_AGREEMENT_TABLE: data_agreement._get_data_agreement_schema(),
        DATA_AGREEMENT_EVIDENCE_TABLE: data_agreement._get_data_agreement_evidence_schema(),
    }
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
    assert first["created_tables"] == [DATA_STEWARD_TABLE, DATA_AGREEMENT_TABLE, DATA_AGREEMENT_EVIDENCE_TABLE]
    assert second["created_tables"] == []
    assert writes == [
        ("dev", "metadata", DATA_STEWARD_TABLE, {"mode": "ignore", "overwrite_schema": True}),
        ("dev", "metadata", DATA_AGREEMENT_TABLE, {"mode": "ignore", "overwrite_schema": True}),
        ("dev", "metadata", DATA_AGREEMENT_EVIDENCE_TABLE, {"mode": "ignore", "overwrite_schema": True}),
    ]
    assert source_rows == [
        [{field: "" for field in schemas[DATA_STEWARD_TABLE]}],
        [{field: "" for field in schemas[DATA_AGREEMENT_TABLE]}],
        [{field: "" for field in schemas[DATA_AGREEMENT_EVIDENCE_TABLE]}],
    ]
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


def test_widget_entrypoints_and_app_render_tabbed_widgets(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: [])
    assert data_agreement.render_data_steward_widget(_config(), "dev", spark="spark")["container"] is not None
    assert data_agreement.render_data_agreement_widget(_config(), "dev", spark="spark")["container"] is not None
    app = data_agreement.render_agreement_intake_app(spark="spark", config=_config(), env="dev")
    assert set(app) == {"data_steward", "data_agreement", "agreement_evidence", "tab"}
    assert app["data_steward"]["container"] is not None
    assert app["data_agreement"]["container"] is not None
    assert app["agreement_evidence"]["container"] is not None
    assert app["tab"].titles == {0: "Data Steward", 1: "Data Agreement", 2: "Agreement Evidence"}
    assert len(app["tab"].children) == 3


def test_metadata_table_documentation_explains_generated_ids_json_extension_and_hidden_audit_fields():
    docs = Path("docs/how-fabricops-works/metadata-tables.md").read_text(encoding="utf-8")
    assert "## Lightweight `01_da` intake" in docs
    assert "stored in backend tables but hidden from normal widget users" in docs
    assert "`custom_fields_json`" in docs
    assert "Do not add a physical column for each local intake concept" in docs
    assert "steward_id | STEW-8d889875dd | Backend-generated" in docs
    assert "is_active | `true` | Backend-derived" in docs
    assert "DataAgreementConfig.steward_role_options" in docs
    assert "add organization-specific role extensions to that config list" in docs
    assert "METADATA_DATA_AGREEMENT_EVIDENCE" in docs
    assert "metadata lakehouse `Files` area" in docs
    assert "does not store uploaded binary content" in docs
    assert "Evidence upload is optional" in docs


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


def test_steward_save_normalizes_false_boolean_and_string_to_inactive(monkeypatch):
    rows = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: rows.append(kwargs["row"]))
    for is_active in (False, "False"):
        row = data_agreement._create_or_update_data_steward(
            spark=object(), config=_config(), env_name="dev", values=_steward(is_active=is_active)
        )
        assert row["is_active"] == "false"
        assert data_agreement._active_steward(row) is False
    assert [row["is_active"] for row in rows] == ["false", "false"]


def test_active_steward_filter_excludes_saved_inactive_row(monkeypatch):
    writes = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    inactive = data_agreement._create_or_update_data_steward(
        spark=object(), config=_config(), env_name="dev", values=_steward(steward_id="inactive", is_active="False")
    )
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [inactive, _steward(steward_id="active", is_active=True)])
    assert [row["steward_id"] for row in data_agreement._list_data_stewards(_config(), "dev")] == ["active"]


def test_widget_save_path_generates_steward_id_and_derives_active_status(monkeypatch):
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
    assert data_agreement._active_steward(writes[0]) is True


def test_multiselect_custom_field_round_trips_json_to_widget_tuple(monkeypatch):
    _install_widget_stubs(monkeypatch)
    custom_config = {"custom_fields": [{"key": "groups", "label": "Groups", "type": "multiselect", "options": ["ODI", "Faculty"]}]}
    stored = data_agreement._deserialize_custom_fields(data_agreement._serialize_custom_fields({"groups": ["ODI", "Faculty"]}))
    widgets = data_agreement._render_custom_fields(custom_config)
    data_agreement._set_widget_value(widgets["groups"], stored["groups"])
    assert widgets["groups"].value == ("ODI", "Faculty")


def test_metadata_setup_and_steward_writes_use_string_is_active_schema(monkeypatch):
    setup_rows, write_rows = [], []
    schemas = {
        DATA_STEWARD_TABLE: data_agreement._get_data_steward_schema(),
        DATA_AGREEMENT_TABLE: data_agreement._get_data_agreement_schema(),
        DATA_AGREEMENT_EVIDENCE_TABLE: data_agreement._get_data_agreement_evidence_schema(),
    }
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


def test_standard_dropdown_tuple_options_default_to_option_value(monkeypatch):
    _install_widget_stubs(monkeypatch)
    widget = data_agreement._standard_widget("steward_id", options=[("Configured Steward", "steward-001")])
    assert widget.value == "steward-001"
    assert widget.value != ("Configured Steward", "steward-001")


def test_standard_dropdown_preserves_existing_tuple_option_value(monkeypatch):
    _install_widget_stubs(monkeypatch)
    widget = data_agreement._standard_widget(
        "steward_id",
        value="steward-002",
        options=[("First", "steward-001"), ("Second", "steward-002")],
    )
    assert widget.value == "steward-002"


def test_maintenance_dropdowns_use_ids_and_internal_row_lookup(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    assert widget["existing_record"].options[1] == ("Configured Steward | Data Steward | steward@example.com", "steward-001")
    assert widget["existing_records_by_id"]["steward-001"]["steward_name"] == "Configured Steward"
    assert not isinstance(widget["existing_record"].options[1][1], dict)


def test_agreement_steward_dropdown_returns_actual_steward_id(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    assert widget["fields"]["steward_id"].options == [("Configured Steward | Data Steward | steward@example.com", "steward-001")]
    assert widget["fields"]["steward_id"].value == "steward-001"


def test_save_output_clears_old_messages_before_save(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_create_or_update_data_steward", lambda **kwargs: _steward(**kwargs["values"]))
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    values = _steward()
    for field, control in widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    widget["save_button"].callbacks[0](None)
    assert widget["output"].clear_calls == [{"wait": True}]


def test_steward_save_refreshes_agreement_steward_options(monkeypatch):
    _install_widget_stubs(monkeypatch)
    steward_rows = []
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: list(steward_rows))
    def save_steward(**kwargs):
        row = _steward(**kwargs["values"])
        steward_rows.append(row)
        return row
    monkeypatch.setattr(data_agreement, "_create_or_update_data_steward", save_steward)
    app = data_agreement.render_agreement_intake_app(spark=object(), config=_config(), env="dev")
    steward_widget = app["data_steward"]
    agreement_widget = app["data_agreement"]
    assert agreement_widget["fields"]["steward_id"].options == []
    values = _steward()
    for field, control in steward_widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    steward_widget["save_button"].callbacks[0](None)
    assert agreement_widget["fields"]["steward_id"].options == [("Configured Steward | Data Steward | steward@example.com", "steward-001")]
    assert agreement_widget["fields"]["steward_id"].value == "steward-001"


def test_field_labels_and_layout_are_not_raw_technical_names(monkeypatch):
    _install_widget_stubs(monkeypatch)
    purpose = data_agreement._standard_widget("business_purpose")
    steward_name = data_agreement._standard_widget("steward_name")
    assert purpose.description == "Business Purpose"
    assert steward_name.description == "Steward Name"
    assert purpose.style == {"description_width": "150px"}
    assert purpose.layout.width == "600px"
    assert purpose.layout.height == "80px"
    assert steward_name.layout.width == "600px"


def test_build_steward_dropdown_options_uses_friendly_label_and_id_value():
    options = data_agreement._build_steward_dropdown_options([
        _steward(steward_id="s1", steward_name="Alice", steward_role="Owner", contact="alice@example.com"),
        _steward(steward_id="s2", steward_name="", steward_role="", contact=""),
    ])
    assert options == [("Alice | Owner | alice@example.com", "s1"), ("Unnamed steward (s2)", "s2")]
    assert not isinstance(options[0][1], dict)


def test_selecting_existing_steward_populates_standard_and_custom_fields(monkeypatch):
    _install_widget_stubs(monkeypatch)
    row = _steward(custom_fields_json=data_agreement._serialize_custom_fields({"group": "Shared Services"}))
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [row])
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    widget["existing_record"].callbacks[0]({"new": "steward-001"})
    assert widget["fields"]["steward_name"].value == "Configured Steward"
    assert widget["fields"]["steward_role"].value == "Data Steward"
    assert widget["fields"]["contact"].value == "steward@example.com"
    assert widget["fields"]["effective_from"].value == date(2026, 1, 1)
    assert widget["custom_fields"]["group"].value == "Shared Services"


def test_saving_existing_steward_reuses_selected_steward_id(monkeypatch):
    _install_widget_stubs(monkeypatch)
    writes = []
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    widget["existing_record"].value = "steward-001"
    values = _steward(steward_name="Updated Steward")
    for field, control in widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    widget["save_button"].callbacks[0](None)
    assert writes[0]["steward_id"] == "steward-001"
    assert writes[0]["steward_name"] == "Updated Steward"


def test_agreement_dropdown_options_show_latest_version_and_id_value():
    rows = [
        {**_agreement(), "agreement_id": "DA-001", "contract_version": "1.0.0"},
        {**_agreement(approved_usage_internal="Updated"), "agreement_id": "DA-001", "contract_version": "1.1.0"},
    ]
    options = data_agreement._agreement_dropdown_options(rows)
    assert options == [("Orders Agreement (DA-001 / v1.1.0)", "DA-001")]
    assert not isinstance(options[0][1], dict)


def test_selecting_existing_agreement_populates_standard_and_custom_fields(monkeypatch):
    _install_widget_stubs(monkeypatch)
    row = {**_agreement(), "agreement_id": "DA-001", "contract_version": "1.1.0", "custom_fields_json": data_agreement._serialize_custom_fields({"consumer_group": "Faculty"})}
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [row])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    widget["existing_record"].callbacks[0]({"new": "DA-001"})
    assert widget["fields"]["agreement_name"].value == "Orders Agreement"
    assert widget["fields"]["domain"].value == "Operations"
    assert widget["fields"]["steward_id"].value == "steward-001"
    assert widget["fields"]["start_date"].value == date(2026, 1, 1)
    assert widget["fields"]["expiry_date"].value == date(2026, 12, 31)
    assert widget["fields"]["business_purpose"].value == "Governed reporting"
    assert widget["fields"]["recipient"].value == "Internal analytics team"
    assert widget["fields"]["approved_usage_internal"].value == "Approved internal reporting only"
    assert widget["fields"]["approved_usage_external"].value == ""
    assert widget["fields"]["approved_usage_research"].value == ""
    assert widget["custom_fields"]["consumer_group"].value == "Faculty"
    assert "Next version on save: 1.2.0" in widget["identity_context"].value


def test_agreement_update_uses_latest_existing_version_for_next_version(monkeypatch):
    writes = []
    rows = [
        {**_agreement(), "agreement_id": "DA-001", "contract_version": "1.0.0", "custom_fields_json": "{}"},
        {**_agreement(approved_usage_internal="Changed once"), "agreement_id": "DA-001", "contract_version": "1.1.0", "custom_fields_json": "{}"},
    ]
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: rows)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    row = data_agreement._create_or_update_data_agreement(
        spark=object(), config=_config(), env_name="dev", values=_agreement(approved_usage_internal="Changed twice"), selected_agreement=rows[0]
    )
    assert row["agreement_id"] == "DA-001"
    assert row["contract_version"] == "1.2.0"
    assert writes[0]["contract_version"] == "1.2.0"


def test_duplicate_agreement_version_is_blocked(monkeypatch):
    existing = [{**_agreement(), "agreement_id": "DA-GENERATED", "contract_version": "1.0.0", "custom_fields_json": "{}"}]
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: existing)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_generate_agreement_id", lambda: "DA-GENERATED")
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: pytest.fail("duplicate version should not append"))
    with pytest.raises(ValueError, match="Agreement DA-GENERATED version 1.0.0 already exists"):
        data_agreement._create_or_update_data_agreement(spark=object(), config=_config(), env_name="dev", values=_agreement())


def test_repeated_agreement_update_with_no_business_changes_does_not_append(monkeypatch):
    existing = [{**_agreement(), "agreement_id": "DA-001", "contract_version": "1.1.0", "custom_fields_json": data_agreement._serialize_custom_fields({"consumer_group": "ODI"})}]
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: existing)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: pytest.fail("unchanged update should not append"))
    row = data_agreement._create_or_update_data_agreement(
        spark=object(), config=_config(), env_name="dev", values=_agreement(), selected_agreement=existing[0], custom_fields={"consumer_group": "ODI"}
    )
    assert row["_fabricops_no_change"] is True
    assert row["_fabricops_message"] == "No changes detected. Nothing was appended."


def test_save_button_reenabled_after_success_and_failure(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_create_or_update_data_steward", lambda **kwargs: _steward(**kwargs["values"]))
    success_widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    values = _steward()
    for field, control in success_widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    success_widget["save_button"].callbacks[0](None)
    assert success_widget["save_button"].disabled is False

    def fail_save(**kwargs):
        raise ValueError("forced failure")
    monkeypatch.setattr(data_agreement, "_create_or_update_data_steward", fail_save)
    failure_widget = data_agreement.render_data_steward_widget(_config(), "dev", spark=object())
    for field, control in failure_widget["fields"].items():
        control.value = date.fromisoformat(values[field]) if field == "effective_from" else values[field]
    failure_widget["save_button"].callbacks[0](None)
    assert failure_widget["save_button"].disabled is False


def test_steward_role_renders_as_dropdown_from_config(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [])
    widget = data_agreement.render_data_steward_widget(
        _config(steward_role_options=["Data Owner", "Business Approver"]), "dev", spark=object()
    )
    role = widget["fields"]["steward_role"]
    assert role.description == "Steward Role"
    assert role.options == [("Data Owner", "Data Owner"), ("Business Approver", "Business Approver")]
    assert role.value == "Data Owner"


def test_selecting_existing_legacy_steward_role_preserves_dropdown_option(monkeypatch):
    _install_widget_stubs(monkeypatch)
    legacy = _steward(steward_role="Legacy Approver")
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [legacy])
    widget = data_agreement.render_data_steward_widget(
        _config(steward_role_options=["Data Owner", "Data Steward"]), "dev", spark=object()
    )
    widget["existing_record"].callbacks[0]({"new": "steward-001"})
    assert ("Legacy Approver", "Legacy Approver") in widget["fields"]["steward_role"].options
    assert widget["fields"]["steward_role"].value == "Legacy Approver"


def test_new_steward_save_rejects_blank_or_invalid_role(monkeypatch):
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: pytest.fail("invalid steward role should not append"))
    with pytest.raises(ValueError, match="steward_role"):
        data_agreement._create_or_update_data_steward(
            spark=object(), config=_config(steward_role_options=["Data Owner"]), env_name="dev", values=_steward(steward_role="")
        )
    with pytest.raises(ValueError, match="configured steward role options"):
        data_agreement._create_or_update_data_steward(
            spark=object(), config=_config(steward_role_options=["Data Owner"]), env_name="dev", values=_steward(steward_role="Legacy Approver")
        )


def test_existing_legacy_steward_role_can_be_saved_when_loaded_from_selected_row(monkeypatch):
    writes = []
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    row = data_agreement._create_or_update_data_steward(
        spark=object(),
        config=_config(steward_role_options=["Data Owner"]),
        env_name="dev",
        values={**_steward(steward_role="Legacy Approver"), "_legacy_steward_role": "Legacy Approver"},
    )
    assert row["steward_role"] == "Legacy Approver"
    assert writes[0]["steward_role"] == "Legacy Approver"


def test_agreement_widget_renders_recipient_text_and_split_usage_textareas(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    widget = data_agreement.render_data_agreement_widget(_config(), "dev", spark=object())
    assert widget["fields"]["recipient"].description == "Recipient / Consumer"
    assert widget["fields"]["recipient"].options == ()
    for field, label in {
        "approved_usage_internal": "Approved Usage - Internal",
        "approved_usage_external": "Approved Usage - External",
        "approved_usage_research": "Approved Usage - Research",
    }.items():
        assert widget["fields"][field].description == label
        assert widget["fields"][field].layout.height == "80px"


def test_agreement_save_requires_recipient_and_at_least_one_usage(monkeypatch):
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: pytest.fail("invalid agreement should not append"))
    with pytest.raises(ValueError, match="recipient"):
        data_agreement._create_or_update_data_agreement(spark=object(), config=_config(), env_name="dev", values=_agreement(recipient=""))
    with pytest.raises(ValueError, match="At least one approved usage field is required: internal, external, or research"):
        data_agreement._create_or_update_data_agreement(
            spark=object(),
            config=_config(),
            env_name="dev",
            values=_agreement(approved_usage_internal="", approved_usage_external="", approved_usage_research=""),
        )


@pytest.mark.parametrize("usage_field", ["approved_usage_internal", "approved_usage_external", "approved_usage_research"])
def test_agreement_save_succeeds_with_any_one_split_usage_field(monkeypatch, usage_field):
    writes = []
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: [])
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    values = _agreement(approved_usage_internal="", approved_usage_external="", approved_usage_research="")
    values[usage_field] = "Approved for this purpose"
    row = data_agreement._create_or_update_data_agreement(spark=object(), config=_config(), env_name="dev", values=values)
    assert row["recipient"] == "Internal analytics team"
    assert row[usage_field] == "Approved for this purpose"
    assert writes[0][usage_field] == "Approved for this purpose"
    assert "approved_usage" not in writes[0]


def test_no_change_detection_includes_recipient_and_split_usage(monkeypatch):
    existing = [{**_agreement(), "agreement_id": "DA-001", "contract_version": "1.1.0", "custom_fields_json": "{}"}]
    writes = []
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: existing)
    monkeypatch.setattr(data_agreement, "_list_data_stewards", lambda *args, **kwargs: [_steward()])
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs["row"]))
    unchanged = data_agreement._create_or_update_data_agreement(
        spark=object(), config=_config(), env_name="dev", values=_agreement(), selected_agreement=existing[0]
    )
    changed = data_agreement._create_or_update_data_agreement(
        spark=object(), config=_config(), env_name="dev", values=_agreement(recipient="Research team"), selected_agreement=existing[0]
    )
    assert unchanged["_fabricops_no_change"] is True
    assert changed["recipient"] == "Research team"
    assert writes[0]["contract_version"] == "1.2.0"


def test_evidence_table_schema_includes_expected_columns():
    assert data_agreement._get_data_agreement_evidence_schema() == [
        "agreement_id",
        "contract_version",
        "evidence_type",
        "file_name",
        "file_path",
        "mime_type",
        "file_size",
        "uploaded_at",
        "uploaded_by",
        *data_agreement._get_standard_runtime_audit_columns(),
    ]


def test_evidence_file_upload_accepts_expected_file_types(monkeypatch):
    _install_widget_stubs(monkeypatch)
    row = {**_agreement(), "agreement_id": "DA-001", "contract_version": "1.0.0"}
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: [row])
    widget = data_agreement._render_agreement_evidence_widget(spark=object(), config=_config(), env_name="dev")
    assert widget["file_upload"].accept == ".pdf,.doc,.docx,.png,.jpg,.jpeg"
    assert widget["file_upload"].multiple is True
    assert widget["evidence_type"].options == [(item, item) for item in data_agreement.AGREEMENT_EVIDENCE_TYPES]


def test_evidence_widget_tells_user_to_save_agreement_first(monkeypatch):
    _install_widget_stubs(monkeypatch)
    monkeypatch.setattr(data_agreement, "_list_all_data_agreement_rows", lambda *args, **kwargs: [])
    widget = data_agreement._render_agreement_evidence_widget(spark=object(), config=_config(), env_name="dev")
    assert "Save a Data Agreement first" in widget["message"].value
    assert widget["file_upload"].disabled is True
    assert widget["save_button"].disabled is True


def test_evidence_records_save_file_metadata_not_binary_content(monkeypatch):
    writes, files = [], []
    monkeypatch.setattr(data_agreement, "build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in data_agreement._get_standard_runtime_audit_columns()})
    monkeypatch.setattr(data_agreement, "_write_evidence_file", lambda **kwargs: files.append(kwargs))
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs))
    rows = data_agreement._save_agreement_evidence_records(
        spark=object(),
        config=_config(),
        env_name="dev",
        agreement_id="DA-001",
        contract_version="1.0.0",
        evidence_type="Signed Agreement",
        uploaded_files=({"name": "signed.pdf", "type": "application/pdf", "size": 7, "content": b"PDFDATA"},),
    )
    assert len(rows) == 1
    assert files[0]["relative_path"].startswith("Files/fabricops/agreement_evidence/DA-001/1.0.0/signed__")
    assert files[0]["relative_path"].endswith(".pdf")
    assert files[0]["content"] == b"PDFDATA"
    assert writes[0]["table"] == DATA_AGREEMENT_EVIDENCE_TABLE
    assert writes[0]["row"]["file_name"] == "signed.pdf"
    assert writes[0]["row"]["file_path"] == files[0]["relative_path"]
    assert writes[0]["row"]["mime_type"] == "application/pdf"
    assert writes[0]["row"]["file_size"] == "7"
    assert "content" not in writes[0]["row"]


@pytest.mark.parametrize(("agreement_id", "contract_version", "message"), [
    ("", "1.0.0", "agreement_id is required"),
    ("DA-001", "", "contract_version is required"),
])
def test_evidence_save_requires_agreement_id_and_contract_version(monkeypatch, agreement_id, contract_version, message):
    monkeypatch.setattr(data_agreement, "_write_evidence_file", lambda **kwargs: pytest.fail("file write should not run"))
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: pytest.fail("metadata write should not run"))
    with pytest.raises(ValueError, match=message):
        data_agreement._save_agreement_evidence_records(
            spark=object(),
            config=_config(),
            env_name="dev",
            agreement_id=agreement_id,
            contract_version=contract_version,
            evidence_type="Other",
            uploaded_files=({"name": "evidence.pdf", "content": b"data"},),
        )


def test_evidence_save_supports_multiple_uploaded_files(monkeypatch):
    writes, files = [], []
    monkeypatch.setattr(data_agreement, "build_runtime_audit_fields", lambda **kwargs: {field: "" for field in data_agreement._get_standard_runtime_audit_columns()})
    monkeypatch.setattr(data_agreement, "_write_evidence_file", lambda **kwargs: files.append(kwargs))
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: writes.append(kwargs))
    rows = data_agreement._save_agreement_evidence_records(
        spark=object(),
        config=_config(),
        env_name="dev",
        agreement_id="DA-001",
        contract_version="1.0.0",
        evidence_type="Email Approval",
        uploaded_files={
            "first": {"name": "approval.msg.pdf", "type": "application/pdf", "content": b"one"},
            "second": {"name": "screen.png", "type": "image/png", "content": memoryview(b"two")},
        },
    )
    assert [row["file_name"] for row in rows] == ["approval.msg.pdf", "screen.png"]
    assert files[0]["relative_path"].startswith("Files/fabricops/agreement_evidence/DA-001/1.0.0/approval.msg__")
    assert files[0]["relative_path"].endswith(".pdf")
    assert files[1]["relative_path"].startswith("Files/fabricops/agreement_evidence/DA-001/1.0.0/screen__")
    assert files[1]["relative_path"].endswith(".png")
    assert len({file["relative_path"] for file in files}) == 2
    assert len(writes) == 2


def test_evidence_save_rejects_unsupported_file_extension_before_writing(monkeypatch):
    monkeypatch.setattr(data_agreement, "_write_evidence_file", lambda **kwargs: pytest.fail("unsupported file should not be written"))
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: pytest.fail("unsupported file should not append metadata"))
    with pytest.raises(ValueError, match=r"Unsupported evidence file type\. Allowed types: \.pdf, \.doc, \.docx, \.png, \.jpg, \.jpeg\."):
        data_agreement._save_agreement_evidence_records(
            spark=object(),
            config=_config(),
            env_name="dev",
            agreement_id="DA-001",
            contract_version="1.0.0",
            evidence_type="Other",
            uploaded_files=({"name": "script.exe", "content": b"data"},),
        )


def test_evidence_save_uses_unique_storage_names_for_duplicate_upload_names(monkeypatch):
    files = []
    monkeypatch.setattr(data_agreement, "build_runtime_audit_fields", lambda **kwargs: {field: "2026-06-01T10:30:00+00:00" if field == "_committed_at" else "" for field in data_agreement._get_standard_runtime_audit_columns()})
    monkeypatch.setattr(data_agreement, "_write_evidence_file", lambda **kwargs: files.append(kwargs))
    monkeypatch.setattr(data_agreement, "_write_row", lambda **kwargs: None)
    rows = data_agreement._save_agreement_evidence_records(
        spark=object(),
        config=_config(),
        env_name="dev",
        agreement_id="DA-001",
        contract_version="1.0.0",
        evidence_type="Signed Agreement",
        uploaded_files=(
            {"name": "approval.pdf", "content": b"first"},
            {"name": "approval.pdf", "content": b"second"},
        ),
    )
    assert [row["file_name"] for row in rows] == ["approval.pdf", "approval.pdf"]
    assert all("/approval__" in row["file_path"] and row["file_path"].endswith(".pdf") for row in rows)
    assert len({row["file_path"] for row in rows}) == 2
    assert [file["relative_path"] for file in files] == [row["file_path"] for row in rows]
