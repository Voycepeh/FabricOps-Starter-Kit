# `data_quality` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 10</span><span class="reference-chip">Outbound: 3</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns DQ rule drafting, review, enforcement, quarantine, and quality results.

## Public callables

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Callable</th>
      <th>Tier</th>
      <th>Type</th>
      <th>Summary</th>
      <th>Related helpers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/assert_dq_passed/"><code>assert_dq_passed</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Raise only after evidence materialization when error-severity rules fail.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/draft_dq_rules/"><code>draft_dq_rules</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.</td>
      <td><a href="../../reference/internal/data_quality/_extract_dq_rules/"><code>_extract_dq_rules</code></a> (internal), <a href="../../reference/internal/data_quality/_prepare_dq_profile_input_rows/"><code>_prepare_dq_profile_input_rows</code></a> (internal), <a href="../../reference/internal/data_quality/_suggest_dq_rules/"><code>_suggest_dq_rules</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/enforce_dq/"><code>enforce_dq</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Enforce approved DQ rules and return structured deterministic outputs.</td>
      <td><a href="../../reference/internal/data_quality/_load_active_dq_rules/"><code>_load_active_dq_rules</code></a> (internal), <a href="../../reference/internal/data_quality/_run_dq_rules/"><code>_run_dq_rules</code></a> (internal), <a href="../../reference/internal/data_quality/_split_dq_rows/"><code>_split_dq_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_dq_review_results/"><code>get_dq_review_results</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Collect current approved/rejected DQ review results from widget state.</td>
      <td><a href="../../reference/internal/data_quality/_attach_rule_metadata_keys/"><code>_attach_rule_metadata_keys</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_dq_rules/"><code>load_dq_rules</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load latest active approved DQ rules from append-only metadata history.</td>
      <td><a href="../../reference/internal/data_quality/_load_active_dq_rules/"><code>_load_active_dq_rules</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/review_dq_rules/"><code>review_dq_rules</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.</td>
      <td><a href="../../reference/internal/data_quality/_require_ipywidgets/"><code>_require_ipywidgets</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_dq_rules/"><code>write_dq_rules</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Validate, build, and persist approved DQ rules.</td>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_history/"><code>_build_dq_rule_history</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/review_dq_rule_deactivations/"><code>review_dq_rule_deactivations</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Review active DQ rules one at a time for governed deactivation actions.</td>
      <td><a href="../../reference/internal/data_quality/_require_ipywidgets/"><code>_require_ipywidgets</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/run_dq_rule_review_widget/"><code>run_dq_rule_review_widget</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Render the notebook widget for human review and approval/rejection of candidate DQ rules.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/validate_dq_rules/"><code>validate_dq_rules</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Validate canonical DQ rules before enforcement.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

Split a Spark DataFrame into pass/quarantine outputs for row-level DQ rules.

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Related public callables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/data_quality/_approved_dq_rules_from_review_rows/"><code>_approved_dq_rules_from_review_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_attach_rule_metadata_keys/"><code>_attach_rule_metadata_keys</code></a></td>
      <td><a href="../../reference/get_dq_review_results/"><code>get_dq_review_results</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_deactivation_metadata_df/"><code>_build_dq_rule_deactivation_metadata_df</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_deactivations/"><code>_build_dq_rule_deactivations</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_history/"><code>_build_dq_rule_history</code></a></td>
      <td><a href="../../reference/write_dq_rules/"><code>write_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rules_metadata_df/"><code>_build_dq_rules_metadata_df</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_extract_candidate_rules_from_responses/"><code>_extract_candidate_rules_from_responses</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_extract_dq_rules/"><code>_extract_dq_rules</code></a></td>
      <td><a href="../../reference/draft_dq_rules/"><code>draft_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_latest_dq_rule_versions/"><code>_latest_dq_rule_versions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_load_active_dq_rule_metadata/"><code>_load_active_dq_rule_metadata</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_load_active_dq_rules/"><code>_load_active_dq_rules</code></a></td>
      <td><a href="../../reference/enforce_dq/"><code>enforce_dq</code></a>, <a href="../../reference/load_dq_rules/"><code>load_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_parse_dq_rules_dict_from_text/"><code>_parse_dq_rules_dict_from_text</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_prepare_dq_profile_input_rows/"><code>_prepare_dq_profile_input_rows</code></a></td>
      <td><a href="../../reference/draft_dq_rules/"><code>draft_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_prepare_dq_profile_rows_with_context/"><code>_prepare_dq_profile_rows_with_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_profile_for_dq/"><code>_profile_for_dq</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_require_ipywidgets/"><code>_require_ipywidgets</code></a></td>
      <td><a href="../../reference/review_dq_rule_deactivations/"><code>review_dq_rule_deactivations</code></a>, <a href="../../reference/review_dq_rules/"><code>review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_run_dq_rules/"><code>_run_dq_rules</code></a></td>
      <td><a href="../../reference/enforce_dq/"><code>enforce_dq</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_split_dq_rows/"><code>_split_dq_rows</code></a></td>
      <td><a href="../../reference/enforce_dq/"><code>enforce_dq</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_suggest_dq_rules/"><code>_suggest_dq_rules</code></a></td>
      <td><a href="../../reference/draft_dq_rules/"><code>draft_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_suggest_dq_rules_with_fabric_ai/"><code>_suggest_dq_rules_with_fabric_ai</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

