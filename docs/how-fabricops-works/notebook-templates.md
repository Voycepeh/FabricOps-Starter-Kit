# Template Notebooks

The notebook templates are the FabricOps operating model. Each template owns a clear part of the handshake and passes evidence to the next notebook through metadata tables.

| Template | Purpose | What you do there | Metadata or evidence created | What the next notebook receives |
| --- | --- | --- | --- | --- |
| [`00_env_config`](environment-config.md) | Bootstrap the Fabric runtime and metadata target. | Set environment, workspace, item, schema, governance, and runtime values; create or validate metadata tables. | Metadata table structures and runtime context. | A `CONFIG` object, `ENV`, and ready metadata target for all notebooks. |
| [`01_agreement`](agreement-setup.md) | Capture steward, agreement, and agreement evidence. | Register data stewards, define agreements, and record supporting evidence. | Agreement metadata rows and evidence rows. | Selectable contract context for `02_pipeline`. |
| [`02_pipeline`](pipeline-execution.md) | Execute the data movement with checks and evidence. | Select an agreement, read sources, configure tables, run guardrails, write targets, lineage, and run summary. | Catalogue/profile evidence, guardrail results, lineage, and pipeline run status. | Evidence and authored rules/enrichment for governance review. |
| [`03_governance`](governance-review.md) | Govern rules and enrichment records formally. | Select a table target, author/review rules and enrichment, approve, reject, replace, deactivate, or inspect history. | Append-only rule/enrichment lifecycle rows. | Active governed rules for future pipeline runs and review state for dashboard visibility. |

The templates intentionally call public helpers rather than hiding workflow behavior in large custom cells. Function links are embedded in the implementation guide page for each notebook, including [setup_notebook](../api/reference/setup_notebook/), [prepare_pipeline_table_configs](../api/reference/prepare_pipeline_table_configs/), and [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/).


## Optional example notebooks

These notebooks are release-specific validation aids. They stay aligned to the notebook handshake. They are not production workflow templates. Use them when you need discovery support, demo data, or focused smoke checks before adapting the core templates.

| Notebook | Purpose | Relevant helpers |
| --- | --- | --- |
| `99_explore.ipynb` | Optional discovery, profiling, troubleshooting, investigation, and ad hoc analysis support. | [`read_data`](../api/reference/read_data/), [`profile_dataframe`](../api/reference/profile_dataframe/) |
| `example_pipeline_demo.ipynb` | Generates deterministic `demo_` source scenario tables for the real `02_pipeline` template to demonstrate happy path, schema, DQ, freshness, and load-behaviour guardrails. | [`write_data`](../api/reference/write_data/) |
| `example_dq_rule_smoke_test.ipynb` | Demonstrates DQ rule evaluation, warning behavior, and error blocking behavior using smoke-test data and rules. | [`write_data`](../api/reference/write_data/), [`enforce_dq_rules`](../api/reference/enforce_dq_rules/) |
