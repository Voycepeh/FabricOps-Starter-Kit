# Metadata and contracts

FabricOps Starter Kit turns notebook evidence into contract-ready handover artifacts for governed, quality-checked, AI-ready notebooks in Microsoft Fabric.

The section follows one product story:

```text
Separate notebooks.
Shared metadata evidence.
Curated decisions plus run observations.
Assembled handover contract.
Standards-compatible export.
```

## What problem does this solve?

Data handover breaks down when each lifecycle stage keeps its own notes, spreadsheet, YAML file, or screenshots. Agreement scope, profiling evidence, governance classifications, DQ rules, run results, drift findings, and lineage notes can quickly become disconnected.

FabricOps solves this by making approved metadata evidence the governed source of truth. Separate notebooks collect evidence at the point where the evidence is created or reviewed. The final contract is assembled later from that shared evidence rather than manually rewritten from memory.

## Why assemble contracts instead of writing them manually?

A manually maintained contract file is easy to drift away from what actually happened in Fabric. FabricOps avoids treating one YAML file, one spreadsheet, or one giant JSON blob as the source of truth. Instead, the contract is reproducible from approved evidence:

- Agreement, classification, business meaning, and DQ rules are governed decisions.
- Profiling, drift, DQ execution, lineage, and run results are evidence observations.
- The final contract is assembled from both.

FabricOps separates metadata storage by lifecycle. Human-owned decisions such as agreements, classifications, business context, and DQ rules are stored as curated metadata. Machine-generated observations such as profiling, DQ results, drift checks, lineage, and run summaries are stored as evidence facts. The handover layer assembles both into contract-ready outputs.

The core architecture rule is:

```text
Standalone curated tables = human-owned decisions.
Collapsed fact/evidence tables = machine/run observations.
Views and exports = assembled outputs, not source of truth.
```

## Role of `metadata`

The `metadata` module is the evidence backbone. It owns metadata evidence persistence, stable keys, notebook registry evidence, and planned evidence-loading boundaries for contract assembly. It is responsible for keeping separate notebook outputs joinable through agreement, table, column, rule, notebook, and run keys.

In the target architecture, `metadata` loads approved evidence by agreement, dataset, table, and optional run. It should not render final handover documents itself. Its job is to make the evidence reliable, traceable, and reusable.

## Role of `handover`

The `handover` module is the final artifact layer. It assembles loaded metadata evidence into human-readable and machine-readable outputs:

1. Markdown handover
2. FabricOps contract JSON
3. ODCS YAML
4. OpenMetadata-compatible payloads

The exported files are views over approved evidence. They are not the governed source of truth by themselves.

## ODCS and OpenMetadata export model

FabricOps is designed so standards-compatible outputs can be generated from the same approved evidence bundle. ODCS YAML and OpenMetadata-compatible payloads should be reproducible export views over curated decisions and run observations:

- ODCS YAML maps agreement, asset, column, and DQ expectation evidence into a data-contract-shaped artifact.
- OpenMetadata-compatible payloads map asset, column, classification, quality, lineage, and ownership evidence into metadata-platform-friendly records.
- FabricOps JSON remains the canonical machine-readable FabricOps handover artifact assembled from the same evidence.

## Page guide

| Page | Purpose |
| --- | --- |
| [Evidence to Handover](evidence-to-handover.md) | Explains the notebook-to-metadata-to-export workflow. |
| [Metadata Architecture](metadata-architecture.md) | Explains the source tables, facts, keys, relationships, and assembled views. |
| [Metadata Columns](metadata-columns.md) | Explains the column catalogue view assembled from the metadata architecture. |

<figure markdown>
  ![Notebook workflow showing agreement, exploration, pipeline contract, and governance evidence assembled into a FabricOps data contract](../assets/notebook-datacontract-flow.png){ .full-width }
  <figcaption>FabricOps data contracts are assembled from approved evidence across the notebook workflow.</figcaption>
</figure>
