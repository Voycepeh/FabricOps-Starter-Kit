# `04_gov_<agreement>_<dataset>_<table>`

`04_gov_<agreement>_<dataset>_<table>` is the governance operations notebook.
It reviews tables produced by `03_pc` and writes approved governance metadata for enforcement and downstream use.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/04_gov_agreement_dataset_table.ipynb">Open template notebook</a>

## What this notebook covers

- Sensitivity classification.
- PII tagging and governance labels.
- Data classification and access classification.
- Retention/export flags.
- Governance exceptions and approval notes.

## What this notebook writes

- Approved governance metadata to metadata tables.
- Evidence that `03_pc` and downstream consumers can load as contract inputs.

## Stage positioning

- Runs after `03_pc` has produced table-level outputs and execution evidence.
- Keeps governance decisions in the governance stage, not in engineering execution notebooks.

## Required metadata routing

Always route metadata reads/writes through configured metadata targets (`read_lakehouse_table` / `write_lakehouse_table` with `CONFIG`, `env_name`, and `"metadata"`).
