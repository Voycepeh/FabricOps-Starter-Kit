# Function Reference

Use this page as a callable lookup after you understand the notebook flow.

> Graph exploration is intentionally deferred. Future PR may use Neo4j or a proper graph backend.

## Find a callable

Use the finder below to look up public callable functions.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search callable functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search callable functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, role, starter path, or what the public function does.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">csv</span> <span class="callable-finder-chip">data_quality</span> <span class="callable-finder-chip">quarantine</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing all public callables.</p>
  <fieldset class="callable-role-filters">
    <legend>Role filters</legend>
    <label><input type="checkbox" data-role-filter="essential" checked> Essential</label>
    <p class="callable-role-note"><strong>Essential</strong>: Core functions used in the starter notebook flow.</p>
    <label><input type="checkbox" data-role-filter="optional" checked> Optional</label>
    <p class="callable-role-note"><strong>Optional</strong>: Extra helper functions for advanced or situational use.</p>
  </fieldset>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No callables match your search.</p>
</div>

## Function catalogue

## All public functions

<div class="reference-catalogue-list">
<article id="assert_dq_passed" class="reference-catalogue-item" data-callable-row="true" data-callable-name="assert_dq_passed" data-callable-module="data_quality" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Raise only after evidence materialization when error-severity rules fail.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/assert_dq_passed/"><code>assert_dq_passed</code></a></h3>
  <p class="reference-catalogue-item-purpose">Raise only after evidence materialization when error-severity rules fail.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="assert_no_blocking_profile_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="assert_no_blocking_profile_drift" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Raise when profile drift check results should block notebook execution.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/assert_no_blocking_profile_drift/"><code>assert_no_blocking_profile_drift</code></a></h3>
  <p class="reference-catalogue-item-purpose">Raise when profile drift check results should block notebook execution.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>SchemaDriftError</code></li></ul></details>

  </div>
</article>
<article id="build_handover" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_handover" data-callable-module="handover" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Build a handover-friendly summary for one data product run.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_handover/"><code>build_handover</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build a handover-friendly summary for one data product run.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="build_lineage_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_handover_markdown" data-callable-module="data_lineage" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Build a concise markdown handover summary from lineage execution results.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_lineage_handover_markdown/"><code>build_lineage_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build a concise markdown handover summary from lineage execution results.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="build_lineage_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_records" data-callable-module="data_lineage" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Build compact lineage records for downstream metadata sinks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_lineage_records/"><code>build_lineage_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build compact lineage records for downstream metadata sinks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="build_runtime_audit_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_runtime_audit_fields" data-callable-module="metadata" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Build shared runtime audit values; 03_pc uses notebook and committed-by context while adding dataframe audit columns inline.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build shared runtime audit values; 03_pc uses notebook and committed-by context while adding dataframe audit columns inline.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_save_agreement_evidence_records</code></li></ul></details>
  </div>
</article>
<article id="check_partition_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="check_partition_drift" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Check partition-level drift using keys, partitions, and optional watermark baselines.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/check_partition_drift/"><code>check_partition_drift</code></a></h3>
  <p class="reference-catalogue-item-purpose">Check partition-level drift using keys, partitions, and optional watermark baselines.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>build_partition_snapshot</code></li><li><code>compare_partition_snapshots</code></li><li><code>default_incremental_safety_policy</code></li></ul></details>

  </div>
</article>
<article id="check_profile_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="check_profile_drift" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Compare profile metrics against a baseline profile and drift thresholds.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/check_profile_drift/"><code>check_profile_drift</code></a></h3>
  <p class="reference-catalogue-item-purpose">Compare profile metrics against a baseline profile and drift thresholds.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_categorical_distance</code></li><li><code>_normalize_profile</code></li><li><code>_numeric_psi</code></li><li><code>_profile_check_status</code></li><li><code>default_profile_drift_policy</code></li></ul></details>

  </div>
</article>
<article id="check_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="check_schema" data-callable-module="drift" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Check a dataframe has the expected pipeline-local columns and datatypes before continuing.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/check_schema/"><code>check_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Check a dataframe has the expected pipeline-local columns and datatypes before continuing.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>SchemaDriftError</code></li><li><code>_actual_schema</code></li><li><code>_normalize_datatype</code></li></ul></details>

  </div>
