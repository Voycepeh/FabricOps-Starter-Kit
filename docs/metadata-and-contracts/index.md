# Metadata and contracts

FabricOps Starter Kit is a lightweight, plug-and-play starter kit for governed, quality-checked, AI-ready notebooks in Microsoft Fabric.

FabricOps does not start by asking users to deploy a large metadata warehouse. It starts with the notebook workflow. Each notebook writes the metadata that matches its responsibility, and FabricOps assembles the approved metadata into agreement-level, table-level, and column-level views for dashboarding, handover JSON, and standards export.

The simplified story is:

```text
01 defines agreement.
02 profiles and discovers.
04 approves column business context and classifications.
03 enforces rules and produces runtime evidence.
All notebooks register traceability.
Handover assembles views and exports JSON/YAML payloads.
```

## Notebook-first metadata

Metadata is collected through notebooks, not through a heavy upfront metadata warehouse. Each notebook records the evidence that belongs to its workflow responsibility:

- `01_agreement_*` defines agreement scope, owners, usage, restrictions, SLA expectations, and the contract anchor.
- `02_ex_*` profiles and discovers table structure, data shape, candidate context, and candidate rules.
- `04_gov_*` approves column business context, descriptions, classifications, PII, sensitivity, and handling requirements.
- `03_pc_*` enforces approved rules, captures runtime DQ evidence, records drift and lineage, and prepares handover outputs.
- All notebooks register traceability so dashboards and handover exports can point back to the notebooks that produced or approved the evidence.

The metadata tables follow the workflow. They are governed source evidence for assembly, not a separate metadata warehouse design that users must deploy before they can use the starter kit.

## Handover and standards export

The final handover is generated from assembled views, not stored as another source metadata table. FabricOps assembles approved metadata and run evidence into agreement-level, table-level, and column-level views, then renders handover or standards-specific exports from those views.

Common generated outputs include:

1. Handover JSON
2. Markdown summary
3. ODCS YAML
4. OpenMetadata-compatible payload

ODCS YAML and OpenMetadata-compatible payloads are exports from the assembled views. They should be reproducible from the same approved metadata instead of becoming competing source-of-truth files.

## Page guide

| Page                  | Purpose                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------- |
| [Metadata Architecture](metadata-architecture.md) | Explains the notebook-driven metadata model, the 9 source metadata tables, and why each table exists. |
| [Assembled Views](metadata-columns.md) | Explains the agreement-level, table-level, and column-level views generated from the 9 source tables. |

<figure markdown>
  ![Notebook workflow showing agreement, exploration, pipeline contract, and governance evidence assembled into a FabricOps data contract](../assets/notebook-datacontract-flow.png){ .full-width }
  <figcaption>FabricOps data contracts are assembled from approved evidence across the notebook workflow.</figcaption>
</figure>
