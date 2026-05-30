from datetime import datetime
from pathlib import Path
import sys
import types
from types import SimpleNamespace

import pytest

import fabricops_kit.data_agreement as data_agreement
from fabricops_kit.data_agreement import (
    DATA_AGREEMENT_FIELDS,
    DATA_AGREEMENT_TABLE,
    DATA_STEWARD_TABLE,
    DATA_STEWARD_FIELDS,
    agreement_dropdown_options,
    collect_agreement_metadata,
    commit_agreement_metadata,
    latest_agreement_versions,
    load_active_data_steward_profiles,
    metadata_lakehouse_root,
    next_minor_version,
    resolve_agreement_identity,
)
from fabricops_kit.fabric_input_output import FabricStore


def _config():
    store = FabricStore(env="dev", workspace_id="workspace", item_id="metadata-item", name="metadata", kind="lakehouse")
    return SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"metadata": store}}))


def _values(**overrides):
    values = {
        "agreement_name": "Orders agreement",
        "data_steward_profile": {"steward_id": "steward-001", "data_steward_name": "Configured steward", "data_steward_email": "steward@example.com", "domain": "Operations", "department": "Reporting", "faculty": "Shared Services"},
        "business_purpose": "Support governed reporting.", "approved_usage": "Approved reporting only.", "restricted_usage": "No redistribution.",
        "allowed_consumer_type": "Internal Department", "expected_output": "Dashboard", "source_system": "ERP", "refresh_frequency": "Daily",
        "retention_expectation": "Retain according to policy.", "start_date": "2026-01-01", "expiry_date": "2026-12-31", "renewal_required": "Yes",
    }
    values.update(overrides)
    return values


def test_agreement_and_steward_schemas_keep_durable_fields_only():
    assert DATA_AGREEMENT_FIELDS == [
        "agreement_id", "contract_version", "agreement_name", "steward_id",
        "business_purpose", "approved_usage", "restricted_usage", "allowed_consumer_type",
        "expected_output", "source_system", "refresh_frequency", "retention_expectation",
        "start_date", "expiry_date", "renewal_required", "_committed_by", "_committed_at",
        "_workspace_name", "_notebook_name", "_metadata_lakehouse_name", "_activity_id",
    ]
    assert DATA_STEWARD_FIELDS == [
        "steward_id", "data_steward_name", "data_steward_email", "domain", "department",
        "faculty", "effective_from", "effective_to", "is_active", "created_at", "updated_at",
    ]


def test_agreement_row_stores_steward_fk_without_profile_snapshot_or_derived_status():
    row = collect_agreement_metadata(widget_values=_values(), committed_by="user@example.com")["agreement_row"]
    assert row["steward_id"] == "steward-001"
    assert set(row) == set(DATA_AGREEMENT_FIELDS)
    for removed in (
        "data_steward_name", "data_steward_email", "domain", "department", "faculty",
        "agreement_status", "status_as_of_date", "review_status", "approved_by", "approved_at",
        "committed_by", "committed_at", "workspace_name", "notebook_name", "lakehouse_name", "run_id",
    ):
        assert removed not in row


def test_create_mode_commits_version_1_0_0():
    result = collect_agreement_metadata(widget_values=_values(), existing_rows=[], committed_by="user@example.com")
    assert result["agreement_row"]["agreement_id"].startswith("DA-")
    assert result["agreement_row"]["contract_version"] == "1.0.0"
    assert result["is_new_agreement"] is True


def test_update_mode_only_shows_latest_version_per_agreement_id():
    rows = [
        {"agreement_id": "DA-1", "contract_version": "1.0.0", "agreement_name": "Orders", "source_system": "ERP", "allowed_consumer_type": "Faculty"},
        {"agreement_id": "DA-1", "contract_version": "1.2.0", "agreement_name": "Orders", "source_system": "ERP", "allowed_consumer_type": "Faculty"},
        {"agreement_id": "DA-2", "contract_version": "1.0.0", "agreement_name": "People", "source_system": "CRM", "allowed_consumer_type": "Central Unit"},
    ]
    latest = latest_agreement_versions(rows)
    assert {(row["agreement_id"], row["contract_version"]) for row in latest} == {("DA-1", "1.2.0"), ("DA-2", "1.0.0")}
    options = agreement_dropdown_options(rows, include_prompt=True)
    assert options[0] == ("Select an agreement to update...", None)
    assert len(options) == 3
    assert "Steward ID:" in options[1][0]
    assert "Configured steward" not in options[1][0]


