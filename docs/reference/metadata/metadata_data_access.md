# METADATA_DATA_ACCESS

**Purpose:** Externally collected access inventory for workspace, object, schema, and table access review.

## Starter Kit usage

- **Written by notebook/template:** External access-log inventory collection, not a FabricOps notebook template.
- **Written by function or widget:** Not currently discoverable.
- **Read by function or widget:** Not currently discoverable.
- **Related template step:** External inventory ingestion / governance access review.

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

- Not currently discoverable.
