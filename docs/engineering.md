<div class="fabricops-product-page" markdown="1">

# Engineering

**Build the project-specific transformation once; reuse FabricOps boundaries for configuration, reads, publication, metadata and diagnostics.**

![Engineering capability visual coming soon](assets/visual-coming-soon.svg){ .fabricops-placeholder }

<div class="fabricops-status-row">
  <span class="fabricops-release-status fabricops-release-status--live">Core pipeline: Live</span>
  <span class="fabricops-release-status fabricops-release-status--preview">Governed execution: gated</span>
</div>

The standard notebook flow is **Setup → Read → Transform → Write → Finalize**. The transformation remains ordinary project-owned PySpark. Dry Run and Ungoverned execution are available; Governed execution currently fails closed pending trusted deployment verification.

## Plug-and-Play pipelines and orchestration

[`00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) maps logical Fabric stores to each workspace. [`02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) wraps a readable engineering path:

| Boundary | Purpose |
| --- | --- |
| [`setup_pipeline()`](api/reference/setup_pipeline.md) | Starts one execution session and fixes its mode and identity. |
| [`orchestrate_read()`](api/reference/orchestrate_read.md) | Resolves, reads and evaluates a source. |
| **Project PySpark** | Joins, filters, enriches or aggregates the returned DataFrames. |
| [`orchestrate_write()`](api/reference/orchestrate_write.md) | Prepares and evaluates a target, then previews or publishes it. |
| [`finalize_pipeline()`](api/reference/finalize_pipeline.md) | Completes run reporting and persistent state where permitted. |

??? info "Under the Hood — execution path and Dry Run"

    `setup_pipeline()` builds the pipeline execution plan used by every Read and Write. `orchestrate_read()` calls internal `pipeline_read()`, then runs applicable Freshness, Schema, Grain and Data Quality checks. `orchestrate_write()` coordinates Schema, Sensitive Data treatment, Source Drift for participating sources, Grain and Data Quality before internal `pipeline_write()`.

    In Dry Run, `ExecutionPlan.permits_persistence` is false. Reads and transformations use real data, applicable Guardrails run, and the prepared target is profiled in memory. The Write returns `published=False` and `publication_status=not_published`; target rows, lineage, profiles, Guardrail Results and processing progress are not committed. A frozen Preview Data Contract can be selected without activation.

    Stage outcomes remain visible in `orchestration_stages`, `profile_result` and the Guardrail result objects. The trade-off is deliberate: Dry Run validates preparation and rules but cannot prove that a later physical write, connector operation or permission will succeed.

## Lakehouse and Warehouse integration

One notebook can address configured Lakehouse and Warehouse sources and targets without relying on one attached default Lakehouse. FabricOps resolves the logical store for the active workspace; Fabric permissions still decide whether access succeeds.

??? info "Under the Hood — store routing and Warehouse pushdown"

    `00_env_config` holds logical store names plus their workspace, item and store type. Internal `resolve_fabric_context()`, `get_store()` and `resolve_store()` choose the physical location. Lakehouse reads use OneLake table or file paths; Warehouse reads use Fabric's `synapsesql` connector. The mapping is configuration, not a new metadata table.

    For an Incremental Warehouse read, `pipeline_read()` resolves the accepted source-to-target watermark and internal `_warehouse_incremental_query()` builds the bounded T-SQL predicate passed to `read_warehouse_query()`. Lakehouse incremental reads use Spark filtering on the Delta DataFrame. Caller SQL is allowed for Full Warehouse reads but rejected for Incremental mode because FabricOps must own the checkpoint predicate.

    Pushdown can reduce data moved into Spark, but connector and Warehouse query costs remain. It is an efficiency choice, not a guarantee that Warehouse access outperforms direct Delta reads.

## Incremental and historical processing

Read mode and Write mode are independent. A pipeline can combine **Full** or **Incremental** reads with **Overwrite**, **Append All**, **Append New Only**, **SCD1** or **SCD2** writes.

