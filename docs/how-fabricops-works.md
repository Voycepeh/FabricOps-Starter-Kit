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

The FabricOps overview video introduces the story. This page goes deeper into how the pieces fit together and why the workflow is structured this way.

[Want to run it yourself? Follow the Guided Demo.](guided-demo.md)

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

### See the whole operating model

**Questions this diagram answers:**

- Where do Governance, Engineering Development, Engineering Production, and project-specific consumers sit?
- Which notebooks belong in each workspace?
- Where does the shared Metadata Lakehouse fit?
- What is promoted to Production?
- Where are approved outputs consumed from?

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

Read it from top to bottom. Governance defines and versions governed expectations. Engineering Development builds and validates the implementation. The validated `02_pipeline` is promoted to Engineering Production, where active contracts are resolved and governed outputs are produced. Project-specific consumers then use approved Production data through `99_explore`.

The rest of this page zooms into that picture without changing the story.

</div>

<div class="fabricops-section-block" markdown>

## How do code-first pipelines work across Fabric stores?

**A Fabric notebook is very convenient when everything lives in one attached Lakehouse or Warehouse. Code-first ETL becomes harder when the same pipeline needs to move data across several Fabric stores and environments.**

With one default attached store, Fabric already gives a very natural notebook experience. Files and tables are easy to browse, reference, and use from the notebook without repeatedly describing where they live.

Real ETL rarely stays inside one store. A pipeline commonly reads from one data store, transforms the data, and writes to another. It may also need to move between Development and Production without changing the engineering logic.

At the time of writing, Fabric does not provide the same simple notebook-level abstraction for a code-first pipeline that needs to resolve two or more arbitrary Fabric stores. Without another layer, projects tend to repeat workspace IDs, item IDs, ABFSS paths, or connection details throughout their code. That makes otherwise reusable pipeline logic environment-specific.

FabricOps solves that problem with **configuration-driven engineering**. The idea is inspired by the configuration files commonly used in software engineering: give a resource a stable logical name once, then let application code refer to that name instead of embedding its physical location everywhere.

In FabricOps, `00_env_config` is that configuration surface. You define the Fabric stores available in the current environment once. Pipeline code then passes the configured store name into FabricOps public functions, and FabricOps resolves the physical Fabric resource for you.

```text
store name used by 02_pipeline
          ↓
      00_env_config
          ↓
resolve Fabric store type + physical location
          ↓
Lakehouse                          Warehouse
   ↓                                  ↓
PySpark / ABFSS resolution        SQL pushdown where appropriate
          \                         /
           → PySpark DataFrame → transformations
```

For a **Lakehouse**, FabricOps resolves the configured store to the appropriate Fabric/ABFSS location and uses the PySpark path naturally supported by Fabric notebooks.

For a **Warehouse**, FabricOps can push expensive source-side work down to SQL instead of pulling the whole Warehouse table into Spark unnecessarily. This matters especially for operations such as large-table profiling, filtering, aggregation, counts, and ranges.

Once the data reaches the transformation stage, the engineering model stays simple: **project transformations are written in PySpark**. FabricOps therefore remains PySpark-first without forcing every source operation through Spark when the source engine can do the work more efficiently.

The same logical store names can then resolve to different physical Fabric resources in Development and Production. `02_pipeline` stays focused on engineering logic while `00_env_config` owns the environment-specific wiring.

