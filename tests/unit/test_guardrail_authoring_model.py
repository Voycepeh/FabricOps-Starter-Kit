"""Tests for governed guardrail authoring state helpers."""

import json

import pytest

from fabricops_kit.pipeline import guardrails_shared as dq_runtime
from fabricops_kit.widgets import shared as governance_review
from fabricops_kit.widgets.shared import (
    CATALOGUE_TABLE,
    GUARDRAIL_RESULTS_TABLE,
    GUARDRAIL_TABLE,
)
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.widgets import widget_author_dq_rules, widget_enrich_table_metadata, widget_review_guardrail_governance


@pytest.fixture(autouse=True)
def active_fabric_context(monkeypatch):
    """Provide the mandatory active Fabric context for widget unit tests."""
    import builtins
    import types

    context = {
        "config": types.SimpleNamespace(
            governance_config=types.SimpleNamespace(
                sensitivity_labels=["public"],
                pii_classifications=["none"],
                enrichment_context_widget={"custom_fields": []},
                enrichment_classification_widget={"custom_fields": []},
            )
        ),
        "env": "dev",
    }
    monkeypatch.setattr(builtins, "FABRIC_CONTEXT", context, raising=False)
    audit = {"_workspace_id": "workspace-id", "_workspace_name": "workspace", "_notebook_id": "notebook-id", "_notebook_name": "notebook", "_activity_id": "activity-id", "_committed_by": "user", "_committed_at": "2026-01-01T00:00:00+00:00", "_metadata_lakehouse_name": "metadata"}
    monkeypatch.setattr(governance_review, "build_runtime_audit_fields", lambda **kwargs: dict(audit))
    return context


