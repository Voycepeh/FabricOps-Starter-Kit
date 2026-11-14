"""Optional Chromium checks of actual Data Contract ipywidgets with in-memory services."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
from threading import Thread

import pytest

from fabricops_kit.widgets import _FABRIC_NOTEBOOK_UX_JAVASCRIPT
from tests.unit.test_widget_data_contract import _enable_ai, module, widget_runtime


def test_dataset_popup_follows_input_width_and_supports_search_and_keyboard(monkeypatch, tmp_path):
    """Exercise the real ComboboxView popup rather than its Python layout alone."""
    bundle = os.environ.get("FABRICOPS_WIDGET_EMBED_BUNDLE")
    if not bundle or not Path(bundle).is_file():
        pytest.skip("Set FABRICOPS_WIDGET_EMBED_BUNDLE to the local html-manager dist/embed.js.")
    playwright = pytest.importorskip("playwright.sync_api")
    widgets = pytest.importorskip("ipywidgets")
    from ipywidgets.embed import dependency_state, embed_minimal_html

    browser = shutil.which("chromium") or shutil.which("google-chrome")
    if not browser:
        pytest.skip("A Chromium-family browser is required.")
    runtime = widget_runtime.__wrapped__(monkeypatch)
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: widgets)
    # Include long real options and a short workspace name in the same form.
    runtime["catalogue"][0]["table_name"] = "inventory_movements_append_all_with_long_dataset_name"
    runtime["catalogue"].extend(
        {**runtime["catalogue"][0], "table_id": f"other-{i}", "table_name": f"other_dataset_with_a_long_name_{i}"}
        for i in range(15)
    )
    monkeypatch.setattr(module.contracts, "list_contract_governance_state", lambda **kwargs: {
        "tables": [row for row in runtime["catalogue"] if row.get("metadata_level") == "table"],
        "contracts": [runtime["contract"]],
    })
    state = runtime["start"]()
    controls = state["_controls"]
    shutil.copyfile(bundle, tmp_path / "embed.js")
    embed_minimal_html(
        str(tmp_path / "selector.html"), views=[controls["page"]], requirejs=False,
        embed_url="./embed.js", title="Data Contract selector fixture",
        state=dependency_state([controls["page"]]),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with playwright.sync_playwright() as driver:
            instance = driver.chromium.launch(executable_path=browser, headless=True, args=["--no-sandbox"])
            page = instance.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            for width in (1613, 1050, 700):
                page.set_viewport_size({"width": width, "height": 1000})
                page.goto(f"http://127.0.0.1:{server.server_port}/selector.html")
                field = page.locator(".fabricops-searchable-selector input").first
                field.wait_for()
                page.add_script_tag(content=_FABRIC_NOTEBOOK_UX_JAVASCRIPT)
                # Reinstalling the safeguard must not add a second popup.
                page.add_script_tag(content=_FABRIC_NOTEBOOK_UX_JAVASCRIPT)
                field.click()
                popup = page.locator(".fabricops-selector-popup")
                popup.wait_for(state="visible")
                page.wait_for_timeout(150)  # pointer focus safeguard must leave the search usable
                assert field.evaluate("e => e === document.activeElement")
                geometry = page.evaluate("""() => {
                    const input = document.querySelector('.fabricops-searchable-selector input');
                    const popup = document.querySelector('.fabricops-selector-popup');
                    const a = input.getBoundingClientRect(), b = popup.getBoundingClientRect();
                    return {inputWidth:a.width, popupWidth:b.width, leftDelta:Math.abs(a.left-b.left),
                            overflow:popup.scrollWidth > popup.clientWidth,
                            pageOverflow:document.documentElement.scrollWidth > innerWidth,
                            bounded:popup.clientHeight <= 320 && popup.scrollHeight > popup.clientHeight};
                }""")
                assert abs(geometry["inputWidth"] - geometry["popupWidth"]) < 2, geometry
                assert geometry["leftDelta"] < 2 and not geometry["overflow"] and not geometry["pageOverflow"]
                assert geometry["bounded"]
                assert popup.count() == 1
                if os.environ.get("FABRICOPS_WIDGET_SCREENSHOT_DIR"):
                    page.screenshot(path=str(Path(os.environ["FABRICOPS_WIDGET_SCREENSHOT_DIR"]) / f"dataset-popup-{width}.png"))
                field.fill("inventory_movements")
                assert popup.locator('[role="option"]').count() == 1
                label = popup.locator('[role="option"]').inner_text()
                field.press("ArrowDown")
                assert field.get_attribute("aria-activedescendant")
                field.press("Enter")
                assert field.input_value() == label
                assert popup.count() == 0
                assert field.get_attribute("aria-expanded") == "false"
                field.click()
                field.fill("no matching dataset")
                assert popup.is_hidden()
                field.fill("")
                popup.wait_for(state="visible")
                field.press("Escape")
                assert popup.count() == 0
                field.click()
                popup.get_by_role("option", name=label, exact=True).click()
                assert field.input_value() == label
                assert popup.count() == 0
                field.click()
                field.press("Tab")
                assert popup.count() <= 1  # next searchable field may open its own menu
                page.locator("body").click(position={"x": 2, "y": 2})
                assert popup.count() == 0
            assert not errors
            instance.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        controls["page"].close()


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
