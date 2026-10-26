"""Real notebook protocol checks; physical Fabric services use delayed in-memory fixtures."""
from pathlib import Path
import time

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("workflow", ["governance", "engineering"])
def test_html_loading_is_published_while_kernel_is_busy(workflow):
    """Observe IOPub during a blocking read rather than assuming widget display paints."""
    client_module = pytest.importorskip("jupyter_client")
    pytest.importorskip("ipykernel")
    manager = client_module.KernelManager()
    manager.start_kernel(cwd=str(Path(__file__).resolve().parents[2]))
    client = manager.client()
    client.start_channels()
    try:
        client.wait_for_ready(timeout=30)
        setup = '''
import time, importlib, threading
from types import SimpleNamespace
from tests.helpers import agreement_config, framework_config, steward_row
owner_thread = threading.get_ident()
def collect():
    assert threading.get_ident() == owner_thread
    print("metadata-start", flush=True)
    time.sleep(0.6)
    print("metadata-end", flush=True)
    return []
'''
        if workflow == "governance":
            setup += '''
m = importlib.import_module("fabricops_kit.widgets.widget_render_data_steward")
m.resolve_fabric_context = lambda **kw: (agreement_config(), "dev", {})
m.list_data_stewards = lambda *a, **kw: collect()
m.get_spark_session = lambda **kw: object()
state = m.widget_render_data_steward()
'''
        else:
            setup += '''
m = importlib.import_module("fabricops_kit.pipeline.shared")
m.get_default_fabric_context = lambda **kw: {"config": framework_config(), "env": "dev"}
m.resolve_fabric_context = lambda **kw: (framework_config(), "dev", {})
m.get_spark_session = lambda: object()
m.resolve_pipeline_registration = lambda identity, **kw: {"pipeline_id": "8f32a471-6c91-4b7e-9d13-2f0c947eab52", "resolution": "Recovered"}
m.read_lakehouse_table = lambda *a, **kw: SimpleNamespace(collect=collect)
state = m.start_pipeline_session("generic", "Test")
state.close()
'''
        message_id = client.execute(setup)
        events = []
        while True:
            message = client.get_iopub_msg(timeout=30)
            if message["parent_header"].get("msg_id") != message_id:
                continue
            content, kind = message["content"], message["msg_type"]
            assert kind != "error", content
            events.append((kind, content, time.monotonic()))
            if kind == "status" and content["execution_state"] == "idle":
                break
        first_html = next(i for i, (kind, value, _) in enumerate(events)
                          if kind == "display_data" and "text/html" in value["data"])
        read_started = next(i for i, (kind, value, _) in enumerate(events)
                            if kind == "stream" and "metadata-start" in value["text"])
        read_finished = next(i for i, (kind, value, _) in enumerate(events)
                             if kind == "stream" and "metadata-end" in value["text"])
        assert first_html < read_started < read_finished
        assert events[read_finished][2] - events[first_html][2] >= 0.5
        # Ordinary HTML is available before Spark; no widget comm round trip is needed.
        assert "application/vnd.jupyter.widget-view+json" not in events[first_html][1]["data"]
        assert any(kind == "update_display_data" and "application/vnd.jupyter.widget-view+json" in value["data"]
                   for kind, value, _ in events)
    finally:
        client.stop_channels()
        manager.shutdown_kernel(now=True)
