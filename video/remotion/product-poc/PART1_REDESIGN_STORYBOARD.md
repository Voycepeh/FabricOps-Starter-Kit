# FabricOps Part 1 redesign storyboard

Status: **Proposal for approval. Animation implementation is paused.**

This storyboard replaces the assumption that the existing Part 1 scene structure must be preserved. Preserve FabricOps' technical accuracy and approved messaging, but do not preserve the original video's scene structure, layouts, text density or animation patterns by default. Redesign them where a clearer visual explanation is possible.

The proposed story has three acts:

1. **Why FabricOps?** Establish the gap between a working notebook and a governed Production workflow.
2. **How it works** Explain the small operating model: environment configuration, Governance, pipeline, Data Contracts and Guardrails.
3. **See it in action** Demonstrate a governed read, project-owned PySpark transformation, governed write, contract authoring, validation, activation, Production run and consumer hand-off.

The seven-step lifecycle remains the factual backbone, not the visual layout. A restrained progress rail can locate each demonstrated action without forcing the viewer to study all seven steps at once.

## Proposed running order

Target duration: approximately 3 minutes 23 seconds. Final timings should follow the approved narration rather than force the narration into the current edit.

| Time | Chapter | Story beat | What the viewer sees | Technical fact carried | Motion and reading hold |
| --- | --- | --- | --- | --- | --- |
| 00:00-00:16 | Why FabricOps? | A notebook can move data, but Production also needs shared governance decisions and evidence. | One simple notebook flow reaches a Production boundary and pauses. Governance requirements appear as three concise questions: approved use, expected quality, sensitive treatment. | FabricOps packages reusable notebooks, governed read/write orchestration, Data Contracts, Data Agreements and shared metadata for Microsoft Fabric workflows. | Build the notebook flow in under 0.6 seconds, then hold the unresolved boundary for 3 seconds. No ambient drift. |
| 00:16-00:36 | Why FabricOps? | FabricOps connects Governance and Engineering without replacing either discipline. | The same notebook remains central. Governance contributes an approved definition; Engineering contributes the transformation. They meet at the read/write boundaries. | Governance as code means structured FabricOps metadata is resolved during validation and execution. Project-owned PySpark remains in the Transform. | Two short directional moves, then a 3-second completed-system hold. Avoid orbiting labels and floating keywords. |
| 00:36-00:58 | How it works | Three notebooks have distinct responsibilities. | A compact workspace view introduces `00_env_config`, `01_governance` and `02_pipeline` one at a time. The Data Contract connects Governance to the pipeline; it is not another notebook. | `00_env_config` resolves environment-specific Fabric locations. Governance authors Data Agreements, Data Contracts, Enrichment and Guardrails. The pipeline uses Read / Transform / Write. | Each item enters in 0.4-0.5 seconds. The complete operating model holds still for 4 seconds. |
| 00:58-01:27 | See it in action | Run a normal engineering workflow through governed boundaries. | A real code-oriented demonstration: `orchestrate_read(...)` returns the source DataFrame and governed identity; a short PySpark selection/derivation transforms it; `orchestrate_write(...)` receives the transformed DataFrame, contributing source result and selected contracts. | The Read can evaluate applicable Freshness, Schema and Data Quality Guardrails and profile a full source. The Write checks Schema, Sensitive Data, Source Drift, Data Quality and Guardrail Coverage before publication. | Animate only the active stage. After Read, Transform and Write each resolves, freeze the result for 2-3 seconds. Do not keep particles or connectors moving during explanation. |
| 01:27-01:58 | See it in action | Governance turns observed context into an explicit, reviewable contract. | The target table opens as a focused contract editor. `customer_id` receives an information classification, then a separate **Mask** Sensitive Data treatment. A business requirement—“Order net amount must not exceed quantity multiplied by unit price”—resolves to a proposed `custom_expression`. A reviewer confirms it before it is added. | Classification is descriptive Enrichment. Mask is an executable Sensitive Data Guardrail applied before write. Business rules resolve to deterministic Data Quality rules where possible; `custom_expression` is the reviewed fallback. | Use a before/after column treatment, not a text list. Stop completely on the masked result and reviewed rule for at least 3 seconds each. |
| 01:58-02:28 | See it in action | Validate the frozen candidate against clean and deliberately dirty data. | The exact frozen Data Contract is selected in **Validate** mode. A clean row passes. A deliberate rule violation is highlighted; Warn records the result, then Block visibly stops the path before publication. Guardrail Coverage confirms the complete governed source-to-target path. | Validate runs the same relevant Guardrail path but returns `published=False`. Warn can continue; Block stops at the failed Guardrail. Guardrail Coverage is the pre-publication readiness gate. Frozen versions are immutable. | One controlled state change per result. Hold PASS, WARN and BLOCK states separately. No pulsing status badges. |
| 02:28-02:53 | See it in action | Approve what was tested and promote the same engineering artifact. | The tested frozen version links to the exact Data Agreement version and becomes Activated. The validated notebook moves from Development to Production while `00_env_config` switches the logical Fabric Store locations. | Production resolves the single active Data Contract for the governed `table_id`. Activation and engineering promotion are distinct actions. Environment-specific identifiers remain in `00_env_config`. | A short two-step hand-off: Activate, then Promote. Hold the final Development/Production mapping for 3 seconds. |
| 02:53-03:12 | See it in action | Run the promoted workflow in Production and publish governed output. | The earlier Read / Transform / Write demonstration repeats in compressed form. Guardrails pass, the target publishes, and the result exposes compact evidence chips for profile, lineage and Guardrail results. | A successful write records source/target participation in `METADATA_DATA_LINEAGE`; profiles are stored in `METADATA_DATA_PROFILED` and, where applicable, `METADATA_DATA_PROFILED_FREQUENCY`; Guardrail outcomes are stored in `METADATA_GUARDRAIL_RESULTS`. Source Observation history is committed through the successful write path. | Reuse familiar states rather than invent new diagrams. The published target and evidence hold still for 4 seconds. |
| 03:12-03:22.9 | Close | Governed Production data is ready for approved consumers; continue into the Guided Demo. | The approved Production table becomes the single focal object. Its governed context resolves around it, then the frame simplifies to the FabricOps wordmark and Guided Demo action. | Consumers use approved Production data through native Fabric permissions and interfaces. FabricOps provides the governed workflow and context; it does not replace Fabric access control. | One reveal, one 4-second final hold. No end-frame zoom or background animation. |

