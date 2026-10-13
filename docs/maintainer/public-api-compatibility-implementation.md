# Public API compatibility dashboard implementation

## Goal

Extend the existing Public Function Call Flows dashboard with an API Compatibility view, backed by a separate generated `public-api-compatibility.json` contract. Do not change the v4 call-flow JSON schema.

## Canonical inputs

* `src/fabricops_kit/public_api.py` defines Live and Preview membership.
* Python source signatures and exports are authoritative.
* The previous published release tag is the comparison baseline, not the current main branch.
* `public-function-call-flows.json` is used only to derive affected callers.

## Companion contract

Generate `docs/reference/_data/public-api-compatibility.json` deterministically. Include schema version, base and head revisions, and one record per API with qualified name, lifecycle, old/new signature, parameter kinds and defaults, change classification, reasons, and impacted callers. Sort records and keys stably. Never hand-edit generated output.

## Compatibility rules

* Added optional keyword parameter: compatible.
* Added required parameter: potentially breaking.
* Removed or renamed parameter: potentially breaking.
* Positional-only, keyword-only, default, and variadic parameter changes must be analyzed conservatively.
* Removed Live API or Live to Preview demotion: breaking.
* Preview changes: warnings, not blocking.
* Annotation-only changes: informational unless validated to affect runtime behavior.
* Dynamic signatures or uncertain analysis: review required, not automatically safe.
* Semantic behavior changes remain the responsibility of tests and human review.

## Dashboard

Preserve all existing Call Flow behavior. Add an API Compatibility tab with release selector or displayed baseline, Live/Preview filters, summary counts, per-function signature diff, reasons, and impacted callers. Provide an explicit unavailable state if the companion JSON is missing.

## CI

Compare the proposed branch against the latest applicable published release. Fail on unapproved breaking Live API changes, report Preview changes as warnings, and publish a readable summary. Do not silently treat missing baselines as clean results. Document an explicit, reviewed override mechanism.

## Tests

Cover additions, removals, renames, positional and keyword parameter changes, defaults, variadics, lifecycle promotion/demotion, deterministic output, absent baseline, and unchanged existing dashboard rendering.

## Acceptance

The dashboard shows real comparison data, generator output is reproducible, and CI demonstrates both a passing compatible change and a failing breaking Live change.
