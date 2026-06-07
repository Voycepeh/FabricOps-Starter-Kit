# Governance Review

Governance Review is where metadata evidence becomes reviewed metadata.

`02_pipeline` records metadata evidence about source and target data. `03_review` uses that evidence to help reviewers add business context, DQ expectations, sensitivity, and classification. AI can help draft suggestions, but people approve the final values.

The boundary is simple: `03_review` owns review and approval. `02_pipeline` owns guardrails and enforcement later, only when it is built to use the approved metadata.

Read [How FabricOps Works](how-fabricops-works/index.md) first for the standard `01_agreement` → `02_pipeline` → `03_review` path. For pipeline blocking behavior, see [Pipeline Guardrails](schema-and-data-drift.md).

## From AI assisted DQ to governance review

This workflow started as an AI assisted data quality pattern:

1. source data is profiled;
2. profile data is used to suggest DQ rules;
3. a human reviews the suggestions;
4. approved rules are stored;
5. a later pipeline can enforce the approved rules.

That same pattern now applies to more than DQ. Governance Review uses profile evidence to support AI assisted suggestions, human review, approved metadata storage, and future pipeline use.

```text
metadata evidence → AI suggestion → human review → reviewed metadata → later pipeline use
```

## What `03_review` uses

`03_review` reads metadata evidence created by `02_pipeline`, especially profile rows stored in `METADATA_DATA_CATALOGUE`.

That catalogue evidence can include:

- table and column names;
- observed data types;
- row counts;
- null counts and null percentages;
- distinct counts and distinct percentages;
- observed ranges such as minimum and maximum values;
- compact distribution evidence;
- source or target profile context;
- pipeline and environment context.

AI suggestions are based on the available catalogue profile data. If profile evidence is incomplete, the suggestion may also be incomplete. Reviewers should treat suggestions as drafts, not approvals.

## What reviewers approve

| Review area | Stored in | Purpose |
| --- | --- | --- |
| Business context | `METADATA_COLUMN_CONTEXT` | Human-approved meaning of a table or column. |
| DQ expectations | `METADATA_DQ_RULES` | Human-reviewed rules or expectations that a pipeline can later implement. |
| Sensitivity and classification | `METADATA_COLUMN_CLASSIFICATION` | Human-approved handling, sensitivity, PII, or classification labels, including fields such as approved PII classification, confidentiality label, handling requirement, and masking requirement. |

These outputs are reviewed metadata. They support review, support, documentation, visibility, and later pipeline guardrails when engineering chooses to implement them.

## Human review workflow

The `03_review` widgets follow the same basic pattern for context, DQ expectations, sensitivity, and classification:

1. Load catalogue profile evidence from `METADATA_DATA_CATALOGUE`.
2. Generate optional AI suggestions from the available evidence.
3. Show the suggestions in the review widget.
4. Let the reviewer edit, overwrite, reject, or accept the suggested value.
5. Commit the approved value.
6. Store the approved value in the relevant metadata table.

In short:

- AI suggests.
- Humans approve.
- Metadata stores.
- Pipelines enforce only when implemented.

## How approved metadata returns to the pipeline

`03_review` does not enforce rules directly.

Approved metadata becomes useful in later runs when `02_pipeline` reads or implements it. DQ expectations approved in `METADATA_DQ_RULES` are loaded by `02_pipeline` as aggregate guardrails before the target write.

The same idea can apply to other reviewed metadata:

| Reviewed metadata | Possible later `02_pipeline` use |
| --- | --- |
| Business context | Include approved descriptions in downstream documentation or support evidence. |
| DQ expectations | Run active approved DQ rules that warn or block before the target write. Warning failures continue, tag rows, and write the full dataset; error failures block. |
| Sensitivity and classification | Record handling context or support checks that an engineer intentionally adds. |

The pipeline decides how reviewed metadata is used. For DQ rules, v1 uses severity: warning failures log a warning, add `_dq_check_status` and `_dq_failed_rules` to the full target dataset, and continue, while error failures block through `stop_if_failed(...)`. Aggregate DQ summary fields are stored with existing profiling/catalogue evidence. The DQ guardrail does not create DQ failure tables, quarantine tables, row-level metadata evidence, filtered writes, alert sends, or partial target writes. Aggregated DQ results can feed dashboards and alerts later.

## What this page is not

Governance Review is not:

- a separate data quality product;
- a standalone policy engine;
- a claim that AI approved the rules;
- a replacement for `02_pipeline` guardrails.

It is the review workflow that turns profile evidence into reviewed metadata for later use.
