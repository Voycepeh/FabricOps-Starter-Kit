# How FabricOps works

<style>
.md-typeset .fabricops-section-block {
  margin: 1.25rem 0;
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.4rem;
  background-color: var(--md-default-bg-color);
  box-shadow: 0 0.12rem 0.45rem rgba(0, 0, 0, 0.04);
}

.md-typeset .fabricops-section-block > :first-child {
  margin-top: 0;
}

.md-typeset .fabricops-section-block > :last-child {
  margin-bottom: 0;
}

.md-typeset .fabricops-workflow-steps {
  margin: 1rem 0 0;
  border-top: 1px solid var(--md-default-fg-color--lightest);
}

.md-typeset details.fabricops-workflow-step {
  margin: 0;
  border: 0;
  border-bottom: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.md-typeset details.fabricops-workflow-step > summary {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.8rem;
  align-items: center;
  min-height: 3.5rem;
  padding: 0.8rem 0.15rem;
  cursor: pointer;
  list-style: none;
  background: transparent;
}

.md-typeset details.fabricops-workflow-step > summary::before,
.md-typeset details.fabricops-workflow-step > summary::after {
  display: none !important;
  content: none !important;
}

.md-typeset details.fabricops-workflow-step > summary::-webkit-details-marker {
  display: none;
}

.md-typeset .fabricops-step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--md-accent-fg-color) 12%, transparent);
  color: var(--md-accent-fg-color);
  font-size: 0.75rem;
  font-weight: 700;
}

.md-typeset .fabricops-step-heading {
  min-width: 0;
}

.md-typeset .fabricops-step-role {
  display: block;
  margin-bottom: 0.12rem;
  color: var(--md-accent-fg-color);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.045em;
  text-transform: uppercase;
}

.md-typeset .fabricops-step-title {
  display: block;
  color: var(--md-default-fg-color);
  font-size: 0.92rem;
  font-weight: 700;
  line-height: 1.35;
}

.md-typeset .fabricops-step-chevron {
  width: 0.5rem;
  height: 0.5rem;
  border-right: 0.1rem solid var(--md-default-fg-color--light);
  border-bottom: 0.1rem solid var(--md-default-fg-color--light);
  transform: rotate(45deg);
  transition: transform 0.15s ease;
}

.md-typeset details.fabricops-workflow-step[open] > summary .fabricops-step-chevron {
  transform: rotate(225deg);
}

.md-typeset details.fabricops-workflow-step[open] > summary {
  border-bottom: 1px solid var(--md-default-fg-color--lightest);
}

.md-typeset .fabricops-step-body {
  padding: 0.15rem 0.15rem 1rem 2.7rem;
}

.md-typeset .fabricops-step-body > :first-child {
  margin-top: 0.55rem;
}

.md-typeset .fabricops-step-body > :last-child {
  margin-bottom: 0;
}

@media screen and (max-width: 44.9844em) {
  .md-typeset .fabricops-step-body {
    padding-left: 0.15rem;
  }
}
</style>

<div class="fabricops-section-block" markdown>

**FabricOps connects Governance, Engineering Development, Engineering Production, and project-specific consumer workspaces through one governed workflow.**

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

The shared Metadata Lakehouse carries FabricOps metadata between Governance and Engineering. Governance defines and approves the governed expectations, Engineering Development builds and validates the pipeline against them, Engineering Production resolves the active Data Contract at runtime, and project-specific consumer workspaces consume approved Production data.

<!-- VIDEO SLOT: Main How FabricOps Works overview -->

</div>

<div class="fabricops-section-block" markdown>

## The workflow at a glance

FabricOps is built around four reusable notebooks that work together as one operating practice:

| Notebook | Role in the workflow |
| --- | --- |
| [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) | Defines the active environment and the configured Fabric items used by the workflow. |
| [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_governance.ipynb) | Creates Data Stewards and Data Agreements, enriches governed tables, defines Guardrails, and manages Data Contract versions. |
| [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) | Performs project-specific engineering, records technical metadata, validates governed expectations, and runs the governed Production pipeline. |
| [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb) | Lets project-specific consumer workspaces use approved Production data without recreating the Production engineering workflow. |

[Browse all reusable notebook templates](notebook-templates.md).

For the deeper engineering reasoning behind `00_env_config`, FabricOps I/O functions, Lakehouse/Warehouse choices, PySpark, incremental processing, and the detailed `02_pipeline` structure, use the [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md).

</div>

<div class="fabricops-section-block" markdown>

## The Governance and Engineering loop

![FabricOps role workflow](assets/fabricops-role-workflow.png)

FabricOps deliberately loops between Governance and Engineering Development before the approved pipeline runs in Production. Scan the seven stages below, then expand a stage when you need the implementation detail.

<!-- VIDEO SLOT: Governance and Engineering loop -->

