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

If you have watched the FabricOps overview video, this page is the same story with more depth. It explains the operating model and why the pieces fit together. The [Guided Demo](guided-demo.md) is where you actually configure and run the workflow.

<div class="fabricops-section-block" markdown>

## What problem is FabricOps solving?

**Microsoft Fabric gives the platform. FabricOps gives the operating practice.**

Fabric already gives teams notebooks, Lakehouses, Warehouses, pipelines, environments, AI capabilities, and many other building blocks. The harder question is how a team uses those building blocks repeatedly without every project inventing a different engineering and governance pattern.

FabricOps packages that operating pattern around four reusable notebooks:

| Notebook | Role |
| --- | --- |
| [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) | Defines the active environment and configured Fabric stores. |
| [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_governance.ipynb) | Authors the governance context and versioned Data Contracts. |
| [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) | Performs project-specific engineering, records technical metadata, and enforces governed expectations. |
| [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb) | Lets project-specific workspaces consume approved Production data without recreating the Production engineering workflow. |

The notebooks are supported by the FabricOps package: reusable public functions and widgets provide the repeatable pieces, while the project keeps its own transformation logic.

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

The result is a standardized flow from **configuration → engineering → governance → validation → Production → consumption**, rather than a collection of disconnected notebooks.

</div>

<div class="fabricops-section-block" markdown>

## How does FabricOps know where my data lives?

**FabricOps is configuration-driven: environment-specific Fabric resources are resolved through `00_env_config` instead of being scattered through pipeline code.**

`00_env_config` defines the active environment and the logical Fabric stores available to the workflow. Public FabricOps functions consume that configuration and resolve the physical Fabric item or path they need at runtime.

```text
logical Fabric store
        ↓
00_env_config
        ↓
FabricOps public function
        ↓
resolved Lakehouse / Warehouse / configured Fabric resource
```

That separation matters when the same engineering pattern moves between Development and Production. The pipeline should express *what* it wants to read or write; environment configuration determines *where* that resource lives.

The same configuration surface can also carry project-controlled options used by the FabricOps workflow, such as governance authoring settings. The goal is not to hide project logic in configuration. It is to keep environment-specific identities and reusable operating settings out of the ETL implementation.

