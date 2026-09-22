<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `pipeline_read`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.pipeline.pipeline_read.pipeline_read`

Source path: `src/fabricops_kit/pipeline/pipeline_read.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/pipeline/pipeline_read.py)

Signature: `pipeline_read(*, store: 'str | None' = None, schema: 'str | None' = None, table_name: 'str | None' = None, table_id: 'str | None' = None, query: 'str | None' = None, read_mode: 'str' = 'full', target_table_id: 'str | None' = None, spark_session=None, verbose: 'bool' = True) -> 'dict[str, Any]'`

## Description

Read one governed pipeline source through the appropriate Fabric store.

## Parameters

store : str, optional
    Configured source store key, such as ``"source"`` or ``"product"``.
    Supply it with ``table_name`` and optional ``schema`` instead of
    ``table_id``.
schema : str, optional
    Physical source schema, when the configured store uses schemas.
table_name : str, optional
    Physical source table name. Required with ``store`` when ``table_id``
    is omitted. ``store``, optional ``schema``, and ``table_name`` form
    one identity form.
table_id : str, optional
    Canonical registered source identity. This is the alternative identity
    form and is mutually exclusive with ``store``, ``schema``, and
    ``table_name``.
query : str, optional
    Read-only SQL for a configured Warehouse source. The supplied source
    identity remains the governed source participant even when the result
    is a projection, filter, join, or aggregation. FabricOps does not infer
    arbitrary source identity by parsing SQL. A query may accompany either
    physical coordinates or ``table_id`` when the resolved store is a
    Warehouse.
read_mode : {"full", "incremental"}, default="full"
    Explicit source read behaviour. ``full`` preserves the complete-source
    read. ``incremental`` resolves unconsumed work from the last Source
    Observation committed for this exact source-to-target relationship.
target_table_id : str, optional
    Canonical governed target being prepared. It is accepted for both read
    modes so target flows can use one consistent call shape, and is required
    when ``read_mode="incremental"``.
spark_session : object, optional
    Spark session forwarded to the selected foundational reader instead of relying on notebook-global ``spark``.
verbose : bool, default=True
    Whether to print one concise orchestration message showing the resolved
    Fabric store type, physical table identity, and selected foundational
    reader. This makes the hidden routing understandable without exposing
    workspace IDs, SQL text, contract payloads, or runtime plumbing.

## Return value

dict
    A deliberately small result with these fields:

    - ``dataframe``: the Spark DataFrame returned by the selected
      foundational Fabric I/O reader.
    - ``table_id``: the canonical identity of the governed physical source.
    - ``is_query``: whether ``dataframe`` is a custom Warehouse query
      result rather than the complete physical table.
    - ``has_contract``: whether an environment-selected immutable Data
      Contract applies. The contract record itself is not exposed.
    - ``read_mode``: the explicit source read mode.
    - ``has_data`` and ``should_process``: whether this read contributes
      unconsumed work. Full reads return ``True`` without triggering a count.
    - ``scope``: a compact summary of the resolved full, bootstrap,
      watermark, or partition scope. Partition scope includes removed
      values that require target reconciliation; no metadata rows are exposed.

## Usage notes

The governed orchestration performs these mechanical steps:

1. Resolve the canonical source ``table_id``.
2. Resolve the configured physical source identity.
3. Infer whether that configured source is a Lakehouse or Warehouse.
4. For incremental reads, observe the complete physical source, resolve the
   last committed state for the exact target, and derive watermark or
   changed-partition scope. A missing baseline deterministically bootstraps
   with a complete read.
5. Select and call ``read_lakehouse_table``, ``read_warehouse_table``, or
   framework-owned ``read_warehouse_query`` pushdown.
6. Capture transient current-run Source Observation state without advancing
   accepted progress. Only successful target publication commits it.
7. Return the DataFrame, explicit ``table_id``, and small source metadata
   required by the notebook.

Higher-level governed pipeline code normally uses ``pipeline_read``.
Foundational readers remain available for direct lower-level or
general-purpose Fabric reads that do not need pipeline orchestration.
``pipeline_read`` orchestrates governed table sources only. Raw Lakehouse
Files do not have a canonical ``table_id`` and should continue to use the
foundational CSV, Excel, JSON, or Parquet readers directly.

Incremental Warehouse reads reject caller-owned ``query`` SQL because
FabricOps cannot safely compose arbitrary SQL with its target-specific
progress predicate. Source Drift remains a separate compatibility check;
incremental scope answers only what this target has not consumed.

This function does not execute Freshness, Source Drift, Schema, DQ, or
Sensitive Data checks. It also does not profile
data, transform rows, or write a pipeline target. Those meaningful
engineering decisions remain explicit in ``02_pipeline`` and
``03_incremental_pipeline``.

With ``verbose=True``, a Warehouse table read reports a line such as
``FabricOps Read → Warehouse table 'product.demo.orders' → read_warehouse_table``.

[Back to release overview](../index.md)
