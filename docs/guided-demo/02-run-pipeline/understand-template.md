# Unit 1: Understand the `02_pipeline` template

**`02_pipeline` is the reusable Engineering template for a complete FabricOps ETL run.**

You do not assemble the FabricOps lifecycle by calling every framework function yourself. The template already provides the standard structure around your project-specific ETL logic.

## What the template does

The notebook follows one visible engineering flow:

```text
Environment → Extract → Transform → Load
```

FabricOps supplies the surrounding operational behaviour such as configured IO, profiling, metadata registration, lineage, governed processing preparation, and checkpoint handling where those capabilities are configured.

Your project mainly supplies:

1. the source configuration,
2. the transformation logic,
3. the target configuration,
4. the processing strategy when incremental behaviour is required.

## Why Guardrails are not required yet

At this point in the learning path, no Guardrails or Data Contract have been created for the demo table.

That is intentional. The same `02_pipeline` template can complete the ETL without those enforcement layers. In later modules you will add governance around this same pipeline rather than build a different pipeline.

```text
Step 2: run ETL without authored Guardrails
        ↓
Step 3: define Guardrails from observed metadata
        ↓
Step 4: rerun the same ETL with Guardrails
        ↓
Step 5: freeze approved expectations into a Data Contract
        ↓
Step 6: run the same ETL in Production against the active contract
```

## What stays project-owned

FabricOps does not hide business transformations. Joins, filters, derivations, aggregations, enrichment, and reshaping remain visible in the **User defined transformation** section of the notebook.

This separation lets the framework standardise the pipeline boundary while keeping business logic explicit and reviewable.

**Previous:** [Module 2 overview](../02-run-pipeline.md)  
**Next:** [Unit 2: Run the baseline ETL](run-baseline-etl.md)
