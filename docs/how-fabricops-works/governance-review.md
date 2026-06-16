# Governance Review

Governance Review is the guardrail governance control point for FabricOps. `02_pipeline` runs first: it writes real data tables, profiles the actual columns that landed, and records catalogue/profile metadata. `03_governance` then runs separately so reviewers can decide table guardrail governance state, approvals, rejections, supersession, and bypass/post-review outcomes without editing pipeline code.

![FabricOps Governance Review operating model](../assets/fabricops-goverance-review.png)

The page follows the flow in the diagram:

1. `02_pipeline` writes real data tables and records catalogue/profile metadata for the tables and columns that actually exist.
2. `03_governance` opens profiled catalogue targets as a control panel for guardrail governance decisions.
3. Governance users approve, reject, supersede, or post-review bypassed guardrail rules and table governance state.
4. Approved decisions are stored as governed metadata/configuration.
5. Later `02_pipeline` runs read that metadata/configuration and apply the relevant guardrails, checks, and behaviours.

AI can help draft suggested metadata, but AI output is advisory only. A person must approve, edit, or reject suggestions before they become governed metadata.

## Operating model

FabricOps keeps metadata configuration separate from runtime pipeline engineering:

- `02_pipeline` runs first and writes the real target tables.
- `02_pipeline` profiles those tables and records catalogue/profile metadata for the real columns, row counts, data types, null counts, distinct counts, min/max values, and related run context.
- `03_governance` runs separately as a metadata control panel over that profiled catalogue output.
- Governance users review guardrail rules and table governance state for profiled catalogue targets.
- Approved decisions are stored in metadata tables as append-only governed configuration.
- Later pipeline runs consume reviewed metadata and apply relevant guardrails, checks, and behaviours.
- AI suggestions stay advisory until a human reviewer commits them.

Some governance metadata cannot be created safely before actual tables and columns exist. For example, reviewers need to see the real column names and profiling signals before approving column meaning, sensitivity, identifier classification, or DQ expectations. That is why `03_governance` works after `02_pipeline` has created and profiled the table.

## Why `03_governance` is separate

`03_governance` is separate so governance users can configure metadata without changing production pipeline code. The pipeline remains responsible for writing data and applying approved configuration. The governance notebook remains responsible for controlled guardrail governance review decisions.

This separation keeps the handoff junior-friendly:

- Pipeline engineers can focus on table creation, profiling, and guardrail execution.
- Governance reviewers can focus on what the profiled columns mean and which metadata should govern later runs.
- Approved metadata remains visible in metadata tables instead of being hidden inside notebook logic.
- Later `02_pipeline` runs behave consistently because they read governed metadata/configuration instead of relying on ad hoc edits.

## What `02_pipeline` creates before governance

`02_pipeline` creates the data and catalogue foundation that Governance Review uses. Typical outputs include:

| Pipeline output | How `03_governance` uses it |
|---|---|
| Real data tables | Reviewers make guardrail governance decisions for tables and columns that actually exist. |
| Profile and catalogue metadata | Reviewers see table identity, column names, data types, row counts, null counts, distinct counts, min/max values, and distribution signals where available. |
| Guardrail and DQ evidence | Reviewers can understand what the pipeline observed when deciding which metadata or expectations to approve. |
| Lineage and run metadata | Reviewers can see which environment, dataset, table, notebook, activity, and run context produced the profiled catalogue rows. |

In this page, “evidence” means the profile/catalogue and run signals produced by `02_pipeline`. The main job of `03_governance` is guardrail governance review over that profiled catalogue, not to act as the runtime enforcement layer.

## What reviewers decide

Governance Review captures append-only human-reviewed guardrail governance decisions:

| Decision area | Metadata table | What reviewers decide |
|---|---|---|
| Table governance state | `METADATA_GOVERNANCE_REVIEWS` | Whether a profiled table is governed or ungoverned and which approval policy applies. |
| Guardrail rule review | `METADATA_GUARDRAIL_RULES` | Whether proposed or bypassed schema, freshness, profile-behavior, and DQ guardrail rules are approved, rejected, or superseded. |
| Bypass/post-review outcome | `METADATA_GUARDRAIL_RULES` | Whether a bypassed active rule remains acceptable after human review or should be rejected or superseded. |

## Human metadata workflow

A typical guardrail governance review flow is:

1. `02_pipeline` writes and profiles a real table.
2. A governance user opens `03_governance` from the governance workspace or governance notebook.
3. The user selects a profile target with [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/), choosing the profiled guardrail target from metadata-backed catalogue evidence.
4. The current guardrail governance widget displays existing rules and current governance state for the selected profiled target.
5. The user reviews table governance state and proposed, bypassed, rejected, or superseded guardrail rule decisions.
6. The user commits reviewed metadata through the current guardrail governance widget actions.
7. Later `02_pipeline` runs read the reviewed metadata/configuration and apply the relevant behaviours.

The important control point is the commit. Nothing becomes governed metadata until a human reviewer explicitly commits it.

## Callable references

Use these generated API references for the helpers behind the governance review flow:

- [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/) selects the profiled table under guardrail review.
- [widget_review_guardrail_governance](../api/reference/widget_review_guardrail_governance/) captures current table governance and guardrail rule review decisions.
- The current guardrail governance widget writes reviewed governance metadata for later pipeline enforcement.
- [enforce_dq_rules](../api/reference/enforce_dq_rules/) is the pipeline-side runtime consumer of governance-approved DQ rules.

## DQ expectations in the control panel

- `03_governance` lets reviewers approve, reject, supersede, or post-review bypassed guardrail rules for profiled tables.
- Approved rules are stored as governed metadata/configuration in `METADATA_GUARDRAIL_RULES`.
- Later `02_pipeline` runs load the newest active governance-approved rules for the table.
- `enforce_dq_rules` enforces those governance-approved rules at runtime and records the outcome as guardrail evidence.

FabricOps uses one canonical DQ rule vocabulary and does not require Great Expectations or dbt at runtime. For the full list of supported rule types, parameters, and examples, see the [DQ rule reference](../reference/dq-rules/index.md).

## How reviewed metadata controls later pipeline runs

Approved metadata affects later runs only after it is written to metadata tables.

- Approved business context and classification become metadata/configuration for downstream reporting, handover, governance review, and runtime decisions where relevant.
- Approved sensitivity and personal-data classifications can influence later pipeline behaviours, handling expectations, and review decisions.
- Active governance-approved DQ rules are read by `02_pipeline` when it calls `enforce_dq_rules`.
- `enforce_dq_rules` reads `METADATA_GUARDRAIL_RULES` from the configured metadata lakehouse target, resolves the newest version for each DQ rule, keeps only active governance-reviewed rows with `guardrail_type="dq"`, evaluates them, and returns a guardrail result with status, checks, a tagged DataFrame, and summary fields for evidence.

Error-severity DQ failures return `status="failed"` and `can_continue=false`. Warning-severity DQ failures return `status="warning"` and `can_continue=true`.
