(function () {
  const MAX_SEARCH_RESULTS = 15;

  async function initCallGraph() {
    const canvas = document.getElementById('call-graph-canvas');
    if (!canvas) return;
    const setStatus = (msg) => {
      canvas.innerHTML = `<div class="call-graph-status">${msg}</div>`;
    };
    setStatus('Loading call graph...');

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

    const nodeRecords = [];
    const edgeRecords = [];
    const inbound = new Map();
    const outbound = new Map();
    const byModule = new Map();

    for (const [id, c] of callableEntries) {
      const module = c.module || 'unknown';
      const shortName = c.short_name || c.callable || id;
      const rec = { id, qn: id, label: shortName, module, searchLabel: `${module}.${shortName}` };
      nodeRecords.push(rec);
      if (!byModule.has(module)) byModule.set(module, []);
      byModule.get(module).push(rec);
      outbound.set(id, new Set());
      inbound.set(id, new Set());
    }

    const knownNodes = new Set(nodeRecords.map((n) => n.id));
    for (const [id, c] of callableEntries) {
      const calls = Array.isArray(c.calls) ? c.calls : [];
      for (const target of calls) {
        if (!knownNodes.has(target)) continue;
        edgeRecords.push({ id: `${id}->${target}`, from: id, to: target });
        outbound.get(id).add(target);
        inbound.get(target).add(id);
      }
    }

    const functionToChip = new Map();
    canvas.innerHTML = '';
    const viewport = document.createElement('div');
    viewport.className = 'call-graph-viewport';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('call-graph-edges');
    const modulesGrid = document.createElement('div');
    modulesGrid.className = 'call-graph-modules';

    for (const moduleName of [...byModule.keys()].sort()) {
      const card = document.createElement('section');
      card.className = 'call-graph-module';
      card.dataset.module = moduleName;
      const title = document.createElement('h3');
      title.className = 'call-graph-module-title';
      title.textContent = moduleName;
      card.appendChild(title);
      const list = document.createElement('div');
      list.className = 'call-graph-function-list';
      for (const rec of byModule.get(moduleName).sort((a, b) => a.label.localeCompare(b.label))) {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'call-graph-function-chip';
        chip.dataset.function = rec.qn;
        chip.dataset.module = moduleName;
        chip.textContent = rec.label;
        chip.title = rec.qn;
        chip.addEventListener('click', () => selectNode(rec.qn));
        list.appendChild(chip);
        functionToChip.set(rec.qn, chip);
      }
      card.appendChild(list);
      modulesGrid.appendChild(card);
    }

    viewport.appendChild(svg);
    viewport.appendChild(modulesGrid);
    canvas.appendChild(viewport);

    const searchInput = document.getElementById('call-graph-search');
    const resultsRoot = document.getElementById('call-graph-search-results');
    const noMatchEl = document.getElementById('call-graph-search-empty');
    let selectedNodeId = null;

    function getMatches(term) { /* unchanged behavior */
      const query = (term || '').trim().toLowerCase();
      if (!query) return [];
      const exact = []; const prefix = []; const includes = [];
      for (const rec of nodeRecords) {
        const qn = rec.qn.toLowerCase(); const name = rec.label.toLowerCase(); const qnByModule = rec.searchLabel.toLowerCase();
        if (qn === query || qnByModule === query || name === query) exact.push(rec);
        else if (qn.endsWith(`.${query}`) || qnByModule.endsWith(`.${query}`) || name.startsWith(query)) prefix.push(rec);
        else if (qn.includes(query) || qnByModule.includes(query) || name.includes(query)) includes.push(rec);
      }
      return [...exact, ...prefix, ...includes].slice(0, MAX_SEARCH_RESULTS);
    }

    function renderDropdown(matches) {
      if (!resultsRoot) return;
      resultsRoot.innerHTML = '';
      if (!matches.length) return;
      const list = document.createElement('ul'); list.className = 'call-graph-search-list';
      for (const rec of matches) {
        const item = document.createElement('li'); const button = document.createElement('button');
        button.type = 'button'; button.className = 'call-graph-search-option'; button.textContent = rec.searchLabel;
        button.addEventListener('click', () => selectNode(rec.qn)); item.appendChild(button); list.appendChild(item);
      }
      resultsRoot.appendChild(list);
    }
    function setNoMatchVisibility(show) { if (noMatchEl) noMatchEl.hidden = !show; }
    function updateUrlForSelection(id) { const url = new URL(window.location.href); url.searchParams.set('function', id); window.history.replaceState({}, '', url); }

    function refreshEdges() {
      const vbox = viewport.getBoundingClientRect();
      svg.setAttribute('viewBox', `0 0 ${vbox.width} ${vbox.height}`);
      svg.innerHTML = '';
      for (const edge of edgeRecords) {
        const fromChip = functionToChip.get(edge.from); const toChip = functionToChip.get(edge.to);
        if (!fromChip || !toChip) continue;
        if (fromChip.classList.contains('is-hidden') || toChip.classList.contains('is-hidden')) continue;
        const from = fromChip.getBoundingClientRect(); const to = toChip.getBoundingClientRect();
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', String(from.right - vbox.left));
        line.setAttribute('y1', String((from.top + from.bottom) / 2 - vbox.top));
        line.setAttribute('x2', String(to.left - vbox.left));
        line.setAttribute('y2', String((to.top + to.bottom) / 2 - vbox.top));
        line.classList.add('call-graph-edge');
        if (selectedNodeId && edge.from === selectedNodeId) line.classList.add('is-outbound');
        else if (selectedNodeId && edge.to === selectedNodeId) line.classList.add('is-inbound');
        else if (selectedNodeId) line.classList.add('is-related');
        svg.appendChild(line);
      }
    }

    function applySelectionStyles(id) {
      const related = new Set([id]);
      (inbound.get(id) || []).forEach((n) => related.add(n));
      (outbound.get(id) || []).forEach((n) => related.add(n));
      const relatedModules = new Set([...related].map((qn) => callables[qn]?.module || 'unknown'));

      for (const [qn, chip] of functionToChip.entries()) {
        chip.classList.remove('is-selected', 'is-inbound', 'is-outbound', 'is-hidden');
        if (!related.has(qn)) chip.classList.add('is-hidden');
        if (qn === id) chip.classList.add('is-selected');
        else if ((inbound.get(id) || new Set()).has(qn)) chip.classList.add('is-inbound');
        else if ((outbound.get(id) || new Set()).has(qn)) chip.classList.add('is-outbound');
      }
      for (const card of modulesGrid.querySelectorAll('.call-graph-module')) {
        const active = relatedModules.has(card.dataset.module);
        card.classList.toggle('is-muted', !active);
      }
      refreshEdges();
    }

    function selectNode(id) {
      if (!knownNodes.has(id)) return;
      selectedNodeId = id;
      applySelectionStyles(id);
      updateUrlForSelection(id);
      const selectedChip = functionToChip.get(id);
      if (selectedChip) {
        selectedChip.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
      }
      const selectedRecord = nodeRecords.find((rec) => rec.qn === id);
      if (searchInput && selectedRecord) searchInput.value = selectedRecord.searchLabel;
      renderDropdown([]); setNoMatchVisibility(false);
    }

    function submitSearch(rawTerm) { const term = (rawTerm || '').trim(); if (!term) return; const matches = getMatches(term); renderDropdown(matches); if (!matches.length) { setNoMatchVisibility(true); return; } setNoMatchVisibility(false); const exact = matches.find((m) => m.qn === term || m.searchLabel === term || m.label === term); selectNode((exact || matches[0]).qn); }

    if (searchInput) {
      searchInput.addEventListener('input', (e) => { const matches = getMatches(e.target.value); renderDropdown(matches); setNoMatchVisibility(Boolean(e.target.value.trim()) && !matches.length); });
      searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); submitSearch(searchInput.value); } });
    }

    window.addEventListener('resize', refreshEdges);
    const query = new URLSearchParams(window.location.search).get('function');
    if (query) submitSearch(query);
    else refreshEdges();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCallGraph);
  else initCallGraph();
})();
