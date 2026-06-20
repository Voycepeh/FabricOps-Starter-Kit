# Template Notebooks

Template Notebooks is the canonical scan-friendly guide for what each FabricOps notebook contains and what users normally configure. Use the [Guided Demo](../../guided-demo.md) for the run sequence, and use the [Function Reference](../../reference/index.md) for reusable functions and classes.

<p class="template-download-hero">
  <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks">Download all template notebooks from this GitHub folder</a>
</p>

<div class="template-card-grid" markdown="1">

<div class="template-card" markdown="1">

## [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb)

Centralizes environment, workspace, path, metadata routing, runtime validation, and audit settings so every later notebook uses the same configured targets.

[Implementation reference](../../api/reference/setup_notebook.md){ .md-button }

??? info "Details"
    **Purpose**

    Configure shared `CONFIG` and `ENV` values, metadata lakehouse routing, schemas, default table names, validation behavior, and audit context.

    **When to use it**

    Run it first in every workspace setup, demo, or delivery flow. Revisit it when workspace item names, schemas, metadata targets, validation behavior, or audit values change.

    **What users normally edit**

    Environment name, workspace and Fabric item names, source/unified/metadata/warehouse routes, schema names, default workflow table names, runtime validation flags, and audit values.

    **What it validates or produces**

    It validates required environment keys and configured paths, routes `METADATA_*` tables through the configured metadata lakehouse, and creates or validates required metadata tables.

    **Downstream dependencies**

    `01_agreement`, `02_pipeline`, `03_governance`, and `99_explore` depend on its routes and runtime context.

</div>

<div class="template-card" markdown="1">

## [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb)

Captures business agreement, ownership, purpose, readiness, and supporting evidence before engineering execution begins.

[Agreement setup guide](agreement-setup.md){ .md-button }

??? info "Details"
    **Purpose**

    Record steward details, agreement scope, business purpose, readiness notes, approvals, and public-safe evidence.

    **When to use it**

    Use it when a governed delivery needs approved context before pipeline work starts.

    **What users normally edit**

    Steward and owner details, agreement name, scope, status, purpose, evidence labels, notes, links, and readiness context.

    **What it validates or produces**

    It validates required agreement and steward fields, then writes steward, agreement, and agreement evidence metadata to the configured metadata target.

    **Downstream dependencies**

    `02_pipeline`, `03_governance`, and `99_explore` use agreement context to connect technical evidence to ownership and purpose.

</div>

<div class="template-card" markdown="1">

## [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)

Provides the engineering notebook for data loading, transformation, validation, publishing, lineage, and run evidence.

[Pipeline execution guide](pipeline-execution.md){ .md-button }

??? info "Details"
    **Purpose**

    Run source-to-target processing under an agreement, profile data, evaluate guardrails, write outputs, and capture lineage and run summaries.

    **When to use it**

    Run it after `00_env_config` and `01_agreement` when source-to-target processing is ready to execute.

    **What users normally edit**

    Source table names, target table names, read and write settings, transformation logic, run labels, operational notes, and exposed validation choices.

    **What it validates or produces**

    It validates agreement context, source reads, schema, freshness, profile, DQ, and load behavior; it produces catalogue evidence, guardrail results, lineage, run summaries, and governed outputs.

    **Downstream dependencies**

    `03_governance` reviews observed metadata and proposed guardrails from pipeline runs. Later pipeline runs enforce active approved rules.

</div>

<div class="template-card" markdown="1">

## [`03_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_governance.ipynb)

Supports metadata enrichment review, guardrail review, lifecycle decisions, and promotion-readiness assessment.

[Governance review guide](governance-review.md){ .md-button }

??? info "Details"
    **Purpose**

    Review observed metadata, complete business metadata, approve or update guardrails, and record lifecycle decisions.

    **When to use it**

    Use it after pipeline evidence exists, or when reviewers need to approve, reject, replace, deactivate, or update enrichment and guardrail intent.

    **What users normally edit**

    Review notes, lifecycle decisions, business descriptions, classifications, stewardship context, and guardrail fields exposed by widgets.

    **What it validates or produces**

    It validates reviewed records and required review fields, then writes enrichment lifecycle records and approved, rejected, replaced, or inactive guardrail intent.

    **Downstream dependencies**

    Future `02_pipeline` runs use active guardrail intent from governance metadata.

</div>

<div class="template-card" markdown="1">

## [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb)

Provides optional read-only inspection and troubleshooting helpers for metadata, data context, or helper behavior.

[Metadata dashboard guide](metadata-dashboard.md){ .md-button }

??? info "Details"
    **Purpose**

    Inspect metadata or data context without changing governed workflow state.

    **When to use it**

    Use it before or after the governed flow for discovery, scratch profiling, troubleshooting, or support investigation.

    **What users normally edit**

    The table or agreement context to inspect, scratch analysis cells, and temporary display logic.

    **What it validates or produces**

    It does not validate production workflow state and creates no required metadata. Outputs are ad hoc notebook displays unless users save separate scratch artifacts.

    **Downstream dependencies**

    No production notebook depends on `99_explore`; treat it as an inspection helper.

</div>

</div>

## Optional example notebooks

The example notebooks support demos, training, and smoke tests. They are optional and are not part of the required production delivery sequence.

<div class="template-card-grid" markdown="1">

<div class="template-card" markdown="1">

## [`example_pipeline_demo`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_pipeline_demo.ipynb)

Generates deterministic demo source tables for the guided demo.

[Guided demo](../../guided-demo.md){ .md-button }

??? info "Details"
    **Purpose**

    Create repeatable demo source scenarios and demo-scoped DQ rules.

    **When to use it**

    Use it only for demos, training, and local validation of the starter workflow. It is not a production delivery notebook.

    **What users normally edit**

    Demo schema, table prefix, and scenario choices exposed by the notebook.

    **What it validates or produces**

    It helps validate that the demo can produce repeatable source inputs for `02_pipeline` and creates demo source tables in the configured source lakehouse.

    **Downstream dependencies**

    The guided demo version of `02_pipeline` reads the generated demo source tables.

</div>

<div class="template-card" markdown="1">

## [`example_dq`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_dq_rule_smoke_test.ipynb)

Demonstrates DQ rule evaluation, warning behavior, and blocking behavior in a smoke-test context.

[DQ rule reference](../../reference/dq-rules/index.md){ .md-button }

??? info "Details"
    **Purpose**

    Validate DQ rule helper behavior with controlled smoke-test examples.

    **When to use it**

    Use it when learning supported DQ rule outcomes or validating helper behavior. It is not a production delivery notebook.

    **What users normally edit**

    Smoke-test rule examples and toy input values.

    **What it validates or produces**

    It validates supported DQ rule behavior in a controlled context and does not define production workflow evidence.

    **Downstream dependencies**

    No production notebook depends on this smoke test. Use the DQ rule reference for rule syntax and supported behavior.

</div>

</div>
