# `01_da_<agreement>`

`01_da_<agreement>` is the high-level data-sharing definition notebook for one agreement.
It captures agreement metadata and approved control-plane evidence for downstream use.
It does **not** perform profiling, DQ authoring, or governance classification.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_da_agreement_template.ipynb">Open template notebook</a>

## What this notebook does

1. **Runtime bootstrap**
   - Runs `%run 00_env_config` so runtime settings and metadata routing come from shared `CONFIG`.
2. **Agreement definition**
   - Defines agreement identity, business purpose, scope, approved use, stewardship/ownership, and control-plane context.
3. **Controlled write behavior**
   - Use `save_to_metadata=False` for dry runs/testing.
   - Use `save_to_metadata=True` when approved agreement evidence is ready to persist.
   - Use `register_notebook_to_metadata=True` when notebook registration should be written to metadata.
4. **Agreement persistence**
   - Agreement rows are written to `METADATA_DATA_AGREEMENT`.
5. **Notebook registration**
   - Notebook registration goes to `METADATA_NOTEBOOK_REGISTRY` under the `agreement_id`.
6. **Downstream contract handoff**
   - Approved metadata evidence is consumed by `02_ex`, `03_pc`, and `04_gov`.

## Required controls

- Keep `agreement_id` stable for the same real-world agreement.
- Route metadata reads/writes through configured metadata targets:
  - `read_lakehouse_table(..., config=CONFIG, env=env_name, target="metadata", ...)`
  - `write_lakehouse_table(..., config=CONFIG, env=env_name, target="metadata", ...)`
- Do not rely on `spark.table("METADATA_*")` or default lakehouse assumptions.

## Out of scope

- Source profiling and analyst exploration.
- DQ rule proposal or approval.
- Column classification / PII / sensitivity / access governance authoring.

These belong in `02_ex` and `04_gov`.
