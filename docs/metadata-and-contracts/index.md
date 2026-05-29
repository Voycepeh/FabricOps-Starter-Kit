# Metadata and contracts

FabricOps moves from **evidence collection to handover export**. Separate notebooks collect approved evidence into metadata tables, and the `handover` module assembles that evidence into final contract-ready artifacts.

FabricOps does **not** require users to manually maintain a standalone contract YAML. The governed source of truth is the approved metadata evidence captured by the notebook workflow and stored through the `metadata` module. YAML and OpenMetadata payloads are export views over that evidence, not the source record by themselves.

Next read: [Evidence to Handover](evidence-to-handover.md), [Metadata Columns](metadata-columns.md), [Quality](../data-quality-rules-system.md), [Notebooks](../notebook-structure.md).

<figure markdown>
  ![Notebook workflow showing agreement, exploration, pipeline contract, and governance evidence assembled into a FabricOps data contract](../assets/notebook-datacontract-flow.png){ .full-width }
  <figcaption>FabricOps data contracts are assembled from approved evidence across the notebook workflow.</figcaption>
</figure>

## Architecture in one sentence

Notebook templates collect approved agreement, profiling, business, governance, quality, lineage, drift, and runtime evidence into metadata tables; `metadata` loads that shared evidence; `handover` turns it into Markdown, FabricOps JSON, ODCS YAML, and OpenMetadata-compatible payloads.

## Evidence collection flow

| Stage | Notebook family | Evidence written | Owning module focus |
| --- | --- | --- | --- |
| Define | `01_agreement_*` | Agreement scope, owners, stewards, usage intent, access boundaries, and handover expectations. | Agreement helpers and metadata persistence. |
| Discover | `02_ex_*` | Profiles, schema/column evidence, business descriptions, AI-assisted suggestions, and candidate rules. | `data_profiling`, `business_context`, `data_quality`, `metadata`. |
| Enforce | `03_pc_*` | Pipeline contracts, DQ enforcement, write expectations, run evidence, and failure/quarantine outcomes. | `data_quality`, IO helpers, lineage, drift, metadata. |
| Monitor | `04_gov_*` | Classification reviews, sensitivity labels, drift checks, governance notes, and approval history. | `data_governance`, `drift`, `metadata`. |
| Handover | Handover/export step | Contract narrative, FabricOps JSON, ODCS YAML, and OpenMetadata-compatible payloads. | `handover`. |

## What the assembled handover contains

The handover artifact combines approved evidence into practical contract outputs that describe:

- **Domain and ownership**: business domain, accountable owner, steward, and review context.
- **Data assets**: tables, files, lakehouse objects, or governed assets in scope.
- **Schema and columns**: approved fields, types, descriptions, requiredness, and profiling evidence.
- **DQ rules and expectations**: accepted values, thresholds, regex checks, severity, review status, and enforcement outcomes.
- **Lineage and sources**: upstream inputs, transformations, downstream consumers, and traceability notes.
- **Classifications and sensitivity**: PII classification, confidentiality labels, reviewer notes, and handling context.
- **Operational evidence**: run results, drift checks, notebook registry, actor traceability, and handover action items.

## Module boundaries

- `metadata` is the evidence backbone: persistence, stable keys, notebook registry, and contract evidence loading.
- `handover` is the final artifact layer: assembly, rendering, and export.
- Domain modules (`data_profiling`, `business_context`, `data_governance`, `data_quality`, `data_lineage`, and `drift`) produce focused evidence that can be reviewed and approved before export.

See [Evidence to Handover](evidence-to-handover.md) for the proposed function boundaries and implementation backlog.

## Standards alignment

FabricOps targets compatibility with open metadata and data contract patterns without forcing a separate manual contract file.

- **FabricOps JSON** is the canonical machine-readable export of assembled approved evidence.
- **ODCS YAML** is a standards-oriented export view generated from approved evidence.
- **OpenMetadata-compatible payloads** are integration views for metadata platforms.
- **Markdown handover** is the junior-friendly human handover view.

FabricOps should be treated as OpenMetadata- and ODCS-compatible in target design until exporters are implemented and validated against the expected field names, schema, and platform behavior.
