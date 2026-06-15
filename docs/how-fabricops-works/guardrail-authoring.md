# Governed guardrail authoring

FabricOps separates metadata ownership so each table has one clear purpose:

- `METADATA_DATA_CATALOGUE` stores observed physical and profile evidence only.
- `METADATA_GUARDRAIL_RULES` stores guardrail rule intent across draft, proposed, self-approved, governance-approved, bypassed, rejected, and superseded states.
- `METADATA_GUARDRAIL_RESULTS` stores runtime enforcement outcomes only.
- `METADATA_GOVERNANCE_REVIEWS` stores table-level governance review and policy state.

## Table governance policy

Tables default to `governance_mode="ungoverned"` and `approval_policy="no_approval_required"` until the latest active row in `METADATA_GOVERNANCE_REVIEWS` marks the table governed. Governed tables can require normal approval or allow an approval bypass that creates a post-review queue.

## 02 engineering authoring flow

`02_pipeline` uses small composable widgets. `widget_select_guardrail_target` reads catalogue targets, current rule history, and the latest governance policy, then returns a handover state. `widget_author_schema_freshness_profile_rules` creates schema, freshness, and profile behavior rules. `widget_author_dq_rules` creates DQ rules in either `DQ_AUTHORING_MODE = "manual"` or `DQ_AUTHORING_MODE = "ai_suggest"`.

For ungoverned tables, engineering-authored rules are saved active with `review_status="self_approved"`. For governed tables, the default action saves inactive proposed rules. When the table policy allows bypass, “Skip approval and activate now” requires a reason and saves active rules with `review_status="bypass_active_pending_review"` and `requires_post_review=true`.

## 03 governance review flow

`03_governance` can mark a table governed or ungoverned, approve proposed rules, reject rules, supersede rules, and review bypassed active rules. Approval activates the rule as `governance_approved` and clears post-review requirements. Rejection and superseding deactivate the rule intent without deleting history.

## Runtime enforcement

Pipeline enforcement loads active rules only when their status is `self_approved`, `governance_approved`, `approved`, or `bypass_active_pending_review`. Draft, proposed, rejected, and superseded rules are not enforced. Bypassed active rules carry a warning in runtime outcome metadata so reviewers can identify rules that still require post-review.
