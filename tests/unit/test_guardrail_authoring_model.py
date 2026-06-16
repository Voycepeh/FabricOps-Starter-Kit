"""Tests for governed guardrail authoring state helpers."""

import json

import fabricops_kit.governance_review as governance_review
from fabricops_kit.governance_review import (
    CATALOGUE_TABLE,
    GOVERNANCE_REVIEWS_TABLE,
    GUARDRAIL_RESULTS_TABLE,
    GUARDRAIL_RULES_TABLE,
    _get_governance_metadata_schemas,
    widget_author_dq_rules,
    widget_author_schema_freshness_profile_rules,
)


def _install_fake_notebook_widgets(monkeypatch):
    """Install minimal ipywidgets/IPython fakes for widget unit tests."""
    import sys
    import types

    class Widget:
        def __init__(self, *args, **kwargs):
            options = kwargs.get("options", [])
            self.options = options
            if "value" in kwargs:
                self.value = kwargs["value"]
            elif options:
                first = options[0]
                self.value = first[1] if isinstance(first, tuple) and len(first) == 2 else first
            else:
                self.value = ""
            self.description = kwargs.get("description", "")
            self.layout = kwargs.get("layout") or types.SimpleNamespace(display="")
            self.button_style = kwargs.get("button_style", "")
            self.disabled = kwargs.get("disabled", False)
            self.rows = kwargs.get("rows", None)

        def observe(self, callback, names=None):
            self._observer = callback

        def on_click(self, callback):
            self._click = callback

    class Box(Widget):
        def __init__(self, children=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.children = children or []

    fake_widgets = types.SimpleNamespace(
        Dropdown=Widget,
        SelectMultiple=Widget,
        Textarea=Widget,
        Text=Widget,
        BoundedIntText=Widget,
        ToggleButtons=Widget,
        Combobox=Widget,
        Button=Widget,
        HTML=Widget,
        VBox=Box,
        HBox=Box,
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    fake_display = types.SimpleNamespace(display=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(display=fake_display))
    monkeypatch.setattr("importlib.import_module", lambda name: fake_widgets if name == "ipywidgets" else __import__(name))


def test_metadata_ownership_schema_separates_catalogue_rules_and_results():
    """Verify catalogue, rule, result, and governance policy fields stay separated."""
    schemas = _get_governance_metadata_schemas()
    catalogue_fields = set(schemas[CATALOGUE_TABLE].fieldNames())
    rule_fields = set(schemas[GUARDRAIL_RULES_TABLE].fieldNames())
    result_fields = set(schemas[GUARDRAIL_RESULTS_TABLE].fieldNames())
    review_fields = set(schemas[GOVERNANCE_REVIEWS_TABLE].fieldNames())

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
    assert {"governance_mode", "approval_policy", "approval_bypass_allowed", "effective_from", "effective_to"}.issubset(review_fields)


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
    assert governed["review_status"] == "proposed"
    assert bypassed["is_active"] is True
    assert bypassed["review_status"] == "bypass_active_pending_review"
    assert bypassed["requires_post_review"] is True
    assert bypassed["bypass_reason"] == "urgent fix"


def test_governance_rule_actions_approve_reject_and_supersede():
    """Verify governance can approve, reject, and supersede append-only rule rows."""
    rule = {"rule_key": "old", "review_status": "proposed", "is_active": False}
    assert governance_review.apply_governance_rule_action(rule, "approve", actor="steward@example.com")["review_status"] == "governance_approved"
    assert governance_review.apply_governance_rule_action(rule, "reject")["is_active"] is False
    superseded = governance_review.apply_governance_rule_action(rule, "supersede", superseded_by_rule_key="new")
    assert superseded["review_status"] == "superseded"
    assert superseded["superseded_by_rule_key"] == "new"


def test_authoring_widgets_write_rule_intent_records_only(monkeypatch):
    """Verify authoring widgets return guardrail-rule rows instead of catalogue or result rows."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "table-key",
        "columns": ["order_id"],
        "catalogue_profile_rows": [{"column_name": "order_id", "data_type": "string"}],
        "governance_mode": "ungoverned",
        "approval_policy": "no_approval_required",
    }
    sfp_widget = widget_author_schema_freshness_profile_rules(state)
    dq_widget = widget_author_dq_rules(state, selected_columns=["order_id"])
    records = sfp_widget["build_records"]() + dq_widget["build_batch_records"]()
    assert {record["guardrail_type"] for record in records} == {"schema", "freshness", "profile_behavior", "dq"}
    assert all("rule_parameters_json" in record for record in records)
    assert all(json.loads(record["rule_parameters_json"]) is not None for record in records)
    assert all("result_id" not in record for record in records)
    assert all("profile_payload_json" not in record for record in records)


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
    from fabricops_kit.guardrails import validate_schema_rule

    df = spark_session.createDataFrame([(1, "ok", "extra")], "order_id int, status string, extra string")
    rules = [_rule(rule_parameters_json=json.dumps({"columns": ["order_id", "status"], "data_types": {"order_id": "int", "status": "string"}}))]

    result = validate_schema_rule(df, rules, dataset_name="sales", table_name="orders")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["guardrail_type"] == "schema"


def test_freshness_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify freshness rule rows are loaded and enforced."""
    from fabricops_kit.guardrails import enforce_freshness_rule

    df = spark_session.createDataFrame([("2026-06-14",)], "business_date string")
    rules = [
        _rule(
            guardrail_type="freshness",
            rule_type="max_lag_days",
            rule_parameters_json=json.dumps({"freshness_column": "business_date", "max_lag_days": 2}),
        )
    ]

    result = enforce_freshness_rule(df, rules, dataset_name="sales", table_name="orders", reference_date="2026-06-15")

    assert result["status"] == "passed"
    assert result["guardrail_type"] == "freshness"


def test_profile_behavior_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify profile behavior rule rows are loaded and enforced."""
    from fabricops_kit.guardrails import enforce_profile_behavior

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
    from fabricops_kit import governance_review

    df = spark_session.createDataFrame([(1,), (None,)], "order_id int")
    rules_df = spark_session.createDataFrame([
        _rule(
            rule_key="dq-rule",
            rule_id="orders.order_id.not_null",
            guardrail_type="dq",
            rule_type="not_null",
            column_name="order_id",
            rule_parameters_json=json.dumps({"columns": ["order_id"]}),
            severity="error",
        )
    ])
    monkeypatch.setattr(governance_review, "_read_guardrail_rule_metadata", lambda *args, **kwargs: rules_df)

    result = governance_review.enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session, write_results=False)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["checks"][0]["rule_id"] == "orders.order_id.not_null"


def test_bypass_warning_is_added_for_schema_freshness_profile_and_dq(spark_session, monkeypatch):
    """Verify bypass-active rules are enforced with post-review warning metadata."""
    from fabricops_kit import governance_review
    from fabricops_kit.guardrails import enforce_freshness_rule, enforce_profile_behavior, validate_schema_rule

    warning = "Rule is active through approval bypass and requires governance post-review."
    schema_df = spark_session.createDataFrame([(1,)], "order_id int")
    bypass_base = {"review_status": "bypass_active_pending_review"}

    schema = validate_schema_rule(
        schema_df,
        [_rule(**bypass_base, rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}}))],
        dataset_name="sales",
        table_name="orders",
    )
    freshness = enforce_freshness_rule(
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
        _rule(**bypass_base, rule_key="dq-bypass", rule_id="orders.order_id.not_null", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", rule_parameters_json=json.dumps({"columns": ["order_id"]}))
    ])
    monkeypatch.setattr(governance_review, "_read_guardrail_rule_metadata", lambda *args, **kwargs: dq_rules_df)
    dq = governance_review.enforce_dq_rules(schema_df, object(), "dev", "sales", "orders", spark_session=spark_session, write_results=False)

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


def test_governance_can_approve_or_reject_bypassed_active_rule():
    """Verify 03 governance can approve or reject bypass-active rules."""
    bypassed = {"rule_key": "rule", "review_status": "bypass_active_pending_review", "is_active": True, "requires_post_review": True}

    approved = governance_review.apply_governance_rule_action(bypassed, "approve", actor="steward@example.com")
    rejected = governance_review.apply_governance_rule_action(bypassed, "reject", actor="steward@example.com")

    assert approved["review_status"] == "governance_approved"
    assert approved["requires_post_review"] is False
    assert rejected["review_status"] == "rejected"
    assert rejected["is_active"] is False


def test_schema_widget_prepopulates_and_validates_user_inputs(monkeypatch):
    """Verify schema/freshness/profile widget prepopulates and validates selections."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "table-key",
        "columns": ["order_id", "business_date"],
        "catalogue_profile_rows": [{"column_name": "order_id", "data_type": "int"}, {"column_name": "business_date", "data_type": "string"}],
        "existing_rules": [
            _rule(guardrail_type="schema", rule_type="strict", rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}})),
            _rule(guardrail_type="freshness", rule_type="max_lag_days", rule_parameters_json=json.dumps({"freshness_column": "business_date", "max_lag_days": 3})),
            _rule(guardrail_type="profile_behavior", rule_type="changing_data", rule_parameters_json=json.dumps({"watermark_column": "business_date"})),
        ],
        "governance_mode": "governed",
        "approval_policy": "approval_required_with_bypass",
        "approval_bypass_allowed": True,
    }
    widget = widget_author_schema_freshness_profile_rules(state)

    assert widget["controls"]["schema_mode"].value == "strict"
    assert widget["controls"]["freshness_column"].value == "business_date"
    assert widget["controls"]["max_lag"].value == 3
    assert widget["controls"]["watermark_column"].value == "business_date"
    widget["controls"]["watermark_column"].value = ""
    try:
        widget["build_records"]()
    except ValueError as exc:
        assert "watermark_column" in str(exc)
    else:
        raise AssertionError("changing_data without watermark_column should fail")


