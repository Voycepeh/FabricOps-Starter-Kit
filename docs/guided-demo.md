# FabricOps Guided Demo

The Guided Demo is the canonical step-by-step execution guide for FabricOps. It explains what to create, configure, open, run, and inspect from initial workspace setup through trusted Production output.

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates-implementation-guide/index.md) as the notebook download and implementation handoff.

## Execution sequence

### 1. Set up the required Fabric workspaces and artifacts

Create the Governance, Engineering Development, and Engineering Production workspaces and the required Fabric artifacts. Follow [Set Up Fabric Artifacts](guided-demo/setup-fabric-artifacts.md).

### 2. Configure `00_env_config`

Configure and run the relevant `00_env_config` notebook in each workspace so later notebooks use the correct environment, workspace, lakehouse, warehouse, and metadata settings. Follow [Run Environment Setup](guided-demo/run-environment-setup.md).

### 3. Create data stewards and establish a data agreement

Open `01_agreement` in Governance, create the data steward records, and establish the data agreement required for the pipeline. Follow [Create Agreement](guided-demo/create-agreement.md).

### 4. Optionally explore the source

Use `99_explore` in Engineering Development to understand the source, test assumptions, investigate quality issues, and develop transformation logic. Important reusable logic should move into `02_pipeline`. See [Explore Metadata Outputs](guided-demo/explore-metadata-outputs.md).

### 5. Run the initial Development pipeline

Run `02_pipeline` in Engineering Development to ingest, transform, profile, catalogue, and write the data. This initial run creates the observable profile, catalogue, lineage, and output evidence required for governance review. Follow [Run a Data Pipeline](guided-demo/run-pipeline.md).

### 6. Review and enrich the catalogue and define guardrails

After the initial pipeline evidence exists, run `03_review` in Governance. Review and enrich the catalogue, then define the applicable guardrails. Follow [Review Governance](guided-demo/review-guardrails.md).

### 7. Rerun the Development pipeline with enforcement

Rerun `02_pipeline` so it consumes the approved enrichment and guardrails. Based on the configured enforcement behaviour, a guardrail may record an informational result, produce a warning, or stop the pipeline. See [Run a Data Pipeline with Guardrails](guided-demo/run-pipeline-with-guardrails.md).

### 8. Review the resulting evidence

Inspect the updated profiling, catalogue, lineage, and guardrail results produced by the enforced rerun. Use [Explore Metadata Outputs](guided-demo/explore-metadata-outputs.md) and the [Metadata Table Reference](reference/metadata.md) to understand the stored evidence.

### 9. Create the data contract

Return to `01_agreement` in Governance and create a data contract tied to the data agreement and the approved pipeline.

### 10. Promote the pipeline to Production

Promote the approved `02_pipeline` notebook from Engineering Development to Engineering Production. All promoted pipelines should be tied to a data contract.

### 11. Run the stable Production pipeline

Run the promoted `02_pipeline` on its required Production schedule so full data loads and long-term outputs are created in the Production lakehouses or warehouses.

### 12. Consume the trusted output

Allow AI, BI, applications, agents, file exports, other engineering pipelines, or other downstream processes to consume the trusted Production data product subject to the appropriate access controls.

## Required lifecycle

**Initial pipeline evidence → Governance review and enrichment → Guardrail definition → Pipeline rerun with enforcement**

Guardrail results from enforcement follow the initial pipeline evidence and governance review. The workflow does not assume that enforceable guardrail results exist before `02_pipeline` has produced observable catalogue and profiling evidence.

## Technical lookup

Use the reference pages for implementation detail rather than duplicating their specifications here:

- [Notebook Templates](notebook-templates-implementation-guide/index.md): notebook responsibilities and downloads
- [Metadata Table Reference](reference/metadata.md): table purposes, schemas, and ownership
- [DQ Rule Reference](reference/dq-rules/index.md): supported rule types and parameters
- [Function Reference](reference/index.md): callable behaviour and implementation detail
