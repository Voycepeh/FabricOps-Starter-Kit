# Callable Flow

> **Make it exist first. Make it good next.**
>
> AI helps FabricOps move quickly from idea to working public callable. Callable Flow helps us come back afterwards to review whether the implementation is clean enough to keep.

## Why this exists

AI can code fast.

That speed is useful when building FabricOps because the first priority is often to create a working public callable function that users can try.

At that stage, the goal is not perfect code.

The goal is:

```text
Make the function exist.
Make it work.
Validate whether the behaviour is useful.
```

Once the behaviour is worth keeping, the next problem is maintainability.

AI generated code can work correctly but still leave behind messy integration patterns: duplicated helpers, private functions used across files, wide dependency surfaces, or long chains of thin wrapper functions.

Callable Flow exists to support that second step.

It helps us move quickly during prototyping, then return later with a clearer view of what should be cleaned up.

## What we want to catch

### Pointless wrapper functions

AI generated code can create small wrapper functions that only pass work to the next function.

Each wrapper may look harmless by itself, but the full chain makes the implementation harder to read, test, and refactor.

![Pointless wrapper functions](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

Wrappers are worth keeping when they add clear naming, validation, reuse, or a meaningful boundary.

They are worth simplifying when they only make the call path longer.

### Wide dependency surfaces

A public callable can become hard to reason about when it pulls in too many downstream helpers.

![Wide dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

This is not automatically wrong.

But it is a signal to ask whether the function is doing too much, or whether the same responsibility has been spread across too many helper functions.

### Public callable dependencies

Public callables should usually be entry points, not dependencies of other public callables.

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

When shared logic is needed, it should usually move into a helper that both public functions can call safely.

### Long nested chains

Long nested chains make it harder to understand where the real work happens.

![Long nested chain](../assets/fabricops-bad-example-nested-functions.png)

The question is not whether the code works.

The question is whether the structure is still simple enough to keep.

## The workflow

The intended workflow is:

```text
Prototype quickly
→ validate with users
→ inspect callable structure
→ export a focused cleanup packet
→ use AI to assist the refactor
→ review the actual code
→ run tests
```

The point is not to review every line of code at the moment it is created.

The point is to avoid letting fast prototypes quietly become long term technical debt.

## Cleanup packet

When a function is worth improving, Callable Flow can export a focused cleanup packet.

The packet gives AI enough context to help with the next step without asking it to freely rewrite the repository.

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

![Prompt export](../assets/fabricops-select-refactor-candidates-prompt-export.png)

Example packet shape:

```yaml
schema: fabricops_public_callable_flow_cleanup_packet

selected_public_callable:
  selected_public_callable_name: display_guardrail_results
  qualified_name: fabricops_kit.pipeline.display_guardrail_results
  source_file: src/fabricops_kit/pipeline.py

compatibility_mode: internal_cleanup

architecture_summary:
  downstream_count: 8
  max_depth: 4
  architecture_violation_count: 1
  merge_candidate_count: 2

requested_work:
  intent: >
    Plan a safe cleanup for the selected public callable and its
    supporting helpers.
  priority_order:
    - Resolve architecture violations first.
    - Keep public callable behaviour stable.
    - Merge or inline thin wrappers only when readability improves.
    - Call out tests required before implementation.
```

The packet keeps the refactor focused on the selected callable, the identified risks, and the compatibility mode.

## Principle

```text
Make it exist first.
Validate that it is useful.
Then make the implementation good enough to keep.
```

Callable Flow exists because AI assisted development should be fast, but the repository still needs a maintainability checkpoint before messy prototypes become permanent.

## Generated outputs

- [Open Callable Architecture](../assets/callable-functions-dashboard.html)
- [Open Code Inventory](../assets/callable-functions-inventory.html)
- [Open callable-flow.json](_data/callable-flow.json)
