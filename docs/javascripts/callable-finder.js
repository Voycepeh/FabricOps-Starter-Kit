(function () {
  function normalize(value) { return (value || "").toLowerCase().trim(); }
  function levenshtein(a, b) {
    if (a === b) return 0;
    if (!a.length) return b.length;
    if (!b.length) return a.length;
    const prev = new Array(b.length + 1);
    const curr = new Array(b.length + 1);
    for (let j = 0; j <= b.length; j += 1) prev[j] = j;
    for (let i = 1; i <= a.length; i += 1) {
      curr[0] = i;
      for (let j = 1; j <= b.length; j += 1) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        curr[j] = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost);
      }
      for (let j = 0; j <= b.length; j += 1) prev[j] = curr[j];
    }
    return prev[b.length];
  }

  function fuzzyTokenMatch(query, haystackTokens) {
    if (!query || query.length < 4 || haystackTokens.length === 0) return false;
    const maxDistance = query.length <= 5 ? 1 : 2;
    return haystackTokens.some((token) => {
      if (Math.abs(token.length - query.length) > maxDistance) return false;
      return levenshtein(query, token) <= maxDistance;
    });
  }

  function tokenize(value) {
    return normalize(value).split(/[\s_./-]+/).filter(Boolean);
  }

  function queryMatchesEntry(queryTokens, entryTokens) {
    return queryTokens.every((queryToken) => {
      if (entryTokens.includes(queryToken)) return true;
      if (entryTokens.some((token) => token.includes(queryToken))) return true;
      return fuzzyTokenMatch(queryToken, entryTokens);
    });
  }

  function scoreEntry(query, queryTokens, entry) {
    if (!query) return 1;
    if (entry.name === query) return 100;
    if (entry.name.startsWith(query)) return 80;
    if (entry.name.includes(query)) return 60;
    if (queryMatchesEntry(queryTokens, entry.nameTokens)) return 50;
    if (entry.module.includes(query) || entry.functionType.includes(query) || entry.starterPath.includes(query) || entry.usageSource.includes(query)) return 40;
    if (queryMatchesEntry(queryTokens, entry.tokens)) return 30;
    if (queryTokens.every((token) => fuzzyTokenMatch(token, entry.tokens))) return 10;
    return 0;
  }

  function initRenderedDocLinks() {
    Array.from(document.querySelectorAll("a[href]")).forEach((anchor) => {
      const rawHref = anchor.getAttribute("href");
      if (!rawHref || !rawHref.endsWith(".md") && !rawHref.includes(".md#") && !rawHref.includes(".md?")) return;
      if (/^(https?:|mailto:|tel:)/i.test(rawHref)) return;
      const rewritten = rawHref.replace(/\.md(?=([?#]|$))/i, "/");
      anchor.setAttribute("href", rewritten);
    });
  }

  function initCallableFinder() {
    const container = document.querySelector("[data-callable-finder]");
    const input = document.getElementById("callable-finder-input");
    const status = document.getElementById("callable-finder-status");
    const empty = document.querySelector("[data-callable-finder-empty]");
    const rows = Array.from(document.querySelectorAll("[data-callable-row='true']"));
    const typeFilters = Array.from(document.querySelectorAll("[data-function-type-filter]"));
    if (!container || !input || !status || !empty || rows.length === 0) return;
    if (container.dataset.callableFinderInitialized === "true") return;
    container.dataset.callableFinderInitialized = "true";
    const searchable = rows.map((row) => ({
      row,
      name: normalize(row.dataset.callableName),
      module: normalize(row.dataset.callableModule),
      functionType: normalize(row.dataset.functionType),
      starterPath: normalize(row.dataset.callableStarterPath),
      usageSource: normalize(row.dataset.callableUsageSource),
      purpose: normalize(row.dataset.callablePurpose),
      text: normalize([
        row.dataset.callableName,
        row.dataset.callableModule,
        row.dataset.callableStarterPath,
        row.dataset.callableUsageSource,
        row.dataset.functionType,
        row.dataset.callablePurpose,
      ].join(" ")),
    })).map((entry) => ({
      ...entry,
      tokens: tokenize(entry.text),
      nameTokens: tokenize(entry.name),
    }));
    function enabledTypes() { return new Set(typeFilters.filter((cb) => cb.checked).map((cb) => normalize(cb.dataset.functionTypeFilter))); }
    function update() {
      const query = normalize(input.value);
      const queryTokens = tokenize(query);
      const types = enabledTypes();
      let matched = 0;
      let total = 0;
      const visibleEntries = [];
      searchable.forEach((entry) => {
        const typeEnabled = types.has(entry.functionType);
        if (typeEnabled) total += 1;
        const score = scoreEntry(query, queryTokens, entry);
        const show = typeEnabled && score > 0;
        entry.row.hidden = !show;
        if (show) {
          matched += 1;
          visibleEntries.push({ entry, score });
        }
      });
      visibleEntries
        .sort((a, b) => b.score - a.score || a.entry.name.localeCompare(b.entry.name))
        .forEach(({ entry }) => {
          entry.row.parentElement.appendChild(entry.row);
        });
      empty.hidden = matched !== 0;
      status.textContent = `Showing ${matched} of ${total} functions.`;
    }
    input.addEventListener("input", update);
    typeFilters.forEach((cb) => cb.addEventListener("change", update));
    update();
  }
  function initCallableMapFinder() {
    const input = document.getElementById("callable-map-search");
    const rows = Array.from(document.querySelectorAll("[data-callable-map-row='true']"));
    if (!input || rows.length === 0) return;
    if (input.dataset.callableMapInitialized === "true") return;
    input.dataset.callableMapInitialized = "true";
    const entries = rows.map((row) => {
      const text = normalize([
        row.dataset.callableName,
        row.dataset.callableModule,
        row.dataset.callableRole,
        row.dataset.callableHelpers,
        row.dataset.callableCrossModule,
      ].join(" "));
      return { row, tokens: tokenize(text), text };
    });
    function update() {
      const query = normalize(input.value);
      const qTokens = tokenize(query);
      entries.forEach((entry) => {
        const show = !query || queryMatchesEntry(qTokens, entry.tokens) || entry.text.includes(query);
        entry.row.hidden = !show;
      });
    }
    input.addEventListener("input", update);
    update();
  }
  document.addEventListener("DOMContentLoaded", initRenderedDocLinks);
  document.addEventListener("DOMContentLoaded", initCallableFinder);
  document.addEventListener("DOMContentLoaded", initCallableMapFinder);
  if (typeof document$ !== "undefined" && document$.subscribe) document$.subscribe(initRenderedDocLinks);
  if (typeof document$ !== "undefined" && document$.subscribe) document$.subscribe(initCallableFinder);
  if (typeof document$ !== "undefined" && document$.subscribe) document$.subscribe(initCallableMapFinder);
})();
