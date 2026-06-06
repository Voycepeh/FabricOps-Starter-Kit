# Table-scoped governance

`04_gov` is the FabricOps v1.0.0 human review workflow for one catalogue table at a time.

It uses catalogue/profile evidence written by `02_ex` or `03_pc`, lets reviewers add or approve column context, DQ expectations, and classification metadata, and commits those decisions to the configured metadata lakehouse.

## v1.0.0 boundary

`04_gov` does not enforce production rules. It does not block pipelines, mutate production data, or change `03_pc` output behavior.

Governance DQ rules stored in `METADATA_DQ_RULES` are reviewed expectations/advisory metadata in v1.0.0 unless a team manually implements them as guardrails inside the relevant `03_pc` notebook.

Separate data contracts are not required for v1.0.0. Data agreements remain available from `01_da`, but `04_gov` can review a catalogue table without requiring a separate agreement relationship.

AI suggestions are optional and advisory only. A human reviewer must explicitly commit any accepted metadata.

## Implemented in v1.0.0

| Area | Implemented behavior |
| --- | --- |
| Table selection | Selects from `METADATA_DATA_CATALOGUE`. |
| Column context review | Commits reviewed business context to `METADATA_COLUMN_CONTEXT`. |
| DQ expectation review | Commits reviewed expectations to `METADATA_DQ_RULES` as advisory metadata. |
| Classification review | Commits reviewed PII and sensitivity decisions to `METADATA_COLUMN_CLASSIFICATION`. |
| AI assistance | Can draft suggestions when configured, but suggestions remain editable and advisory. |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Optional metadata-driven DQ rule execution | Let `03_pc` notebooks opt into executing reviewed metadata rules. |
| Rule promotion workflow | Promote reviewed expectations into implemented production guardrails. |
| Governance dashboard improvements | Improve reporting over reviewed context, expectations, and classifications. |
| Richer AI-assisted review | Improve suggestions while keeping humans accountable for commits. |

## Review workflow

1. Select a catalogue table created by `02_ex` or `03_pc`.
2. Review observed columns, profiles, and existing metadata.
3. Optionally generate AI suggestions where configured.
4. Edit, approve, reject, or defer suggested context, expectations, and classifications.
5. Commit reviewed metadata to the relevant metadata tables.
6. If a DQ expectation should become enforceable, manually implement the check inside the relevant `03_pc` notebook and smoke test the failure behavior.

## Enforcement boundary

For v1.0.0, `03_pc` is the production guardrail notebook. `04_gov` supplies reviewed metadata that helps people understand and improve production notebooks, but it is not itself an enforcement engine.
