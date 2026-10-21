"""Regression coverage for explicit participant selection and exact payload inspection."""

import importlib
import json

import pytest

module = importlib.import_module("fabricops_kit.pipeline.setup_pipeline")


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


def _render(monkeypatch, rows, *, interactive=False, metadata_error=None, lineage_state="empty", targets=None, testing_writes=False):
    monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline.shared"), "persist_pipeline_run", lambda *a, **kw: None)
    context = {"config": object(), "env": "canary-east", "notebook_id": "notebook-1"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context_obj["config"], "canary-east", context_obj))
    context_obj = context
    monkeypatch.setattr(module, "get_spark_session", lambda spark=None: object())
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *a: "metadata")
    builder = importlib.import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(builder, "resolve_physical_table_identity", lambda c, e, **kw: {
        **kw, "table_id": kw["table_name"], "store_kind": "lakehouse"})
    monkeypatch.setattr(builder, "pipeline_physical_bindings", lambda identities, **kw: {})
    reads = []
    def read(name, **kw):
        reads.append(name)
        if name == "METADATA_DATA_LINEAGE" and lineage_state == "missing":
            raise RuntimeError("Lineage table does not exist")
        if metadata_error:
            raise metadata_error
        return type("Frame", (), {"collect": lambda self: rows})()
    monkeypatch.setattr(module, "read_lakehouse_table", read)
    if interactive:
        from IPython import display as ip
        monkeypatch.setattr(ip, "display", lambda *a: None)
    if not interactive:
        monkeypatch.setattr(importlib.import_module("fabricops_kit.widgets.shared"), "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    state = module.setup_pipeline(
        sources=[{"store": "Bronze", "schema": "demo", "table_name": "source"}],
        targets=targets if targets is not None else [{"store": "Silver", "schema": "demo", "table_name": "target"}], context=context, interactive=True, pipeline_id="example", testing_writes=testing_writes,
    )
    return context, state, reads


@pytest.mark.parametrize("lineage_state", ["empty", "missing"])
def test_bootstrap_never_requires_lineage_and_no_contract_is_explicit(monkeypatch, lineage_state):
    """An empty contract store does not implicitly choose No Contract or read Lineage."""
    context, state, reads = _render(monkeypatch, [], lineage_state=lineage_state)
    assert state["execution_mode"] == "testing"
    assert callable(state["refresh"])
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
    with pytest.raises(ValueError, match="Testing only"):
        state["set_mode"]("live")
    assert "pipeline-testing" in state["widget"]._dom_classes
    assert state["_controls"]["source"]["inspector"].value == before


def test_live_rejects_inactive_substitution(monkeypatch):
    """Testing candidates stay selectable; Live only accepts active frozen versions."""
    _, state, _ = _render(monkeypatch, [_row(1, active=True), _row(2)])
    state["select_contract"]("source", "contract-source", 2)
    with pytest.raises(ValueError, match="Testing only"):
        state["set_mode"]("live")
    assert state["tables"]["source"]["selected"]["contract_version"] == 2


@pytest.mark.parametrize("corruption", ["json", "identity", "duplicate"])
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


def test_public_imports_do_not_require_optional_notebook_packages():
    """Package imports and headless APIs work without IPython or ipywidgets."""
    import subprocess
    import sys

    code = '''
import builtins
original_import = builtins.__import__
def without_notebook_packages(name, *args, **kwargs):
    if name.split('.')[0] in {'IPython', 'ipywidgets'}:
        raise ModuleNotFoundError(name)
    return original_import(name, *args, **kwargs)
builtins.__import__ = without_notebook_packages
import fabricops_kit as kit
import sys
assert "fabricops_kit.widgets" not in sys.modules
for name in kit.__all__:
    getattr(kit, name)
assert callable(kit.setup_pipeline)
assert not hasattr(kit, "create_pipeline_execution_plan")
assert not hasattr(kit, "widget_select_data_contract")
'''
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)


