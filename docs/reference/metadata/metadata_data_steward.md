# METADATA_DATA_STEWARD

**Purpose:** Active and historical data steward records used by agreement intake.

## Starter Kit usage

- **Written by notebook/template:** 01_agreement.ipynb
- **Written by function or widget:** [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)
- **Read by function or widget:** [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), [`widget_select_agreement`](../../api/modules/data_agreement.md#widgetselectagreement)
- **Related template step:** 01_agreement.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `steward_id` | `string` | Nullable |
| `steward_name` | `string` | Nullable |
| `steward_role` | `string` | Nullable |
| `contact` | `string` | Nullable |
| `effective_from` | `string` | Nullable |
| `effective_to` | `string` | Nullable |
| `is_active` | `string` | Nullable |
| `custom_fields_json` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md)
- [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)
- [`widget_select_agreement`](../../api/modules/data_agreement.md#widgetselectagreement)
