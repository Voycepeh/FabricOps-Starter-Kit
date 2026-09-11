"""Focused contracts for standalone normalized Guardrail authoring."""

from __future__ import annotations

import inspect
import json
import sys
import types

import pytest

import fabricops_kit
from fabricops_kit.widgets import shared as authoring
from fabricops_kit.data_contract import shared as contract_authoring
from fabricops_kit.widgets.widget_author_guardrails import widget_author_guardrails
guardrail_widget_module = __import__("importlib").import_module("fabricops_kit.widgets.widget_author_guardrails")
from fabricops_kit.widgets.widget_author_guardrails import (
    _guardrail_records_from_selection,
    _render_guardrail_authoring,
    _render_sensitive_data_editor,
)


OBSOLETE_GUARDRAIL_FIELDS = {
    "configuration_version", "metadata_table_key", "metadata_column_key", "dataset_name", "table_name",
    "column_name", "rule_key", "review_status", "review_state", "approval_required", "approval_bypassed",
    "requires_governance_review", "requires_post_review", "bypass_reason", "action_type", "source_notebook_type",
    "created_by_role",
}


def _install_fake_notebook_widgets(monkeypatch, *, auto_observe=False):
    """Install minimal ipywidgets/IPython fakes for widget unit tests."""

    class Widget:
        def __init__(self, *args, **kwargs):
            self._observers = []
            options = kwargs.get("options", [])
            self.options = options
            if "value" in kwargs:
                self._value = kwargs["value"]
            elif options:
                first = options[0]
                self._value = first[1] if isinstance(first, tuple) and len(first) == 2 else first
            else:
                self._value = ""
            self.description = kwargs.get("description", "")
            self.layout = kwargs.get("layout") or types.SimpleNamespace(display="")
            self.button_style = kwargs.get("button_style", "")
            self.disabled = kwargs.get("disabled", False)

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            previous = self._value
            self._value = value
            if auto_observe and previous != value:
                for callback in self._observers:
                    callback({"name": "value", "old": previous, "new": value})

        def observe(self, callback, names=None):
            self._observer = callback
            self._observers.append(callback)

        def on_click(self, callback):
            self._click = callback

        def add_class(self, _name):
            return None

    class Box(Widget):
        def __init__(self, children=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.children = children or []

    fake_widgets = types.SimpleNamespace(
        Dropdown=Widget, Select=Widget, SelectMultiple=Widget, Textarea=Widget, Text=Widget,
        BoundedIntText=Widget, FloatText=Widget, ToggleButtons=Widget, Combobox=Widget,
        Checkbox=Widget, Button=Widget, HTML=Widget, VBox=Box, HBox=Box, GridBox=Box,
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    fake_display = types.SimpleNamespace(display=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(display=fake_display))
    monkeypatch.setitem(sys.modules, "ipywidgets", fake_widgets)
    return fake_widgets


def _state(existing=()):
    rows = [
        {"table_id": "table-orders", "column_id": "col-id", "column_name": "id", "data_type": "bigint"},
        {"table_id": "table-orders", "column_id": "col-updated", "column_name": "updated_at", "data_type": "timestamp"},
        {"table_id": "table-orders", "column_id": "col-snapshot", "column_name": "snapshot_date", "data_type": "date"},
        {"table_id": "table-orders", "column_id": "col-extra", "column_name": "extra", "data_type": "string"},
    ]
    return {
        "environment_name": "dev",
        "table_id": "table-orders",
        "contract_id": "contract-orders",
        "contract_version": 2,
        "table_name": "orders",
        "store_type": "lakehouse",
        "layer": "source",
        "schema_name": "dbo",
        "columns": [row["column_name"] for row in rows],
        "column_ids": {row["column_name"]: row["column_id"] for row in rows},
        "catalogue_profile_rows": rows,
        "existing_rules": list(existing),
    }


def _records(**overrides):
    values = dict(
        required_columns=["id"], freshness_column="updated_at", maximum_age=1,
        maximum_age_unit="Hours",
        partition_column="snapshot_date", change_column="updated_at",
    )
    values.update(overrides)
    return _guardrail_records_from_selection(_state(), **values)


@pytest.mark.parametrize("treatment,parameters", [
    ("tokenize", {}),
    ("mask", {"preserve_start": 1, "preserve_end": 2, "mask_character": "*"}),
    ("bucket", {"bins": [0, 10], "labels": ["low", "high"]}),
    ("remove", {}),
])
def test_sensitive_data_selection_uses_canonical_column_identity(treatment, parameters):
    """The existing Guardrail service authors explicit column-scoped treatment."""
    records = _records(
        sensitive_rules=[{
            "column_name": "extra", "treatment": treatment, "action": "Warn",
            "parameters": parameters,
        }],
    )
    rule = next(row for row in records if row["guardrail_type"] == "sensitive_data")
    assert rule["column_id"] == "col-extra"
    assert rule["rule_id"] == "sensitive_data_col-extra"
    assert rule["contract_id"] == "contract-orders"
    assert rule["contract_version"] == 2
    assert json.loads(rule["rule_parameters_json"]) == {
        "scope": "column", "treatment": treatment, **parameters,
    }
    assert rule["action"] == "Warn"


def test_multiple_sensitive_columns_have_independent_logical_identities():
    """Each governed column produces one independently versioned logical rule."""
    rules = [
        {"column_name": "id", "treatment": "tokenize", "action": "Block"},
        {"column_name": "extra", "treatment": "remove", "action": "Warn"},
    ]
    sensitive = [
        row for row in _records(sensitive_rules=rules)
        if row["guardrail_type"] == "sensitive_data"
    ]
    assert [row["column_id"] for row in sensitive] == ["col-id", "col-extra"]
    assert len({row["rule_id"] for row in sensitive}) == 2
    assert len({row["guardrail_rule_id"] for row in sensitive}) == 2


def test_sensitive_editor_uses_one_control_set_not_one_per_column(monkeypatch):
    """The compact editor instantiates treatment controls only for the edited rule."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    editor = _render_sensitive_data_editor(_state(), widgets=widgets, ai_config={})
    assert set(editor["controls"]) == {
        "column", "treatment", "action", "preserve_start", "preserve_end",
        "mask_character", "bins", "labels",
    }
    assert len(editor["draft_rules"]) == 0


def test_sensitive_editor_adds_edits_removes_and_retains_rules(monkeypatch):
    """Draft rule actions retain independent columns and deactivate saved rules."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    saved = authoring.sensitive_data_record_from_selection(
        _state(), column_name="id", treatment="tokenize", action="Block"
    )
    editor = _render_sensitive_data_editor(
        _state([saved]), widgets=widgets, ai_config={}
    )
    controls = editor["controls"]
    controls["column"].value = "extra"
    controls["treatment"].value = "mask"
    controls["preserve_start"].value = 1
    controls["preserve_end"].value = 2
    controls["mask_character"].value = "*"
    added = editor["add_or_update"]()
    assert added["treatment"] == "mask"
    assert len([rule for rule in editor["draft_rules"] if rule["is_active"]]) == 2
    editor["edit_rule"](added)
    controls["action"].value = "Warn"
    editor["add_or_update"]()
    assert next(rule for rule in editor["draft_rules"] if rule["column_name"] == "extra")["action"] == "Warn"
    persisted = next(rule for rule in editor["draft_rules"] if rule["column_name"] == "id")
    editor["remove_rule"](persisted)
    assert persisted["is_active"] is False


def test_sensitive_editor_shows_only_relevant_treatment_fields(monkeypatch):
    """Mask and Bucket options toggle for the single current editor."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    editor = _render_sensitive_data_editor(_state(), widgets=widgets, ai_config={})
    editor["controls"]["treatment"].value = "mask"
    editor["update_options"]()
    assert editor["mask_options"].layout.display == ""
    assert editor["bucket_options"].layout.display == "none"
    editor["controls"]["treatment"].value = "bucket"
    editor["update_options"]()
    assert editor["mask_options"].layout.display == "none"
    assert editor["bucket_options"].layout.display == ""


def test_sensitive_ai_suggestions_are_draft_only(monkeypatch):
    """Validated AI suggestions populate drafts without invoking persistence."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    suggestion = {
        "column_name": "extra", "column_id": "col-extra", "treatment": "remove",
        "action": "Block", "parameters": {}, "is_active": True,
    }
    prompts = []
    def fake_suggest(*_args, **kwargs):
        prompts.append(kwargs["prompt"])
        return [suggestion]
    monkeypatch.setattr(
        guardrail_widget_module.enrichment_ai, "suggest_sensitive_data", fake_suggest,
    )
    editor = _render_sensitive_data_editor(
        _state(), widgets=widgets,
        ai_config={"enabled": True, "sensitive_data_prompt": "policy"},
    )
    assert editor["suggest"]() == [suggestion]
    assert editor["draft_rules"][0]["column_name"] == "extra"
    assert "persisted" in editor["draft_rules"][0]
    assert prompts == ["policy"]


