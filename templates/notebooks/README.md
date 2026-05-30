# Notebook templates

Run the minimal end-to-end sample in the canonical framework lifecycle:
1. `00_env_config` = runtime/environment paths and shared runtime configuration.
2. `01_da_agreement_template` = approved usage + agreement context + stewardship notes.
3. `02_ex_*` = exploration, profiling, AI-assisted proposals, and evidence capture for governance/pipeline handoff.
4. `03_pc_*` = deterministic enforcement from approved metadata.
5. `04_gov_*` = optional governance enrichment after profile evidence exists; review and write approved column context/classification metadata.
6. Seed/create the sample source table (`minimal_source`) from generated rows in notebook code, then run `02_ex_agreement_topic` and `03_pc_agreement_source_to_target` with `USE_SAMPLE_DATA = True`.

This proves the core flow: generated sample DataFrame -> persisted source table -> proposal evidence created in `02_ex` -> versioned agreement boundaries maintained in `01_da_<agreement>` and governance-approved metadata maintained in `04_gov_*` -> approved metadata loaded/enforced in `03_pc` -> valid/quarantine split -> output write.

Templates are copy ready, not source ready. For real projects, replace source paths, target paths, contract values, transformation logic, approval details, and lineage notes.

Local metadata fallback is optional for local-only runs. Set `USE_LOCAL_SAMPLE_METADATA = True` in both `02_ex` and `03_pc` when you need local metadata artifacts under `samples/end_to_end/_output/metadata`.

## Template notebook purposes
- `01_da_agreement_template.ipynb`: Captures standalone data-agreement intake and usage boundaries as append-only `METADATA_DATA_AGREEMENT` versions; its steward dropdown is maintained through active `METADATA_DATA_STEWARD` rows.
- `04_gov_agreement_dataset_table.ipynb`: Enriches table and column governance context from `METADATA_PROFILE_ROWS`, launches review widgets, and writes approved rows to `METADATA_COLUMN_CONTEXT` and `METADATA_COLUMN_GOVERNANCE`.