def test_governed_bypass_widget_save_requires_reason(monkeypatch):
    """Verify governed bypass widget save requires a reason and creates bypass rows."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "columns": ["order_id"], "catalogue_profile_rows": [{"column_name": "order_id", "data_type": "int"}], "existing_rules": [], "governance_mode": "governed", "approval_policy": "approval_required_with_bypass", "approval_bypass_allowed": True}
    widget = widget_author_schema_freshness_profile_rules(state)

    try:
        widget["build_records"](use_bypass=True)
    except ValueError as exc:
        assert "Bypass reason" in str(exc)
    else:
        raise AssertionError("bypass without reason should fail")
    widget["controls"]["bypass_reason"].value = "urgent production fix"
    records = widget["build_records"](use_bypass=True)
    assert all(record["review_status"] == "bypass_active_pending_review" for record in records)
    assert all(record["approval_bypassed"] is True for record in records)


def test_dq_widget_manual_individual_clear_and_ai_drafts(monkeypatch):
    """Verify DQ widget supports batch, individual, clear, and AI draft flows."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit import governance_review

    monkeypatch.setattr(governance_review, "_draft_dq_rules", lambda **kwargs: [{"rule_id": "ai", "rule_type": "not_null", "columns": ["order_id"]}])
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "columns": ["order_id", "amount"], "catalogue_profile_rows": [{"column_name": "order_id"}], "existing_rules": [], "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "approval_bypass_allowed": False}
    widget = widget_author_dq_rules(state, selected_columns=["order_id"], dq_authoring_mode="ai_suggest")

    batch = widget["build_batch_records"]()
    individual = widget["build_individual_record"]()
    cleared = widget["build_individual_record"](action_type="superseded")
    assert len(batch) == 1
    assert individual[0]["column_name"] == "order_id"
    assert cleared[0]["is_active"] is False
    assert widget["suggest_ai"]() == [{"rule_id": "ai", "rule_type": "not_null", "columns": ["order_id"], "review_status": "draft", "is_active": False}]
    approved = widget["approve_ai"]()
    assert approved[0]["guardrail_type"] == "dq"
    widget["reject_ai"]()
    assert widget["suggestions"] == []