def _install_fake_notebook_widgets(monkeypatch, *, auto_observe=False):
    """Install minimal ipywidgets/IPython fakes for widget unit tests."""
    import sys
    import types

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
            self.rows = kwargs.get("rows", None)

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

    class Box(Widget):
        def __init__(self, children=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.children = children or []

    fake_widgets = types.SimpleNamespace(
        Dropdown=Widget,
        Select=Widget,
        SelectMultiple=Widget,
        Textarea=Widget,
        Text=Widget,
        BoundedIntText=Widget,
        ToggleButtons=Widget,
        Combobox=Widget,
        Checkbox=Widget,
        Button=Widget,
        HTML=Widget,
        VBox=Box,
        HBox=Box,
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    fake_display = types.SimpleNamespace(display=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(display=fake_display))
    monkeypatch.setattr("importlib.import_module", lambda name: fake_widgets if name == "ipywidgets" else __import__(name))


def _widget_descriptions(widget):
    """Return all widget descriptions reachable from a fake widget tree."""
    descriptions = []
    description = getattr(widget, "description", "")
    if description:
        descriptions.append(description)
    for child in getattr(widget, "children", []) or []:
        descriptions.extend(_widget_descriptions(child))
    return descriptions


def test_metadata_ownership_schema_separates_catalogue_rules_and_results():
    """Verify catalogue, rule, result, and governance policy fields stay separated."""
    schemas = metadata_table_schema_registry()
    catalogue_fields = set(schemas[CATALOGUE_TABLE].fieldNames())
    rule_fields = set(schemas[GUARDRAIL_TABLE].fieldNames())
    result_fields = set(schemas[GUARDRAIL_RESULTS_TABLE].fieldNames())

    removed_catalogue_fields = {
        "load_behavior",
        "source_data_change_check",
        "target_data_change_check",
        "source_schema_check",
        "target_schema_check",
        "dq_status",
        "dq_rule_count",
        "dq_failed_rule_count",
        "dq_failed_row_count",
        "source_change_signal_json",
    }
    assert not removed_catalogue_fields & catalogue_fields
    assert {"approval_required", "approval_bypassed", "requires_post_review", "governance_mode", "approval_policy"}.issubset(rule_fields)
    assert {"result_id", "result_payload_json", "actual_value_json"}.issubset(result_fields)
    assert {"governance_mode", "approval_policy", "bypass_allowed", "policy_reason"}.isdisjoint(catalogue_fields)
    assert {"policy_updated_by", "policy_updated_at"}.isdisjoint(catalogue_fields)
    assert governance_review.DATA_ACCESS_TABLE in schemas


def test_table_policy_defaults_to_ungoverned_no_approval():
    """Verify missing policy rows make a table ungoverned by default."""
    policy = governance_review.resolve_table_governance_policy([], environment_name="dev", dataset_name="sales", table_name="orders")
    assert policy["governance_mode"] == "ungoverned"
    assert policy["approval_policy"] == "no_approval_required"


def test_authoring_status_matches_ungoverned_governed_and_bypass_paths():
    """Verify authoring lifecycle fields for all table governance paths."""
    ungoverned = governance_review.guardrail_authoring_status({"governance_mode": "ungoverned"})
    governed = governance_review.guardrail_authoring_status({"governance_mode": "governed", "approval_policy": "approval_required"})
    bypassed = governance_review.guardrail_authoring_status({"governance_mode": "governed", "approval_policy": "approval_required_with_bypass"}, bypass_reason="urgent fix", actor="engineer@example.com")

    assert ungoverned["is_active"] is True
    assert ungoverned["review_status"] == "self_approved"
    assert governed["is_active"] is False
    assert governed["review_status"] == "pending_governance_review"
    assert bypassed["is_active"] is True
    assert bypassed["review_status"] == "active_pending_governance_review"
    assert bypassed["requires_post_review"] is True
    assert bypassed["bypass_reason"] == "urgent fix"


def test_governance_rule_actions_approve_reject_and_supersede():
    """Verify governance can approve, reject, and supersede append-only rule rows."""
    rule = {"rule_key": "old", "review_status": "pending_governance_review", "is_active": False}
    assert governance_review.apply_governance_rule_action(rule, "approve", actor="steward@example.com")["review_status"] == "governance_approved"
    assert governance_review.apply_governance_rule_action(rule, "reject")["is_active"] is False
    superseded = governance_review.apply_governance_rule_action(rule, "supersede", superseded_by_rule_key="new")
    assert superseded["review_status"] == "superseded"
    assert superseded["superseded_by_rule_key"] == "new"






def _rule(**overrides):
    base = {
        "rule_key": "rule-key",
        "rule_id": "rule-id",
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "column_name": "",
        "guardrail_type": "schema",
        "rule_type": "relaxed",
        "rule_parameters_json": "{}",
        "severity": "blocking",
        "is_active": True,
        "review_status": "self_approved",
        "created_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def test_schema_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify schema rule rows are loaded and enforced."""
    from fabricops_kit.pipeline.guardrails_shared import schema_check_core

    df = spark_session.createDataFrame([(1, "ok", "extra")], "order_id int, status string, extra string")
    rules = [_rule(rule_parameters_json=json.dumps({"columns": ["order_id", "status"], "data_types": {"order_id": "int", "status": "string"}}))]

    result = schema_check_core(df, rules, dataset_name="sales", table_name="orders")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["guardrail_type"] == "schema"


def test_freshness_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify freshness rule rows are loaded and enforced."""
    from fabricops_kit.pipeline.guardrails_shared import freshness_check_core

    df = spark_session.createDataFrame([("2026-06-14",)], "business_date string")
    rules = [
        _rule(
            guardrail_type="freshness",
            rule_type="max_lag_days",
            rule_parameters_json=json.dumps({"freshness_column": "business_date", "max_lag_days": 2}),
        )
    ]

    result = freshness_check_core(df, rules, dataset_name="sales", table_name="orders", reference_date="2026-06-15")

    assert result["status"] == "passed"
    assert result["guardrail_type"] == "freshness"


def test_profile_behavior_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify profile behavior rule rows are loaded and enforced."""
    from fabricops_kit.pipeline.guardrails_shared import enforce_profile_behavior

    df = spark_session.createDataFrame([(1, "2026-06-14")], "order_id int, business_date string")
    rules = [
        _rule(
            guardrail_type="profile_behavior",
            rule_type="static_data",
            rule_parameters_json=json.dumps({}),
        )
    ]

    result = enforce_profile_behavior(
        spark_session,
        df,
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="target",
        run_id="run-1",
        rules_df=rules,
        catalogue_df=[],
        write_results=False,
    )

    assert result["status"] == "baseline_created"
    assert result["guardrail_type"] == "profile_behavior"
    assert result["rule_type"] == "static_data"


def test_dq_rules_from_guardrail_metadata_are_loaded_and_enforced(spark_session, monkeypatch):
    """Verify DQ rule rows are loaded and enforced."""
    df = spark_session.createDataFrame([(1,), (None,)], "order_id int")
    rules_df = spark_session.createDataFrame([
        _rule(
            rule_key="dq-rule",
            rule_id="orders.order_id.null_rate_below",
            guardrail_type="dq",
            rule_type="null_rate_below",
            column_name="order_id",
            rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0}),
            severity="error",
        )
    ])
    monkeypatch.setattr(dq_runtime, "_read_guardrail_rule_metadata", lambda *args, **kwargs: rules_df)

    result = dq_runtime.run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session, write_results=False)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["checks"][0]["rule_id"] == "orders.order_id.null_rate_below"