??? info "Read more: why SQL pushdown matters"

    Pulling millions of Warehouse rows into Spark only to calculate summary statistics creates avoidable data movement and memory work. SQL pushdown performs that work where the data already lives and returns only the result the notebook needs.

    This is an execution optimization, not a second FabricOps workflow. The same pipeline still resolves configuration, produces the same governed metadata, and participates in the same Data Contract lifecycle.

    [How does configuration-driven resolution work in detail?](reference/engineering-cheat-sheet.md#config-driven-engineering)

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

    [How do load strategies, Medallion layers, failure-safe processing, and incremental loads work?](reference/engineering-cheat-sheet.md)

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

??? info "Read more: what exactly is authored and activated?"

    ```mermaid
    flowchart LR
        subgraph AUTHOR[Author]
            TABLE["table_id"] --> CONTRACT["Data Contract version"]
            CONTRACT --> ENRICH["Enrichment<br/>Description + Classification"]
            CONTRACT --> RULES["Guardrails<br/>Schema · Freshness · Source Stability<br/>Data Quality · Sensitive Data"]
            CONTRACT --> SNAPSHOT["Immutable schema / processing definition"]
        end
        subgraph ACTIVATE[Activate]
            TESTED["Tested frozen Data Contract version"] --> LINK["Explicit linkage"]
            AGREEMENT["Data Agreement version"] --> LINK
            LINK --> ACTIVE["ACTIVE for Production"]
        end
    ```

    **Enrichment** is descriptive. It helps people and downstream systems understand what the table and columns mean and how the information is classified.

    **Guardrails** are enforceable expectations. Examples include schema expectations, freshness, Source Stability, Data Quality, and Sensitive Data handling. A Guardrail can use a **Warn** or **Block** action.

    Authoring and activation are deliberately separate Governance decisions. A frozen version gives Engineering Development an immutable definition to test. Only after the selected frozen version has been tested does Governance explicitly link the exact Data Agreement version and activate the contract for Production.

</div>

<div class="fabricops-section-block" markdown>

## Why do Governance and Engineering loop before Production?

**Because a governed expectation should be tested against the real engineering implementation before it becomes the active Production definition.**

### See the Governance and Engineering loop

**Questions this diagram answers:**

- What happens first in Governance and Engineering Development?
- Where is the Data Contract authored?
- Why do steps 3 and 4 repeat?
- What is activated before Production runs?
- What is promoted into Engineering Production?
- Where do consumers enter the flow?

![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read the numbered stages as one controlled feedback loop:

1. Governance establishes the Data Stewards and Data Agreement.
2. Engineering Development builds the ETL, produces the governed table, and records Catalogue, profiling, Lineage, and runtime observations.
3. Governance selects the `table_id`, authors the Data Contract, and freezes a version.
4. Engineering Development selects that frozen version and validates its Guardrails against the real pipeline.
5. When the definition needs refinement, Governance and Engineering repeat the author-and-validate loop.
6. Governance links the tested contract to the Data Agreement and activates it.
7. Engineering promotes the validated `02_pipeline`, Production runs against the active contract, and consumers use the approved result.

This is not Governance handing Engineering a document once. It is a controlled feedback loop between what Governance expects and what Engineering actually observes and executes.

??? info "Read more: how Development and Production resolve contracts"

    ```mermaid
    flowchart LR
        NB["notebook_id"] --> LIN["METADATA_DATA_LINEAGE"]
        LIN --> T["linked table_id values"]
        T --> DEV["Development<br/>select frozen version per table_id"]
        T --> PROD["Production<br/>resolve active version per table_id"]
    ```

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

### See the metadata ownership model

**Questions this diagram answers:**

- Which metadata belongs to the Governance schema?
- Which metadata is written by Engineering/runtime?
- How does `table_id` connect the governed asset across both sides?
- How do Data Contracts own Enrichment and Guardrails?
- Where do profiling, Lineage, Source Observation, access, and Guardrail Results live?

![FabricOps metadata model](assets/fabricops-metadata-model.png)

The purple Governance area contains authoritative definitions: Data Stewards, Data Agreements, Data Contracts, Enrichment, and Guardrails. The blue Engineering area contains what Engineering discovers or records while the workflow runs: Catalogue, profiles, Lineage, Source Observation, access, and Guardrail Results.

The bridge between those areas is the governed asset identity. `table_id` anchors the physical table in Engineering metadata and lets the selected Data Contract attach the governed definition to that same asset.

Engineering can read Governance definitions during pipeline execution without taking ownership of them. The governed output table itself is project-owned physical data rather than FabricOps metadata.

??? info "Read more: what is not stored as FabricOps metadata"

    Optional support data such as Data Quality failed rows or Sensitive Data token mappings remains caller-owned. FabricOps does not automatically turn failing business rows into metadata records or prescribe a mandatory persistence location for that support data.

    `METADATA_GUARDRAIL_RESULTS` stores runtime summaries and continuation decisions, not copies of the failing business rows.

    [What exactly is stored in each metadata table?](reference/metadata.md)

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

That is the operating practice the overview video introduces. This page explains how the pieces connect.

[How do I run the complete workflow myself?](guided-demo.md)

</div>

<div class="fabricops-section-block" markdown>

## Where to go next

- [How do I run the workflow myself?](guided-demo.md)
- [Why does FabricOps make these engineering choices?](reference/engineering-cheat-sheet.md)
- [What exactly is stored in FabricOps metadata?](reference/metadata.md)
- [What does each FabricOps function do?](reference/index.md)
- [Where are the reusable notebook templates?](notebook-templates.md)

</div>