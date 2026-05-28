# Start

This page explains: the fastest execution path from install to evidence.
Use this when: you need a practical first run with clear next actions and outputs.
Next read: [Install](install.md), [Templates](notebook-structure.md), [Govern / Quality](data-quality-rules-system.md).

## Quick flow

`Install wheel → Open templates → Configure 00_env_config → Run 01/02/03/04 notebooks → Review generated evidence`

## First run checklist

| Step | Notebook/action | Purpose | Output | Next page |
| --- | --- | --- | --- | --- |
| 1 | Install wheel in Fabric environment | Enable reusable helper functions for templates. | Import-ready `fabricops_kit` runtime. | [Install](install.md) |
| 2 | Open/copy template notebooks | Create a working notebook set in your workspace. | Project-specific 00/01/02/03/04 notebooks. | [Templates](notebook-structure.md) |
| 3 | `00_env_config` | Configure environment-local paths and metadata routing. | Validated runtime config. | [Templates](notebook-structure/00-env-config.md) |
| 4 | `01_agreement_*` | Capture agreement scope, ownership, and usage intent. | Approved agreement metadata evidence. | [Templates](notebook-structure/01-data-sharing-agreement.md) |
| 5 | `02_ex_*` | Profile data and draft/review DQ rules. | Profile evidence and approved DQ rule metadata. | [Govern / Quality](data-quality-rules-system.md) |
| 6 | `03_pc_*` | Execute transforms and enforce approved controls. | Curated outputs, DQ enforcement results, lineage evidence. | [Govern / Metadata](metadata-and-contracts/index.md) |
| 7 | `04_gov_*` | Review classification/access governance context. | Approved governance metadata and review updates. | [Workflow](lifecycle-operating-model.md) |
| 8 | Review generated evidence | Confirm metadata + quality + lineage + contract readiness. | Reusable governed evidence for handover/deploy. | [Deploy](deployment-and-promotion.md) |
