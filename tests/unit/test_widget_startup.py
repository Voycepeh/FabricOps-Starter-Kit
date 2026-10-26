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
        monkeypatch.setattr(module, "get_spark_session", lambda *_args, **kwargs: object())
        state = getattr(module, name)()
        root = state["container"]
        assert reads == (["agreements", "stewards"] if "agreement" in name else ["stewards"])
    elif name == "widget_data_contract":
        monkeypatch.setattr(module, "get_spark_session", lambda *_, **_kwargs: object())
        monkeypatch.setattr(module.contracts, "list_contract_governance_state", read("catalogue", {"tables": [], "contracts": []}))
        state = module.widget_data_contract()
        root = state["_controls"]["page"]
        assert reads == ["catalogue"]
    else:
        monkeypatch.setattr(module, "metadata_records", lambda table, **kw: read(table, [])())
        monkeypatch.setattr(module, "read_pipeline_authority", read("activation", (None, {})))
        monkeypatch.setattr(module, "environment_activation", lambda *_: {"pipelines": {}, "tables": {}, "revision": 0})
        monkeypatch.setattr(module, "get_spark_session", lambda *_args, **kwargs: object())
        state = module.widget_activate_pipeline()
        root = state["widget"]
        assert reads == ["METADATA_PIPELINE_RUN", "METADATA_DATA_AGREEMENT", "activation"]
    assert outputs[-1][1] is root
    banner_updates = [
        value.data
        for kind, value, options in outputs
        if kind == "update" and str(options.get("display_id", "")).endswith("-banner")
    ]
    assert banner_updates
    assert root.fabricops_page_title in banner_updates[-1]
    assert root.fabricops_page_description in banner_updates[-1]
    assert ".fabricops-form.fabricops-started .fabricops-page-header { display:none; }" in root.children[0].value
    assert root.startup_timings["metadata_loading"] >= 0
    assert "interactive_ready" not in root.startup_timings
    root._view_count = 1
    assert root.startup_timings["interactive_ready"] >= root.startup_timings["form_display_submitted"]
    root.close()


def test_governance_record_selector_derives_environment_from_record(outputs):
    """The selector lists all records without a Governance-level environment setting."""
    from fabricops_kit.widgets.shared import select_governance_record

    config = framework_config()
    config.path_config.paths["test"] = dict(config.path_config.paths["dev"])
    config.path_config.paths["governance"] = {"Metadata": config.path_config.paths["dev"]["Metadata"]}
    received = []
    startup = WidgetStartup("Data Contract")
    state = select_governance_record(
        startup=startup, title="Data Contract", config=config,
        runtime_context={"config": config, "env": "governance"}, record_name="governed table",
        records=[{"environment_name": "dev", "table_id": "orders"},
                 {"environment_name": "test", "table_id": "accounts"}],
        record_label=lambda row: f"{row['environment_name']} · {row['table_id']}",
        launch=lambda record, scoped: received.append((record, scoped)) or {"loaded": True},
    )
    assert state["record"].value is None
    assert state["open"].disabled
    assert len(state["record"].options) == 3
    assert "dev" in state["record"].options[1][0]
    assert "test" in state["record"].options[2][0]
    state["record"].value = 1
    state["open"].click()
    assert len(received) == 1
    assert received[0][0]["table_id"] == "accounts"
    assert received[0][1]["env"] == "test"
    assert state["active"] == {"loaded": True}
    state["widget"].close()


def test_central_governance_widgets_show_records_from_all_engineering_environments(monkeypatch, outputs):
    """Contract and activation widgets must list records, not ask for an environment."""
    from importlib import import_module
    config = framework_config()
    config.path_config.paths["prod"] = dict(config.path_config.paths["dev"])
    config.path_config.paths["governance"] = {"Metadata": config.path_config.paths["dev"]["Metadata"]}
    contracts_widget = import_module("fabricops_kit.widgets.widget_data_contract")
    activation_widget = import_module("fabricops_kit.widgets.widget_activate_pipeline")
    for module in (contracts_widget, activation_widget):
        monkeypatch.setattr(module, "resolve_fabric_context", lambda **kw: (config, "governance", {}))
        monkeypatch.setattr(module, "get_spark_session", lambda **kw: object())

    calls = []
    def contract_rows(**kw):
        calls.append(("contracts", kw))
        return {"tables": [{"environment_name": "dev", "table_id": "a", "table_name": "sales"},
                           {"environment_name": "prod", "table_id": "b", "table_name": "stock"}],
                "contracts": []}
    monkeypatch.setattr(contracts_widget.contracts, "list_contract_governance_state", contract_rows)
    contract_state = contracts_widget.widget_data_contract()
    assert "environment" not in contract_state
    assert len(contract_state["records"]) == 2
    assert calls[0][1]["env"] == "governance"
    assert calls[0][1]["include_contracts"] is False

    def run_rows(table, **kw):
        calls.append(("runs", kw))
        return [{"environment_name": "dev", "pipeline_id": "first", "run_id": "dev-run"},
                {"environment_name": "prod", "pipeline_id": "second", "run_id": "prod-run"}]
    monkeypatch.setattr(activation_widget, "metadata_records", run_rows)
    monkeypatch.setattr(activation_widget, "_eligible_candidate", lambda row, pipeline_id=None:
                        pipeline_id is None or row["pipeline_id"] == pipeline_id)
    activation_state = activation_widget.widget_activate_pipeline()
    assert "environment" not in activation_state
    assert len(activation_state["records"]) == 2
    assert calls[-1][1]["all_environments"] is True
    assert calls[-1][1]["context"]["env"] == "governance"
    contract_state["widget"].close()
    activation_state["widget"].close()


def test_pipeline_loading_precedes_initialization_and_collect(monkeypatch, outputs):
    """The Engineering path keeps metadata collection and session work on this thread."""
    import IPython
    from fabricops_kit.pipeline import shared
    shell = SimpleNamespace(events=Mock())
    config = framework_config()
    monkeypatch.setattr(IPython, "get_ipython", lambda: shell)
    calls = []

    def reuse(**kwargs):
        assert outputs and "Pipeline execution" in outputs[0][1].data
        calls.append("reuse")
        return {"config": config, "env": "dev"}

    def collect():
        assert "Loading frozen" in outputs[-1][1].data
        calls.append("collect")
        return []

    monkeypatch.setattr(shared, "resolve_pipeline_registration", lambda identity, **kwargs: {"pipeline_id": "8f32a471-6c91-4b7e-9d13-2f0c947eab52", "resolution": "Recovered"})
    monkeypatch.setattr(shared, "get_default_fabric_context", reuse)
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda **kw: (config, "dev", {}))
    monkeypatch.setattr(shared, "get_spark_session", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: SimpleNamespace(collect=collect))
    token = shared._ACTIVE_PIPELINE.set(None)
    session = None
    try:
        session = shared.start_pipeline_session("generic", "Test")
        assert calls == ["reuse", "collect"]
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
