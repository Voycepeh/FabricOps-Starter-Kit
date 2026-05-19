# `01_da_<agreement>`

`01_da_<agreement>` is the agreement-level approval notebook for one agreement.
It defines the source/agreement-level permission boundary and writes agreement evidence only.
It does **not** perform column-level governance enrichment.

Its operational template remains:

- `templates/notebooks/01_data_agreement_template.ipynb`

When copied into a project workspace, keep the notebook naming convention as `01_da_<agreement>`.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_da_agreement_template.ipynb">Open template notebook</a>

## What this notebook does

1. **Runtime bootstrap**
   - Runs `%run 00_env_config` so runtime settings and metadata routing come from shared `CONFIG`.
2. **Agreement metadata definition**
   - Defines agreement identity, approved usage context, ownership/stewardship, and agreement-level control evidence.
3. **Controlled write behavior**
   - Use `save_to_metadata=False` for dry runs/testing.
   - Use `save_to_metadata=True` when approval evidence is ready to persist.
   - Use `register_notebook_to_metadata=True` when notebook registration should be written to metadata.
4. **Agreement persistence**
   - Agreement rows are written to `METADATA_DATA_AGREEMENT`.
5. **Notebook registration**
   - Notebook registration goes to `METADATA_NOTEBOOK_REGISTRY` under the `agreement_id`.
6. **Downstream reuse**
   - `02_ex` and `03_pc` select and reuse the approved `agreement_id` and its agreement metadata.

## Required controls

- Keep `agreement_id` stable for the same real-world agreement.
- Route metadata reads/writes through configured metadata targets:
  - `read_lakehouse_table(..., config=CONFIG, env=env_name, target="metadata", ...)`
  - `write_lakehouse_table(..., config=CONFIG, env=env_name, target="metadata", ...)`
- Do not rely on `spark.table("METADATA_*")` or default lakehouse assumptions.

## Out of scope

- Column business context review and enrichment.
- Column classification / PII / confidentiality review and enrichment.
- Writes to `METADATA_COLUMN_CONTEXT` and `METADATA_COLUMN_GOVERNANCE`.

These belong in `04_gov_<agreement>_<dataset>_<table>`.

## Cross-notebook requirements

- Downstream notebooks (`02_ex`, `03_pc`, `04_gov`) must declare `agreement_id`.
- Downstream notebooks must validate `agreement_id` exists in `METADATA_DATA_AGREEMENT` before doing work.
- All notebooks should register in `METADATA_NOTEBOOK_REGISTRY` under `agreement_id` to avoid stray runs.
