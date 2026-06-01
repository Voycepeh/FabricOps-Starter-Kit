# AI-Assisted Data Quality Rules System

A data analyst profiles source data in a `02_ex_*` notebook. The notebook captures profile evidence such as nulls, distinct values, ranges, patterns, duplicates, and suspicious values.

AI uses that evidence to suggest candidate data quality rules. A human reviewer approves, edits, rejects, or defers each suggestion. Only approved active rules are stored for enforcement.

A `03_pc_*` notebook loads approved rules during pipeline runs, applies them to the current dataframe or table, sends passing rows downstream, and quarantines failed rows with reasons. These approved rules are one enforceable part of the wider [How FabricOps Works](how-fabricops-works/index.md): the shared metadata flow used by governance and engineering.

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and deterministic enforcement in pipelines](assets/DQ-with-ai.png){ .full-width }
  <figcaption>Data quality workflow from profiling, rule suggestion, review, approval, enforcement, quarantine, and feedback.</figcaption>
</figure>

Next read: [How FabricOps Works](how-fabricops-works/index.md), [Quick Start](quick-start.md), [Function Reference](reference/index.md).

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

Rule metadata:

| Field | Purpose |
| --- | --- |
| `rule_id` | Identifies the rule. |
| `agreement_id` or `data_product_id` | Links the rule to the agreement or product. |
| `table_name` | Table being checked. |
| `column_name` | Column being checked, when applicable. |
| `rule_type` | Check type. |
| `rule_parameters` | Values or expression used by the check. |
| `suggested_by_ai` | Whether the rule started as an AI suggestion. |
| `human_decision` | Approve, edit, reject, or defer. |
| `approval_status` | Whether the rule is approved for enforcement. |
| `approved_by` | Reviewer who approved the rule. |
| `approved_at` | When approval happened. |
| `active_flag` | Whether the rule is currently enforced. |
| `severity` | How failure should be handled. |

Enforcement evidence:

| Field | Purpose |
| --- | --- |
| `run_id` | Pipeline run that applied the rule. |
| `rule_id` | Rule that was applied. |
| `failure_reason` | Why the row failed. |
| `failed_row_count` | Number of failed rows. |
| `accepted_row_count` | Number of accepted rows. |

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
