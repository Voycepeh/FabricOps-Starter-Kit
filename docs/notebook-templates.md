# Notebook Templates

**FabricOps provides four editable Microsoft Fabric notebook templates that work together as one Governance and Engineering operating flow.**

[Open all notebook templates on GitHub](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks){ .md-button .md-button--primary }

```text
00_env_config
     ↓
01_governance ⇄ 02_pipeline
                     ↓
              Engineering Production
                     ↓
                 99_explore
```

`01_governance` owns the complete Governance lifecycle. There is no separate agreement or review notebook. `02_pipeline` is the repeatable Engineering unit and publishes one governed target per pipeline. `99_explore` is the read-only consumer and exploration surface for approved Production data.

<div class="template-list" markdown="1">

<div class="template-card" markdown="1">

## `00_env_config`

**Defines where the same FabricOps workflow runs.**

Use it to configure:

- Governance, Engineering Development, and Engineering Production workspaces
- logical Lakehouse and Warehouse targets such as `source`, `unified`, `product`, and `metadata`
- environment-specific workspace and item identities
- metadata routing
- audit and runtime settings
- configurable Governance and widget options

`02_pipeline`, `01_governance`, and `99_explore` reuse this configuration so notebooks do not need environment-specific Fabric item IDs or paths hard-coded throughout their logic.

[Open `00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `01_governance`

**Owns the complete Governance lifecycle around Engineering.**

Use it to:

- create Data Stewards and Data Agreements
- inspect Data Catalogue, Data Profiled, frequency, and Lineage context produced by Engineering
- select a governed `table_id`
- author descriptive Enrichment and enforced Guardrails
- define the governed target load strategy and parameters
- freeze an immutable table-centric Data Contract version
- after Development validation, link the tested frozen version to the required Data Agreement version
- activate the approved version for Production

The operating pattern is:

```text
Governance authors
      ↓
Engineering develops and records metadata
      ↓
Governance freezes a Data Contract
      ↓
Engineering selects and validates it
      ↓
Governance links the Data Agreement and activates
```

All of that Governance work stays in `01_governance`; the removed `03_review` workflow is no longer part of FabricOps.

[Open `01_governance.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_governance.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `02_pipeline`

**Runs the canonical governed Engineering workflow.**

The visible notebook stages are:

```text
0. Environment → 1. Data Contracts → 2. Read → 3. Transform → 4. Write
```

Use it to:

- initialise the active Fabric environment
- select frozen Data Contract versions in Development or resolve active versions automatically in Production
- read one or more configured Lakehouse or Warehouse sources
- observe sources and evaluate applicable source Guardrails
- profile and register complete physical source tables where appropriate
- keep project-specific PySpark transformation logic explicit in the Transform section
- prepare and validate one governed target
- apply the target's governed load strategy
- write the physical target
- commit successful source-observation baselines and target Lineage only after the physical write succeeds
- read the persisted target back and profile/register the complete stored result
- write Guardrail Results for governed validation

### One pipeline, one governed target

A single `02_pipeline` may read many upstream sources, but it publishes **one governed target table**. When another persisted output is required, create a downstream `02_pipeline` and use the first target as an upstream source.

This keeps failure boundaries clear and avoids independent multi-target writes leaving a notebook in a partial-success state.

Develop and validate `02_pipeline` in Engineering Development. After Governance activates the tested Data Contract, promote the validated notebook to Engineering Production. Production uses the same pipeline logic with Production `00_env_config` and automatically resolves the active contract context.

[Open `02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb){ .md-button }

</div>

<div class="template-card" markdown="1">

## `99_explore`

**Provides a read-only exploration and consumption surface over governed Production data.**

Use it to:

- discover and inspect approved Production datasets
- review FabricOps Catalogue, Profile, Lineage, Enrichment, Guardrail, and Guardrail Result context
- investigate data-quality issues
- test analysis ideas without changing the governed Engineering pipeline
- support Power BI, AI, analytics, and data science work in Project-Specific Consumer workspaces

`99_explore` does not write back to the main governed Lakehouses or Warehouses. Consumer workspaces consume approved data from Engineering Production rather than maintaining their own copy of the Production pipeline.

!!! note "Keep repeatable preparation in `02_pipeline`"

    `99_explore` is for discovery, analysis, and experimentation. Move preparation that must become stable, recurring, governed, or operational into a `02_pipeline`.

[Open `99_explore.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb){ .md-button }

</div>

</div>

## How the four notebooks fit together

```text
00_env_config
    provides environment-specific configuration

01_governance
    Author → Freeze
          ↓
02_pipeline in Development
    Select → Validate
          ↓
01_governance
    Link Data Agreement → Activate
          ↓
02_pipeline in Production
    Promote → Run Production
          ↓
99_explore
    Consume approved Production data
```

## Next step

Follow the [Guided Demo](guided-demo.md) through **Author → Freeze → Select → Validate → Link Data Agreement → Activate → Promote → Run Production**, then use `99_explore` for governed downstream consumption.
