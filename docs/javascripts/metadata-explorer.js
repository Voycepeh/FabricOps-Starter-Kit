(() => {
  "use strict";

  // The physical table details are loaded from the generated, canonical
  // reference page only when selected. Logical/future entities remain explicit.
  const definitions = [
    ["DATA_STEWARD", "governance", ["steward_id"], [], "metadata_data_steward/"],
    ["DATA_AGREEMENT", "governance", ["agreement_id", "agreement_version"], ["provider_steward_id", "recipient_steward_id"], "metadata_data_agreement/"],
    ["DATA_CONTRACT", "governance", ["contract_id", "contract_version"], ["table_id"], "metadata_data_contract/"],
    ["PIPELINE_REGISTRY", "engineering", ["authority_id"], ["approvals[].testing_run_id", "approvals[].agreement_id/version", "table_ownership[].contract_id/version"], "metadata_pipeline_registry/"],
    ["PIPELINE_RUN", "engineering", ["run_id"], ["approval_id", "operations[].contract_id/version"], "metadata_pipeline_run/"],
    ["GUARDRAIL_RESULTS", "engineering", ["guardrail_result_id"], ["run_id", "contract_id", "contract_version"], "metadata_guardrail_results/"],
    ["DATA_CATALOGUE", "engineering", ["environment_name", "table_id", "column_id"], [], "metadata_data_catalogue/"],
    ["DATA_PROFILED", "engineering", ["profile_id"], ["table_id", "column_id"], "metadata_data_profiled/"],
    ["DATA_PROFILED_FREQUENCY", "engineering", ["frequency_id"], ["profile_id", "table_id"], "metadata_data_profiled_frequency/"],
    ["DATA_LINEAGE", "engineering", ["lineage_id"], ["table_id"], "metadata_data_lineage/"],
    ["PROCESSING_STATE", "engineering", ["record_id"], ["source_table_id", "target_table_id", "run_id", "publication_id"], "metadata_processing_state/"],
    ["DATA_ACCESS", "engineering", ["access_id"], ["table_id"], "metadata_data_access/"]
  ];

  // Cardinalities always follow the declared parent-to-child direction.
  // Relationship tooltips identify that direction when inspecting either table.
  // Registry cardinalities describe approvals; the physical authority is one row.
  const links = [
    ["DATA_STEWARD", "DATA_AGREEMENT", "1-N", "Provider or recipient"],
    ["DATA_AGREEMENT", "PIPELINE_REGISTRY", "1-N", "Exact approved Agreement versions"],
    ["PIPELINE_REGISTRY", "DATA_CONTRACT", "N-N", "Exact table ownership contracts"],
    ["PIPELINE_RUN", "DATA_CONTRACT", "N-N", "Exact operation contracts"],
    ["DATA_CATALOGUE", "DATA_CONTRACT", "1-N", "Contracts for a table"],
    ["PIPELINE_REGISTRY", "PIPELINE_RUN", "1-N", "Live runs per approved pipeline release"],
    ["PIPELINE_RUN", "GUARDRAIL_RESULTS", "1-N", "Run evaluations"],
    ["PIPELINE_RUN", "PROCESSING_STATE", "1-N", "Run processing state"],
    ["DATA_CATALOGUE", "PROCESSING_STATE", "1-N", "Source and target processing state"],
    ["DATA_CATALOGUE", "DATA_PROFILED", "1-N", "Profile snapshots"],
    ["DATA_CATALOGUE", "DATA_PROFILED_FREQUENCY", "1-N", "Frequency snapshots"],
    ["DATA_PROFILED", "DATA_PROFILED_FREQUENCY", "1-N", "Optional statistical profile"],
    ["DATA_CATALOGUE", "DATA_LINEAGE", "1-N", "Lineage records"],
    ["DATA_CATALOGUE", "DATA_ACCESS", "1-N", "Access observations"],
    ["DATA_CONTRACT", "GUARDRAIL_RESULTS", "1-N", "Contract evaluations"]
  ];

  const byName = new Map(definitions.map(row => [row[0], row]));
  const escapeHtml = value => String(value).replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[ch]);
  const cardinalityFrom = edge => edge[2] || "Reference";

  const makeSvg = (tag, attributes) => {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attributes || {}).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  };

  // Reuse the rendered canonical metadata page rather than duplicating its
  // descriptions, tables, links, and writer documentation in this script.
  const referenceCache = new Map();
  async function loadReference(url) {
    if (!referenceCache.has(url)) {
      const request = fetch(url).then(response => {
        if (!response.ok) throw new Error("Reference page returned " + response.status);
        return response.text().then(text => ({ text, url: response.url }));
      }).then(({ text, url: finalUrl }) => {
        const doc = new DOMParser().parseFromString(text, "text/html");
        const content = doc.querySelector(".md-content__inner");
        if (!content) throw new Error("Metadata reference content not found");
        const sections = [];
        let current = null;
        for (const child of Array.from(content.children)) {
          if (child.tagName === "H1") continue;
          if (child.tagName === "H2") {
            current = { heading: child.textContent.trim(), nodes: [] };
            sections.push(current);
          } else if (current) {
            current.nodes.push(child);
          } else if (child.matches("p")) {
            sections.unshift({ heading: "Overview", nodes: [child] });
          }
        }
        // Links in cloned reference content must resolve relative to the
        // original reference document, not relative to the model overview.
        sections.forEach(section => section.nodes.forEach(node => {
          node.querySelectorAll("a[href]").forEach(a => {
            const href = a.getAttribute("href");
            if (href && !href.startsWith("#") && !href.startsWith("javascript:")) {
              a.setAttribute("href", new URL(href, finalUrl).href);
            }
          });
        }));
        return sections;
      });
      referenceCache.set(url, request);
    }
    return referenceCache.get(url);
  }

  function init(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = "true";
    const modelSource = root.querySelector(".metadata-explorer-model");
    let canonicalModels = {};
    try {
      canonicalModels = JSON.parse(modelSource?.textContent || "{}");
    } catch (_error) {
      // The navigation links remain accessible if the data payload is invalid.
    }
    root.innerHTML =
      '<div class="metadata-explorer-topbar">' +
      '<span class="metadata-explorer-legend"><i class="metadata-dot governance"></i> Governance <i class="metadata-dot engineering"></i> Engineering</span>' +
      '<span class="metadata-explorer-hint">Solid: keyed joins · Dashed: conceptual references</span>' +
      '</div>' +
      '<div class="metadata-explorer-layout">' +
      '<div class="metadata-explorer-viewport" role="region" tabindex="0" aria-label="Scrollable metadata relationship diagram">' +
      '<div class="metadata-explorer-graph" role="group" aria-label="Metadata relationships"></div></div>' +
      '<section class="metadata-explorer-details" aria-live="polite" aria-label="Selected table details"></section></div>';

    const graph = root.querySelector(".metadata-explorer-graph");
    const detail = root.querySelector(".metadata-explorer-details");
    const viewport = root.querySelector(".metadata-explorer-viewport");
    const tooltip = document.createElement("div");
    tooltip.className = "metadata-explorer-tooltip";
    tooltip.id = "metadata-explorer-tooltip";
    tooltip.setAttribute("role", "tooltip");
    tooltip.hidden = true;
    root.appendChild(tooltip);

    const modelFor = name => canonicalModels[name] || {};
    const hideTooltip = () => {
      tooltip.hidden = true;
    };
    const showTooltip = (name, link) => {
      const model = modelFor(name);
      if (!model.purpose && !model.grain) return;
      tooltip.replaceChildren();
      const title = document.createElement("strong");
      title.textContent = "METADATA_" + name;
      const description = document.createElement("p");
      description.textContent = model.purpose || "No description available";
      const grain = document.createElement("p");
      const label = document.createElement("b");
      label.textContent = "One row represents: ";
      grain.append(label, document.createTextNode(model.grain || "Not defined"));
      tooltip.append(title, description, grain);
      tooltip.hidden = false;
      const rect = link.getBoundingClientRect();
      const bounds = tooltip.getBoundingClientRect();
      const left = Math.max(10, Math.min(rect.left, window.innerWidth - bounds.width - 10));
      const below = rect.bottom + 10;
      const top = below + bounds.height > window.innerHeight ? Math.max(10, rect.top - bounds.height - 10) : below;
      tooltip.style.left = left + "px";
      tooltip.style.top = top + "px";
    };
    viewport.addEventListener("scroll", hideTooltip, { passive: true });
    window.addEventListener("scroll", hideTooltip, { passive: true });
    // Keep the reviewed SVG as the exact visual model, while reusing the
    // existing selection/details panel for every physical metadata table.
    const buttons = {};
    const approvedDiagram = new URL("../../assets/fabricops-metadata-approved.svg", document.baseURI);
    graph.style.width = "100%";
    graph.style.minWidth = "860px";
    graph.style.aspectRatio = "1540 / 980";
    fetch(approvedDiagram).then(response => {
      if (!response.ok) throw new Error("Approved diagram returned " + response.status);
      return response.text();
    }).then(source => {
      const parsed = new DOMParser().parseFromString(source, "image/svg+xml");
      if (parsed.querySelector("parsererror")) throw new Error("Invalid metadata diagram SVG");
      const svg = document.importNode(parsed.documentElement, true);
      svg.classList.add("metadata-explorer-approved-svg");
      svg.setAttribute("aria-label", "FabricOps metadata ERD. Select a table to inspect its details.");
      svg.querySelectorAll("a").forEach(link => {
        const nativeTitle = link.querySelector("title");
        const caption = nativeTitle?.textContent || "";
        const name = caption.split("Open metadata documentation: ").pop().trim();
        if (!byName.has(name)) return;
        link.setAttribute("role", "button");
        link.setAttribute("tabindex", "0");
        link.setAttribute("aria-label", "Inspect " + name);
        link.setAttribute("aria-describedby", tooltip.id);
        nativeTitle?.remove();
        link.addEventListener("mouseenter", () => showTooltip(name, link));
        link.addEventListener("mouseleave", hideTooltip);
        link.addEventListener("focus", () => showTooltip(name, link));
        link.addEventListener("blur", hideTooltip);
        link.addEventListener("click", event => {
          hideTooltip();
          event.preventDefault();
          select(name, { focusDetails: true });
        });
        link.addEventListener("keydown", event => {
          if (event.key === "Escape") hideTooltip();
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            select(name, { focusDetails: true });
          }
        });
        buttons[name] = link;
      });
      if (Object.keys(buttons).length !== definitions.length) throw new Error("Unexpected approved diagram table count");
      graph.replaceChildren(svg);
      select("DATA_AGREEMENT");
    }).catch(() => {
      graph.innerHTML = '<p class="metadata-explorer-loading">Unable to load the diagram. Open a metadata table directly:</p>' +
        '<nav aria-label="Metadata table references">' +
        definitions.filter(row => row[4])
          .map(row => '<a href="' + escapeHtml(row[4]) + '">METADATA_' + escapeHtml(row[0]) + '</a>')
          .join(" · ") + '</nav>';
      select("DATA_AGREEMENT");
    });

    detail.id = "metadata-explorer-selected-table";
    detail.tabIndex = -1;

    let activeSelection = 0;
    function relationships(name) {
      return links.filter(edge => edge[0] === name || edge[1] === name);
    }

    const logicalJoinKeys = {
      "DATA_CATALOGUE|DATA_PROFILED_FREQUENCY": ["DATA_PROFILED_FREQUENCY.table_id + column_id → DATA_CATALOGUE.table_id + column_id (logical table/column reference)"]
    };
    const keyJoinRows = (from, to) => {
      const rows = [];
      for (const child of [from, to]) {
        const other = child === from ? to : from;
        for (const fk of (modelFor(child).foreign_keys || [])) {
          if (fk.referenced_table?.replace(/^METADATA_/, "") !== other) continue;
          const suffix = child === "DATA_PROFILED_FREQUENCY" && fk.local_field === "profile_id"
            ? " (optional profile reference)" : "";
          rows.push(child + "." + fk.local_field + " → " + other + "." + fk.referenced_field + suffix);
        }
      }
      // A registration is unique by pipeline and environment inside the authority.
      if ((from === "PIPELINE_REGISTRY" && to === "PIPELINE_RUN") ||
          (to === "PIPELINE_REGISTRY" && from === "PIPELINE_RUN")) {
        rows.push("PIPELINE_RUN.pipeline_id + environment_name → PIPELINE_REGISTRY.registrations[].pipeline_id + environment_name (registered pipeline and environment; Live approval must match both)");
      }
      if (rows.length) return rows;
      return logicalJoinKeys[from + "|" + to] || logicalJoinKeys[to + "|" + from] || ["Logical relationship; no physical FK declared"];
    };
    function renderRelationships(name) {
      const relationshipsForTable = relationships(name);
      if (!relationshipsForTable.length) return '<p>No direct logical relationship is shown.</p>';
      return '<div class="metadata-explorer-related">' +
        relationshipsForTable.map(edge => {
          const other = edge[0] === name ? edge[1] : edge[0];
          const joinLines = keyJoinRows(edge[0], edge[1]);
          const referenceOnly = !edge[2];
          return '<div class="metadata-explorer-related-row">' +
            '<span class="metadata-explorer-cardinality-text' +
            (referenceOnly ? ' metadata-explorer-reference-label' : '') +
            '" title="' + escapeHtml(edge[0] + ' → ' + edge[1] + ': ' + edge[3] + '; Application-enforced identity reference') + '">' +
            escapeHtml(cardinalityFrom(edge, name)) + '</span>' +
            '<button type="button" class="metadata-explorer-related-link" data-table="' + escapeHtml(other) + '">' +
            escapeHtml(other) + '</button>' +
            '<span class="metadata-explorer-related-joins">' +
            joinLines.map(line => '<code>' + escapeHtml(line) + '</code>').join('') +
            '</span></div>';
        }).join("") + '</div>';
    }

        // Exact schema is the only large reference section; it stays visible.
    function sectionDetails(section) {
      const wrapper = document.createElement("section");
      wrapper.className = "metadata-explorer-implemented-schema";
      const heading = document.createElement("h4");
      heading.textContent = "Implemented schema";
      wrapper.appendChild(heading);
      const content = document.createElement("div");
      content.className = "metadata-explorer-section-body";
      section.nodes.forEach(node => content.appendChild(node.cloneNode(true)));
      wrapper.appendChild(content);
      return wrapper;
    }

    async function select(name, { focusDetails = false } = {}) {
      const [title, schema, pk, fk, url, status] = byName.get(name);
      const selectionId = ++activeSelection;
      Object.entries(buttons).forEach(([key, button]) => {
        button.classList.toggle("selected", key === name);
        button.setAttribute("aria-pressed", String(key === name));
      });
      graph.querySelectorAll(".metadata-er-relationship").forEach(group => {
        group.classList.toggle("selected",
          group.getAttribute("data-from") === name || group.getAttribute("data-to") === name);
      });
      const model = modelFor(name);
      const writerNames = model.write_entrypoints || [];
      const writers = writerNames.map(fn =>
        '<a href="../../api/reference/' + encodeURIComponent(fn) + '/"><code>' +
        escapeHtml(fn) + '()</code></a>'
      ).join(' · ');
      detail.innerHTML =
        '<div class="metadata-explorer-detail-head"><div>' +
        '<span class="metadata-explorer-schema-tag ' + schema + '">' + escapeHtml(schema) + '</span>' +
        '<h3>METADATA_' + escapeHtml(title) + '</h3></div>' +
        '<span class="metadata-explorer-state">' + escapeHtml(status || "") + '</span></div>' +
        '<div class="metadata-explorer-summary">' +
        '<p class="metadata-explorer-purpose">' + escapeHtml(model.purpose || status || "") + '</p>' +
        '<div class="metadata-explorer-detail-facts">' +
        '<div><strong>One row represents</strong><span>' + escapeHtml(model.grain || "Logical release held in activation authority") + '</span></div>' +
        '<div><strong>Primary key</strong><code>' + escapeHtml((model.primary_key || pk).join(" · ")) + '</code></div>' +
        '<div><strong>Written via</strong><span>' + (writers || "See activation authority") + '</span></div>' +
        '</div></div>' +
        '<div class="metadata-explorer-relationship-summary"><h4>Relationships</h4>' +
        renderRelationships(name) + '</div>' +
        '<div class="metadata-explorer-reference-content" data-reference-content></div>';
      if (focusDetails) {
        // Selection from the SVG scrolls the newly populated details into
        // view. Do not jump when rendering the initial default selection.
        window.requestAnimationFrame(() => {
          detail.focus({ preventScroll: true });
          detail.scrollIntoView({
            block: "start",
            behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"
          });
        });
      }
      detail.querySelectorAll("[data-table]").forEach(button => {
        button.addEventListener("click", () => select(button.dataset.table, { focusDetails: false }));
      });
      const content = detail.querySelector("[data-reference-content]");
      if (!url) {
        content.textContent = "This table is proposed and has no implemented schema yet.";
        return;
      }
      content.innerHTML = '<p class="metadata-explorer-loading">Loading table reference…</p>';
      try {
        const sections = await loadReference(url);
        if (activeSelection !== selectionId) return;
        content.innerHTML = "";
        const implemented = sections.find(section => section.heading === "Implemented schema");
        if (implemented) {
          content.appendChild(sectionDetails(implemented));
        } else {
          content.innerHTML = '<p>Schema details are available on the ' +
            '<a href="' + escapeHtml(url) + '">full table reference page</a>.</p>';
        }
      } catch (_error) {
        if (activeSelection !== selectionId) return;
        content.innerHTML = '<p>Could not load the detailed reference. ' +
          '<a href="' + escapeHtml(url) + '">Open the table reference page →</a></p>';
      }
    }

    // Ensure the selected card is in view when accessed by keyboard / click
    // without jumping the full document to the details pane.
    viewport.addEventListener("keydown", event => {
      if (event.key === "ArrowRight") viewport.scrollLeft += 120;
      if (event.key === "ArrowLeft") viewport.scrollLeft -= 120;
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(() => document.querySelectorAll("[data-metadata-explorer]").forEach(init));
  } else {
    document.addEventListener("DOMContentLoaded",
      () => document.querySelectorAll("[data-metadata-explorer]").forEach(init));
  }
})();