# Callable Flow Dashboard

AI coding tools make it easy to add callables quickly. That speed is useful, but it can also create too many entry points, thin wrapper callables, nested helpers, and uncontrolled dependencies. The Callable Flow Dashboard exists to make those relationships visible before the codebase becomes hard to maintain.

!!! info "Interactive dashboard"
    The interactive [Callable Flow Dashboard](../assets/callable-functions-dashboard.html) is available from this page. This documentation explains why the dashboard exists, how to read the signals, and how to use the exported context for AI-assisted refactoring.

## Why callable flow matters

FabricOps keeps notebook-facing APIs small and explainable. A callable should have a clear role in the callable hierarchy:

```text
Public callables → Internal helpers → Utility callables
```

The dependency rule is intentionally simple: a callable may call lower layers, but not the same layer or higher layers.

- Public callables may call internal helpers and utility callables.
- Internal helpers may call utility callables.
- Utility callables should be self-contained and should not call shared project callables.

This keeps public callables as stable entry points, internal helpers as reusable implementation details, and utility callables as low-risk building blocks.

## How the dashboard is generated

The dashboard is built from repository scans that inspect callable definitions and relationships. The scan produces callable relationship metadata in [`_data/callable-flow.json`](_data/callable-flow.json), and the visual dashboard uses that JSON to show caller and callee relationships, depth, reuse, and refactor recommendations.

Because the dashboard is generated from the codebase, it is a maintenance aid rather than a separate source of truth. Use it to decide where to inspect source code, update docstrings, flatten helper chains, or preserve shared helpers carefully.

## What the dashboard detects

Use the dashboard signals to find patterns that deserve review:

- public callables calling public callables
- internal helpers with too many dependencies
- deep nested helper chains
- low-value wrapper or inline candidates
- highly reused helpers that should be preserved carefully
- callables used by only one caller
- large dependency surfaces

## Refactor signals

Refactor signals are warnings generated from the callable graph. They do not automatically mean the code is wrong. Instead, they help guard against architecture drift from the intended public → internal → utility hierarchy and identify where cleanup should be reviewed before changes are made.

### Possible wrapper or inline candidates

![Possible wrapper or inline candidates](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

*Guardrail: Warn when a helper appears to add little abstraction value. Single-use or thin wrapper callables may still be valid, but they should earn their place through clearer naming, validation, readability, or reuse.*

### Large dependency surface

![Large dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

*Guardrail: Warn when a public callable depends on many nested helpers. This may be valid orchestration, but it increases the chance that a small helper change breaks a wider workflow.*

### Public callable dependency

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

*Guardrail: Warn when one public callable depends on another public callable. Public callables should usually be entry points. Shared logic should usually move into an internal helper or utility callable.*

### Nested helper chain

![Nested helper chain](../assets/fabricops-bad-example-nested-functions.png)

*Guardrail: Warn when internal helpers repeatedly call other internal helpers. This makes the architecture harder to reason about and should be flattened where the extra layer does not add validation, naming, or reuse value.*

## Selecting refactor candidates

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

*Selecting a focused cleanup set.*

The dashboard supports selecting callables with refactor signals so users can build a focused cleanup set. This narrows review to specific architecture guardrails instead of asking AI tools to reason over the whole codebase at once.

## Exporting an AI refactor prompt

![Exporting an AI refactor prompt](../assets/fabricops-select-refactor-candidates-prompt-export.png)

*Exporting a structured AI refactor packet.*

Selected callables can be exported as a structured AI refactor packet. The export gives AI tools the callable layer, call graph context, recommended action, compatibility mode, safety constraints, and expected output so they can reason from architecture context instead of guessing from isolated code snippets.

??? example "Example exported AI refactor packet"

    ```text
    FabricOps callable refactor packet

    Prompt for AI

    You are reviewing a FabricOps callable refactor packet. Use the selected callables and call graph metadata to plan a safe cleanup. Group callables by refactor type, explain the rationale, identify risks, and propose an ordered implementation plan. Do not write code yet. Respect the compatibility mode in this packet. If compatibility_mode is stable_api_safe, preserve public API compatibility and call out migration risks. If compatibility_mode is internal_cleanup, preserve external behavior but allow internal signatures and helper boundaries to change when justified. If compatibility_mode is development_breaking_allowed, propose cleaner breaking changes where they improve the design. Always call out tests required before changes.

    Refactor context

    Intent: Plan safe cleanup for selected FabricOps helper callables.

    Mode: Planning only.

    Compatibility mode: Internal cleanup

    Selected callable actions:
    - Architecture violation

    Safety constraints:
    - Preserve external behavior
    - Internal helper names, signatures, and module boundaries may change if justified
    - Identify impacted callers before recommending changes

    Expected AI output:
    - Group selected callables by refactor type
    - Explain which callables are safe cleanup candidates
    - Identify callables that should not be refactored yet
    - Propose an ordered refactor plan
    - List risks and required tests
    - Do not produce code changes unless explicitly requested

    Selected callables

    Callable 1: _audit_timestamp_expr

    Qualified name: fabricops_kit.config._audit_timestamp_expr
    Module: config
    Callable layer: Internal helper
    Recommended action: Architecture violation
    Priority: High
    Signal reason: Architecture violation: Callable dependency direction breaks the public → internal → utility layer rule.
    Callers:
    - profile_dataframe (data_profiling)

    Callees:
    - _get_audit_timezone (config)

    Source path: src/fabricops_kit/config.py
    ```

## Conclusion

The Callable Flow Dashboard is not only a dependency viewer. It is an architecture guardrail for keeping FabricOps maintainable as the kit grows.

The main rule is simple: public callables should orchestrate, internal helpers should contain reusable workflow logic, and utility callables should stay small, stable, and dependency-light. When a callable breaks this direction, depends on too many nested helpers, or creates repeated helper chains, the dashboard should flag it for review before cleanup.

The exported refactor packet gives AI tools enough context to reason safely from the call graph instead of guessing from isolated code snippets. This makes the workflow useful for planned refactors, code review, and future architecture governance.
