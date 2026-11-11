# METADATA_PROCESSING_STATE

Stores source observations, accepted checkpoints, Source Drift baselines and publication receipts so pipelines can resume and recover processing safely.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One source snapshot partition/header, source-to-target progress member, or exact target publication receipt.

**Primary key:** `record_id`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → 1)**
via `run_id`

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `source_table_id` + `target_table_id`

`METADATA_PROCESSING_STATE` **(N → 1)**
via `publication_id`

**Implementation details:** Stores incremental source observations/checkpoints and target publication receipts, plus pipeline-owned complete-source snapshots. source_snapshot manifests and source_row_evidence hash multiplicities are immutable; source_drift_baseline heads are shared by execution workspace and physical workspace/item/table. source_snapshot_acceptance retains successful history. Source Drift heads advance together only after confirmed whole-run finalization and verified required publications through a Serializable conditional transaction. Historical drift_baseline and full_source_baseline records are retained without new Contract authority. Hash rows stay distributed and are excluded before compact checkpoint history is collected.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">37</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">29</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>record_id</code></td><td><code>string</code></td><td>Stable SHA-256 primary key. Publication acceptance updates staged records; source baseline heads update conditionally while snapshot manifests, hash rows and acceptance history remain immutable.</td></tr>
<tr class="metadata-column--engineering"><td><code>record_type</code></td><td><code>string</code></td><td>source_observation, incremental_checkpoint and publication_receipt for processing; source_snapshot, source_row_evidence, source_drift_baseline and source_snapshot_acceptance for complete-source history. Historical drift_baseline/full_source_baseline records remain retained.</td></tr>
<tr class="metadata-column--engineering"><td><code>status</code></td><td><code>string</code></td><td>observed for source observations and complete-source snapshots; staged for publication members; committed for verified publication receipts/checkpoints and successfully finalized Source Drift acceptance.</td></tr>
<tr class="metadata-column--engineering"><td><code>observation_id</code></td><td><code>string</code></td><td>Identifier grouping one source observation or a complete-source manifest and its distributed hash rows.</td></tr>
<tr class="metadata-column--engineering"><td><code>run_id</code></td><td><code>string</code></td><td>Originating logical pipeline attempt, shared with METADATA_PIPELINE_RUN.run_id; null for standalone execution. Recovery retains the original run.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Stable pipeline identity when execution uses a pipeline plan.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_table_id</code></td><td><code>string</code></td><td>Identifier stored for <code>source_table_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_table_name</code></td><td><code>string</code></td><td>Physical source table name captured with the observation; null on publication receipts.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_table_id</code></td><td><code>string</code></td><td>Identifier stored for <code>target_table_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_table_name</code></td><td><code>string</code></td><td>Physical target table name captured at publication; null on unbound observations.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>observed_at</code></td><td><code>timestamp</code></td><td>Original source capture timestamp; distinct from acknowledgement time.</td></tr>
<tr class="metadata-column--engineering"><td><code>accepted_at</code></td><td><code>timestamp</code></td><td>Timestamp of successful metadata acknowledgement, shared by the receipt and all members accepted in one merge; null before acceptance.</td></tr>
<tr class="metadata-column--engineering"><td><code>partition_column</code></td><td><code>string</code></td><td>Column defining observed source partitions, or the incremental watermark column.</td></tr>
<tr class="metadata-column--engineering"><td><code>change_column</code></td><td><code>string</code></td><td>Source column supplying minimum and maximum change values.</td></tr>
<tr class="metadata-column--engineering"><td><code>watermark_type</code></td><td><code>string</code></td><td>Source scalar type for lossless change-value bounds, including distinct timestamp and timestamp_ntz semantics. Numeric and temporal values can be cast explicitly for queries.</td></tr>
<tr class="metadata-column--engineering"><td><code>partition_value</code></td><td><code>string</code></td><td>Canonical partition text for incremental/historical partition records; SHA256 identity hash for source_row_evidence. Null applies to receipts and complete-source manifests/heads.</td></tr>
<tr class="metadata-column--engineering"><td><code>row_count</code></td><td><code>long</code></td><td>Partition row count for incremental observations, exact hash multiplicity for source_row_evidence, or total complete-source rows for manifests and accepted heads.</td></tr>
<tr class="metadata-column--engineering"><td><code>min_change_value</code></td><td><code>string</code></td><td>Lossless minimum change value encoded according to watermark_type; null for empty observations/removals.</td></tr>
<tr class="metadata-column--engineering"><td><code>max_change_value</code></td><td><code>string</code></td><td>Lossless maximum change value encoded according to watermark_type; used as progress only on committed incremental_checkpoint records.</td></tr>
<tr class="metadata-column--engineering"><td><code>content_fingerprint</code></td><td><code>string</code></td><td>Partition fingerprint for incremental/historical records, typed SHA256 content hash for source_row_evidence, or multiset completeness fingerprint for complete-source manifests/heads. Independent of publication batch fingerprints.</td></tr>
<tr class="metadata-column--engineering"><td><code>is_present</code></td><td><code>boolean</code></td><td>True for a present source partition; false for an absent partition or empty incremental aggregate; null when no source partition applies, including empty-source headers and receipts.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_id</code></td><td><code>string</code></td><td>Reference to the exact target-specific publication_receipt record_id; a receipt references itself.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_batch_id</code></td><td><code>string</code></td><td>Prepared business content, schema, source membership and processing fingerprint; stored only on the receipt.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_activity_id</code></td><td><code>string</code></td><td>Fabric activity whose atomic target write stamped the batch; recovery does not substitute the retry activity.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_at</code></td><td><code>timestamp</code></td><td>UTC timestamp stamped atomically with target rows; paired with publication_activity_id for verification.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_input_rows</code></td><td><code>long</code></td><td>Prepared batch row count. Warehouse append/overwrite recovery verifies the complete marker count.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_strategy</code></td><td><code>string</code></td><td>Physical append, overwrite, scd1 or scd2 strategy of the receipt.</td></tr>
<tr class="metadata-column--engineering"><td><code>snapshot_payload_json</code></td><td><code>string</code></td><td>Versioned complete-source manifest: physical context, schema, validated authored keys, parent observation and hash completeness totals. Row hash evidence is distributed, never a driver-collected business snapshot.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_id</code></td><td><code>string</code></td><td>Fabric workspace identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_name</code></td><td><code>string</code></td><td>Fabric workspace name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr class="metadata-column--audit"><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>
