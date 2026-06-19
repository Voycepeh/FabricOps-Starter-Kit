# METADATA_DATA_ACCESS

**Purpose:** Public-safe access context used by governance and metadata review workflows.

## Workflow usage

- **Written by notebook/template:** 03_governance.ipynb
- **Written by function or widget:** Not currently discoverable.
- **Read by function or widget:** [`widget_review_table_governance`](../../api/reference/widget_review_table_governance.md)
- **Related template step:** 03_governance.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `user_principal` | `string` | Nullable |
| `role_name` | `string` | Nullable |
| `permission` | `string` | Nullable |
| `access_purpose` | `string` | Nullable |
| `approval_status` | `string` | Nullable |
| `access_scope` | `string` | Nullable |
| `table_id` | `string` | Nullable |
| `metadata_table_key` | `string` | Nullable |
| `metadata_column_key` | `string` | Nullable |
| `granted_date` | `string` | Nullable |
| `expires_at` | `string` | Nullable |
| `approved_by` | `string` | Nullable |
| `approved_at` | `string` | Nullable |
| `notes` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`widget_review_table_governance`](../../api/reference/widget_review_table_governance.md)
