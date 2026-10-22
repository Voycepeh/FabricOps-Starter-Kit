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
