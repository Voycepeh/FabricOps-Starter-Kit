# Governance Review

Governance Review is the operating model that turns pipeline evidence into approved metadata. `02_pipeline` records evidence during normal runs, and `03_governance` helps people review that evidence before any business context, data-quality (DQ) expectations, or sensitivity/classification decisions become governed metadata.

![FabricOps Governance Review operating model](../assets/fabricops-goverance-review.png)

The page follows the flow in the diagram:

1. `02_pipeline` profiles data and records evidence.
2. `03_governance` reviews that evidence with a human in the loop.
3. Approved decisions are written back as metadata.
4. Later `02_pipeline` runs load approved metadata and enforce it where relevant.

AI can help draft suggestions, but AI output is advisory only. A person must approve, edit, or reject suggestions before they become metadata.

## Operating model

FabricOps keeps governance separate from runtime pipeline logic:

- `02_pipeline` records profile, catalogue, guardrail, DQ, lineage, and run evidence during normal execution.
- `03_governance` reviews recorded evidence and captures explicit human decisions.
- Humans approve business context, DQ expectations, and sensitivity/classification.
- Approved decisions are stored in metadata tables as append-only history.
- Later pipeline runs load approved metadata and apply it where it is relevant.
- AI suggestions stay advisory until a human reviewer commits them.

This keeps the workflow metadata-driven and junior-friendly. Engineers can inspect what the pipeline observed, reviewers can see what they are approving, and later runs can enforce approved metadata without hiding governance rules inside notebook code.

## What `02_pipeline` records

`02_pipeline` creates the evidence that Governance Review depends on. Typical evidence includes:

| Evidence area | What it helps reviewers understand |
|---|---|
| Profile and catalogue evidence | Which table was profiled, which columns exist, observed data types, row counts, null counts, distinct counts, min/max values, and distribution signals where available. |
| Guardrail evidence | Whether schema, source stability, and other pipeline guardrails passed, warned, or failed. |
| DQ evidence | Which approved DQ rules were evaluated, which checks passed or failed, and whether failures should block or warn. |
| Lineage evidence | Which upstream and downstream objects were involved in the run. |
| Run evidence | Which environment, dataset, table, notebook, activity, and run summary produced the evidence. |

The pipeline records this evidence first. It does not ask reviewers to approve rules inside the production pipeline path.

## What `03_governance` reviews

`03_governance` starts from the latest successful catalogue evidence, then gives reviewers a focused place to inspect and approve metadata. Reviewers can answer questions such as:

- Which table and profile run are being reviewed?
- Which columns exist in the latest successful profile?
- What do the observed data types, null rates, distinct counts, and min/max values suggest?
- Did recent pipeline runs pass schema, stability, DQ, lineage, and run guardrails?
- Is there enough evidence for a human to approve metadata safely?

The governance notebook writes approved metadata only after explicit commit actions. Draft rows, AI suggestions, and uncommitted edits are not enforced by later pipeline runs.

## What humans approve

Governance Review is responsible for append-only human decisions:

| Review area | Metadata table | What humans approve |
|---|---|---|
| Business context | `METADATA_COLUMN_CONTEXT` | Human-readable meaning, notes, and context for columns. |
| DQ expectations | `METADATA_DQ_RULES` | Active approved DQ rules for a table or columns. |
| Sensitivity/classification | `METADATA_COLUMN_CLASSIFICATION` | Sensitivity labels, personal-data classification, identifier type, and handling requirements. |
| Governance outcome | `METADATA_GOVERNANCE_REVIEWS` | Optional final review outcome based on evidence, blockers, and warnings. |

AI suggestions can be useful starting points, especially for first-pass descriptions or candidate DQ expectations, but they are never auto-approved.

## Human review workflow

A typical review flow is:

1. Select a profiled catalogue table with `widget_select_catalogue_table`.
2. Load profile rows for that selection with `load_catalogue_profile_rows`.
3. Review or edit business context using the column context workflow.
4. Review or edit DQ expectations using `widget_review_dq_rules`.
5. Review sensitivity and personal-data classification.
6. Commit approved rows with `record_table_governance`.
7. Optionally write a governance review outcome after checking related evidence.

The important control point is the commit. Nothing becomes governed metadata until a human reviewer explicitly commits it.

## DQ expectations in the workflow

DQ expectations are one approval area inside Governance Review; they are not the purpose of the whole page.

- `03_governance` reviews the profiling evidence and approves DQ expectations that are appropriate for the table.
- Approved rules are stored as metadata in `METADATA_DQ_RULES`.
- Later `02_pipeline` runs load the newest active approved rules for the table.
- `enforce_dq_rules` enforces those approved rules at runtime and records the outcome as guardrail evidence.

FabricOps uses one canonical DQ rule vocabulary and does not require Great Expectations or dbt at runtime. For the full list of supported rule types, parameters, and examples, see the [DQ rule reference](../reference/dq-rules/index.md).

## How approved metadata returns to the pipeline

Approved metadata affects later runs only after it is written to metadata tables.

- Approved business context and classification become metadata evidence for downstream reporting, handover, and later governance review.
- Approved active DQ rules are read by `02_pipeline` when it calls `enforce_dq_rules`.
- `enforce_dq_rules` reads `METADATA_DQ_RULES` from the configured metadata lakehouse target, resolves the newest version for each rule, keeps only active approved rules, evaluates them, and returns a guardrail result with status, checks, a tagged DataFrame, and summary fields for evidence.

Error-severity DQ failures return `status="failed"` and `can_continue=false`. Warning-severity DQ failures return `status="warning"` and `can_continue=true`.

## What this page is not

Governance Review is not a full data product platform, an external DQ framework wrapper, or a replacement for normal pipeline engineering. It does not move DQ authoring into `02_pipeline`, expose one public Python function per rule, or require Great Expectations or dbt at runtime.

### Schema guardrails are separate

Do not model schema rules such as required columns, expected schema, or datatype checks as DQ rules. Schema guardrails are a separate FabricOps layer and should remain in schema validation configuration.

### Source stability is separate

Do not model source stability checks as DQ rules. Source stability compares catalogue/profile evidence across runs and is handled by the source stability guardrail layer, not by `METADATA_DQ_RULES`.
