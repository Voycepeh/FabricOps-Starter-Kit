# Callable Flow Dashboard

AI coding tools make it easy to add functions quickly. That speed is useful, but it can also create too many entry points, thin wrapper functions, nested helpers, and uncontrolled dependencies. The Callable Flow Dashboard exists to make those relationships visible before the codebase becomes hard to maintain.

!!! info "Interactive dashboard"
    The interactive [Callable Flow Dashboard](../assets/callable-functions-dashboard.html) is available from this page. This documentation explains why the dashboard exists, how to read the signals, and how to use the exported context for AI-assisted refactoring.

## Why callable flow matters

FabricOps keeps notebook-facing APIs small and explainable. A function should have a clear role in the callable hierarchy:

```text
Public callables → Internal helpers → Utility functions
```

The dependency rule is intentionally simple: a callable may call lower layers, but not the same layer or higher layers.

- Public callables may call internal helpers and utility functions.
- Internal helpers may call utility functions.
- Utility functions should be self-contained and should not call shared project callables.

This keeps public callables as stable entry points, internal helpers as reusable implementation details, and utility functions as low-risk building blocks.

## How the dashboard is generated

The dashboard is built from repository scans that inspect callable definitions and relationships. The scan produces callable relationship metadata in [`_data/callable-flow.json`](_data/callable-flow.json), and the visual dashboard uses that JSON to show caller and callee relationships, depth, reuse, and review recommendations.

Because the dashboard is generated from the codebase, it is a maintenance aid rather than a separate source of truth. Use it to decide where to inspect source code, update docstrings, flatten helper chains, or preserve shared helpers carefully.

## What the dashboard detects

Use the dashboard signals to find patterns that deserve review:

- public callables calling public callables
- internal helpers with too many dependencies
- deep nested helper chains
- low-value wrapper or inline candidates
- highly reused helpers that should be preserved carefully
- functions used by only one caller
- large dependency surfaces

## Review signals

### Possible wrapper or inline candidates

![Possible wrapper or inline candidates](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

*Possible wrapper or inline candidates.*

Helpers used by only one function and calling no other function may still be valid, but should be reviewed for abstraction value. If they do not improve naming, validation, readability, or reuse, they may be better inlined.

### Large dependency surface

![Large dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

*Large dependency surface.*

A public callable depending on many nested helpers may be valid orchestration, but it should be reviewed for accidental complexity. A large dependency surface increases the risk that a small change breaks another part of the workflow.

### Public callable dependency

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

*Public callable dependency.*

Public callables should usually be entry points, not dependencies of other public callables. When shared logic is needed, it should usually move into an internal helper that both public functions can call safely.

### Nested helper chain

![Nested helper chain](../assets/fabricops-bad-example-nested-functions.png)

*Nested helper chain.*

Repeated internal-to-internal helper chains make the architecture harder to reason about. These chains should be reviewed and flattened where the extra layers do not add clear value.

## Selecting refactor candidates

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

*Selecting refactor candidates.*

The dashboard supports selecting functions that need review. This lets the user focus on a specific cleanup set instead of asking AI to reason about the whole codebase.

## Exporting an AI refactor prompt

![Exporting an AI refactor prompt](../assets/fabricops-select-refactor-candidates-prompt-export.png)

*Exporting an AI refactor prompt.*

Selected functions can be exported as a structured AI prompt. The prompt should include function type, call graph context, recommended action, compatibility mode, and safety constraints so AI tools can refactor with architecture context instead of guessing from isolated snippets.
