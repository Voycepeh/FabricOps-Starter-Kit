# Function Reference

Use this page as a callable lookup after you understand the notebook flow.

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
<article id="assert_dq_passed" class="reference-catalogue-item" data-callable-row="true" data-callable-name="assert_dq_passed" data-callable-module="data_quality" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Raise only after evidence materialization when error-severity rules fail.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/assert_dq_passed/"><code>assert_dq_passed</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Raise only after evidence materialization when error-severity rules fail.</p>
</article>
<article id="build_handover" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_handover" data-callable-module="handover" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Build a handover-friendly summary for one data product run.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/build_handover/"><code>build_handover</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Build a handover-friendly summary for one data product run.</p>
</article>
<article id="build_lineage_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_handover_markdown" data-callable-module="data_lineage" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Build a concise markdown handover summary from lineage execution results.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/build_lineage_handover_markdown/"><code>build_lineage_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Build a concise markdown handover summary from lineage execution results.</p>
</article>
<article id="build_lineage_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_records" data-callable-module="data_lineage" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Build compact lineage records for downstream metadata sinks.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/build_lineage_records/"><code>build_lineage_records</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Build compact lineage records for downstream metadata sinks.</p>
</article>
<article id="check_partition_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="check_partition_drift" data-callable-module="drift" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Check partition-level drift using keys, partitions, and optional watermark baselines.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/check_partition_drift/"><code>check_partition_drift</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Check partition-level drift using keys, partitions, and optional watermark baselines.</p>
</article>
<article id="check_profile_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="check_profile_drift" data-callable-module="drift" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Compare profile metrics against a baseline profile and drift thresholds.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/check_profile_drift/"><code>check_profile_drift</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Compare profile metrics against a baseline profile and drift thresholds.</p>
</article>
<article id="check_schema_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="check_schema_drift" data-callable-module="drift" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Compare a current dataframe schema against a baseline schema snapshot.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/check_schema_drift/"><code>check_schema_drift</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Compare a current dataframe schema against a baseline schema snapshot.</p>
</article>
<article id="draft_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="draft_business_context" data-callable-module="business_context" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Run Fabric AI to draft column business context suggestions.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/draft_business_context/"><code>draft_business_context</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Run Fabric AI to draft column business context suggestions.</p>
</article>
<article id="draft_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="draft_dq_rules" data-callable-module="data_quality" data-callable-starter-path="02_ex" data-role="essential" data-callable-purpose="Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/draft_dq_rules/"><code>draft_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>02_ex</span></p>
  <p class="reference-catalogue-item-purpose">Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.</p>
