# Unit 1: Understand the `02_pipeline` template

**`02_pipeline` is the reusable Engineering template for a complete FabricOps pipeline run.**

You do not assemble the FabricOps lifecycle by calling every framework function yourself. The template already provides the standard structure around your project-specific processing logic.

FabricOps deliberately uses the notebook as the visible governed engineering unit, while native Fabric Pipelines can orchestrate it when scheduling or dependencies are required. Read more in [Notebook first — vs Pipeline vs Dataflow Gen2](../../reference/engineering-cheat-sheet.md#notebook-first).

## What the template does

The notebook follows one visible engineering flow:

```text
Environment → Read → Transform → Write
```

FabricOps supplies the surrounding operational behaviour such as configured IO, profiling, metadata registration, lineage, governed processing preparation, and target-backed incremental state where those capabilities are configured.

In this notebook, **Read**, **Transform**, and **Write** name the user-facing stages. **Source** and **target** remain technical terms for datasets and FabricOps configuration, processing, and lineage relationships used within those stages.

Your project mainly supplies:

1. the Read configuration,
2. the transformation logic,
3. the Write configuration,
4. the processing strategy when incremental behaviour is required.

## Pipeline design rule

A FabricOps governed pipeline may consume one or many upstream sources, but it publishes exactly one governed target table.

Multi-target fan-out is technically possible through the individual writer functions, but the governed pipeline pattern deliberately avoids it because independent physical writes can partially succeed. If another persisted output is required, create a separate downstream pipeline.

Keep dependencies directional and acyclic. A pipeline should not use its own target as an engineer-authored source. Persisted intermediate stages should be explicit outputs of upstream pipelines and inputs to separate downstream pipelines.

```mermaid
flowchart LR
    A["Source table A"] --> P1["02_pipeline"]
    B["Source table B"] --> P1
    C["Reference table"] --> P1
    P1 --> T1["Governed target A"]

    T1 --> P2["Downstream 02_pipeline"]
    D["Another source"] --> P2
    P2 --> T2["Governed target B"]

    P1 -.-> N["Why one target?<br/>Independent writes can partially succeed.<br/>No notebook-level rollback."]
```

## Why Guardrails are not required yet

At this point in the learning path, no Guardrails or Data Contract have been created for the demo table.

That is intentional. The same `02_pipeline` template can complete the pipeline without those enforcement layers. In later modules you will add governance around this same pipeline rather than build a different pipeline.

```text
Step 2: run the pipeline and write Catalogue / Profiled / Lineage metadata
        ↓
Step 3: select table_id; author Enrichment + Guardrails; freeze the version
        ↓
Step 4: select the frozen version and validate it in the same pipeline
        ↓
Step 5: link the tested version to the Data Agreement and activate it
        ↓
Step 6: run the same pipeline in Production against the active contract
```

## What stays project-owned

FabricOps does not hide business transformations. Joins, filters, derivations, aggregations, enrichment, and reshaping remain visible in the **Transform** section of the notebook.

This separation lets the framework standardise the pipeline boundary while keeping business logic explicit and reviewable.

**Previous:** [Module 2 overview](../02-run-pipeline.md)  
**Next:** [Unit 2: Run the baseline ETL](run-baseline-etl.md)