## Seven-step backbone mapping

| Lifecycle step | Where it appears in the redesigned story |
| --- | --- |
| 1. Data Stewards and Data Agreement | Introduced as approved use in the opening; exact Data Agreement linkage is shown before activation. |
| 2. ETL, Profile and Catalogue | Demonstrated in the governed Read / Transform / Write sequence. |
| 3. Author Data Contract | Expanded into the classification, Sensitive Data treatment and reviewed business-rule demonstration. |
| 4. ETL with Contract Guardrails | Expanded into clean validation, deliberate failure, Warn / Block and Guardrail Coverage. |
| 5. Activate and Promote | Shown as two distinct approvals/actions. |
| 6. Run Production Pipeline | Reuses the established workflow with the active Production contract. |
| 7. Consume approved Production data | Closes on the governed Production table and consumer hand-off. |

## Visual system

- Use a single 16:9 stage with a stable coordinate system. Camera moves only to change the subject and completes in 0.3-0.7 seconds.
- Follow **Move -> Settle -> Hold -> Transition**. A completed explanation must have a genuinely static 2-4 second reading hold.
- Use code only when it demonstrates the product boundary. Keep the visible Read, Transform and Write calls short enough to read.
- Replace capability lists with state changes: unresolved -> governed, raw identifier -> masked representation, clean -> warning -> blocked, frozen -> activated, Development -> Production.
- Keep supporting metadata visually subordinate. Do not place all `METADATA_*` tables on screen at once.
- Do not use perpetual grain, drifting cameras, idle bobbing, orbiting labels, looping tracers, pulsing badges or decorative particles.
- Quantize settled positions to whole pixels. Deterministic frame-based transitions must end at fixed values.
- Use sound only to acknowledge meaningful state changes; silence is acceptable during reading holds.

## Accuracy guardrails for production

- Do not depict information classification as enforcement. The **Mask** treatment comes from a Sensitive Data Guardrail.
- Do not depict a business sentence becoming active without review. Show the resolved deterministic rule and reviewer confirmation.
- Do not imply that Validate publishes a target; its result remains `published=False`.
- Do not imply that a frozen Data Contract is already active. Activation follows successful Development validation and links the exact Data Agreement version.
- Do not imply that FabricOps owns arbitrary business transformation logic. The project owns the PySpark Transform.
- Do not imply that FabricOps replaces native Microsoft Fabric permissions or deployment controls.
- When persisted outputs are named, use their exact implemented `METADATA_*` table names.

## Approval gates before implementation

1. Approve the three-act structure and the approximate time allocation.
2. Approve the two hero demonstrations: `customer_id` Mask treatment and the reviewed order-net-amount business rule.
3. Approve how much code is visible in the Read / Transform / Write demonstration.
4. Approve the proposed narration rewrite and confirm whether the target remains approximately 202.9 seconds.
5. Only then replace the current motion experiment with new scene components and a new timeline.

## Planned validation after approval

- Render the complete video twice: a review pass, corrections, then a final pass.
- Define at least one named static hold for every storyboard beat.
- Render consecutive lossless frames inside every static hold and require pixel-identical primary content and camera geometry.
- Generate 2-second contact sheets plus frames 0.5 seconds before, at and after every transition.
- Review the complete MP4 with narration and sound, not only isolated frames.
- Publish the corrected full MP4, contact sheets, hold-verification report and timestamp review guide through the existing PR workflow.
