# `02_ex_<agreement>_<topic>`

Use this page to understand the purpose and segment flow of this notebook template. Each segment shows the typical callables commonly used there.

Exploration notebook flow used to profile source data and draft advisory AI outputs for human review.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_ex_agreement_topic.ipynb">Open template notebook</a>

> `02_ex` proposes evidence and AI-assisted suggestions.

## Segment 1: Load shared config and runtime

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a></td>
      <td data-label="Why it is commonly used here">Run consolidated FabricOps startup for exploration and pipeline notebooks.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/load_config/"><code>load_config</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a></td>
      <td data-label="Why it is commonly used here">Validate and return a user-supplied framework configuration.</td>
    </tr>
  </tbody>
</table>

## Segment 2: Profile source and capture evidence

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a></td>
      <td data-label="Why it is commonly used here">Read a Delta table from a Fabric lakehouse.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a></td>
      <td data-label="Why it is commonly used here">Read a table from a Microsoft Fabric warehouse.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a></td>
      <td data-label="Why it is commonly used here">Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
    </tr>
  </tbody>
</table>

## Segment 3: AI-assisted drafting (advisory only)

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/draft_dq_rules/"><code>draft_dq_rules</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/review_dq_rules/"><code>review_dq_rules</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/write_dq_rules/"><code>write_dq_rules</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Validate, build, and persist approved DQ rules.</td>
    </tr>
  </tbody>
</table>

## Segment 4: Human review and write approved DQ rules

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/write_dq_rules/"><code>write_dq_rules</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Validate, build, and persist approved DQ rules.</td>
    </tr>
  </tbody>
</table>

## Optional lineage notes

