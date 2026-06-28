# Function Call Graph

> **Make it exist first. Make it good next.**
>
> AI helps FabricOps move quickly from idea to working public function. The Function Call Graph helps us come back afterwards to review whether the implementation is clean enough to keep.

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

AI generated code can work correctly but still leave behind messy integration patterns: duplicated helpers, private functions used across files, wide dependency surfaces, public callables depending on other public callables, or long chains of thin wrapper functions.

The Function Call Graph exists to support that second step.

It helps us move quickly during prototyping, then return later with a clearer view of what should be cleaned up.

## What we want to catch

### Pointless wrapper functions

AI generated code can create small wrapper functions that only pass work to the next function.

Each wrapper may look harmless by itself, but the full chain makes the implementation harder to read, test, and refactor.

Wrappers are worth keeping when they add clear naming, validation, reuse, or a meaningful boundary.

They are worth simplifying when they only make the call path longer.

### Wide dependency surfaces

A public callable can become hard to reason about when it pulls in too many downstream helpers.

![Wide dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

This is not automatically wrong.

But it is a signal to ask whether the function is doing too much, or whether the same responsibility has been spread across too many helper functions.

### Public callable dependencies

Public callables should usually be entry points, not dependencies of other public callables.

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
→ inspect the function call graph
→ export a focused cleanup packet
→ use AI to assist the refactor
→ review the actual code
→ run tests
```

The point is not to review every line of code at the moment it is created.

The point is to avoid letting fast prototypes quietly become long term technical debt.

## Dashboard context

The generated review surfaces are:

- [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html) shows how public functions, shared helpers, and private helpers connect across the package. Use it to inspect function dependencies, architecture boundaries, and cleanup candidates.
- [Function Inventory](../assets/function-inventory.html) focuses on function-level code assets, including public callables, shared helpers, private helpers, and cleanup candidates.

Use the Function Call Graph Dashboard first when you are deciding whether a public callable is clean enough to keep. Use Function Inventory when the graph points to function-level code assets that need closer review or when you need to batch related function assets for cleanup planning.

## Cleanup packets

When a function is worth improving, the Function Call Graph Dashboard can export focused cleanup packets as JSON or YAML.

The packet gives AI enough context to help with the next step without asking it to freely rewrite the repository. Reviewers select refactor candidates in the dashboard and use the prompt export to hand AI a focused cleanup scope.

The Function Call Graph Dashboard exports `fabricops_public_callable_flow_cleanup_packet` for one selected public function graph. The Function Inventory exports `fabricops_support_inventory_cleanup_packet` for selected function-level code assets.

Both packet types are designed to keep the cleanup focused on the selected function or assets, the identified risks, the compatibility mode, and the tests that should be reviewed before changes are merged.

Example packet shape:

```yaml
schema: fabricops_public_callable_flow_cleanup_packet

selected_public_callable:
  selected_public_callable_name: display_guardrail_results
  qualified_name: fabricops_kit.pipeline.display_guardrail_results
  source_file: src/fabricops_kit/pipeline.py

compatibility_mode: preserve_backwards_compatibility

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

The packet keeps the refactor focused on the selected function, the identified risks, and the compatibility mode.

## Generated outputs and source checks

The Function Call Graph is generated from repository scans.

The generated review outputs are:

- [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html)
- [Function Inventory](../assets/function-inventory.html)
- [function-call-graph.json](_data/function-call-graph.json)

The source scanner is the Python file that scans the repository and identifies the public callable functions, supporting private functions, classes, internal methods, and dependency edges used to build the graph.

- Scanner: `scripts/generate_function_reference.py`

The architecture is also protected by an enforcement test. This test makes sure the callable structure stays intentional as the codebase changes, instead of allowing public callables, shared helpers, or generated reference outputs to drift silently.

- Enforcement test: `tests/contract/test_callable_architecture_validation.py`

Because these outputs are generated, update the scanner and architecture rules first, then regenerate the reference artifacts when intentionally refreshing this page.

<!-- Test compatibility breadcrumbs: [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html) [Function Inventory](../assets/function-inventory.html) -->

## Principle

```text
Make it exist first.
Validate that it is useful.
Then make the implementation good enough to keep.
```

The Function Call Graph exists because AI assisted development should be fast, but the repository still needs a maintainability checkpoint before messy prototypes become permanent.
