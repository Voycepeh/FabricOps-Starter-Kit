"""Focused regression coverage for the agent call-flow lookup."""
import pytest

from scripts.query_public_function_call_flow import lookup


@pytest.fixture
def graph():
    return {
        "defined_functions": [
            {"qualified_name": "pkg.a.run", "source_path": "a.py"},
            {"qualified_name": "pkg.b.helper", "source_path": "b.py"},
            {"qualified_name": "pkg.c.leaf", "source_path": "c.py"},
        ],
        "public_functions": [{"qualified_name": "pkg.a.run", "width": 1}],
        "relationships": [
            {"caller_qualified_name": "pkg.a.run", "callee_qualified_name": "pkg.b.helper"},
            {"caller_qualified_name": "pkg.b.helper", "callee_qualified_name": "pkg.c.leaf"},
            {"caller_qualified_name": "pkg.c.leaf", "callee_qualified_name": "pkg.b.helper"},
        ],
    }


def test_direct_lookup_limits_context(graph):
    result = lookup(graph, "run")
    assert result["callable"]["qualified_name"] == "pkg.a.run"
    assert result["public_root"]["width"] == 1
    assert len(result["direct_and_transitive_callees"]) == 1
    assert set(result["related_functions"]) == {"pkg.b.helper"}
    assert result["callers"] is None


def test_deeper_lookup_is_bounded_and_cycle_safe(graph):
    result = lookup(graph, "pkg.a.run", depth=3)
    assert [e["depth"] for e in result["direct_and_transitive_callees"]] == [1, 2, 3]
    assert set(result["related_functions"]) == {"pkg.b.helper", "pkg.c.leaf"}


def test_upstream_is_opt_in(graph):
    result = lookup(graph, "pkg.b.helper", include_callers=True)
    assert [e["caller_qualified_name"] for e in result["callers"]] == ["pkg.a.run", "pkg.c.leaf"]


def test_unknown_and_ambiguous_names_fail(graph):
    with pytest.raises(ValueError, match="Unknown callable"):
        lookup(graph, "missing")
    graph["defined_functions"].append({"qualified_name": "pkg.other.helper"})
    with pytest.raises(ValueError, match="Ambiguous callable"):
        lookup(graph, "helper")
