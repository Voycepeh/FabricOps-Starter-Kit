# Start

This page explains: the quickest way to run FabricOps Starter Kit end-to-end.
Use this when: you want a practical first run with clear outputs at each step.
Next read: [Install](install.md), [Templates](notebook-structure.md), [Govern / Quality](data-quality-rules-system.md).

!!! tip "Dominant onboarding path"
    **Install Wheel → Copy Notebook Templates → Configure `00_env_config` → Run Notebooks → Review Generated Evidence → Deploy Later**

<div class="home-cta" markdown="1">

[Copy Notebook Template](notebook-structure.md){ .md-button .md-button--primary }
[Install Wheel](install.md){ .md-button }

</div>

## First run steps

| Step | Notebook/action | Purpose | Output | Next page |
| --- | --- | --- | --- | --- |
| 1 | Install wheel in Fabric Environment | Enable reusable helper functions. | Import-ready `fabricops_kit` runtime. | [Install](install.md) |
| 2 | Copy notebook templates | Create a working 00/01/02/03/04 notebook set. | Project-specific starter notebooks. | [Templates](notebook-structure.md) |
| 3 | `00_env_config` | Configure environment-local paths and metadata routing. | Validated runtime configuration. | [Template: 00_env_config](notebook-structure/00-env-config.md) |
| 4 | `01_agreement_*` | Capture scope, ownership, and intended usage. | Approved agreement metadata evidence. | [Template: 01](notebook-structure/01-data-sharing-agreement.md) |
| 5 | `02_ex_*` | Profile data and draft/review DQ rules. | Profile evidence + approved DQ rule metadata. | [Govern / Quality](data-quality-rules-system.md) |
| 6 | `03_pc_*` | Run transforms and deterministic enforcement. | Curated outputs, DQ enforcement results, lineage evidence. | [Template: 03](notebook-structure/03-pipeline-contract.md) |
| 7 | `04_gov_*` | Review classification/access governance context. | Governance approvals and metadata updates. | [Template: 04](notebook-structure/04-governance-operations.md) |
| 8 | Review generated evidence | Validate contract-ready evidence package. | Reusable evidence for handover and deployment. | [Deploy](deployment-and-promotion.md) |
