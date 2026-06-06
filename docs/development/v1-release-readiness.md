# v1.0.0 release readiness

Use this checklist before treating FabricOps Starter Kit v1.0.0 as ready for a public release or workspace handover.

## v1.0.0 scope statement

FabricOps v1.0.0 implements a Fabric-native starter kit for metadata setup, agreement intake, notebook registry, production notebook guardrails, profiling evidence, lineage, governance review, and handover.

The production control boundary is each `03_pc` notebook. Separate data contracts are not required. `04_gov` is a human review workflow for column context, DQ expectations, and classification metadata; it does not enforce production rules.

Governance DQ rules stored in metadata are reviewed expectations/advisory metadata unless manually implemented as guardrails inside the relevant `03_pc` notebook. AI suggestions are optional and advisory only.

## Implemented in v1.0.0

| Capability | Readiness check |
| --- | --- |
| Metadata lakehouse setup through `00_env_config` | Metadata tables are created or validated in the configured metadata target. |
| Data agreement, steward, and evidence tables | `01_da` can write and version agreement metadata. |
| Notebook registry | `02_ex` and `03_pc` registrations can be written and reviewed. |
| Production notebook template with schema validation and data-change monitoring | `03_pc` can pass normal runs and stop deliberate blocking failures. |
| Lakehouse and warehouse IO helpers | Read/write helpers work with configured Fabric targets. |
| Profiling/catalogue evidence | `02_ex` and `03_pc` profile evidence appears in metadata. |
| Lineage records | `03_pc` writes source-to-target lineage metadata. |
| Table-scoped governance review | `04_gov` can select a catalogue table for review. |
| Human-reviewed column context, DQ expectation, and classification metadata | `04_gov` commits reviewed metadata without relying on AI. |
| Handover summary support | Production notebook evidence and metadata can support handover notes. |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Full Fabric validation notes from real workspace testing | Expand and publish validation evidence from representative workspaces. |
| Governance dashboard improvements | Improve reporting assets and view guidance. |
| Optional metadata-driven DQ rule execution | Allow reviewed metadata rules to be executed by opt-in pipeline patterns. |
| Rule promotion workflow | Promote approved expectations into implemented production notebook guardrails. |
| Richer AI-assisted governance suggestions | Keep suggestions advisory and human-reviewed. |
| More complete operational monitoring | Add broader run health, alerting, and support visibility. |

## Fabric validation checklist

Run these checks in a Microsoft Fabric workspace before release sign-off:

1. Install the release wheel in a Fabric Environment.
2. Attach the Environment to copied `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov` notebooks.
3. Run `00_env_config` and confirm metadata tables are created or validated in the configured metadata lakehouse.
4. Run `01_da` and confirm data agreement, steward, and evidence metadata writes succeed.
5. Run `02_ex` and confirm example source/topic setup writes catalogue/profile evidence.
6. Run `03_pc` and confirm implemented schema/data-change guardrails pass, outputs are written, profiles are recorded, lineage is written, and run evidence is available.
7. Run `04_gov` and confirm human-reviewed column context, DQ expectation, and classification metadata can be committed.
8. Rerun `03_pc` and confirm it still passes implemented guardrails.
9. Deliberately introduce a blocking schema change and confirm `03_pc` stops.
10. Deliberately introduce a blocking data-change scenario and confirm `03_pc` stops when the preset and baseline require it.
11. Confirm AI suggestions, if enabled, remain optional and are not committed without human action.
12. Confirm no real data, secrets, tenant/workspace identifiers, internal URLs, or production screenshots are included in release docs or examples.

## Known v1 limitations

- `04_gov` does not enforce production rules.
- Governance DQ rules in metadata are advisory unless manually implemented in `03_pc`.
- Metadata-driven DQ rule execution is planned after v1.0.0.
- Rule promotion from reviewed metadata into notebook guardrails is planned after v1.0.0.
- Dashboard assets and operational monitoring are starter guidance, not a complete monitoring platform.
- Fabric validation evidence should be expanded as more real workspace testing is completed.