def test_bypass_warning_is_added_for_schema_freshness_profile_and_dq(spark_session, monkeypatch):
    """Verify active-pending-review rules use standard runtime warning metadata."""
    from fabricops_kit.pipeline.guardrails_shared import freshness_check_core, enforce_profile_behavior, schema_check_core

    warning = "Rule is active through approval bypass and requires governance post-review."
    schema_df = spark_session.createDataFrame([(1,)], "order_id int")
    bypass_base = {"review_status": "active_pending_governance_review"}

    schema = schema_check_core(
        schema_df,
        [_rule(**bypass_base, rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}}))],
        dataset_name="sales",
        table_name="orders",
    )
    freshness = freshness_check_core(
        spark_session.createDataFrame([("2026-06-14",)], "business_date string"),
        [_rule(**bypass_base, guardrail_type="freshness", rule_type="max_lag_days", rule_parameters_json=json.dumps({"freshness_column": "business_date", "max_lag_days": 2}))],
        dataset_name="sales",
        table_name="orders",
        reference_date="2026-06-15",
    )
    profile = enforce_profile_behavior(
        spark_session,
        schema_df,
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="target",
        run_id="run-1",
        rules_df=[_rule(**bypass_base, guardrail_type="profile_behavior", rule_type="static_data")],
        catalogue_df=[],
        write_results=False,
    )

    dq_rules_df = spark_session.createDataFrame([
        _rule(**bypass_base, rule_key="dq-bypass", rule_id="orders.order_id.null_rate_below", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0}))
    ])
    monkeypatch.setattr(dq_runtime, "_read_guardrail_rule_metadata", lambda *args, **kwargs: dq_rules_df)
    dq = dq_runtime.run_active_dq_guardrail(schema_df, object(), "dev", "sales", "orders", spark_session=spark_session, write_results=False)

    for result in (schema, freshness, profile, dq):
        assert result["can_continue"] is True
        assert warning in result.get("reason", result.get("message", "")) or result.get("bypass_warning") == warning


def test_table_governance_policy_records_mark_governed_and_ungoverned():
    """Verify 03 governance helper records can mark table policy state."""
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key"}
    governed = governance_review.mark_table_governed(state, actor="steward@example.com", reason="critical table")
    ungoverned = governance_review.mark_table_ungoverned(state, actor="steward@example.com", reason="sandbox table")

    assert governed["governance_mode"] == "governed"
    assert governed["approval_policy"] == "approval_required_with_bypass"
    assert governed["approval_bypass_allowed"] is True
    assert ungoverned["governance_mode"] == "ungoverned"
    assert ungoverned["approval_policy"] == "no_approval_required"