def test_update_mode_reuses_id_and_appends_next_minor_version():
    selected = {"agreement_id": "DA-1", "contract_version": "1.2.0"}
    result = collect_agreement_metadata(widget_values=_values(), mode="update", selected_agreement=selected, committed_by="user@example.com")
    assert result["agreement_row"]["agreement_id"] == "DA-1"
    assert result["agreement_row"]["contract_version"] == "1.3.0"
    assert result["is_new_agreement"] is False
    assert next_minor_version("invalid") == "1.0.0"


def test_create_mode_does_not_reuse_matching_existing_agreement_id(monkeypatch):
    monkeypatch.setattr(data_agreement, "_generate_agreement_id", lambda: "DA-NEW")
    rows = [{"agreement_id": "DA-1", "contract_version": "1.1.0", "agreement_name": "Orders agreement", "source_system": "ERP", "allowed_consumer_type": "Internal Department"}]
    identity = resolve_agreement_identity(rows, agreement_name="Orders agreement", source_system="ERP", allowed_consumer_type="Internal Department")
    assert identity == {"agreement_id": "DA-NEW", "contract_version": "1.0.0", "is_new_agreement": True}


def test_update_mode_requires_selected_agreement():
    with pytest.raises(ValueError, match="Update mode requires selected_agreement"):
        collect_agreement_metadata(widget_values=_values(), mode="update", committed_by="user@example.com")


def test_collect_agreement_metadata_accepts_spark_like_existing_rows_without_truthiness():
    class SparkLikeDataFrame:
        def __bool__(self):
            raise ValueError("Spark DataFrame truthiness is ambiguous")

    result = collect_agreement_metadata(widget_values=_values(), existing_rows=SparkLikeDataFrame(), committed_by="user@example.com")
    assert result["agreement_row"]["contract_version"] == "1.0.0"


def test_collect_agreement_metadata_uses_shared_runtime_audit_helper(monkeypatch):
    calls = []
    monkeypatch.setattr(data_agreement, "build_runtime_audit_fields", lambda **kwargs: calls.append(kwargs) or {
        "_committed_by": "fabric.user@example.com",
        "_committed_at": "2026-01-01T00:00:00+00:00",
        "_workspace_name": "Workspace",
        "_notebook_name": "01_da_orders",
        "_metadata_lakehouse_name": "metadata",
        "_activity_id": "activity-123",
    })
    config = _config()
    result = collect_agreement_metadata(widget_values=_values(), config=config, env="dev")
    assert calls == [{"config": config, "env": "dev", "committed_by": None, "committed_at": None, "runtime_context": None}]
    assert result["agreement_row"]["_committed_by"] == "fabric.user@example.com"


def test_agreement_row_uses_framework_managed_technical_audit_names():
    row = collect_agreement_metadata(
        widget_values=_values(),
        runtime_context={
            "userName": "fabric.user@example.com",
            "currentWorkspaceName": "Workspace",
            "currentNotebookName": "01_da_orders",
            "activityId": "activity-123",
        },
        config=_config(),
        env="dev",
        committed_at="2026-01-01T00:00:00+00:00",
    )["agreement_row"]
    assert row["_committed_by"] == "fabric.user@example.com"
    assert row["_committed_at"] == "2026-01-01T00:00:00+00:00"
    assert row["_workspace_name"] == "Workspace"
    assert row["_notebook_name"] == "01_da_orders"
    assert row["_metadata_lakehouse_name"] == "metadata"
    assert row["_activity_id"] == "activity-123"


def test_metadata_root_uses_configured_onelake_store_without_default_lakehouse():
    assert metadata_lakehouse_root(_config(), "dev") == "abfss://workspace@onelake.dfs.fabric.microsoft.com/metadata-item"


