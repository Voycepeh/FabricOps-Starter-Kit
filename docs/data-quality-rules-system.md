# AI-Assisted Data Quality Rules System

A data analyst profiles source data in a `02_ex_*` notebook. The notebook captures profile evidence such as nulls, distinct values, ranges, patterns, duplicates, and suspicious values.

AI uses that evidence to suggest candidate data quality rules. A human reviewer approves, edits, rejects, or defers each suggestion. Only approved active rules are stored as append-only governance metadata for later enforcement work.

In v1.0.0, `04_gov_dataset_table` stores approved DQ rules but the base `03_pc_*` notebook does not load or enforce them. Future enhanced pipeline patterns can consume these approved rules as part of the wider [How FabricOps Works](how-fabricops-works/index.md) metadata flow.

## Business rules and drift monitoring

Business data quality rules validate whether current records satisfy approved expectations. FabricOps also uses schema and profile drift checks to detect structural or statistical changes that may not cause individual records to fail.

For example, every faculty value may remain valid while the distribution of records changes unexpectedly. Business rules, schema drift, and profile drift therefore operate as complementary controls.

Read [Schema and Data Drift Monitoring](schema-and-data-drift.md) for the monitoring approach.

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and planned deterministic enforcement in pipelines](assets/DQ-with-ai.png){ .full-width }
  <figcaption>Data quality workflow from profiling, rule suggestion, human review, approval, and planned later enforcement.</figcaption>
</figure>

Next read: [Schema and Data Drift Monitoring](schema-and-data-drift.md), [How FabricOps Works](how-fabricops-works/index.md), [Quick Start](quick-start.md), [Function Reference](reference/index.md).

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
   A later enhanced pipeline pattern can load approved active rules and apply the same checks on every run. The v1.0.0 `03_pc` template does not enforce approved DQ rules.

7. **Later enforcement pattern**
   Passing/quarantine split outputs are planned for a future enhanced production pattern, not the v1.0.0 base `03_pc` notebook.

## What happens in the `02_ex_*` notebook

The analyst:

1. loads the source data;
2. profiles columns and candidate keys;
3. reviews profile output;
4. asks AI for candidate rules;
5. checks whether each rule makes business sense;
6. records the review decision.

The `02_ex_*` notebook is for exploration and review. It does not enforce production rules.

## What happens in the v1.0.0 `03_pc_*` notebook

The base pipeline:

1. uses notebook-defined schema and drift guardrails;
2. writes profile evidence to `METADATA_DATA_CATALOGUE`;
3. does not load approved DQ rules for enforcement;
4. does not quarantine rows based on approved governance metadata.

AI is not used during production pipeline checks. Approved-rule enforcement is planned for a later enhancement.

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
| `approval_status` | Whether the rule is approved for storage and future enforcement work. |
| `approved_by` | Reviewer who approved the rule. |
| `approved_at` | When approval happened. |
| `active_flag` | Whether the rule is currently stored for later enforcement. |
| `severity` | How failure should be handled. |

Planned future enforcement evidence:

| Field | Purpose |
| --- | --- |
| `run_id` | Future pipeline run that applies the rule. |
| `rule_id` | Rule that would be applied by a future enhanced pipeline. |
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

Suggestions, review decisions, approved rules, and rejected rules are stored as evidence. Future enforcement outcomes can be added by a later enhanced pipeline pattern. Teams can use that evidence to improve prompts and rule suggestions.