<div class="fabricops-workflow-steps" markdown>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">1</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Governance</span><span class="fabricops-step-title">Create Data Stewards and a Data Agreement in <code>01_governance</code></span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

In `01_governance`, Governance creates the provider and recipient **Data Stewards** and a **Data Agreement** between them.

The Data Agreement establishes the governed sharing context: who is providing and receiving the data, the business purpose, approved usages, validity, and other agreement-level governance information.

</div>
</details>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">2</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Engineering Development</span><span class="fabricops-step-title">Build the ETL pipeline within <code>02_pipeline</code></span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

Engineering Development uses `02_pipeline` to read one or more configured sources, perform project-specific transformations, and write governed target tables to the configured Lakehouse or Warehouse.

Each governed target is identified by a canonical `table_id`. Engineering then records the technical context around that table, including:

- **Data Catalogue metadata** — the governed table and column structure used as the canonical technical identity for the target.
- **Data Profiled records** — observed characteristics of the data that help Engineering and Governance understand what is actually present.
- **Data Profiled Frequency**, where applicable — the recorded frequency distribution for profiled values where that deeper profile is useful.
- **Data Lineage** — the relationship between the source data used by the pipeline and the governed target it produces.

The `table_id` is the shared identity that lets the rest of the FabricOps workflow refer to the same governed table.

#### Engineering choices

FabricOps makes several engineering choices so projects do not need to redefine the same foundations every time. This page only introduces them; use each link to jump into the deeper Engineering Guide explanation.

