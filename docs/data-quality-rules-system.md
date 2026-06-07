# Governance Review

FabricOps treats data quality as one part of a notebook pipeline workflow, not as a standalone data quality product.

Read [How FabricOps Works](how-fabricops-works/index.md) first for the required `01_agreement` → `02_pipeline` → `03_review` delivery path. This page focuses on how `03_review` enriches metadata for review and later pipeline use.

Separate data contracts are not part of the current operating model.

## Where review metadata comes from

`02_pipeline` creates the pipeline metadata that governance reviewers need:

- current source and output profiles;
- schema and data-change guardrail results;
- notebook-defined DQ check outcomes, when the engineer adds them;
- output write metadata;
- lineage records;
- run summaries for review.

`03_review` uses that metadata to help reviewers understand columns, candidate data quality rules, sensitivity, and classification. It is a human review workflow that adds governed metadata for later pipeline runs.

## What `03_review` does

`03_review` helps reviewers enrich metadata with:

- business context;
- data quality rules;
- data sensitivity;
- classification.

Reviewers may optionally use AI suggestions as a starting point. AI suggestions are advisory. A person must review, edit where needed, and approve governance metadata before it is used by a pipeline.

## Human approval boundary

Reviewed governance metadata should not become active just because an AI suggestion exists or because a draft row was created. A person remains accountable for approving business context, data quality rules, sensitivity, and classification.

After approval, the metadata becomes useful when `02_pipeline` reads or implements the approved rules and classifications during pipeline runs.

## How reviewed metadata becomes pipeline behavior

When reviewed governance metadata should affect pipeline behavior:

1. identify the relevant `02_pipeline` notebook;
2. decide which approved rules and classifications the pipeline should read or implement;
3. decide whether each check should warn or stop the run;
4. apply the approved metadata alongside schema and data drift guardrails;
5. write outputs only after required guardrails pass;
6. record profile, lineage, and run-summary metadata;
7. rerun the notebook and test failure behavior where blocking checks are expected.

This keeps the boundary clear: `03_review` owns reviewed governance metadata, and `02_pipeline` owns pipeline enforcement.

## What to review before approval

Before approving governance metadata, reviewers should check:

- whether the business context describes the column or table in plain wording;
- whether each data quality rule is specific enough for `02_pipeline` to read or implement;
- whether sensitivity values match the intended data handling policy;
- whether classifications are appropriate for the data and audience;
- whether any AI suggestion has been edited or rejected when it is not accurate.
