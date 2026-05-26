(function () {
  const MAX_SEARCH_RESULTS = 15;
  async function initCallGraph() {
    const canvas = document.getElementById('call-graph-canvas');
    if (!canvas) return;
    const setStatus = (msg) => { canvas.innerHTML = `<div class="call-graph-status">${msg}</div>`; };
    setStatus('Loading call graph...');

    const metadataUrl = new URL('../dependency-metadata.json', window.location.href);
    let data;
    try { const r = await fetch(metadataUrl); if (!r.ok) throw new Error(); data = await r.json(); }
    catch (_err) { setStatus('Unable to load dependency metadata.'); return; }

    const callables = data?.callables && typeof data.callables === 'object' ? data.callables : {};
    const entries = Object.entries(callables).filter(([, v]) => v && typeof v === 'object');
    if (!entries.length) { setStatus('No callable nodes found.'); return; }

    const nodeRecords = []; const edgeRecords = []; const moduleEdges = new Map(); const inbound = new Map(); const outbound = new Map(); const byModule = new Map();
    for (const [id, c] of entries) {
      const module = c.module || 'unknown'; const shortName = c.short_name || c.callable || id;
      const rec = { id, qn: id, label: shortName, module, searchLabel: `${module}.${shortName}` };
      nodeRecords.push(rec); if (!byModule.has(module)) byModule.set(module, []); byModule.get(module).push(rec); inbound.set(id, new Set()); outbound.set(id, new Set());
    }
    const knownNodes = new Set(nodeRecords.map((n) => n.id));
    for (const [id, c] of entries) for (const target of (Array.isArray(c.calls) ? c.calls : [])) if (knownNodes.has(target)) { edgeRecords.push({ id: `${id}->${target}`, from: id, to: target }); outbound.get(id).add(target); inbound.get(target).add(id); const srcModule = c.module || 'unknown'; const tgtModule = callables[target]?.module || 'unknown'; if (srcModule !== tgtModule) moduleEdges.set(`${srcModule}->${tgtModule}`, { from: srcModule, to: tgtModule }); }

    canvas.innerHTML = '';
    const toolbar = document.createElement('div'); toolbar.className = 'call-graph-view-toggle'; toolbar.innerHTML = '<button type="button" data-mode="function">Relationship view</button><button type="button" data-mode="full">Full map</button><button type="button" data-action="clear" hidden>Clear selection</button>'; canvas.appendChild(toolbar);
    const viewport = document.createElement('div'); viewport.className = 'call-graph-viewport';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.classList.add('call-graph-edges');
    const modulesGrid = document.createElement('div'); modulesGrid.className = 'call-graph-modules';
    const focusedLayout = document.createElement('div'); focusedLayout.className = 'call-graph-focused';
    viewport.append(svg, modulesGrid, focusedLayout); canvas.appendChild(viewport);

    const functionToChip = new Map();
    for (const moduleName of [...byModule.keys()].sort()) {
      const card = document.createElement('section'); card.className = 'call-graph-module'; card.dataset.module = moduleName;
      card.innerHTML = `<h3 class="call-graph-module-title">${moduleName}</h3>`;
      const list = document.createElement('div'); list.className = 'call-graph-function-list';
      for (const rec of byModule.get(moduleName).sort((a, b) => a.label.localeCompare(b.label))) {
        const chip = document.createElement('button'); chip.type = 'button'; chip.className = 'call-graph-function-chip'; chip.dataset.function = rec.qn; chip.dataset.module = moduleName; chip.textContent = rec.label; chip.title = rec.qn;
        chip.addEventListener('click', () => selectNode(rec.qn)); list.appendChild(chip); functionToChip.set(rec.qn, chip);
      }
      const reveal = document.createElement('button'); reveal.type = 'button'; reveal.className = 'call-graph-module-expand'; reveal.textContent = 'Show all functions';
      reveal.addEventListener('click', () => { card.classList.toggle('is-expanded'); reveal.textContent = card.classList.contains('is-expanded') ? 'Show connector functions' : 'Show all functions'; applyConnectorVisibility(); refreshEdges(); });
      card.append(list, reveal); modulesGrid.appendChild(card);
    }

    const searchInput = document.getElementById('call-graph-search'); const resultsRoot = document.getElementById('call-graph-search-results'); const noMatchEl = document.getElementById('call-graph-search-empty');
    let selectedNodeId = null; let currentMode = 'full'; let selectedModuleOnly = null;
    const getRecord = (qn) => nodeRecords.find((r) => r.qn === qn);

    function setMode(mode) { currentMode = mode; canvas.dataset.mode = mode; toolbar.querySelectorAll('button').forEach((b) => b.classList.toggle('is-active', b.dataset.mode === mode)); refreshEdges(); }
    function updateClearButtonVisibility() {
      const clearButton = toolbar.querySelector('button[data-action="clear"]');
      if (!clearButton) return;
      clearButton.hidden = !selectedNodeId;
    }
    function renderDropdown(matches) { if (!resultsRoot) return; resultsRoot.innerHTML=''; if (!matches.length) return; const list=document.createElement('ul'); list.className='call-graph-search-list'; for (const rec of matches) { const li=document.createElement('li'); const b=document.createElement('button'); b.type='button'; b.className='call-graph-search-option'; b.textContent=rec.searchLabel; b.addEventListener('click',()=>selectNode(rec.qn)); li.appendChild(b); list.appendChild(li);} resultsRoot.appendChild(list); }
    const setNoMatchVisibility = (show) => { if (noMatchEl) noMatchEl.hidden = !show; };

    function getMatches(term) { const q=(term||'').trim().toLowerCase(); if(!q)return []; const exact=[];const prefix=[];const includes=[]; for(const rec of nodeRecords){const qn=rec.qn.toLowerCase();const name=rec.label.toLowerCase();const mb=rec.searchLabel.toLowerCase(); if(qn===q||name===q||mb===q) exact.push(rec); else if(qn.endsWith(`.${q}`)||name.startsWith(q)||mb.endsWith(`.${q}`)) prefix.push(rec); else if(qn.includes(q)||name.includes(q)||mb.includes(q)) includes.push(rec);} return [...exact,...prefix,...includes].slice(0,MAX_SEARCH_RESULTS); }

    function updateMapVisibility() {
      const allCards = modulesGrid.querySelectorAll('.call-graph-module');
      for (const card of allCards) {
        card.classList.remove('is-hidden', 'is-muted');
        if (currentMode === 'module' && selectedModuleOnly) {
          card.classList.toggle('is-hidden', card.dataset.module !== selectedModuleOnly);
        }
      }
    }

    function applyConnectorVisibility() {
      for (const rec of nodeRecords) {
        const chip = functionToChip.get(rec.qn); if (!chip) continue;
        const hasCrossModuleRelation = [...(inbound.get(rec.qn) || [])].some((qn) => getRecord(qn)?.module !== rec.module)
          || [...(outbound.get(rec.qn) || [])].some((qn) => getRecord(qn)?.module !== rec.module);
        chip.classList.toggle('is-connector', hasCrossModuleRelation);
        const moduleCard = chip.closest('.call-graph-module');
        const show = moduleCard?.classList.contains('is-expanded') || hasCrossModuleRelation || currentMode === 'function' || currentMode === 'module';
        chip.classList.toggle('is-hidden', !show);
      }
    }

    function renderFocusedFunction(id) {
      focusedLayout.innerHTML = '';
      if (!id) { focusedLayout.innerHTML = '<p class="call-graph-empty">Select a function to open Focused view.</p>'; return; }
      const rec = getRecord(id); if (!rec) return;
      const inboundFns = [...(inbound.get(id) || new Set())]; const outboundFns = [...(outbound.get(id) || new Set())];
      const internalInbound = inboundFns.filter((qn) => getRecord(qn)?.module === rec.module).map(getRecord).filter(Boolean);
      const internalOutbound = outboundFns.filter((qn) => getRecord(qn)?.module === rec.module).map(getRecord).filter(Boolean);
      const byMod = (qns) => qns.reduce((acc, qn) => { const r=getRecord(qn); if (!r || r.module===rec.module) return acc; (acc[r.module] ||= []).push(r); return acc; }, {});
      const inMods = byMod(inboundFns); const outMods = byMod(outboundFns);
      const mkCard = (title, moduleName, rows, cls) => { const el=document.createElement('section'); el.className=`call-graph-focus-card ${cls||''}`.trim(); el.innerHTML=`<h4>${title}</h4><p class="call-graph-focus-module">${moduleName}</p>`; const list=document.createElement('div'); list.className='call-graph-focus-chip-list'; rows.forEach((r)=>{const b=document.createElement('button'); b.className='call-graph-function-chip'; b.textContent=r.label; b.title=r.qn; b.addEventListener('click',()=>selectNode(r.qn)); list.appendChild(b);}); el.appendChild(list); return el; };
      const left=document.createElement('div'); left.className='call-graph-focus-column'; left.innerHTML='<h3>Inbound callers</h3>'; Object.entries(inMods).forEach(([m,rows])=>left.appendChild(mkCard('called by',m,rows,'is-inbound'))); if(!Object.keys(inMods).length) left.innerHTML+='<p class="call-graph-empty">No cross-module inbound callers.</p>';
      const center=document.createElement('div'); center.className='call-graph-focus-column'; center.innerHTML='<h3>Selected function/module</h3>'; const sel=mkCard('selected',rec.module,[rec],'is-selected'); sel.querySelector('.call-graph-function-chip').classList.add('is-selected'); center.appendChild(sel); center.innerHTML += '<h5>Internal callers</h5>'; center.appendChild(mkCard('called by',rec.module,internalInbound,'is-neutral')); center.innerHTML += '<h5>Internal uses</h5>'; center.appendChild(mkCard('uses',rec.module,internalOutbound,'is-neutral'));
      const right=document.createElement('div'); right.className='call-graph-focus-column'; right.innerHTML='<h3>Outbound callees</h3>'; Object.entries(outMods).forEach(([m,rows])=>right.appendChild(mkCard('uses',m,rows,'is-outbound'))); if(!Object.keys(outMods).length) right.innerHTML+='<p class="call-graph-empty">No cross-module outbound callees.</p>';
      focusedLayout.append(left,center,right);
    }

    function refreshEdges() {
      if (currentMode === 'function') { svg.innerHTML = ''; return; }
      const vbox = viewport.getBoundingClientRect(); svg.setAttribute('viewBox', `0 0 ${vbox.width} ${vbox.height}`); svg.innerHTML = '';
      const activeEdges = currentMode === 'full'
        ? [...moduleEdges.values()].map((edge) => ({ fromChip: modulesGrid.querySelector(`.call-graph-module[data-module="${edge.from}"] .call-graph-module-title`), toChip: modulesGrid.querySelector(`.call-graph-module[data-module="${edge.to}"] .call-graph-module-title`) }))
        : edgeRecords.map((edge) => ({ fromChip: functionToChip.get(edge.from), toChip: functionToChip.get(edge.to) }));
      for (const edge of activeEdges) {
        const { fromChip, toChip } = edge; if (!fromChip || !toChip) continue;
        if (fromChip.closest('.is-hidden') || toChip.closest('.is-hidden')) continue;
        const from=fromChip.getBoundingClientRect(); const to=toChip.getBoundingClientRect(); const line=document.createElementNS('http://www.w3.org/2000/svg','line');
        line.setAttribute('x1', String(from.right - vbox.left)); line.setAttribute('y1', String((from.top + from.bottom) / 2 - vbox.top)); line.setAttribute('x2', String(to.left - vbox.left)); line.setAttribute('y2', String((to.top + to.bottom) / 2 - vbox.top)); line.classList.add('call-graph-edge'); svg.appendChild(line);
      }
    }

    function selectNode(id) {
      if (!knownNodes.has(id)) return;
      selectedNodeId = id; selectedModuleOnly = null; setMode('function'); updateMapVisibility(); renderFocusedFunction(id);
      const url = new URL(window.location.href); url.searchParams.set('function', id); window.history.replaceState({}, '', url);
      const selectedRecord = getRecord(id); if (searchInput && selectedRecord) searchInput.value = selectedRecord.searchLabel;
      renderDropdown([]); setNoMatchVisibility(false);
      updateClearButtonVisibility();
    }
    function clearSelection() {
      selectedNodeId = null;
      selectedModuleOnly = null;
      focusedLayout.innerHTML = '';
      if (searchInput) searchInput.value = '';
      renderDropdown([]);
      setNoMatchVisibility(false);
      const url = new URL(window.location.href); url.searchParams.delete('function'); window.history.replaceState({}, '', url);
      setMode('full');
      updateMapVisibility();
      applyConnectorVisibility();
      updateClearButtonVisibility();
      refreshEdges();
    }
    function submitSearch(rawTerm){const term=(rawTerm||'').trim(); if(!term)return; const matches=getMatches(term); renderDropdown(matches); if(!matches.length){setNoMatchVisibility(true); return;} setNoMatchVisibility(false); const exact=matches.find((m)=>m.qn===term||m.searchLabel===term||m.label===term); selectNode((exact||matches[0]).qn);}

    if (searchInput) {
      searchInput.addEventListener('input', (e) => { const matches = getMatches(e.target.value); renderDropdown(matches); setNoMatchVisibility(Boolean(e.target.value.trim()) && !matches.length); });
      searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); submitSearch(searchInput.value); } });
    }

    toolbar.addEventListener('click', (e) => {
      const mode = e.target?.dataset?.mode; if (!mode) return;
      if (mode === 'full') { selectedModuleOnly = null; setMode('full'); updateMapVisibility(); applyConnectorVisibility(); focusedLayout.innerHTML=''; }
      if (mode === 'function') {
        if (selectedNodeId) { setMode('function'); renderFocusedFunction(selectedNodeId); }
        else { focusedLayout.innerHTML = '<p class="call-graph-empty">Focused view needs a selected function. Use search or click a function chip.</p>'; setMode(selectedModuleOnly ? 'module' : 'full'); }
      }
      if (e.target?.dataset?.action === 'clear') clearSelection();
    });

    canvas.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && selectedNodeId) {
        e.preventDefault();
        clearSelection();
      }
    });

    window.addEventListener('resize', refreshEdges);
    const params = new URLSearchParams(window.location.search); const moduleQuery = params.get('module'); const functionQuery = params.get('function');
    if (functionQuery) { submitSearch(functionQuery); updateClearButtonVisibility(); return; }
    if (moduleQuery) { selectedModuleOnly = moduleQuery.replace(/^fabricops_kit\./, ''); setMode('module'); updateMapVisibility(); applyConnectorVisibility(); renderFocusedFunction(null); }
    else { setMode('full'); updateMapVisibility(); applyConnectorVisibility(); }
    updateClearButtonVisibility();
    refreshEdges();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCallGraph); else initCallGraph();
})();
