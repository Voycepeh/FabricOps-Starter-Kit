# AI-Assisted Data Quality Rules System

A data analyst profiles source data in a `02_ex_*` notebook. The notebook captures profile evidence such as nulls, distinct values, ranges, patterns, duplicates, and suspicious values.

AI uses that evidence to suggest candidate data quality rules. A human reviewer approves, edits, rejects, or defers each suggestion. Only approved active rules are stored for enforcement.

A `03_pc_*` notebook loads approved rules during pipeline runs, applies them to the current dataframe or table, sends passing rows downstream, and quarantines failed rows with reasons.

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and deterministic enforcement in pipelines](assets/DQ-with-ai.png){ .full-width }
  <figcaption>Data quality workflow from profiling, rule suggestion, review, approval, enforcement, quarantine, and feedback.</figcaption>
</figure>

Next read: [Metadata](metadata-and-contracts/index.md), [Start](quick-start.md), [API](reference/index.md).

## Operating flow

1. **Source data**
   Analyst starts with the raw dataframe or source table.

2. **Profile in `02_ex_*`**
   Capture nulls, distinct values, ranges, patterns, duplicates, and suspicious values.

3. **Suggest rules**
   AI suggests candidate DQ rules from the profile evidence.

4. **Review rules**
   Human reviewer approves, edits, rejects, or defers each suggestion.

5. **Store approved rules**
   Approved active rules are saved as metadata. Rejected and deferred rules are kept as review evidence only.

6. **Enforce in `03_pc_*`**
   Pipeline contract notebook loads approved active rules and applies the same checks on every run.

7. **Split outputs**
   Passing rows continue downstream. Failed rows go to quarantine with failure reasons.

## What happens in the `02_ex_*` notebook

The analyst:

1. loads the source data;
2. profiles columns and candidate keys;
3. reviews profile output;
4. asks AI for candidate rules;
5. checks whether each rule makes business sense;
6. records the review decision.

The `02_ex_*` notebook is for exploration and review. It does not enforce production rules.

## What happens in the `03_pc_*` notebook

The pipeline:

1. loads approved active rules;
2. applies them to the current dataframe or table;
3. writes accepted rows to the target layer;
4. writes failed rows to quarantine;
5. records rule results, failure reasons, and run context.

AI is not used during enforcement. The `03_pc_*` notebook only runs approved active rules.

## Metadata to capture

| Field | Purpose |
| --- | --- |
| `rule_id` | Identifies the rule. |
| `agreement_id` or `data_product_id` | Links the rule to the agreement or product context. |
| `table_name` | Identifies the table being checked. |
| `column_name` | Identifies the column being checked, when applicable. |
| `rule_type` | Names the check type. |
| `rule_parameters` | Stores the values or expression used by the check. |
| `suggested_by_ai` | Shows whether the rule started as an AI suggestion. |
| `human_decision` | Records approve, edit, reject, or defer. |
| `approval_status` | Shows whether the rule is approved for enforcement. |
| `approved_by` | Identifies the reviewer who approved the rule. |
| `approved_at` | Records when approval happened. |
| `active_flag` | Controls whether an approved rule is currently enforced. |
| `severity` | Describes the enforcement level. |
| `failure_reason` | Explains why a row failed. |
| `run_id` | Links results to the pipeline run. |

## Starter rule types

- not null
- allowed values
- numeric range
- date range
- format or regex
- uniqueness
- referential check
- freshness
- duplicate detection

## Feedback loop

Suggestions, review decisions, approved rules, rejected rules, and enforcement outcomes are stored as evidence. Teams can use that evidence to improve future prompts and rule suggestions.