def test_governance_can_approve_or_reject_active_pending_rule():
    """Verify 03 governance can approve or reject active-pending-review rules."""
    active_pending = {"rule_key": "rule", "review_status": "active_pending_governance_review", "activation_state": "active", "is_active": True, "requires_post_review": True}

    approved = governance_review.apply_governance_rule_action(active_pending, "approve", actor="steward@example.com")
    rejected = governance_review.apply_governance_rule_action(active_pending, "reject", actor="steward@example.com")

    assert approved["review_status"] == "governance_approved"
    assert approved["requires_post_review"] is False
    assert rejected["review_status"] == "rejected_by_governance"
    assert rejected["is_active"] is False






def test_dq_widget_batch_and_individual_actions_create_required_lifecycles(monkeypatch):
    """Verify DQ authoring creates draft, submit, and apply-now lifecycle rows."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "columns": ["order_id", "amount"], "catalogue_profile_rows": [{"column_name": "order_id"}], "existing_rules": [], "governance_mode": "governed", "approval_policy": "approval_required_with_bypass", "approval_bypass_allowed": True}
    def build(action):
        return governance_review._dq_records_from_selection(
            state, rule_type="null_rate_below", selected_columns=["order_id"], parameters={"max_null_percent": 0}, action=action
        )

    batch_draft = individual_draft = build("draft")
    batch_submitted = individual_submitted = build("submit")
    batch_applied = individual_applied = build("apply_now")

    for records in (batch_draft, individual_draft):
        assert {record["activation_state"] for record in records} == {"inactive"}
        assert {record["is_active"] for record in records} == {False}
        assert {record["review_state"] for record in records} == {"draft"}
        assert {record["review_status"] for record in records} == {"draft"}
        assert {record["requires_governance_review"] for record in records} == {False}
    for records in (batch_submitted, individual_submitted):
        assert {record["activation_state"] for record in records} == {"pending"}
        assert {record["is_active"] for record in records} == {False}
        assert {record["review_state"] for record in records} == {"pending_governance_review"}
        assert {record["review_status"] for record in records} == {"pending_governance_review"}
        assert {record["requires_governance_review"] for record in records} == {True}
    for records in (batch_applied, individual_applied):
        assert {record["activation_state"] for record in records} == {"active"}
        assert {record["is_active"] for record in records} == {True}
        assert {record["review_state"] for record in records} == {"active_pending_governance_review"}
        assert {record["review_status"] for record in records} == {"active_pending_governance_review"}
        assert {record["requires_governance_review"] for record in records} == {True}
        assert {record["activation_reason"] for record in records} == {"engineering_apply_now"}


def test_governance_review_widget_actions(monkeypatch):
    """Verify governance review widget exposes policy and rule actions."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit.widgets import widget_review_guardrail_governance

    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "existing_rules": [_rule(review_status="pending_governance_review", is_active=False)]}
    widget = widget_review_guardrail_governance(state)
    approved = widget["save_rule_action"]("approve")
    rejected = widget["save_rule_action"]("reject")
    superseded = widget["save_rule_action"]("supersede")

    assert approved["review_status"] == "governance_approved"
    assert rejected["review_status"] == "rejected_by_governance"
    assert superseded["review_status"] == "superseded"


