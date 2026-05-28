# `02_ex_<agreement>_<topic>`

`02_ex_<agreement>_<topic>` is the analyst notebook for profiling, exploration, and analysis.
It turns observed data behavior into approved, metadata-backed DQ rules for engineering enforcement.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_ex_agreement_topic.ipynb">Open template notebook</a>

## What this notebook does

1. **Load shared config and runtime**
   - Initialize with shared configuration from `00_env_config`.
2. **Analyst-led profiling and analysis**
   - Profile source data, assess quality patterns, and capture analysis evidence for the scoped topic.
3. **DQ proposal and approval loop**
   - Draft candidate DQ rules, review them with explicit approve/reject decisions, and finalize approved rules.
4. **Metadata persistence for enforcement**
   - Write approved DQ rules to metadata tables so `03_pc` can load and enforce them deterministically.

## Scope boundaries

- This notebook is where DQ rules are proposed and approved.
- This notebook does not own source-to-target publishing or enforcement execution (that is `03_pc`).
- This notebook does not author governance classification decisions (that is `04_gov`).

## Required metadata routing

Always route metadata reads/writes through configured metadata targets (`read_lakehouse_table` / `write_lakehouse_table` with `CONFIG`, `env_name`, and `"metadata"`).