def test_inspector_shows_only_exact_contract_results_and_escapes_details():
    """Saved states and matching evaluations remain distinct expandable sections."""
    row = _row(2)
    result = {"table_id": "source", "contract_id": "contract-source", "contract_version": 2,
              "guardrail_type": "data_quality", "guardrail_rule_id": "rule-2", "execution_type": "testing",
              "status": "warning", "can_continue": True, "result_payload_json": '<script>unsafe</script>'}
    rendered = module._inspector(row, ["source"], [result, {**result, "contract_version": 1}])
    assert "Execution results · 1" in rendered and "warning" in rendered and "testing" in rendered
    assert "&lt;script&gt;unsafe&lt;/script&gt;" in rendered and "<script>unsafe" not in rendered
    assert "2 checks · 1 inactive" in rendered and "decimal(18,4)" in rendered
    assert "Not executed in this plan" in module._inspector(row, ["target"])


def test_inspector_refresh_uses_built_plan_and_locks_selection(monkeypatch):
    """A built plan keeps its journal and rejects mode or contract changes."""
    from types import SimpleNamespace
    _, state, _ = _render(monkeypatch, [_row(active=True)], interactive=True)
    state["select_contract"]("source", "contract-source", 1)
    state["select_contract"]("target", no_contract=True)
    plan = SimpleNamespace(results=[])
    monkeypatch.setattr(module, "build_pipeline_execution_plan", lambda **kw: plan)
    assert state["build_plan"]() is plan
    plan.results.append({"table_id": "source", "contract_id": "contract-source", "contract_version": 1,
                         "guardrail_type": "schema", "status": "passed"})
    state["refresh"]()
    assert "Execution results · 1" in state["_controls"]["source"]["inspector"].value
    assert state["build_plan"]() is plan
    assert state["mode_control"].disabled
    assert all(controls["version"].disabled for controls in state["_controls"].values())
    with pytest.raises(RuntimeError, match="active execution plan"):
        state["set_mode"]("live")
    with pytest.raises(RuntimeError, match="active execution plan"):
        state["select_contract"]("source", "contract-source", 1)
    assert state["execution_plan"] is plan
    assert "Execution results · 1" in state["_controls"]["source"]["inspector"].value


def test_headless_uses_builder_without_loading_ui_or_listing_contracts(monkeypatch):
    """Scheduled selection reaches the same builder without notebook dependencies."""
    from unittest.mock import Mock

    sentinel = object()
    builder = Mock(return_value=sentinel)
    forbidden = Mock(side_effect=AssertionError("Interactive-only work reached"))
    monkeypatch.setattr(module, "build_pipeline_execution_plan", builder)
    monkeypatch.setattr(importlib.import_module("fabricops_kit.widgets.shared"), "require_ipywidgets", forbidden)
    monkeypatch.setattr(module, "read_lakehouse_table", forbidden)
    selections = {"source": {"contract_id": "contract-source", "contract_version": 2}}
    assert module.setup_pipeline(sources=[{"table_id": "source"}], targets=[], interactive=False,
                                  execution_mode="testing", selections=selections, pipeline_id="example") is sentinel
    builder.assert_called_once_with(execution_mode="testing", sources=[{"table_id": "source"}],
                                    targets=[], selections=selections, context=None, spark_session=None,
                                    pipeline_id="example", configuration=None, testing_writes=False)
    forbidden.assert_not_called()


@pytest.mark.parametrize("configuration", [{"execution_mode": "testing"}, {"execution_mode": "live"}])
def test_headless_missing_configuration_fails_before_metadata_access(monkeypatch, configuration):
    """Headless execution never infers mode or silently chooses contracts."""
    monkeypatch.setattr(module, "build_pipeline_execution_plan", lambda **kw: pytest.fail("Builder reached"))
    with pytest.raises(ValueError, match="requires"):
        module.setup_pipeline(sources=[], targets=[], interactive=False, **configuration)