def test_review_widget_does_not_write_separate_policy_table(monkeypatch):
    """Verify review widget actions write rule rows, not a separate policy table."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit.widgets import shared as governance_review
    from fabricops_kit import widgets
    from fabricops_kit.widgets import shared as widget_shared

    writes = []

    class Spark:
        def createDataFrame(self, records):
            return records

    monkeypatch.setattr(widget_shared, "write_lakehouse_table_core", lambda frame, table, *, target, context, **kwargs: writes.append(table))
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "existing_rules": [_rule(review_status="pending_governance_review", is_active=False)]}
    widget = widgets.widget_review_guardrail_governance(state, context={"config": object(), "env": "dev"}, spark_session=Spark())

    widget["save_rule_action"]("approve")

    assert writes == [governance_review.GUARDRAIL_TABLE]
    assert governance_review.CATALOGUE_TABLE not in writes
    assert governance_review.GUARDRAIL_RESULTS_TABLE not in writes

def test_guardrail_rule_active_statuses_are_strict_for_schema_rules():
    """Verify only new active rule statuses are enforced for schema rules."""
    from fabricops_kit.pipeline.guardrails_shared import schema_check_core

    class Frame:
        dtypes = [("order_id", "int")]
        columns = ["order_id"]

    active_statuses = {"self_approved", "governance_approved", "active_pending_governance_review"}
    for status in active_statuses:
        result = schema_check_core(
            Frame(),
            [_rule(guardrail_type="schema", rule_type="strict", review_status=status, rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}}))],
            dataset_name="sales",
            table_name="orders",
        )
        assert result["guardrail_type"] == "schema"
        assert result["rule_key"] == "rule-key"

    for inactive_rule in [
        _rule(guardrail_type="schema", rule_type="strict", review_status="approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}})),
        _rule(guardrail_type="schema", rule_type="strict", rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}}), review_status=""),
        {key: value for key, value in _rule(guardrail_type="schema", rule_type="strict", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}})).items() if key != "is_active"},
        _rule(guardrail_type="schema", rule_type="strict", review_status="self_approved", dataset_name="", rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}})),
    ]:
        result = schema_check_core(Frame(), [inactive_rule], dataset_name="sales", table_name="orders")
        assert result["preset"] == "monitor_only"
        assert "rule_key" not in result


def test_dq_loader_excludes_ambiguous_and_missing_lifecycle_fields(spark_session):
    """Verify DQ loading excludes approved, missing status, missing active, and blank dataset rows."""
    from fabricops_kit.pipeline.guardrails_shared import _load_active_dq_rules

    rows = [
        _rule(rule_key="self", rule_id="self", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
        _rule(rule_key="gov", rule_id="gov", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", review_status="governance_approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
        _rule(rule_key="bypass", rule_id="bypass", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", review_status="active_pending_governance_review", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
        _rule(rule_key="old", rule_id="old", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", review_status="approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
        _rule(rule_key="blank_dataset", rule_id="blank_dataset", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", dataset_name="", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
        _rule(rule_key="missing_status", rule_id="missing_status", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
        _rule(rule_key="missing_active", rule_id="missing_active", guardrail_type="dq", rule_type="null_rate_below", column_name="order_id", severity="error", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"], "max_null_percent": 0})),
    ]
    rows[-2].pop("review_status")
    rows[-1].pop("is_active")
    frame = spark_session.createDataFrame(rows)

    loaded = _load_active_dq_rules(frame, table_name="orders", env="dev", dataset_name="sales")

    assert {rule["rule_id"] for rule in loaded} == {"self", "gov", "bypass"}


def test_new_authoring_lifecycle_draft_submit_apply_now_and_ungoverned():
    """Verify 02_pipeline authoring cannot create formal review decisions."""
    ungoverned = governance_review.guardrail_authoring_status({"governance_mode": "ungoverned"})
    draft = governance_review.guardrail_authoring_status({"governance_mode": "governed"}, action="draft")
    submit = governance_review.guardrail_authoring_status({"governance_mode": "governed"}, action="submit")
    apply_now = governance_review.guardrail_authoring_status({"governance_mode": "governed"}, action="apply_now")

    assert ungoverned["activation_state"] == "active"
    assert ungoverned["requires_governance_review"] is False
    assert draft["activation_state"] == "inactive"
    assert draft["review_state"] == "draft"
    assert submit["activation_state"] == "pending"
    assert submit["review_state"] == "pending_governance_review"
    assert apply_now["activation_state"] == "active"
    assert apply_now["review_state"] == "active_pending_governance_review"
    assert apply_now["activation_reason"] == "engineering_apply_now"
    assert "governance_approved" not in {draft["review_state"], submit["review_state"], apply_now["review_state"]}


def test_formal_review_context_and_lifecycles():
    """Verify formal review actions are Governance-only and produce new lifecycle states."""
    pending = {"rule_key": "r1", "rule_id": "r1", "activation_state": "pending", "review_state": "pending_governance_review", "is_active": False}
    active_pending = {**pending, "activation_state": "active", "review_state": "active_pending_governance_review", "is_active": True}

    try:
        governance_review.apply_governance_rule_action(pending, "approve", source_notebook_type="02_pipeline")
    except PermissionError as exc:
        assert "01_governance" in str(exc)
    else:
        raise AssertionError("02_pipeline formal review was not blocked")

    approved = governance_review.apply_governance_rule_action(pending, "approve_and_activate")
    rejected = governance_review.apply_governance_rule_action(active_pending, "reject")
    deactivated = governance_review.apply_governance_rule_action({**pending, "review_state": "governance_approved", "activation_state": "active", "is_active": True}, "deactivate")
    replaced = governance_review.apply_governance_rule_action(active_pending, "replace", replacement={"rule_id": "r2", "rule_key": "r2"})

    assert approved["activation_state"] == "active"
    assert approved["review_state"] == "governance_approved"
    assert rejected["activation_state"] == "inactive"
    assert rejected["review_state"] == "rejected_by_governance"
    assert deactivated["review_state"] == "inactive"
    assert len(replaced) == 2
    assert replaced[0]["review_state"] == "superseded"
    assert replaced[0]["superseded_by_record_id"] == "r2"
    assert replaced[1]["review_state"] == "governance_approved"
    assert replaced[1]["supersedes_record_id"] == "r1"


def test_authoring_widgets_stamp_engineering_and_governance_sources(monkeypatch):
    """Verify authoring widgets stamp notebook type and creator role by context."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "columns": ["order_id"], "catalogue_profile_rows": [{"column_name": "order_id", "data_type": "int"}], "existing_rules": [], "governance_mode": "governed", "approval_policy": "approval_required"}

    engineering = governance_review._dq_records_from_selection(
        state, rule_type="null_rate_below", selected_columns=["order_id"], parameters={"max_null_percent": 0}, action="submit"
    )[0]
    governance = governance_review._dq_records_from_selection(
        state, rule_type="null_rate_below", selected_columns=["order_id"], parameters={"max_null_percent": 0}, action="submit",
        source_notebook_type="01_governance", created_by_role="governance"
    )[0]

    assert engineering["source_notebook_type"] == "02_pipeline"
    assert engineering["created_by_role"] == "engineering"
    assert governance["source_notebook_type"] == "01_governance"
    assert governance["created_by_role"] == "governance"


def test_review_guardrail_governance_actions_and_replace_mapping(monkeypatch):
    """Verify the canonical governance review widget records and uses replace actions."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "table-key",
        "existing_rules": [
            _rule(rule_id="pending", rule_key="pending", activation_state="pending", is_active=False, review_state="pending_governance_review", review_status="pending_governance_review"),
            _rule(rule_id="active", rule_key="active", activation_state="active", is_active=True, review_state="governance_approved", review_status="governance_approved"),
            _rule(rule_id="old", rule_key="old", activation_state="inactive", is_active=False, review_state="superseded", review_status="superseded"),
        ],
    }
    widget = widget_review_guardrail_governance(state)

    assert widget["controls"]["replacement_key"].description == "Supersedes/replacement"
    replaced = widget["save_record_action"]("replace")
    assert len(replaced) == 2
    assert replaced[0]["review_state"] == "superseded"
    assert replaced[1]["review_state"] == "governance_approved"
