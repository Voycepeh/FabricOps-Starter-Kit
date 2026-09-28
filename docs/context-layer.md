# FabricOps Context Layer

The FabricOps Context Layer supplies focused, self-contained FabricOps knowledge to an AI assistant without requiring repository, documentation, or internet access.

## What it provides

**The Context Layer is deterministic, offline, and vendor-neutral.** Its plain-text output can be given to Microsoft Fabric Copilot or any other capable AI assistant. The required curated resources ship with the installed FabricOps version, so the output describes that installation's target conventions.

The first supported task helps migrate a FabricOps v0.2.0 `02_pipeline` toward the current canonical pipeline. It explains the version-specific differences, public APIs, pipeline structure, project/FabricOps ownership boundary, migration instructions, and verification expectations. It does not rewrite a notebook or call an AI service.

!!! important
    Migration follows **replace the shell, preserve the payload**: preserve project-owned configuration and transformation/business logic while adapting the FabricOps-owned scaffold. An engineer must review and validate the result.

## Generate migration context

```python
from fabricops_kit import FabricOpsContextLayer

context = FabricOpsContextLayer()

migration_context = context.for_task(
    "migrate_pipeline",
    from_version="0.2.0",
)

print(migration_context)
```

Unsupported tasks and source versions fail explicitly rather than returning generic advice. The public class and its `for_task()` docstring define the exact callable contract.