def test_steward_profiles_use_active_rows_only_and_never_seed_fake_people(monkeypatch):
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [
        {"steward_id": "1", "data_steward_name": "Configured steward", "data_steward_email": "configured@example.com", "domain": "Ops", "department": "BI", "faculty": "Shared", "effective_from": "2020-01-01", "effective_to": "", "is_active": "true"},
        {"steward_id": "2", "data_steward_name": "Inactive steward", "effective_from": "2020-01-01", "effective_to": "", "is_active": "false"},
        {"steward_id": "3", "data_steward_name": "Future steward", "effective_from": "2999-01-01", "effective_to": "", "is_active": "true"},
        {"steward_id": "4", "data_steward_name": "Expired steward", "effective_from": "2020-01-01", "effective_to": "2020-12-31", "is_active": "true"},
    ])
    profiles = load_active_data_steward_profiles(spark=object(), config=_config(), env="dev")
    assert [profile["data_steward_name"] for profile in profiles] == ["Configured steward"]


def test_invalid_steward_effective_date_raises_clear_setup_error(monkeypatch):
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [
        {"steward_id": "bad-date", "data_steward_name": "Configured steward", "effective_from": "not-a-date", "is_active": "true"},
    ])
    with pytest.raises(ValueError, match=f"{DATA_STEWARD_TABLE} row 'bad-date' has an invalid effective date"):
        load_active_data_steward_profiles(spark=object(), config=_config(), env="dev")


def test_no_active_stewards_raise_clear_setup_error(monkeypatch):
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match=f"{DATA_STEWARD_TABLE} has no active steward rows"):
        load_active_data_steward_profiles(spark=object(), config=_config(), env="dev")


def test_commit_appends_single_primary_table_by_configured_path(monkeypatch):
    calls = []
    class Frame:
        columns = []
    class Spark:
        def createDataFrame(self, rows):
            calls.append(("rows", rows))
            return Frame()
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: Frame())
    monkeypatch.setattr(data_agreement, "write_lakehouse_table", lambda df, config, env, target, table, mode: calls.append((env, target, table, mode)))
    metadata = collect_agreement_metadata(widget_values=_values(), committed_by="user@example.com")
    summary = commit_agreement_metadata(spark=Spark(), config=_config(), env="dev", agreement_metadata=metadata)
    assert calls[-1] == ("dev", "metadata", DATA_AGREEMENT_TABLE, "append")
    assert summary["table_updated"] == DATA_AGREEMENT_TABLE


def test_required_fields_and_date_validation_are_clear():
    with pytest.raises(ValueError, match="agreement_name"):
        collect_agreement_metadata(widget_values=_values(agreement_name=""), committed_by="user")
    with pytest.raises(ValueError, match="expiry_date must be a valid date"):
        collect_agreement_metadata(widget_values=_values(expiry_date="31/12/2026"), committed_by="user")