</article>
<article id="current_notebook_active_registrations" class="reference-catalogue-item" data-callable-row="true" data-callable-name="current_notebook_active_registrations" data-callable-module="metadata" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Return active latest agreement registrations for the running notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/current_notebook_active_registrations/"><code>current_notebook_active_registrations</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return active latest agreement registrations for the running notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>load_notebook_registry</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="default_profile_drift_policy" class="reference-catalogue-item" data-callable-row="true" data-callable-name="default_profile_drift_policy" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return lightweight default thresholds for profile-based data drift checks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/default_profile_drift_policy/"><code>default_profile_drift_policy</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return lightweight default thresholds for profile-based data drift checks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>check_profile_drift</code></li></ul></details>
  </div>
</article>
<article id="draft_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="draft_business_context" data-callable-module="business_context" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Run Fabric AI to draft column business context suggestions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/draft_business_context/"><code>draft_business_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run Fabric AI to draft column business context suggestions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="draft_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="draft_dq_rules" data-callable-module="data_quality" data-callable-starter-path="02_ex" data-role="essential" data-callable-purpose="Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/draft_dq_rules/"><code>draft_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_extract_dq_rules</code></li><li><code>_prepare_dq_profile_input_rows</code></li><li><code>_suggest_dq_rules</code></li></ul></details>

  </div>
</article>
<article id="draft_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="draft_governance" data-callable-module="data_governance" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Run Fabric AI personal-identifier suggestion prompt on prepared governance rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/draft_governance/"><code>draft_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run Fabric AI personal-identifier suggestion prompt on prepared governance rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="enforce_dq" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_dq" data-callable-module="data_quality" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Enforce approved DQ rules and return structured deterministic outputs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_dq/"><code>enforce_dq</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce approved DQ rules and return structured deterministic outputs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>DQEnforcementResult</code></li><li><code>_load_active_dq_rules</code></li><li><code>_run_dq_rules</code></li><li><code>_split_dq_rows</code></li><li><code>validate_dq_rules</code></li></ul></details>

  </div>
</article>
<article id="extract_categorical_distribution_categories" class="reference-catalogue-item" data-callable-row="true" data-callable-name="extract_categorical_distribution_categories" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Extract baseline categorical vocabularies so current profiles can produce comparable categorical distributions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/extract_categorical_distribution_categories/"><code>extract_categorical_distribution_categories</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract baseline categorical vocabularies so current profiles can produce comparable categorical distributions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_normalize_profile</code></li></ul></details>

  </div>
</article>
<article id="extract_column_business_context_suggestions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="extract_column_business_context_suggestions" data-callable-module="business_context" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Extract review-ready business context suggestion rows from AI responses.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/extract_column_business_context_suggestions/"><code>extract_column_business_context_suggestions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract review-ready business context suggestion rows from AI responses.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_extract_column_business_context_suggestions</code></li></ul></details>

  </div>
</article>
<article id="extract_governance_suggestions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="extract_governance_suggestions" data-callable-module="data_governance" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Extract review-ready governance suggestions from AI responses.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/extract_governance_suggestions/"><code>extract_governance_suggestions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract review-ready governance suggestions from AI responses.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_extract_pii_suggestions</code></li></ul></details>

  </div>
</article>
<article id="extract_numeric_distribution_bin_edges" class="reference-catalogue-item" data-callable-row="true" data-callable-name="extract_numeric_distribution_bin_edges" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Extract baseline numeric bin edges so current profiles can produce comparable PSI distributions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/extract_numeric_distribution_bin_edges/"><code>extract_numeric_distribution_bin_edges</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract baseline numeric bin edges so current profiles can produce comparable PSI distributions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_normalize_profile</code></li></ul></details>

  </div>
</article>
<article id="get_docs_url" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_docs_url" data-callable-module="versioning" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return the published documentation URL for a package version.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_docs_url/"><code>get_docs_url</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the published documentation URL for a package version.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/versioning/" title="Open versioning module page" aria-label="Open versioning module page">versioning</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>get_docs_version</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>print_runtime_banner</code></li></ul></details>
  </div>
</article>
<article id="get_docs_version" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_docs_version" data-callable-module="versioning" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Map a full package version to the matching major.minor documentation version.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_docs_version/"><code>get_docs_version</code></a></h3>
  <p class="reference-catalogue-item-purpose">Map a full package version to the matching major.minor documentation version.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/versioning/" title="Open versioning module page" aria-label="Open versioning module page">versioning</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>get_package_version</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>get_docs_url</code></li></ul></details>
  </div>
