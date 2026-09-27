# FabricOps Guided Demo

**Run the FabricOps operating model yourself in Microsoft Fabric, from initial setup through governed Production consumption.**

`00A`, `00B`, and `00C` prepare the Fabric environment, configure the notebooks, exercise the FabricOps I/O helpers, and seed the managed demo tables. The seven numbered steps then walk through the same lifecycle described in [How FabricOps Works](how-fabricops-works.md).

!!! tip "New to Microsoft Fabric?"

    Start with [Microsoft Learn: Fabric fundamentals](https://learn.microsoft.com/en-us/fabric/fundamentals/) for the platform concepts used throughout the demo. When you reach the engineering parts, continue with [Microsoft Learn: Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/) for Lakehouse, notebooks, Spark, and Data Engineering workflows.

    **Useful visual reference:** [Microsoft Fabric Visual Notes](https://www.slideshare.net/slideshow/microsoft-fabric-complete-handwritten-notes-pdf/289496813) — a visual community reference covering Fabric architecture, PySpark, pipelines, incremental loading, data quality, CI/CD, monitoring, and related concepts.

    FabricOps documentation remains the source of truth for how this starter kit is designed and used.

## Foundation setup

| Setup | What you do | Why it matters |
| --- | --- | --- |
| [0A. Prepare Fabric artifacts](guided-demo/00A-prepare-fabric-artifacts.md) | Create the workspaces, stores, and Fabric Environments, then install the FabricOps wheel. | The physical Fabric foundation exists. |
| [0B. Load and configure the Guided Demo assets](guided-demo/00B-configure-environment-and-load-assets.md) | Import the core notebooks, attach their Fabric Environments, configure `00_env_config`, create the metadata tables, and upload the packaged demo files to Bronze `Files/Demo`. | Every notebook can resolve the configured Fabric stores and the raw demo assets are in place. |
| [0C. Prepare the demo data with FabricOps I/O](guided-demo/00C-prepare-demo-data-with-fabricops-io.md) | Run `00C_demo_setup` in Engineering Development to demonstrate file, Lakehouse, and Warehouse I/O and seed the managed source tables. | `02_pipeline` starts from real managed tables prepared through the public FabricOps I/O helpers. |

## The seven-step FabricOps workflow

![FabricOps role workflow](assets/fabricops-role-workflow.png)

| Step | Notebook | What you do |
| --- | --- | --- |
| [1. Establish Governance context](guided-demo/01-establish-governance-context.md) | `01_governance` | Create Data Stewards and a Data Agreement. |
| [2. Build and run the ETL](guided-demo/02-build-and-run-etl.md) | `02_pipeline` / `02B_incremental_append_pipeline` | Choose the pipeline pattern for the workload: [Full Read Pipeline](guided-demo/02-build-and-run-etl.md) for complete-source reads, or [Incremental Append Pipeline](guided-demo/02B-build-and-run-incremental-append-etl.md) for target-aware incremental processing. Both follow the same Read → Transform → Write lifecycle and profile the complete persisted target after publication. |
| [3. Author and freeze the Data Contract](guided-demo/03-author-and-freeze-data-contract.md) | `01_governance` | Select the real `table_id`, author Enrichment, Guardrails, and Processing, then freeze the contract version. |
| [4. Validate the frozen Data Contract](guided-demo/04-validate-frozen-data-contract.md) | `02_pipeline` | Put the governed target in Validate mode, evaluate the exact frozen candidate, record aggregate evidence, and leave the business target unchanged. |
| [5. Activate the Data Contract and promote](guided-demo/05-activate-data-contract-and-promote.md) | `01_governance` + Fabric Deployment Pipeline | Link the tested contract version to the Data Agreement, activate it for Production, then deploy the validated engineering artifact from Development to Production. |
| [6. Run the pipeline in Production](guided-demo/06-run-production.md) | `02_pipeline` | Run the same validated Read → Transform → Write workflow again using Production configuration and the active Data Contract. |
| [7. Consume approved Production data](guided-demo/07-consume-production-data.md) | `99_explore` | Read approved Production outputs from the consumer workspace. |

??? info "Detailed lifecycle responsibilities"

    1. **Governance establishes the people and agreement context.** [`widget_render_data_steward()`](api/reference/widget_render_data_steward.md) writes Data Steward records, and [`widget_render_data_agreement()`](api/reference/widget_render_data_agreement.md) writes Data Agreement records.
    2. **Engineering Development builds the ETL and produces the governed table.** `02_pipeline` reads, transforms, writes, profiles, and records the technical context around the real table. [`profile_table()`](api/reference/profile_table.md) keeps the Data Catalogue and profiling metadata aligned with what Engineering actually produced.
    3. **Governance authors the Data Contract for that `table_id`.** [`widget_data_contract()`](api/reference/widget_data_contract.md) brings together Enrichment, Guardrails, and the governed processing definition for the table.
    4. **Engineering Development selects a contract version and validates the real pipeline.** [`widget_select_data_contract()`](api/reference/widget_select_data_contract.md) sets the selected contract per linked `table_id`, and the Guardrail functions execute its expectations against the real data flow.

        **Steps 3 ↔ 4 are intentionally iterative.** Governance authors the next contract version; Engineering selects that immutable version and reruns the pipeline against it. If the expectation needs refinement or the implementation does not satisfy the intended rule, the flow returns to Governance for another version and then back to Engineering for another validation run. The loop continues until the governed definition and the real engineering implementation agree.

    5. **Governance activates the tested definition, then Engineering promotes it to Production.** [`widget_data_contract()`](api/reference/widget_data_contract.md) links the exact Data Agreement version and tags one frozen Data Contract version as active for that `table_id`. Frozen versions stay frozen; activation does not change their governed JSON. Development can validate any frozen version. Production is strict: it must resolve exactly one frozen version with `is_active=true` for each linked `table_id`. After activation, the validated engineering artifact is deployed from Engineering Development to Engineering Production through the Fabric Deployment Pipeline.
    6. **Engineering runs the same workflow again in Production.** The promoted `02_pipeline` resolves Production stores through `00_env_config`, automatically resolves the active Data Contract, applies the same Read → Transform → Write pattern and Guardrail functions, and publishes the governed output. Successful writes commit the associated runtime Lineage and Source Observation state.
    7. **Project teams consume the approved Production result.** `99_explore` provides the reusable read-only exploration entry point without recreating the Production ETL in every consumer workspace.