</article>
<article id="draft_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="draft_governance" data-callable-module="data_governance" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Run Fabric AI personal-identifier suggestion prompt on prepared governance rows.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/draft_governance/"><code>draft_governance</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Run Fabric AI personal-identifier suggestion prompt on prepared governance rows.</p>
</article>
<article id="enforce_dq" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_dq" data-callable-module="data_quality" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Enforce approved DQ rules and return structured deterministic outputs.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/enforce_dq/"><code>enforce_dq</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Enforce approved DQ rules and return structured deterministic outputs.</p>
</article>
<article id="extract_column_business_context_suggestions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="extract_column_business_context_suggestions" data-callable-module="business_context" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Extract review-ready business context suggestion rows from AI responses.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/extract_column_business_context_suggestions/"><code>extract_column_business_context_suggestions</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Extract review-ready business context suggestion rows from AI responses.</p>
</article>
<article id="extract_governance_suggestions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="extract_governance_suggestions" data-callable-module="data_governance" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Extract review-ready governance suggestions from AI responses.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/extract_governance_suggestions/"><code>extract_governance_suggestions</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Extract review-ready governance suggestions from AI responses.</p>
</article>
<article id="get_dq_review_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_dq_review_results" data-callable-module="data_quality" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Collect current approved/rejected DQ review results from widget state.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/get_dq_review_results/"><code>get_dq_review_results</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Collect current approved/rejected DQ review results from widget state.</p>
</article>
<article id="get_reviewed_business_context_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_reviewed_business_context_rows" data-callable-module="business_context" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Return reviewed business context rows from widget state.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/get_reviewed_business_context_rows/"><code>get_reviewed_business_context_rows</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Return reviewed business context rows from widget state.</p>
</article>
<article id="get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Return selected agreement from widget flow.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Return selected agreement from widget flow.</p>
</article>
<article id="load_agreements" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_agreements" data-callable-module="data_agreement" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Load latest distinct agreement metadata rows for widget selection.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/load_agreements/"><code>load_agreements</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Load latest distinct agreement metadata rows for widget selection.</p>
</article>
<article id="load_config" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_config" data-callable-module="config" data-callable-starter-path="00_env_config, 02_ex, 03_pc" data-role="essential" data-callable-purpose="Validate and return a user-supplied framework configuration.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/load_config/"><code>load_config</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>00_env_config, 02_ex, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Validate and return a user-supplied framework configuration.</p>
</article>
<article id="load_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_dq_rules" data-callable-module="data_quality" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Load latest active approved DQ rules from append-only metadata history.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/load_dq_rules/"><code>load_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Load latest active approved DQ rules from append-only metadata history.</p>
</article>
<article id="load_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_governance" data-callable-module="data_governance" data-callable-starter-path="01_data_agreement, 03_pc" data-role="essential" data-callable-purpose="Load approved governance metadata as read-only agreement context.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/load_governance/"><code>load_governance</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>01_data_agreement, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Load approved governance metadata as read-only agreement context.</p>
</article>
<article id="load_notebook_registry" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_notebook_registry" data-callable-module="metadata" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Load notebook registration metadata rows for agreement notebook traceability.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/load_notebook_registry/"><code>load_notebook_registry</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Load notebook registration metadata rows for agreement notebook traceability.</p>
</article>
<article id="prepare_business_context_profile_input" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_business_context_profile_input" data-callable-module="business_context" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Prepare profile rows for business context prompt drafting.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/prepare_business_context_profile_input/"><code>prepare_business_context_profile_input</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Prepare profile rows for business context prompt drafting.</p>
</article>
<article id="prepare_governance_input" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_governance_input" data-callable-module="data_governance" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Prepare governance prompt input rows from profile evidence and approved context.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/prepare_governance_input/"><code>prepare_governance_input</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Prepare governance prompt input rows from profile evidence and approved context.</p>
</article>
<article id="profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="02_ex, 03_pc" data-role="essential" data-callable-purpose="Build canonical DQ-ready profiling rows from a Spark DataFrame.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>02_ex, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Build canonical DQ-ready profiling rows from a Spark DataFrame.</p>
</article>
<article id="read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Read a CSV file from a Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a Fabric lakehouse Files path.</p>
</article>
<article id="read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Read an Excel file from a Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a Fabric lakehouse Files path.</p>
</article>
<article id="read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Read a Parquet file from a Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Read a Parquet file from a Fabric lakehouse Files path.</p>
</article>
<article id="read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex, 03_pc" data-role="essential" data-callable-purpose="Read a Delta table from a Fabric lakehouse.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>02_ex, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Read a Delta table from a Fabric lakehouse.</p>
</article>
<article id="read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex, 03_pc" data-role="essential" data-callable-purpose="Read a table from a Microsoft Fabric warehouse.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>02_ex, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Read a table from a Microsoft Fabric warehouse.</p>
</article>
<article id="register_current_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="register_current_notebook" data-callable-module="metadata" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Register current notebook metadata evidence for agreement traceability.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/register_current_notebook/"><code>register_current_notebook</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Register current notebook metadata evidence for agreement traceability.</p>
</article>
<article id="render_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="render_handover_markdown" data-callable-module="handover" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Render a handover summary dictionary into Markdown for handover notes.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/render_handover_markdown/"><code>render_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Render a handover summary dictionary into Markdown for handover notes.</p>
</article>
<article id="review_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="review_business_context" data-callable-module="business_context" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Display interactive approval widget.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/review_business_context/"><code>review_business_context</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Display interactive approval widget.</p>
</article>
<article id="review_dq_rule_deactivations" class="reference-catalogue-item" data-callable-row="true" data-callable-name="review_dq_rule_deactivations" data-callable-module="data_quality" data-callable-starter-path="—" data-role="optional" data-callable-purpose="Review active DQ rules one at a time for governed deactivation actions.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/review_dq_rule_deactivations/"><code>review_dq_rule_deactivations</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Review active DQ rules one at a time for governed deactivation actions.</p>
</article>
<article id="review_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="review_dq_rules" data-callable-module="data_quality" data-callable-starter-path="02_ex" data-role="essential" data-callable-purpose="Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/review_dq_rules/"><code>review_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>02_ex</span></p>
  <p class="reference-catalogue-item-purpose">Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.</p>
