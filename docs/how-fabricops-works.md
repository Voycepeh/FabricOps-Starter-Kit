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
| `00_env_config` | Defines the active environment and the configured Fabric items used by the workflow. |
| `01_governance` | Creates Data Stewards and Data Agreements, enriches governed tables, defines Guardrails, and manages Data Contract versions. |
| `02_pipeline` | Performs project-specific engineering, records technical metadata, validates governed expectations, and runs the governed Production pipeline. |
| `99_explore` | Lets project-specific consumer workspaces use approved Production data without recreating the Production engineering workflow. |

For the deeper engineering reasoning behind `00_env_config`, FabricOps I/O functions, Lakehouse/Warehouse choices, PySpark, incremental processing, and the detailed `02_pipeline` structure, use the [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md).

</div>

<div class="fabricops-section-block" markdown>

## The Governance and Engineering loop

![FabricOps role workflow](assets/fabricops-role-workflow.png)

FabricOps deliberately loops between Governance and Engineering Development before the approved pipeline runs in Production.

<!-- VIDEO SLOT: Governance and Engineering loop -->

### 1. Governance establishes the sharing relationship

In `01_governance`, Governance creates the provider and recipient **Data Stewards** and a **Data Agreement** between them.

The Data Agreement establishes the governed sharing context: who is providing and receiving the data, the business purpose, approved usages, validity, and other agreement-level governance information.

### 2. Engineering Development builds the initial pipeline

Engineering Development uses `02_pipeline` to read one or more configured sources, perform project-specific transformations, and write governed target tables to the configured Lakehouse or Warehouse.

Each governed target is identified by a canonical `table_id`. Engineering then records the technical context around that table, including:

- Data Catalogue metadata
- Data Profiled records
- Data Profiled Frequency where applicable
- Data Lineage

The `table_id` is the shared identity that lets the rest of the FabricOps workflow refer to the same governed table.

### 3. Governance turns the Engineering context into governed expectations

Back in `01_governance`, Governance uses the same `table_id` to read the Catalogue and Profile information produced by Engineering.

Governance can then add:

- **Enrichment**, such as business meaning, sensitivity classification, PII classification, and other table- or column-level context
- **Guardrails**, such as schema, freshness, and Data Quality expectations
- the governed target **load strategy** and its parameters, such as overwrite, append, SCD1, or SCD2, as part of the table definition that will be frozen into the Data Contract

At this stage, Governance is assembling the governed definition that will become the table-level Data Contract.

### 4. Engineering Development validates the governed definition

The same `02_pipeline` runs again with the authored Guardrails or a selected frozen Data Contract.

Engineering evaluates the governed expectations against the real pipeline and writes Guardrail Results, plus row-level results where applicable.

If the expectations do not yet work, Governance and Engineering iterate: Governance refines the definition and Engineering validates it again.

### 5. Governance freezes, tests, and activates the Data Contract

Once the governed definition is ready, Governance freezes an immutable Data Contract version for one canonical `table_id` under one exact Data Agreement version.

That frozen version includes the approved governed context for the table, including its Catalogue/schema, Enrichment, active Guardrails, governed usages, target load strategy and load-strategy parameters, and the relevant Data Agreement and Steward context.

Engineering Development tests the frozen version. After governance sign-off, Governance activates the approved frozen version that Production is allowed to resolve.

<!-- VIDEO SLOT: Data Agreement and Data Contract lifecycle -->

!!! important "Activation and promotion are separate"

    **Activate** selects the approved frozen Data Contract version that Production may resolve.

    **Promote** moves the validated `02_pipeline` into Engineering Production using the organisation's deployment process.

### 6. Engineering Production runs the governed pipeline

The validated `02_pipeline` is promoted into Engineering Production through the organisation's deployment process.

At runtime, the Production pipeline resolves the active Data Contract for each governed table and runs against those frozen expectations.

### 7. Consumers use Production only

Project-specific consumer workspaces use `99_explore` to consume approved data from Engineering Production for Power BI, AI, data science, exploration, and other downstream project work.

Consumer workspaces do not recreate the Production pipeline or maintain their own Production copy of the engineering workflow. Engineering Production remains the trusted Production source.

<!-- VIDEO SLOT: Development to Production to Consumer -->

</div>

<div class="fabricops-section-block" markdown>

## The core loop: author, validate, approve

The heart of FabricOps is the iterative loop between Governance and Engineering Development:

```text
Governance authors / refines the governed definition
                    ↓
Engineering Development validates it in 02_pipeline
                    ↓
       Do the governed expectations pass?
          ↙                         ↘
        No                           Yes
        ↓                             ↓
Governance refines              Freeze contract
        ↑                             ↓
        └──────── validate again ← Test frozen version
                                      ↓
                                   Activate
                                      ↓
                         Engineering Production
```

This is how FabricOps makes Governance executable: Governance decisions are captured as structured metadata, Guardrails, and Data Contracts that Engineering can directly resolve and validate rather than leaving them only in documentation.

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
