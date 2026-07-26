# FabricOps Guided Demo

The Guided Demo is the canonical step-by-step execution guide for FabricOps. It explains what to create, configure, open, run, and inspect from initial workspace setup through Production promotion.

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) as the notebook download and implementation handoff.

## Required execution sequence

| Step | Workspace | Notebook | Maintained action page |
| ---- | --------- | -------- | ---------------------- |
| 0 | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Set up the operating environment](guided-demo/run-environment-setup.md) |
| 1 | Governance | `01_agreement` | [Create data stewards and a data agreement](guided-demo/create-agreement.md) |
| 2 | Engineering Development | `02_pipeline` | [Run the first Development pipeline](guided-demo/run-pipeline.md) |
| 3 | Governance | `03_review` | [Review catalogue evidence and define guardrails](guided-demo/review-guardrails.md) |
| 4 | Engineering Development | `02_pipeline` | [Rerun the Development pipeline with guardrails](guided-demo/run-pipeline-with-guardrails.md) |
| 5 | Governance | `01_agreement` | [Create the Data Contract and record steward sign-off](guided-demo/create-data-contract.md) |
| 6 | Engineering Production | Promoted `02_pipeline` | [Promote the validated pipeline to Production](guided-demo/promote-to-production.md) |

Approval and promotion occur only after the Data Contract is signed off in Step 5. Step 6 promotes the validated `02_pipeline` from Engineering Development into Engineering Production.

## Optional demo support

`99_explore` is optional and outside the required Step 0 through Step 6 production workflow. Use it in Engineering Development for one-off exploration, analysis, troubleshooting, and transformation development. It must not change governed agreement, contract, enrichment, or guardrail state. See [Explore Metadata Outputs](guided-demo/explore-metadata-outputs.md).

`example_pipeline_demo` and other example notebooks support demos, training, and smoke testing. They are not canonical workflow steps and should not be presented as required production work.

## Required lifecycle

**Step 0 setup → Step 1 agreement → Step 2 Development evidence → Step 3 governance review → Step 4 guardrail validation → Step 5 contract sign-off → Step 6 Production promotion**

Guardrail results from enforcement follow the initial pipeline evidence and governance review. The workflow does not assume that enforceable guardrail results exist before `02_pipeline` has produced observable catalogue, profiling, and lineage evidence.

## Technical lookup

Use the reference pages for implementation detail rather than duplicating their specifications here:

- [Notebook Templates](notebook-templates.md): notebook responsibilities and downloads
- [Metadata Table Reference](reference/metadata.md): table purposes, schemas, and ownership
- [DQ Rule Reference](reference/dq-rules/index.md): supported rule types and parameters
- [Function Reference](reference/index.md): callable behaviour and implementation detail