def test_interactive_and_headless_share_identity_validation_and_plan_snapshots(monkeypatch):
    """Both paths produce identical frozen authority and isolated journals."""
    context, state, _ = _render(monkeypatch, [], interactive=True)
    builder = importlib.import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(builder, "resolve_fabric_context", lambda context=None: (
        context["config"], context["env"], context))
    for table_id in ("source", "target"):
        state["select_contract"](table_id, no_contract=True)
    plan = state["build_plan"]()
    choices = {"source": {"no_contract": True}, "target": {"no_contract": True}}
    scheduled = module.setup_pipeline(
        sources=[{"store": "Bronze", "schema": "demo", "table_name": "source"}],
        targets=[{"store": "Silver", "schema": "demo", "table_name": "target"}],
        interactive=False, execution_mode="testing", selections=choices, context=context, pipeline_id="example",
    )
    assert plan.participants_json == scheduled.participants_json
    assert plan.selections_json == scheduled.selections_json
    assert plan.contracts_json == scheduled.contracts_json
    assert plan.plan_id != scheduled.plan_id
    choices["source"]["no_contract"] = False
    assert json.loads(scheduled.selections_json)["source"] == {"no_contract": True}
    plan.results.append({"status": "passed"})
    assert not scheduled.results
    assert state["build_plan"]() is plan


@pytest.mark.parametrize("interactive", [True, False])
def test_participant_mismatch_rejected_in_both_paths(monkeypatch, interactive):
    """The interactive inspector cannot ignore a mismatched canonical table ID."""
    context, _, _ = _render(monkeypatch, [])
    builder = importlib.import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(builder, "resolve_fabric_context", lambda context=None: (
        context["config"], context["env"], context))
    with pytest.raises(ValueError, match="canonical table_id"):
        module.setup_pipeline(
            sources=[{"store": "Bronze", "schema": "demo", "table_name": "source", "table_id": "wrong"}],
            targets=[], interactive=interactive, execution_mode="testing",
            selections={"wrong": {"no_contract": True}}, context=context, pipeline_id="example",
        )


def test_obsolete_public_apis_and_modules_are_removed():
    """The breaking cleanup leaves no callable aliases or old owner modules."""
    import fabricops_kit as kit
    import fabricops_kit.pipeline as pipeline
    import fabricops_kit.widgets as widgets

    assert "setup_pipeline" in kit.__all__ and "setup_pipeline" in pipeline.__all__
    assert "setup_pipeline" not in widgets.__all__
    for package in (kit, pipeline):
        assert not hasattr(package, "create_pipeline_execution_plan")
    for package in (kit, widgets):
        assert not hasattr(package, "widget_select_data_contract")
        assert not hasattr(package, "widget_pipeline")
    for name in ("fabricops_kit.pipeline.create_pipeline_execution_plan",
                 "fabricops_kit.widgets.widget_select_data_contract",
                 "fabricops_kit.widgets.widget_pipeline"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(name)


def test_interactive_read_only_selection_has_no_target_controls(monkeypatch):
    """The interactive selector accepts a Read-only structure without inventing a target."""
    _, state, _ = _render(monkeypatch, [_row()], interactive=True, targets=[])
    assert set(state["tables"]) == {"source"}
    assert state["tables"]["source"]["identity"]["roles"] == ["source"]
    state["select_contract"]("source", "contract-source", 1)
    assert state["tables"]["source"]["selected"]["contract_version"] == 1


def test_real_testing_write_authorization_locks_with_the_built_plan(monkeypatch):
    """The confirmation cannot appear to disable writes after authority is frozen."""
    from types import SimpleNamespace
    _, state, _ = _render(monkeypatch, [], interactive=True, testing_writes=True)
    sentinel = SimpleNamespace(results=[])
    monkeypatch.setattr(module, "build_pipeline_execution_plan", lambda **kw: sentinel)
    for table_id in state["tables"]:
        state["select_contract"](table_id, no_contract=True)
    with pytest.raises(ValueError, match="Confirm real Testing writes"):
        state["build_plan"]()
    authorization = state["write_authorized"]
    authorization.value = True
    assert state["build_plan"]() is sentinel
    assert authorization.disabled
