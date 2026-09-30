<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `pipeline_write`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.pipeline.pipeline_write.pipeline_write`

Source path: `src/fabricops_kit/pipeline/pipeline_write.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/pipeline/pipeline_write.py)

Signature: `pipeline_write(df, *, store: 'str | None' = None, schema: 'str | None' = None, table_name: 'str | None' = None, table_id: 'str | None' = None, load_strategy: 'str | None' = None, load_strategy_parameters: 'dict[str, Any] | None' = None, source_table_ids: 'list[str] | tuple[str, ...] | None' = None, repartition_by=None, options: 'dict[str, Any] | None' = None, spark_session=None, verbose: 'bool' = True) -> 'dict[str, str]'`

## Description

Publish one governed pipeline table target through its configured Fabric store.

## Parameters

df : pyspark.sql.DataFrame
    Prepared target DataFrame after explicit target checks have passed.
store : str, optional
    Configured store key. Supply it with ``table_name`` and optional
    ``schema`` instead of ``table_id``.
schema : str, optional
    Physical target schema when the configured store uses schemas.
table_name : str, optional
    Physical target table name. Required with ``store`` when ``table_id``
    is omitted.
table_id : str, optional
    Canonical registered target identity. This identity form is mutually
    exclusive with ``store``, ``schema``, and ``table_name``.
load_strategy : {"overwrite", "append", "scd1", "scd2"}, optional
    Development-authored processing proposal. Selected or frozen contract
    validation applies in Development, and the active approved Data
    Contract remains authoritative in Production.
load_strategy_parameters : dict, optional
    Development-authored strategy parameters, such as key, effective,
    tracked, or partition columns, subject to contract validation.
source_table_ids : list[str] or tuple[str, ...], optional
    Canonical identities of the exact governed sources that feed this
    target publication. Supply identities returned by ``pipeline_read``.
    FabricOps requires this explicit association because activity-wide
    reads and Spark transformation plans cannot reliably identify which
    source subset produced a particular target DataFrame.
repartition_by : int or str or list[str] or tuple[str, ...], optional
    Optional Spark repartitioning passed to simple physical writes.
options : dict, optional
    Additional physical writer options for append or overwrite publication.
spark_session : object, optional
    Spark session used for write-side metadata persistence. Supply the active Fabric notebook session explicitly when available.
verbose : bool, default=True
    Whether to print one concise orchestration message showing the resolved
    Fabric store type, physical table identity, governed strategy, and
    selected foundational writer or governed SCD publication path. This
    explains hidden routing without exposing implementation plumbing.

## Return value

dict
    A deliberately small result containing only the canonical ``table_id``.
    Profile the persisted target through an explicit read-back rather than
    treating the input DataFrame as persisted state.

## Usage notes

The governed orchestration performs these mechanical steps:

1. Resolve the canonical target ``table_id``.
2. Resolve the configured physical target identity.
3. Resolve the selected or active Data Contract.
4. Resolve the governed load strategy and parameters.
5. Resolve processing scope.
6. Apply FabricOps target audit fields.
7. Validate target notebook ownership.
8. Detect whether this activity already produced target rows.
9. Perform append/overwrite or dedicated SCD processing only when the
   activity is not already represented in the physical target.
10. Persist the resolved target load strategy and parameters on the
    table-level ``METADATA_DATA_CATALOGUE`` row.
11. Only after physical and Catalogue success, idempotently commit target
    Lineage and accepted Source Observation/write-success metadata.
12. Return a small publication result with no hidden profiling state.

Callers do not provide a store type, manually resolve ``table_id``, choose
a Lakehouse versus Warehouse writer, construct processing scope or success
context, or manually commit Lineage or Source Observation metadata. Callers
provide only the canonical identities of the sources that actually feed
this target, rather than internal read or preparation dictionaries. This
keeps multiple target writes in one activity exact and independent.

Same-activity retries use the target's persisted ``_activity_id`` audit
field to detect a row-producing publication and skip its physical mutation.
Catalogue processing, Lineage, and accepted Source Observation metadata are
idempotent and replayed on every retry. Empty append, empty overwrite,
partition-removal-only overwrite, and true SCD no-op operations may leave
no activity marker; repeating those operations is safe. Changing the
participating source set represents a different logical publication and
therefore requires a new activity rather than reuse of the current one.
Lakehouse SCD2 closes changed rows and inserts their replacement current
versions in one Delta ``MERGE`` so an activity marker cannot represent a
partially applied two-step history mutation. Warehouse SCD2 retains its
existing SQL transaction boundary.

Before physical publication, target-specific Source Observation evidence
is durably staged with ``observation_status='observed'``. If a scheduled
activity terminates after target rows materialize but before finalization,
the next activity verifies the prior target ``_activity_id``, promotes that
staged evidence idempotently, and calculates incremental work from the
recovered committed baseline. Evidence for another target is not promoted.

A first incremental append has no committed baseline and therefore reads a
complete bootstrap scope. FabricOps permits that bootstrap only for a new
or empty physical target. A populated target fails before publication so
missing metadata cannot silently duplicate all source rows. SCD1 and SCD2
bootstraps continue through their existing keyed, idempotent merge paths.

A removed source partition is actionable incremental work even though its
input DataFrame contains no rows for that partition. FabricOps permits the
removal only when governed partition-scoped overwrite can include the
removed value in ``replaceWhere`` and clear stale target rows. Other target
strategies, or mismatched source and target partition columns, fail before
publication and therefore do not commit the removal baseline.

With ``verbose=True``, a simple Lakehouse overwrite reports a line such as
``FabricOps Write → Lakehouse table 'unified.demo.curated_orders' → overwrite → write_lakehouse_table``.

This function does not perform transformations, schema checks, DQ checks,
Sensitive Data Guardrails, Source Drift, or profiling. These remain
explicit notebook engineering and governance steps. ``pipeline_write`` publishes governed
table targets only. Raw Lakehouse Files do not have a canonical FabricOps
``table_id``; direct file-output concerns, if supported in future, belong
outside this governed table orchestration API.

[Back to release overview](../index.md)
