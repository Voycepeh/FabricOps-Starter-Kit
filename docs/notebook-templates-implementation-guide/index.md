# Templates

FabricOps Starter Kit provides editable Microsoft Fabric notebook templates for governed, quality-checked notebook workflows. Use this page as the lightweight template landing page: download the notebooks, scan the run order, then follow the Guided Demo for the maintained step-by-step instructions.

## Tested release records

Notebook templates are maintained as a living track independently from FabricOps package releases. The compatibility table near the top of each maintained template is a manual Microsoft Fabric test record: add a package release only after that template has actually been run and verified with the release in Microsoft Fabric. Keep the stable template filenames current instead of duplicating or freezing a separate notebook copy for every package release.

<p class="template-download-hero">
  <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks">Download all template notebooks from this GitHub folder</a>
</p>

## Notebook sequence

| Order | Notebook | Guided Demo destination |
| ----- | -------- | ----------------------- |
| 1 | `00_env_config` | [Run Environment Setup](../guided-demo/run-environment-setup.md) |
| 2 | `01_agreement` | [Create Agreement](../guided-demo/create-agreement.md) |
| 3 | `example_pipeline_demo` | [Run Pipeline](../guided-demo/run-pipeline.md#seed-demo-source-data-with-example_pipeline_demo) |
| 4 | `02_pipeline` | [Run Pipeline](../guided-demo/run-pipeline.md#run-02_pipeline) |
| 5 | `03_review` | [Review Guardrails](../guided-demo/review-guardrails.md) |
| Optional | `99_explore` | [Explore Metadata Outputs](../guided-demo/explore-metadata-outputs.md) |

<div class="template-card-grid" markdown="1">

<div class="template-card" markdown="1">

## [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb)

Centralizes environment, workspace, path, metadata routing, runtime validation, widget configuration, and audit settings so every later notebook uses the same configured targets.

[Open Guided Demo step](../guided-demo/run-environment-setup.md){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb)

Captures steward, agreement, business purpose, readiness, and supporting evidence before pipeline execution begins.

[Open Guided Demo step](../guided-demo/create-agreement.md){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)

Runs source-to-target processing under an agreement, profiles data, evaluates guardrails, writes governed outputs, and records lineage and run evidence.

[Open Guided Demo step](../guided-demo/run-pipeline.md#run-02_pipeline){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`03_review`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_review.ipynb)

Supports enrichment review, guardrail review, lifecycle decisions, and promotion-readiness assessment based on observed metadata and runtime evidence.

[Open Guided Demo step](../guided-demo/review-guardrails.md){ .md-button }

</div>

<div class="template-card" markdown="1">

## [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb)

Provides optional read-only inspection and troubleshooting for metadata, configured data targets, and helper behavior without changing governed workflow state.

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

## [`example_dq`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_dq_rule_smoke_test.ipynb)

Demonstrates supported DQ rule outcomes in a smoke-test context for users learning rule behavior outside the production sequence. It is not a production delivery notebook.

[Open DQ rule reference](../reference/dq-rules/index.md){ .md-button }

</div>

</div>
