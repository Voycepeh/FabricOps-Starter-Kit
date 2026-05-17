# `data_quality` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

| Essential | Optional | Internal | Depends On | Used By |
|---:|---:|---:|---:|---:|
| 7 | 2 | 20 | 3 | 0 |

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`assert_dq_passed`](../../reference/assert_dq_passed/) | function | Raise only after evidence materialization when error-severity rules fail. | — |
| [`draft_dq_rules`](../../reference/draft_dq_rules/) | function | Draft candidate DQ rules from metadata profiles or raw DataFrame fallback. | [`__prepare_dq_profile_input_rows`](../../reference/internal/data_quality/__prepare_dq_profile_input_rows/) (internal), [`_extract_dq_rules`](../../reference/internal/data_quality/_extract_dq_rules/) (internal), [`_suggest_dq_rules`](../../reference/internal/data_quality/_suggest_dq_rules/) (internal) |
| [`enforce_dq`](../../reference/enforce_dq/) | function | Enforce approved DQ rules and return structured deterministic outputs. | [`_load_active_dq_rules`](../../reference/internal/data_quality/_load_active_dq_rules/) (internal), [`_run_dq_rules`](../../reference/internal/data_quality/_run_dq_rules/) (internal), [`_split_dq_rows`](../../reference/internal/data_quality/_split_dq_rows/) (internal) |
| [`get_dq_review_results`](../../reference/get_dq_review_results/) | function | Collect current approved/rejected DQ review results from widget state. | [`_attach_rule_metadata_keys`](../../reference/internal/data_quality/_attach_rule_metadata_keys/) (internal) |
| [`load_dq_rules`](../../reference/load_dq_rules/) | function | Load latest active approved DQ rules from append-only metadata history. | [`_load_active_dq_rules`](../../reference/internal/data_quality/_load_active_dq_rules/) (internal) |
| [`review_dq_rules`](../../reference/review_dq_rules/) | function | Review AI-suggested DQ rules sequentially with explicit approve/reject decisions. | [`_require_ipywidgets`](../../reference/internal/data_quality/_require_ipywidgets/) (internal) |
| [`write_dq_rules`](../../reference/write_dq_rules/) | function | Validate, build, and persist approved DQ rules. | [`_build_dq_rule_history`](../../reference/internal/data_quality/_build_dq_rule_history/) (internal) |

Split a Spark DataFrame into pass/quarantine outputs for row-level DQ rules.

## Optional callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`review_dq_rule_deactivations`](../../reference/review_dq_rule_deactivations/) | function | Review active DQ rules one at a time for governed deactivation actions. | [`_require_ipywidgets`](../../reference/internal/data_quality/_require_ipywidgets/) (internal) |
| [`validate_dq_rules`](../../reference/validate_dq_rules/) | function | Validate canonical DQ rules before enforcement. | — |

## Related internal helpers

<details>
<summary>Expand internal helper table</summary>

| Helper | Related public callables |
|---|---|
| [`__parse_dq_rules_dict_from_text`](../../reference/internal/data_quality/__parse_dq_rules_dict_from_text/) | — |
| [`__prepare_dq_profile_input_rows`](../../reference/internal/data_quality/__prepare_dq_profile_input_rows/) | [`draft_dq_rules`](../../reference/draft_dq_rules/) |
| [`_approved_dq_rules_from_review_rows`](../../reference/internal/data_quality/_approved_dq_rules_from_review_rows/) | — |
| [`_attach_rule_metadata_keys`](../../reference/internal/data_quality/_attach_rule_metadata_keys/) | [`get_dq_review_results`](../../reference/get_dq_review_results/) |
| [`_build_dq_rule_deactivation_metadata_df`](../../reference/internal/data_quality/_build_dq_rule_deactivation_metadata_df/) | — |
| [`_build_dq_rule_deactivations`](../../reference/internal/data_quality/_build_dq_rule_deactivations/) | — |
| [`_build_dq_rule_history`](../../reference/internal/data_quality/_build_dq_rule_history/) | [`write_dq_rules`](../../reference/write_dq_rules/) |
| [`_build_dq_rules_metadata_df`](../../reference/internal/data_quality/_build_dq_rules_metadata_df/) | — |
| [`_extract_candidate_rules_from_responses`](../../reference/internal/data_quality/_extract_candidate_rules_from_responses/) | — |
| [`_extract_dq_rules`](../../reference/internal/data_quality/_extract_dq_rules/) | [`draft_dq_rules`](../../reference/draft_dq_rules/) |
| [`_latest_dq_rule_versions`](../../reference/internal/data_quality/_latest_dq_rule_versions/) | — |
| [`_load_active_dq_rule_metadata`](../../reference/internal/data_quality/_load_active_dq_rule_metadata/) | — |
| [`_load_active_dq_rules`](../../reference/internal/data_quality/_load_active_dq_rules/) | [`enforce_dq`](../../reference/enforce_dq/), [`load_dq_rules`](../../reference/load_dq_rules/) |
| [`_prepare_dq_profile_input_rows`](../../reference/internal/data_quality/_prepare_dq_profile_input_rows/) | — |
| [`_profile_for_dq`](../../reference/internal/data_quality/_profile_for_dq/) | — |
| [`_require_ipywidgets`](../../reference/internal/data_quality/_require_ipywidgets/) | [`review_dq_rule_deactivations`](../../reference/review_dq_rule_deactivations/), [`review_dq_rules`](../../reference/review_dq_rules/) |
| [`_run_dq_rules`](../../reference/internal/data_quality/_run_dq_rules/) | [`enforce_dq`](../../reference/enforce_dq/) |
| [`_split_dq_rows`](../../reference/internal/data_quality/_split_dq_rows/) | [`enforce_dq`](../../reference/enforce_dq/) |
| [`_suggest_dq_rules`](../../reference/internal/data_quality/_suggest_dq_rules/) | [`draft_dq_rules`](../../reference/draft_dq_rules/) |
| [`_suggest_dq_rules_with_fabric_ai`](../../reference/internal/data_quality/_suggest_dq_rules_with_fabric_ai/) | — |