</article>
<article id="review_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="review_governance" data-callable-module="data_governance" data-callable-starter-path="01_data_agreement" data-role="essential" data-callable-purpose="Display governance review widget and capture approve/reject decisions in module state.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/review_governance/"><code>review_governance</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>01_data_agreement</span></p>
  <p class="reference-catalogue-item-purpose">Display governance review widget and capture approve/reject decisions in module state.</p>
</article>
<article id="select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="select_agreement" data-callable-module="data_agreement" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Render a widget dropdown and store selected agreement metadata row in module state.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/select_agreement/"><code>select_agreement</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Render a widget dropdown and store selected agreement metadata row in module state.</p>
</article>
<article id="setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config, 02_ex, 03_pc" data-role="essential" data-callable-purpose="Run consolidated FabricOps startup for exploration and pipeline notebooks.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>00_env_config, 02_ex, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Run consolidated FabricOps startup for exploration and pipeline notebooks.</p>
</article>
<article id="standardize_columns" class="reference-catalogue-item" data-callable-row="true" data-callable-name="standardize_columns" data-callable-module="technical_columns" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Apply canonical technical/audit enrichment in one notebook-facing wrapper.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/standardize_columns/"><code>standardize_columns</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/technical_columns/" title="Open technical_columns module page" aria-label="Open technical_columns module page">technical_columns</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Apply canonical technical/audit enrichment in one notebook-facing wrapper.</p>
</article>
<article id="summarize_drift_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="summarize_drift_results" data-callable-module="drift" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Summarize schema, partition, and profile drift outcomes into one decision.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/summarize_drift_results/"><code>summarize_drift_results</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Summarize schema, partition, and profile drift outcomes into one decision.</p>
</article>
<article id="validate_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="validate_dq_rules" data-callable-module="data_quality" data-callable-starter-path="03_pc" data-role="optional" data-callable-purpose="Validate canonical DQ rules before enforcement.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/validate_dq_rules/"><code>validate_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>optional</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Validate canonical DQ rules before enforcement.</p>
</article>
<article id="write_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_business_context" data-callable-module="business_context" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Persist approved business context rows via metadata writer.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/write_business_context/"><code>write_business_context</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/business_context/" title="Open business_context module page" aria-label="Open business_context module page">business_context</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>—</span></p>
  <p class="reference-catalogue-item-purpose">Persist approved business context rows via metadata writer.</p>
</article>
<article id="write_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_dq_rules" data-callable-module="data_quality" data-callable-starter-path="02_ex" data-role="essential" data-callable-purpose="Validate, build, and persist approved DQ rules.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/write_dq_rules/"><code>write_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_quality/" title="Open data_quality module page" aria-label="Open data_quality module page">data_quality</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>02_ex</span></p>
  <p class="reference-catalogue-item-purpose">Validate, build, and persist approved DQ rules.</p>
</article>
<article id="write_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_governance" data-callable-module="data_governance" data-callable-starter-path="01_data_agreement, 03_pc" data-role="essential" data-callable-purpose="Persist approved governance rows to metadata table.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/write_governance/"><code>write_governance</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/data_governance/" title="Open data_governance module page" aria-label="Open data_governance module page">data_governance</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>01_data_agreement, 03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Persist approved governance rows to metadata table.</p>
</article>
<article id="write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Write a Spark DataFrame to a Fabric lakehouse Delta table.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Write a Spark DataFrame to a Fabric lakehouse Delta table.</p>
</article>
<article id="write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc" data-role="essential" data-callable-purpose="Write a Spark DataFrame to a Microsoft Fabric warehouse table.">
  <h3 class="reference-catalogue-item-name"><a href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-meta"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a> <span class="reference-catalogue-separator">·</span> <span>essential</span> <span class="reference-catalogue-separator">·</span> <span>03_pc</span></p>
  <p class="reference-catalogue-item-purpose">Write a Spark DataFrame to a Microsoft Fabric warehouse table.</p>
</article>
</div>

