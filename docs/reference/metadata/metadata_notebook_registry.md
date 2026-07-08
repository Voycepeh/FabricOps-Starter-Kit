# METADATA_NOTEBOOK_REGISTRY

**Purpose:** Active notebook registration records linking notebooks to agreement, environment, dataset, and pipeline context.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `agreement_id` | `string` | No | Notebook registration workflow | Metadata Notebook Registry field `agreement_id`. |
| `agreement_version` | `string` | No | Notebook registration workflow | Canonical agreement version associated with the row. |
| `environment_name` | `string` | No | Notebook registration workflow | Metadata Notebook Registry field `environment_name`. |
| `dataset_name` | `string` | Yes | Notebook registration workflow | Metadata Notebook Registry field `dataset_name`. |
| `table_name` | `string` | Yes | Notebook registration workflow | Metadata Notebook Registry field `table_name`. |
| `topic` | `string` | Yes | Notebook registration workflow | Metadata Notebook Registry field `topic`. |
| `notebook_type` | `string` | No | Notebook registration workflow | Metadata Notebook Registry field `notebook_type`. |
| `notebook_url` | `string` | Yes | Notebook registration workflow | Metadata Notebook Registry field `notebook_url`. |
| `registration_id` | `string` | No | Notebook registration workflow | Metadata Notebook Registry field `registration_id`. |
| `registration_role` | `string` | No | Notebook registration workflow | Metadata Notebook Registry field `registration_role`. |
| `registration_status` | `string` | No | Notebook registration workflow | Metadata Notebook Registry field `registration_status`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_pipeline_bootstrap`](../../api/reference/widget_pipeline_bootstrap.md)
