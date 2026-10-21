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
    class Plan:
        run_result = {"status": "succeeded" if passed else "failed"}
        def __enter__(self): return self
        def __exit__(self, *args): finalize(); return False
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
