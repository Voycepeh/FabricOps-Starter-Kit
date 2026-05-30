# Metadata and contracts

## A shared promise between teams

A data contract is a clear, written, machine-readable promise between the teams that produce data and the teams that consume it. It explains:

- what data will be sent;
- what each field means;
- how fresh and complete the data should be;
- who owns the data; and
- what happens when something changes or breaks.

**In FabricOps, a data contract is not just documentation. It is a machine-readable agreement that describes what data is expected, who owns it, how fresh it should be, what quality rules apply, and what happens when the promise is broken.**

FabricOps Starter Kit supports governed, quality-checked, AI-ready notebooks in Microsoft Fabric. It gives teams a practical way to capture agreement metadata, collect evidence, approve rules, and produce reusable contract outputs without deploying a large metadata platform first.

## Without a contract

When expectations remain in meeting notes, spreadsheets, or people's heads:

- upstream fields can change without warning;
- dashboards can break or, worse, become silently wrong;
- analytics teams firefight instead of building useful products; and
- business users lose trust in the numbers.

The technical issue may look like a renamed column or a late file. The business issue is that teams no longer know what they can rely on.

## With a contract

A data contract creates a shared working agreement:

- producers agree what they will send;
- consumers know what they can rely on;
- notebooks validate incoming data against agreed expectations;
- bad data can be blocked, quarantined, or flagged; and
- changes are versioned and communicated.

The contract does not remove conversation between teams. It makes that conversation visible, reviewable, and easier to enforce consistently.

## What is inside a data contract?

A useful contract records both business expectations and technical checks.

| Contract area | What it answers |
| --- | --- |
| Dataset identity and owner | What dataset is this, and who is accountable for it? |
| Fields, types, descriptions, and business meaning | What is sent, how is it represented, and what does each field mean? |
| Required and optional fields | Which fields must always be present, and which may be omitted? |
| Freshness expectations | How often should data arrive, and when is it considered late? |
| Quality rules | What completeness, uniqueness, referential integrity, and business checks apply? |
| Allowed values or domains | Which codes, categories, ranges, or patterns are valid? |
| Upstream source | Where did the data come from? |
| Downstream consumers | Which reports, tables, teams, or AI use cases depend on it? |
| Change notice period | How much notice should consumers receive before a change? |
| Contract version | Which reviewed version of the promise is in force? |
| Severity and enforcement behaviour | Should a failed expectation block, quarantine, warn, or allow processing? |

The starter kit includes a source-controlled [dataset contract JSON schema](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/schemas/dataset_contract.schema.json). It provides a machine-readable starting point for dataset identity, sources, targets, refresh behaviour, keys, policies, quality rules, governance, contracts, and transformations. Teams can add dataset-specific context where needed while keeping the shared promise understandable.

## Where should the contract live?

Keep the contract close to the dataset or module it governs:

- the contract definition lives in the source-controlled repository;
- the shared schema lives under `src/fabricops_kit/schemas/`;
- dataset-specific contracts live beside the dataset, module, or configuration they govern; and
- notebooks load the relevant contract during ingestion or validation.

The contract should not only live in a documentation page. It should be used by the notebook or pipeline that processes the data. The recommended pattern is to review contract changes through pull requests so producers and consumers can see the same versioned agreement.

## Which notebook enforces it?

Enforcement can happen across multiple notebooks. The recommended pattern is:

| Notebook stage | Recommended contract checks |
| --- | --- |
| Ingestion | Check that raw incoming files or tables match the basic schema and include required columns. |
| Standardisation | Check renamed fields, types, allowed values, and the canonical shape. |
| Data quality | Check freshness, completeness, uniqueness, referential integrity, and business rules. |
| Publishing | Promote only trusted data that passed the required contract and data quality checks. |

The first hard gate should happen as early as possible in ingestion or standardisation. This stops a known contract breach from moving further downstream.

FabricOps currently uses notebook families rather than requiring one notebook per table row above. The `03_pc_*` pipeline-contract notebook is the deterministic production enforcement point for approved rules and runtime evidence. Teams can place early schema checks in the ingestion or standardisation segments of that pipeline. See [Notebook Structure](../notebook-structure.md) and the [`03_pc_*` pipeline-contract guide](../notebook-structure/03-pipeline-contract.md).

## How enforcement works

The recommended flow is intentionally simple:

