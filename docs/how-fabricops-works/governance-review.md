# Governance Review

Governance Review is the metadata control panel for FabricOps. `02_pipeline` runs first: it writes real data tables, profiles the actual columns that landed, and records catalogue/profile metadata. `03_governance` then runs separately, usually from a governance workspace or governance notebook, so reviewers can augment that profiled catalogue without editing pipeline code.

![FabricOps Governance Review operating model](../assets/fabricops-goverance-review.png)

The page follows the flow in the diagram:

1. `02_pipeline` writes real data tables and records catalogue/profile metadata for the tables and columns that actually exist.
2. `03_governance` opens the profiled catalogue as a control panel for metadata augmentation.
3. Governance users add or update business context, sensitivity/classification, personal-data or identifier classification, DQ expectations, and optional governance notes.
4. Approved augmentations are stored as governed metadata/configuration.
5. Later `02_pipeline` runs read that metadata/configuration and apply the relevant guardrails, checks, and behaviours.

AI can help draft suggested metadata, but AI output is advisory only. A person must approve, edit, or reject suggestions before they become governed metadata.

## Operating model

FabricOps keeps metadata configuration separate from runtime pipeline engineering:

- `02_pipeline` runs first and writes the real target tables.
- `02_pipeline` profiles those tables and records catalogue/profile metadata for the real columns, row counts, data types, null counts, distinct counts, min/max values, and related run context.
- `03_governance` runs separately as a metadata control panel over that profiled catalogue output.
- Governance users augment the catalogue with human-approved meaning, classification, DQ expectations, and notes.
- Approved augmentations are stored in metadata tables as append-only governed configuration.
- Later pipeline runs consume reviewed metadata and apply relevant guardrails, checks, and behaviours.
- AI suggestions stay advisory until a human reviewer commits them.

Some governance metadata cannot be created safely before actual tables and columns exist. For example, reviewers need to see the real column names and profiling signals before approving column meaning, sensitivity, identifier classification, or DQ expectations. That is why `03_governance` works after `02_pipeline` has created and profiled the table.

## Why `03_governance` is separate

`03_governance` is separate so governance users can configure metadata without changing production pipeline code. The pipeline remains responsible for writing data and applying approved configuration. The governance notebook remains responsible for controlled metadata augmentation.

This separation keeps the handoff junior-friendly:

- Pipeline engineers can focus on table creation, profiling, and guardrail execution.
- Governance reviewers can focus on what the profiled columns mean and which metadata should govern later runs.
- Approved metadata remains visible in metadata tables instead of being hidden inside notebook logic.
- Later `02_pipeline` runs behave consistently because they read governed metadata/configuration instead of relying on ad hoc edits.

## What `02_pipeline` creates before governance

`02_pipeline` creates the data and catalogue foundation that Governance Review augments. Typical outputs include:

| Pipeline output | How `03_governance` uses it |
|---|---|
| Real data tables | Reviewers augment metadata for tables and columns that actually exist. |
| Profile and catalogue metadata | Reviewers see table identity, column names, data types, row counts, null counts, distinct counts, min/max values, and distribution signals where available. |
| Guardrail and DQ evidence | Reviewers can understand what the pipeline observed when deciding which metadata or expectations to approve. |
| Lineage and run metadata | Reviewers can see which environment, dataset, table, notebook, activity, and run context produced the profiled catalogue rows. |

In this page, “evidence” means the profile/catalogue and run signals produced by `02_pipeline`. The main job of `03_governance` is to augment that profiled catalogue, not to act as the runtime enforcement layer.

## What reviewers augment

Governance Review captures append-only human-reviewed metadata/configuration:

| Augmentation area | Metadata table | What reviewers add or approve |
|---|---|---|
| Business context | `METADATA_COLUMN_CONTEXT` | Human-readable meaning, notes, and context for real profiled columns. |
| Sensitivity/classification | `METADATA_COLUMN_CLASSIFICATION` | Sensitivity labels and handling requirements for profiled columns. |
| Personal-data or identifier classification | `METADATA_COLUMN_CLASSIFICATION` | Whether columns represent personal data, identifiers, or other governed classification signals. |
| Guardrail rules | `METADATA_GUARDRAIL_RULES` | Active approved or proposed schema, freshness, profile-behavior, and DQ rules that later pipeline runs can load and enforce. |
| Governance outcome notes | `METADATA_GOVERNANCE_REVIEWS` | Optional outcome notes, blockers, warnings, or review decisions for the table. |

AI suggestions can be useful starting points, especially for first-pass descriptions or candidate DQ expectations, but they are never auto-approved.

## Human metadata workflow

A typical metadata augmentation flow is:

1. `02_pipeline` writes and profiles a real table.
2. A governance user opens `03_governance` from the governance workspace or governance notebook.
3. The user selects a profile target with [widget_select_governance_profile_target](../api/reference/widget_select_governance_profile_target/), choosing the physical asset first (asset/lakehouse or warehouse, schema/layer, table) and then the profile date/run.
4. The notebook loads the profiled catalogue rows with `load_catalogue_profile_rows`.
5. The user augments column business context, sensitivity/classification, personal-data or identifier classification, and DQ expectations.
6. The user commits reviewed metadata with `record_table_governance` and related commit actions.
7. Optional governance outcome notes are stored when useful for handover.
8. Later `02_pipeline` runs read the reviewed metadata/configuration and apply the relevant behaviours.

The important control point is the commit. Nothing becomes governed metadata until a human reviewer explicitly commits it.

## Callable references

Use these generated API references for the helpers behind the governance review flow:

- [widget_select_governance_profile_target](../api/reference/widget_select_governance_profile_target/), [get_selected_catalogue_table](../api/reference/get_selected_catalogue_table/), and [load_catalogue_profile_rows](../api/reference/load_catalogue_profile_rows/) select the profiled table under review. The selector treats source/target `profile_stage` and pipeline/run metadata as supporting evidence for profile history, not as the physical table identity.
- [widget_review_column_context](../api/reference/widget_review_column_context/), [widget_review_dq_rules](../api/reference/widget_review_dq_rules/), and [widget_review_column_classification](../api/reference/widget_review_column_classification/) capture reviewer decisions.
- [record_table_governance](../api/reference/record_table_governance/) writes reviewed governance metadata for later pipeline enforcement.
- [enforce_dq_rules](../api/reference/enforce_dq_rules/) is the pipeline-side runtime consumer of governance-approved DQ rules.

## DQ expectations in the control panel

DQ expectations are one kind of metadata augmentation in Governance Review; they are not the purpose of the whole page.

- `03_governance` lets reviewers add, edit, approve, deactivate, or reactivate DQ expectations for profiled tables and columns.
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
