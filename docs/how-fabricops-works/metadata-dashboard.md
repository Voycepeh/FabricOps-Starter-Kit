# Metadata Dashboard

A full metadata dashboard is planned after v1.0.0. FabricOps v1.0.0 creates the metadata foundation, but it does not ship a complete dashboard experience.

Read [How FabricOps Works](index.md) first. This page explains the future visibility layer that can sit over the metadata-backed notebook workflow.

## v1.0.0 foundation

The v1.0.0 notebooks create useful metadata even without a complete dashboard:

- `01_da` captures agreement, steward, and evidence context.
- The notebook registry records notebook participation.
- `03_pc` writes profile evidence, lineage, output evidence, and run summaries.
- `04_gov` commits reviewed column context, DQ expectations, and classifications.

This evidence can support handover and manual review today. A dashboard can make the same evidence easier to browse later.

## Planned visibility layer

![FabricOps metadata dashboard wireframe](../assets/fabricops-metadata-dashboard.png){ .full-width }

A future dashboard should be a visibility layer over collected metadata, not a separate source of truth.

| Planned view | Purpose |
| --- | --- |
| Agreement overview | Show agreement status, owner, steward, and coverage. |
| Production evidence | Show recent `03_pc` profile, lineage, guardrail, output, and run-summary evidence. |
| Governance review | Show reviewed column context, DQ expectations, and classifications from `04_gov`. |
| Handover readiness | Show whether enough evidence exists for support and operational handover. |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Metadata dashboard visibility layer | Build a complete dashboard experience over collected metadata. |
| Richer governance dashboard views | Improve views for classifications, DQ expectations, agreement coverage, and lineage. |
| Optional metadata-driven DQ rule execution | Show execution results if future pipelines opt into metadata-driven rules. |
| Rule promotion workflow | Show which reviewed expectations have been implemented as `03_pc` guardrails. |
| Richer AI-assisted review | Surface AI suggestions and human approval status clearly. |
| More complete operational monitoring | Add broader run health and support visibility. |

## Design principle

Keep the metadata tables as the source of evidence. Any dashboard should report what the notebooks and reviewers recorded; it should not imply that dashboard views enforce production rules.
