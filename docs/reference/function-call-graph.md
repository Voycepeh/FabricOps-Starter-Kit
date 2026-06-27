# Function Call Graph

> **First make it exist. Then make it good.**
>
> AI helps FabricOps move quickly from idea to working public function. The Function Call Graph is the maintainability checkpoint that helps us decide whether the implementation is clean enough to keep.

The Function Call Graph turns repository scans into a review surface for AI-assisted development. It shows which public callable functions exist, what supports them, where dependencies go, and which cleanup candidates are worth reviewing before prototypes become permanent.

## Dashboard context

Use the Function Call Graph Dashboard first when you are deciding whether a public callable is clean enough to keep.

![Function Call Graph Dashboard](../../assets/fabricops-select-refactor-candidates.png)

[Open architecture dashboard](../../assets/function-call-graph-dashboard.html){ .md-button .md-button--primary }

## Why this exists

AI can code fast.

That speed is useful when building FabricOps because the first priority is often to create a working public callable function that users can try.

At that stage, the goal is:

```text
First make it exist.
Then make it good.
Validate whether the behaviour is useful.
```

Once the behaviour is worth keeping, the next problem is maintainability.

AI generated code can work correctly but still leave behind messy integration patterns: duplicated helpers, private functions used across files, wide dependency surfaces, public callables depending on other public callables, or long chains of thin wrapper functions.

The Function Call Graph exists to support that second step.

## What it helps with

The dashboard helps reviewers:

- see all public callable functions in one place
- understand the supporting private functions, shared helpers, classes, and internal methods behind each public callable
- spot architecture violations and dependency chains that deserve a closer look
- export focused cleanup packets for AI-assisted refactors
- review compatibility mode and test expectations before changing implementation

## What we want to catch

### Pointless wrapper functions

AI generated code can create small wrapper functions that only pass work to the next function.

![Pointless wrapper functions](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

### Wide dependency surfaces

A public callable can become hard to reason about when it pulls in too many downstream helpers.

![Wide dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

### Public callable dependencies

Public callables should usually be entry points, not dependencies of other public callables.

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

### Long nested chains

Long nested chains make it harder to understand where the real work happens.

![Long nested chain](../assets/fabricops-bad-example-nested-functions.png)

The question is not whether the code works. The question is whether the structure is still simple enough to keep.

## The workflow

Prototype quickly, validate with users, inspect the function call graph, export a focused cleanup packet, review the actual code, then run tests.

The point is to avoid letting fast prototypes quietly become long term technical debt.

## Cleanup packets

When a function is worth improving, the Function Call Graph Dashboard can export focused cleanup packets as JSON or YAML.

The Function Call Graph Dashboard exports `fabricops_public_callable_flow_cleanup_packet` for one selected public function graph. The Function Inventory exports `fabricops_support_inventory_cleanup_packet` for selected function-level code assets.

The packet keeps the refactor focused on the selected function, the identified risks, and the compatibility mode.

## Generated outputs

The Function Call Graph is generated from repository scans. The generated outputs are:

- [Function Call Graph Dashboard](../../assets/function-call-graph-dashboard.html)
- [Function Inventory](../../assets/function-inventory.html)
- [function-call-graph.json](_data/function-call-graph.json)

Because these outputs are generated, update source inputs and the generator first, then regenerate the reference artifacts when intentionally refreshing this page.

## Principle

```text
First make it exist.
Then make it good.
```

The Function Call Graph exists because AI assisted development should be fast, but the repository still needs a maintainability checkpoint before messy prototypes become permanent.
