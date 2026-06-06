# Notebook Templates

FabricOps Starter Kit uses five Microsoft Fabric notebook templates. Each template has one clear responsibility in the v1.0.0 workflow.

The templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

!!! note "Notebook preview"
    The notebook templates are optimized for Microsoft Fabric execution. GitHub may not always render `.ipynb` files reliably. Open the templates in Microsoft Fabric, VS Code, or Jupyter if the GitHub preview fails.

## v1.0.0 scope

The v1.0.0 production control boundary is each `03_pc` notebook. Separate data contracts are not required. The `03_pc` notebook owns the schema checks, data-change checks, notebook-defined DQ checks, output writes, lineage records, profiling evidence, and run summaries for its pipeline.

`04_gov` is a human review workflow. It commits column context, DQ expectations, and classification metadata, but it does not enforce production rules. Governance DQ rules stored in metadata are advisory expectations unless a team manually implements them as guardrails in the relevant `03_pc` notebook. AI suggestions are optional and advisory only.

## Template overview

| Notebook | Main owner | Purpose |
| --- | --- | --- |
| `00_env_config` | Engineer | Defines environment paths and creates or validates all active metadata tables. |
| `01_da` | Governance | Maintains data stewards, data agreements, and supporting evidence. |
| `02_ex` | Analyst or data scientist | Demonstrates example source/topic setup, exploration, profiling, and catalogue evidence. |
| `03_pc` | Engineer | Runs production-control guardrails, repeatable transformations, output writes, profiles, lineage, and run summaries. |
| `04_gov` | Governance | Reviews one catalogue table at a time and commits business context, DQ expectations, and column classifications. |

## Role-based notebook flow

![Role-based notebook workflow from environment configuration through governance review](../assets/fabricops-role-workflow.png){ .full-width }

| Step | Owner | Notebook or action | Result |
| ---: | --- | --- | --- |
| 0 | Engineer | Configure and run `00_env_config`. | Environment paths and active metadata table schemas are ready. |
| 1 | Governance | Use `01_da`. | Steward, agreement, and agreement-evidence records are stored. |
| 2 | Analyst or data scientist | Use `02_ex`. | Example source/topic data is explored and profiled; catalogue evidence is written. |
| 3 | Engineer | Build and run `03_pc`. | The pipeline applies implemented guardrails, writes outputs, writes profile evidence, records lineage, and creates run evidence. |
| 4 | Governance | Use `04_gov`. | Business context, DQ expectations, sensitivity labels, and PII classifications are reviewed and committed table by table. |
| 5 | Engineer | Rerun `03_pc`. | The production notebook continues to enforce its implemented checks; any governance expectations must be manually implemented here to become production guardrails. |
| 6 | Engineer | Store the approved production notebook for handover. | The implementation and supporting metadata remain available for support and future enhancement. |

## What each template owns

### `00_env_config`

Configure this notebook first in each environment.

It defines the environment-specific workspace, lakehouse, warehouse, and metadata paths used by all other notebooks. On first run, it creates every active metadata table with its expected schema. Later runs validate existing schemas before workflow notebooks read or write metadata.

Active metadata setup includes:

- `METADATA_DATA_STEWARD`
- `METADATA_DATA_AGREEMENT`
- `METADATA_DATA_AGREEMENT_EVIDENCE`
- `METADATA_NOTEBOOK_REGISTRY`
- `METADATA_DATA_LINEAGE_TABLE`
- `METADATA_DATA_CATALOGUE`
- `METADATA_DATA_ACCESS`
- `METADATA_COLUMN_CONTEXT`
- `METADATA_DQ_RULES`
- `METADATA_COLUMN_CLASSIFICATION`

Downstream notebooks append or read records. They do not own physical metadata table creation.

### `01_da`

Run this notebook in the Governance workspace.

It captures:

- data steward metadata;
- versioned data agreement metadata;
- supporting agreement evidence.

Creating an agreement generates a stable `agreement_id` and first version. Updating an agreement appends a new version instead of overwriting the previous record. Preserve agreement terminology: data agreements remain part of the kit and are distinct from the v1.0.0 production guardrail boundary.