def test_blank_sensitive_ai_prompt_disables_only_suggestions(monkeypatch):
    """A missing dedicated prompt leaves the compact manual editor available."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    editor = _render_sensitive_data_editor(
        _state(), widgets=widgets,
        ai_config={"enabled": True, "description_prompt": "describe", "classification_prompt": "classify"},
    )
    assert editor["suggest_button"].disabled is True
    assert editor["suggest"]() == []
    assert "not configured" in editor["status"].value
    assert editor["add_or_update"]()["treatment"] == "tokenize"


def test_sensitive_ai_unavailable_keeps_manual_editor_usable(monkeypatch):
    """AI failure is advisory and does not disable manual rule creation."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    monkeypatch.setattr(
        guardrail_widget_module.enrichment_ai, "suggest_sensitive_data",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("unavailable")),
    )
    editor = _render_sensitive_data_editor(
        _state(), widgets=widgets,
        ai_config={"enabled": True, "sensitive_data_prompt": "policy"},
    )
    assert editor["suggest"]() == []
    assert "Manual authoring remains available" in editor["status"].value
    assert editor["add_or_update"]()["treatment"] == "tokenize"


def test_classification_context_alone_does_not_create_sensitive_rule(monkeypatch):
    """Classification remains advisory context until Suggest or Add is explicit."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    state = _state()
    state["catalogue_profile_rows"][0]["classification"] = "Restricted"
    editor = _render_sensitive_data_editor(state, widgets=widgets, ai_config={"enabled": False})
    assert editor["draft_rules"] == []


def test_legacy_guardrail_widgets_are_implementation_only():
    """Keep owner-module coverage without restoring the fragmented public API."""
    from fabricops_kit.widgets.widget_author_dq_rules import widget_author_dq_rules

    assert callable(widget_author_guardrails)
    assert callable(widget_author_dq_rules)
    assert "widget_author_guardrails" not in fabricops_kit.__all__
    assert "widget_author_dq_rules" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "widget_author_guardrails")
    assert not hasattr(fabricops_kit, "widget_author_dq_rules")


def test_guardrail_records_use_only_stage4a_authoring_fields():
    """Verify that authored Guardrail rows use only the Stage 4A contract."""
    records = _records()
    expected = {
        "guardrail_rule_id", "guardrail_version", "contract_id", "contract_version", "column_id", "environment_name",
        "guardrail_type", "rule_id", "rule_type", "rule_parameters_json", "action", "is_active",
    }
    assert all(set(row) == expected for row in records)
    assert all(row["contract_id"] == "contract-orders" and row["contract_version"] == 2 for row in records)
    assert all("table_id" not in row for row in records)
    assert all(not (set(row) & OBSOLETE_GUARDRAIL_FIELDS) for row in records)


def test_schema_selection_serializes_required_columns_and_current_types():
    """Verify that Schema rules persist required columns and current data types."""
    schema = _records(required_columns=["id", "extra"])[0]
    assert schema["guardrail_type"] == "schema"
    assert schema["rule_id"] == "schema"
    assert schema["rule_type"] == "minimum_required"
    assert json.loads(schema["rule_parameters_json"]) == {
        "columns": ["id", "extra"], "data_types": {"extra": "string", "id": "bigint"},
    }


def test_freshness_uses_runtime_parameter_vocabulary_and_failure_severity():
    """Verify that Freshness rules use the runtime parameter vocabulary."""
    freshness = _records(maximum_age=24, maximum_age_unit="Hours", freshness_action="Warn")[1]
    assert freshness["rule_type"] == "max_age"
    assert freshness["action"] == "Warn"
    assert json.loads(freshness["rule_parameters_json"]) == {
        "freshness_column": "updated_at", "maximum_age": 24.0, "maximum_age_unit": "hours",
    }
    assert freshness["column_id"] == ""


def test_freshness_can_be_disabled_without_removing_logical_rule():
    """Verify that Freshness can be disabled while preserving its logical row."""
    freshness = _records(freshness_column="")[1]
    assert freshness["rule_id"] == "freshness"
    assert freshness["rule_type"] == "skip"
    assert json.loads(freshness["rule_parameters_json"])["freshness_column"] == ""


def test_source_stability_authors_only_observation_inputs():
    """Source Stability authoring stores no parallel processing vocabulary."""
    rule = _records()[2]
    params = json.loads(rule["rule_parameters_json"])
    assert rule["guardrail_type"] == "source_stability"
    assert rule["rule_id"] == "source_stability"
    assert rule["rule_type"] == "historical_mutation"
    assert params == {
        "partition_column": "snapshot_date",
        "change_column": "updated_at",
    }


def test_invalid_columns_age_and_failure_action_fail_clearly():
    """Verify that invalid Guardrail inputs fail with clear validation errors."""
    with pytest.raises(ValueError, match="positive"):
        _records(maximum_age=0)
    with pytest.raises(ValueError, match="selected table schema"):
        _records(required_columns=["missing"])
    with pytest.raises(ValueError, match="Failure action"):
        _records(schema_action="error")


def test_rule_identity_is_stable_while_guardrail_version_advances():
    """Verify stable logical identity across Guardrail versions."""
    first = _records(guardrail_version=1)
    second = _records(guardrail_version=2, maximum_age=48)
    assert [row["guardrail_rule_id"] for row in first] == [row["guardrail_rule_id"] for row in second]
    assert {row["guardrail_version"] for row in first} == {1}
    assert {row["guardrail_version"] for row in second} == {2}


def test_column_name_to_column_id_resolution_is_canonical():
    """Verify that visible column names resolve through canonical Catalogue IDs."""
    assert authoring._column_id_for_name(_state(), "updated_at") == "col-updated"
    with pytest.raises(ValueError, match="column_id"):
        authoring._column_id_for_name(_state(), "missing")


def test_target_resolver_joins_latest_profile_snapshot_to_catalogue(monkeypatch):
    """Verify that target resolution joins the latest profile snapshot to Catalogue."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    catalogue = [
        {
            "metadata_level": "table", "table_id": "table-orders", "column_id": "", "environment_name": "dev",
            "store_type": "lakehouse", "layer": "silver", "schema_name": "dbo", "table_name": "orders",
        },
        *[
            {
                "metadata_level": "column", "table_id": "table-orders", "column_id": column_id,
                "column_name": column_name, "environment_name": "dev",
            }
            for column_id, column_name in (("col-a", "a"), ("col-b", "b"), ("col-c", "obsolete_c"))
        ],
    ]
    profiles = [
        {
            "profile_id": f"old-{column_id}", "profile_snapshot_id": "snapshot-1", "table_id": "table-orders",
            "column_id": column_id, "environment_name": "dev", "data_type": "string",
            "_committed_at": "2026-01-01T00:00:00Z",
        }
        for column_id in ("col-a", "col-c")
    ] + [
        {
            "profile_id": f"new-{column_id}", "profile_snapshot_id": "snapshot-2", "table_id": "table-orders",
            "column_id": column_id, "environment_name": "dev", "data_type": "string",
            "_committed_at": "2026-02-01T00:00:00Z",
        }
        for column_id in ("col-a", "col-b")
    ]
    rules = [{"contract_id": "contract-orders", "contract_version": 2, "environment_name": "dev", "guardrail_type": "schema"}]
    contracts = [{"contract_id": "contract-orders", "contract_version": 2, "table_id": "table-orders", "status": "draft"}]

    def fake_read(config, env, table_name, *, spark_session):
        return {
            authoring.CATALOGUE_TABLE: catalogue,
            authoring.PROFILED_TABLE: profiles,
            authoring.GUARDRAIL_TABLE: rules,
            authoring.DATA_CONTRACT_TABLE: contracts,
            "METADATA_ENRICHMENT": [],
        }[table_name]

    monkeypatch.setattr(authoring, "read_metadata_table_or_empty", fake_read)
    state, _, _ = authoring.load_guardrail_authoring_targets(
        object(), "dev", spark_session=object(), widgets=widgets
    )

    assert state["table_id"] == "table-orders"
    assert state["profile_snapshot_id"] == "snapshot-2"
    assert state["columns"] == ["a", "b"]
    assert state["column_ids"] == {"a": "col-a", "b": "col-b"}
    assert state["existing_rules"] == rules
    assert "metadata_table_key" not in state


