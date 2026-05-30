# Metadata and contracts

## What this is

FabricOps Starter Kit is a lightweight, plug-and-play starter kit for governed, quality-checked, AI-ready notebooks in Microsoft Fabric.

FabricOps assembles data contract outputs from notebook-collected metadata evidence. It does not ask teams to deploy a large metadata warehouse before they can start. Instead, each notebook records the evidence that belongs to its workflow responsibility, and FabricOps assembles the approved metadata into agreement-level, table-level, and column-level views for dashboarding, handover JSON, and standards export.

## Notebook-first contract assembly

<figure markdown>
  ![Notebook workflow showing agreement, exploration, pipeline contract, and governance evidence assembled into a FabricOps data contract](../assets/notebook-datacontract-flow.png){ .full-width }
  <figcaption>FabricOps data contracts are assembled from approved evidence across the notebook workflow.</figcaption>
</figure>

The metadata and contract workflow starts with notebooks. The simple story is:

```text
01 defines agreement.
02 profiles and discovers.
04 approves business context and classifications.
03 enforces rules and produces evidence.
All notebooks register traceability.
Handover assembles JSON/YAML payloads.
```

This notebook-first flow keeps the contract grounded in reviewed evidence instead of a disconnected documentation exercise. AI touchpoints can help draft descriptions, candidate rules, summaries, and handover text, but the overview begins with the operating workflow: collect evidence, approve it, enforce it, and assemble it into reusable outputs.

## What each notebook contributes

| Notebook | Contributes |
| --- | --- |
| 01 | Agreement metadata, including scope, owners, usage, restrictions, and service expectations. |
| 02 | Data catalogue and profile metadata from exploration and discovery. |
| 04 | Business context and governance metadata, including approved descriptions and classifications. |
| 03 | Data quality rules, data quality results, drift evidence, lineage, and handover preparation. |
| All | Notebook registry entries that preserve traceability across the workflow. |

## `01` agreement metadata capture

The standalone `01_da_*` notebook captures the intake and usage boundary in one primary append-only table: `METADATA_DATA_AGREEMENT`. Its grain is one row per agreement version. `agreement_id` is stable, while `contract_version` starts at `1.0.0` and increments by minor version for later revisions. The same agreement identity is `agreement_name + source_system + allowed_consumer_type`.

The steward dropdown reads active rows from `METADATA_DATA_STEWARD`; setup creates the table empty and never seeds fake people. Widget defaults are owned by the `DataAgreementConfig` section from `00_env_config`. Notebook users call `setup_data_agreement_tables(...)`, `create_agreement_form(...)`, `collect_agreement_metadata(...)`, and `commit_agreement_metadata(...)`. Reads and writes route through `CONFIG.path_config.paths[env]["metadata"]`, so no default attached lakehouse is required.

## Source metadata versus assembled views

FabricOps separates source metadata evidence from assembled contract views:

```text
9 source metadata tables → 3 assembled views
```

The 9 source metadata tables capture workflow evidence from the notebooks. The 3 assembled views organize approved evidence into agreement-level, table-level, and column-level outputs for downstream use. This page intentionally stays light; detailed source table columns live in [Metadata Architecture](metadata-architecture.md), and assembled view output fields live in [Assembled Views](metadata-columns.md).

## Handover and standards export

The final handover is generated from assembled views, not stored as another source metadata table. FabricOps renders reusable outputs from the same approved metadata and run evidence so exports remain reproducible.

Common generated outputs include:

1. Handover JSON
2. Markdown summary
3. ODCS YAML
4. OpenMetadata-compatible payload

ODCS YAML and OpenMetadata-compatible payloads are exports from the assembled views. They should be reproducible from the same approved metadata instead of becoming competing source-of-truth files.

## Related pages

| Page | Purpose |
| --- | --- |
| [Metadata Architecture](metadata-architecture.md) | Explains the 9 source metadata tables, their columns, examples, and how notebook evidence is captured. |
| [Assembled Views](metadata-columns.md) | Explains the agreement-level, table-level, and column-level views and their output fields. |
