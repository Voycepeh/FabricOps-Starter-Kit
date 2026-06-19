# Metadata Tables

Metadata table reference content now lives in the generated [List of Metadata Tables](../reference/metadata-tables/index.md).

Use that generated reference when you need table purpose, implemented schema, nullable status, notebook ownership, writer and reader functions, and links back to related function pages. The generated pages are sourced from the metadata setup schema registry used by `00_env_config`, so this overview page is intentionally short to avoid maintaining duplicate table guesses.

The [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) helper prepares these tables during environment setup.
Pipeline evidence writers such as [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) link runtime activity back to the generated metadata table reference.
