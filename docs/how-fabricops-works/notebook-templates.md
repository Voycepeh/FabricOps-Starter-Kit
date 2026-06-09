# Notebook Templates

FabricOps Starter Kit uses a small set of notebook templates so teams can move from agreement to pipeline to review without inventing a new process for every data product.

## The templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

![Role-based notebook workflow from environment configuration through governance review](../assets/fabricops-role-workflow.png){ .full-width }

## What each template is for

### `00_env_config`

Run first in each environment.

Defines environment paths, Fabric item targets, metadata lakehouse settings, downstream defaults, and active metadata table schemas.

On first run, it creates metadata tables if needed. Later runs validate expected schemas.

**Result:** environment paths and active metadata schemas are ready.

### `01_agreement`

Run when governance needs to capture the request, ownership, and supporting evidence.

Records business purpose, steward and owner details, support expectations, and agreement evidence.

It stores agreement metadata only. It does not approve classifications, save reviewed DQ rules, or enforce checks.

**Result:** steward, agreement, and agreement-evidence records are stored.

### `99_explore`

Use only when optional discovery or troubleshooting is useful.

Supports source exploration, profiling, pre-agreement checks, failed-run investigation, or review questions.

Run in Engineering Dev and link it to one or more agreements when relevant.

**Result:** data is explored and profiled.

### `02_pipeline`

Run when engineering is ready to build or run the data product.

It is a thin orchestration notebook. Users first read source data into DataFrames using normal Spark code or the same helper functions shown in `99_explore`, then register those existing DataFrames with per-source schema/stability/DQ guardrails. After transformation, users register target DataFrames with write settings and target guardrails. FabricOps starts after each DataFrame exists: it profiles, validates, enforces approved active DQ rules, records evidence, and writes configured targets. Reusable evidence helpers hide catalogue enrichment, lineage capture, and runtime summary logging.

The template supports many sources and many targets. Source and target registrations contain DataFrame references and guardrail presets rather than loader metadata. Source and target guardrail flows are symmetrical: schema checks, source stability checks, and approved active DQ rules from `METADATA_DQ_RULES` run per dataset using that dataset's configured preset.

See [Pipeline Guardrails](schema-and-data-drift.md) for the source/target guardrail flow and supported schema, source stability, and DQ settings.

Runtime evidence is stored in metadata. Profiles and DQ summaries are written to `METADATA_DATA_CATALOGUE`, many-to-many lineage is written to `METADATA_DATA_LINEAGE_TABLE`, and run summaries are written to `METADATA_PIPELINE_RUNS`.

**Result:** repeatable transformations, output tables, catalogue evidence, lineage, runtime evidence, schema guardrails, stability guardrails, and DQ guardrails are produced without exposing implementation-heavy code in the notebook.

### `03_governance`

Run after `02_pipeline` has created evidence for review.

Use it to review and commit business context, DQ rules, sensitivity labels, PII classifications, and column classifications.

It stores reviewed metadata. Enforcement happens only when a later `02_pipeline` run loads the approved rules.

**Result:** reviewed governance metadata is committed table by table.

### Enforce approved governance rules

After `03_governance`, engineering reruns or updates `02_pipeline`.

The pipeline fetches approved rules from:

* `METADATA_DQ_RULES`
* `METADATA_COLUMN_CLASSIFICATION`

**Result:** approved DQ rules and column classifications are enforced during the pipeline run.

### Production handover

After the production pipeline is approved and stable, store the approved production notebook for handover.

**Result:** the production implementation and supporting metadata remain available for support and future enhancement.

## Ownership summary

| Area                                                    | Owner                     | Notebook or action                 |
| ------------------------------------------------------- | ------------------------- | ---------------------------------- |
| Environment paths and metadata setup                    | Engineering               | `00_env_config`                    |
| Agreement and steward metadata                          | Governance                | `01_agreement`                     |
| Optional discovery and profiling                        | Analyst or data scientist | `99_explore`                       |
| Transformation and output delivery                      | Engineering               | `02_pipeline`                      |
| Catalogue, lineage, profile, schema, and stability evidence | Engineering               | `02_pipeline`                      |
| Reviewed governance metadata                            | Governance                | `03_governance`                        |
| Approved rule enforcement                               | Engineering               | `02_pipeline` after `03_governance`    |
| Production handover                                     | Engineering               | Store approved production notebook |

## Next step

Continue to [Metadata Tables](metadata-tables.md) for a lightweight map of the metadata used by the notebook workflow.
