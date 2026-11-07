"""Browser regression for delayed FabricOps callback output scrolling a notebook."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from fabricops_kit.widgets import _FABRIC_NOTEBOOK_UX_JAVASCRIPT


_SCROLL_SMOKE = r"""
(async () => {
  const check = (ok, message) => { if (!ok) throw new Error(message); };
  const settle = () => new Promise(resolve => setTimeout(resolve, 150));
  const setup = async (nested) => {
    document.body.innerHTML = `${nested ? '<div id="notebook" style="height:700px;overflow:auto">' : ''}
      <div style="height:1200px"></div><div id="output"><div class="fabricops-form" style="height:500px">
      <select id="columns" size="5"><option>A</option><option>B</option></select><input id="keyboard">
      <div id="panel" style="height:100px;overflow:auto"><div style="height:600px">Editor</div></div>
      </div></div><div style="height:2000px"></div>${nested ? '</div>' : ''}`;
    await settle();
    if (nested) document.getElementById('notebook').scrollTop = 1000;
    else window.scrollTo(0, 1000);
    await settle();
    const select = document.getElementById('columns');
    select.dispatchEvent(new Event('pointerdown', {bubbles:true}));
    select.dispatchEvent(new Event('change', {bubbles:true}));
    return {select, top:window.scrollY, nestedTop:document.getElementById('notebook')?.scrollTop || 0};
  };
  try {
    for (const nested of [false, true]) {
      const before = await setup(nested);
      // The old 50/100 ms focus workaround has finished before this output arrives.
      await settle();
      const output = document.createElement('div');
      output.textContent = 'Late callback output';
      output.style.height = '900px';
      document.getElementById('output').append(output);
      output.scrollIntoView({block:'end'});
      before.select.focus();
      document.getElementById('panel').scrollTop = 150;
      await settle();
      await settle();
      check(Math.abs(window.scrollY-before.top) <= 1, 'callback moved notebook window');
      check(Math.abs((document.getElementById('notebook')?.scrollTop || 0)-before.nestedTop) <= 1,
            'callback moved notebook scroll container');
      check(document.getElementById('panel').scrollTop === 150, 'guard moved the internal editor pane');
    }
    const late = await setup(false);
    const stream = document.createElement('pre');
    document.getElementById('output').append(stream);
    // A second callback can append to an existing output long after the click.
    await new Promise(resolve => setTimeout(resolve, 1200));
    stream.textContent = 'Profiling progress\n'.repeat(100);
    stream.scrollIntoView({block:'end'});
    await settle();
    await settle();
    check(window.scrollY === late.top, 'late output appended to an existing stream moved the notebook');
    for (const action of ['wheel', 'touchmove', 'keydown', 'outside']) {
      await setup(false);
      if (action === 'outside') document.body.dispatchEvent(new Event('pointerdown', {bubbles:true}));
      else if (action === 'keydown') document.dispatchEvent(new KeyboardEvent('keydown', {key:'Tab', bubbles:true}));
      else document.dispatchEvent(new Event(action, {bubbles:true}));
      window.scrollTo(0, 1400);
      document.getElementById('output').append(document.createTextNode('Late output after user navigation'));
      document.getElementById('keyboard').focus({preventScroll:true});
      await settle();
      await settle();
      check(window.scrollY === 1400, `guard fought deliberate ${action} navigation`);
      check(document.activeElement === document.getElementById('keyboard'), `guard blurred focus after ${action}`);
    }
    await setup(false);
    document.getElementById('columns').dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowDown', bubbles:true}));
    const keyboard = document.getElementById('keyboard');
    keyboard.focus({preventScroll:true});
    keyboard.dispatchEvent(new Event('change', {bubbles:true}));
    await settle();
    check(document.activeElement === keyboard, 'keyboard form interaction lost focus');
    document.body.dataset.scrollSmoke = JSON.stringify({ok:true});
  } catch (error) {
    document.body.dataset.scrollSmoke = JSON.stringify({ok:false,error:String(error.stack || error)});
  }
})();
"""


def test_delayed_output_preserves_notebook_scroll_and_user_navigation():
    """Preserve outer scroll for callbacks while respecting keyboard, touch, wheel, and pane scrolling."""
    candidates = [os.environ.get("FABRICOPS_BROWSER"), shutil.which("chromium"),
                  shutil.which("google-chrome"), shutil.which("chromium-browser")]
    browser = next((str(path) for path in candidates if path and Path(path).exists()), None)
    if browser is None:
        pytest.skip("A Chromium-family browser is required for the notebook scroll regression.")
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as runtime:
        instance = runtime.chromium.launch(executable_path=browser, headless=True,
                                           args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            page = instance.new_page(viewport={"width": 1280, "height": 900})
            page.set_content('<!doctype html><html><body style="margin:0"></body></html>')
            page.add_script_tag(content=_FABRIC_NOTEBOOK_UX_JAVASCRIPT)
            page.add_script_tag(content=_SCROLL_SMOKE)
            page.wait_for_function("document.body.dataset.scrollSmoke !== undefined", timeout=15000)
            outcome = json.loads(page.locator("body").get_attribute("data-scroll-smoke"))
            assert outcome["ok"], outcome
        finally:
            instance.close()
