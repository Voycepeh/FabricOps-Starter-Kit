# Metadata tables

FabricOps Starter Kit v1.0.0 keeps metadata small, explicit, and safe for public examples. `00_env_config` prepares the required physical tables in the configured `metadata` lakehouse before runtime notebooks write to them.

## Physical tables prepared by `00_env_config`

| Physical table | Grain | Main writer | Purpose |
| --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | Data steward profile | `01_da` | Stores reusable steward contacts used by Data Agreements. |
| `METADATA_DATA_AGREEMENT` | Agreement version | `01_da` | Stores lightweight agreement identity, purpose, usage, recipient, and effective dates. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | Evidence link | `01_da` | Stores references to supporting files already uploaded to the metadata lakehouse `Files` area. |
| `METADATA_NOTEBOOK_REGISTRY` | Notebook registration event | `02_ex`, `03_pc` | Keeps agreement-linked execution notebooks discoverable. `04_gov` does not need a mandatory agreement registration. |
| `METADATA_DATA_CATALOGUE` | One row per column per profile run | `03_pc` | Stores both logical table context and column profile evidence. |
| `METADATA_DATA_LINEAGE_TABLE` | Table-level lineage event | `03_pc` | Stores source-to-target lineage summaries. |
| `METADATA_COLUMN_CONTEXT` | Approved column-context event | `04_gov` | Stores append-only human-approved business context. |
| `METADATA_DQ_RULES` | Approved DQ-rule event | `04_gov` | Stores append-only human-approved DQ rules for later enforcement work. |
| `METADATA_COLUMN_CLASSIFICATION` | Approved classification event | `04_gov` | Stores append-only human-approved sensitivity and personal-data decisions. |

## Catalogue architecture

`METADATA_DATA_CATALOGUE` is the canonical catalogue table. It replaces separate table/column catalogue concepts and any separate profile-row store.

Required catalogue fields include:

| Field | Description |
| --- | --- |
| `metadata_table_key` | Stable table identity generated from environment, dataset, and table. |
| `metadata_column_key` | Stable column identity generated from environment, dataset, table, and column. |
| `environment_name`, `dataset_name`, `table_name`, `column_name` | Mandatory logical governance identity. |
| `layer`, `asset_kind`, `pipeline_name` | Table context from the producing pipeline. |
| `profile_run_id`, `profile_stage`, `profile_status`, `profiled_at` | Profile-run identity and status. |
| `baseline_status`, `source_data_change_check`, `profile_baseline_mode` | Drift and baseline evidence retained from `03_pc`. |
| `data_type`, `row_count`, `null_count`, `distinct_count` | Column profile metrics. |
| `distribution_type`, `distribution_json` | Safe distribution summary metadata. |

## Governance review relationships

```text
METADATA_DATA_CATALOGUE
    |
    +--> METADATA_DATA_LINEAGE_TABLE
    |
    +--> METADATA_COLUMN_CONTEXT
    |
    +--> METADATA_DQ_RULES
    |
    +--> METADATA_COLUMN_CLASSIFICATION
```

`04_gov_dataset_table` selects a table from `METADATA_DATA_CATALOGUE`, loads the latest successful profile run, and shows existing approved context/rules/classification when available. Every write is append-only and requires an explicit human commit action.

## AI assistance boundary

Fabric `ai.generate_response(...)` can suggest business context, DQ rules, sensitivity labels, and PII classifications from safe profile metadata. Suggestions are advisory only. They are not committed unless a reviewer accepts or edits them and runs the matching commit helper.

## Enforcement boundary

For v1.0.0, `03_pc` continues to use notebook-defined schema and data-drift guardrails. It writes catalogue and lineage evidence but does not read approved DQ or classification metadata for enforcement. Enforcement of approved governance metadata is planned for a later enhancement.

## Lightweight `01_da` intake

`01_da` remains a lightweight agreement and steward intake workflow. Backend-generated identifiers and runtime audit fields are stored in backend tables but hidden from normal widget users. Organization-specific extension fields are serialized to `custom_fields_json`; Do not add a physical column for each local intake concept unless it becomes a stable public schema field.

| Field | Example | Source | Notes |
| --- | --- | --- | --- |
| steward_id | STEW-8d889875dd | Backend-generated | Stable steward identifier. |
| is_active | `true` | Backend-derived | Derived from effective dates and current state. |
| custom_fields_json | `{}` | Widget config | Holds local extensions safely. |

`DataAgreementConfig.steward_role_options` controls the standard role dropdown. add organization-specific role extensions to that config list instead of changing physical schemas.

Evidence upload is optional. Users can upload supporting files to the metadata lakehouse `Files` area and save references in `METADATA_DATA_AGREEMENT_EVIDENCE`. The metadata table does not store uploaded binary content.

### `01_da` widget options

- **Option A** uses `widget_render_agreement_intake_app` for a compact tabbed app.
- **Option B** uses separate `widget_render_data_steward`, `widget_render_data_agreement`, and `widget_render_agreement_evidence` widgets. Use Option B if Fabric output scrolling feels jumpy.
