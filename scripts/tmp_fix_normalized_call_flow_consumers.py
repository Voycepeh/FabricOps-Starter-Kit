from pathlib import Path
import re


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return
        raise SystemExit(f"Expected block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# 1. Contract test now owns the normalized v3 contract.
path = Path("tests/contract/test_public_contract.py")
replace_once(
    path,
    '''def test_supported_public_api_matches_generated_call_flow_contract():
    """Verify contract entries remain generated v2 callable-flow entries."""
''',
    '''def test_supported_public_api_matches_generated_call_flow_contract():
    """Verify contract entries remain generated normalized callable-flow entries."""
''',
)
replace_once(
    path,
    '    assert callable_flow["metadata"]["schema"] == "fabricops_public_function_call_flows_v2"\n',
    '    assert callable_flow["metadata"]["schema"] == "fabricops_public_function_call_flows_v3"\n',
)

# 2. Widget role test should inspect canonical function records, not removed persisted flows.
path = Path("tests/unit/test_config.py")
old = '''def test_data_agreement_widget_callable_inventory_roles_are_current():
    """Verify generated v2 callable-flow inventory reflects the widget role split."""
    import json

    flow_data = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    rows = {row["qualified_name"]: row for row in flow_data["defined_functions"]}
    assert "fabricops_kit.widgets.shared.render_maintenance_widget_shared_workflow" not in rows
    assert (
        "fabricops_kit.widgets.widget_render_agreement_evidence._render_agreement_evidence_widget_workflow" not in rows
    )
    assert "fabricops_kit.widgets.shared._render_agreement_evidence_widget_workflow" not in rows
    public_functions = {row["qualified_name"]: row for row in flow_data["public_functions"]}
    assert (
        public_functions["fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward"]["flow"][0][
            "function_type"
        ]
        == "widget_function"
    )
    assert (
        public_functions["fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement"]["flow"][0][
            "function_type"
        ]
        == "widget_function"
    )
'''
new = '''def test_data_agreement_widget_callable_inventory_roles_are_current():
    """Verify normalized callable inventory reflects the widget role split."""
    import json

    flow_data = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    rows = {row["qualified_name"]: row for row in flow_data["defined_functions"]}
    assert "fabricops_kit.widgets.shared.render_maintenance_widget_shared_workflow" not in rows
    assert (
        "fabricops_kit.widgets.widget_render_agreement_evidence._render_agreement_evidence_widget_workflow" not in rows
    )
    assert "fabricops_kit.widgets.shared._render_agreement_evidence_widget_workflow" not in rows
    assert rows["fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward"]["function_type"] == "widget_function"
    assert (
        rows["fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement"]["function_type"]
        == "widget_function"
    )
'''
replace_once(path, old, new)

# 3. Reference generator derives the old expanded downstream-row count from normalized edges.
path = Path("scripts/generate_individual_function_reference_pages.py")
text = path.read_text(encoding="utf-8")
start = text.find("def _load_public_call_flow_inventory(")
if start < 0:
    raise SystemExit("call-flow inventory loader not found")
match = re.search(r"^def ", text[start + 1 :], flags=re.MULTILINE)
if not match:
    raise SystemExit("next top-level function not found after call-flow loader")
end = start + 1 + match.start()
old_loader = text[start:end]
new_loader = '''def _expanded_downstream_count(root_qn: str, relationships: list[dict[str, Any]]) -> int:
    """Return the expanded downstream row count reconstructed from normalized edges."""
    children: dict[str, list[str]] = {}
    for relationship in relationships:
        caller = relationship.get("caller_qualified_name")
        callee = relationship.get("callee_qualified_name")
        if caller and callee:
            children.setdefault(str(caller), []).append(str(callee))
    for callees in children.values():
        callees.sort()

    count = 0

    def visit(qn: str, stack: set[str]) -> None:
        nonlocal count
        next_stack = set(stack)
        next_stack.add(qn)
        for callee in children.get(qn, []):
            count += 1
            if callee not in next_stack:
                visit(callee, next_stack)

    visit(root_qn, set())
    return count


def _load_public_call_flow_inventory(path: Path = PUBLIC_CALL_FLOW_DATA_PATH) -> dict[str, Any]:
    """Load normalized callable inventory and derive presentation-only downstream counts."""
    if not path.exists():
        return {"public_functions": [], "relationships": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    public_functions = data.get("public_functions")
    if not isinstance(public_functions, list):
        return {"public_functions": [], "relationships": []}
    relationships = data.get("relationships", [])
    if not isinstance(relationships, list):
        relationships = []
    for record in public_functions:
        qualified_name = record.get("qualified_name")
        record["downstream_callable_count"] = (
            _expanded_downstream_count(str(qualified_name), relationships) if qualified_name else 0
        )
    return data


'''
text = text[:start] + new_loader + text[end:]
old_expr = "f\"- Downstream callables: {max(len(record.get('flow', [])) - 1, 0)}\""
new_expr = "f\"- Downstream callables: {record.get('downstream_callable_count', 0)}\""
if old_expr in text:
    text = text.replace(old_expr, new_expr, 1)
elif new_expr not in text:
    raise SystemExit("downstream callable rendering expression not found")
path.write_text(text, encoding="utf-8")
