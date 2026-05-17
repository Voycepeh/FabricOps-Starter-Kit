# `03_pc_<agreement>_<pipeline>`

Use this page to understand the purpose and segment flow of this notebook template. Each segment shows the typical callables commonly used there.

Pipeline notebook flow for deterministic enforcement and controlled publishing.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_pc_agreement_pipeline_template.ipynb">Open template notebook</a>

> `03_pc` loads approved metadata and enforces controls.

## Segment 1: Load shared config and runtime context

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

## Segment 2: Load source data and validate required columns

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
  </tbody>
</table>

## Segment 3: Transform and apply runtime standards

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
      <td data-label="Callable"><a href="../../api/reference/standardize_columns/"><code>standardize_columns</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/technical_columns/" title="Open technical_columns module page" aria-label="Open technical_columns module page">technical_columns</a></td>
      <td data-label="Why it is commonly used here">Apply canonical technical/audit enrichment in one notebook-facing wrapper.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/validate_dq_rules/"><code>validate_dq_rules</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Validate canonical DQ rules before enforcement.</td>
    </tr>
  </tbody>
</table>

## Segment 4: Run DQ, split outputs, and publish

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
      <td data-label="Callable"><a href="../../api/reference/enforce_dq/"><code>enforce_dq</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Enforce approved DQ rules and return structured deterministic outputs.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/assert_dq_passed/"><code>assert_dq_passed</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a></td>
      <td data-label="Why it is commonly used here">Raise only after evidence materialization when error-severity rules fail.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a></td>
      <td data-label="Why it is commonly used here">Write a Spark DataFrame to a Fabric lakehouse Delta table.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a></td>
      <td data-label="Why it is commonly used here">Write a Spark DataFrame to a Microsoft Fabric warehouse table.</td>
    </tr>
  </tbody>
</table>

## Optional profiling, drift, governance, lineage, and handover

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
      <td data-label="Callable"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a></td>
      <td data-label="Why it is commonly used here">Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/check_schema_drift/"><code>check_schema_drift</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a></td>
      <td data-label="Why it is commonly used here">Compare a current dataframe schema against a baseline schema snapshot.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/check_partition_drift/"><code>check_partition_drift</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a></td>
      <td data-label="Why it is commonly used here">Check partition-level drift using keys, partitions, and optional watermark baselines.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/check_profile_drift/"><code>check_profile_drift</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a></td>
      <td data-label="Why it is commonly used here">Compare profile metrics against a baseline profile and drift thresholds.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/summarize_drift_results/"><code>summarize_drift_results</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a></td>
      <td data-label="Why it is commonly used here">Summarize schema, partition, and profile drift outcomes into one decision.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/write_governance/"><code>write_governance</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a></td>
      <td data-label="Why it is commonly used here">Persist approved governance rows to metadata table.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/write_governance/"><code>write_governance</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a></td>
      <td data-label="Why it is commonly used here">Persist approved governance rows to metadata table.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/load_governance/"><code>load_governance</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a></td>
      <td data-label="Why it is commonly used here">Load approved governance metadata as read-only agreement context.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/build_lineage_records/"><code>build_lineage_records</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a></td>
      <td data-label="Why it is commonly used here">Build compact lineage records for downstream metadata sinks.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/build_lineage_handover_markdown/"><code>build_lineage_handover_markdown</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a></td>
      <td data-label="Why it is commonly used here">Build a concise markdown handover summary from lineage execution results.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/build_handover/"><code>build_handover</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a></td>
      <td data-label="Why it is commonly used here">Build a handover-friendly summary for one data product run.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/render_handover_markdown/"><code>render_handover_markdown</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a></td>
      <td data-label="Why it is commonly used here">Render a handover summary dictionary into Markdown for handover notes.</td>
    </tr>
  </tbody>
</table>

