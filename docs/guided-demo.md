# FabricOps Guided Demo

The Guided Demo is the canonical step-by-step execution guide for FabricOps. It explains what to create, configure, open, run, and inspect from initial Fabric preparation through Production promotion and project-specific consumption.

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) as the notebook download and implementation handoff.

## Required execution sequence

| Step | Workspace | Notebook | Maintained action page |
| ---- | --------- | -------- | ---------------------- |
| 0A | Governance, Engineering Development, Engineering Production, and any required Project-Specific Consumer workspaces | — | [Prepare Fabric artifacts](guided-demo/setup-fabric-artifacts.md) |
| 0B | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Set up the operating environment](guided-demo/run-environment-setup.md) |
| 1 | Governance | `01_agreement` | [Create data stewards and a data agreement](guided-demo/create-agreement.md) |
| 2 | Engineering Development | `02_pipeline` | [Run the first Development pipeline](guided-demo/run-pipeline.md) |
| 3 | Governance | `03_review` | [Review catalogue evidence and define guardrails](guided-demo/review-guardrails.md) |
| 4 | Engineering Development | `02_pipeline` | [Rerun the Development pipeline with guardrails](guided-demo/run-pipeline-with-guardrails.md) |
| 5 | Governance | `01_agreement` | [Create the Data Contract and record steward sign-off](guided-demo/create-data-contract.md) |
| 6 | Engineering Production | Promoted `02_pipeline` | [Promote the validated pipeline to Production](guided-demo/promote-to-production.md) |
| 7 | Project-Specific Consumer | `99_explore` | [Consume approved Production data with FabricOps IO and profiling](guided-demo/run-io-and-profiling-demo.md) |

Step 0 is split into two preparation stages. Step 0A creates the required Fabric workspaces, lakehouses, warehouses, Environment, installed FabricOps wheel, and copied notebook templates. Step 0B configures `00_env_config` and creates or validates the Governance metadata tables.

Approval and promotion occur only after the Data Contract is signed off in Step 5. Step 6 promotes the validated `02_pipeline` from Engineering Development into Engineering Production.

After approved Production outputs are available, Step 7 uses `99_explore` in one or more project-specific consumer workspaces for exploration, AI, and BI consumption. Consumer workspaces read approved Engineering Production data and do not replace or duplicate the governed production pipeline.

## Supporting walkthroughs

[Understand FabricOps widgets and metadata outputs](guided-demo/explore-metadata-outputs.md) explains the widgets, selections, metadata records, and outputs users encounter across the FabricOps notebook workflow. It is supporting guidance rather than a separately numbered lifecycle step because the widgets are used within the relevant agreement, pipeline, review, and consumer notebooks.

`example_pipeline_demo` and other example notebooks support demos, training, and smoke testing. They are not canonical workflow steps and should not be presented as required production work.

## Required lifecycle

**Step 0A Fabric preparation → Step 0B environment configuration → Step 1 agreement → Step 2 Development evidence → Step 3 governance review → Step 4 guardrail validation → Step 5 contract sign-off → Step 6 Production promotion → Step 7 project consumption**

Steps 0A and 0B prepare the shared FabricOps environment. Steps 1 through 6 establish and operate the governed production pipeline. Step 7 consumes approved Production outputs in one or more project-specific consumer workspaces.

Guardrail results from enforcement follow the initial pipeline evidence and governance review. The workflow does not assume that enforceable guardrail results exist before `02_pipeline` has produced observable catalogue, profiling, and lineage evidence.

## Technical lookup

Use the reference pages for implementation detail rather than duplicating their specifications here:

- [Notebook Templates](notebook-templates.md): notebook responsibilities and downloads
- [Metadata Table Reference](reference/metadata.md): table purposes, schemas, and ownership
- [DQ Rule Reference](reference/dq-rules/index.md): supported rule types and parameters
- [Function Reference](reference/index.md): callable behaviour and implementation detail
