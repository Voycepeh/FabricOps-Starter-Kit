"""Startup uses ordinary display output before synchronous services and real widgets."""
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import ipywidgets as widgets
import pytest
from IPython import display as ip

from fabricops_kit.widgets.shared import WidgetStartup, form_page, list_data_stewards, list_data_agreements
from tests.helpers import agreement_config, framework_config, steward_row


@pytest.fixture
def outputs(monkeypatch):
    """Capture notebook protocol output while keeping native widget construction."""
    events = []
    monkeypatch.setattr(ip, "display", lambda value, **kw: events.append(("display", value, kw)))
    monkeypatch.setattr(ip, "update_display", lambda value, **kw: events.append(("update", value, kw)))
    return events


@pytest.mark.parametrize("name", ["widget_render_data_steward", "widget_render_data_agreement",
                                  "widget_data_contract", "widget_activate_pipeline"])
def test_public_widget_displays_before_services_without_duplicate_reads(name, monkeypatch, outputs):
    """Every public Governance entrypoint publishes loading before its first read."""
    module = import_module("fabricops_kit.widgets." + name)
    config = framework_config() if name == "widget_data_contract" else agreement_config()
    reads = []

    def read(label, result):
        def service(*args, **kwargs):
            assert len(outputs) >= 3
            assert "role=\"status\"" in outputs[-1][1].data
            reads.append(label)
            return result
        return service

    monkeypatch.setattr(module, "resolve_fabric_context", lambda **kw: (config, "dev", {}))
    if "steward" in name or "agreement" in name:
        monkeypatch.setattr(module, "list_data_stewards", read("stewards", [steward_row()]))
        if "agreement" in name:
            monkeypatch.setattr(module, "list_data_agreements", read("agreements", []))
        state = getattr(module, name)(spark=object())
        root = state["container"]
        assert reads == (["agreements", "stewards"] if "agreement" in name else ["stewards"])
    elif name == "widget_data_contract":
        monkeypatch.setattr(module, "get_spark_session", lambda *_: object())
        monkeypatch.setattr(module.contracts, "list_contract_governance_state", read("catalogue", {"tables": [], "contracts": []}))
        state = module.widget_data_contract()
        root = state["_controls"]["page"]
        assert reads == ["catalogue"]
    else:
        monkeypatch.setattr(module, "metadata_records", lambda table, **kw: read(table, [])())
        monkeypatch.setattr(module, "read_activation_state", read("activation", (None, {})))
        monkeypatch.setattr(module, "environment_activation", lambda *_: {"pipelines": {}, "tables": {}, "revision": 0})
        state = module.widget_activate_pipeline(testing_results=[])
        root = state["widget"]
        assert reads == ["METADATA_DATA_AGREEMENT", "activation"]
    assert outputs[-1][1] is root
    assert root.startup_timings["metadata_loading"] >= 0
    assert "interactive_ready" not in root.startup_timings
    root._view_count = 1
    assert root.startup_timings["interactive_ready"] >= root.startup_timings["form_display_submitted"]
    root.close()


def test_pipeline_loading_precedes_initialization_and_collect(monkeypatch, outputs):
    """The Engineering path keeps metadata collection and session work on this thread."""
    import IPython
    from fabricops_kit.pipeline import shared
    shell = SimpleNamespace(events=Mock())
    config = framework_config()
    monkeypatch.setattr(IPython, "get_ipython", lambda: shell)
    calls = []

    def initialize(**kwargs):
        assert outputs and "Pipeline execution" in outputs[0][1].data
        calls.append("initialize")
        return SimpleNamespace(notebook_name="02_pipeline")

    def collect():
        assert "Loading frozen" in outputs[-1][1].data
        calls.append("collect")
        return []

    monkeypatch.setattr(shared, "resolve_pipeline_registration", lambda identity, **kwargs: {"pipeline_id": "8f32a471-6c91-4b7e-9d13-2f0c947eab52", "resolution": "Recovered"})
    monkeypatch.setattr(shared, "initialize_notebook", initialize)
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda **kw: (config, "dev", {}))
    monkeypatch.setattr(shared, "get_spark_session", lambda: object())
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: SimpleNamespace(collect=collect))
    token = shared._ACTIVE_PIPELINE.set(None)
    session = None
    try:
        session = shared.start_pipeline_session("generic", "Test")
        assert calls == ["initialize", "collect"]
        assert "spark_loading" in session.startup_timings
        assert session.controls == []
    finally:
        if session:
            session.close()
        shared._ACTIVE_PIPELINE.reset(token)


def test_load_failure_is_actionable_and_preserves_exception(outputs):
    """Report recovery steps without swallowing or exposing sensitive exception text in HTML."""
    startup = WidgetStartup("Data Agreement")
    original = RuntimeError("private <path>")
    with pytest.raises(RuntimeError) as caught:
        with startup.phase("metadata_loading", "Loading agreements…"):
            raise original
    assert caught.value is original
    assert "rerun this cell" in outputs[-1][1].data
    assert "private" not in outputs[-1][1].data
    assert "failed" in startup.timings


@pytest.mark.parametrize("loader", [list_data_stewards, list_data_agreements])
def test_missing_ok_never_turns_access_failure_into_empty_metadata(loader, monkeypatch):
    """Access failures must reach the startup error instead of a misleading empty form."""
    shared = import_module("fabricops_kit.widgets.shared")
    monkeypatch.setattr(shared, "read_lakehouse_table", Mock(side_effect=PermissionError("denied")))
    with pytest.raises(PermissionError):
        loader(agreement_config(), "dev", missing_ok=True)


def test_notebook_setup_summary_uses_escaped_styled_html(monkeypatch, outputs):
    """The caller keeps all setup diagnostics in the restored FabricOps banner."""
    import IPython
    from fabricops_kit.config import shared
    monkeypatch.setattr(IPython, "get_ipython", lambda: object())
    context = SimpleNamespace(runtime_metadata={}, workspace_name="<workspace>", notebook_name="<notebook>",
                              run_id="generic", environment="dev", paths={}, readiness_status="ready",
                              validation_results=[])
    shared._print_notebook_setup_summary(context, config=framework_config(), config_workspace_id=None)
    html = outputs[-1][1].data
    assert "#0f6cbd" in html and "FabricOps v" in html
    assert "&lt;notebook&gt;" in html and "&lt;workspace&gt;" in html
    assert "Readiness: ready" in html and "Metadata schemas:" in html
    assert 'href="https://github.com/Voycepeh/FabricOps-Starter-Kit"' in html
