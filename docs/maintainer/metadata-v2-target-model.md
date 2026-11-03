# Notebook Pipeline Promotion metadata

The unreleased mixed Registry/deployment-attestation design is replaced by 13 canonical tables. Use an [explicit disposable development reset](governed-pipeline-promotion-v3-reset.md); there is no #1774 migration or compatibility adapter.

## Authority and grains

| Table | Grain | Authority |
| --- | --- | --- |
| METADATA_DATA_CONTRACT | Contract ID/version | Global immutable frozen definitions; authoring workspace is evidence only |
| METADATA_DATA_CONTRACT_ACTIVATION | Physical workspace/Table ID | Independently activated exact Contract and physical binding, revision and replay-safe activation ID |
| METADATA_PIPELINE_REGISTRY | Execution workspace/Pipeline ID/version | Immutable notebook promotion, archived snapshots, code/binding hashes, operations and Agreement where applicable |
| METADATA_PIPELINE_RUN | Run ID | Actual operations and exact Contract versions, frozen Pipeline version/promotion and execution identity |

Pipeline Registry contains no Contract Activation, control, Git/deployment or per-run lease rows. Superseded versions remain. Whole-table tracked Serializable Delta mutation plus an expected active version rejects simultaneous and phantom approvals; a naive MERGE is insufficient.

## Publication coordination

The existing exclusive physical-target publication claim protocol is retained in a small auxiliary Delta ledger under Metadata Lakehouse Files. It is runtime coordination, outside the 13 canonical tables and outside Registry. Ungoverned and Governed writers use the same target identity. Contract Activation takes that claim while changing protection, so writers cannot race an activation check. Claims never expire automatically after a crash; reconcile physical publication before removal. Profile scheduling still uses successful Run history and does not reserve Registry rows.

## Notebook integrity

Promotion archives both the complete saved development notebook and the promoted notebook under write-once Metadata Files. Only the literal setup mode changes from Dry Run to Governed; the rest of the notebook is retained. A separate versioned physical notebook is created, even within one workspace. Logical stores resolve through destination configuration and exact physical bindings are reviewed.

Executable hashing includes code and behavior metadata and excludes Markdown, outputs and execution counts. Imported dependencies are not frozen. Cross-workspace data operations require an exact effective Agreement; internal same-workspace pipelines may omit it. An API/snapshot/hash/binding/Agreement failure blocks managed Governed operations. Existing admitted versions may finish after promotion while new starts use the active item. Exact restoration preserves changed code before replacing and verifying the active snapshot.

**Governed admission remains blocked pending [signed-in Fabric validation](governed-pipeline-promotion-v3-validation.md).** Saved-definition checks have TOCTOU limits; folders and framework checks cannot stop privileged direct Spark execution.

## Recovery and rollback

Staging and clone failures never deactivate the prior Registry row. A lost commit acknowledgement is recovered only from the exact operation marker and versioned readback; the same promotion ID cannot authorize different content. Retain the review object when retrying staged work. Artifacts contain the promotion ID for explicit inspection and cleanup; they are not authority until the atomic Registry commit succeeds.

Exact active-snapshot restoration reuses its original promotion. Changed implementation or rollback to previous logic requires a manual Dry Run and a new reviewed monotonically increasing version. Normal setup never deletes tables or business targets.
