# FabricOps canonical product narrative

This document is the source of truth for FabricOps product positioning, terminology, workspace responsibilities, notebook responsibilities, and the end-to-end workflow.

Public-facing documentation may shorten or reorganize this content for its intended audience, but it must not introduce a conflicting product story or change the meaning of the workflow without first updating this document.

## What is FabricOps?

FabricOps, short for Fabric Operations, is a plug-and-play, lightweight starter kit that helps data teams across three main roles:

- Governance
- Data engineering
- AI and BI analytics

It helps these teams quickly set up and adopt an out-of-the-box workflow within the Microsoft Fabric platform.

FabricOps consists of:

- A Python package containing out-of-the-box helper and orchestrator functions
- Standardized Python notebook templates that weave these functions into reusable workflows
- A shared metadata model that connects governance and engineering activities
- A guided demo to help teams understand and adopt the workflow quickly
- Technical documentation for the notebook templates, metadata tables, and individual functions

By standardizing these workflows, FabricOps ensures that essential metadata and governance processes are built directly into engineering pipelines.

This provides the AI and BI consumption layer with a stable, governed, and reusable data foundation to work from.

## How FabricOps works

FabricOps works through a three-workspace setup:

1. Governance workspace
2. Engineering Development workspace
3. Engineering Production workspace

The Governance workspace defines ownership, agreements, enrichment, and guardrails.

The Engineering Development workspace is where pipelines are developed, tested, profiled, and reviewed.

The Engineering Production workspace contains promoted and stable pipelines that run on a recurring basis and produce trusted data for downstream AI and BI consumption.

Together, these workspaces create one connected workflow:

Define governance requirements → Develop the pipeline → Capture metadata evidence → Review and enrich the catalogue → Enforce guardrails → Create a data contract → Promote to production → Consume the trusted data

## Shared environment configuration

Every workspace contains a single `00_env_config` notebook template.

This is the central configuration notebook where shared information required by the other workflows is stored for downstream use.

It may contain:

- Workspace and lakehouse information
- Environment-specific settings
- Metadata configuration
- Shared variables
- FabricOps package imports
- Runtime context used by other notebook templates

The relevant `00_env_config` notebook runs at the start of every other FabricOps notebook template.

Each workspace has its own copy because the Governance, Development, and Production environments may use different workspace IDs, lakehouses, warehouses, and configuration values.

## Governance workspace

The Governance workspace contains:

- `00_env_config`
- `01_agreement`
- `03_review`
- A manually created metadata lakehouse

The metadata lakehouse is created manually because it is the long-term metadata store used across the FabricOps workflow.

On the first run of `00_env_config` in the Governance workspace, FabricOps helps set up the metadata tables required by the installed release.

These tables capture the essential governance and engineering metadata generated throughout the workflow.

### `01_agreement` template

The `01_agreement` template provides users with an avenue to:

- Create data steward records
- Record a data agreement between two data stewards
- Review the enriched data catalogue after the `02_pipeline` and `03_review` workflows have been completed
- Create a data contract
- Tie the data contract back to a data agreement and the relevant production pipeline

The data contract provides the governance approval required to promote a `02_pipeline` notebook from Development to Production.

The primary metadata tables written to by this workflow are:

- Data Steward
- Data Agreement
- Data Contract

The template contains a simple front-end interface using Python notebook widgets. This helps ensure that users enter the correct information into the correct underlying metadata tables.

### `03_review` template

The `03_review` template provides users with an avenue to browse the data catalogue generated from the current tables in the engineering lakehouses.

Governance users can review and enrich the catalogue information. This enrichment is then consumed as guardrails within the engineering pipelines.

Supported enrichment may include:

1. Personal identifier labelling for columns
2. Sensitivity classification, such as confidential, restricted, or public
3. Business descriptions for tables and columns

Supported guardrails may include:

1. Data quality rules
2. Schema drift
3. Data drift, such as unexpected changes compared with yesterday’s or a previous run’s data
4. Anonymity or masking requirements for personal identifier columns
5. Granularity rules based on the assigned data classification

The primary metadata tables written to are:

- Enrichment
- Guardrails

Like `01_agreement`, the `03_review` template uses notebook widgets to provide a simple user interface and ensure that governance information is written correctly.

## Engineering Development workspace

The Engineering Development workspace contains:

- `00_env_config`
- Development versions of `02_pipeline`
- `99_explore`
- Development lakehouses or warehouses

A suggested setup may include:

- A source lakehouse
- A unified lakehouse
- A product warehouse

However, this is only a suggested architecture.

Teams may use any number of lakehouses or warehouses based on their own requirements. FabricOps standardizes the operating workflow without forcing every team to adopt one fixed data architecture.

The Development workspace is intended for development, testing, and one-off analysis.

Teams should avoid performing unnecessary full data loads or using this workspace as long-term storage for production datasets.

Development data and temporary notebooks should be expected to be cleaned or removed regularly.

### `02_pipeline` template

The `02_pipeline` template provides data engineers with a reusable PySpark data pipeline notebook.

A standard pipeline normally:

1. Ingests data
2. Transforms the data
3. Writes the data

The FabricOps template adds standardized governance and metadata activities around this engineering workflow.

These activities include:

