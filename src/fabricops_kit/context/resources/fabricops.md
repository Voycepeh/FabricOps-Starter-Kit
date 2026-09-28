## What FabricOps is

FabricOps Starter Kit provides governed, quality-checked, Microsoft Fabric notebook workflows. This Context Layer is vendor-neutral plain text: use it with any capable AI assistant. It is curated task context, not a copy of all FabricOps documentation.

The installed package is the authority for supported public APIs and the target version. Work offline from this context; do not assume repository, documentation, or internet access.

### Authority and ownership

FabricOps owns the notebook scaffold and runtime conventions: public FabricOps APIs, reads and writes, Data Contracts, Guardrails, metadata, profiling, pipeline execution behaviour, and version-specific FabricOps knowledge.

The project owns its environment and source/target configuration values and its transformation/business logic. Apply the migration rule: **replace the shell, preserve the payload**.

Use only public names exported by `fabricops_kit`. Never invent unsupported FabricOps APIs. Never import underscore-prefixed, private, internal, shared, generated-metadata, or test-only package objects.
