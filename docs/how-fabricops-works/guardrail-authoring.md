# Governed guardrail authoring

FabricOps separates metadata ownership so each table has one clear purpose:

- `METADATA_DATA_CATALOGUE` stores observed table and column profiles plus current table governance policy fields.
- `METADATA_ENRICHMENT_RULES` stores reviewable enrichment intent and its review lifecycle.
- `METADATA_GUARDRAIL_RULES` stores guardrail rule intent across draft, pending governance review, active pending governance review, self-approved, governance-approved, rejected, inactive, and superseded states.
- `METADATA_GUARDRAIL_RESULTS` stores enforcement outcomes only.
- Approval logs are derived from append-only history in `METADATA_ENRICHMENT_RULES` and `METADATA_GUARDRAIL_RULES`.

## Table governance policy

Tables default to `governance_mode="ungoverned"` and `approval_policy="no_approval_required"` unless the selected catalogue context carries governed policy fields. Governed tables can require formal review while still allowing engineering to apply a rule immediately when pipeline continuity requires it. Immediate application makes the rule active pending governance review.

## 02 engineering authoring flow

This PR implements a basic runnable Fabric notebook widget flow. `widget_select_guardrail_target` renders an interactive target selector, reads catalogue targets, current rule history, and the latest governance policy, then returns a handover state. `widget_author_schema_freshness_profile_rules` renders schema, freshness, and profile behavior controls with preview/save actions. `widget_author_dq_rules` renders manual DQ authoring controls. Richer styling can come later; the current flow is intentionally small and composable.

For ungoverned tables, engineering-authored saves remain active and non-pending with `review_status="self_approved"`. For governed tables, authors can choose **Save draft** for inactive drafts, **Submit for governance review** for inactive pending records, or **Apply now** for active rules with `review_status="active_pending_governance_review"` and `requires_governance_review=true`.

DQ rule authoring is deterministic and reviewer-controlled in the public authoring widget.

## 03 governance review flow

`03_governance` uses `widget_review_guardrail_governance` to review enrichment and guardrail rows from the rule tables, approve pending records, reject records, replace records, deactivate approved records, and view history. Approval activates or confirms the record as `governance_approved`. Rejection, replacement, and deactivation preserve append-only history instead of deleting prior intent.

## Enforcement

Pipeline enforcement loads active rules only when their status is `self_approved`, `governance_approved`, or `active_pending_governance_review`. Draft, pending, rejected, inactive, and superseded rules are not enforced. Active pending review rules carry the runtime warning `Rule is active pending governance review.` so reviewers can identify rules that still need formal governance review.
