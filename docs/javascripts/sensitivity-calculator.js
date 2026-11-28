(() => {
  const workerURL = new URL("sensitivity-calculator-worker.js", document.currentScript.src);
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

  function classification(result) {
    return `${result.classification ?? "Unresolved"} · ${result.minimum_handling_classification ?? "Unresolved"}`;
  }

  function renderResults(result, container) {
    const { default: baseline, current } = result;
    const table = element("table");
    table.className = "sensitivity-calculator__table";
    const caption = table.createCaption();
    caption.textContent = "Assessed classification · Minimum handling";
    const headings = table.createTHead().insertRow();
    for (const title of ["Assessment", "FabricOps defaults", "Edited policy"]) {
      const head = element("th", title);
      head.scope = "col";
      headings.append(head);
    }
    const body = table.createTBody();
    for (const [name, before, after] of [
      [current.scope.column_only ? "Column summary" : "Dataset", baseline, current],
      ...current.columns.map((column, index) => [column.column_name, baseline.columns[index], column]),
    ]) {
      const row = body.insertRow();
      const heading = element("th", name);
      heading.scope = "row";
      row.append(heading);
      for (const assessment of [before, after]) {
        const cell = row.insertCell();
        cell.append(element("div", classification(assessment)));
        if (assessment.human_review_required) cell.append(element("small", "Review required"));
      }
      if (classification(before) !== classification(after) ||
          before.human_review_required !== after.human_review_required) {
        row.lastElementChild.classList.add("sensitivity-calculator__changed");
        row.lastElementChild.append(element("small", "Differs from defaults"));
      }
    }
    const reasons = [
      ...current.dataset_findings.map((finding) => {
        const categories = finding.categories?.map(label).join(" + ");
        return categories ? `${label(finding.code)} (${categories})` : label(finding.code);
      }),
      ...current.limitations.map(label),
      ...current.columns.flatMap((column) => column.evidence.map(
        (code) => `${column.column_name} — ${label(code)}`,
      )),
    ];
    const findings = element("div");
    if (reasons.length) {
      const list = element("ul");
      for (const reason of reasons) list.append(element("li", reason));
      findings.append(element("h4", "Findings under the edited policy"), list);
    }
    if (current.recommended_treatments.length || current.residual_risks.length) {
      const list = element("ul");
      for (const item of current.recommended_treatments) {
        list.append(element("li", `${label(item.parameters.treatment)} ${item.column_name}. ${item.rationale}`));
      }
      for (const risk of current.residual_risks) list.append(element("li", risk));
      findings.append(element("h4", "Treatment suggestions"), list);
    }
    const comparison = element("div");
    comparison.className = "sensitivity-calculator__comparison";
    comparison.tabIndex = 0;
    comparison.setAttribute("role", "region");
    comparison.setAttribute("aria-label", "Classification comparison");
    comparison.append(table);
    container.replaceChildren(element("h3", "Assessment results"), comparison, findings);
    container.hidden = false;
  }

  function initialize() {
    const root = document.querySelector("[data-sensitivity-calculator]");
    if (!root || datasets.has(root)) return;
    datasets.add(root);

    const form = root.querySelector("form");
    const file = root.querySelector("[data-profile-file]");
    const sample = root.querySelector("[data-example]");
    const inputs = root.querySelector("[data-calculator-inputs]");
    const fields = root.querySelector("[data-column-fields]");
    const profileName = root.querySelector("[data-profile-name]");
    const policy = root.querySelector("[data-policy]");
    const apply = root.querySelector("[data-apply]");
    const reset = root.querySelector("[data-reset]");
    const target = root.querySelector("[data-target]");
    const results = root.querySelector("[data-results]");
    const status = root.querySelector("[role=status]");
    let worker;
    let profile;
    let defaultPolicy;
    let currentPolicy;
    let columns = [];

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
        column.initial = "";
      }
      syncOptions(target, Object.keys(currentPolicy.classification_levels).map((level) => [level, level]),
        "No target");
    }

    function addColumns(rows, definitions) {
      columns = rows.map(({ column_name: name, data_type: type }) => {
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
        return { name, row, description, category, initial: initial.category ?? "" };
      });
      fields.replaceChildren(...columns.map(({ row }) => row));
      updateOptions();
    }

    async function assess() {
      const definitions = Object.fromEntries(columns.map(({ name, description, category }) => [
        name, { description: description.value, category: category.value || null },
      ]));
      const result = await send({
        action: "assess", profile, definitions, policy: policy.value, target: target.value || null,
      });
      renderResults(result, results);
      const scope = label(result.current.scope.kind).toLowerCase();
      status.textContent = `Assessment complete. Profile scope is ${scope}.`;
    }

    async function loadProfile(upload) {
      await perform("Loading profile and calculator…", async () => {
        if (upload?.size > 2 * 1024 * 1024) throw new Error("Choose a profile file up to 2 MB.");
        const data = await send(upload ? {
          action: "load", text: await upload.text(), csv: /\.csv$/i.test(upload.name),
        } : { action: "load", example: true });
        profile = data.profile;
        defaultPolicy ??= data.defaultPolicy;
        if (!currentPolicy) {
          currentPolicy = defaultPolicy;
          policy.value = JSON.stringify(defaultPolicy, null, 2);
        }
        addColumns(data.columns, data.definitions);
        inputs.hidden = false;
        results.hidden = true;
        profileName.textContent = upload ? upload.name : "Example profile";
        const count = `${columns.length} ${columns.length === 1 ? "column" : "columns"}`;
        status.textContent = `Loaded ${profileName.textContent}. ${count}.`;
      });
      file.value = "";
    }

    sample.addEventListener("click", () => loadProfile());
    file.addEventListener("change", () => {
      if (file.files[0]) loadProfile(file.files[0]);
    });
    form.addEventListener("input", () => {
      if (!results.hidden) status.textContent = "Run another assessment to update the results.";
    });
    apply.addEventListener("click", () => perform("Checking policy…", async () => {
      currentPolicy = await send({ action: "policy", policy: policy.value });
      updateOptions();
      await assess();
    }));
    reset.addEventListener("click", () => perform("Restoring default policy…", async () => {
      currentPolicy = defaultPolicy;
      policy.value = JSON.stringify(defaultPolicy, null, 2);
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
