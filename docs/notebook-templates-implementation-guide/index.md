# Templates

FabricOps Starter Kit provides editable Microsoft Fabric notebook templates for governed, quality-checked notebook workflows. Use this page as the notebook download and implementation handoff: download the notebooks, scan their responsibilities, then follow the [Guided Demo](../guided-demo.md) for the maintained execution instructions. Read [How FabricOps Works](../how-fabricops-works.md) for the architecture and operating model.

## Tested release records

Notebook templates are maintained as a living track independently from FabricOps package releases. The compatibility table near the top of each maintained template is a manual Microsoft Fabric test record: add a package release only after that template has actually been run and verified with the release in Microsoft Fabric. Keep the stable template filenames current instead of duplicating or freezing a separate notebook copy for every package release.

<p class="template-download-hero">
  <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks">Download all template notebooks from this GitHub folder</a>
</p>

## FabricOps operating workflow

The required workflow uses only the three core FabricOps workspaces: Governance, Engineering Development, and Engineering Production. The same notebook may appear at multiple workflow stages; for example, "02_pipeline" is used in Development first to capture evidence and later to wire in approved guardrails before promotion to Production.

| Step | Stage | Workspace | Template | Purpose |
| ---- | ----- | --------- | -------- | ------- |
| 0 | Set up the operating environment | Governance, Engineering Development, and Engineering Production | `00_env_config` | Create the Fabric workspaces, create the required lakehouses and warehouses, configure `00_env_config` in every workspace, and create the metadata tables in Governance. |
| 1 | Governance workflow 1 | Governance | `01_agreement` | Create data stewards and create a data agreement between data stewards. |
| 2 | Engineering workflow 1 | Engineering Development | `02_pipeline` | Extract, transform, and load data from one data store to another; profile source and target tables; and write data catalogue, data profiled, and data lineage metadata. |
| 3 | Governance workflow 2 | Governance | `03_review` | Pick from the data catalogue table, add descriptions and classifications to selected tables, and define guardrails such as schema enforcement and data quality. |
| 4 | Engineering workflow 2 | Engineering Development | `02_pipeline` | Wire in the guardrail rules defined during review, run the pipeline, and make sure it fails or warns users as configured. |
| 5 | Governance workflow 3 | Governance | `01_agreement` | Pick from the data catalogue table, create a data contract linking the data tables to the data agreement, and get the data steward to sign off on the contract. |
| 6 | Engineering workflow 3 | Engineering Production | Promoted `02_pipeline` | Promote the `02_pipeline` that was completed in Engineering Development. |

## Guided Demo support notebooks

These notebooks support demos, training, and smoke testing. They are not part of the required production workflow.

| Notebook | Purpose |
| -------- | ------- |
| `example_pipeline_demo` | Generates deterministic demo source data and demo-scoped rule intent for the Guided Demo pipeline run. |
| `example_dq_rule_smoke_test` | Demonstrates supported DQ rule outcomes in a smoke-test context for users learning rule behavior. |

<div class="template-card-grid" markdown="1">

<div class="template-card" markdown="1">

## [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb)

Centralizes workspace, storage, metadata routing, runtime validation, widget, audit, and package settings so downstream templates use consistent environment-specific configuration.

[Open Guided Demo step](../guided-demo/run-environment-setup.md){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb)

Creates data stewards and establishes the initial data agreement before development begins. After validation and review, it creates the data contract that provides approval for promotion to Production; it does not automatically deploy the notebook.

[Open Guided Demo step](../guided-demo/create-agreement.md){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)

Provides the reusable PySpark pipeline template for Development validation and promoted Production execution. It ingests, transforms, and writes data; profiles data; registers catalogue and lineage evidence; evaluates and records guardrail results; and consumes approved enrichment and guardrails.

[Open Guided Demo step](../guided-demo/run-pipeline.md#run-02_pipeline){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`03_review`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_review.ipynb)

Allows governance users to review the catalogue and evidence captured by "02_pipeline", add business descriptions and classifications, define or review guardrails, and assess whether the pipeline is ready for validation and approval.

[Open Guided Demo step](../guided-demo/review-guardrails.md){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb)

Provides an optional notebook for one-off analysis in Engineering Development: exploring datasets, testing assumptions, investigating data quality, developing transformation logic, producing one-off analytical outputs, and deciding whether work should become a repeatable "02_pipeline". It should not change governed workflow state through agreement, contract, enrichment, or guardrail writes. Important or reusable work should either move into "02_pipeline" or be preserved for reproducibility.

[Open Guided Demo step](../guided-demo/explore-metadata-outputs.md){ .md-button }

</div>

</div>

## Optional example notebooks

These notebooks support demos, training, and smoke tests. They are not part of the required production workflow sequence.

<div class="template-card-grid" markdown="1">

<div class="template-card" markdown="1">

## [`example_pipeline_demo`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_pipeline_demo.ipynb)

Generates deterministic demo source tables and demo-scoped rule intent for the Guided Demo pipeline run.

[Open Guided Demo step](../guided-demo/run-pipeline.md#seed-demo-source-data-with-example_pipeline_demo){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`example_dq_rule_smoke_test`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_dq_rule_smoke_test.ipynb)

Demonstrates supported DQ rule outcomes in a smoke-test context for users learning rule behavior outside the production sequence. It is not a production delivery notebook.

[Open DQ rule reference](../reference/dq-rules/index.md){ .md-button }

</div>

</div>