def test_widget_preview_uses_new_metadata_vocabulary(monkeypatch):
    """Verify that the widget preview exposes only normalized metadata vocabulary."""
    _install_fake_notebook_widgets(monkeypatch)
    widget = _render_guardrail_authoring(_state(), context={"config": object(), "env": "dev"})
    preview = widget["controls"]["preview"].value
    assert '"contract_id": "contract-orders"' in preview
    assert '"contract_version": 2' in preview
    assert '"guardrail_version": 1' in preview
    for field in OBSOLETE_GUARDRAIL_FIELDS:
        assert f'"{field}"' not in preview


def test_widget_save_uses_shared_canonical_writer_and_advances_version(monkeypatch):
    """Verify that saving uses the shared writer and advances Guardrail version."""
    _install_fake_notebook_widgets(monkeypatch)
    saved = []
    monkeypatch.setattr(guardrail_widget_module, "save_guardrails", lambda records, **kwargs: saved.append([dict(row) for row in records]) or [dict(row) for row in records])
    widget = _render_guardrail_authoring(
        _state(), spark_session=object(), context={"config": object(), "env": "dev"}
    )
    first = widget["save"]()
    second = widget["save"]()
    assert len(saved) == 2
    assert {row["guardrail_version"] for row in first} == {1}
    assert {row["guardrail_version"] for row in second} == {2}


def test_authoring_widgets_do_not_depend_on_each_other_or_public_target_selector():
    """Verify that the standalone widgets do not depend on each other or old selector."""
    guardrail_source = inspect.getsource(sys.modules["fabricops_kit.widgets.widget_author_guardrails"])
    assert "widget_author_dq_rules(" not in guardrail_source
    assert "widget_select_guardrail_target" not in guardrail_source
