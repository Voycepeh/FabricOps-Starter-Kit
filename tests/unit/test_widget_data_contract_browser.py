"""Optional Chromium checks of actual Data Contract ipywidgets with in-memory services."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
from threading import Thread

import pytest

from tests.unit.test_widget_data_contract import _enable_ai, module, widget_runtime


def test_sidebar_and_single_content_scroll_region(monkeypatch, tmp_path):
    """Render each section at notebook widths; keep actions visible during deep scrolling."""
    bundle = os.environ.get("FABRICOPS_WIDGET_EMBED_BUNDLE")
    if not bundle or not Path(bundle).is_file():
        pytest.skip("Set FABRICOPS_WIDGET_EMBED_BUNDLE to the local html-manager dist/embed.js for offline rendering.")
    playwright = pytest.importorskip("playwright.sync_api")
    widgets = pytest.importorskip("ipywidgets")
    from ipywidgets.embed import dependency_state, embed_minimal_html

    browser = shutil.which("chromium") or shutil.which("google-chrome")
    if not browser:
        pytest.skip("A Chromium-family browser is required.")
    runtime = widget_runtime.__wrapped__(monkeypatch)
    _enable_ai(runtime, monkeypatch)
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: widgets)
    state = runtime["open"]()
    controls = state["_controls"]
    shutil.copyfile(bundle, tmp_path / "embed.js")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with playwright.sync_playwright() as driver:
            instance = driver.chromium.launch(executable_path=browser, headless=True, args=["--no-sandbox"])
            page = instance.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            for section in module._TABS:
                controls["top_nav"].value = section
                target = tmp_path / "contract.html"
                embed_minimal_html(
                    str(target), views=[controls["page"]], requirejs=False,
                    embed_url="./embed.js", title="Data Contract test fixture",
                    state=dependency_state([controls["page"]]),
                )
                for width in (1440, 1050, 700):
                    page.set_viewport_size({"width": width, "height": 1000})
                    page.goto(f"http://127.0.0.1:{server.server_port}/contract.html")
                    page.wait_for_selector(".fabricops-contract-sidebar")
                    page.wait_for_function("document.querySelector('.fabricops-contract-nav button') !== null")
                    result = page.evaluate("""() => {
                        const root = document.querySelector('.fabricops-data-contract');
                        const sidebar = root.querySelector('.fabricops-contract-sidebar');
                        const detail = root.querySelector('.fabricops-contract-detail');
                        const before = sidebar.getBoundingClientRect().top;
                        detail.scrollTop = detail.scrollHeight;
                        const regions = [...root.querySelectorAll('*')].filter(e =>
                            ['auto','scroll'].includes(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 2
                            && !e.matches('select, textarea') && !e.closest('.widget-select, .widget-select-multiple, .widget-textarea'));
                        return {
                            horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
                            regionClasses: regions.map(e => e.className),
                            sidebarMoved: sidebar.getBoundingClientRect().top !== before,
                            actionsVisible: [...sidebar.querySelectorAll('button')].filter(e =>
                                ['Save draft', 'Discard changes', 'Exit'].includes(e.textContent.trim())
                            ).every(e => e.getBoundingClientRect().bottom <= innerHeight),
                            detailClipped: detail.scrollHeight > detail.clientHeight + 2 && getComputedStyle(detail).overflowY !== 'auto',
                        };
                    }""")
                    assert not result["horizontalOverflow"], (section, width, result)
                    assert len(result["regionClasses"]) <= 1, (section, width, result)
                    assert all("fabricops-contract-detail" in value for value in result["regionClasses"])
                    assert not result["sidebarMoved"] and result["actionsVisible"], (section, width, result)
                    assert not result["detailClipped"], (section, width, result)
            assert not errors
            instance.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        state["_dispose_editor"]()
        controls["page"].close()
