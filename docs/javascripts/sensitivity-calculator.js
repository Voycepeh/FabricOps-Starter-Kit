(() => {
  const workerURL = new URL("sensitivity-calculator-worker.js", document.currentScript.src);
  const scenariosURL = new URL("../assets/sensitivity-scenarios.json", workerURL);
  const datasets = new WeakSet();

  function element(tag, text) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function label(code) {
    return code.replaceAll("_", " ").replace(/^./, (first) => first.toUpperCase());
  }

  function syncOptions(select, choices, placeholder, selected = select.value) {
    select.replaceChildren(new Option(placeholder, ""));
    for (const [value, text] of choices) select.add(new Option(text, value));
    select.value = choices.some(([value]) => value === selected) ? selected : "";
  }

  function assessmentSummary(assessment) {
    const assessed = assessment.classification;
    const handling = assessment.minimum_handling_classification ?? assessed;
    const evidence = assessment.evidence ?? assessment.columns.flatMap((column) => column.evidence);
    const patterns = [...new Set(evidence.filter((code) => code.startsWith("pattern_match:")))]
      .map((code) => {
        const detector = code.slice("pattern_match:".length);
        return detector === "nric_fin" ? "NRIC/FIN" : detector.replaceAll("_", " ");
      });
    const classified = assessment.is_personal_data ?? assessment.contains_personal_data;
    const personalData = classified === true ? "PII indicated by category"
      : patterns.length ? `Possible PII (${patterns.join(", ")})`
        : classified === false ? "Category indicates non-personal data" : "PII status unknown";
    const findings = assessment.dataset_findings?.map(({ code }) => code) ?? [];
    const review = assessment.human_review_required || !assessed;
    let reason;
    if (review) {
      if (findings.includes("limited_dataset_coverage")) {
        reason = "Check coverage of the full dataset before lowering handling.";
      } else if (patterns.length && assessed !== handling) {
        reason = "Keep this level until the business use of the matched values is confirmed.";
      } else if (findings.includes("sensitive_linkage_unverified")) {
        reason = "Confirm whether the fields link people to sensitive information.";
      } else if (findings.includes("identifiable_sensitive_information")) {
        reason = "The linked fields can identify people in sensitive information.";
      } else if (!assessed) {
        reason = "Confirm the business use and choose the appropriate category.";
      }
    }
    return { handling, assessed, personalData, review, reason };
  }

  function renderResults(result, container, policyLabel) {
    const table = element("table");
    table.className = "sensitivity-calculator__table";
    const caption = table.createCaption();
    caption.textContent = policyLabel;
    const headings = table.createTHead().insertRow();
    for (const title of ["Scope", "Suggested handling"]) {
      const head = element("th", title);
      head.scope = "col";
      headings.append(head);
    }
    const body = table.createTBody();
    for (const [name, assessment] of [
      [result.scope.column_only ? "Column" : "Dataset", result],
      ...result.columns.map((column) => [column.column_name, column]),
    ]) {
      const row = body.insertRow();
      const heading = element("th", name);
      heading.scope = "row";
      row.append(heading);
      const { handling, assessed, personalData, review, reason } = assessmentSummary(assessment);
      const cell = row.insertCell();
      cell.append(element("strong", handling ?? "Review"));
      if (review && handling) {
        const status = element("small", "Review");
        status.className = "sensitivity-calculator__review";
        cell.append(status);
      }
      if (assessed && assessed !== handling) cell.append(element("small", `Assessed as ${assessed}.`));
      cell.append(element("small", personalData));
      if (reason) cell.append(element("small", reason));
    }
    const reasons = [
      ...result.dataset_findings.map((finding) => {
        const categories = finding.categories?.map(label).join(" + ");
        return categories ? `${label(finding.code)} (${categories})` : label(finding.code);
      }),
      ...result.limitations.map(label),
      ...result.columns.flatMap((column) => column.evidence.map(
        (code) => `${column.column_name} — ${label(code)}`,
      )),
    ];
    const findings = element("div");
    if (reasons.length) {
      const list = element("ul");
      for (const reason of reasons) list.append(element("li", reason));
      findings.append(element("h4", "Findings"), list);
    }
    if (result.recommended_treatments.length || result.residual_risks.length) {
      const list = element("ul");
      for (const item of result.recommended_treatments) {
        list.append(element("li", `${label(item.parameters.treatment)} ${item.column_name}. ${item.rationale}`));
      }
      for (const risk of result.residual_risks) list.append(element("li", risk));
      findings.append(element("h4", "Treatment suggestions"), list);
    }
    const tableRegion = element("div");
    tableRegion.className = "sensitivity-calculator__results-table";
    tableRegion.tabIndex = 0;
    tableRegion.setAttribute("role", "region");
    tableRegion.setAttribute("aria-label", "Suggested handling");
    tableRegion.append(table);
    container.replaceChildren(element("h3", "Assessment results"), tableRegion, findings);
    container.hidden = false;
  }

  function initialize() {
    const root = document.querySelector("[data-sensitivity-calculator]");
    if (!root || datasets.has(root)) return;
    datasets.add(root);

    const form = root.querySelector("form");
    const file = root.querySelector("[data-dataset-file]");
    const dictionary = root.querySelector("[data-dictionary-file]");
    const picker = root.querySelector("[data-scenario]");
    const loadScenario = root.querySelector("[data-load-scenario]");
    const sparkReference = root.querySelector("[data-spark-reference]");
    const showcase = root.querySelector("[data-scenario-showcase]");
    const slides = [...showcase.querySelectorAll("[data-slide]")];
    const showcaseButtons = showcase.querySelectorAll("[data-showcase-scenario]");
    const inputs = root.querySelector("[data-calculator-inputs]");
    const fields = root.querySelector("[data-column-fields]");
    const profileName = root.querySelector("[data-profile-name]");
    const sampleData = root.querySelector("[data-sample-data]");
    const sampleCSV = sampleData.querySelector("code");
    const policy = root.querySelector("[data-policy]");
    const apply = root.querySelector("[data-apply]");
    const reset = root.querySelector("[data-reset]");
    const target = root.querySelector("[data-target]");
    const linkage = root.querySelector("[data-linkage]");
    const results = root.querySelector("[data-results]");
    const status = root.querySelector("[role=status]");
    let worker;
    let profile;
    let defaultPolicy;
    let currentPolicy;
    let activePolicyText;
    let usingDefaults = true;
    let columns = [];
    const scenarios = new Map();

    function send(message) {
      worker ??= new Worker(workerURL);
      return new Promise((resolve, reject) => {
        const stop = () => {
          worker.terminate();
          worker = undefined;
          reject(new Error("The calculator timed out or stopped. Try again."));
        };
        const timeout = setTimeout(stop, 90000);
        worker.onmessage = ({ data }) => {
          clearTimeout(timeout);
          if (data.error) reject(new Error(data.error));
          else resolve(data);
        };
        worker.onerror = () => {
          clearTimeout(timeout);
          stop();
        };
        worker.postMessage(message);
      });
    }

    async function perform(message, action) {
      form.inert = true;
      form.setAttribute("aria-busy", "true");
      status.textContent = message;
      try {
        await action();
      } catch (error) {
        status.textContent = error.message;
      } finally {
        form.inert = false;
        form.removeAttribute("aria-busy");
      }
    }

    function updateOptions() {
      const categories = Object.keys(currentPolicy.sensitivity_assessment.categories)
        .map((key) => [key, label(key)])
        .sort((left, right) => left[1].localeCompare(right[1]));
      for (const column of columns) {
        syncOptions(column.category, categories, "Choose a category", column.category.value || column.initial);
        if (!column.category.value) column.suggestion.hidden = true;
        column.initial = "";
      }
      syncOptions(target, Object.keys(currentPolicy.classification_levels).map((level) => [level, level]),
        "No target");
    }

    function addColumns(rows, definitions, suggestCategories) {
      columns = rows.map(({ column_name: name, data_type: type, row_count, null_count, distinct_count }) => {
        const row = element("fieldset");
        row.append(element("legend", type ? `${name} (${type})` : name));
        const description = element("input");
        description.type = "text";
        const initial = Object.hasOwn(definitions, name) ? definitions[name] : {};
        description.value = initial.description ?? "";
        const category = element("select");
        for (const [title, control] of [["Description", description], ["Business category", category]]) {
          const wrapper = element("label", title);
          wrapper.append(control);
          row.append(wrapper);
        }
        const counts = [];
        if (row_count != null) counts.push(`${row_count} rows`);
        if (null_count != null) counts.push(`${null_count} blank`);
        if (distinct_count != null) counts.push(`${distinct_count} distinct`);
        const suggestion = element("small", "Category suggested from the header. Review its business use.");
        suggestion.hidden = !suggestCategories || !initial.category ||
          !Object.hasOwn(currentPolicy.sensitivity_assessment.categories, initial.category);
        suggestion.className = "sensitivity-calculator__column-detail";
        category.addEventListener("change", () => { suggestion.hidden = true; });
        if (counts.length) {
          const stats = element("small", counts.join(" · "));
          stats.className = "sensitivity-calculator__column-detail";
          row.append(stats);
        }
        row.append(suggestion);
        return { name, row, description, category, suggestion, initial: initial.category ?? "" };
      });
      fields.replaceChildren(...columns.map(({ row }) => row));
      updateOptions();
    }

    async function assess() {
      const definitions = Object.fromEntries(columns.map(({ name, description, category }) => [
        name, { description: description.value, category: category.value || null },
      ]));
      const result = await send({
        action: "assess", profile, definitions, policy: activePolicyText, target: target.value || null,
        sensitiveLinkage: linkage.value ? linkage.value === "yes" : null,
      });
      const policyLabel = usingDefaults ? "Using FabricOps defaults." : "Using your applied policy.";
      renderResults(result, results, policyLabel);
      const scope = label(result.scope.kind).toLowerCase();
      status.textContent = `Assessment complete for ${profileName.textContent}. Profile scope is ${scope}.`;
    }

    function restoreDefaultPolicy() {
      currentPolicy = defaultPolicy;
      activePolicyText = JSON.stringify(defaultPolicy, null, 2);
      policy.value = activePolicyText;
      usingDefaults = true;
    }

    async function loadProfile({ upload, scenario }) {
      await perform(upload ? "Profiling the CSV and starting the calculator…" : "Loading scenario…", async () => {
        if (upload?.size > 2 * 1024 * 1024) throw new Error("Choose a CSV file up to 2 MB.");
        const csv = upload ? await upload.text() : scenario.csv;
        const data = await send(csv !== undefined ? {
          action: "dataset", text: csv, profileScope: scenario?.profileScope, columnOnly: scenario?.columnOnly,
        } : { action: "load", text: JSON.stringify(scenario.profile) });
        profile = data.profile;
        defaultPolicy ??= data.defaultPolicy;
        if (!currentPolicy) restoreDefaultPolicy();
        addColumns(data.columns, scenario?.definitions ?? data.definitions, Boolean(upload));
        linkage.closest("label").hidden = data.columnOnly;
        linkage.value = scenario?.sensitiveLinkage == null ? "" : scenario.sensitiveLinkage ? "yes" : "no";
        inputs.hidden = false;
        results.hidden = true;
        profileName.textContent = upload ? upload.name : scenario.title;
        sampleData.hidden = !scenario?.csv;
        sampleCSV.textContent = scenario?.csv ?? "";
        sparkReference.hidden = !scenario?.spark;
        if (scenario?.spark) {
          const { classification, handling } = scenario.spark.expected;
          sparkReference.textContent = `With the default policy and a Spark scan, this scenario assessed as ${classification}, with ${handling} handling. The browser uses your active policy and the profile evidence available here.`;
        }
        if (upload) {
          picker.value = "";
          loadScenario.disabled = true;
        }
        await assess();
      });
      file.value = "";
    }

    let currentSlide = 0;
    const showcasePosition = showcase.querySelector("[data-showcase-position]");

    function moveShowcase(offset) {
      slides[currentSlide].hidden = true;
      currentSlide = (currentSlide + offset + slides.length) % slides.length;
      const slide = slides[currentSlide];
      slide.hidden = false;
      const title = slide.querySelector("figcaption strong").textContent;
      showcasePosition.textContent = `${currentSlide + 1} of ${slides.length}`;
      showcasePosition.setAttribute("aria-label", `${currentSlide + 1} of ${slides.length}. ${title}`);
    }

    showcase.querySelector("[data-showcase-previous]").addEventListener("click", () => moveShowcase(-1));
    showcase.querySelector("[data-showcase-next]").addEventListener("click", () => moveShowcase(1));
    showcase.querySelector("[data-showcase-nav]").hidden = false;
    for (const button of showcaseButtons) {
      button.addEventListener("click", () => {
        picker.value = button.dataset.showcaseScenario;
        loadScenario.disabled = false;
        loadProfile({ scenario: scenarios.get(picker.value) });
      });
    }

    fetch(scenariosURL).then(async (response) => {
      if (!response.ok) throw new Error("Scenario library is unavailable.");
      const groups = { C: "Single columns", T: "Datasets", S: "Spark group-size checks" };
      const options = Object.fromEntries(Object.entries(groups).map(([prefix, title]) => {
        const group = element("optgroup");
        group.label = title;
        return [prefix, group];
      }));
      for (const scenario of await response.json()) {
        scenarios.set(scenario.id, scenario);
        options[scenario.id[0]].append(new Option(scenario.title, scenario.id));
      }
      picker.replaceChildren(new Option("Choose a scenario", ""), ...Object.values(options));
      picker.disabled = false;
      for (const button of showcaseButtons) {
        button.hidden = !scenarios.has(button.dataset.showcaseScenario);
      }
    }).catch(() => {
      picker.replaceChildren(new Option("Scenarios unavailable", ""));
    });

    picker.addEventListener("change", () => {
      loadScenario.disabled = !scenarios.has(picker.value);
    });
    loadScenario.addEventListener("click", () => loadProfile({ scenario: scenarios.get(picker.value) }));
    file.addEventListener("change", () => {
      if (file.files[0]) loadProfile({ upload: file.files[0] });
    });
    dictionary.addEventListener("change", async () => {
      const upload = dictionary.files[0];
      if (!upload || !profile) return;
      await perform("Applying data dictionary…", async () => {
        if (upload.size > 2 * 1024 * 1024) throw new Error("Choose a dictionary file up to 2 MB.");
        const { definitions } = await send({
          action: "dictionary",
          text: await upload.text(),
          csv: /\.csv$/i.test(upload.name),
          columns: columns.map(({ name }) => name),
          categories: Object.keys(currentPolicy.sensitivity_assessment.categories),
        });
        for (const column of columns) {
          if (!Object.hasOwn(definitions, column.name)) continue;
          const definition = definitions[column.name];
          column.description.value = definition.description;
          if (definition.category) {
            column.category.value = definition.category;
            column.suggestion.hidden = true;
          }
        }
        await assess();
      });
      dictionary.value = "";
    });
    form.addEventListener("input", (event) => {
      if (event.target === policy) {
        status.textContent = "Select Apply policy and assess to use your edits.";
      } else if (![picker, file, dictionary].includes(event.target) && !results.hidden) {
        status.textContent = "Run another assessment to update the results.";
      }
    });
    apply.addEventListener("click", () => perform("Checking policy…", async () => {
      const draft = policy.value;
      currentPolicy = await send({ action: "policy", policy: draft });
      activePolicyText = draft;
      usingDefaults = draft === JSON.stringify(defaultPolicy, null, 2);
      updateOptions();
      await assess();
    }));
    reset.addEventListener("click", () => perform("Restoring default policy…", async () => {
      restoreDefaultPolicy();
      updateOptions();
      await assess();
    }));
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (profile) perform("Assessing profile…", assess);
    });
  }

  if (typeof document$ !== "undefined") document$.subscribe(initialize);
  else document.addEventListener("DOMContentLoaded", initialize);
})();