- **[Configuration-driven engineering](reference/engineering-cheat-sheet.md#config-driven-engineering)** — separate reusable `02_pipeline` logic from environment-specific Fabric item identities through `00_env_config` and FabricOps I/O resolution.
- **[Code-first engineering](reference/engineering-cheat-sheet.md#notebook-first)** — keep governed transformation logic explicit, reviewable, and versionable in code, with `02_pipeline` as the primary engineering implementation.
- **[ETL lifecycle implementation](reference/engineering-cheat-sheet.md#etl-lifecycle)** — keep one visible `Environment → Extract → Transform → Load` lifecycle while FabricOps supplies the repeatable engineering behaviour around it.
- **[PySpark-first transformation](reference/engineering-cheat-sheet.md#pyspark-first)** — use PySpark DataFrames for the main transformation path, with T-SQL for efficient Warehouse-side operations before data enters Spark.
- **[Lakehouse-first engineering](reference/engineering-cheat-sheet.md#lakehouse-first)** — prefer Lakehouse for substantial or repeated Spark engineering while still supporting Warehouse as a relational source or curated serving layer.
- **[Single-target pipeline implementation](reference/engineering-cheat-sheet.md#single-target-pipeline)** — allow many upstream sources to feed one `02_pipeline`, but publish one governed target so independent writes cannot leave a partially completed multi-target pipeline.
- **[Governance as Code](reference/engineering-cheat-sheet.md#governance-as-code)** — keep FabricOps self-contained in Fabric by recording Catalogue, Profile, Lineage, Enrichment, Guardrails, results, Agreements, and Contracts in shared metadata tables centred on the canonical `table_id`.
- **[Medallion architecture implementation](reference/engineering-cheat-sheet.md#medallion-architecture)** — implement progressive data layers where they add architectural value without forcing unnecessary copies or fixed layer names.
- **[Incremental load implementation](reference/engineering-cheat-sheet.md#full-vs-incremental)** — use full, watermark, or partition-based processing according to source behaviour, scale, and recovery requirements.
- **[Failure-safe processing and recovery](reference/engineering-cheat-sheet.md#failure-safe-processing)** — persist successful progress atomically on governed target rows through `_watermark_value` or `_partition_bucket`.

The exact ETL implementation stays project-specific. FabricOps standardizes the environment, I/O boundaries, metadata capture, validation, and governed hand-offs around that engineering work.

</div>
</details>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">3</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Governance</span><span class="fabricops-step-title">Select the <code>table_id</code> and author the governed Data Contract definition</span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

Back in `01_governance`, Governance selects the same canonical `table_id` from the Data Catalogue and reads the Catalogue and Profile information produced by Engineering.

Governance can then add:

- **Enrichment**, such as business meaning, sensitivity classification, PII classification, and other table- or column-level context
- **Guardrails**, such as schema, freshness, and Data Quality expectations
- the governed target **load strategy** and its parameters, such as overwrite, append, SCD1, or SCD2, as part of the table definition that will be saved into the Data Contract

Together, these records form the authored governed definition for that `table_id`. Governance can refine this definition before it is saved as an immutable Data Contract version.

</div>
</details>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">4</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Engineering Development</span><span class="fabricops-step-title">Run the governed definition in <code>02_pipeline</code> and validate it</span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

Engineering Development reruns the same `02_pipeline` using the authored Guardrails or a selected saved Data Contract version.

The pipeline evaluates the governed expectations against the real ETL and writes Guardrail Results, plus row-level results where applicable.

If the expectations do not yet work, the workflow returns to `01_governance` so Governance can refine the definition before Engineering validates it again.

</div>
</details>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">5</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Governance</span><span class="fabricops-step-title">Save the Data Contract, link the Data Agreement, test the saved version, then activate it</span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

Once the governed definition is ready, Governance uses `01_governance` to save an immutable Data Contract version for one canonical `table_id` under one exact Data Agreement version.

That saved immutable version captures the governed context for the table, including its Catalogue/schema, Enrichment, active Guardrails, governed usages, target load strategy and load-strategy parameters, and the relevant Data Agreement and Steward context.

Engineering Development selects and tests that exact saved version in `02_pipeline`. After governance sign-off, Governance activates the selected version in `01_governance` so Engineering Production is allowed to resolve it.

<!-- VIDEO SLOT: Data Agreement and Data Contract lifecycle -->

!!! important "Data Contract activation and pipeline promotion are separate"

    **Activate** in `01_governance` selects the saved Data Contract version that Production may resolve. FabricOps currently treats test and governance sign-off as workflow practice rather than a technical activation gate.

    **Promote** moves the validated `02_pipeline` notebook into Engineering Production using the organisation's deployment process.

</div>
</details>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">6</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Engineering Production</span><span class="fabricops-step-title">Promote <code>02_pipeline</code> and run with the active Data Contract</span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

Engineering promotes the validated `02_pipeline` into the Engineering Production workspace using the organisation's deployment process.

At runtime, the Production `02_pipeline` resolves the active Data Contract for each governed `table_id` and executes the pipeline against those saved immutable expectations.

</div>
</details>

<details class="fabricops-workflow-step" markdown>
<summary><span class="fabricops-step-number">7</span><span class="fabricops-step-heading"><span class="fabricops-step-role">Consumers</span><span class="fabricops-step-title">Use <code>99_explore</code> to consume approved Production data only</span></span><span class="fabricops-step-chevron"></span></summary>
<div class="fabricops-step-body" markdown>

Project-specific consumer workspaces use `99_explore` to read approved data from Engineering Production for Power BI, AI, data science, exploration, and other downstream project work.

Consumer workspaces do not recreate the Production pipeline or maintain their own Production copy of the engineering workflow. Engineering Production remains the trusted Production source.

<!-- VIDEO SLOT: Development to Production to Consumer -->

</div>
</details>

</div>

</div>

<div class="fabricops-section-block" markdown>

## The core loop: author, validate, save, test, activate

The heart of FabricOps is the iterative loop between Governance and Engineering Development:

```mermaid
flowchart TD
    AUTHOR["Author"] --> VALIDATE["Validate"] --> SAVE["Save Contract"] --> TEST["Test Saved Version"] --> ACTIVATE["Activate"] --> PROD["Production Resolves Active Contract"]
    VALIDATE -. "Fail · refine" .-> AUTHOR
    TEST -. "Fail · author and save new version" .-> AUTHOR

    classDef focal fill:#f2eff8,stroke:#6750a4,stroke-width:2px,color:#20242d;
    class SAVE,ACTIVATE focal;
```

The details live in the expandable workflow above. The key idea is simple: Governance authors the governed definition, Engineering validates it, Governance saves an immutable Data Contract version, Engineering tests that exact saved version, Governance activates the selected version, and Production resolves the active contract. Testing and governance sign-off are part of the recommended operating workflow; activation is not currently blocked by a recorded approval state.

<!-- VIDEO SLOT: Governance as Code / core loop -->

</div>

<div class="fabricops-section-block" markdown>

## Shared metadata carries the context

**The Data Catalogue sits at the centre of the FabricOps metadata model.**

![FabricOps metadata model](assets/fabricops-metadata-model.png)

Engineering and Governance write different metadata around the same governed `table_id` in the shared Metadata Lakehouse. Engineering records technical observations such as Catalogue, Profile, and Lineage context. Governance reads that context and adds Enrichment, Guardrails, Data Agreements, and Data Contracts.

The important point is not the number of metadata tables. It is that Governance and Engineering work from the same structured context instead of maintaining separate copies of the definition.

<!-- VIDEO SLOT: Shared metadata model -->

For exact table schemas, ownership, and field definitions, use the [Metadata Tables reference](reference/metadata.md).

</div>

<div class="fabricops-section-block" markdown>

## Where to go next

- **Run the workflow yourself:** [FabricOps Guided Demo](guided-demo.md)
- **Understand the engineering choices:** [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md)
- **Inspect the shared metadata model:** [Metadata Tables](reference/metadata.md)
- **Browse reusable notebook-facing functions:** [FabricOps Functions](reference/index.md)
- **Download the notebooks:** [Notebook Templates](notebook-templates.md)

</div>