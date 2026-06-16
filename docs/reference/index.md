# Function Reference

Use this page as a function lookup after you understand the notebook flow. The default catalogue shows public v1 callables that notebook authors can import from the package root; the Template Function Map shows where those callables are used in starter templates; Implementation Modules show the active source modules that maintainers debug and extend.

- Use [Template Function Map](template-function-map.md) to see what notebook users call from the starter notebook templates.
- Use the [Glossary](glossary.md) for simple definitions of repeated FabricOps terms used on callable pages.
- Use the Function catalogue below to browse public v1 callables. Internal helper details are embedded inside callable pages instead of normal catalogue entries.
- Use Implementation Modules only when debugging or maintaining current major source boundaries; they do not document every `.py` file.

## How to use this reference

- **Callable helpers** are public v1 functions intended for notebook authors and human operators.
- **Internal helpers** are maintainer implementation details embedded inside the public callable pages that use them.
- **Implementation modules** show source ownership, module-level dependencies, and helper relationships for maintainers.
- **Function manifests** (`manifest.json` and `function-manifest.json`) provide machine-readable callable/module inventory for checks and automation.
- **Agent manifest** (`agent-manifest.json`) adds AI-oriented execution fields for planning, side-effect checks, and verification.
- **AI implementation contracts** on callable pages summarize expectations agents must satisfy before using or changing a function.
- **Skill file** (`.agents/skills/fabricops/SKILL.md`) gives agents repo-specific rules and points them to these generated references.

## Find a function

Use the finder below to look up public callables from active v1 modules. For internal helper behavior, open the public callable page and expand the Internal implementation summary.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, function type, starter path, or description.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">csv</span> <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">quarantine</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing callable functions.</p>
  <fieldset class="callable-type-filters">
    <legend>Function type filters</legend>
    <label><input type="checkbox" data-function-type-filter="callable" checked> Callable</label>
    <p class="callable-type-note"><strong>Callable</strong>: Public functions intended for notebook authors.</p>
  </fieldset>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No functions match your search.</p>
</div>

## Function catalogue

## Functions

<div class="reference-catalogue-list">
<article id="pipeline-display_guardrail_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="display_guardrail_results" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Return summary, detailed, or debug guardrail display output for Fabric notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return summary, detailed, or debug guardrail display output for Fabric notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-enforce_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_dq_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Enforce approved active DQ rules as a target-write guardrail without filtering rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce approved active DQ rules as a target-write guardrail without filtering rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="guardrails-enforce_freshness" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_freshness" data-callable-module="guardrails" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Enforce whether the latest data arrived within the configured freshness lag.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_freshness/"><code>enforce_freshness</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce whether the latest data arrived within the configured freshness lag.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>enforce_freshness_rule</code></li><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="guardrails-enforce_freshness_rule" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_freshness_rule" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Evaluate freshness using an active metadata-backed freshness guardrail rule.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_freshness_rule/"><code>enforce_freshness_rule</code></a></h3>
  <p class="reference-catalogue-item-purpose">Evaluate freshness using an active metadata-backed freshness guardrail rule.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>enforce_freshness</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="guardrails-enforce_profile_behavior" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_profile_behavior" data-callable-module="guardrails" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Enforce static, changing, or skipped profile behavior against accepted catalogue profile evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce static, changing, or skipped profile behavior against accepted catalogue profile evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>profile_dataframe</code></li><li><code>read_lakehouse_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Return the agreement selected by widget_select_agreement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the agreement selected by widget_select_agreement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="pipeline-prepare_pipeline_table_configs" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_pipeline_table_configs" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Prepare source or target table configs for 02_pipeline.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare source or target table configs for 02_pipeline.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_profiling-profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>enforce_profile_behavior</code></li><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-callable-starter-path="00_env_config, 02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a CSV file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config, 02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config, 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="fabric_input_output-read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read an Excel file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="fabric_input_output-read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a Parquet path from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet path from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="fabric_input_output-read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore" data-function-type="callable" data-callable-purpose="Read a Delta table from a configured Fabric lakehouse target by ABFSS path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Delta table from a configured Fabric lakehouse target by ABFSS path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore</p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>enforce_profile_behavior</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="00_env_config, 02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a table from a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config, 02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config, 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="pipeline-run_table_guardrails" class="reference-catalogue-item" data-callable-row="true" data-callable-name="run_table_guardrails" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>profile_dataframe</code></li><li><code>enforce_dq_rules</code></li><li><code>enforce_freshness</code></li><li><code>enforce_freshness_rule</code></li><li><code>enforce_profile_behavior</code></li><li><code>stop_if_failed</code></li><li><code>write_catalogue_evidence</code></li></ul></details>

  </div>
</article>
<article id="config-setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-function-type="callable" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="config-setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-function-type="callable" data-callable-purpose="Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="guardrails-stop_if_failed" class="reference-catalogue-item" data-callable-row="true" data-callable-name="stop_if_failed" data-callable-module="guardrails" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/stop_if_failed/"><code>stop_if_failed</code></a></h3>
  <p class="reference-catalogue-item-purpose">Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="governance_review-widget_author_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_dq_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Render interactive manual or AI-assisted DQ guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive manual or AI-assisted DQ guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-widget_author_schema_freshness_profile_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_schema_freshness_profile_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Render interactive schema, freshness, and profile-behavior guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive schema, freshness, and profile-behavior guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-widget_enrich_table_metadata" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_enrich_table_metadata" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-function-type="callable" data-callable-purpose="Render a consolidated column metadata enrichment widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a consolidated column metadata enrichment widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_agreement-widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-function-type="callable" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 01_agreement</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_agreement-widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-function-type="callable" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 01_agreement</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_agreement-widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-function-type="callable" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 01_agreement</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-widget_review_guardrail_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_guardrail_governance" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-function-type="callable" data-callable-purpose="Render interactive controls for reviewing proposed and bypassed guardrail rules.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive controls for reviewing proposed and bypassed guardrail rules.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_agreement-widget_select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_agreement" data-callable-module="data_agreement" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Render an agreement selector and optionally register the active notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an agreement selector and optionally register the active notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-widget_select_guardrail_target" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_guardrail_target" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-function-type="callable" data-callable-purpose="Render an interactive target selector for guardrail authoring and governance review.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an interactive target selector for guardrail authoring and governance review.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="pipeline-write_catalogue_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_catalogue_evidence" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Enrich profile rows with guardrail context and write catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enrich profile rows with guardrail context and write catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>write_lakehouse_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="00_env_config, 01_agreement, 02_pipeline, 03_governance" data-function-type="callable" data-callable-purpose="Write a DataFrame to a configured Fabric lakehouse target by ABFSS path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric lakehouse target by ABFSS path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config, 01_agreement, 02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config, 01_agreement, 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>write_catalogue_evidence</code></li><li><code>write_pipeline_lineage</code></li><li><code>write_pipeline_run_summary</code></li></ul></details>
  </div>
</article>
<article id="pipeline-write_pipeline_lineage" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_lineage" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Write many-to-many source-to-target lineage evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write many-to-many source-to-target lineage evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>write_lakehouse_table</code></li></ul></details>

  </div>
</article>
<article id="pipeline-write_pipeline_run_summary" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_run_summary" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Write one pipeline runtime summary row to metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write one pipeline runtime summary row to metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>write_lakehouse_table</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="00_env_config, 02_pipeline" data-function-type="callable" data-callable-purpose="Write a DataFrame to a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config, 02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config, 02_pipeline</p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
</div>

