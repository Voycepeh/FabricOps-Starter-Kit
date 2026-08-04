# METADATA_ENRICHMENT

**Purpose:** Append-only generic descriptive and governance values for catalogue table and column identities.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 13 |
| Business columns | 5 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `enrichment_id` | `string` | `fabricops_kit.widgets.shared.build_enrichment_records` | Identifier stored for `enrichment_id`. |
| `enrichment_level` | `string` | `fabricops_kit.widgets.shared.build_enrichment_records` | Metadata Enrichment field `enrichment_level`. |
| `metadata_key` | `string` | `fabricops_kit.widgets.shared.build_enrichment_records` | Metadata Enrichment field `metadata_key`. |
| `enrichment_type` | `string` | `fabricops_kit.widgets.shared.build_enrichment_records` | Enrichment type recorded for the row. |
| `value` | `string` | `fabricops_kit.widgets.shared.build_enrichment_records` | Metadata Enrichment field `value`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Breaking pre-release replacement

This intentionally breaking schema replaces the previous enrichment lifecycle and payload model. Existing development `METADATA_ENRICHMENT` tables must be recreated; no automated migration or compatibility support is provided. Values to retain may be exported and manually reshaped before recreation.

## Grain

One row per enrichment level + metadata key + enrichment type + append event.

## Current value

The latest appended row for `enrichment_level` + `metadata_key` + `enrichment_type` is current, ordered by `_committed_at`, `_activity_id`, and `enrichment_id`. Empty values are rejected, so clearing is deferred to a future change.

## Examples

| enrichment_level | metadata_key | enrichment_type | value |
| --- | --- | --- | --- |
| table | tbl_abc | Description | Student enrolment records |
| table | tbl_abc | Classification | Highly sensitive |
| column | col_xyz | Description | Unique student identifier |
| column | col_xyz | Personal_identifier | Direct PII |

The catalogue remains the source of table and column identity. New enrichment types do not require a schema change.

## Related function reference

- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
