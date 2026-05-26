# Interactive call graph

Explore callable relationships across modules.

<div class="call-graph-page">
<div class="call-graph-toolbar">
  <label for="call-graph-search"><strong>Search function:</strong></label>
  <input id="call-graph-search" type="search" placeholder="e.g. load_fabric_config or fabricops_kit.config.load_fabric_config" />
  <div id="call-graph-search-results" class="call-graph-search-results" aria-live="polite"></div>
  <p id="call-graph-search-empty" class="call-graph-search-empty" hidden>No matching function found.</p>
</div>
<div class="call-graph-legend" aria-label="Call graph legend">
<span class="call-graph-legend-item is-selected">selected</span>
<span class="call-graph-legend-item is-connector">connector</span>
<span class="call-graph-legend-item is-helper">internal helper</span>
<span class="call-graph-legend-item is-inbound">inbound</span>
<span class="call-graph-legend-item is-outbound">outbound</span>
</div>
<div id="call-graph-canvas" class="call-graph-canvas" aria-label="Interactive call graph canvas" tabindex="0"></div>
</div>

> Tip: add `?function=fabricops_kit.config.load_fabric_config` to preselect a node.

<!-- pages-redeploy: trigger after PR #321 -->
