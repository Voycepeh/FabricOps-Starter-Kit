# Notebook Templates

FabricOps Starter Kit uses a small set of notebook templates so teams can move from agreement to pipeline to review without inventing a new process for every data product.

The templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

```text
templates/notebooks/
```

## Template overview

| Template | Primary user | Purpose | Typical result |
| --- | --- | --- | --- |
| `00_env_config` | Platform or engineering lead | Configure Fabric paths, runtime defaults, and metadata tables for an environment. | Other notebooks know where to read, write, and store metadata. |
| `01_agreement` | Data steward or product owner | Capture the agreed purpose, owner, steward, and supporting agreement evidence. | A clear agreement exists before build work is treated as production-ready. |
| `02_pipeline` | Data engineer | Build the data product, run guardrails, write outputs, and record metadata evidence. | A repeatable pipeline produces data and evidence for review. |
| `03_review` | Governance reviewer or data steward | Review catalogue evidence and approve business context, DQ expectations, sensitivity, and classification. | Reviewed metadata is available for support and later pipeline use when engineers wire it in. |
| `99_explore` | Analyst or engineer | Optional discovery, profiling, troubleshooting, or ad hoc investigation. | Findings can inform agreement, pipeline, or review work, but this is not a required step. |

## Role-based notebook flow

![Role-based notebook workflow from environment configuration through governance review](../assets/fabricops-role-workflow.png){ .full-width }

| Stage | Who usually runs it | What to check before moving on |
| --- | --- | --- |
| Configure | Platform or engineering lead | `00_env_config` points to the correct Fabric items and `metadata_lakehouse`. |
| Agree | Steward or product owner | `01_agreement` captures the purpose, owner, steward, and useful evidence. |
| Build | Engineer | `02_pipeline` reads the agreement, writes the output, and records metadata evidence. |
| Review | Reviewer or steward | `03_review` uses pipeline evidence to save reviewed metadata. |
| Support | Any approved user | `99_explore` may help investigate questions, but it does not replace the core workflow. |

## What each template is for

### `00_env_config`

Run `00_env_config` first in each environment.

It defines:

- workspace and Fabric item paths;
- source, unified, warehouse, and metadata targets;
- the `metadata_lakehouse` used by the workflow;
- default settings used by downstream notebooks;
- the active metadata table schemas.

On first run, it creates the metadata tables if needed. On later runs, it validates that the expected schemas are still present. Most users do not need to manually maintain metadata schemas.

### `01_agreement`

Run `01_agreement` when a team needs to capture what is being requested and who owns it.

Use it to record:

- the agreed business purpose;
- data steward and owner details;
- readiness or support expectations;
- links or file references for supporting agreement evidence.

`01_agreement` is intentionally about agreement. It does not approve column classifications, save reviewed DQ expectations, or enforce production checks.

### `02_pipeline`

Run `02_pipeline` when engineering is ready to build or run the data product.

Use it to:

- load `00_env_config`;
- link the pipeline to the relevant agreement;
- read configured sources;
- transform data;
- run guardrails for schema, data changes, and any implemented approved rules;
- write outputs;
- record metadata evidence such as profiles, lineage, and run context.

`02_pipeline` owns enforcement. If a check should block or warn during a run, it belongs in the pipeline notebook.

### `03_review`

Run `03_review` after `02_pipeline` has created catalogue and profile evidence.

Use it to review and save:

- plain-language business context;
- reviewed DQ expectations;
- sensitivity notes;
- column classification.

`03_review` stores reviewed metadata. It does not enforce anything by itself. A later `02_pipeline` run can use approved reviewed metadata only when the engineer has implemented that behavior in the pipeline.

### `99_explore`

Use `99_explore` only when extra discovery or troubleshooting is helpful.

Common uses include:

- exploring an unfamiliar source;
- checking sample data before an agreement is finalized;
- investigating a failed pipeline run;
- supporting a governance review question.

`99_explore` is optional support. It is not required before `01_agreement`, `02_pipeline`, or `03_review`.

## Ownership summary

| Area | Owner notebook | Notes |
| --- | --- | --- |
| Paths and metadata table setup | `00_env_config` | Keeps environment routing explicit and repeatable. |
| Agreement and steward metadata | `01_agreement` | Captures the agreed purpose and owner. |
| Output data and blocking behavior | `02_pipeline` | The pipeline decides when to warn, stop, or write. |
| Metadata evidence | `02_pipeline` | Profiles, lineage, and run context support review and operations. |
| Reviewed metadata | `03_review` | Human-approved context, DQ expectations, sensitivity, and classification. |
| Optional investigation | `99_explore` | Helps answer questions without becoming a required delivery step. |

## Next step

Continue to [Metadata Tables](metadata-tables.md) for a lightweight map of the metadata used by the notebook workflow.
