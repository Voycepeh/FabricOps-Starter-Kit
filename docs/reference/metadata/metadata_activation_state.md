# METADATA_ACTIVATION_STATE

Records which pipeline releases are approved to run Live in each environment, together with the agreements and approvals behind them.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)
* [`setup_pipeline`](../../api/reference/setup_pipeline.md)
* [`widget_activate_pipeline`](../../api/reference/widget_activate_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One central record containing the approval and execution state for all environments.

**Primary key:** `authority_id`

**Relationships:**

**Activated Pipeline (logical entity; 1 → N):** Each registered Pipeline UUID can have many immutable Activated Pipeline releases in the environment history. Activated Pipeline is a logical entity in snapshot_json, not a separate Delta table.

**Live Pipeline Run (logical entity; 1 → N):** Each approved Activated Pipeline release authorizes many Live Pipeline Runs; registration alone never authorizes execution.

**Implementation details:** Single atomic central authority for environment activation revisions, immutable approval history, table contracts, writer ownership, running execution reservations, transient notebook-rebind barriers and renewable profiling claims.

**Implementation details:** Single atomic central authority for environment activation revisions, immutable approval history, table contracts, writer ownership, running execution reservations, transient notebook-rebind barriers and renewable profiling claims.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 11 |
| Business columns | 3 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `authority_id` | `string` | Identifier stored for `authority_id`. |
| `token` | `string` | Metadata Activation State field `token`. |
| `snapshot_json` | `string` | JSON payload stored for `snapshot_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