</article>
<article id="get_dq_review_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_dq_review_results" data-callable-module="data_quality" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Collect current approved/rejected DQ review results from widget state.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_dq_review_results/"><code>get_dq_review_results</code></a></h3>
  <p class="reference-catalogue-item-purpose">Collect current approved/rejected DQ review results from widget state.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_attach_rule_metadata_keys</code></li></ul></details>

  </div>
</article>
<article id="get_notebook_registry_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_notebook_registry_schema" data-callable-module="metadata" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return the required notebook registry metadata columns.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_notebook_registry_schema/"><code>get_notebook_registry_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the required notebook registry metadata columns.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="get_package_version" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_package_version" data-callable-module="versioning" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return the installed FabricOps Starter Kit package version for the active notebook runtime.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_package_version/"><code>get_package_version</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the installed FabricOps Starter Kit package version for the active notebook runtime.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/versioning/" title="Open versioning module page" aria-label="Open versioning module page">versioning</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>get_docs_version</code></li><li><code>get_release_notes_url</code></li><li><code>print_runtime_banner</code></li></ul></details>
  </div>
</article>
<article id="get_release_notes_url" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_release_notes_url" data-callable-module="versioning" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return the patch-specific release notes URL for a package version.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_release_notes_url/"><code>get_release_notes_url</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the patch-specific release notes URL for a package version.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/versioning/" title="Open versioning module page" aria-label="Open versioning module page">versioning</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>get_package_version</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>print_runtime_banner</code></li></ul></details>
  </div>
</article>
<article id="get_reviewed_business_context_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_reviewed_business_context_rows" data-callable-module="business_context" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return reviewed business context rows from widget state.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_reviewed_business_context_rows/"><code>get_reviewed_business_context_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return reviewed business context rows from widget state.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Return the agreement selected by :func:`widget_select_agreement`.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the agreement selected by :func:`widget_select_agreement`.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="load_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_dq_rules" data-callable-module="data_quality" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Load latest active approved DQ rules from append-only metadata history.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_dq_rules/"><code>load_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load latest active approved DQ rules from append-only metadata history.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_load_active_dq_rules</code></li></ul></details>

  </div>
</article>
<article id="load_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_governance" data-callable-module="data_governance" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Load approved governance metadata as read-only agreement context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_governance/"><code>load_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load approved governance metadata as read-only agreement context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_coerce_row_dicts</code></li></ul></details>

  </div>
</article>
<article id="load_latest_profile" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_latest_profile" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Load the latest previous successful or approved source/target profile baseline from existing profile metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_latest_profile/"><code>load_latest_profile</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load the latest previous successful or approved source/target profile baseline from existing profile metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_is_missing_table_error</code></li><li><code>_normalize_profile</code></li><li><code>_safe_spark_collect</code></li></ul></details>

  </div>
</article>
<article id="load_notebook_registry" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_notebook_registry" data-callable-module="metadata" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Load notebook registration metadata rows for agreement notebook traceability.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_notebook_registry/"><code>load_notebook_registry</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load notebook registration metadata rows for agreement notebook traceability.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_latest_registration_events</code></li><li><code>_registry_rows_with_defaults</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>current_notebook_active_registrations</code></li></ul></details>
  </div>
</article>
<article id="prepare_business_context_profile_input" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_business_context_profile_input" data-callable-module="business_context" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Prepare profile rows for business context prompt drafting.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_business_context_profile_input/"><code>prepare_business_context_profile_input</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare profile rows for business context prompt drafting.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_prepare_business_context_profile_input</code></li></ul></details>

  </div>
</article>
<article id="prepare_governance_input" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_governance_input" data-callable-module="data_governance" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Prepare governance prompt input rows from profile evidence and approved context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_governance_input/"><code>prepare_governance_input</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare governance prompt input rows from profile evidence and approved context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_prepare_governance_input</code></li></ul></details>

  </div>
