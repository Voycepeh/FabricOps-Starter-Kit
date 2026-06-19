# FabricOps Guided Demo

<div class="demo-hero" markdown>

Use this page as a course-style walkthrough for the FabricOps Starter Kit in Microsoft Fabric. It now lives in the main navigation, and the primary flow is the end-to-end guided demo.

## Demo at a glance

This demo builds a governed, quality-checked Microsoft Fabric notebook workflow around deterministic order and customer source data. You will configure the environment, create agreement metadata, generate demo source tables, run the real pipeline template, review governance metadata, rerun the pipeline with active guardrails, and inspect the evidence that explains what happened.

It is for data engineers, analytics engineers, data stewards, governance reviewers, and junior team members who need a practical handover path through FabricOps. Plan for a focused half-day the first time if you are also setting up Fabric workspaces and wheel installation; the notebook flow itself is shorter once your Fabric workspace, lakehouses, warehouse, and Environment are ready.

By the end, you should understand how FabricOps uses Fabric workspaces, lakehouses, notebooks, and metadata tables to make delivery traceable from data agreement through governed pipeline review. For the full operating model, read [How FabricOps Works](how-fabricops-works/index.md).

</div>

<div class="demo-learning-outcomes" markdown>

## By the end of this demo, you will learn how to

- Configure `00_env_config` with environment-specific Fabric routes and metadata targets.
- Create steward, agreement, and evidence metadata in `01_agreement`.
- Generate deterministic demo source tables using `example_pipeline_demo.ipynb`.
- Run `02_pipeline` on demo source data.
- Profile source and target DataFrames.
- Write governed unified outputs.
- Author or review schema, freshness, profile, DQ, and enrichment metadata.
- Run `03_governance` for formal review.
- Rerun `02_pipeline` to enforce active guardrails.
- Inspect metadata evidence and final outputs.

</div>

<div class="demo-defaults" markdown>

## Demo defaults

Keep these defaults for your first pass so the screenshots, notebooks, and expected metadata evidence line up.

| Default | Value |
| ------- | ----- |
| Source schema | `DemoTest` |
| Generated source table prefix | `demo_` |
| Happy path source tables | `demo_src_orders_happy` and `demo_src_customers_happy` |
| Default unified outputs | `demo_unified_orders_enriched` and `demo_unified_orders_summary` |
| Demo generator behavior | `example_pipeline_demo.ipynb` is safe to rerun and overwrites demo tables only. |

</div>

<div class="demo-milestone-card" markdown>

## Milestone 0: Prepare Fabric workspace and wheel

**Objective:** Create the Fabric workspace items and install the FabricOps wheel so every demo notebook can import `fabricops_kit`.

**Open:** [Fabric Wheel Install](install.md), then your Microsoft Fabric workspace and Fabric Environment.

**Run or edit:**

1. Create one Governance workspace and one Engineering workspace. For a lightweight demo, you may use a single workspace if that is easier.
2. Create or identify these Fabric items:

    | Workspace | Required items | Purpose |
    | --------- | -------------- | ------- |
    | Governance workspace | `metadata_lakehouse` | Stores shared metadata, notebook registration, agreements, profiles, reviewed guardrail expectations, classifications, and lineage evidence. |
    | Engineering workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Hosts source demo tables, governed unified outputs, and warehouse outputs used by the notebook flow. |

3. Build or download the FabricOps wheel, upload it to a Microsoft Fabric Environment, and attach that Environment to the copied demo notebooks.
4. Copy notebook templates from the GitHub `templates` folder into Fabric: `00_env_config`, `01_agreement`, `02_pipeline`, `03_governance`, `example_pipeline_demo`, and `99_explore` if you want the bonus discovery notebook.

<div class="demo-expected-output" markdown>

**Expected output:** Fabric notebooks attached to the Environment can import `fabricops_kit`, and editable template copies exist in your Fabric workspace.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** No FabricOps metadata is required yet. This milestone prepares the runtime and workspace items that later milestones use.

</div>

**Install screenshots:**

