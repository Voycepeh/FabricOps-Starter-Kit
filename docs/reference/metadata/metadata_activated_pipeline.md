# METADATA_ACTIVATED_PIPELINE

Immutable whole-pipeline approval linked to exact successful Testing, candidate manifest, reusable frozen contracts and one exact effective Agreement. Only is_active changes during explicit switching/deactivation.

## Writer functions

* [`set_pipeline_active`](../../api/reference/set_pipeline_active.md)

## Used in Workflow Template

* [`01_governance, 02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Pipeline activation and deployment

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One immutable approved version of one stable logical pipeline.

**Primary key:** `activated_pipeline_id`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → 1)**
via `testing_run_id`

`METADATA_DATA_AGREEMENT` **(N → 1)**
via `agreement_id` + `agreement_version`

`METADATA_DATA_CONTRACT` **(N → M)**
via Not defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 18 |
| Business columns | 10 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `activated_pipeline_id` | `string` | Identifier stored for `activated_pipeline_id`. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `pipeline_name` | `string` | Human-readable name stored for `pipeline_name`. |
| `pipeline_version` | `string` | Metadata Activated Pipeline field `pipeline_version`. |
| `agreement_id` | `string` | Stable identifier for the agreement lifecycle. |
| `agreement_version` | `string` | Canonical agreement version associated with the row. |
| `testing_run_id` | `string` | Identifier stored for `testing_run_id`. |
| `candidate_fingerprint` | `string` | Metadata Activated Pipeline field `candidate_fingerprint`. |
| `manifest_json` | `string` | JSON payload stored for `manifest_json`. |
| `is_active` | `boolean` | Whether the row is currently active. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
