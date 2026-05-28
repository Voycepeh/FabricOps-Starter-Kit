# `03_pc_<agreement>_<pipeline>`

`03_pc_<agreement>_<pipeline>` is the engineering source-to-target pipeline contract notebook.
It transforms source data to target outputs, enforces approved metadata rules, and writes operational evidence.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_pc_agreement_pipeline_template.ipynb">Open template notebook</a>

## What this notebook does

1. **Load shared config and contract metadata**
   - Initialize shared runtime.
   - Load approved metadata contract inputs from `01_da`, `02_ex`, and `04_gov`.
2. **Source-to-target engineering pipeline execution**
   - Read source tables, apply transformations, and prepare target model outputs.
3. **Rule and governance enforcement**
   - Enforce approved DQ rules.
   - Load and enforce approved governance metadata where applicable.
4. **Operational evidence writing**
   - Write run summary, transformation summary, lineage evidence, and enforcement evidence to metadata targets.

## Scope boundaries

- This notebook consumes approved rules and metadata; it does not author governance classifications.
- Governance classifications (sensitivity, PII, labels, access classifications) are authored in `04_gov`.

## Metadata contract requirements

- Treat metadata tables as contract inputs owned by 01/02/04.
- Validate required agreement/governance/DQ metadata exists before final publish.
- Route metadata operations through configured metadata targets, not default-lakehouse access.
