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
    boundary = {"open": False}
    class Plan:
        run_result = {"status": "succeeded" if passed else "failed"}
        def __enter__(self): boundary["open"] = True; return self
        def __exit__(self, *args): boundary["open"] = False; finalize(); return False
    plan = Plan()
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
        assert boundary["open"], "Reads must execute inside the whole-run boundary"
        assert kwargs["execution_plan"] is plan
        result = {"dataframe": dataframe, "table_name": kwargs["table_name"], "plan": plan}
        reads.append(result)
        return result

    def write(prepared, **kwargs):
        assert boundary["open"], "Writes must execute inside the whole-run boundary"
        assert kwargs["execution_plan"] is plan
        assert all(source["plan"] is plan for source in kwargs["sources"])
        writes.append(kwargs["table_name"])
        return {"dataframe": prepared, "execution_mode": mode, "validation_passed": passed,
                "published": mode != "testing", "publication_status": "published" if mode != "testing" else "not_published"}

    forbidden = Mock(side_effect=AssertionError("Notebook exited or published outside the orchestrators"))
    namespace = {
        "PIPELINE_CONTRACT_TESTING": mode == "testing", "PIPELINE_LIVE_ENABLED": mode == "live",
        "PIPELINE_DEPLOYMENT_PATH": "/configured/deployment" if mode == "live" else None,
        "F": MagicMock(), "spark": object(), "display": Mock(),
        "setup_pipeline": select, "orchestrate_read": read, "orchestrate_write": write,
        "resolve_table_id": Mock(return_value="inventory-target"),
        "read_lakehouse_csv": forbidden, "read_lakehouse_table": forbidden,
        "write_lakehouse_table": forbidden,
        "notebookutils": SimpleNamespace(notebook=SimpleNamespace(exit=forbidden)),
    }
    notebook = nbformat.read(DEMO_DIR / name, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code" and cell.id not in {"environment", "imports"}:
            if cell.id == "finalize-run":
                assert not reads and not writes, "Stage definition cells must not execute the pipeline"
            source = cell.source
            exec(compile(source, f"{name}:{cell.id}", "exec"), namespace)
    assert [row["table_name"] for row in reads] == [row["table_name"] for row in namespace["PIPELINE_SOURCES"]]
    assert writes == [row["table_name"] for row in namespace["PIPELINE_TARGETS"]]
    finalize.assert_called_once_with()
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
@pytest.mark.parametrize("failure_stage", ["transform", "write"])
def test_notebook_execution_boundary_propagates_project_and_write_failures(name, failure_stage):
    """Every scaffold keeps project failures inside the same boundary as its operations."""
    boundary = {"open": False, "outcome": None}
    class Plan:
        def __enter__(self): boundary["open"] = True; return self
        def __exit__(self, exc_type, *_):
            boundary.update(open=False, outcome=exc_type)
            return False
    plan = Plan()
    dataframe = MagicMock()
    def fail(*args, **kwargs):
        assert boundary["open"]
        raise RuntimeError("Project failure inside " + failure_stage)
    namespace = {
        "PIPELINE_LIVE_ENABLED": True, "spark": object(), "F": MagicMock(), "display": Mock(),
        "setup_pipeline": Mock(return_value=plan), "resolve_table_id": Mock(return_value="target"),
        "orchestrate_read": Mock(return_value={"dataframe": dataframe}),
        "orchestrate_write": fail if failure_stage == "write" else Mock(),
    }
    notebook = nbformat.read(DEMO_DIR / name, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != "code" or cell.id in {"environment", "imports"}:
            continue
        if cell.id == "finalize-run":
            if failure_stage == "transform":
                namespace["transform"] = fail
            with pytest.raises(RuntimeError, match="Project failure"):
                exec(compile(cell.source, f"{name}:{cell.id}", "exec"), namespace)
            break
        exec(compile(cell.source, f"{name}:{cell.id}", "exec"), namespace)
    assert boundary == {"open": False, "outcome": RuntimeError}