1. Load data.
2. Load the relevant contract.
3. Compare actual columns, types, nullability, freshness, and rules with the expected contract.
4. Write validation results.
5. Fail, quarantine, warn, or allow processing based on severity.
6. Publish only if the data is trusted.

FabricOps already provides building blocks for approved data quality rules, pipeline checks, quarantine handling, drift evidence, and handover outputs. A team can enforce additional dataset-contract checks as it adopts this pattern. See the [Data Quality Rules System](../data-quality-rules-system.md) for the implemented AI-assisted review and deterministic enforcement workflow.

## How contracts evolve

Contracts should change deliberately, not silently:

- non-breaking changes can use a minor version change;
- breaking changes require a new major version or explicit approval;
- downstream consumers should be notified before breaking changes; and
- a `v1` to `v2` contract change should be visible and reviewable in a pull request.

A breaking change might remove a required field, change a field type, or alter an agreed meaning. A non-breaking change might add an optional field with a clear description. Teams should agree their notice period and approval path as part of the contract.

FabricOps agreement metadata is append-only: `agreement_id` remains stable and `contract_version` identifies the reviewed agreement revision. The existing `01_da_*` update flow increments minor versions. Teams introducing breaking-change workflows should use an explicit major-version and approval process rather than treating that current helper as automatic breaking-change management.

## AI-ready data still needs human approval

AI needs reliable, well-described, governed data. Data contracts give AI systems clearer metadata and expectations, making it easier to understand which fields exist, what they mean, and whether the data is suitable for use.

AI can assist by proposing field descriptions, quality rules, and contract changes from profiling evidence. Humans still approve the contract before enforcement. FabricOps keeps AI in the loop for drafting and keeps deterministic checks in the production path.

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

This notebook-first flow keeps the contract grounded in reviewed evidence instead of a disconnected documentation exercise. AI touchpoints can help draft descriptions, candidate rules, summaries, and handover text, but the operating workflow remains: collect evidence, approve it, enforce it, and assemble it into reusable outputs.

## What each notebook contributes

| Notebook | Contributes |
| --- | --- |
| 01 | Agreement metadata, including scope, owners, usage, restrictions, and service expectations. |
| 02 | Data catalogue and profile metadata from exploration and discovery. |
| 04 | Business context and governance metadata, including approved descriptions and classifications. |
| 03 | Data quality rules, data quality results, drift evidence, lineage, and handover preparation. |
| All | Notebook registry entries that preserve traceability across the workflow. |

## `01` agreement metadata capture

The standalone `01_da_*` notebook captures the intake and usage boundary in one primary append-only table: `METADATA_DATA_AGREEMENT`. Its grain is one row per agreement version. `agreement_id` is stable, while `contract_version` starts at `1.0.0` and increments by minor version for later revisions. Create mode always generates a fresh ID and `1.0.0`, even when entered descriptive identity fields match an older row. Update mode requires an explicit latest-version selection before it reuses an ID and increments its minor version.

The steward dropdown reads active rows from `METADATA_DATA_STEWARD`; setup creates the table empty and never seeds fake people. Widget defaults are owned by the `DataAgreementConfig` section from `00_env_config`. Notebook users call `setup_data_agreement_tables(...)`, `create_agreement_form(...)`, `collect_agreement_metadata(...)`, and `commit_agreement_metadata(...)`. Reads and writes route through `CONFIG.path_config.paths[env]["metadata"]`, so no default attached lakehouse is required.

## Source metadata versus assembled views

FabricOps separates source metadata evidence from assembled contract views:

```text
9 source metadata tables → 3 assembled views
```

The 9 source metadata tables capture workflow evidence from the notebooks. The 3 assembled views organize approved evidence into agreement-level, table-level, and column-level outputs for downstream use. Detailed source table columns live in [Metadata Architecture](metadata-architecture.md), and assembled view output fields live in [Assembled Views](metadata-columns.md).

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
| [Notebook Structure](../notebook-structure.md) | Explains the FabricOps notebook families and how they work together. |
| [Data Quality Rules System](../data-quality-rules-system.md) | Explains AI-assisted rule proposals, human approval, deterministic checks, and quarantine handling. |
| [Dataset contract JSON schema](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/schemas/dataset_contract.schema.json) | Provides the source-controlled machine-readable schema included with the starter kit. |
