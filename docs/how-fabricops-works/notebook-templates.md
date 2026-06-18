# Template Notebooks

The notebook templates are the FabricOps operating model. Each template owns a clear part of the handshake and passes evidence to the next notebook through metadata tables.

| Template | Purpose | What you do there | Metadata or evidence created | What the next notebook receives |
| --- | --- | --- | --- | --- |
| [`00_env_config`](environment-config.md) | Bootstrap the Fabric runtime and metadata target. | Set environment, workspace, item, schema, governance, and runtime values; create or validate metadata tables. | Metadata table structures and runtime context. | A `CONFIG` object, `ENV`, and ready metadata target for all notebooks. |
| [`01_agreement`](agreement-setup.md) | Capture steward, agreement, and agreement evidence. | Register data stewards, define agreements, and record supporting evidence. | Agreement metadata rows and evidence rows. | Selectable contract context for `02_pipeline`. |
| [`02_pipeline`](pipeline-execution.md) | Execute the data movement with checks and evidence. | Select an agreement, read sources, configure tables, run guardrails, write targets, lineage, and run summary. | Catalogue/profile evidence, guardrail results, lineage, and pipeline run status. | Evidence and authored rules/enrichment for governance review. |
| [`03_governance`](governance-review.md) | Govern rules and enrichment records formally. | Select a table target, author/review rules and enrichment, approve, reject, replace, deactivate, or inspect history. | Append-only rule/enrichment lifecycle rows. | Active governed rules for future pipeline runs and review state for dashboard visibility. |


## Open the actual starter notebooks

Use this page as a launch point, not only a concept map. The template notebooks live in the repository and should be copied/customized from these source files:

| Notebook file | Guide page | When to open it |
| --- | --- | --- |
| [`templates/notebooks/00_env_config.ipynb`](../../templates/notebooks/00_env_config.ipynb) | [00 Environment Configuration](environment-config.md) | First. Configure runtime paths, metadata routing, schemas, governance settings, and table setup. |
| [`templates/notebooks/01_agreement.ipynb`](../../templates/notebooks/01_agreement.ipynb) | [01 Agreement Setup](agreement-setup.md) | After setup. Capture data steward, agreement, and supporting evidence records. |
| [`templates/notebooks/02_pipeline.ipynb`](../../templates/notebooks/02_pipeline.ipynb) | [02 Pipeline Execution](pipeline-execution.md) | Delivery notebook. Select agreement context, read data, run guardrails, write outputs, and publish evidence. |
| [`templates/notebooks/03_governance.ipynb`](../../templates/notebooks/03_governance.ipynb) | [03 Governance Review](governance-review.md) | Review notebook. Author and review enrichment and guardrail lifecycle records. |
| [`templates/notebooks/99_explore.ipynb`](../../templates/notebooks/99_explore.ipynb) | Optional | Discovery/troubleshooting notebook for profiling, investigation, and ad hoc exploration. |

## Optional example notebooks

These notebooks are release-specific validation aids. They stay aligned to the notebook handshake. They are not production workflow templates. Use them when you need discovery support, demo data, or focused smoke checks before adapting the core templates.

| Notebook | Purpose | Relevant helpers |
| --- | --- | --- |
| [`templates/notebooks/99_explore.ipynb`](../../templates/notebooks/99_explore.ipynb) | Optional discovery, profiling, troubleshooting, investigation, and ad hoc analysis support. | [`read_data`](../api/reference/read_data.md), [`profile_dataframe`](../api/reference/profile_dataframe.md) |
| [`templates/notebooks/example_pipeline_demo.ipynb`](../../templates/notebooks/example_pipeline_demo.ipynb) | Generates deterministic `demo_` source scenario tables for the real `02_pipeline` template to demonstrate happy path, schema, DQ, freshness, and load-behaviour guardrails. | [`write_data`](../api/reference/write_data.md) |
| [`templates/notebooks/example_dq_rule_smoke_test.ipynb`](../../templates/notebooks/example_dq_rule_smoke_test.ipynb) | Demonstrates DQ rule evaluation, warning behavior, and error blocking behavior using smoke-test data and rules. | [`write_data`](../api/reference/write_data.md), [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) |

![FabricOps workspace setup](../assets/fabric-example-workspace-setup.png)

## Sequencing guidance

1. Start with `00_env_config` and run metadata setup before any workflow notebook writes evidence.
2. Run `01_agreement` until at least one active agreement and steward can be selected.
3. Use `02_pipeline` for executable source-to-target movement. Keep transformations visible and beginner-editable.
4. Use `03_governance` for formal lifecycle decisions; do not treat pipeline runtime failures as governance approvals.
5. Use `99_explore` and examples for investigation, demos, and smoke tests, not as replacements for the governed template sequence.

The templates intentionally call public helpers rather than hiding workflow behavior in large custom cells. Function links are embedded in the implementation guide page for each notebook, including [setup_notebook](../api/reference/setup_notebook.md), [prepare_pipeline_table_configs](../api/reference/prepare_pipeline_table_configs.md), and [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target.md).