Governance classification, business context, and DQ expectation review belong in `04_gov`, not `01_da`.

### `02_ex`

Run this notebook for exploration and example source/topic setup.

It demonstrates how analysts can:

- load source or unified data;
- profile source/topic data;
- write catalogue evidence;
- register notebook relationships;
- prepare evidence that later helps reviewers and engineers.

`02_ex` does not enforce production rules and should not be treated as the production boundary.

### `03_pc`

Run this notebook for production-control processing.

The v1.0.0 `03_pc` template owns the pipeline guardrails:

- source and target schema validation;
- source and target data-change monitoring;
- notebook-defined DQ checks where the engineer implements them;
- fail-fast stops for blocking guardrail results;
- output writes to lakehouse or warehouse targets;
- profile/catalogue evidence writes;
- table lineage records;
- run summaries and handover evidence.

The schema and data-change presets live in the notebook so the engineer can make the control boundary explicit for each pipeline. FabricOps does not require a separate metadata artifact for v1.0.0 production enforcement.

Reviewed governance DQ expectations in `METADATA_DQ_RULES` are advisory metadata unless the engineer manually translates them into checks in the relevant `03_pc` notebook.

### `04_gov`

Run this notebook in the Governance workspace after `02_ex` or `03_pc` has written catalogue evidence.

`04_gov` is a table-scoped human review workflow. It selects a catalogue table and supports review of:

- column business context;
- DQ expectations;
- sensitivity labels;
- PII classifications;
- reviewer notes and status fields.

`04_gov` commits reviewed metadata to `METADATA_COLUMN_CONTEXT`, `METADATA_DQ_RULES`, and `METADATA_COLUMN_CLASSIFICATION`. It does not enforce production rules, block pipeline runs, or change output data. AI suggestions are optional, editable, and advisory; no suggestion becomes approved metadata without a human commit action.

## Implemented in v1.0.0

| Capability | Template or component |
| --- | --- |
| Metadata lakehouse setup | `00_env_config` |
| Data agreement, steward, and evidence tables | `01_da` |
| Notebook registry | `00_env_config`, `02_ex`, `03_pc` |
| Production notebook template with schema validation and data-change monitoring | `03_pc` |
| Lakehouse and warehouse IO helpers | `fabricops_kit` helper wheel |
| Profiling/catalogue evidence | `02_ex`, `03_pc` |
| Lineage records | `03_pc` |
| Table-scoped governance review | `04_gov` |
| Human-reviewed column context, DQ expectation, and classification metadata | `04_gov` |
| Handover summary support | Handover helpers and stored notebook evidence |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Full Fabric validation notes from real workspace testing | Capture representative workspace smoke-test evidence. |
| Governance dashboard improvements | Improve dashboard templates and reporting guidance. |
| Optional metadata-driven DQ rule execution | Allow selected `03_pc` notebooks to execute reviewed metadata rules. |
| Rule promotion workflow | Promote approved expectations into implemented notebook guardrails. |
| Richer AI-assisted governance suggestions | Keep suggestions optional and human-reviewed. |
| More complete operational monitoring | Add broader run health and support views. |

## Inputs and outputs by notebook

| Notebook | Reads | Writes |
| --- | --- | --- |
| `00_env_config` | Environment-specific configuration values | Metadata table schemas and path configuration |
| `01_da` | Steward and agreement input | Agreement, steward, and evidence metadata |
| `02_ex` | Source/topic data and agreement context | Notebook registry and catalogue/profile evidence |
| `03_pc` | Agreement metadata, previous profiles, source data, and notebook settings | Output tables, catalogue/profile evidence, lineage, run summaries, and handover evidence |
| `04_gov` | Catalogue evidence and existing governance metadata | Column context, DQ expectations, and classifications |

## Handover principle

For handover, store the approved production `03_pc` notebook and relevant metadata evidence. The production notebook is the most accurate source for implemented checks, data movement, outputs, and operational notes.
