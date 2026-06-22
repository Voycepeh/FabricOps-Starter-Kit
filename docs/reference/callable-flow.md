# Callable Flow Dashboard

AI coding tools make it easy to add callables quickly. That speed is useful, but it can also create too many entry points, thin wrapper callables, nested helpers, and uncontrolled dependencies. The Callable Flow Dashboard exists to make those relationships visible before the codebase becomes hard to maintain.

<div align="center" markdown="1">

[Open the interactive Callable Flow Dashboard](../assets/callable-functions-dashboard.html){ .md-button .md-button--primary }

</div>


## Why callable flow matters

FabricOps keeps notebook-facing APIs small and explainable. A callable should have a clear role in the role-aware callable model:

```text
Public API entrypoints → Internal workflows/adapters/validators/resolvers/services → Utilities/models/lifecycle helpers
```

Callable review is no longer based on a blanket “internal calls internal is bad” rule. The current classifier uses callable roles, architectural roles, reachability kinds, dependency roles, lifecycle handling, and layer consistency evidence to separate intentional implementation support from architecture drift.

- Public API entrypoints should remain stable notebook-facing surfaces.
- Internal workflows may orchestrate lower-level implementation roles.
- Validators, resolvers, normalizers, adapters, and services may support workflows when their direction is intentional.
- Utilities and model/lifecycle helpers should stay low-level and avoid depending upward on workflows.

This keeps public APIs stable, lets internal role calls support governed workflows when intentional, and still flags upward dependencies that can make implementation details harder to maintain.

## How the dashboard is generated

The dashboard is built from repository scans that inspect callable definitions and relationships. The scan produces callable relationship metadata in [`_data/callable-flow.json`](_data/callable-flow.json), and the visual dashboard uses that JSON to show caller and callee relationships, depth, reuse, and refactor recommendations.

Because the dashboard is generated from the codebase, it is a maintenance aid rather than a separate source of truth. Use it to decide where to inspect source code, update docstrings, flatten helper chains, or preserve shared helpers carefully.

## What the dashboard detects

Use the dashboard signals to find patterns that deserve review:

- workflow-to-workflow coupling
- utilities depending on project workflows
- validators/resolvers/models depending upward on workflows
- unknown or classification-pending roles
- unreachable or orphan candidates
- thin wrapper or inline candidates
- single-use helpers that need abstraction review
- high fanout helpers that should be protected
- implicit lifecycle and property accessor methods that should not be treated as ordinary orphans

## Refactor signals

Refactor signals are warnings generated from the callable graph. They do not automatically mean the code is wrong. Instead, they help guard against architecture drift from the intended role-aware hierarchy and identify where cleanup should be reviewed before changes are made.

### EG. Pointless wrapper