![Fabric custom wheel install example](assets/fabric-example-install-custom-whl.png)

![Fabric workspace setup example](assets/fabric-example-workspace-setup.png)

![Fabric notebook Environment selection example](assets/fabric-example-set-notebook-environment.png)

!!! note "Screenshot to add"
    Capture: Fabric workspace showing copied demo notebooks: `00_env_config`, `01_agreement`, `example_pipeline_demo`, `02_pipeline`, `03_governance`, and `99_explore`.
    Suggested filename: `docs/assets/demo/demo-00-copied-notebooks.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 1](#milestone-1-configure-00_env_config). For template responsibilities, see [List of Templates](how-fabricops-works/notebook-templates.md).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 1: Configure `00_env_config`

**Objective:** Register environment routes so all metadata reads and writes use the configured metadata target instead of an attached/default lakehouse.

**Open:** `00_env_config` in Fabric and the [Environment Configuration](how-fabricops-works/environment-config.md) guide.

**Run or edit:**

1. Edit workspace, lakehouse, and warehouse URLs or item paths for your demo environment.
2. Keep or set `FABRICOPS_AUDIT_TIMEZONE` to a valid IANA timezone.
3. Run the notebook cells that build `CONFIG`, set `ENV`, and register metadata tables.
4. Confirm downstream notebooks can reuse the same `CONFIG` and `ENV` values.

<div class="demo-expected-output" markdown>

**Expected output:** `CONFIG`, `ENV`, metadata lakehouse routes, source lakehouse routes, unified lakehouse routes, warehouse routes, and audit timestamp settings are available to downstream notebooks.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Metadata table setup/registration is available in `metadata_lakehouse`, including the shared `METADATA_*` tables described in [List of Metadata Tables](reference/metadata-tables/index.md).

</div>

![`00_env_config` path configuration example](assets/fabric-example-00_config_paths.png)

!!! note "Screenshot to add"
    Capture: Successful `00_env_config` run showing the `CONFIG`/`ENV` summary and metadata target registration.
    Suggested filename: `docs/assets/demo/demo-01-env-config-summary.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 2](#milestone-2-create-agreement-in-01_agreement).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 2: Create agreement in `01_agreement`

**Objective:** Capture the steward, agreement, and initial evidence metadata that explains what the demo pipeline is meant to build and who owns it.

**Open:** `01_agreement` in Fabric and the [List of Templates](how-fabricops-works/notebook-templates.md) guide.

**Run or edit:**

1. Reuse the `CONFIG` and `ENV` from `00_env_config`.
2. Enter public-safe demo steward details.
3. Define the data agreement for the demo order/customer workflow.
4. Save or render the agreement evidence using the notebook widgets and helper cells.

<div class="demo-expected-output" markdown>

**Expected output:** The agreement notebook shows the selected steward/agreement context and renders agreement evidence that downstream notebooks can reference.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Steward, agreement, and agreement evidence rows are written to the configured metadata target. These rows become the governance context for `02_pipeline` and `03_governance`.

</div>

!!! note "Screenshot to add"
    Capture: `01_agreement` rendered steward, agreement, and evidence widgets for the demo order/customer workflow.
    Suggested filename: `docs/assets/demo/demo-02-agreement-widgets.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 3](#milestone-3-generate-demo-data-with-example_pipeline_demo).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 3: Generate demo data with `example_pipeline_demo`

**Objective:** Create deterministic `demo_` source scenario tables in the configured source lakehouse.

**Open:** `example_pipeline_demo.ipynb` in Fabric.

**Run or edit:**

1. Confirm the `source_schema` widget is `DemoTest` unless you intentionally want a different demo schema.
2. Confirm the unified target prefix remains `demo_unified_orders` for the first pass.
3. Run the full notebook to overwrite and recreate the demo source tables.

<div class="demo-expected-output" markdown>

**Expected output:** The configured source lakehouse contains deterministic demo source tables, including `demo_src_orders_happy` and `demo_src_customers_happy` for the happy path. The notebook also seeds demo-scoped DQ rules so the later governance and enforcement milestones have rules to review and apply.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Demo source tables are written under the `DemoTest` schema with the `demo_` prefix, and demo-scoped DQ rule rows are seeded into `METADATA_GUARDRAIL_RULES`. The generator is safe to rerun because it overwrites demo tables only.

</div>

!!! note "Screenshot to add"
    Capture: `example_pipeline_demo` output showing generated `demo_` source tables in `DemoTest` and seeded demo DQ rule metadata.
    Suggested filename: `docs/assets/demo/demo-03-demo-data-generator.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 4](#milestone-4-run-02_pipeline-happy-path).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 4: Run `02_pipeline` happy path

**Objective:** Run the real pipeline template against the generated happy path source data, profile source and target DataFrames, enforce currently active guardrails, and write governed unified outputs.

**Open:** `02_pipeline` in Fabric and [Pipeline Guardrails](how-fabricops-works/pipeline-guardrails.md).

**Run or edit:**

1. Keep the default source reads pointed at `DemoTest.demo_src_orders_happy` and `DemoTest.demo_src_customers_happy`.
2. Keep the default outputs set to `DemoTest.demo_unified_orders_enriched` and `DemoTest.demo_unified_orders_summary`.
3. Run the main pipeline cells that read, transform, validate, profile, and write the demo tables.
4. Use the optional governance curation section only when you want to author or review rule suggestions from inside the pipeline notebook; formal review still happens in `03_governance`.
5. Review the source profile, target profile, schema checks, freshness checks, DQ checks, lineage capture, and output write summary.

<div class="demo-expected-output" markdown>

**Expected output:** `02_pipeline` successfully reads demo sources, produces enriched and summary outputs, writes governed unified tables, and displays run evidence.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Pipeline run summaries, schema/profiles, evidence, lineage evidence, and output metadata are written through the configured metadata target where supported by the template flow. Final output tables are written to the configured unified lakehouse.

</div>

![Role-based notebook workflow from environment configuration through governed review](assets/fabricops-role-workflow.png){ .full-width }

!!! note "Screenshot to add"
    Capture: `02_pipeline` happy path guardrail/run summary showing successful unified writes for `demo_unified_orders_enriched` and `demo_unified_orders_summary`.
    Suggested filename: `docs/assets/demo/demo-04-pipeline-happy-path.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 5](#milestone-5-review-governance-in-03_governance).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 5: Review governance in `03_governance`

**Objective:** Formally review the metadata suggested or observed by the agreement and pipeline flow.

**Open:** `03_governance` in Fabric and [Governance Review](how-fabricops-works/governance-review.md).

**Run or edit:**

1. Select a profiled demo source or target table from `METADATA_DATA_CATALOGUE`.
2. Review schema, freshness, profile, DQ, and enrichment metadata for that profiled table.
3. Approve, reject, replace, deactivate, or mark active-pending-review items according to your demo script.
4. Save the governance decisions.

<div class="demo-expected-output" markdown>

**Expected output:** The governance notebook records formal review decisions that downstream pipeline runs can load as active guardrails.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Reviewed guardrail intent is written to `METADATA_GUARDRAIL_RULES`; observed profiles remains separate from approved guardrail intent, and runtime outcomes remain separate in guardrail results. See [List of Metadata Tables](reference/metadata-tables/index.md) for the table responsibilities.

</div>

!!! note "Screenshot to add"
    Capture: `03_governance` selected profiled table and review grid with approved demo schema, freshness, profile, DQ, or enrichment rows.
    Suggested filename: `docs/assets/demo/demo-05-governance-review.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 6](#milestone-6-rerun-02_pipeline-with-active-guardrails).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 6: Rerun `02_pipeline` with active guardrails

**Objective:** Show that reviewed guardrails are enforced by the pipeline runtime rather than just documented in governance metadata.

**Open:** `02_pipeline` in Fabric, then [Pipeline Guardrails](how-fabricops-works/pipeline-guardrails.md) and the [Function Reference](reference/index.md) if you want callable-level details.

**Run or edit:**

1. Keep the happy path source tables selected: `DemoTest.demo_src_orders_happy` and `DemoTest.demo_src_customers_happy`.
2. Rerun the full `02_pipeline` notebook.
3. Confirm it loads active guardrail rows from the configured metadata target.
4. Confirm warning-level DQ rules do not block publication, while error-level DQ rules block before the target write when they fail.

<div class="demo-expected-output" markdown>

**Expected output:** The happy path still publishes governed unified outputs, and the run summary shows which active guardrails were evaluated.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Runtime outcomes are written as guardrail/run evidence, with active approved rule intent remaining in `METADATA_GUARDRAIL_RULES` and observed outcomes kept as runtime evidence.

</div>

!!! note "Screenshot to add"
    Capture: `02_pipeline` rerun showing active guardrail checks loaded from governance metadata.
    Suggested filename: `docs/assets/demo/demo-06-active-guardrails-rerun.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Continue to [Milestone 7](#milestone-7-try-failure-scenarios).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Milestone 7: Try failure scenarios

**Objective:** Demonstrate how the same pipeline responds when demo source data violates schema, DQ, freshness, or profile expectations.

**Open:** `example_pipeline_demo.ipynb` if you need to regenerate scenarios, then `02_pipeline`.

**Run or edit:**

1. Rerun `example_pipeline_demo.ipynb` if you want a clean set of deterministic demo tables.
2. Point `02_pipeline` at one scenario at a time.
3. Run the relevant `02_pipeline` cells or the full notebook and inspect whether the guardrail warns, fails before write, or records profile behavior.

| Scenario | Source table | What it demonstrates |
| -------- | ------------ | -------------------- |
| Happy path | `demo_src_orders_happy` | Valid source reads and writes successfully. |
| Schema guardrail | `demo_src_orders_schema_drift` | Missing, extra, or changed columns are detected. |
| DQ guardrail | `demo_src_orders_dq_issue` | Invalid records trigger DQ warning or failure depending on reviewed severity. |
| Freshness guardrail | `demo_src_orders_stale` | Stale source data is detected. |
| Profile behavior | `demo_src_orders_reload_a` / `demo_src_orders_reload_b` | Static versus changing profile modes are visible. |

<div class="demo-expected-output" markdown>

**Expected output:** Failure scenarios either stop before governed target writes or record warning/runtime evidence, depending on the active rule type and severity.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Guardrail outcomes, run summaries, profiles, and lineage/output evidence show what was evaluated and what happened. The final unified outputs remain the pipeline outputs from successful runs.

</div>

!!! note "Screenshot to add"
    Capture: `02_pipeline` failure scenario showing blocked write or warning output.
    Suggested filename: `docs/assets/demo/demo-07-failure-scenario.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Use the [Bonus](#bonus-use-99_explore-for-discovery-or-troubleshooting) notebook for discovery or troubleshooting, or move to [What success looks like](#what-success-looks-like).

</div>

</div>

<div class="demo-milestone-card" markdown>

## Bonus: Use `99_explore` for discovery or troubleshooting

**Objective:** Use exploration support without making it a prerequisite for the governed delivery flow.

**Open:** `99_explore` in Fabric and [List of Templates](how-fabricops-works/notebook-templates.md).

**Run or edit:**

1. Select demo source or unified output tables.
2. Profile, inspect, or troubleshoot the data.
3. Capture notes or evidence that help with support and review.

<div class="demo-expected-output" markdown>

**Expected output:** Analysts can investigate source or output data without changing the required Agreement → Pipeline → Governance Review flow.

</div>

<div class="demo-evidence" markdown>

**Metadata or table evidence produced:** Any exploration evidence should remain support/discovery context. Formal approved guardrail intent still belongs in `03_governance`, and runtime outcomes still belong to `02_pipeline` runs.

</div>

!!! note "Screenshot to add"
    Capture: `99_explore` profiling a `demo_` table for troubleshooting.
    Suggested filename: `docs/assets/demo/demo-99-explore-profile.png`
    Status: Not included in this PR.

<div class="demo-next-step" markdown>

**Next:** Review [List of Metadata Tables](reference/metadata-tables/index.md) and the [Function Reference](reference/index.md) when you need to trace which helpers produced each evidence row.

</div>

</div>

## Screenshot inventory

These planned screenshots are text-only references for a future PR. No image files are included here.

| Milestone | Planned screenshot | Suggested filename | Status |
| --------- | ------------------ | ------------------ | ------ |
| Milestone 0 | Copied demo notebooks in Fabric workspace. | `docs/assets/demo/demo-00-copied-notebooks.png` | Not included in this PR. |
| Milestone 1 | Successful `00_env_config` run / `CONFIG` summary. | `docs/assets/demo/demo-01-env-config-summary.png` | Not included in this PR. |
| Milestone 2 | `01_agreement` steward/agreement/evidence widget. | `docs/assets/demo/demo-02-agreement-widgets.png` | Not included in this PR. |
| Milestone 3 | `example_pipeline_demo` generated `demo_` source tables and seeded DQ rules. | `docs/assets/demo/demo-03-demo-data-generator.png` | Not included in this PR. |
| Milestone 4 | `02_pipeline` happy path guardrail/run summary and successful unified writes. | `docs/assets/demo/demo-04-pipeline-happy-path.png` | Not included in this PR. |
| Milestone 5 | `03_governance` selected profiled table and review grid. | `docs/assets/demo/demo-05-governance-review.png` | Not included in this PR. |
| Milestone 6 | `02_pipeline` rerun with active guardrails loaded. | `docs/assets/demo/demo-06-active-guardrails-rerun.png` | Not included in this PR. |
| Milestone 7 | `02_pipeline` failure scenario blocked/warning output. | `docs/assets/demo/demo-07-failure-scenario.png` | Not included in this PR. |
| Bonus | `99_explore` profiling a `demo_` table. | `docs/assets/demo/demo-99-explore-profile.png` | Not included in this PR. |

## What success looks like

After the full demo, the flow should replace tribal knowledge with metadata-backed answers.

| Question | Where the answer should come from |
| -------- | --------------------------------- |
| Who owns the data and what is it used for? | Agreement and steward metadata captured in `01_agreement`. |
| What source and target data was profiled? | Source and target profiles captured by `02_pipeline`, plus `99_explore` notes when used. |
| What transformations created the output? | Pipeline registration, lineage, and output metadata captured in `02_pipeline`. |
| Which schema, freshness, profile, DQ, or enrichment expectations were reviewed? | Governance metadata from `03_governance`, especially active rows in `METADATA_GUARDRAIL_RULES`. |
| Which production guardrails ran? | Runtime evidence from `02_pipeline` guardrail checks, DQ enforcement, output writes, lineage, and run summaries. |
| What should support use after production? | Stored production notebook export, metadata evidence, final output tables, run summaries, and support notes. |

The goal is that support and review should no longer depend on memory or side conversations. The metadata should explain who owns the data, how it was transformed, which controls were approved, what evidence exists from the run, and which final outputs were published.

## Next reads

| Page | Why read it |
| ---- | ----------- |
| [Environment Configuration](how-fabricops-works/environment-config.md) | Understand how `00_env_config` controls configured runtime targets and metadata routing. |
| [List of Templates](how-fabricops-works/notebook-templates.md) | Learn each notebook responsibility and handoff. |
| [Pipeline Guardrails](how-fabricops-works/pipeline-guardrails.md) | Learn how `02_pipeline` owns schema, freshness, DQ, profile behavior, and run evidence. |
| [Governance Review](how-fabricops-works/governance-review.md) | Learn how `03_governance` reviews and records approved guardrail intent. |
| [List of Metadata Tables](reference/metadata-tables/index.md) | See how observed evidence, approved intent, and runtime outcomes stay separated. |
| [Function Reference](reference/index.md) | Review the reusable helper APIs used by the notebook templates. |