??? info "Under the Hood — checkpoints, row hashes and SCD state"

    `pipeline_read()` resolves the last accepted source-to-target watermark and captures an upper bound before returning the current batch. `pipeline_write()` accepts progress only after verified publication. `METADATA_PROCESSING_STATE` distinguishes `source_observation`, `incremental_checkpoint`, drift/full-source baselines and `publication_receipt`, with source/target IDs, watermark values, status and acceptance time.

    `add_row_hash()` computes a lowercase SHA256 `_row_hash` from final incoming business values after transformation and Sensitive Data treatment. Append New Only de-duplicates incoming hashes and anti-joins target hashes. SCD strategies use configured business keys; SCD2 also writes `_effective_from`, `_effective_to` and `_is_current`.

    The costs are extra scans and hashing. Append New Only never updates existing rows. SCD behavior depends on correct keys, and an existing managed target with missing or invalid hashes requires a reviewed overwrite or migration.

??? info "Under the Hood — full-source observation"

    Incremental success alone cannot show that rows elsewhere in a full source disappeared or changed. With `observe_source` configured, internal `observe_full_source()` fingerprints the complete physical source independently of the incremental predicate. A baseline is accepted only after verified target publication.

    `METADATA_PROCESSING_STATE` records `record_type=full_source_baseline`, `source_table_id`, `row_count`, `content_fingerprint`, `publication_id` and `accepted_at`. The full scan provides evidence; it does not automatically delete rows or block publication, and it adds compute.

## Reliable publication, retries and recovery

FabricOps separates preparing data from accepting progress. A retry is recovered only when the framework can reconcile the batch identity, saved receipt and physical target.

??? info "Under the Hood — publication receipts and fail-closed recovery"

    `orchestrate_write()` delegates to internal `pipeline_write()` and its `PublicationBatch`. Lakehouse recovery verifies Delta commit evidence; Warehouse recovery checks the exact publication audit-marker row count. Unverifiable or partial writes fail closed rather than advancing a checkpoint.

    `METADATA_PROCESSING_STATE` persists the publication receipt with `publication_id`, `publication_batch_id`, `publication_activity_id`, `publication_input_rows`, `publication_strategy`, `target_table_id` and `status`. Fingerprinting and physical verification add compute, but prevent a metadata retry from silently duplicating a successful write.

??? info "Under the Hood — managed writer coordination and limitations"

    A target lease in `METADATA_PIPELINE_REGISTRY.leases_json` coordinates competing managed writers; `finalize_pipeline()` releases it. Schema, Grain, Data Quality, Source Drift and Sensitive Data checks can block continuation according to their configured behavior. Interrupted leases or inconsistent physical targets can require manual reconciliation.

    The lease does not protect against writers outside FabricOps. Multiple target writes in one notebook are independent publications, not one atomic transaction. Governed admission and publication currently fail closed until trusted deployment verification is integrated.

??? info "Under the Hood — row-level publication fields"

    Before the physical write, `resolve_target_audit_fields()` creates one run-consistent record and `add_target_audit_fields()` adds `_committed_at`, `_committed_by`, `_activity_id`, `_workspace_id`, `_notebook_id` and `_notebook_name`. The published target also receives `_row_hash`; SCD2 adds its three lifecycle columns.

    These are physical target columns, not an audit metadata table. They identify the publishing execution, not necessarily the original creator of each source record. Updates and merges can refresh audit values, and every managed target pays the storage cost.

## Profiling, lineage and observability

FabricOps records the technical context around each participating table so Engineering and Governance can reason from the same observations.

??? info "Under the Hood — what is stored and when"

    `orchestrate_read()` and `orchestrate_write()` schedule profiling; [`profile_table()`](api/reference/profile_table.md) can also profile an exact DataFrame or complete physical table. `METADATA_DATA_PROFILED` stores snapshot/table/column identity plus metrics such as row and non-null counts. `METADATA_DATA_PROFILED_FREQUENCY` stores bounded frequency rows linked to a snapshot. `METADATA_DATA_CATALOGUE` remains the canonical identity, location, type and processing-definition record.

    `METADATA_DATA_LINEAGE` records registered source/target pipeline participation—it does not claim column-level transformation lineage. `METADATA_PIPELINE_RUN` records the authoritative run, including execution mode, status, validated JSON operations, profiling, failures and final boundary state. `METADATA_GUARDRAIL_RESULTS` holds aggregate rule outcomes and continuation decisions.

    Dry Run keeps these results in memory. Persistent modes commit applicable metadata only through the execution/finalization boundaries. Whole-table profiling and frequency distributions can be expensive, so policy and scheduling matter.

</div>
