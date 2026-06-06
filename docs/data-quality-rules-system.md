# AI-assisted DQ expectation review

A data analyst profiles source data in a `02_ex_*` notebook. The notebook captures profile evidence such as nulls, distinct values, ranges, patterns, duplicates, and suspicious values.

AI can use that evidence to suggest candidate DQ expectations. A human reviewer approves, edits, rejects, or defers each suggestion. Reviewed active expectations are stored as append-only governance metadata.

In v1.0.0, `04_gov` stores reviewed DQ expectations, but the base `03_pc` template does not load or enforce them. They are advisory metadata unless a team manually implements them as guardrails inside the relevant `03_pc` notebook.

## v1.0.0 boundary

| Area | v1.0.0 behavior |
| --- | --- |
| AI suggestions | Optional and advisory only. |
| Human review | Required before suggestions become committed governance metadata. |
| Metadata storage | Reviewed expectations are stored in `METADATA_DQ_RULES`. |
| Production enforcement | Lives in `03_pc` only when engineers implement the checks in that notebook. |
| Future enhancement | Optional metadata-driven execution and rule promotion are planned after v1.0.0. |

## Business expectations and data-change monitoring

Business DQ expectations describe what reviewers expect from current records. FabricOps also uses schema and profile/data-change checks to detect structural or statistical changes that may not cause individual records to fail.

For example, every value in a column may remain valid while the distribution of records changes unexpectedly. Business expectations, schema checks, and data-change monitoring therefore operate as complementary controls when teams implement them in `03_pc`.

Read [Schema and Data-Change Guardrails](schema-and-data-drift.md) for the production-control guardrail approach.

<figure markdown>
  ![Data quality workflow with AI suggestions, human review, approval, and planned deterministic enforcement in pipelines](assets/DQ-with-ai.png){ .full-width }
  <figcaption>DQ expectation workflow from profiling, suggestion, human review, metadata storage, and planned later metadata-driven enforcement.</figcaption>
</figure>

## Operating flow

1. **Profile source/topic data**
   `02_ex` captures profile evidence from the dataframe or source table.

2. **Suggest expectations**
   AI may suggest candidate expectations from profile evidence when configured.

3. **Review expectations**
   A human reviewer approves, edits, rejects, or defers each suggestion.

4. **Store reviewed metadata**
   Reviewed active expectations are saved to `METADATA_DQ_RULES`. Rejected and deferred items remain review evidence.

5. **Implement guardrails when needed**
   If an expectation should stop production, an engineer manually implements the check inside the relevant `03_pc` notebook and smoke tests the failure behavior.

6. **Planned later pattern**
   Optional metadata-driven rule execution, rule promotion, and richer monitoring are planned after v1.0.0.

## What happens in `02_ex`

The analyst:

1. loads the source/topic data;
2. profiles columns and candidate keys;
3. reviews profile output;
4. optionally asks AI for candidate expectations;
5. checks whether each expectation makes business sense;
6. records the review decision.

`02_ex` is for exploration and evidence. It does not enforce production rules.

## What happens in v1.0.0 `03_pc`

The production-control notebook:

1. uses notebook-defined schema and data-change guardrails;
2. can include manually implemented DQ checks;
3. writes profile evidence to `METADATA_DATA_CATALOGUE`;
4. writes outputs only after implemented blocking guardrails pass;
5. does not automatically load or enforce reviewed DQ expectations from metadata.

AI is not used during production pipeline checks.

## Metadata to capture

Expectation metadata:

| Field | Purpose |
| --- | --- |
| `rule_id` | Identifies the reviewed expectation. |
| `agreement_id` or `data_product_id` | Links the expectation to the agreement or product where used. |
| `table_name` | Table being reviewed. |
| `column_name` | Column being reviewed, when applicable. |
| `rule_type` | Expectation/check type. |
| `rule_parameters` | Values or expression used by the expectation. |
| `suggested_by_ai` | Whether the expectation started as an AI suggestion. |
| `human_decision` | Approve, edit, reject, or defer. |
| `approval_status` | Whether the expectation is approved for metadata storage. |
| `approved_by` | Reviewer who approved the expectation. |
| `approved_at` | When approval happened. |
| `active_flag` | Whether the expectation is currently active as reviewed metadata. |
| `severity` | Intended severity if a team later implements the expectation as a guardrail. |

Planned future enforcement evidence:

| Field | Purpose |
| --- | --- |
| `run_id` | Future pipeline run that applies a metadata-driven rule. |
| `rule_id` | Reviewed expectation applied by a future enhanced pipeline. |
| `failure_reason` | Why the row failed. |
| `failed_row_count` | Number of failed rows. |
| `accepted_row_count` | Number of accepted rows. |

## Starter expectation types

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

Suggestions, review decisions, approved expectations, rejected expectations, and manually implemented guardrail outcomes are evidence. Teams can use that evidence to improve review prompts, production notebooks, and future rule-promotion workflows.
