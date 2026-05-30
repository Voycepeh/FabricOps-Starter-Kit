from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

import fabricops_kit.data_agreement as data_agreement
from fabricops_kit.data_agreement import (
    DATA_AGREEMENT_FIELDS,
    DATA_AGREEMENT_TABLE,
    DATA_STEWARD_TABLE,
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
        "data_steward_profile": {"data_steward_name": "Configured steward", "data_steward_email": "steward@example.com", "domain": "Operations", "department": "Reporting", "faculty": "Shared Services"},
        "business_purpose": "Support governed reporting.", "approved_usage": "Approved reporting only.", "restricted_usage": "No redistribution.",
        "allowed_consumer_type": "Internal Department", "expected_output": "Dashboard", "source_system": "ERP", "refresh_frequency": "Daily",
        "retention_expectation": "Retain according to policy.", "start_date": "2026-01-01", "expiry_date": "2026-12-31", "renewal_required": "Yes",
    }
    values.update(overrides)
    return values


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


def test_committed_by_resolves_fabric_user_name_before_user_id(monkeypatch):
    monkeypatch.setattr(data_agreement, "_runtime_context", lambda: {"userName": "fabric.user@example.com", "userId": "fabric-user-id"})
    result = collect_agreement_metadata(widget_values=_values())
    assert result["agreement_row"]["committed_by"] == "fabric.user@example.com"


def test_metadata_root_uses_configured_onelake_store_without_default_lakehouse():
    assert metadata_lakehouse_root(_config(), "dev") == "abfss://workspace@onelake.dfs.fabric.microsoft.com/metadata-item"


def test_steward_profiles_use_active_rows_only_and_never_seed_fake_people(monkeypatch):
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(data_agreement, "read_lakehouse_table", lambda *args, **kwargs: [
        {"steward_id": "1", "data_steward_name": "Configured steward", "data_steward_email": "configured@example.com", "domain": "Ops", "department": "BI", "faculty": "Shared", "is_active": "true"},
        {"steward_id": "2", "data_steward_name": "Inactive steward", "is_active": "false"},
    ])
    profiles = load_active_data_steward_profiles(spark=object(), config=_config(), env="dev")
    assert [profile["data_steward_name"] for profile in profiles] == ["Configured steward"]


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
    steward = {"label": "Configured steward | Ops | BI | Shared", "steward_id": "1", "data_steward_name": "Configured steward", "data_steward_email": "configured@example.com", "domain": "Ops", "department": "BI", "faculty": "Shared"}
    latest = {"agreement_id": "DA-1", "contract_version": "1.2.0", "agreement_name": "Latest orders", "data_steward_name": "Configured steward", "data_steward_email": "configured@example.com", "domain": "Ops", "department": "BI", "faculty": "Shared", "business_purpose": "Latest purpose", "approved_usage": "Latest usage", "restricted_usage": "Latest restriction", "retention_expectation": "Latest retention", "allowed_consumer_type": "Internal Department", "expected_output": "Dashboard", "source_system": "ERP", "refresh_frequency": "Daily", "renewal_required": "Yes", "start_date": "2026-01-01", "expiry_date": "2026-12-31"}
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
    form["mode"].value = "Update Existing Agreement"
    form["existing_agreement"].value = latest
    assert form["agreement_name"].value == "Latest orders"
    assert form["business_purpose"].value == "Latest purpose"
    assert form["data_steward_profile"].value == steward
    assert "Latest version: 1.2.0" in form["agreement_identity"].value
    assert "Next version: 1.3.0" in form["agreement_identity"].value
    assert "Agreement status:" in form["agreement_identity"].value
    assert "Review status:" in form["agreement_identity"].value
    assert "Latest expiry date: 2026-12-31" in form["agreement_identity"].value


def test_setup_data_agreement_tables_creates_only_current_metadata_tables(monkeypatch):
    ensured = []
    monkeypatch.setattr(data_agreement, "_ensure_delta_table", lambda spark, config, env, table_name, fields: ensured.append(table_name))

    tables = data_agreement.setup_data_agreement_tables(spark=object(), config=_config(), env="dev")

    assert tables == [DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE]
    assert ensured == [DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE]


def test_metadata_architecture_documents_implemented_agreement_schema():
    architecture = Path("docs/metadata-and-contracts/metadata-architecture.md").read_text(encoding="utf-8")
    section = architecture.split("### `METADATA_DATA_AGREEMENT`", 1)[1].split("### `METADATA_DATA_CATALOGUE`", 1)[0]
    documented_fields = [
        line.split("|", 2)[1].strip()
        for line in section.splitlines()
        if line.startswith("| ") and "| Implemented |" in line
    ]

    assert documented_fields == DATA_AGREEMENT_FIELDS
    assert "One row = one agreement version" in section
    assert "agreement_id + contract_version" in section
    assert "LYRA-style workbook or data-dictionary fields" in section
    assert "exactly nine source metadata tables" in architecture
    assert "`METADATA_DATA_STEWARD` is a setup/helper table" in architecture
