<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `resolve_table_id`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.pipeline.resolve_table_id.resolve_table_id`

Source path: `src/fabricops_kit/pipeline/resolve_table_id.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/pipeline/resolve_table_id.py)

Signature: `resolve_table_id(*, store: str, schema: str | None = None, table_name: str) -> str`

## Description

Return the canonical table identity for configured physical coordinates.

## Parameters

store : str
    Configured FabricStore key.
schema : str, optional
    Physical schema, or ``None`` when the configured store does not use one.
table_name : str
    Physical table name.

## Return value

str
    Deterministic canonical ``table_id``. The physical table and Catalogue
    record do not need to exist yet.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)
