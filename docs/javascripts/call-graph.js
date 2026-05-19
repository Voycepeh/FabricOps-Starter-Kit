(function () {
  async function initCallGraph() {
    const canvas = document.getElementById('call-graph-canvas');
    if (!canvas) return;
    const response = await fetch('/FabricOps-Starter-Kit/reference/dependency-metadata.json');
    const data = await response.json();
    const callables = data.callables || {};
    const nodes = [];
    const edges = [];
    const modules = [...new Set(Object.values(callables).map((c) => c.module))];
    const moduleColor = Object.fromEntries(modules.map((m, i) => [m, `hsl(${(i * 47) % 360} 60% 75%)`]));
    for (const [id, c] of Object.entries(callables)) {
      nodes.push({ id, label: c.short_name || c.callable, color: moduleColor[c.module], title: `${id}\nModule: ${c.module}\nInbound: ${c.used_by_count}\nOutbound: ${c.calls_count}` });
      for (const target of c.calls || []) edges.push({ from: id, to: target, arrows: 'to' });
    }
    const network = new vis.Network(canvas, { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) }, { interaction: { hover: true, dragNodes: true }, physics: { stabilization: true } });
    network.on('click', (params) => {
      if (params.nodes.length) {
        const n = callables[params.nodes[0]];
        if (n && n.docs_url) window.location.href = n.docs_url;
      }
    });
    const query = new URLSearchParams(window.location.search).get('function');
    const searchInput = document.getElementById('call-graph-search');
    function focus(term) {
      if (!term) return;
      const found = Object.keys(callables).find((qn) => qn === term || qn.endsWith(`.${term}`));
      if (found) network.focus(found, { scale: 1.2, animation: true });
    }
    if (searchInput) searchInput.addEventListener('change', (e) => focus(e.target.value.trim()));
    if (query) focus(query);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCallGraph);
  else initCallGraph();
})();