</article>
<article id="print_runtime_banner" class="reference-catalogue-item" data-callable-row="true" data-callable-name="print_runtime_banner" data-callable-module="versioning" data-callable-starter-path="00_env_config" data-role="essential" data-callable-purpose="Print the installed package version and matching documentation links in a notebook-friendly banner.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/print_runtime_banner/"><code>print_runtime_banner</code></a></h3>
  <p class="reference-catalogue-item-purpose">Print the installed package version and matching documentation links in a notebook-friendly banner.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/versioning/" title="Open versioning module page" aria-label="Open versioning module page">versioning</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>get_docs_url</code></li><li><code>get_package_version</code></li><li><code>get_release_notes_url</code></li></ul></details>

  </div>
</article>
<article id="profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="02_ex, 03_pc" data-role="essential" data-callable-purpose="Build canonical DQ-ready profiling rows from a Spark DataFrame.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build canonical DQ-ready profiling rows from a Spark DataFrame.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex, 03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_build_distribution_summaries</code></li><li><code>_get_profiled_columns</code></li><li><code>_is_min_max_supported_type</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_prepare_dq_profile_input_rows</code></li></ul></details>
  </div>
</article>
<article id="read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Read a CSV file from a Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Read an Excel file from a Fabric lakehouse Files path and pass options such as skiprows, header, usecols, dtype, and nrows through to pandas.read_excel.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a Fabric lakehouse Files path and pass options such as skiprows, header, usecols, dtype, and nrows through to pandas.read_excel.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Read a Parquet file from a Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet file from a Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_get_store</code></li><li><code>_convert_single_parquet_ns_to_us</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex, 03_pc" data-role="essential" data-callable-purpose="Read a Delta table from a Fabric lakehouse.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Delta table from a Fabric lakehouse.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex, 03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_list_data_stewards</code></li><li><code>load_notebook_registry</code></li><li><code>setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex, 03_pc" data-role="essential" data-callable-purpose="Read a table from a Microsoft Fabric warehouse.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a Microsoft Fabric warehouse.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex, 03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="register_current_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="register_current_notebook" data-callable-module="metadata" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Register current notebook metadata evidence for agreement traceability.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/register_current_notebook/"><code>register_current_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Register current notebook metadata evidence for agreement traceability.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_context_get</code></li><li><code>_notebook_registration_key</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>_write_metadata_rows_legacy</code></li><li><code>column_context_rows_for_spark</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="render_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="render_handover_markdown" data-callable-module="handover" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Render a handover summary dictionary into Markdown for handover notes.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/render_handover_markdown/"><code>render_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a handover summary dictionary into Markdown for handover notes.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_status_of</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>build_handover_record</code></li></ul></details>
  </div>
</article>
<article id="setup_data_agreement_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_data_agreement_tables" data-callable-module="data_agreement" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Create, validate, and report readiness for agreement metadata tables.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create, validate, and report readiness for agreement metadata tables.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_list_data_stewards</code></li></ul></details>

  </div>
</article>
<article id="setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config, 02_ex, 03_pc" data-role="essential" data-callable-purpose="Run consolidated FabricOps startup for exploration and pipeline notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run consolidated FabricOps startup for exploration and pipeline notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">00_env_config, 02_ex, 03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>NotebookSetupContext</code></li><li><code>_get_store</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li></ul></details>

  </div>
</article>
<article id="setup_notebook_registry_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook_registry_table" data-callable-module="metadata" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Create or validate notebook registry metadata before workflow notebooks register themselves.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate notebook registry metadata before workflow notebooks register themselves.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 8</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>write_lakehouse_table</code></li><li><code>_coerce_row_dicts</code></li><li><code>_column_names</code></li><li><code>_notebook_registration_key</code></li><li><code>_safe_str</code></li><li><code>column_context_rows_for_spark</code></li><li><code>get_notebook_registry_schema</code></li></ul></details>

  </div>
</article>
<article id="summarize_drift_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="summarize_drift_results" data-callable-module="drift" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Summarize schema, partition, and profile drift outcomes into one decision.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/summarize_drift_results/"><code>summarize_drift_results</code></a></h3>
  <p class="reference-catalogue-item-purpose">Summarize schema, partition, and profile drift outcomes into one decision.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="validate_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="validate_dq_rules" data-callable-module="data_quality" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Validate canonical DQ rules before enforcement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/validate_dq_rules/"><code>validate_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate canonical DQ rules before enforcement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_run_dq_rules</code></li><li><code>_split_dq_rows</code></li><li><code>enforce_dq</code></li><li><code>write_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_data_agreement" data-role="essential" data-callable-purpose="Render standalone agreement evidence upload controls for an existing agreement version.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone agreement evidence upload controls for an existing agreement version.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_data_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_widget_render_agreement_evidence</code></li></ul></details>

  </div>