</details>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["data_quality._extract_candidate_rules_from_responses"] --> n1b["data_quality._extract_dq_rules"]
  n2["data_quality._extract_candidate_rules_from_responses"] --> n2b["data_quality._parse_dq_rules_dict_from_text"]
  n3["data_quality._extract_dq_rules"] --> n3b["data_quality._parse_dq_rules_dict_from_text"]
  n4["data_quality._load_active_dq_rule_metadata"] --> n4b["data_quality._latest_dq_rule_versions"]
  n5["data_quality._load_active_dq_rules"] --> n5b["data_quality._latest_dq_rule_versions"]
  n6["data_quality._run_dq_rules"] --> n6b["data_quality._split_dq_rows"]
  n7["data_quality._run_dq_rules"] --> n7b["data_quality.validate_dq_rules"]
  n8["data_quality._split_dq_rows"] --> n8b["data_quality.validate_dq_rules"]
  n9["data_quality.draft_dq_rules"] --> n9b["data_quality._extract_dq_rules"]
  n10["data_quality.draft_dq_rules"] --> n10b["data_quality._prepare_dq_profile_input_rows"]
  n11["data_quality.draft_dq_rules"] --> n11b["data_quality._suggest_dq_rules"]
  n12["data_quality.enforce_dq"] --> n12b["data_quality._load_active_dq_rules"]
  n13["data_quality.enforce_dq"] --> n13b["data_quality._run_dq_rules"]
  n14["data_quality.enforce_dq"] --> n14b["data_quality._split_dq_rows"]
  n15["data_quality.enforce_dq"] --> n15b["data_quality.validate_dq_rules"]
  n16["data_quality.get_dq_review_results"] --> n16b["data_quality._attach_rule_metadata_keys"]
  n17["data_quality.load_dq_rules"] --> n17b["data_quality._load_active_dq_rules"]
  n18["data_quality.review_dq_rule_deactivations"] --> n18b["data_quality._require_ipywidgets"]
  n19["data_quality.review_dq_rules"] --> n19b["data_quality._require_ipywidgets"]
  n20["data_quality.run_dq_rule_review_widget"] --> n20b["data_quality.review_dq_rules"]
  n21["data_quality.write_dq_rules"] --> n21b["data_quality._build_dq_rule_history"]
  n22["data_quality.write_dq_rules"] --> n22b["data_quality.validate_dq_rules"]
```
</div>

</details>

### Outbound

<details>
<summary>Expand cross-module callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  c1["data_quality._attach_rule_metadata_keys"] --> d1["metadata.build_dq_rule_key"]
  c2["data_quality._attach_rule_metadata_keys"] --> d2["metadata.build_metadata_column_key"]
  c3["data_quality._attach_rule_metadata_keys"] --> d3["metadata.build_metadata_table_key"]
  c4["data_quality._build_dq_rule_deactivation_metadata_df"] --> d4["metadata._now_utc_iso"]
  c5["data_quality._build_dq_rule_deactivation_metadata_df"] --> d5["metadata._resolve_action_by"]
  c6["data_quality._build_dq_rule_deactivations"] --> d6["metadata._resolve_action_by"]
  c7["data_quality._build_dq_rule_history"] --> d7["metadata._resolve_action_by"]
  c8["data_quality._build_dq_rules_metadata_df"] --> d8["metadata._now_utc_iso"]
  c9["data_quality._build_dq_rules_metadata_df"] --> d9["metadata._resolve_action_by"]
  c10["data_quality._prepare_dq_profile_input_rows"] --> d10["data_profiling.profile_dataframe"]
  c11["data_quality.write_dq_rules"] --> d11["fabric_input_output.write_lakehouse_table"]
```
</div>

</details>
