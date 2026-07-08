# METADATA_DATA_AGREEMENT_EVIDENCE

**Purpose:** Supporting agreement files and related metadata captured during agreement intake.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `agreement_id` | `string` | No | Agreement evidence widget | Metadata Data Agreement Evidence field `agreement_id`. |
| `agreement_version` | `string` | No | Agreement evidence widget | Canonical agreement version associated with the row. |
| `evidence_type` | `string` | No | Agreement evidence widget | Metadata Data Agreement Evidence field `evidence_type`. |
| `file_name` | `string` | No | Agreement evidence widget | Metadata Data Agreement Evidence field `file_name`. |
| `file_path` | `string` | No | Agreement evidence widget | Metadata Data Agreement Evidence field `file_path`. |
| `mime_type` | `string` | Yes | Agreement evidence widget | Metadata Data Agreement Evidence field `mime_type`. |
| `file_size` | `long` | Yes | Agreement evidence widget | Metadata Data Agreement Evidence field `file_size`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_render_agreement_evidence`](../../api/reference/widget_render_agreement_evidence.md)