def test_update_form_prefills_latest_selected_row(monkeypatch):
    intake = SimpleNamespace(
        source_systems=("ERP",), refresh_frequencies=("Daily",),
        allowed_consumer_types=("Internal Department",), expected_outputs=("Dashboard",),
        renewal_options=("Yes", "No"), default_values={},
    )
    config = SimpleNamespace(path_config=_config().path_config, data_agreement_config=intake)
    steward = {"label": "Configured steward | Ops | BI | Shared", "steward_id": "1", "data_steward_name": "Configured steward", "data_steward_email": "configured@example.com", "domain": "Ops", "department": "BI", "faculty": "Shared", "effective_from": "2020-01-01", "effective_to": ""}
    latest = {"agreement_id": "DA-1", "contract_version": "1.2.0", "agreement_name": "Latest orders", "steward_id": "1", "business_purpose": "Latest purpose", "approved_usage": "Latest usage", "restricted_usage": "Latest restriction", "retention_expectation": "Latest retention", "allowed_consumer_type": "Internal Department", "expected_output": "Dashboard", "source_system": "ERP", "refresh_frequency": "Daily", "renewal_required": "Yes", "start_date": "2026-01-01", "expiry_date": "2026-12-31"}
    monkeypatch.setattr(data_agreement, "load_active_data_steward_profiles", lambda **kwargs: [steward])
    monkeypatch.setattr(data_agreement, "load_agreements", lambda *args, **kwargs: [latest])
    import sys
    import types

    class Widget:
        def __init__(self, options=(), value=None, **kwargs):
            self.options = options
            self._value = value if value is not None else (options[0][1] if options and isinstance(options[0], tuple) else options[0] if options else None)
            self.layout = SimpleNamespace(display="")
            self._observers = []
        @property
        def value(self): return self._value
        @value.setter
        def value(self, value):
            self._value = value
            for callback in self._observers: callback({"name": "value", "new": value})
        def observe(self, callback, names=None): self._observers.append(callback)
    widgets = types.ModuleType("ipywidgets")
    for name in ("Dropdown", "Text", "Textarea", "DatePicker", "Button", "Output", "HTML"):
        setattr(widgets, name, type(name, (Widget,), {}))
    widgets.VBox = lambda values: values
    display = types.ModuleType("IPython.display")
    display.display = lambda *args, **kwargs: None
    ipython = types.ModuleType("IPython")
    ipython.display = display
    monkeypatch.setitem(sys.modules, "ipywidgets", widgets)
    monkeypatch.setitem(sys.modules, "IPython", ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", display)
    form = data_agreement.create_agreement_form(spark=object(), config=config, env="dev")
    assert form["source_system"].options == ["ERP"]
    assert form["refresh_frequency"].options == ["Daily"]
    assert form["allowed_consumer_type"].options == ["Internal Department"]
    assert form["expected_output"].options == ["Dashboard"]
    assert form["renewal_required"].options == ["Yes", "No"]
    form["mode"].value = "Update Existing Agreement"
    form["existing_agreement"].value = latest
    assert form["agreement_name"].value == "Latest orders"
    assert form["business_purpose"].value == "Latest purpose"
    assert form["data_steward_profile"].value == steward
    assert "Latest version: 1.2.0" in form["agreement_identity"].value
    assert "Next version: 1.3.0" in form["agreement_identity"].value
    assert "Agreement status:" not in form["agreement_identity"].value
    assert "Review status:" not in form["agreement_identity"].value
    assert "Latest expiry date: 2026-12-31" in form["agreement_identity"].value



def _stub_ipython_display(monkeypatch):
    display = types.ModuleType("IPython.display")
    display.clear_output = lambda: None
    ipython = types.ModuleType("IPython")
    ipython.display = display
    monkeypatch.setitem(sys.modules, "IPython", ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", display)


def test_render_agreement_intake_app_wires_commit_button_and_commits(monkeypatch, capsys):
    _stub_ipython_display(monkeypatch)

    class Output:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class Button:
        callback = None

        def on_click(self, callback):
            self.callback = callback

    button = Button()
    form = {
        "mode": SimpleNamespace(value="Create New Agreement"),
        "existing_agreement": SimpleNamespace(value=None),
        "commit_button": button,
        "output": Output(),
    }
    latest = [{"agreement_id": "DA-OLD", "contract_version": "1.0.0"}]
    values = _values()
    metadata = {"agreement_row": {"agreement_id": "DA-NEW"}}
    summary = {
        "agreement_id": "DA-NEW",
        "contract_version": "1.0.0",
        "expiry_date": "2026-12-31",
        "_committed_by": "user@example.com",
        "_committed_at": "2026-01-01T00:00:00+00:00",
        "table_updated": DATA_AGREEMENT_TABLE,
    }
    calls = []
    monkeypatch.setattr(data_agreement, "create_agreement_form", lambda **kwargs: form)
    monkeypatch.setattr(data_agreement, "load_agreements", lambda *args, **kwargs: latest)
    monkeypatch.setattr(data_agreement, "read_agreement_form", lambda actual_form: values)
    monkeypatch.setattr(data_agreement, "collect_agreement_metadata", lambda **kwargs: calls.append(("collect", kwargs)) or metadata)
    monkeypatch.setattr(data_agreement, "commit_agreement_metadata", lambda **kwargs: calls.append(("commit", kwargs)) or summary)

    app = data_agreement.render_agreement_intake_app(spark="spark", config="config", env="dev")

    assert app is form
    assert button.callback is not None
    button.callback(None)
    assert calls[0] == ("collect", {
        "widget_values": values,
        "mode": "create",
        "existing_rows": latest,
        "selected_agreement": None,
        "config": "config",
        "env": "dev",
    })
    assert calls[1] == ("commit", {
        "spark": "spark",
        "config": "config",
        "env": "dev",
        "agreement_metadata": metadata,
    })
    output = capsys.readouterr().out
    assert "Data agreement committed successfully." in output
    assert "- Agreement ID: DA-NEW" in output
    assert f"- Table Updated: {DATA_AGREEMENT_TABLE}" in output


def test_render_agreement_intake_app_prints_clear_failure_for_missing_update_selection(monkeypatch, capsys):
    _stub_ipython_display(monkeypatch)

    class Output:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class Button:
        callback = None

        def on_click(self, callback):
            self.callback = callback

    button = Button()
    form = {
        "mode": SimpleNamespace(value="Update Existing Agreement"),
        "existing_agreement": SimpleNamespace(value=None),
        "commit_button": button,
        "output": Output(),
    }
    monkeypatch.setattr(data_agreement, "create_agreement_form", lambda **kwargs: form)
    monkeypatch.setattr(data_agreement, "load_agreements", lambda *args, **kwargs: [])

    data_agreement.render_agreement_intake_app(spark="spark", config="config", env="dev")
    button.callback(None)

    assert "Commit failed: Update mode selected, but no existing agreement was chosen." in capsys.readouterr().out

def test_setup_data_agreement_tables_creates_only_current_metadata_tables(monkeypatch):
    ensured = []
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda spark, config, env, table_name, fields: ensured.append((table_name, fields)))

    tables = data_agreement.setup_data_agreement_tables(spark=object(), config=_config(), env="dev")

    assert tables == [DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE]
    assert ensured == [(DATA_AGREEMENT_TABLE, DATA_AGREEMENT_FIELDS), (DATA_STEWARD_TABLE, DATA_STEWARD_FIELDS)]


def test_metadata_architecture_documents_current_agreement_and_steward_model():
    architecture = Path("docs/metadata-and-contracts/metadata-architecture.md").read_text(encoding="utf-8")
    agreement_section = architecture.split("### `METADATA_DATA_AGREEMENT`", 1)[1].split("### `METADATA_DATA_STEWARD`", 1)[0]
    steward_section = architecture.split("### `METADATA_DATA_STEWARD`", 1)[1].split("### `METADATA_DATA_CATALOGUE`", 1)[0]
    documented_fields = [
        line.split("|", 2)[1].strip()
        for line in agreement_section.splitlines()
        if line.startswith("| ") and "| Implemented |" in line
    ]

    assert documented_fields == [
        "agreement_id", "contract_version", "agreement_name", "steward_id",
        "business_purpose", "approved_usage", "restricted_usage",
        "allowed_consumer_type", "expected_output", "source_system",
        "refresh_frequency", "retention_expectation", "start_date",
        "expiry_date", "renewal_required", "_committed_by", "_committed_at",
        "_notebook_name", "_workspace_name", "_lakehouse_name", "_run_id",
    ]
    assert "One row = one agreement version" in agreement_section
    assert "agreement_id + contract_version" in agreement_section
    assert "LYRA-style workbook or data-dictionary fields" in agreement_section
    assert "derive the current status dynamically from `expiry_date`" in agreement_section
    assert "nine workflow evidence metadata tables plus maintained reference metadata tables" in architecture
    assert "`METADATA_DATA_STEWARD` is maintained reference metadata" in architecture
    assert "maintained source of truth for data steward identity" in steward_section
    assert "Do not put steward reference rows inside `METADATA_DATA_CATALOGUE`" in steward_section
