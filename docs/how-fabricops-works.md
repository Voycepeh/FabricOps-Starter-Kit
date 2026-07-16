# How FabricOps works

FabricOps works through a three-workspace setup:

1. Governance workspace
2. Engineering Development workspace
3. Engineering Production workspace

The Governance workspace defines ownership, agreements, enrichment, and guardrails.

The Engineering Development workspace is where pipelines are developed, tested, profiled, and reviewed.

The Engineering Production workspace contains promoted and stable pipelines that run on a recurring basis and produce trusted data for downstream AI and BI consumption.

Together, these workspaces create one connected workflow:

**Define governance requirements → Develop the pipeline → Capture metadata evidence → Review and enrich the catalogue → Enforce guardrails → Create a data contract → Promote to production → Consume the trusted data**

## Shared environment configuration

Every workspace contains a single `00_env_config` notebook template. This is the central configuration notebook where shared information required by the other workflows is stored for downstream use. The relevant `00_env_config` notebook runs at the start of every other FabricOps notebook template.

Each workspace has its own copy because the Governance, Development, and Production environments may use different workspace IDs, lakehouses, warehouses, and configuration values.

## Three-workspace setup

### Governance workspace

The Governance workspace contains `00_env_config`, `01_agreement`, `03_review`, and a manually created metadata lakehouse. It defines ownership and agreements, reviews and enriches the data catalogue, defines guardrails, and creates the data contract that provides governance approval to promote a pipeline.

### Engineering Development workspace

The Engineering Development workspace contains `00_env_config`, Development versions of `02_pipeline`, `99_explore`, and Development lakehouses or warehouses. It is intended for development, testing, profiling, review, and one-off analysis. FabricOps standardizes the operating workflow without forcing every team to adopt one fixed data architecture.

The `02_pipeline` template adds statistical profiling, frequency tables, schema evolution tracking, lineage registration, catalogue registration, guardrail enforcement, guardrail result capture, and standardized Fabric input and output operations around a reusable PySpark pipeline.

The `99_explore` template supports one-off exploration and analysis. Important or reusable findings should eventually move into a proper `02_pipeline` workflow, while important one-off analyses should be preserved when future reproducibility is required.

### Engineering Production workspace

The Engineering Production workspace contains `00_env_config`, promoted and stable `02_pipeline` notebooks, Production lakehouses or warehouses, and full Production datasets and outputs.

It mirrors the relevant Engineering Development setup but contains only deployed and stable pipelines that need to run on a recurring basis. All promoted `02_pipeline` notebooks should be tied to a data contract. Production is where full data loads and long-term storage should take place.

## AI and BI analytics consumption

The stable data products generated in the Engineering Production workspace provide the base for downstream AI and BI consumption, including Power BI reports and semantic models, AI and machine-learning workloads, agents, applications, file exports, and other analytics or engineering products.

A separate consumption workspace is an optional extension, rather than a mandatory part of the initial three-workspace setup, when an organisation's scale, access, ownership, compute, or release requirements justify it.

## The complete FabricOps workflow

1. Configure the Governance, Engineering Development, and Engineering Production workspaces through their respective `00_env_config` notebooks.
2. Create the metadata lakehouse and initialize the required metadata tables.
3. Use `01_agreement` to create data stewards and establish a data agreement.
4. Use `99_explore` to understand the data and investigate the required pipeline logic.
5. Use `02_pipeline` in Development to ingest, transform, profile, catalogue, and write the data.
6. Capture profiling, schema, catalogue, and lineage evidence automatically.
7. Use `03_review` to review the catalogue, enrich the metadata, and define guardrails.
8. Re-run `02_pipeline` to consume and enforce the approved enrichment and guardrails.
9. Review the resulting evidence and guardrail results.
10. Use `01_agreement` to create a data contract tied to the agreement and pipeline.
11. Promote the approved `02_pipeline` notebook from Development to Production.
12. Run the stable Production pipeline on its required schedule.
13. Allow AI, BI, and other data consumers to use the trusted Production data product.
14. Preserve important one-off analyses when future reproducibility is required.

FabricOps therefore connects governance, engineering, and analytics through one standardized Microsoft Fabric workflow.

For the detailed approved terminology and responsibilities behind this overview, see the [canonical product narrative](maintainers/product-narrative.md).