</details>

## Module internal callable graph

```mermaid
flowchart LR
  n1["data_quality._extract_candidate_rules_from_responses"] --> n1b["data_quality.__parse_dq_rules_dict_from_text"]
  n2["data_quality._extract_candidate_rules_from_responses"] --> n2b["data_quality._extract_dq_rules"]
  n3["data_quality._extract_dq_rules"] --> n3b["data_quality.__parse_dq_rules_dict_from_text"]
  n4["data_quality._load_active_dq_rule_metadata"] --> n4b["data_quality._latest_dq_rule_versions"]
  n5["data_quality._load_active_dq_rules"] --> n5b["data_quality._latest_dq_rule_versions"]
  n6["data_quality._run_dq_rules"] --> n6b["data_quality._split_dq_rows"]
  n7["data_quality._run_dq_rules"] --> n7b["data_quality.validate_dq_rules"]
  n8["data_quality._split_dq_rows"] --> n8b["data_quality.validate_dq_rules"]
  n9["data_quality.draft_dq_rules"] --> n9b["data_quality.__prepare_dq_profile_input_rows"]
  n10["data_quality.draft_dq_rules"] --> n10b["data_quality._extract_dq_rules"]
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

## Cross-module callable graph

```mermaid
flowchart LR
  c1[data_quality.__prepare_dq_profile_input_rows] --> d1[data_profiling.profile_dataframe]
  c2[data_quality._attach_rule_metadata_keys] --> d2[metadata.build_dq_rule_key]
  c3[data_quality._attach_rule_metadata_keys] --> d3[metadata.build_metadata_column_key]
  c4[data_quality._attach_rule_metadata_keys] --> d4[metadata.build_metadata_table_key]
  c5[data_quality._build_dq_rule_deactivation_metadata_df] --> d5[metadata._now_utc_iso]
  c6[data_quality._build_dq_rule_deactivation_metadata_df] --> d6[metadata._resolve_action_by]
  c7[data_quality._build_dq_rule_deactivations] --> d7[metadata._resolve_action_by]
  c8[data_quality._build_dq_rule_history] --> d8[metadata._resolve_action_by]
  c9[data_quality._build_dq_rules_metadata_df] --> d9[metadata._now_utc_iso]
  c10[data_quality._build_dq_rules_metadata_df] --> d10[metadata._resolve_action_by]
  c11[data_quality.write_dq_rules] --> d11[fabric_input_output.write_lakehouse_table]
```

## Cross-module references

| Caller | Callee |
|---|---|
| `data_quality.__prepare_dq_profile_input_rows` | `data_profiling.profile_dataframe` |
| `data_quality._attach_rule_metadata_keys` | `metadata.build_dq_rule_key` |
| `data_quality._attach_rule_metadata_keys` | `metadata.build_metadata_column_key` |
| `data_quality._attach_rule_metadata_keys` | `metadata.build_metadata_table_key` |
| `data_quality._build_dq_rule_deactivation_metadata_df` | `metadata._now_utc_iso` |
| `data_quality._build_dq_rule_deactivation_metadata_df` | `metadata._resolve_action_by` |
| `data_quality._build_dq_rule_deactivations` | `metadata._resolve_action_by` |
| `data_quality._build_dq_rule_history` | `metadata._resolve_action_by` |
| `data_quality._build_dq_rules_metadata_df` | `metadata._now_utc_iso` |
| `data_quality._build_dq_rules_metadata_df` | `metadata._resolve_action_by` |
| `data_quality.write_dq_rules` | `fabric_input_output.write_lakehouse_table` |
