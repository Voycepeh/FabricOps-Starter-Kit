# Callable Flow Dashboard

AI coding tools make it easy to add callables quickly. That speed is useful, and it needs clear architecture guardrails. The Callable Flow Dashboard shows entry points, thin wrappers, nested helpers, and cross-layer dependencies so maintainers can plan focused cleanup work.

<div align="center" markdown="1">

[Architecture](../assets/callable-functions-dashboard.html){ .md-button .md-button--primary }
[Inventory](../assets/callable-functions-inventory.html){ .md-button }

</div>


## Why callable flow matters

FabricOps keeps notebook-facing APIs small and explainable. A callable should have a clear role in the role-aware callable model:

```text
Public API entrypoints → Internal workflows/adapters/validators/resolvers/services → Utilities/models/lifecycle helpers
```

Callable review is role-aware. Internal-to-internal calls are valid when the dependency direction is intentional and the helper role is clear. The classifier distinguishes public API entrypoints, internal workflows, adapters, validators, resolvers, normalizers, services, utilities, model classes, lifecycle methods, property accessors, reachability kinds, dependency roles, and allowed internal role calls.

The intent is:

- Public API entrypoints should remain stable notebook-facing surfaces.
- Public API callables may be heavier when that makes the code easier to follow.
- Internal workflows may orchestrate lower-level implementation roles.
- Validators, resolvers, normalizers, adapters, and services may support workflows when their direction is intentional.
- Utilities and model/lifecycle helpers should stay low-level and avoid depending upward on workflows.
- Single-use helpers should be inlined, privatized, or moved closer to their caller when that improves readability.

This keeps public callables stable, lets purposeful internal implementation roles collaborate, and still flags dependency direction that makes the architecture harder to maintain.

## How the dashboard is generated

The dashboard is built from repository scans that inspect callable definitions and relationships. The scan produces callable relationship metadata in [`_data/callable-flow.json`](_data/callable-flow.json), and the visual dashboard uses that JSON to show caller and callee relationships, roles, reachability, reuse, layer consistency, and refactor recommendations.

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

Refactor signals are warnings generated from the callable graph. They do not automatically mean the code is wrong or that a callable must be changed. They highlight role-aware architecture drift and identify where cleanup should be reviewed.

### EG. Pointless wrapper

![Possible wrapper or inline candidates](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

*Guardrail: Warn when a helper appears to add little abstraction value. Single-use or thin wrapper callables may still be valid, but they should earn their place through clearer naming, validation, readability, or reuse.*

### EG. Large dependency surface

![Large dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

*Guardrail: Warn when a public callable depends on many nested helpers. This may be valid orchestration, but it increases the chance that a small helper change breaks a wider workflow.*

### EG. Messy callable dependency

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

*Guardrail: Warn when one public callable depends on another public callable. Public callables should usually be entry points. Shared logic should usually move into an internal workflow, service, adapter, validator, resolver, normalizer, or utility according to its role.*

### EG. Nested helper chain

![Nested helper chain](../assets/fabricops-bad-example-nested-functions.png)

*Guardrail: Repeated workflow-to-workflow chains or upward dependency patterns need review because they make orchestration harder to reason about. Allowed internal role calls can be valid when validators, resolvers, normalizers, adapters, services, utilities, models, lifecycle hooks, or property accessors support the intended lower-level direction.*

## Selecting refactor candidates

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

*Selecting a focused cleanup set.*

The dashboard supports selecting callables with refactor signals so users can build a focused cleanup set. This narrows review to specific architecture guardrails instead of asking AI tools or Codex to reason over the whole codebase at once.

## Exporting an AI refactor prompt

![Exporting an AI refactor prompt](../assets/fabricops-select-refactor-candidates-prompt-export.png)

*Exporting a structured callable refactor packet.*

Selected callables export as structured callable refactor packets for AI tools or Codex. Each packet is a planning and execution aid that summarizes architecture intent, compatibility mode, selected callable evidence, requested work, expected output, and batch accounting. It is not automatic proof that a callable must be changed. Maintainers inspect the callable, review direct and downstream dependencies, preserve expected public behavior, and decide whether to keep, inline, move, privatize, simplify, or intentionally leave the callable unchanged.

??? example "Example exported callable refactor packet"

    ```text
    Callable refactor packet

    Objective:
    Review and refactor selected FabricOps callables to improve maintainability, flatten overly deep call chains, reduce confusing cross layer dependencies, and preserve expected public behavior.

    Architecture intent:
    Keep the public API surface small and clear.
    Public API callables may be heavier if that makes the code easier to follow.
    Prefer public API to internal workflow, resolver, validator, adapter, service, utility, or model flow.
    Avoid deep cross module helper chains.
    Inline or privatize single use helpers when readability improves.
    Move helpers closer to their caller when they are not genuinely reusable.
    Keep genuinely shared utilities stable and generic.
    Do not casually change public API behavior.

    Compatibility mode:
    selected mode: internal_cleanup
    instruction: Preserve public API behavior. Internal helpers may be renamed, moved, privatized, inlined, or simplified when tests and callers remain valid.

    Selected callable example:
    qualified_name: fabricops_kit._profiling_adapters._build_categorical_distribution
    function_name: _build_categorical_distribution
    module: _profiling_adapters
    layer / function_type: utility
    callable_kind: function
    recommended_action: Inline candidate
    priority or risk: Medium
    callable_role: internal_adapter, spark_profiling_adapter
    dependency_role: internal_adapter
    reachability_kind: directly_reachable
    callers count: 1
    callees count: None
    signal reason / signals: Single use internal helper, leaf internal helper, utility but low reuse

    Requested work:
    Inspect the callable and its direct and downstream dependencies.
    Decide whether to keep public, flatten internals, inline single use helpers, move helper closer to caller, or review cross layer dependency.
    Preserve external behavior unless compatibility mode explicitly allows breaking changes.
    Prefer simpler, flatter code over deeply nested helper chains.
    Keep utilities generic and prevent utility to project specific workflow dependencies.
    Update or add tests where needed.
    Avoid broad unrelated refactors.

    Expected output:
    Summary of changes
    Callables changed
    Callables intentionally left unchanged
    Tests added or updated
    Risks
    Remaining follow up items
    Batch accounting: completed, deferred, remaining
    ```

## Conclusion

The Callable Flow Dashboard is an architecture guardrail for keeping FabricOps maintainable as the kit grows. It helps maintainers choose focused inspection and refactor work, especially when using AI or Codex, without treating graph signals as automatic change requirements. The main rule is role-aware: public API entrypoints should remain stable notebook-facing surfaces; internal workflows may orchestrate lower-level implementation roles; validators, resolvers, normalizers, adapters, and services may support workflows when their direction is intentional; and utilities plus model/lifecycle helpers should stay low-level and avoid depending upward on workflows.