def test_governance_review_widget_actions(monkeypatch):
    """Verify governance review widget exposes policy and rule actions."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit.governance_review import widget_review_guardrail_governance

    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "existing_rules": [_rule(review_status="proposed", is_active=False)]}
    widget = widget_review_guardrail_governance(state)
    governed = widget["mark_governed"]()
    ungoverned = widget["mark_ungoverned"]()
    approved = widget["save_rule_action"]("approve")
    rejected = widget["save_rule_action"]("reject")
    superseded = widget["save_rule_action"]("supersede")

    assert governed["governance_mode"] == "governed"
    assert ungoverned["governance_mode"] == "ungoverned"
    assert approved["review_status"] == "governance_approved"
    assert rejected["review_status"] == "rejected"
    assert superseded["review_status"] == "superseded"


def test_target_selector_returns_handover_state_with_policy_and_rules(monkeypatch):
    """Verify target selector reads catalogue, rules, and governance policy."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit import governance_review

    catalogue = [{"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "profile_run_id": "profile-1", "profile_stage": "target", "column_name": "order_id", "data_type": "int"}]
    rules = [_rule(metadata_table_key="table-key")]
    reviews = [{"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "governance_mode": "governed", "approval_policy": "approval_required_with_bypass", "governance_status": "active", "approval_bypass_allowed": True, "effective_from": "2026-01-01T00:00:00Z"}]

    def fake_read(config, env, table_name, *, spark_session):
        return {governance_review.CATALOGUE_TABLE: catalogue, governance_review.GUARDRAIL_RULES_TABLE: rules, governance_review.GOVERNANCE_REVIEWS_TABLE: reviews}[table_name]

    monkeypatch.setattr(governance_review, "_read_metadata_table_or_empty", fake_read)
    state = governance_review.widget_select_guardrail_target(object(), "dev", spark_session=object())

    assert state["environment_name"] == "dev"
    assert state["columns"] == ["order_id"]
    assert state["existing_rules"] == rules
    assert state["governance_mode"] == "governed"
    assert state["approval_bypass_allowed"] is True
    assert len(state["_controls"]["target"].options) == 1


def test_schema_widget_freshness_lag_rejects_negative(monkeypatch):
    """Verify freshness max lag rejects negative values when enforce mode is active."""
    _install_fake_notebook_widgets(monkeypatch)
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "columns": ["business_date"], "catalogue_profile_rows": [{"column_name": "business_date", "data_type": "string"}], "existing_rules": [], "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "approval_bypass_allowed": False}
    widget = widget_author_schema_freshness_profile_rules(state)
    widget["controls"]["freshness_mode"].value = "enforce"
    widget["controls"]["freshness_column"].value = "business_date"
    widget["controls"]["max_lag"].value = -1

    try:
        widget["build_records"]()
    except ValueError as exc:
        assert "max_lag_days" in str(exc)
    else:
        raise AssertionError("negative max lag should fail")


def test_authoring_widget_save_writes_only_guardrail_rules(monkeypatch):
    """Verify authoring widget save writes only METADATA_GUARDRAIL_RULES."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit import governance_review

    writes = []

    class Spark:
        def createDataFrame(self, records):
            return records

    monkeypatch.setattr(governance_review, "write_lakehouse_table", lambda frame, config, env, target, table, **kwargs: writes.append(table))
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "columns": ["order_id"], "catalogue_profile_rows": [{"column_name": "order_id", "data_type": "int"}], "existing_rules": [], "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "approval_bypass_allowed": False}
    widget = widget_author_schema_freshness_profile_rules(state, config=object(), env="dev", spark_session=Spark())

    widget["save"]()

    assert writes == [governance_review.GUARDRAIL_RULES_TABLE]
    assert governance_review.CATALOGUE_TABLE not in writes
    assert governance_review.GUARDRAIL_RESULTS_TABLE not in writes


def test_governance_policy_widget_writes_only_governance_reviews(monkeypatch):
    """Verify governance policy widget saves only METADATA_GOVERNANCE_REVIEWS."""
    _install_fake_notebook_widgets(monkeypatch)
    from fabricops_kit import governance_review

    writes = []

    class Spark:
        def createDataFrame(self, records):
            return records

    monkeypatch.setattr(governance_review, "write_lakehouse_table", lambda frame, config, env, target, table, **kwargs: writes.append(table))
    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key", "governance_mode": "ungoverned", "approval_policy": "no_approval_required", "existing_rules": []}
    widget = governance_review.widget_review_guardrail_governance(state, config=object(), env="dev", spark_session=Spark())

    widget["mark_governed"]()

    assert writes == [governance_review.GOVERNANCE_REVIEWS_TABLE]
    assert governance_review.CATALOGUE_TABLE not in writes
    assert governance_review.GUARDRAIL_RESULTS_TABLE not in writes


def test_guardrail_rule_active_statuses_are_strict_for_schema_rules():
    """Verify only new active rule statuses are enforced for schema rules."""
    from fabricops_kit.guardrails import validate_schema_rule

    class Frame:
        dtypes = [("order_id", "int")]
        columns = ["order_id"]

    active_statuses = {"self_approved", "governance_approved", "bypass_active_pending_review"}
    for status in active_statuses:
        result = validate_schema_rule(
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
        result = validate_schema_rule(Frame(), [inactive_rule], dataset_name="sales", table_name="orders")
        assert result["preset"] == "monitor_only"
        assert "rule_key" not in result


def test_dq_loader_excludes_ambiguous_and_missing_lifecycle_fields(spark_session):
    """Verify DQ loading excludes approved, missing status, missing active, and blank dataset rows."""
    from fabricops_kit.governance_review import _load_active_dq_rules

    rows = [
        _rule(rule_key="self", rule_id="self", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
        _rule(rule_key="gov", rule_id="gov", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", review_status="governance_approved", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
        _rule(rule_key="bypass", rule_id="bypass", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", review_status="bypass_active_pending_review", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
        _rule(rule_key="old", rule_id="old", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", review_status="approved", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
        _rule(rule_key="blank_dataset", rule_id="blank_dataset", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", dataset_name="", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
        _rule(rule_key="missing_status", rule_id="missing_status", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
        _rule(rule_key="missing_active", rule_id="missing_active", guardrail_type="dq", rule_type="not_null", column_name="order_id", severity="error", review_status="self_approved", rule_parameters_json=json.dumps({"columns": ["order_id"]})),
    ]
    rows[-2].pop("review_status")
    rows[-1].pop("is_active")
    frame = spark_session.createDataFrame(rows)

    loaded = _load_active_dq_rules(frame, table_name="orders", env_name="dev", dataset_name="sales")

    assert {rule["rule_id"] for rule in loaded} == {"self", "gov", "bypass"}
