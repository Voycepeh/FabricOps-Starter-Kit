# Governance Review

Governance review is the human review step in FabricOps Starter Kit. It helps people add approved business context to the metadata evidence created by `02_pipeline`.

Read [How FabricOps Works](how-fabricops-works/index.md) first for the standard `01_agreement` → `02_pipeline` → `03_review` path. For pipeline blocking behavior, see [Pipeline Guardrails](schema-and-data-drift.md).

## What governance review adds

`03_review` helps reviewers look at catalogue and profile evidence, then save reviewed metadata for:

| Reviewed area | What it means |
| --- | --- |
| Business context | Plain-language meaning for a table or column. |
| DQ expectations | Human-reviewed expectations such as not-null, uniqueness, accepted values, or range checks. |
| Sensitivity | Notes about how carefully the data should be handled. |
| Classification | Reviewed labels such as PII or other locally defined categories. |

This reviewed metadata supports handover, support, documentation, and possible future pipeline use.

## Who approves it?

A person approves it. AI suggestions can help draft descriptions or expectations, but they are advisory only.

Before approval, reviewers should check that:

- the wording is clear to a consumer;
- the DQ expectation is specific enough for an engineer to implement if needed;
- sensitivity and classification choices match local handling expectations;
- unsupported AI suggestions have been edited or rejected.

## Human approval boundary

`03_review` stores reviewed metadata. It does not enforce anything by itself.

Reviewed DQ expectations, sensitivity, and classification records should not become active just because a draft exists. A human reviewer remains accountable for approving them.

## How it can later affect the pipeline

Reviewed metadata can affect a future `02_pipeline` run only when the pipeline is built to use it.

A practical handoff looks like this:

1. `03_review` saves reviewed metadata.
2. The steward or reviewer agrees which expectations should matter in production.
3. The engineer updates `02_pipeline` to read or implement the approved expectations.
4. The engineer decides whether each check should warn or stop the run.
5. `02_pipeline` records new metadata evidence showing what happened.

This keeps the boundary clear: `03_review` owns reviewed metadata, and `02_pipeline` owns guardrails and enforcement.

## Related page

Use [Pipeline Guardrails](schema-and-data-drift.md) when you need to understand schema checks, data-change checks, and blocking behavior inside `02_pipeline`.
