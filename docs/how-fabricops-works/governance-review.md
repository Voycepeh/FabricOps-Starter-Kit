# Governance Review

`03_governance` is the metadata enrichment and guardrail governance review control point for FabricOps. It reviews profiled table metadata and guardrail rule intent; it does **not** enforce runtime guardrails. Runtime enforcement happens only in `02_pipeline`.

![FabricOps Governance Review operating model](../assets/fabricops-goverance-review.png)

The current flow is:

1. `02_pipeline` runs profiling and guardrail steps for source tables and target DataFrames.
2. Those steps write catalogue/profile evidence to `METADATA_DATA_CATALOGUE`.
3. `03_governance` selects a profiled target from that catalogue evidence with [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/).
4. Reviewers use [widget_enrich_table_metadata](../api/reference/widget_enrich_table_metadata/) to enrich column metadata.
5. Reviewers use [widget_review_guardrail_governance](../api/reference/widget_review_guardrail_governance/) to review guardrail rule intent and table governance state.
6. Later `02_pipeline` runs read approved active guardrail rules and write runtime outcomes to `METADATA_GUARDRAIL_RESULTS`.

`03_governance` lets reviewers approve and records governance decisions for guardrail rules, catalogue evidence, and runtime enforcement readiness before `02_pipeline` applies approved controls.

AI can help draft suggested metadata, but AI output is advisory only. A person must approve, edit, or reject suggestions before they become governed metadata.

## Operating model

FabricOps keeps enrichment, guardrail intent, catalogue evidence, and runtime enforcement separate:

- `02_pipeline` keeps agreement selection and notebook registry linkage. It starts by selecting an agreement and can register the active pipeline notebook in `METADATA_NOTEBOOK_REGISTRY` before writing pipeline evidence.
- `02_pipeline` profiles source tables and target DataFrames and records observed catalogue/profile evidence in `METADATA_DATA_CATALOGUE`.
- `03_governance` uses catalogue-based guardrail target selection. New target tables can be selected before the physical target table exists, as long as the target DataFrame has been profiled and recorded in `METADATA_DATA_CATALOGUE`.
- `03_governance` surfaces metadata enrichment and guardrail governance review; it does not run runtime enforcement.
- Later `02_pipeline` runs consume reviewed guardrail metadata and apply runtime guardrails.

## Why `03_governance` is separate

`03_governance` is separate so governance users can review metadata and guardrail intent without changing pipeline code. The pipeline remains responsible for data processing, profiling, runtime checks, and enforcement results. The governance notebook remains responsible for table selection, enrichment, and guardrail governance review.

This separation keeps the handoff junior-friendly:

- Pipeline engineers can focus on table creation, profiling, agreement linkage, lineage, and runtime guardrail execution.
- Governance reviewers can focus on what the profiled columns mean, how columns should be classified, and which guardrail intent should govern later runs.
- Approved metadata remains visible in metadata tables instead of being hidden inside notebook logic.
- Later `02_pipeline` runs behave consistently because they read governed metadata/configuration instead of relying on ad hoc edits.

## Current `03_governance` responsibilities

| Responsibility | Widget | Writes |
| --- | --- | --- |
| Select a profiled source table or target DataFrame | `widget_select_guardrail_target` | Reads `METADATA_DATA_CATALOGUE`; does not write runtime outcomes. |
| Metadata enrichment | `widget_enrich_table_metadata` | `METADATA_ENRICHMENT_RULES` |
| Guardrail governance review | `widget_review_guardrail_governance` | `METADATA_GUARDRAIL_RULES` |

The old separated business context, classification, and DQ review widget flow is removed from the current template. DQ belongs with guardrail authoring/review, not metadata enrichment.

## Metadata table split

| Evidence or intent | Metadata table | Main writer |
| --- | --- | --- |
| Catalogue/profile evidence and table policy | `METADATA_DATA_CATALOGUE` | `02_pipeline` profiling/guardrail steps |
| Metadata enrichment | `METADATA_ENRICHMENT_RULES` | `03_governance` enrichment widget |
| Guardrail governance intent | `METADATA_GUARDRAIL_RULES` | Guardrail authoring/review widgets |
| Runtime enforcement outcomes | `METADATA_GUARDRAIL_RESULTS` | `02_pipeline` runtime guardrail enforcement |

## What `02_pipeline` creates before governance

`02_pipeline` creates the catalogue foundation that Governance Review uses. Typical outputs include:

| Pipeline output | How `03_governance` uses it |
|---|---|
| Profiled source table evidence | Reviewers can select and enrich source-table metadata. |
| Profiled target DataFrame evidence | Reviewers can select target DataFrames after profiling, even before or independently of physical target table existence. |
| Profile and catalogue metadata | Reviewers see table identity, column names, data types, row counts, null counts, distinct counts, min/max values, and distribution signals where available. |
| Guardrail and DQ runtime evidence | Reviewers can understand what the pipeline observed; DQ expectations are governed through guardrail authoring/review rather than enrichment. |
| Lineage and run metadata | Reviewers can see which environment, dataset, table, notebook, activity, and run context produced the profiled catalogue rows. |

## Human workflow

A typical current governance flow is:

1. Run `02_pipeline` through the relevant source or target profiling/guardrail steps.
2. Open `03_governance`.
3. Select a catalogue-backed target with [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/).
4. Use [widget_enrich_table_metadata](../api/reference/widget_enrich_table_metadata/) to save enrichment intent and classification metadata.
5. Use [widget_review_guardrail_governance](../api/reference/widget_review_guardrail_governance/) to review table governance state and proposed, bypassed, rejected, or superseded guardrail rules.
6. Rerun `02_pipeline` when runtime enforcement should consume approved active guardrail rules.

The important control point is the commit. Nothing becomes governed metadata until a human reviewer explicitly commits it.

## Callable references

Use these generated API references for the helpers behind the current governance flow:

- [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/) selects profiled targets from `METADATA_DATA_CATALOGUE`.
- [widget_enrich_table_metadata](../api/reference/widget_enrich_table_metadata/) writes enrichment intent and classification enrichment metadata.
- [widget_review_guardrail_governance](../api/reference/widget_review_guardrail_governance/) captures table governance and guardrail rule review decisions.
- [enforce_dq_rules](../api/reference/enforce_dq_rules/) is the pipeline-side runtime consumer of governance-approved DQ rules.

## How reviewed metadata controls later pipeline runs

Approved metadata affects later runs only after it is written to metadata tables.

- Approved business context and classification support downstream reporting, handover, review, and runtime decisions where relevant.
- Approved sensitivity and personal-data classifications can influence later pipeline behaviours, handling expectations, and review decisions.
- Active governance-approved DQ rules are read by `02_pipeline` when it calls `enforce_dq_rules`.
- `enforce_dq_rules` reads `METADATA_GUARDRAIL_RULES` from the configured metadata lakehouse target, resolves the newest version for each DQ rule, keeps only active governance-reviewed rows with `guardrail_type="dq"`, evaluates them, and returns a guardrail result with status, checks, a tagged DataFrame, and summary fields for evidence.

Error-severity DQ failures return `status="failed"` and `can_continue=false`. Warning-severity DQ failures return `status="warning"` and `can_continue=true`.

Approval logs are derived from append-only rows in `METADATA_ENRICHMENT_RULES` and `METADATA_GUARDRAIL_RULES`; there is no separate review log table.
