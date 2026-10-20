"""Headless-browser regression coverage for the generated call-flow dashboard."""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "docs/assets/public-function-call-flows-dashboard.html"
DATA = ROOT / "docs/reference/_data/public-function-call-flows.json"
ARTIFACTS = ROOT / "docs/reference/_data/generated-artifacts.json"
COMPATIBILITY = ROOT / "docs/reference/_data/public-api-compatibility.json"


def _browser_executable() -> str | None:
    """Return an installed Chromium-family browser suitable for headless CI."""
    candidates = [
        os.environ.get("FABRICOPS_BROWSER"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("chrome"),
        shutil.which("msedge"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((str(path) for path in candidates if path and Path(path).exists()), None)


SMOKE_SCRIPT = r"""
<script>
(() => {
  const errors = [];
  const originalConsoleError = console.error.bind(console);
  console.error = (...args) => { errors.push(args.map(String).join(' ')); originalConsoleError(...args); };
  addEventListener('error', event => errors.push(String(event.message || event.error || 'window error')));
  addEventListener('unhandledrejection', event => errors.push(String(event.reason || 'unhandled rejection')));
  const started = performance.now();
  const finish = result => document.body.dataset.browserSmoke = JSON.stringify(result);
  const fail = error => finish({ok:false,error:String(error && error.stack || error),errors});
  const timer = setInterval(() => {
    if (!document.getElementById('dataLoadStatus')?.textContent.includes('Loaded')) return;
    if (document.getElementById('compatBaseline')?.options.length < 2) return;
    clearInterval(timer);
    try {
      const check = (condition, message) => { if (!condition) throw new Error(message); };
      check(errors.length === 0, `console errors: ${errors.join(' | ')}`);
      check(DATA.metadata.schema === 'fabricops_public_function_call_flows_v4', 'v4 JSON was not loaded');

      const renderedRows = [...document.querySelectorAll('[data-public-flow-row]')];
      check(renderedRows.length > 1, 'public function rows did not render');
      const initialQn = selectedPublic.qualified_name;
      const initialTree = document.getElementById('selected-call-tree').textContent;
      renderedRows.find(row => row.dataset.publicFlowRow !== initialQn).click();
      check(selectedPublic.qualified_name !== initialQn, 'public function selection did not change');
      check(document.getElementById('selected-call-tree').textContent !== initialTree, 'selected call graph did not change');

      const recursiveRoot = DATA.public_functions.find(row => row.function_name === 'orchestrate_read');
      check(recursiveRoot, 'recursive smoke-test root is missing');
      selectPublic(recursiveRoot.qualified_name, {scrollToPanel:false});
      check(recursiveRoot.flow.some(row => row.recursive), 'recursive relationship was not bounded and marked');
      const toggle = document.querySelector('[data-tree-node-toggle]');
      check(toggle, 'expand/collapse control is missing');
      const beforeExpanded = toggle.getAttribute('aria-expanded');
      const toggleKey = toggle.dataset.treeNodeToggle;
      toggle.click();
      const updatedToggle = document.querySelector(`[data-tree-node-toggle="${CSS.escape(toggleKey)}"]`);
      check(updatedToggle && updatedToggle.getAttribute('aria-expanded') !== beforeExpanded, 'helper branch did not toggle');

      const search = document.getElementById('searchBox');
      search.value = 'orchestrate_read'; search.dispatchEvent(new Event('input', {bubbles:true}));
      check(publicRows.length === 1 && publicRows[0].function_name === 'orchestrate_read', 'function search failed');
      search.value = ''; search.dispatchEvent(new Event('input', {bubbles:true}));
      const lifecycle = document.getElementById('lifecycleFilter');
      lifecycle.value = 'live'; lifecycle.dispatchEvent(new Event('input', {bubbles:true}));
      check(publicRows.length > 0 && publicRows.every(row => lifecycleValue(row) === 'live'), 'lifecycle filter failed');
      lifecycle.value = ''; lifecycle.dispatchEvent(new Event('input', {bubbles:true}));
      const signal = document.getElementById('signalFilter');
      const signalRoot = DATA.public_functions.find(row => publicSignalsForFunction(row).length > 0);
      check(signalRoot, 'signal filter smoke-test root is missing');
      const signalName = publicSignalsForFunction(signalRoot)[0];
      selectPublic(signalRoot.qualified_name, {scrollToPanel:false});
      signal.value = signalName; signal.dispatchEvent(new Event('input', {bubbles:true}));
      check(publicRows.length > 0 && publicRows.every(row => hasPublicSignal(row, signalName)), 'signal filter failed');
      signal.value = ''; signal.dispatchEvent(new Event('input', {bubbles:true}));

      showWorkflow('compatibility');
      const fixtureChange = (name, before, after, classification, change_type='modified') => ({qualified_name:name,lifecycle_before:before,lifecycle_after:after,classification,change_type,signature_before:'demo(value)',signature_after:after?'demo(value, option = None)':null,reasons:['Reason for '+name]});
      const releaseFixture = [
        fixtureChange('removed_live','Live',null,'potentially_breaking','removed'),
        fixtureChange('demoted_live','Live','Preview','potentially_breaking'),
        fixtureChange('preview_break','Preview','Live','potentially_breaking'),
        fixtureChange('preview_removed','Preview',null,'review_required','removed'),
        fixtureChange('compatible_live','Live','Live','nonbreaking'),
        {...fixtureChange('review_live','Live','Live','review_required'),signature_before:'demo(value, /, *, flag = None)',signature_after:'demo(value, *, flag = None)'},
        fixtureChange('new_live',null,'Live','nonbreaking','added'),
        fixtureChange('unreleased_preview',null,'Preview','nonbreaking','added'),
        fixtureChange('old_discontinued','Discontinued','Live','nonbreaking'),
        fixtureChange('unknown','Unknown','Live','review_required')
      ];
      renderReleaseImpact(releaseFixture);
      const breakingText = document.getElementById('releaseBreakingResults').textContent;
      const usedText = document.getElementById('compatResults').textContent;
      check(document.querySelectorAll('#releaseBreakingResults article').length === 2, 'Live question must use released lifecycle');
      check(breakingText.includes('removed_live') && breakingText.includes('demoted_live') && !breakingText.includes('preview_break'), 'Live question selected incorrect functions');
      check(document.querySelectorAll('#compatResults article').length === 6, 'used-functions question selected incorrect functions');
      check(usedText.includes('preview_removed') && usedText.includes('preview_break'), 'released Preview changes missing');
      check(['Breaking','Compatible','Needs review'].every(label=>usedText.includes(label)), 'release status labels missing');
      check(!usedText.includes('new_live') && !usedText.includes('unreleased_preview') && !usedText.includes('old_discontinued') && !usedText.includes('unknown'), 'excluded functions appeared');
      check(document.querySelectorAll('#compatResults details:not([open])').length === 6, 'function details should start collapsed');
      check(usedText.includes('Reason for compatible_live'), 'brief function reasons missing');
      check(usedText.includes('demo(value, /, *, flag = None)') && usedText.includes('demo(value, *, flag = None)'), 'exact released and main signatures must preserve parameter kinds');
      check(getComputedStyle(document.querySelector('#compatResults pre')).whiteSpace === 'pre-wrap', 'long signatures must wrap on mobile');
      renderReleaseImpact([]);
      check(document.getElementById('releaseBreakingResults').textContent === 'No breaking Live/Public function changes found.', 'empty Live question message incorrect');
      compareMainImpact();
      const expectedRelease = releaseQuestionChanges(currentCompatComparison.changes);
      check(document.querySelectorAll('#compatResults article').length === expectedRelease.used.length, 'production to main comparison not rendered');
      const compatBaseline = document.getElementById('compatBaseline');
      const compatTarget = document.getElementById('compatTarget');
      check([...compatBaseline.options].some(option => option.value === 'v0.1.0'), 'v0.1.0 baseline option is missing');
      check([...compatTarget.options].some(option => option.value === 'v0.2.0'), 'v0.2.0 target option is missing');
      check(!compatBaseline.textContent.includes('PR #1613'), 'stale PR selector remains');
      compatBaseline.value = 'v0.1.0'; compatTarget.value = 'v0.2.0';
      document.getElementById('compatCompare').click();
      check(document.querySelectorAll('.compatibility-record').length > 0, 'release comparison did not render');
      check(document.querySelectorAll('#historicalResults .compatibility-record').length > 0, 'historical comparison results are not visible in their panel');
      check(document.querySelector('.compatibility-summary').textContent.includes('Potentially breaking'), 'compatibility summary is missing');
      check(document.getElementById('compatStatus').textContent.includes('source-backed'), 'source-backed status is missing');
      check(new URLSearchParams(location.search).get('baseline') === 'v0.1.0', 'baseline URL parameter was not retained');
      check(new URLSearchParams(location.search).get('compare') === 'v0.2.0', 'compare URL parameter was not retained');
      const compatLifecycle = document.getElementById('compatLifecycle');
      compatLifecycle.value = 'Live'; compatLifecycle.dispatchEvent(new Event('change', {bubbles:true}));
      check(new URLSearchParams(location.search).get('compatLifecycle') === 'Live', 'lifecycle URL parameter was not retained');
      document.getElementById('releaseImpactTab').click();
      check(currentCompatComparison.target === 'main', 'history comparison leaked into release view');
      check(!['baseline','compare','compatLifecycle'].some(key=>new URLSearchParams(location.search).has(key)), 'historical URL parameters must be cleared on return to release view');
      check(document.querySelectorAll('#compatResults article').length === expectedRelease.used.length, 'release view not restored after history');
      showWorkflow('architecture');

      selectPublic(recursiveRoot.qualified_name, {scrollToPanel:false});
      const fullInventoryCount = uniqInventory(selectedPublic.flow).length;
      const helper = uniqInventory(selectedPublic.flow).find(row => row.depth > 0 && row.function_type !== 'public_dependency');
      check(helper, 'scoped inventory helper is missing');
      setScopeRootFromCallFlowCard(helper.qualified_name);
      check(currentScopeRootFunction.qualified_name === helper.qualified_name, 'helper scope was not selected');
      check(inventoryRows.length <= fullInventoryCount, 'scoped inventory grew beyond the full flow');
      resetScopeToPublicFunction();
      check(currentScopeRootFunction.qualified_name === selectedPublic.qualified_name, 'public inventory scope did not reset');

      const downloads = [];
      download = (name, text, type) => downloads.push({name,text,type});
      const scopeControl = document.getElementById('exportScope');
      for (const scope of ['full_selected_flow','current_scoped_helper_flow','visible_inventory_rows_only']) {
        scopeControl.value = scope; scopeControl.dispatchEvent(new Event('change', {bubbles:true}));
        document.getElementById('downloadPacket').click();
        const payload = JSON.parse(downloads.at(-1).text);
        check(payload.evidence_packet.export_scope === scope, `wrong exported scope for ${scope}`);
        check(payload.evidence_packet.exported_function_count === payload.evidence_packet.exported_functions.length, `wrong exported count for ${scope}`);
      }
      selectedInventory.clear();
      selectedInventory.add(uniqInventory(selectedPublic.flow)[0].qualified_name);
      scopeControl.value = 'checked_functions_only'; scopeControl.dispatchEvent(new Event('change', {bubbles:true}));
      document.getElementById('downloadPacket').click();
      const checked = JSON.parse(downloads.at(-1).text).evidence_packet;
      check(checked.export_scope === 'checked_functions_only' && checked.exported_function_count === 1, 'checked export scope did not match selection');
      document.getElementById('downloadSimplifyPacket').click();
      check(JSON.parse(downloads.at(-1).text).evidence_packet.prompt_task === 'simplify_preserve_behaviour', 'simplify packet export failed');

      // Reproduce the screenshot's helper tree, including long dependent names.
      selectPublic(DATA.public_functions.find(row => row.function_name === 'create_data_agent').qualified_name, {scrollToPanel:false});
      const tree = document.getElementById('selected-call-tree');
      check(!/[Ââ]/.test(tree.textContent), 'call tree contains corrupted Unicode');
      check(tree.querySelector('.tree-toggle').textContent === '▾', 'expanded tree arrow is corrupted');
      check(tree.querySelector('.tree-toggle-placeholder').textContent === '•', 'leaf bullet is corrupted');
      const checkTreeBounds = () => {
        const bounds = tree.getBoundingClientRect();
        check(tree.scrollWidth <= tree.clientWidth + 1, 'helper content overflows the tree');
        tree.querySelectorAll('.tree-node, .tree-row-main, .tree-card-button, .tree-meta').forEach(element => {
          const rect = element.getBoundingClientRect();
          check(rect.right <= bounds.right + 1, 'helper content extends beyond tree bounds');
        });
      };
      checkTreeBounds();
      tree.querySelector('.tree-function').textContent = 'long_function_name_'.repeat(30);
      tree.querySelector('.tree-meta').textContent = 'long_dependent_function_'.repeat(40);
      checkTreeBounds();

      const filterColumns = getComputedStyle(document.querySelector('.filter-panel')).gridTemplateColumns.split(' ').length;
      const treeNameStyle = getComputedStyle(document.querySelector('.tree-function'));
      check(document.documentElement.scrollWidth <= window.innerWidth + 1, 'dashboard overflows the viewport');
      check(treeNameStyle.overflowWrap === 'anywhere', 'long tree function names are not allowed to wrap');
      check(window.innerWidth > 760 ? filterColumns > 1 : filterColumns === 1, 'responsive filter layout did not switch at the mobile breakpoint');
      finish({
        ok:true,
        errors,
        viewport_width:window.innerWidth,
        smoke_duration_ms:Number((performance.now()-started).toFixed(2)),
        navigation_duration_ms:Number(performance.getEntriesByType('navigation')[0]?.duration.toFixed(2) || 0),
        relationship_count:DATA.relationships.length,
        selected_graph_rows:selectedPublic.flow.length,
        exported_packets:downloads.length
      });
    } catch (error) { fail(error); }
  }, 25);
  setTimeout(() => { if (!document.body.dataset.browserSmoke) { clearInterval(timer); fail(new Error('dashboard load timed out')); } }, 12000);
})();
</script>
"""


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *args: object) -> None:
        """Keep successful browser smoke tests quiet."""


def _run_browser_smoke(tmp_path: Path, browser: str, width: int) -> dict[str, object]:
    """Serve an instrumented copy of the generated dashboard and return results."""
    assets = tmp_path / "docs/assets"
    data_dir = tmp_path / "docs/reference/_data"
    assets.mkdir(parents=True)
    data_dir.mkdir(parents=True)
    dashboard_html = DASHBOARD.read_text(encoding="utf-8").replace("</body>", f"{SMOKE_SCRIPT}</body>")
    (assets / DASHBOARD.name).write_text(dashboard_html, encoding="utf-8")
    shutil.copy2(DATA, data_dir / DATA.name)
    shutil.copy2(ARTIFACTS, data_dir / ARTIFACTS.name)
    shutil.copy2(COMPATIBILITY, data_dir / COMPATIBILITY.name)

    handler = partial(_QuietHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/docs/assets/{DASHBOARD.name}"
        profile = tmp_path / f"browser-profile-{width}"
        result = subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--user-data-dir={profile}",
                f"--window-size={width},900",
                "--virtual-time-budget=15000",
                "--dump-dom",
                url,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=35,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    match = re.search(r'data-browser-smoke="([^"]+)"', result.stdout)
    assert match, result.stdout[-3000:] + result.stderr[-3000:]
    return json.loads(html.unescape(match.group(1)))


@pytest.mark.parametrize("width", [1440, 390], ids=["desktop", "mobile"])
def test_generated_dashboard_browser_interactions_and_exports(tmp_path: Path, width: int) -> None:
    """Exercise v4 loading, navigation, filtering, scoping, exports, and layout."""
    browser = _browser_executable()
    if browser is None:
        pytest.skip("Chrome, Chromium, or Edge is required for dashboard browser coverage")

    result = _run_browser_smoke(tmp_path, browser, width)

    assert result["ok"] is True, result
    assert result["errors"] == []
    assert result["relationship_count"] > 0
    assert result["selected_graph_rows"] > 0
    assert result["exported_packets"] == 5
    print("dashboard browser benchmark", json.dumps(result, sort_keys=True))
