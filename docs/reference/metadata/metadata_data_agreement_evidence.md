# METADATA_DATA_AGREEMENT_EVIDENCE

**Purpose:** Supporting agreement files and evidence metadata captured during agreement intake.

## Starter Kit usage

- **Written by notebook/template:** 01_agreement.ipynb
- **Written by function or widget:** [`widget_render_agreement_evidence`](../../api/reference/widget_render_agreement_evidence.md)
- **Read by function or widget:** [`widget_select_agreement`](../../api/modules/data_agreement.md#widgetselectagreement)
- **Related template step:** 01_agreement.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `agreement_id` | `string` | Nullable |
| `contract_version` | `string` | Nullable |
| `evidence_type` | `string` | Nullable |
| `file_name` | `string` | Nullable |
| `file_path` | `string` | Nullable |
| `mime_type` | `string` | Nullable |
| `file_size` | `string` | Nullable |
| `uploaded_at` | `string` | Nullable |
| `uploaded_by` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`widget_render_agreement_evidence`](../../api/reference/widget_render_agreement_evidence.md)
- [`widget_select_agreement`](../../api/modules/data_agreement.md#widgetselectagreement)
