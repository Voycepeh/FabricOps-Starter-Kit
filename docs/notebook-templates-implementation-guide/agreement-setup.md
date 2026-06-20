# 01 Agreement Setup

`01_agreement` is the agreement intake notebook. It records who owns the data relationship, what agreement applies, and which evidence supports that agreement before a pipeline uses it.

## What the notebook captures

The notebook keeps agreement setup readable by splitting intake into three widgets: one for the accountable data steward, one for the data agreement, and one for supporting agreement evidence. Each widget writes durable metadata through the configured `metadata` target from `00_env_config`; it does not depend on the default attached Lakehouse for metadata writes.

| Intake step | Widget function | Metadata table written |
| --- | --- | --- |
| Data steward intake | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) | [`METADATA_DATA_STEWARD`](../reference/metadata/metadata_data_steward.md) |
| Agreement intake | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) | [`METADATA_DATA_AGREEMENT`](../reference/metadata/metadata_data_agreement.md) |
| Agreement evidence | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) | [`METADATA_DATA_AGREEMENT_EVIDENCE`](../reference/metadata/metadata_data_agreement_evidence.md) |

Use this page as the notebook-facing guide. Use the [metadata tables reference](../reference/metadata.md) for column-level table details and the [Environment Configuration](environment-config.md#agreement-widget-configuration) page for the source of truth for widget configuration.

## Data steward intake

Use [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) to capture steward details. Steward rows give agreements an accountable owner and make later pipeline evidence easier to interpret.

### Text-based widget preview

| Widget area | What it captures or writes |
| --- | --- |
| Widget function | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) |
| Fields captured | `steward_name`, `steward_role`, `contact`, `effective_from`, `effective_to`, plus any configured custom steward fields. |
| Metadata written | One active or historical steward row in [`METADATA_DATA_STEWARD`](../reference/metadata/metadata_data_steward.md), including generated `steward_id`, lifecycle fields, `custom_fields_json`, and runtime audit columns. |
| Metadata table documentation | [`METADATA_DATA_STEWARD`](../reference/metadata/metadata_data_steward.md) |

!!! info "Related metadata"
    Data steward intake writes [`METADATA_DATA_STEWARD`](../reference/metadata/metadata_data_steward.md). Agreement intake and agreement selection read those steward rows so later notebook evidence can point to an accountable steward.

## Agreement intake

Use [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) to define the agreement context. This is the contract context that `02_pipeline` later selects with its agreement selector, so keep names, scope, and ownership readable for notebook users.

### Text-based widget preview

| Widget area | What it captures or writes |
| --- | --- |
| Widget function | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) |
| Fields captured | `agreement_name`, `domain`, `steward_id`, `recipient`, `start_date`, `expiry_date`, `business_purpose`, `approved_usage_internal`, `approved_usage_external`, `approved_usage_research`, plus any configured custom agreement fields. |
| Metadata written | One agreement row in [`METADATA_DATA_AGREEMENT`](../reference/metadata/metadata_data_agreement.md), including generated `agreement_id`, `contract_version`, selected steward context, `custom_fields_json`, and runtime audit columns. |
| Metadata table documentation | [`METADATA_DATA_AGREEMENT`](../reference/metadata/metadata_data_agreement.md) |

!!! info "Related metadata"
    Agreement intake writes [`METADATA_DATA_AGREEMENT`](../reference/metadata/metadata_data_agreement.md). `02_pipeline` later reads this table through the agreement selector so pipeline summary, lineage, and guardrail evidence can be tied back to the selected agreement.

## Agreement evidence

Use [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) to attach agreement evidence. Evidence makes the agreement more than a label: it gives later pipeline runs a traceable reason for why the selected contract exists.

### Text-based widget preview

| Widget area | What it captures or writes |
| --- | --- |
| Widget function | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) |
| Fields captured | Selected `agreement_id` and `contract_version`, `evidence_type`, `file_name`, `file_path`, `mime_type`, `file_size`, `uploaded_at`, and `uploaded_by`. Evidence files must be uploaded separately to the metadata Lakehouse `Files` area before their `Files/...` paths are recorded. |
| Metadata written | One evidence reference row per saved file reference in [`METADATA_DATA_AGREEMENT_EVIDENCE`](../reference/metadata/metadata_data_agreement_evidence.md). The widget writes metadata rows only; it does not write binary file content. |
| Metadata table documentation | [`METADATA_DATA_AGREEMENT_EVIDENCE`](../reference/metadata/metadata_data_agreement_evidence.md) |

!!! info "Related metadata"
    Agreement evidence writes [`METADATA_DATA_AGREEMENT_EVIDENCE`](../reference/metadata/metadata_data_agreement_evidence.md). Dashboard and handover views can use those rows to explain which files or references support the selected agreement.

## Configurable dropdowns and custom fields

`00_env_config` is the source of truth for agreement widget configuration. Do not duplicate hardcoded dropdown values or custom-field definitions in `01_agreement` documentation, notebook cells, or downstream pipeline code.

Agreement widget configuration is managed through `DataAgreementConfig` in `00_env_config` and is described on the [Environment Configuration](environment-config.md#agreement-widget-configuration) page. Use that configuration to control:

- which lightweight metadata table names are prepared for agreement intake;
- which standard columns are visible in the data steward and data agreement widgets;
- which `steward_role` dropdown values appear in the data steward widget;
- which reusable custom metadata fields appear in the steward and agreement widgets.

Custom steward and agreement fields are stored in `custom_fields_json` on the relevant metadata table. They do not create new physical metadata table columns.

## Handoff to `02_pipeline`

After agreement setup, `02_pipeline` can select the agreement and register the active notebook relationship. The pipeline then records run, lineage, and guardrail evidence against the selected agreement context instead of running as an isolated technical notebook.

The handoff works because `01_agreement` has already written:

- accountable steward context to [`METADATA_DATA_STEWARD`](../reference/metadata/metadata_data_steward.md);
- agreement identity, scope, usage, and steward linkage to [`METADATA_DATA_AGREEMENT`](../reference/metadata/metadata_data_agreement.md);
- supporting file-reference evidence to [`METADATA_DATA_AGREEMENT_EVIDENCE`](../reference/metadata/metadata_data_agreement_evidence.md).

`02_pipeline` then uses [`widget_select_agreement`](../api/modules/data_agreement.md#widget_select_agreement) and [`get_selected_agreement`](../api/modules/data_agreement.md#get_selected_agreement) to read the selected agreement context for pipeline metadata and evidence.

## Related navigation

Use the Function Reference when you need callable-level details for agreement widgets; the inline widget links above remain direct because each section explains the exact function used at that notebook step.

[Back to Template Notebooks](index.md){ .md-button } [View Function Reference](../reference/index.md){ .md-button }