![Possible wrapper or inline candidates](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

*Guardrail: Warn when a helper appears to add little abstraction value. Single-use or thin wrapper callables may still be valid, but they should earn their place through clearer naming, validation, readability, or reuse.*

### EG. Large dependency surface

![Large dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

*Guardrail: Warn when a public callable depends on many nested helpers. This may be valid orchestration, but it increases the chance that a small helper change breaks a wider workflow.*

### EG. Messy callable dependency

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

*Guardrail: Warn when one public callable depends on another public callable. Public callables should usually be entry points. Shared logic should usually move into an internal helper or utility callable.*

### EG. Nested helper chain

![Nested helper chain](../assets/fabricops-bad-example-nested-functions.png)

*Guardrail: Warn when repeated workflow-to-workflow chains or upward dependency patterns make the architecture harder to reason about. Allowed internal role calls can be valid when validators, resolvers, normalizers, adapters, services, utilities, models, lifecycle hooks, or property accessors support the expected direction.*

## Selecting refactor candidates

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

*Selecting a focused cleanup set.*

The dashboard supports selecting callables with refactor signals so users can build a focused cleanup set. This narrows review to specific architecture guardrails instead of asking AI tools to reason over the whole codebase at once.

## Exporting an AI refactor prompt

![Exporting an AI refactor prompt](../assets/fabricops-select-refactor-candidates-prompt-export.png)

*Exporting a structured AI refactor packet.*

Selected callables can be exported as a structured AI refactor packet. The export gives AI tools the callable layer, callable_role, architectural_role, reachability_kind, dependency_role, change_risk, refined_recommended_action, layer_consistency, layer_consistency_label, architecture_signals, review_signals, review_status, review_status_label, used_by_count, calls_count, callers, callees, direct_internal_helpers, batch accounting, completion accounting, compatibility mode, safety constraints, and expected output so they can reason from architecture context instead of guessing from isolated code snippets.

??? example "Example exported AI refactor packet"

    ```text
    FabricOps callable refactor packet

    Prompt for AI

    You are reviewing a FabricOps callable refactor packet. Use the selected callables and call graph metadata to plan a safe cleanup. Group callables by refactor type, explain the rationale, identify risks, and propose an ordered implementation plan. Do not write code yet. Respect the compatibility mode in this packet. If compatibility_mode is stable_api_safe, preserve public API compatibility and call out migration risks. If compatibility_mode is internal_cleanup, preserve external behavior but allow internal signatures and helper boundaries to change when justified. If compatibility_mode is development_breaking_allowed, propose cleaner breaking changes where they improve the design. Batch accounting: report how many callables were selected, how many are intended for the current batch, how many were actually refactored in the PR, which selected callables were deferred, why each deferred group was deferred, and what the next suggested batch should be. Do not imply that all selected callables were refactored unless they were actually changed. If this PR handles only a subset, clearly label it as a batch and list the remaining selected callables as deferred. Completion accounting required in PR description: include selected / handled / remaining counts in the PR body and fill completed_or_refactored_count after implementation if it was unknown at export time. Always call out tests required before changes. Review the assigned layer against the usage evidence. Do not assume that a Utility layer is correct when used_by_count is low. Do not assume that a highly reused Internal helper must remain internal. Do not treat all internal-to-internal calls as violations. Only flag role-aware upward dependencies, workflow-to-workflow coupling, or project-callable dependencies from utility/model layers. Protect public APIs, lifecycle hooks, property accessors, model classes, and high-fanout shared services unless tests and caller review justify changes.

    Refactor context

    Intent: Plan safe cleanup for selected FabricOps helper callables.

    Mode: Planning only.

    Compatibility mode: Internal cleanup

    Batch accounting

    Selected callables: 1
    Planned batch count: 1
    Batch ID: batch-1
    Batch scope: All selected callables by default; narrow this before implementation when a smaller safe batch is intended.
    Batch strategy: Single batch by default. If implementation handles only a subset, group deferred selected callables by risk, ownership, or dependency order.
    Completed/refactored count: fill in after implementation
    Remaining selected count: fill in after implementation
    Deferred selected callables: none by default before implementation; list any selected callables not handled in this PR.

    Completion accounting required in PR description

    Include selected / handled / remaining counts in the PR body. Do not imply that all selected callables were refactored unless they were actually changed. If this PR handles only a subset, clearly label it as a batch and list the remaining selected callables as deferred. Explain why each deferred group was deferred and recommend the next batch.

    Selected callable actions:
    - Architecture violation

    Role-aware review guidance:
    - Review callable_role, architectural_role, reachability_kind, dependency_role, change_risk, refined_recommended_action, and layer_consistency before proposing changes
    - Do not treat all internal-to-internal calls as violations
    - Only flag role-aware upward dependencies, workflow-to-workflow coupling, or project-callable dependencies from utility/model layers
    - Protect public APIs, lifecycle hooks, property accessors, model classes, and high-fanout shared services unless tests and caller review justify changes

    Safety constraints:
    - Preserve external behavior
    - Internal helper names, signatures, and module boundaries may change if justified
    - Identify impacted callers before recommending changes

    Expected AI output:
    - Group selected callables by refactor type
    - Explain which callables are safe cleanup candidates
    - Identify callables that should not be refactored yet
    - Propose an ordered refactor plan
    - Report selected, intended batch, actually refactored, deferred, and remaining callable counts
    - List risks and required tests
    - Do not produce code changes unless explicitly requested

    Selected callables

    Callable 1: _audit_timestamp_expr

    Qualified name: fabricops_kit.config._audit_timestamp_expr
    Module: config
    Kind: function
    Layer: Internal helper
    Callable role: internal_resolver, shared_internal_service
    Architectural role: internal_resolver
    Reachability kind: public_reachable
    Dependency role: internal_resolver
    Change risk: medium
    Refined recommended action: Review upward dependency
    Used by count: 1
    Calls count: 1
    Layer consistency: Needs role-aware review
    Review status: Classified
    Architecture signals: workflow_to_workflow_coupling
    Review signals: role_aware_upward_dependency
    Recommended action: Architecture violation
    Priority: High
    Signal reason: Architecture violation: Callable dependency direction breaks the role-aware callable dependency rule.
    Callers:
    - profile_dataframe (data_profiling)

    Callees:
    - _get_audit_timezone (config)

    Source path: src/fabricops_kit/config.py
    ```

## Conclusion

The Callable Flow Dashboard is not only a dependency viewer. It is an architecture guardrail for keeping FabricOps maintainable as the kit grows.

The main rule is role-aware: public API entrypoints should remain stable notebook-facing surfaces, internal workflows may orchestrate intentional lower-level roles, and utilities/models/lifecycle helpers should stay low-level rather than depending upward on workflows. When a callable creates workflow-to-workflow coupling, an upward dependency, a project-callable dependency from a utility/model layer, a questionable abstraction, or a high-risk orphan signal, the dashboard should flag it for review before cleanup.

The exported refactor packet gives AI tools enough context to reason safely from the call graph instead of guessing from isolated code snippets. This makes the workflow useful for planned refactors, code review, and future architecture governance.
