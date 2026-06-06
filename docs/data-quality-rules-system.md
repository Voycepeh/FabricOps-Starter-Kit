# AI-assisted governance review

FabricOps v1.0.0 treats data quality as one part of a notebook workflow, not as a standalone data quality product.

Read [How FabricOps Works](how-fabricops-works/index.md) first. This page then explains the `04_gov` governance review workflow.

The workflow is intentionally lightweight:

1. teams profile and inspect data;
2. engineers implement notebook-scoped guardrails inside each `03_pc` production notebook;
3. `03_pc` records profile and lineage evidence;
4. reviewers use `04_gov` to review governance metadata;
5. teams prepare production handover from the implemented notebook and supporting evidence.

Separate data contracts are not part of the v1.0.0 operating model.

## Where review evidence comes from

`03_pc` creates the production evidence that governance reviewers need:

- current source and output profiles;
- schema and data-change guardrail results;
- notebook-defined DQ check outcomes, when the engineer adds them;
- output write evidence;
- lineage records;
- run summaries for review and handover.

`04_gov` uses that evidence to help reviewers understand columns, candidate DQ expectations, and classification metadata. It is a human review workflow, not an enforcement engine.

## What `04_gov` does

`04_gov` helps reviewers:

- review column context and business meaning;
- review candidate DQ expectations;
- review classification and sensitivity metadata;
- optionally use AI suggestions as a starting point;
- commit reviewed governance metadata after human approval.

AI suggestions are optional and advisory. They must be reviewed, edited where needed, and explicitly approved by a person before they become committed metadata.

## What `04_gov` does not do

`04_gov` does not enforce production rules. It does not block a production run, quarantine rows, change output data, or replace checks implemented in `03_pc`.

Approved DQ expectations stored in metadata are review evidence in v1.0.0. They are not automatically enforced unless an engineer manually implements them as guardrails inside the relevant `03_pc` notebook.

## How expectations become guardrails

When a reviewed DQ expectation should affect production behavior:

1. identify the relevant `03_pc` notebook;
2. add the check where the pipeline logic lives;
3. decide whether the check should warn or stop the run;
4. write outputs only after required guardrails pass;
5. record profile, lineage, and run-summary evidence;
6. rerun the notebook and deliberately test failure behavior.

This keeps the v1.0.0 boundary clear: `03_pc` owns production enforcement, while `04_gov` owns reviewed governance metadata.

## Practical handover note

For handover, point support teams to the production `03_pc` notebook for implemented guardrails and to `04_gov` metadata for reviewed context, expectations, and classifications. The two should support each other, but only the notebook-scoped guardrails in `03_pc` control production behavior in v1.0.0.
