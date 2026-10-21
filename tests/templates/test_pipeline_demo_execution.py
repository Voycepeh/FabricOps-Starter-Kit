"""Execute demo notebook control flow with isolated Fabric and Spark boundaries."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import nbformat
import pytest

DEMO_DIR = Path(__file__).resolve().parents[2] / "templates" / "DemoData"
DEMOS = (
    "../notebooks/02_pipeline.ipynb",
    "02A_full_refresh_demo.ipynb",
    "02B_incremental_append_demo.ipynb",
    "02C_scd_demo.ipynb",
)


@pytest.mark.parametrize("name", DEMOS)
@pytest.mark.parametrize("mode,passed", [("testing", True), ("testing", False), ("live", True)])
def test_demo_executes_every_declared_operation_before_inspection(name, mode, passed, capsys):
    """Fresh sessions and failed Testing results still reach every target and the inspector."""
    plan = object()
    reads, writes = [], []
    dataframe = MagicMock(name="dataframe")
    finalize = Mock(return_value={"status": "succeeded" if passed else "failed"})
    refresh = Mock()
    build_plan = Mock(return_value=plan)

    def select(**kwargs):
        assert kwargs["sources"] and kwargs["targets"]
        if not kwargs["interactive"]:
            assert mode == "live"
            assert kwargs.get("execution_mode") == ("live" if mode == "live" else "testing")
            return plan
        return {"build_plan": build_plan, "refresh": refresh}

    def read(**kwargs):
        assert kwargs["execution_plan"] is plan
        result = {"dataframe": dataframe, "table_name": kwargs["table_name"], "plan": plan}
        reads.append(result)
        return result

    def write(prepared, **kwargs):
        assert kwargs["execution_plan"] is plan
        assert all(source["plan"] is plan for source in kwargs["sources"])
        writes.append(kwargs["table_name"])
        return {"dataframe": prepared, "execution_mode": mode, "validation_passed": passed,
                "published": mode != "testing", "publication_status": "published" if mode != "testing" else "not_published"}

    forbidden = Mock(side_effect=AssertionError("Notebook exited or published outside the orchestrators"))
    namespace = {
        "PIPELINE_CONTRACT_TESTING": mode == "testing", "PIPELINE_LIVE_ENABLED": mode == "live",
        "F": MagicMock(), "spark": object(), "display": Mock(),
        "finalize_pipeline": finalize, "setup_pipeline": select, "orchestrate_read": read, "orchestrate_write": write,
        "resolve_table_id": Mock(return_value="inventory-target"),
        "read_lakehouse_csv": forbidden, "read_lakehouse_table": forbidden,
        "write_lakehouse_table": forbidden,
        "notebookutils": SimpleNamespace(notebook=SimpleNamespace(exit=forbidden)),
    }
    notebook = nbformat.read(DEMO_DIR / name, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code" and cell.id not in {"environment", "imports"}:
            source = cell.source
            exec(compile(source, f"{name}:{cell.id}", "exec"), namespace)
    assert [row["table_name"] for row in reads] == [row["table_name"] for row in namespace["PIPELINE_SOURCES"]]
    assert writes == [row["table_name"] for row in namespace["PIPELINE_TARGETS"]]
    finalize.assert_called_once_with(plan)
    assert len(namespace["writes"]) == len(writes)
    assert all(result["validation_passed"] is passed for result in namespace["writes"].values())
    if mode == "testing":
        build_plan.assert_called_once_with()
        refresh.assert_called_once_with()
    else:
        build_plan.assert_not_called()
        refresh.assert_not_called()
    forbidden.assert_not_called()
    output = capsys.readouterr().out
    if mode == "testing" and not passed:
        assert "validation_passed: False" in output


@pytest.mark.parametrize("name", DEMOS)
def test_stopped_notebook_never_reaches_finalization(name):
    """A project exception stops execution and leaves setup tracking incomplete."""
    finalize = Mock()
    namespace = {"PIPELINE_LIVE_ENABLED": True, "spark": object(), "F": MagicMock(), "display": Mock(),
        "setup_pipeline": Mock(return_value=object()), "finalize_pipeline": finalize,
        "resolve_table_id": Mock(return_value="target"),
        "orchestrate_read": Mock(side_effect=RuntimeError("interrupted pipeline"))}
    notebook = nbformat.read(DEMO_DIR / name, as_version=4)
    with pytest.raises(RuntimeError, match="interrupted pipeline"):
        for cell in notebook.cells:
            if cell.cell_type == "code" and cell.id not in {"environment", "imports"}:
                exec(compile(cell.source, name, "exec"), namespace)
    finalize.assert_not_called()


@pytest.mark.parametrize('name', DEMOS)
def test_pipeline_templates_use_one_explicit_setup_and_finalization(name):
    """All standard and variant templates expose the same direct execution stages."""
    import ast
    notebook = nbformat.read(DEMO_DIR / name, as_version=4)
    ids = [cell.id for cell in notebook.cells]
    stages = ['environment', 'setup-heading', 'contracts', 'contracts-heading', 'execution-plan',
              'read-heading', 'transform', 'write-heading', 'finalize-run', 'inspect']
    assert [ids.index(stage) for stage in stages] == sorted(ids.index(stage) for stage in stages)
    calls = {}
    for cell in notebook.cells:
        if cell.cell_type != 'code' or cell.id == 'environment':
            continue
        tree = ast.parse(cell.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.setdefault(node.func.id, []).append((cell.id, node))
        assert not any(isinstance(node, ast.FunctionDef) for node in tree.body), cell.id
    assert len(calls['setup_pipeline']) == len(calls['finalize_pipeline']) == 1
    assert calls['setup_pipeline'][0][0] == 'contracts'
    assert calls['finalize_pipeline'][0][0] == 'finalize-run'
    finalize_argument = calls['finalize_pipeline'][0][1].args[0]
    assert isinstance(finalize_argument, ast.Name) and finalize_argument.id == 'EXECUTION_PLAN'
    for function in ('orchestrate_read', 'orchestrate_write'):
        assert all(any(arg.arg == 'execution_plan' and isinstance(arg.value, ast.Name)
                       and arg.value.id == finalize_argument.id for arg in call.keywords)
                   for _, call in calls[function])
