"""Optional Chromium geometry checks of native contract controls with in-memory services."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
from threading import Thread

import pytest

from tests.unit.test_widget_data_contract import _enable_ai, module, widget_runtime


@pytest.fixture
def contract_browser(tmp_path):
    """Serve offline widget snapshots without manually injecting enhancement JavaScript."""
    bundle = os.environ.get("FABRICOPS_WIDGET_EMBED_BUNDLE")
    if not bundle or not Path(bundle).is_file():
        pytest.skip("Set FABRICOPS_WIDGET_EMBED_BUNDLE to html-manager dist/embed.js.")
    playwright = pytest.importorskip("playwright.sync_api")
    widgets = pytest.importorskip("ipywidgets")
    from ipywidgets.embed import dependency_state, embed_minimal_html

    browser = shutil.which("chromium") or shutil.which("google-chrome")
    if not browser:
        pytest.skip("Chromium is required.")
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

            def show(root, width, name):
                embed_minimal_html(str(tmp_path / "contract.html"), views=[root], requirejs=False,
                                   embed_url="./embed.js", state=dependency_state([root]))
                page.set_viewport_size({"width": width, "height": 900})
                page.goto(f"http://127.0.0.1:{server.server_port}/contract.html")
                page.wait_for_selector(".fabricops-data-contract")
                page.wait_for_timeout(150)
                if os.environ.get("FABRICOPS_WIDGET_SCREENSHOT_DIR"):
                    target = Path(os.environ["FABRICOPS_WIDGET_SCREENSHOT_DIR"])
                    target.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(target / f"{name}-{width}.png"), full_page=True)
                return page

            yield widgets, show
            assert not errors
            instance.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_searchable_entry_dropdown_wraps_and_filters_without_expanding_form(monkeypatch, contract_browser):
    """Open and search one dropdown; long labels fit without shifting adjacent fields."""
    widgets, show = contract_browser
    runtime = widget_runtime.__wrapped__(monkeypatch)
    runtime["catalogue"][0]["table_name"] = "inventory_movements_append_all_" * 7
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: widgets)
    state = runtime["start"]()
    controls = state["_controls"]
    controls["workspace_select"].value = "dev"
    controls["store_select"].value = "Silver"
    from fabricops_kit.widgets import _FABRIC_NOTEBOOK_UX_JAVASCRIPT
    for width in (1440, 1050, 700, 420):
        page = show(controls["page"], width, "entry-dropdown")
        page.evaluate(_FABRIC_NOTEBOOK_UX_JAVASCRIPT)
        field = page.locator(".fabricops-searchable-selector-v2 input").nth(2)
        contract = page.locator(".fabricops-searchable-selector-v2").nth(3)
        before = contract.evaluate("e => [e.offsetTop, e.offsetLeft, e.offsetWidth, e.offsetHeight]")
        field.click()
        option = page.locator(".fabricops-selector-popup [role=option]").filter(has_text="inventory_movements").first
        option.wait_for()
        assert option.evaluate("e => e.scrollWidth <= e.clientWidth + 1")
        assert option.evaluate("e => getComputedStyle(e).whiteSpace === 'normal'")
        field.fill("no-such-dataset")
        assert page.locator(".fabricops-selector-popup [role=option]").count() == 0
        field.fill("inventory_movements")
        option.wait_for()
        assert contract.evaluate("e => [e.offsetTop, e.offsetLeft, e.offsetWidth, e.offsetHeight]") == before
        if os.environ.get("FABRICOPS_WIDGET_SCREENSHOT_DIR"):
            page.screenshot(path=str(Path(os.environ["FABRICOPS_WIDGET_SCREENSHOT_DIR"]) / f"dropdown-open-{width}.png"), full_page=True)
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
        field.press("ArrowDown")
        field.press("Enter")
        assert page.locator(".fabricops-selector-popup").count() == 0
        assert "inventory_movements" in field.input_value()
        selected = page.locator(".fabricops-selector-value").nth(2)
        assert selected.evaluate("e => e.scrollWidth <= e.clientWidth + 1")
    controls["page"].close()


def test_single_content_body_keeps_actions_and_navigation_outside_scroll(monkeypatch, contract_browser):
    """All tabs fit widths, with optional expansion confined to the active body."""
    widgets, show = contract_browser
    runtime = widget_runtime.__wrapped__(monkeypatch)
    _enable_ai(runtime, monkeypatch)
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: widgets)
    state = runtime["open"]()
    controls = state["_controls"]
    for section in module._TABS:
        controls["top_nav"].value = section
        for width in (1440, 1050, 700, 420):
            page = show(controls["page"], width, section.replace(" ", "-"))
            result = page.evaluate("""() => {
                const root = document.querySelector('.fabricops-data-contract');
                const detail = root.querySelector('.fabricops-contract-detail');
                const nav = root.querySelector('.fabricops-contract-nav');
                const actions = root.querySelector('.fabricops-contract-actions');
                const before = [nav.getBoundingClientRect().top, actions.getBoundingClientRect().top];
                detail.scrollTop = detail.scrollHeight;
                return {
                    overflow: document.documentElement.scrollWidth > innerWidth,
                    bounded: detail.clientHeight <= 562,
                    stable: before[0] === nav.getBoundingClientRect().top && before[1] === actions.getBoundingClientRect().top,
                    outside: !detail.contains(actions) && !detail.contains(nav),
                    actionVisible: actions.getBoundingClientRect().bottom <= innerHeight,
                };
            }""")
            assert not result["overflow"], (section, width, result)
            assert result["bounded"] and result["stable"] and result["outside"], (section, width, result)
            assert result["actionVisible"], (section, width, result)
    controls["table_context"].selected_index = 0
    page = show(controls["page"], 700, "expanded-context")
    assert page.locator(".fabricops-contract-detail").evaluate("e => e.clientHeight <= 562")
    state["_dispose_editor"]()
    controls["page"].close()
