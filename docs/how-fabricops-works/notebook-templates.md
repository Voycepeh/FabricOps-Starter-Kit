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
| 3 | `99_explore` | Analyst or engineering | Optionally inspect and profile <span class="glossary-term" title="Data read from configured upstream Lakehouse or Warehouse targets before transformation.">source data</span> before production delivery. |
| 4 | `02_pipeline` | Engineering | Build the data product, write outputs, and record profile, lineage, DQ, and run evidence. |
| 5 | `03_governance` | Governance | Select profiled data, <span class="glossary-term" title="Add reviewed descriptive metadata such as meaning, ownership, classification, sensitivity, and usage context.">enrich metadata</span>, and review guardrail state, approvals, rejections, replacements, deactivations, and active-pending-review decisions. |
| 6 | `02_pipeline` | Engineering | Rerun the pipeline so active guardrail rules are enforced during delivery. |

For detailed behavior, continue to [Pipeline Guardrails](pipeline-guardrails.md), [Governance Review](governance-review.md), and [Metadata Tables](metadata-tables.md).

## Callable references by workflow step

Use these generated API references when you want implementation details for the helper functions used by each notebook step:

- `00_env_config`: central environment, target, and Lakehouse schema settings; [setup_notebook](../api/reference/setup_notebook/); plus an optional commented [setup_metadata_tables](../api/reference/setup_metadata_tables/) block. Uncomment and run metadata setup once per environment, then comment it back so downstream `%run 00_env_config` stays fast.
- `01_agreement`: [widget_render_data_steward](../api/reference/widget_render_data_steward/), [widget_render_data_agreement](../api/reference/widget_render_data_agreement/), and [widget_render_agreement_evidence](../api/reference/widget_render_agreement_evidence/).
- `02_pipeline`: starts by selecting an approved agreement with [widget_select_agreement](../api/reference/widget_select_agreement/) and reading it with [get_selected_agreement](../api/reference/get_selected_agreement/) so the active notebook can be registered before pipeline evidence is written. It then uses [prepare_pipeline_table_configs](../api/reference/prepare_pipeline_table_configs/), [run_table_guardrails](../api/reference/run_table_guardrails/), [profile_dataframe](../api/reference/profile_dataframe/), [write_pipeline_lineage](../api/reference/write_pipeline_lineage/), and [write_pipeline_run_summary](../api/reference/write_pipeline_run_summary/).
- `03_governance`: [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/), [widget_enrich_table_metadata](../api/reference/widget_enrich_table_metadata/), and [widget_review_table_governance](../api/reference/widget_review_table_governance/). Governance reviewers use the current profile-based target selection, enrichment, and guardrail review flow. The old separated business context/classification widgets are removed from the current template flow; DQ belongs with guardrail authoring/review, not enrichment.

## Template notebooks

<div class="template-card-list" markdown>

<div markdown class="card">

### `00_env_config`

**Objective**

Set up the Fabric environment so the downstream notebooks can run consistently.

**Used by**

Engineering or platform setup owner.

**Key function**

Defines workspace paths, Fabric item targets, lakehouse and warehouse locations, <span class="glossary-term" title="Configured metadata target where FabricOps stores workflow metadata.">metadata lakehouse</span> settings, notebook defaults, and reusable widgets. On first run, it creates the metadata tables. On later runs, it validates that the expected metadata schemas are still available.

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

Reads source data, registers source and pipeline outputs, applies schema checks, applies freshness and profile behavior checks, runs active governance-approved DQ rules, writes configured outputs, and records runtime evidence. It also writes profile, lineage, DQ, and pipeline run metadata so governance can review what was produced.

**Output**

The data product tables are created or refreshed, and the supporting metadata evidence is written for governance review and future enforcement.

**Template**

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)

</div>

<div markdown class="card">

### `03_governance`

**Objective**

Select profiled tables from `METADATA_DATA_CATALOGUE`, enrich metadata, and review guardrail decisions.

**Used by**

Governance, data stewards, or reviewers.

**Key function**

Uses `widget_select_guardrail_target`, `widget_enrich_table_metadata`, `widget_author_guardrail_rules`, and `widget_review_table_governance` to select catalogue-backed targets, save column context/classification enrichment, and review table governance state, approvals, rejections, replacements, deactivations, and active-pending-review decisions. It stores enrichment and governance decisions, but does not enforce rules. Enforcement happens when `02_pipeline` runs again using active guardrail rules, including active pending governance review records where applicable.

**Output**

Reviewed enrichment and governance metadata is committed table by table and becomes available for reporting, handover, review, and later pipeline enforcement where relevant.

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
| `example_pipeline_demo.ipynb` | Generates deterministic `demo_` source scenario tables for the real `02_pipeline` template to demonstrate happy path, schema, DQ, freshness, and load-behaviour guardrails. |
| `example_dq_rule_smoke_test.ipynb` | Demonstrates DQ rule evaluation, warning behavior, and error blocking behavior using smoke-test data and rules. |

Agreement selection is separate from guardrail target selection. The agreement selector anchors pipeline evidence to approved agreement metadata and notebook registry linkage; guardrail target selection uses `METADATA_DATA_CATALOGUE` profiles after profiling.
