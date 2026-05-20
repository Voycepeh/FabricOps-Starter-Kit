(function () {
  const MAX_SEARCH_RESULTS = 15;

  async function initCallGraph() {
    const canvas = document.getElementById('call-graph-canvas');
    if (!canvas) return;
    const setStatus = (msg) => {
      canvas.innerHTML = `<div class="call-graph-status">${msg}</div>`;
    };
    setStatus('Loading call graph...');

    if (!window.vis || !window.vis.Network || !window.vis.DataSet) {
      setStatus('Unable to load graph library.');
      return;
    }

    const metadataUrl = new URL('../dependency-metadata.json', window.location.href);
    let data;
    try {
      const response = await fetch(metadataUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      data = await response.json();
    } catch (_err) {
      setStatus('Unable to load dependency metadata.');
      return;
    }

    const rawCallables = data && typeof data === 'object' ? data.callables : null;
    const callables = rawCallables && typeof rawCallables === 'object' ? rawCallables : {};
    const callableEntries = Object.entries(callables).filter(([, value]) => value && typeof value === 'object');
    if (!callableEntries.length) {
      setStatus('No callable nodes found.');
      return;
    }

    canvas.innerHTML = '';
    const modules = [...new Set(callableEntries.map(([, c]) => c.module || 'unknown'))];
    const moduleColor = Object.fromEntries(modules.map((m, i) => [m, `hsl(${(i * 47) % 360} 60% 75%)`]));

    const nodeRecords = [];
    const edgeRecords = [];
    const inbound = new Map();
    const outbound = new Map();

    for (const [id, c] of callableEntries) {
      const module = c.module || 'unknown';
      const shortName = c.short_name || c.callable || id;
      nodeRecords.push({
        id,
        qn: id,
        label: shortName,
        searchLabel: `${module}.${shortName}`,
        title: `${id}
Module: ${module}
Inbound: ${Number(c.used_by_count || 0)}
Outbound: ${Number(c.calls_count || 0)}`,
        color: moduleColor[module],
      });
      outbound.set(id, new Set());
      inbound.set(id, new Set());
    }

    const knownNodes = new Set(nodeRecords.map((n) => n.id));
    for (const [id, c] of callableEntries) {
      const calls = Array.isArray(c.calls) ? c.calls : [];
      for (const target of calls) {
        if (!knownNodes.has(target)) continue;
        edgeRecords.push({ id: `${id}->${target}`, from: id, to: target, arrows: 'to' });
        outbound.get(id).add(target);
        inbound.get(target).add(id);
      }
    }

    const nodes = new vis.DataSet(nodeRecords.map((n) => ({ id: n.id, label: n.label, color: n.color, title: n.title })));
    const edges = new vis.DataSet(edgeRecords);
    const network = new vis.Network(
      canvas,
      { nodes, edges },
      {
        interaction: { hover: true, dragNodes: true, zoomView: true, dragView: true },
        physics: { stabilization: true },
      },
    );

    const searchInput = document.getElementById('call-graph-search');
    const resultsRoot = document.getElementById('call-graph-search-results');
    const noMatchEl = document.getElementById('call-graph-search-empty');
    let selectedNodeId = null;

    const baseNodeStyles = new Map(nodeRecords.map((n) => [n.id, { color: n.color, font: { color: '#1d1d1d', size: 14 }, hidden: false } ]));

    function getMatches(term) {
      const query = (term || '').trim().toLowerCase();
      if (!query) return [];
      const exact = [];
      const prefix = [];
      const includes = [];
      for (const rec of nodeRecords) {
        const qn = rec.qn.toLowerCase();
        const name = rec.label.toLowerCase();
        const qnByModule = rec.searchLabel.toLowerCase();
        if (qn === query || qnByModule === query || name === query) {
          exact.push(rec);
        } else if (qn.endsWith(`.${query}`) || qnByModule.endsWith(`.${query}`) || name.startsWith(query)) {
          prefix.push(rec);
        } else if (qn.includes(query) || qnByModule.includes(query) || name.includes(query)) {
          includes.push(rec);
        }
      }
      return [...exact, ...prefix, ...includes].slice(0, MAX_SEARCH_RESULTS);
    }

    function renderDropdown(matches) {
      if (!resultsRoot) return;
      resultsRoot.innerHTML = '';
      if (!matches.length) return;
      const list = document.createElement('ul');
      list.className = 'call-graph-search-list';
      for (const rec of matches) {
        const item = document.createElement('li');
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'call-graph-search-option';
        button.textContent = rec.searchLabel;
        button.addEventListener('click', () => selectNode(rec.qn));
        item.appendChild(button);
        list.appendChild(item);
      }
      resultsRoot.appendChild(list);
    }

    function setNoMatchVisibility(show) {
      if (!noMatchEl) return;
      noMatchEl.hidden = !show;
    }

    function updateUrlForSelection(id) {
      const url = new URL(window.location.href);
      url.searchParams.set('function', id);
      window.history.replaceState({}, '', url);
    }

    function applySelectionStyles(id) {
      const highlight = new Set([id]);
      (inbound.get(id) || []).forEach((n) => highlight.add(n));
      (outbound.get(id) || []).forEach((n) => highlight.add(n));

      nodes.update(nodeRecords.map((rec) => {
        const base = baseNodeStyles.get(rec.id) || {};
        if (!highlight.has(rec.id)) {
          return { id: rec.id, hidden: true };
        }
        if (rec.id === id) {
          return {
            id: rec.id,
            hidden: false,
            borderWidth: 4,
            color: { background: '#f8d66d', border: '#7f4f00' },
            font: { color: '#2b2b2b', size: 16, bold: true },
          };
        }
        return {
          id: rec.id,
          hidden: false,
          borderWidth: 1,
          color: base.color,
          font: base.font,
        };
      }));

      edges.update(edgeRecords.map((edge) => {
        const show = highlight.has(edge.from) && highlight.has(edge.to);
        const connected = edge.from === id || edge.to === id;
        return {
          id: edge.id,
          hidden: !show,
          width: connected ? 2 : 1,
          color: connected ? '#1f5faa' : '#b4b8c5',
        };
      }));
    }

    function selectNode(id) {
      if (!knownNodes.has(id)) return;
      selectedNodeId = id;
      applySelectionStyles(id);
      network.selectNodes([id]);
      network.focus(id, { scale: 1.2, animation: { duration: 280, easingFunction: 'easeInOutQuad' } });
      updateUrlForSelection(id);
      const selectedRecord = nodeRecords.find((rec) => rec.qn === id);
      if (searchInput && selectedRecord) searchInput.value = selectedRecord.searchLabel;
      renderDropdown([]);
      setNoMatchVisibility(false);
    }

    function submitSearch(rawTerm) {
      const term = (rawTerm || '').trim();
      if (!term) return;
      const matches = getMatches(term);
      renderDropdown(matches);
      if (!matches.length) {
        setNoMatchVisibility(true);
        return;
      }
      setNoMatchVisibility(false);
      const exact = matches.find((m) => m.qn === term || m.searchLabel === term || m.label === term);
      selectNode((exact || matches[0]).qn);
    }

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const matches = getMatches(e.target.value);
        renderDropdown(matches);
        setNoMatchVisibility(Boolean(e.target.value.trim()) && !matches.length);
      });
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          submitSearch(searchInput.value);
        }
      });
    }

    network.on('doubleClick', (params) => {
      if (params.nodes.length) {
        const node = callables[params.nodes[0]];
        if (node && node.docs_url) window.location.href = node.docs_url;
      }
    });

    const query = new URLSearchParams(window.location.search).get('function');
    if (query) submitSearch(query);
    else if (!selectedNodeId) {
      edges.update(edgeRecords.map((edge) => ({ id: edge.id, hidden: false, width: 1, color: '#b4b8c5' })));
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCallGraph);
  else initCallGraph();
})();