??? info "Read more: why this matters for promotion"

    Engineering Development and Engineering Production can use the same logical pipeline structure while resolving different configured Fabric resources. Promotion therefore does not require rewriting paths throughout `02_pipeline`.

    The [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md#config-driven-engineering) contains the deeper configuration and I/O design.

</div>

<div class="fabricops-section-block" markdown>

## How does Engineering actually run?

**`02_pipeline` keeps the project-specific ETL visible while FabricOps supplies the reusable operating foundations around it.**

At a high level, an engineering run follows the same recognizable shape:

```text
Read → Transform → Profile / Catalogue → Validate Guardrails → Write
```

The transformation itself remains project-specific. FabricOps standardizes the surrounding concerns: configured I/O, table identity, metadata capture, profiling, Lineage, governed validation, and the hand-off into Production.

Each governed target is anchored by a canonical `table_id`. That identity connects what Engineering observes about a physical table with the governance definition that will later be authored for it.

Engineering records technical context such as the **Data Catalogue**, **Data Profiled** results, optional **Data Profiled Frequency**, **Data Lineage**, source observations, and Guardrail Results. Those records are not a second copy of the business data; they are the context that lets FabricOps reason consistently about the governed asset.

??? info "Read more: what FabricOps standardizes around your ETL"

    FabricOps is code-first and notebook-first: governed transformation logic stays explicit and reviewable in `02_pipeline`.

    A pipeline may read multiple upstream sources, but the governed write boundary is intentionally clear so FabricOps can associate the resulting table, observations, Lineage, and Data Contract with one canonical target identity.

    For the detailed engineering decisions, including load strategies, Medallion usage, failure-safe processing, and full versus incremental processing, use the [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md).

</div>

<div class="fabricops-section-block" markdown>

## Does PySpark-first mean Spark for everything?

**No. FabricOps is PySpark-first at the notebook workflow level, but it should execute expensive work close to the data when another engine is materially more efficient.**

For Lakehouse sources, PySpark is the natural path. FabricOps reads through its public I/O surface into a Spark DataFrame, after which the pipeline can transform, profile, and validate the data in the normal PySpark workflow.

```text
Lakehouse → public FabricOps read → PySpark DataFrame → ETL / profile / checks
```

If the pipeline already has a DataFrame, the same DataFrame-oriented workflow can continue without creating another source-specific programming model.

Warehouse sources are different. A large Warehouse table should not be pulled wholesale into Spark merely to compute profile statistics that the Warehouse engine can calculate more efficiently itself. For heavy operations such as large-scale profiling, FabricOps can use SQL pushdown so filtering, aggregation, counts, ranges, or similar work happens in the Warehouse first and only the required result is materialized for the notebook workflow.

```text
Warehouse → SQL pushdown → reduced / aggregated result → DataFrame when needed
```

The principle is therefore **PySpark-first, not Spark-only**. Lakehouse work naturally stays in Spark; Warehouse work can use T-SQL close to the data when moving the full source into Spark would be unnecessarily expensive.

??? info "Read more: why SQL pushdown matters"

    The cost becomes visible on large Warehouse tables. Rendering millions of Warehouse rows into Spark just to calculate summary statistics creates data movement and memory work that is often unnecessary. SQL pushdown lets the Warehouse perform the heavy calculation and return the smaller result required by the pipeline.

    This is an execution optimization, not a second FabricOps operating model. The same pipeline still resolves configuration, identifies the same governed tables, produces the same metadata context, and participates in the same Data Contract lifecycle.

</div>

<div class="fabricops-section-block" markdown>

## Where does Governance enter the engineering flow?

**Engineering first makes the governed asset observable; Governance then turns that context into an explicit Data Contract.**

Engineering Development produces the table and records what FabricOps can observe about it. Governance works from the same `table_id`, Data Catalogue, profile, and related technical context rather than authoring rules against an unrelated document.

```text
Engineering output
      ↓
Data Catalogue + Profile + Lineage + observations
      ↓
canonical table_id
      ↓
Governance authors a Data Contract
```

Before the contract is authored, `01_governance` can also establish **Data Stewards** and the **Data Agreement** that describes the governed sharing context between provider and recipient: ownership, purpose, approved usage, validity, and related agreement-level information.

FabricOps can optionally use Microsoft Fabric AI Functions to propose descriptions and information classifications from Catalogue and profiling context. Those suggestions remain editable and require Governance review; AI assistance does not replace the governance decision.

</div>

<div class="fabricops-section-block" markdown>

## What is a Data Contract in FabricOps?

**The Data Contract is the versioned governance definition for a governed table, not passive documentation beside the pipeline.**

Governance selects the `table_id` and authors a table-centric Data Contract in `01_governance`. The contract brings together the definition Engineering is expected to run against, including:

- **Enrichment** for descriptive table and column metadata and information classification
- **Guardrails** for enforceable expectations such as schema, freshness, Source Stability, Data Quality, and Sensitive Data requirements
- the governed target processing definition, including its load strategy
- the logical notebook ownership needed to keep the governed write relationship unambiguous

Governance reviews that definition and freezes an immutable version for Development validation.

The important point is what happens next: **Engineering selects that frozen contract and FabricOps check functions enforce its Guardrails against the real pipeline.** Guardrails can continue with a warning or block governed write continuation according to the authored action.

```text
Governance authors
      ↓
Data Contract version
      ↓
Freeze
      ↓
Engineering selects
      ↓
FabricOps check functions enforce Guardrails
      ↓
Guardrail Results
```

That is the core **Governance as Code** idea in FabricOps. Governance definitions are connected to executable engineering behavior through the Data Contract rather than remaining a separate policy document.

??? info "Read more: what belongs to Enrichment and Guardrails"

    **Enrichment** is descriptive. It helps people and downstream systems understand what the table and columns mean and how the information is classified.

    **Guardrails** are enforceable expectations. Examples include schema expectations, freshness, Source Stability, Data Quality, and Sensitive Data handling. A Guardrail can use a **Warn** or **Block** action.

    Freshness asks whether incoming source data is recent enough. Source Stability asks whether data already observed by the pipeline changed unexpectedly. The target load strategy determines whether such historical change is compatible with the governed processing definition.

??? info "Read more: why freeze before activation"

    Authoring and activation are deliberately separate Governance decisions. A frozen version gives Engineering Development an immutable definition to test. If the contract needs refinement, Governance authors another version and Engineering validates again.

    Only after the selected frozen version has been tested does Governance explicitly link the exact Data Agreement version and activate the contract for Production.

</div>

<div class="fabricops-section-block" markdown>

## Why do Governance and Engineering loop before Production?

**Because a governed expectation should be tested against the real engineering implementation before it becomes the active Production definition.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

The loop is easier to understand as one story:

1. Governance establishes the Data Stewards and Data Agreement.
2. Engineering Development builds the ETL, produces the governed table, and records Catalogue, profiling, Lineage, and runtime observations.
3. Governance selects the `table_id`, authors the Data Contract, and freezes a version.
4. Engineering Development selects that frozen version and validates its Guardrails against the real pipeline.
5. If the definition needs refinement, Governance and Engineering repeat the author-and-validate loop.
6. Governance links the tested contract to the Data Agreement and activates it.
7. Engineering promotes the validated `02_pipeline` and Production runs against the active contract.

This is not Governance handing Engineering a document once. It is a controlled feedback loop between what Governance expects and what Engineering actually observes and executes.

??? info "Read more: how Development and Production resolve contracts"

    Development uses notebook Lineage to discover linked `table_id` values and lets the developer select one exact frozen contract version for each governed table being validated.

    Production uses the same governed identities but removes manual version choice: each linked `table_id` must resolve to exactly one active contract. Zero or multiple active versions fail resolution rather than silently choosing one.

??? info "Read more: Source Observation and successful writes"

    Source Observation records relationship-scoped evidence around the logical notebook, source `table_id`, and target `table_id`. A successful physical target write advances the accepted committed observation and successful target Lineage. A failed write does not advance that accepted baseline.

    This keeps runtime evidence aligned with what was actually written rather than claiming a successful lineage or observation state before the governed output exists.

</div>

<div class="fabricops-section-block" markdown>

## What changes when the pipeline reaches Production?

**The operating pattern does not get rebuilt for Production. The validated pipeline is promoted and resolves Production configuration plus active governance at runtime.**

Engineering promotes the validated `02_pipeline` into the Engineering Production workspace using the organisation's deployment process. Production resolves its own configured Fabric stores through `00_env_config`, discovers the governed `table_id` values through the pipeline's Lineage, and resolves the single active Data Contract for each linked table.

```text
validated 02_pipeline
        +
Production 00_env_config
        +
active Data Contract(s)
        ↓
governed Production run
```

The contract and pipeline remain separate controls. **Activate** determines which Data Contract version Production may resolve. **Promote** moves the validated engineering implementation into Production. FabricOps keeps those decisions explicit rather than treating a notebook deployment as governance approval.

</div>

<div class="fabricops-section-block" markdown>

## How do project teams consume the result?

**Project-specific consumer workspaces consume approved Production outputs instead of recreating the Production engineering workflow.**

`99_explore` is the reusable read-only exploration entry point. A project can use approved Production data for Power BI, AI, data science, exploration, and other downstream work while Engineering Production remains the trusted source.

The consumer workspace does not need its own copy of the governed ETL just to use the result. This keeps the responsibility clear: Engineering produces the approved physical output; project-specific consumers use it.

</div>

<div class="fabricops-section-block" markdown>

## Where is the shared governance and engineering state kept?

**The Metadata Lakehouse carries the shared FabricOps context, with a clear ownership boundary between Governance definitions and Engineering/runtime evidence.**

![FabricOps metadata model](assets/fabricops-metadata-model.png)

Governance writes authoritative definitions in the `governance` schema. Engineering/runtime writes discovered metadata, execution observations, and results in the `engineering` schema. Engineering can read Governance definitions during pipeline execution without taking ownership of them.

The governed output table itself is project-owned physical data rather than FabricOps metadata. Optional support data such as Data Quality failed rows or Sensitive Data token mappings remains caller-owned; FabricOps does not automatically turn failing business rows into metadata records or prescribe a mandatory persistence location for that support data.

??? info "Read more: why table_id matters"

    `table_id` anchors the governed data asset across the workflow. Engineering metadata describes that asset directly. The Data Contract binds the Governance definition to the same asset, and contract-owned Enrichment and Guardrails resolve through the selected contract version.

    `METADATA_GUARDRAIL_RESULTS` stores runtime summaries and continuation decisions, not copies of the failing business rows. For exact schemas, ownership, and field definitions, use the [Metadata Tables reference](reference/metadata.md).

</div>

<div class="fabricops-section-block" markdown>

## So what is the complete FabricOps story?

**Configure once per environment, engineer against reusable foundations, observe the data, turn those observations into a versioned Data Contract, enforce that contract in code, activate the tested definition, promote the same engineering pattern to Production, and let projects consume only the approved output.**

```text
Configure
   ↓
Engineer + Observe
   ↓
Author Data Contract
   ↓
Freeze ↔ Validate
   ↓
Link + Activate
   ↓
Promote + Run Production
   ↓
Consume approved output
```

That is the operating practice the overview video introduces. This page explains how the pieces connect; the Guided Demo shows you how to perform the workflow yourself.

</div>

<div class="fabricops-section-block" markdown>

## Where to go next

- **Run the workflow yourself:** [FabricOps Guided Demo](guided-demo.md)
- **Understand the engineering choices:** [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md)
- **Inspect the shared metadata model:** [Metadata Tables](reference/metadata.md)
- **Browse reusable notebook-facing functions:** [FabricOps Functions](reference/index.md)
- **Download the notebooks:** [Notebook Templates](notebook-templates.md)

</div>