</article>
<article id="widget_render_agreement_intake_app" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_intake_app" data-callable-module="data_agreement" data-callable-starter-path="01_data_agreement" data-role="essential" data-callable-purpose="Render and wire the compact agreement-intake section switcher application.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_intake_app/"><code>widget_render_agreement_intake_app</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render and wire the compact agreement-intake section switcher application.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_data_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_render_maintenance_widget</code></li><li><code>_require_ipywidgets</code></li><li><code>_widget_render_agreement_evidence</code></li></ul></details>

  </div>
</article>
<article id="widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_data_agreement" data-role="essential" data-callable-purpose="Render append-only agreement maintenance using active steward rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render append-only agreement maintenance using active steward rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_data_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_data_agreement" data-role="essential" data-callable-purpose="Render append-only data steward maintenance.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render append-only data steward maintenance.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_data_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="widget_review_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_business_context" data-callable-module="business_context" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Display interactive approval widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_business_context/"><code>widget_review_business_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Display interactive approval widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_require_ipywidgets</code></li><li><code>build_metadata_column_key</code></li><li><code>build_metadata_table_key</code></li></ul></details>

  </div>
</article>
<article id="widget_review_dq_rule_deactivations" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_dq_rule_deactivations" data-callable-module="data_quality" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Review active DQ rules one at a time for governed deactivation actions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_dq_rule_deactivations/"><code>widget_review_dq_rule_deactivations</code></a></h3>
  <p class="reference-catalogue-item-purpose">Review active DQ rules one at a time for governed deactivation actions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-optional">Optional</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_require_ipywidgets</code></li></ul></details>

  </div>
</article>
<article id="widget_review_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_dq_rules" data-callable-module="data_quality" data-callable-starter-path="02_ex" data-role="essential" data-callable-purpose="Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_require_ipywidgets</code></li></ul></details>

  </div>
</article>
<article id="widget_review_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_governance" data-callable-module="data_governance" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Display governance review widget and capture approve/reject decisions in module state.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_governance/"><code>widget_review_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Display governance review widget and capture approve/reject decisions in module state.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_undo_last_action</code></li><li><code>_now_utc_iso</code></li><li><code>build_metadata_column_key</code></li><li><code>build_metadata_table_key</code></li></ul></details>

  </div>
</article>
<article id="widget_select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_agreement" data-callable-module="data_agreement" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Render a searchable agreement selector and store selected agreement metadata row in module state.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a searchable agreement selector and store selected agreement metadata row in module state.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_load_agreements</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>current_notebook_active_registrations</code></li><li><code>register_current_notebook</code></li></ul></details>

  </div>
</article>
<article id="write_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_business_context" data-callable-module="business_context" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Persist approved business context rows via metadata writer.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_business_context/"><code>write_business_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Persist approved business context rows via metadata writer.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>write_column_business_context</code></li></ul></details>

  </div>
</article>
<article id="write_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_dq_rules" data-callable-module="data_quality" data-callable-starter-path="02_ex" data-role="essential" data-callable-purpose="Validate, build, and persist approved DQ rules.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_dq_rules/"><code>write_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate, build, and persist approved DQ rules.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_build_dq_rule_history</code></li><li><code>validate_dq_rules</code></li><li><code>write_lakehouse_table</code></li></ul></details>

  </div>
</article>
<article id="write_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_governance" data-callable-module="data_governance" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Persist approved governance rows to metadata table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_governance/"><code>write_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Persist approved governance rows to metadata table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_approved_widget_rows</code></li></ul></details>

  </div>
</article>
<article id="write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Write a Spark DataFrame to a Fabric lakehouse Delta table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a Spark DataFrame to a Fabric lakehouse Delta table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 6</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_write_row</code></li><li><code>write_dq_rules</code></li><li><code>seed_minimal_sample_source_table</code></li><li><code>register_current_notebook</code></li><li><code>setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Write a Spark DataFrame to a Microsoft Fabric warehouse table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a Spark DataFrame to a Microsoft Fabric warehouse table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>

  </div>
</article>
</div>

