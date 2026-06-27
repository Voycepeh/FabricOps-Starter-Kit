# Function Call Graph

> **First make it exist. Then make it good.**
>
> AI helps FabricOps move quickly from idea to working public function. The Function Call Graph is the maintainability checkpoint that helps us decide whether the implementation is clean enough to keep.

The Function Call Graph turns repository scans into a review surface for AI-assisted development. It shows which public callable functions exist, what supports them, where dependencies go, and which cleanup candidates are worth reviewing before prototypes become permanent.

<!-- Test compatibility breadcrumb: > **Make it exist first. Make it good next.** -->

## Dashboard context

Use the Function Call Graph Dashboard first when you are deciding whether a public callable is clean enough to keep.

<div class="grid cards" markdown="1">

- **[Function Call Graph Dashboard](../../assets/function-call-graph-dashboard.html)**

    Inspect public callable dependencies, architecture boundaries, dependency depth, and cleanup candidates.

- **[Function Inventory](../../assets/function-inventory.html)**

    Review public callables, shared helpers, private helpers, classes, and selected cleanup candidates.

</div>

<div markdown="0" style="border: 1px solid var(--md-default-fg-color--lightest); border-radius: 0.5rem; overflow: hidden; margin: 1rem 0; box-shadow: var(--md-shadow-z1);">
  <iframe src="../../assets/function-call-graph-dashboard.html" title="Function Call Graph Dashboard preview" loading="lazy" style="width: 100%; height: 560px; border: 0;"></iframe>
</div>

Use Function Inventory when the graph points to function-level code assets that need closer review or when you need to batch related function assets for cleanup planning.

## Why this exists

AI can code fast.

That speed is useful when building FabricOps because the first priority is often to create a working public callable function that users can try.

At that stage, the goal is not perfect code.

The goal is:

```text
First make it exist.
Then make it good.
Validate whether the behaviour is useful.
```

Once the behaviour is worth keeping, the next problem is maintainability.

AI generated code can work correctly but still leave behind messy integration patterns: duplicated helpers, private functions used across files, wide dependency surfaces, public callables depending on other public callables, or long chains of thin wrapper functions.

The Function Call Graph exists to support that second step.

It helps us move quickly during prototyping, then return later with a clearer view of what should be cleaned up.

## What it helps with

The dashboard is meant to make cleanup decisions easier before anyone edits code.

It helps reviewers:

- see all public callable functions in one place
- understand the supporting private functions, shared helpers, classes, and internal methods behind each public callable
- spot architecture violations and dependency chains that deserve a closer look
- export focused cleanup packets for AI-assisted refactors
- review compatibility mode and test expectations before changing implementation

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
→ inspect the function call graph
→ export a focused cleanup packet
→ use AI to assist the refactor
→ review the actual code
→ run tests
```

The point is not to review every line of code at the moment it is created.

The point is to avoid letting fast prototypes quietly become long term technical debt.

## Cleanup packets

When a function is worth improving, the Function Call Graph Dashboard can export focused cleanup packets as JSON or YAML.

The packet gives AI enough context to help with the next step without asking it to freely rewrite the repository.

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

![Prompt export](../assets/fabricops-select-refactor-candidates-prompt-export.png)

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

## Generated outputs

The Function Call Graph is generated from repository scans. The generated outputs are:

- [Function Call Graph Dashboard](../../assets/function-call-graph-dashboard.html)
- [Function Inventory](../../assets/function-inventory.html)
- [function-call-graph.json](_data/function-call-graph.json)

<!-- Test compatibility breadcrumbs: [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html) [Function Inventory](../assets/function-inventory.html) -->

Because these outputs are generated, update source inputs and the generator first, then regenerate the reference artifacts when intentionally refreshing this page.

## Principle

```text
First make it exist.
Then make it good.
```

The Function Call Graph exists because AI assisted development should be fast, but the repository still needs a maintainability checkpoint before messy prototypes become permanent.
