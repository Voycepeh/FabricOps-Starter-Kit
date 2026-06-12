# Notebook Templates

FabricOps Starter Kit uses a small set of notebook templates to move a data product from setup, agreement, exploration, pipeline delivery, and governance review.

Each template has a clear owner and purpose. The notebooks are meant to stay lightweight in Fabric, while the helper wheel handles the repeated setup, metadata, profiling, lineage, and governance evidence work.

## The templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

These links open the current development templates. Released documentation should link to the matching released templates.

![Role-based notebook workflow from environment configuration through governance review](../assets/fabricops-role-workflow.png){ .full-width }

## How the templates work together

| Step | Notebook | Main owner | What happens |
| ---- | -------- | ---------- | ------------ |
| 1 | `00_env_config` | Engineering | Configure paths, Fabric targets, metadata tables, and reusable widgets. |
| 2 | `01_agreement` | Governance | Capture the request, ownership, steward details, and agreement evidence. |
| 3 | `99_explore` | Analyst or engineering | Optionally inspect and profile source data before production delivery. |
| 4 | `02_pipeline` | Engineering | Build the data product, write outputs, and record catalogue, lineage, DQ, and run evidence. |
| 5 | `03_governance` | Governance | Review and approve metadata, classifications, sensitivity labels, and DQ rules. |
| 6 | `02_pipeline` | Engineering | Rerun the pipeline so approved rules are enforced during delivery. |

For detailed behavior, continue to [Pipeline Guardrails](pipeline-guardrails.md), [Governance Review](governance-review.md), and [Metadata Tables](metadata-tables.md).

## Callable references by workflow step

Use these generated API references when you want implementation details for the helper functions used by each notebook step:

- `00_env_config`: [setup_notebook](../api/reference/setup_notebook/) and [setup_metadata_tables](../api/reference/setup_metadata_tables/).
- `01_agreement`: [widget_render_data_steward](../api/reference/widget_render_data_steward/), [widget_render_data_agreement](../api/reference/widget_render_data_agreement/), [widget_render_agreement_evidence](../api/reference/widget_render_agreement_evidence/), [widget_select_agreement](../api/reference/widget_select_agreement/), and [get_selected_agreement](../api/reference/get_selected_agreement/).
- `02_pipeline`: [prepare_pipeline_table_configs](../api/reference/prepare_pipeline_table_configs/), [run_table_guardrails](../api/reference/run_table_guardrails/), [profile_dataframe](../api/reference/profile_dataframe/), [build_lineage_records](../api/reference/build_lineage_records/), [write_pipeline_lineage](../api/reference/write_pipeline_lineage/), and [write_pipeline_run_summary](../api/reference/write_pipeline_run_summary/).
- `03_governance`: [widget_select_catalogue_table](../api/reference/widget_select_catalogue_table/), [load_catalogue_profile_rows](../api/reference/load_catalogue_profile_rows/), [widget_review_dq_rules](../api/reference/widget_review_dq_rules/), and [record_table_governance](../api/reference/record_table_governance/).

## Template notebooks

<div class="template-card-list" markdown>

<div markdown class="card">

### `00_env_config`

**Objective**

Set up the Fabric environment so the downstream notebooks can run consistently.

**Used by**

Engineering or platform setup owner.

**Key function**

Defines workspace paths, Fabric item targets, lakehouse and warehouse locations, metadata lakehouse settings, notebook defaults, and reusable widgets. On first run, it creates the metadata tables. On later runs, it validates that the expected metadata schemas are still available.

**Output**

The environment is ready for `01_agreement`, `02_pipeline`, `03_governance`, and optional `99_explore`.

**Template**

[Open `00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb)

</div>

<div markdown class="card">

### `01_agreement`

**Objective**

Capture the business agreement before engineering starts building the data product.

**Used by**

Governance, data stewards, or the team coordinating the request.

**Key function**

Records the agreement name, business purpose, steward and owner details, support expectations, and supporting evidence. It establishes the governed request, but does not approve classifications, save reviewed DQ rules, or enforce production checks.

**Output**

Agreement, steward, and agreement evidence records are stored in the metadata lakehouse.

**Template**

[Open `01_agreement.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb)

</div>

<div markdown class="card">


### `02_pipeline`

**Objective**

Build and run the governed data product pipeline.

**Used by**

Engineering.

**Key function**

Reads source data, registers source and target DataFrames, applies schema checks, applies freshness and profile behavior checks, runs approved active DQ rules, writes configured outputs, and records runtime evidence. It also writes catalogue, profile, lineage, DQ, and pipeline run metadata so governance can review what was produced.

**Output**

The data product tables are created or refreshed, and the supporting metadata evidence is written for governance review and future enforcement.

**Template**

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)

</div>

<div markdown class="card">

### `03_governance`

**Objective**

Review and approve the governance evidence produced by the pipeline.

**Used by**

Governance, data stewards, or reviewers.

**Key function**

Reviews and commits business context, sensitivity labels, PII classifications, column classifications, and DQ rules. It stores reviewed metadata, but does not itself enforce the rules. Enforcement happens when `02_pipeline` runs again using the approved metadata.

**Output**

Reviewed governance metadata is committed table by table and becomes available for later pipeline enforcement.

**Template**

[Open `03_governance.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_governance.ipynb)

</div>

### `99_explore`

**Objective**

Explore source data before or during delivery when discovery is needed.

**Used by**

Analysts, data scientists, or engineers.

**Key function**

Supports source inspection, profiling, early schema understanding, pre-agreement checks, troubleshooting, and review questions. It can be linked to one or more agreements when the exploration produces useful evidence.

**Output**

Source data is explored and profiled without turning the exploration notebook into the production pipeline.

**Template**

[Open `99_explore.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb)

</div>

<div markdown class="card">

</div>

## Optional example notebooks

These notebooks are release-specific validation aids. They are stored beside the templates with an `example_` prefix so users can quickly test or understand specific flows before adapting the production templates. They are not production workflow templates.

| Notebook | Purpose |
| --- | --- |
| `example_pipeline_smoke_test.ipynb` | Validates the pipeline path: source and target guardrails, catalogue evidence, lineage, runtime summary, and a smoke target write. |
| `example_dq_rule_smoke_test.ipynb` | Demonstrates DQ rule evaluation, warning behavior, and error blocking behavior using smoke-test data and rules. |
