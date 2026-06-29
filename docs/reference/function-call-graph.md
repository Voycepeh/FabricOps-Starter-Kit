# Function Call Graph

> **First make it exist. Then make it good.**
>
> AI helps FabricOps move quickly from idea to working public callable function:
>
> * create the function quickly
> * test whether the behaviour is useful
> * keep it if the behaviour is worth preserving
> * clean the architecture before the prototype becomes permanent
>
> The Function Call Graph is the maintainability checkpoint that helps us decide whether the implementation is clean enough to keep.

The Function Call Graph turns repository scans into a review surface for AI assisted development. It shows which public callable functions exist, what supports them, where dependencies go, and which cleanup candidates are worth reviewing before prototypes become permanent.

## How it works

The Function Call Graph follows a simple flow:

```text
Repository Code → Scan & Analyze → Enforce Architecture → Dashboard → AI Refactor Packets
```

![Function Call Graph setup](../assets/fabricops-call-graph-setup.png)

## 1. Repository code

The repository is the source of truth.

FabricOps public callable functions, shared helpers, private functions, classes, and internal methods all live in the codebase. The Function Call Graph starts by scanning this code structure instead of relying on manually maintained documentation.

## 2. Scan and analyze

The Function Call Graph is generated from repository scans.

The source scanner is:

* [`scripts/generate_function_reference.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_function_reference.py)

The scanner reads the codebase and identifies:

* public callable functions
* supporting private functions
* shared helpers
* classes
* internal methods
* dependency edges between functions and modules

The scanner then produces generated review artifacts that make the callable architecture easier to inspect.

The generated review outputs are:

* [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html)
* [Function Inventory](../assets/function-inventory.html)
* [function-call-graph.json](_data/function-call-graph.json)

## 3. Enforce architecture

AI generated code can work correctly but still leave behind messy integration patterns:

* duplicated helpers
* private functions used across files
* wide dependency surfaces
* public callables depending on other public callables
* long chains of thin wrapper functions

The question is not only whether the code works.

The question is whether the structure is still simple enough to keep.

The Function Call Graph is protected by an enforcement test that keeps the callable architecture intentional as the codebase changes.

The enforcement test makes sure public callables, shared helpers, and generated reference outputs do not drift silently.

The enforcement test is:

* [`tests/contract/test_callable_architecture_validation.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/tests/contract/test_callable_architecture_validation.py)

This helps prevent accidental architecture violations from becoming permanent.

### Architecture violations we are preventing

The Function Call Graph supports the public function architecture rule used by FabricOps.

Each public callable should have a clear owner file, shared implementation details should stay in `shared.py`, and the package `__init__.py` should be the supported export surface.

For the full rule, see:

* [Public Function Architecture](../public-function-architecture/)

The main violations we want to catch are:

* public callables depending directly on other public callables
* public owner files defining more than one public function
* public owner files defining classes
* public function names not matching their owner file names
* support classes, dataclasses, or value objects living outside `shared.py`
* forbidden grouping files such as `public.py`, `models.py`, `classes.py`, `adapter.py`, `adapters.py`, `resolver.py`, or `resolvers.py`
* generated reference outputs drifting away from the codebase

The preferred package shape is:

```text
src/fabricops_kit/my_feature/
  __init__.py
  my_public_function.py
  shared.py
```

For multiple public functions in the same batch:

```text
src/fabricops_kit/my_feature/
  __init__.py
  first_public_function.py
  second_public_function.py
  shared.py
```

The intended pattern is simple:

```text
public owner file → shared.py → internal implementation details
```

Avoid this pattern:

```text
public callable → public callable → public callable
```

Public callables should be clean entry points. Shared logic belongs behind them, not inside a chain of public function calls.

### Wide dependency surfaces

A public callable can become hard to reason about when it pulls in too many downstream helpers.

![Wide dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

### Long nested chains

Long nested chains make it harder to understand where the real work happens.

![Long nested chain](../assets/fabricops-bad-example-nested-functions.png)

Because these outputs are generated, update the scanner and architecture rules first, then regenerate the reference artifacts when intentionally refreshing this page.

## 4. Function Call Graph Dashboard

The Function Call Graph Dashboard is the review surface for deciding whether a public callable is clean enough to keep.

After the scanner identifies public callables, supporting private functions, shared helpers, classes, internal methods, and dependency edges, the dashboard turns that scan into something reviewers can inspect.

![Function Call Graph Dashboard](../assets/fabricops-call-graph-dashboard.png)

<div align="center" markdown>

[Open architecture dashboard](../assets/function-call-graph-dashboard.html){ .md-button .md-button--primary }

</div>

The dashboard helps reviewers:

* see all public callable functions in one place
* understand what supports each public callable
* trace where dependencies go
* spot architecture violations and dependency chains that deserve a closer look

## 5. AI refactor packets

When a function is worth refactoring, the Function Call Graph Dashboard can export focused cleanup packets as JSON or YAML.

The Function Call Graph Dashboard exports `fabricops_public_callable_flow_cleanup_packet` for one selected public function graph.

The Function Inventory exports `fabricops_support_inventory_cleanup_packet` for selected function level code assets.

The packet keeps the AI refactor focused on:

* the selected function
* the supporting code assets
* the identified architecture risks
* the compatibility mode
* the relevant test expectations

![Function Call Graph AI refactor package](../assets/fabricops-call-graph-ai-refactor-package.png)

![Function Call Graph AI refactor package detail](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

The cleanup packet gives AI a focused review surface so it can improve the implementation without losing the original intent.

<!-- Test compatibility breadcrumbs: [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html) [Function Inventory](../assets/function-inventory.html) -->