- Statistical data profiling
- Full or sampled frequency-table generation
- Schema evolution tracking
- Table-level data lineage registration for the entire notebook
- Data catalogue registration
- Guardrail enforcement
- Guardrail result capture
- Standardized Fabric input and output operations

After the data has been profiled, the pipeline consumes the enrichment and guardrails created in the Governance workspace through the `03_review` template.

Based on the configured enforcement behaviour, a guardrail may:

- Record an informational result
- Produce a warning
- Stop the pipeline

The primary metadata tables written to by the pipeline are:

- Data Profiled
- Data Catalogue
- Lineage
- Guardrail Results

This means that metadata is not recorded manually after pipeline development. It is captured as part of the normal engineering workflow.

### Why PySpark is used

Spark has a startup time, and Python with pandas may be faster for smaller datasets.

However, FabricOps uses PySpark as the standard pipeline approach because it needs to support larger datasets and provide a consistent engineering pattern.

Using one standardized approach also makes pipelines easier to understand, maintain, and hand over between engineers.

This does not prevent users from using pandas or other tools for appropriate one-off analysis. It simply establishes PySpark as the standard approach for repeatable `02_pipeline` workflows.

### `99_explore` template

The `99_explore` template is intended for one-off exploration and analysis.

Users may use it to:

- Explore a dataset
- Test assumptions
- Investigate data quality issues
- Develop transformation logic
- Produce a one-off analytical output
- Decide whether an analysis should later become a repeatable pipeline

Important or reusable findings from `99_explore` should eventually be moved into a proper `02_pipeline` workflow.

The Development workspace should remain disposable. Therefore, important one-off analysis should not rely only on the current state of a source table.

If the source table is updated, replaced, or dropped, the original analysis may no longer be reproducible.

## Engineering Production workspace

The Engineering Production workspace contains:

- `00_env_config`
- Promoted and stable `02_pipeline` notebooks
- Production lakehouses or warehouses
- Full production datasets and outputs

This workspace is intended for production workloads.

It mirrors the relevant Engineering Development setup but contains only deployed and stable `02_pipeline` notebooks that need to run on a recurring basis.

A recurring pipeline may run:

- Hourly
- Daily
- Monthly
- Annually
- Based on another operational schedule

Even a pipeline that runs only once a year is still considered a recurring production process if it needs to remain stable and repeatable.

All promoted `02_pipeline` notebooks should be tied to a data contract.

The data contract connects:

- The data agreement
- The responsible data stewards
- The governed dataset
- The approved pipeline
- The expected output
- The applicable enrichment and guardrails

Production is where full data loads and long-term storage should take place.

## AI and BI analytics consumption

The stable data products generated in the Engineering Production workspace provide the base for downstream AI and BI consumption.

These outputs may be consumed by:

- Power BI reports and semantic models
- AI and machine-learning workloads
- Agents
- Applications
- File exports
- Other engineering pipelines
- Other analytics products

For a smaller implementation, these consumers may access the production lakehouse or warehouse directly, subject to the appropriate access controls.

For a larger implementation, teams may introduce a separate consumption workspace.

A standalone consumption workspace may be useful when:

- BI and AI teams have different access requirements from engineering teams
- Semantic models have separate owners
- Compute capacity needs to be isolated
- Consumers should not access engineering workspaces
- Data products need their own release and support lifecycle

This consumption workspace should be treated as an optional extension rather than a mandatory part of the initial three-workspace setup.

## Preserving important one-off analysis

The Engineering Development workspace may be cleaned regularly to remove excess data, temporary outputs, and unused notebooks.

This creates a reproducibility risk for important `99_explore` analyses.

For example, an analyst may use:

```sql
SELECT *
FROM source_table
```

If the underlying source table is later updated or dropped, the original analysis may no longer be reproduced accurately.

For useful or important `99_explore` notebooks, FabricOps should support an analysis archive or analysis packet.

The archived package may contain:

1. The notebook itself
2. The FabricOps package version
3. The environment and execution information
4. The exact input table references
5. The queries, selected columns, and filters used
6. The input schema
7. Input data stored as CSV or Parquet where required
8. Output data stored as CSV or Parquet
9. Row counts and checksums
10. The related agreement or contract context
11. The purpose and owner of the analysis

Not every analysis requires a complete copy of the source dataset.

FabricOps may support different preservation levels.

### Reference only

Store:

- The source table
- The table version
- The query
- The schema
- The execution timestamp

This is appropriate when the source platform provides reliable version history or time travel.

### Input extract

Store only the exact rows and columns used by the analysis.

This may be the most practical default for useful one-off analyses.

### Full snapshot

Store a complete copy of the source data used by the analysis.

This should be used only when the business, governance, or regulatory need justifies the additional storage.

These archived analysis packets should not be kept permanently in the disposable Development workspace.

They may be stored in:

- A governed archival lakehouse in Production
- A dedicated Analytics workspace
- A dedicated Evidence or Archive workspace
- A controlled Files area associated with the relevant data product

A separate archive or consumption workspace may therefore be added when the organisation’s scale and governance requirements justify it.

## The complete FabricOps workflow

The complete workflow is:

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
12. Run the stable production pipeline on its required schedule.
13. Allow AI, BI, and other data consumers to use the trusted production data product.
14. Preserve important one-off analyses when future reproducibility is required.

FabricOps therefore connects governance, engineering, and analytics through one standardized Microsoft Fabric workflow.
