# Metadata Dashboard

A full metadata dashboard is planned after v1.0.0. The current starter kit creates metadata evidence first, so teams have useful records before a dashboard exists.

Read [How FabricOps Works](index.md) first for the notebook workflow.

## Current v1.0.0 foundation

Today, the notebooks create metadata that can already support review and operations:

- `01_agreement` captures agreement, steward, and supporting evidence.
- `02_pipeline` writes profiles, lineage, guardrail results, output context, and run metadata evidence.
- `03_governance` saves guardrail review decisions for profiled tables.

## Planned visibility layer

![FabricOps metadata dashboard wireframe](../assets/fabricops-metadata-dashboard.png){ .full-width }

A future dashboard should make collected metadata easier to browse. It should not become the source of truth and it should not enforce production rules.

| Planned view | Purpose |
| --- | --- |
| Agreement overview | Show agreement status, owner, steward, and evidence coverage. |
| Pipeline evidence | Show recent `02_pipeline` profiles, lineage, guardrail results, and run context. |
| Governance review | Show guardrail review decisions from `03_governance`. |
| Support readiness | Show whether enough evidence exists for support and review. |

## Design principle

Keep the metadata tables as the source of evidence. A dashboard should report what notebooks and reviewers recorded; it should not imply that dashboard views approve rules or block pipeline runs.
