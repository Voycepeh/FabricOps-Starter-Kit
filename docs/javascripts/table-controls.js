(function () {
  const BLANK = "(blank)";
  const TABLE_CLASS = "fo-table-enhanced";
  const state = new WeakMap();

  function cellText(row, index) {
    const cell = row.cells[index];
    return (cell ? cell.innerText || cell.textContent || "" : "").trim();
  }

  function displayValue(value) {
    return value === "" ? BLANK : value;
  }

  function isNumericColumn(rows, index) {
    const values = rows.map((row) => cellText(row, index)).filter(Boolean);
    return values.length > 0 && values.every((value) => /^-?\d+(\.\d+)?$/.test(value.replace(/,/g, "")));
  }

  function numericValue(value) {
    const parsed = Number(String(value).replace(/,/g, ""));
    return Number.isFinite(parsed) ? parsed : null;
  }

  function compareValues(a, b, numeric) {
    if (numeric) {
      const left = numericValue(a);
      const right = numericValue(b);
      if (left === null && right === null) return 0;
      if (left === null) return 1;
      if (right === null) return -1;
      return left - right;
    }
    return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
  }

  function tableState(table) {
    if (!state.has(table)) {
      state.set(table, { sort: null, filters: new Map(), originalRows: Array.from(table.tBodies[0]?.rows || []) });
    }
    return state.get(table);
  }

  function isOptInTable(table) {
    return table && table.dataset && table.dataset.tableControls === "excel";
  }

  function currentRows(table) {
    return Array.from(table.tBodies[0]?.rows || []);
  }

  function uniqueValues(table, column) {
    const rows = tableState(table).originalRows;
    return [...new Set(rows.map((row) => displayValue(cellText(row, column))))].sort((a, b) => compareValues(a, b, false));
  }

  function rowMatchesFilter(row, filter) {
    const value = cellText(row, filter.column);
    if (filter.kind === "values") {
      return filter.values.has(displayValue(value));
    }
    const number = numericValue(value);
    const a = numericValue(filter.a);
    const b = numericValue(filter.b);
    if (number === null) return false;
    if (filter.operator === "equals") return number === a;
    if (filter.operator === "greater") return a !== null && number > a;
    if (filter.operator === "less") return a !== null && number < a;
    if (filter.operator === "between") return a !== null && b !== null && number >= Math.min(a, b) && number <= Math.max(a, b);
    return true;
  }

  function applyTable(table) {
    const cfg = tableState(table);
    const tbody = table.tBodies[0];
    if (!tbody) return;
    let rows = cfg.originalRows.filter((row) => [...cfg.filters.values()].every((filter) => rowMatchesFilter(row, filter)));
    if (cfg.sort) {
      const { column, direction, numeric } = cfg.sort;
      const dir = direction === "desc" ? -1 : 1;
      rows = rows.map((row, index) => ({ row, index })).sort((left, right) => {
        const result = compareValues(cellText(left.row, column), cellText(right.row, column), numeric);
        return result === 0 ? left.index - right.index : result * dir;
      }).map((item) => item.row);
    }
    rows.forEach((row) => tbody.appendChild(row));
    cfg.originalRows.forEach((row) => { row.hidden = !rows.includes(row); });
    updateHeaderStates(table);
    renderClearAll(table);
  }

  function closeMenus() {
    document.querySelectorAll(".fo-table-menu").forEach((menu) => menu.remove());
  }

  function renderClearAll(table) {
    const cfg = tableState(table);
    let action = table.previousElementSibling;
    if (!action || !action.classList.contains("fo-table-clear-all")) {
      action = document.createElement("button");
      action.type = "button";
      action.className = "fo-table-clear-all";
      action.textContent = "Clear all filters";
      action.addEventListener("click", () => {
        cfg.filters.clear();
        cfg.sort = null;
        applyTable(table);
      });
      table.parentNode.insertBefore(action, table);
    }
    action.hidden = cfg.filters.size === 0;
  }

  function updateHeaderStates(table) {
    const cfg = tableState(table);
    table.querySelectorAll("thead th").forEach((th, index) => {
      th.classList.toggle("fo-filter-active", cfg.filters.has(index));
      th.classList.toggle("fo-sort-active", Boolean(cfg.sort && cfg.sort.column === index));
      th.dataset.sortDirection = cfg.sort && cfg.sort.column === index ? cfg.sort.direction : "";
      const button = th.querySelector(".fo-table-menu-button");
      if (button) {
        button.setAttribute("aria-label", `Sort and filter ${th.textContent.trim() || `column ${index + 1}`}`);
      }
    });
  }

  function textMenu(table, column, menu) {
    const cfg = tableState(table);
    const active = cfg.filters.get(column);
    menu.insertAdjacentHTML("beforeend", `<button type="button" data-sort="asc">Sort A to Z</button><button type="button" data-sort="desc">Sort Z to A</button><button type="button" data-clear-sort>Clear sort</button><label class="fo-menu-search">Search values<input type="search" data-search-values></label><label><input type="checkbox" data-select-all checked> Select all</label><div class="fo-value-list"></div><button type="button" data-apply>Apply</button><button type="button" data-clear-filter>Clear filter</button>`);
    const list = menu.querySelector(".fo-value-list");
    const values = uniqueValues(table, column);
    const selected = active && active.kind === "values" ? active.values : new Set(values);
    values.forEach((value) => {
      const label = document.createElement("label");
      label.innerHTML = `<input type="checkbox" value="${value.replace(/"/g, "&quot;")}" ${selected.has(value) ? "checked" : ""}> ${value}`;
      list.appendChild(label);
    });
    menu.querySelector("[data-search-values]").addEventListener("input", (event) => {
      const q = event.target.value.toLowerCase();
      list.querySelectorAll("label").forEach((label) => { label.hidden = !label.textContent.toLowerCase().includes(q); });
    });
    menu.querySelector("[data-select-all]").addEventListener("change", (event) => {
      list.querySelectorAll('input[type="checkbox"]').forEach((box) => { box.checked = event.target.checked; });
    });
  }

  function numericMenu(menu) {
    menu.insertAdjacentHTML("beforeend", `<button type="button" data-sort="asc">Sort smallest to largest</button><button type="button" data-sort="desc">Sort largest to smallest</button><button type="button" data-clear-sort>Clear sort</button><label>Equals<input type="number" data-op="equals"></label><label>Greater than<input type="number" data-op="greater"></label><label>Less than<input type="number" data-op="less"></label><fieldset><legend>Between</legend><input type="number" data-between="a"><input type="number" data-between="b"></fieldset><button type="button" data-apply>Apply</button><button type="button" data-clear-filter>Clear filter</button>`);
  }

  function openMenu(table, th, column, button) {
    closeMenus();
    const rows = tableState(table).originalRows;
    const numeric = isNumericColumn(rows, column);
    const menu = document.createElement("div");
    menu.className = "fo-table-menu";
    menu.tabIndex = -1;
    menu.dataset.columnType = numeric ? "numeric" : "text";
    numeric ? numericMenu(menu) : textMenu(table, column, menu);
    document.body.appendChild(menu);
    const rect = button.getBoundingClientRect();
    menu.style.left = `${Math.max(8, rect.left)}px`;
    menu.style.top = `${rect.bottom + 4}px`;
    menu.addEventListener("click", (event) => {
      const cfg = tableState(table);
      const target = event.target;
      if (target.matches("[data-sort]")) {
        cfg.sort = { column, direction: target.dataset.sort, numeric };
        applyTable(table);
        closeMenus();
      } else if (target.matches("[data-clear-sort]")) {
        if (cfg.sort && cfg.sort.column === column) cfg.sort = null;
        applyTable(table);
        closeMenus();
      } else if (target.matches("[data-clear-filter]")) {
        cfg.filters.delete(column);
        applyTable(table);
        closeMenus();
      } else if (target.matches("[data-apply]")) {
        if (numeric) {
          const betweenA = menu.querySelector('[data-between="a"]').value;
          const betweenB = menu.querySelector('[data-between="b"]').value;
          const opInput = [...menu.querySelectorAll("[data-op]")].find((input) => input.value !== "");
          if (betweenA !== "" || betweenB !== "") cfg.filters.set(column, { column, kind: "numeric", operator: "between", a: betweenA, b: betweenB });
          else if (opInput) cfg.filters.set(column, { column, kind: "numeric", operator: opInput.dataset.op, a: opInput.value });
        } else {
          const values = new Set([...menu.querySelectorAll('.fo-value-list input[type="checkbox"]:checked')].map((box) => box.value));
          cfg.filters.set(column, { column, kind: "values", values });
        }
        applyTable(table);
        closeMenus();
      }
    });
    menu.addEventListener("keydown", (event) => { if (event.key === "Escape") closeMenus(); });
    menu.focus();
  }

  function enhanceTable(table) {
    if (!table.tHead || !table.tBodies[0]) return;
    if (!isOptInTable(table)) return;
    if (table.classList.contains(TABLE_CLASS)) {
      const cfg = tableState(table);
      cfg.originalRows = currentRows(table);
      applyTable(table);
      return;
    }
    table.classList.add(TABLE_CLASS);
    tableState(table);
    table.querySelectorAll("thead th").forEach((th, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "fo-table-menu-button";
      button.innerHTML = "▾";
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        openMenu(table, th, index, button);
      });
      if (!th.querySelector(":scope > .fo-table-menu-button")) th.appendChild(button);
    });
    renderClearAll(table);
    updateHeaderStates(table);
  }

  function enhance(table) {
    enhanceTable(table);
  }

  function enhanceAll(root = document) {
    root.querySelectorAll('table[data-table-controls="excel"]').forEach(enhanceTable);
  }

  function resetAll(root = document) {
    root.querySelectorAll('table[data-table-controls="excel"]').forEach((table) => {
      const cfg = tableState(table);
      cfg.filters.clear();
      cfg.sort = null;
      applyTable(table);
    });
  }

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".fo-table-menu") && !event.target.closest(".fo-table-menu-button")) closeMenus();
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeMenus(); });
  document.addEventListener("DOMContentLoaded", () => enhanceAll());

  window.FabricOpsTableControls = { enhance, enhanceAll, resetAll, _test: { compareValues, displayValue, numericValue, rowMatchesFilter } };
})();
