# `01_da_<agreement>`

`01_da_<agreement>` is the standalone **Data Agreement Intake / Usage Boundary** notebook. It captures the human-approved agreement boundary and appends one immutable agreement-version row to the configured metadata lakehouse. It does **not** perform governance classification or review; those responsibilities remain in `04_gov_*`.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_da_agreement_template.ipynb">Open template notebook</a>

## Primary metadata tables

| Table | Grain | Purpose |
| --- | --- | --- |
| `METADATA_DATA_AGREEMENT` | One row per agreement version | Append-only agreement intake and usage boundary. |
| `METADATA_DATA_STEWARD` | One row per steward profile | Maintained setup table used to populate the intake dropdown. |

`00_env_config` owns environment bootstrap: it creates or checks both Delta tables in the configured metadata lakehouse and reports steward readiness. `01_da_*` is a form notebook: it calls `render_agreement_intake_app(...)`, and that framework helper handles commit-button wiring, create/update branching, widget reads, metadata collection, commit execution, and friendly output. Neither notebook seeds fake steward people. Before rendering the form, maintain real steward profiles in `METADATA_DATA_STEWARD` and mark selectable rows with `is_active = true`. If no active rows exist, `00_env_config` prints a clear readiness warning in warning mode and the intake form raises a clear setup error; strict validation mode makes `00_env_config` fail after printing the warning.

## Agreement identity and versioning

- `agreement_id` is the stable key.
- `contract_version` is the version key.
- **Create New Agreement** always generates a fresh `agreement_id` and `contract_version = "1.0.0"`, even if its entered fields match an older agreement.
- **Update Existing Agreement** requires an explicit selection from the latest-version dropdown, reuses that selected stable `agreement_id`, and increments the minor version, for example `1.2.0 → 1.3.0`.
- `agreement_name + source_system + allowed_consumer_type` remains the descriptive identity combination shown to users, but it never silently changes create mode into update mode.
- Existing rows are never overwritten. Each commit appends a new version row.
- Update mode lists only the latest row per `agreement_id` and pre-fills the latest values for editing.

## Intended notebook call flow

1. `00_env_config` assembles `CONFIG`, creates or checks the agreement metadata tables, and reports steward readiness.
2. `01_da_*` calls `render_agreement_intake_app(...)` to render the framework-managed intake form.
3. Downstream notebooks call `load_agreements(...)`, `select_agreement(...)`, and `get_selected_agreement()` to bind work to a committed agreement version.

## Runtime and routing controls

- The form uses `ipywidgets`, not `notebookutils.widgets`.
- Display rendering imports `IPython.display as ip_display`, avoiding any shadowing of Fabric display behavior.
- `committed_by` resolves from `notebookutils.runtime.context`: `userName`, then `userId`, then `unknown`.
- Metadata setup, steward reads, agreement reads, and agreement writes resolve `CONFIG.path_config.paths[env]["metadata"]` and use that lakehouse's OneLake path. No default attached lakehouse is required.
- Widget defaults are exposed through `CONFIG.data_agreement_config`, the `01_da`-specific `DataAgreementConfig` section explicitly assembled by `00_env_config`.
- The default notebook calls `render_agreement_intake_app(...)`. Advanced users may call `create_agreement_form(...)`, `read_agreement_form(...)`, `collect_agreement_metadata(...)`, and `commit_agreement_metadata(...)` directly only when customizing the workflow.

## Downstream role

Reusable selectors load the latest committed version per `agreement_id`. Notebooks `02_ex_*`, `03_pc_*`, and `04_gov_*` bind downstream evidence to both `agreement_id` and `contract_version`. Governance classification, review widgets, and approved governance controls stay in `04_gov_*`.
