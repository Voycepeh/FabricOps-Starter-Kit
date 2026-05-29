# `01_da_<agreement>`

`01_da_<agreement>` is the human-approved data sharing agreement notebook for one agreement.
It captures agreement metadata through notebook widgets where practical, builds audited metadata records, and commits those records to the configured metadata lakehouse.
It does **not** perform profiling, DQ authoring, lineage capture, or pipeline contract enforcement.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_da_agreement_template.ipynb">Open template notebook</a>

## What this notebook does

1. **Runtime bootstrap**
   - Runs `%run 00_env_config` so metadata routing and notebook policy come from shared `CONFIG`.
   - Calls `setup_notebook(...)` to validate the notebook runtime and required metadata target.
2. **Widget-driven agreement capture**
   - Creates widgets for human-entered agreement fields such as agreement identity, steward, department, purpose, source table, allowed outputs, refresh frequency, and commit notes.
   - Does not expose derived fields as widgets.
3. **Structured record building**
   - Builds append-friendly records for:
     - `metadata.agreement_header`
     - `metadata.agreement_catalogue`
     - `metadata.agreement_scope`
4. **Audit fields**
   - Every committed record includes `committed_by` and `committed_at`.
   - Runtime context fields such as notebook, workspace, lakehouse, and run ID are included when available.
5. **Commit preview and summary**
   - Records are previewed before commit.
   - The commit summary prints `agreement_id`, `agreement_status`, `expiry_date`, `status_as_of_date`, `committed_by`, `committed_at`, and `tables_updated`.

## Widget behavior

- `renewal_required` is a required `Yes` / `No` dropdown.
- `sensitivity_label` is always a dropdown.
  - It defaults to `Public`, `Confidential`, and `Restricted`.
  - Projects can pass a custom `sensitivity_labels` list.
- `contains_sensitive_data`, `dashboard_allowed`, `data_dump_allowed`, and `self_service_extract_allowed` are `Yes` / `No` dropdowns.
- `refresh_frequency` is a dropdown using FabricOps defaults unless a custom list is supplied.
- `department` is a dropdown only when a `departments` list is supplied; otherwise it remains free text.
- `source_system` is a dropdown only when a `source_systems` list is supplied; otherwise it remains free text.
- Explanation fields such as purpose, scope, business description, intended use, retention expectation, special conditions, and commit note remain text fields.

## Derived status rule

`agreement_status` is computed from `expiry_date`; it is not manually selected.

```text
agreement_status = "Active" if today <= expiry_date else "Inactive"
```

The record also stores `status_as_of_date` so downstream users can see when the status was evaluated.

## Required controls

- Keep `agreement_id` stable for the same real-world agreement.
- Validate required agreement fields before commit.
- Use ISO date format (`YYYY-MM-DD`) for `start_date` and `expiry_date`.
- Route metadata writes through the configured metadata target from `00_env_config`; do not rely on a default lakehouse for metadata tables.
- Keep the agreement layer generic and public-safe. Do not hardcode department names, source systems, tenant IDs, workspace IDs, internal URLs, or production screenshots.

## Downstream role

The `01` agreement metadata becomes the anchor for later profiling, DQ rules, lineage, and pipeline contract evidence. Later notebooks should attach their evidence to the approved `agreement_id` instead of redefining the agreement boundary.

## Out of scope

- Source profiling and analyst exploration.
- DQ rule proposal or approval.
- Pipeline contract enforcement.
- Lineage capture.
- Column classification / PII / sensitivity / access governance authoring beyond agreement-level metadata.

These belong in later workflow notebooks.
