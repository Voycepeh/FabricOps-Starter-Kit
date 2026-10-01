# How FabricOps works

**Understand the end-to-end operating model: how Governance and Engineering work together from contract authoring through validation, activation, promotion, and Production use.**

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

.md-typeset .fabricops-big-picture {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.md-typeset .fabricops-big-picture__visual img {
  width: 100%;
  height: auto;
  margin: 0;
}

.md-typeset .fabricops-assets-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.md-typeset .fabricops-asset {
  padding: 1rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.4rem;
  background-color: var(--md-default-bg-color);
}

.md-typeset .fabricops-asset > :first-child {
  margin-top: 0;
}

.md-typeset .fabricops-asset > :last-child {
  margin-bottom: 0;
}

@media (max-width: 1200px) {
  .md-typeset .fabricops-big-picture {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .md-typeset .fabricops-assets-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="fabricops-section-block" markdown="1">

## The Big Picture

<div class="fabricops-big-picture" markdown="1">

<div class="fabricops-big-picture__visual" markdown="1">

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

</div>

<div class="fabricops-big-picture__copy" markdown="1">

**Microsoft Fabric gives the platform. FabricOps gives the operating practice.**

Fabric already gives teams notebooks, Lakehouses, Warehouses, pipelines, environments, AI capabilities, and many other building blocks. The harder question is how a team uses those building blocks repeatedly without every project inventing a different engineering and governance pattern.

**How Governance and Engineering work hand in hand within Microsoft Fabric**

- **Microsoft Fabric building blocks**  
  FabricOps operates inside Microsoft Fabric using its native building blocks: Workspaces to separate responsibilities and environments, Notebooks running PySpark for engineering and governance logic, Deployment Pipelines for promotion, Lakehouses and Warehouses for Bronze, Silver, Gold, and Metadata storage, and Fabric environments and object configuration to keep Development and Production aligned.

- **Governance Workspace**  
  Owns the governed definition of the data. `00_env_config` stores the Governance environment configuration and Fabric object paths. `01_governance` manages Data Agreements, Stewards, Enrichment, Guardrails, Data Contracts, and access metadata.

- **Shared Metadata Lakehouse**  
  Lives in the Governance Workspace and connects Governance with Engineering. It stores the shared FabricOps metadata used across the lifecycle, including Catalogue, profiling, contracts, lineage, Guardrail Results, and related governance metadata.

- **Engineering Development Workspace**  
  This is where the engineering implementation is built and validated. Its `00_env_config` points to the Development Lakehouses, Warehouses, schemas, and other Fabric object paths. `02_pipeline` reads and profiles data, applies transformations and audit columns, validates Guardrails, writes outputs, and records engineering metadata.

- **Engineering Production Workspace**  
  Runs the same validated `02_pipeline` using Production configuration. Its own `00_env_config` points to the equivalent Production Lakehouses, Warehouses, schemas, and Fabric object paths, while the pipeline resolves the activated Data Contract and produces governed Production outputs.

- **Aligned environments and promotion**  
  Development and Production keep the same logical Bronze, Silver, and Gold architecture, whether those stores are implemented as Lakehouses or Warehouses. The physical Fabric objects differ by environment, but their roles and structure stay aligned 1:1. Once `02_pipeline` is validated in Development against the frozen Data Contract, that validated notebook is promoted to the Engineering Production Workspace through the deployment flow.

- **Project-Specific Consumer Workspace**  
  Consumers receive approved Production access through native Fabric controls and use the Fabric interface appropriate to their work. FabricOps does not require a dedicated exploration notebook after the governed output is published. Data Agents provide the first productized FabricOps consumption path; other BI, AI, analytics, and data-science consumers can use the approved Production data directly.



</div>

</div>

</div>

<div class="fabricops-section-block" markdown="1">

## The Governance ↔ Engineering Cycle

![FabricOps Governance and Engineering cycle](assets/fabricops-roles.png)

**FabricOps turns Governance and Engineering into one executable cycle around the same `table_id`.**

`02_pipeline` creates the Engineering side of the shared metadata: `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_DATA_LINEAGE`, and `METADATA_SOURCE_OBSERVATION`.

`01_governance` creates the Governance side: `METADATA_DATA_STEWARD`, `METADATA_DATA_AGREEMENT`, and the versioned `METADATA_DATA_CONTRACT`. Engineering selects that contract, validates and enforces its Guardrails, and records the outcomes in `METADATA_GUARDRAIL_RESULTS`.

If the implementation or governed definition needs refinement, Governance creates the next contract version and Engineering validates it again. Once the tested version is approved, Governance activates it for Production and the same `02_pipeline` runs against the active Data Contract.

**For the notebook-level implementation, browse the [FabricOps notebook templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks). For the schema, purpose, and relationships of each metadata table, see the [Metadata reference](reference/metadata.md).**

??? info "Implementation and metadata handoff"

    | What happens | Implementation | Metadata |
    | --- | --- | --- |
    | Establish Governance context | [`widget_render_data_steward()`](api/reference/widget_render_data_steward.md), [`widget_render_data_agreement()`](api/reference/widget_render_data_agreement.md) | `METADATA_DATA_STEWARD`, `METADATA_DATA_AGREEMENT` |
    | Register and profile the table | [`profile_table()`](api/reference/profile_table.md) | `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` |
    | Record pipeline state | [`pipeline_read()`](api/reference/pipeline_read.md), [`pipeline_write()`](api/reference/pipeline_write.md) | `METADATA_DATA_LINEAGE`, `METADATA_SOURCE_OBSERVATION` |
    | Author and activate the Data Contract | [`widget_data_contract()`](api/reference/widget_data_contract.md) | `METADATA_DATA_CONTRACT` |
    | Enforce Guardrails | [`check_schema()`](api/reference/check_schema.md), [`check_freshness()`](api/reference/check_freshness.md), [`check_source_drift()`](api/reference/check_source_drift.md), [`check_dq()`](api/reference/check_dq.md), [`check_sensitive_data()`](api/reference/check_sensitive_data.md) | `METADATA_GUARDRAIL_RESULTS` |

    `table_id` connects the physical table, Engineering observations, and governed definition.

    Some Guardrails also return caller-owned row-level support DataFrames. FabricOps does not persist these automatically: `check_dq()` can return `failed_values`, while `check_sensitive_data()` can return a token `support_mapping`. See the [Metadata reference](reference/metadata.md) for the full table schemas, relationships, access metadata, and runtime-output details.

</div>

<div class="fabricops-section-block" markdown="1">

## Data Contracts

**The Data Contract is the versioned, executable governance definition for one governed `table_id`.** It is assembled from the real Engineering metadata and the Governance decisions made against that asset, then stored as a single `contract_payload_json` manifest in `METADATA_DATA_CONTRACT`.

The manifest captures:

- **Contract identity and lifecycle** — `contract_id`, `contract_version`, and lifecycle status.
- **Table definition** — the governed `table_id`, schema/table identity, observed columns and data types from `METADATA_DATA_CATALOGUE`, plus the governed processing definition.
- **Enrichment** — reviewed table- and column-level descriptions, classifications, and table grain authored by Governance.
- **Guardrails** — the executable Schema, Freshness, Source Drift, Data Quality, and Sensitive Data expectations authored by Governance.

In other words, **Engineering supplies what physically exists; Governance adds what it means and what must be enforced.** Saving updates the mutable draft manifest. Freezing makes that version immutable. Activation selects the tested frozen version for Production and links it to the exact Data Agreement version.

??? example "What the JSON manifest looks like"

    ```json
    {
      "contract": {
        "contract_id": "...",
        "contract_version": 1,
        "status": "frozen"
      },
      "table": {
        "table_id": "...",
        "schema_name": "demo",
        "table_name": "orders",
        "columns": [
          {
            "column_id": "...",
            "column_name": "order_id",
            "data_type": "string"
          }
        ],
        "processing": {
          "load_strategy": "overwrite"
        }
      },
      "enrichment": {
        "table": [],
        "columns": []
      },
      "guardrails": []
    }
    ```

    The exact manifest grows with the Enrichment, Processing, and Guardrails authored for the table. See [METADATA_DATA_CONTRACT](reference/metadata/metadata_data_contract.md) for the persisted table schema.

[Explore Sensitive Data Classification & Treatment →](solutions/ai-assisted-data-contract-authoring.md)

[Explore Business Rules to Data Quality →](solutions/business-rules-to-data-quality.md)

</div>



<div class="fabricops-section-block" markdown="1">

## The 7-Step FabricOps Lifecycle

**The seven stages below are the core operating flow. They connect the Governance and Engineering responsibilities shown in the workflow image to the metadata written behind the scenes.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

| Step | What happens |
| --- | --- |
| **1. Establish Governance context** | Create Data Stewards and a Data Agreement. |
| **2. Build and run the ETL** | Choose the pipeline pattern for the workload and run the real Engineering Development flow. |
| **3. Author and freeze the Data Contract** | Select the real `table_id`, author Enrichment, Guardrails, and Processing, then freeze the contract version. |
| **4. Validate the frozen Data Contract** | Evaluate the exact frozen candidate against the real pipeline. |
| **5. Activate the Data Contract and promote** | Link the tested contract version to the Data Agreement, activate it for Production, then deploy the validated engineering artifact from Development to Production. |
| **6. Run the pipeline in Production and grant access** | Run the validated Production workflow, publish governed outputs, then grant approved consumers direct access through native Fabric permissions. |
| **7. Publish governed data to a Data Agent** | Turn approved Production tables and FabricOps context into a native Fabric Data Agent for consumption. |

**Steps 3 ↔ 4 are intentionally iterative.** Governance authors the next contract version; Engineering selects that immutable version and reruns the pipeline against it. The loop continues until the governed definition and the real engineering implementation agree.

[Run the full lifecycle yourself in the Guided Demo →](guided-demo.md)

??? info "Detailed lifecycle responsibilities"

    1. **Governance establishes the people and agreement context.** [`widget_render_data_steward()`](api/reference/widget_render_data_steward.md) writes Data Steward records, and [`widget_render_data_agreement()`](api/reference/widget_render_data_agreement.md) writes Data Agreement records.
    2. **Engineering Development builds the ETL and produces the governed table.** `02_pipeline` reads, transforms, writes, profiles, and records the technical context around the real table. [`profile_table()`](api/reference/profile_table.md) keeps the Data Catalogue and profiling metadata aligned with what Engineering actually produced.
    3. **Governance authors the Data Contract for that `table_id`.** [`widget_data_contract()`](api/reference/widget_data_contract.md) brings together Enrichment, Guardrails, and the governed processing definition for the table.
    4. **Engineering Development selects a contract version and validates the real pipeline.** [`widget_select_data_contract()`](api/reference/widget_select_data_contract.md) sets the selected contract per linked `table_id`, and the Guardrail functions execute its expectations against the real data flow.

        **Steps 3 ↔ 4 are intentionally iterative.** Governance authors the next contract version; Engineering selects that immutable version and reruns the pipeline against it. If the expectation needs refinement or the implementation does not satisfy the intended rule, the flow returns to Governance for another version and then back to Engineering for another validation run. The loop continues until the governed definition and the real engineering implementation agree.

    5. **Governance activates the tested definition, then Engineering promotes it to Production.** [`widget_data_contract()`](api/reference/widget_data_contract.md) links the exact Data Agreement version and tags one frozen Data Contract version as active for that `table_id`. Frozen versions stay frozen; activation does not change their governed JSON. Development can validate any frozen version. Production is strict: it must resolve exactly one frozen version with `is_active=true` for each linked `table_id`. After activation, the validated engineering artifact is deployed from Engineering Development to Engineering Production through the Fabric Deployment Pipeline.
    6. **Engineering runs the same workflow again in Production and hands off access.** The promoted `02_pipeline` resolves Production stores through `00_env_config`, automatically resolves the active Data Contract, applies the same Read → Transform → Write pattern and Guardrail functions, and publishes the governed output. Successful writes commit the associated runtime Lineage and Source Observation state. Approved consumers then receive access through native Fabric controls and can use standard Fabric interfaces directly.
    7. **FabricOps productizes the governed result through a Data Agent.** The Data Agent publishing path assembles the approved table context into native Data Agent instructions and configuration. The first implementation targets one table; explicit PK/FK relationship context extends the same pattern to multiple governed tables.

</div>

<div class="fabricops-section-block" markdown="1">

## Featured Solutions

- [Plug-and-Play Data Pipelines with Data Contract Enforcement](solutions/plug-and-play-data-pipelines.md)
- [Sensitive Data Classification & Treatment](solutions/ai-assisted-data-contract-authoring.md)
- [Generate Enforceable Data Quality Rules from Business Rules](solutions/business-rules-to-data-quality.md)
- [Scan Effective Data Access](solutions/effective-data-access.md)
- [Explore the Public Function Call Flow](function-call-graph.md)

## Read more documentation

- [Function Reference](reference/index.md)
- [Data Quality Rules](reference/dq-rules/index.md)
- [Metadata Tables](reference/metadata.md)
- [Glossary](glossary.md)

</div>
