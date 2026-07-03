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

The Function Call Graph helps reviewers inspect public callable functions, understand review signals, and decide the next cleanup step before refactoring.

## Overview

The Function Call Graph has one maintainer-facing dashboard: the Public Function Call Flows Dashboard. That dashboard combines public callable flows, architecture checks, the selected callable inventory, and cleanup packet export into one review surface.

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

* [Public Function Call Flows Dashboard](../assets/public-function-call-flows-dashboard.html)
* [Public Function Call Flows Dashboard selected callable inventory](../assets/public-function-call-flows-dashboard.html#selected-public-function-panel)
* [public-function-call-flows.json](_data/public-function-call-flows.json)

## 3. Enforce architecture

AI generated code can work correctly but still leave behind messy integration patterns:

* duplicated helpers
* private functions used across files
* wide dependency surfaces
* public callables depending on other public callables
* too many steps across thin wrapper functions

The question is not only whether the code works.

The question is whether the structure is still simple enough to keep.

The Function Call Graph is protected by an enforcement test that keeps the callable architecture intentional as the codebase changes.

The enforcement test makes sure public callables, shared helpers, and generated reference outputs do not drift silently.

The enforcement test is:

* [`tests/contract/test_callable_architecture_validation.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/tests/contract/test_callable_architecture_validation.py)

This helps prevent accidental architecture violations from becoming permanent.

### What the dashboard signals

The dashboard uses deterministic rules. It separates public-flow signals from per-function inventory suggestions.

#### Public-flow signals

| Signal | Color | Calculation | Reviewer action |
|---|---|---|---|
| Large width/depth | Yellow | Width > 10 or Depth > 5 | Review whether the public callable has become too wide or too deeply nested. |
| Architecture violation | Red | Any Type 1-6 architecture violation appears in the callable flow | Fix boundary violations before helper cleanup. |

#### Architecture violation types

| Type | Rule | Why it matters |
|---|---|---|
| Type 1 | Public function calls another public function directly | Public callables should own their workflow rather than chaining public entry points. |
| Type 2 | Shared function calls a public function directly | Shared helpers should not depend on public entry points. |
| Type 3 | Private function calls a public function directly | Private implementation details should not call public entry points. |
| Type 4 | Shared function calls a private function from another file | Shared helpers should not reach into another file’s private implementation. |
| Type 5 | Private function calls a private function from another file | Private helpers should stay file-local. |
| Type 6 | Private function calls a shared function directly | Private implementation details may need boundary review if they depend outward on shared helpers. |

#### Inventory suggestions

| Suggestion | Calculation | Reviewer action |
|---|---|---|
| Inline candidate | Called by exactly one parent, not used elsewhere, not recursive, not called multiple times by the same parent | Consider absorbing the helper into its caller. |
| Promote to shared | Private function called by more than one distinct caller | Consider moving it to a shared helper boundary. |

#### Metric definitions

| Metric | Definition |
|---|---|
| Width | Direct package-local calls from the selected public function. |
| Depth | Deepest nested call path. |
| Scope | Total downstream functions reached by the selected public function flow. |

The preferred public callable shape is still:

```text
public owner file → shared.py → internal implementation details
```

The pattern that usually needs review is:

```text
public callable → helper → helper → helper
```

Because these outputs are generated, update the scanner and architecture rules first, then regenerate the reference artifacts when intentionally refreshing this page.

## 4. Public Function Call Flows Dashboard

The Public Function Call Flows Dashboard is the review surface for deciding whether a public callable is clean enough to keep.

After the scanner identifies public callables, supporting private functions, shared helpers, classes, internal methods, and dependency edges, the dashboard turns that scan into something reviewers can inspect.

![Public Function Call Flows Dashboard](../assets/fabricops-call-graph-dashboard.png)

<div align="center" markdown>

[Open architecture dashboard](../assets/public-function-call-flows-dashboard.html){ .md-button .md-button--primary }

</div>

The dashboard helps reviewers:

* see all public callable functions in one place
* understand what supports each public callable
* trace where dependencies go
* spot architecture violations and dependency chains that deserve a closer look

### Choose architecture scope

Start with the architecture scope table. Choose a public callable flow, **All runtime assets**, or **Others / Cannot trace back to a public callable**. Public callable scopes keep the existing flow review, while the special scopes let maintainers inspect package-level runtime assets without restoring a separate inventory page.

### Inspect call graph when available

When the selected scope is a public callable, the dashboard shows the callable dependency tree, direct/transitive helper details, and architecture findings. The special runtime scopes show a clear no-flow message instead of inventing a fake public call graph.

### Review selected callable inventory

The selected callable inventory is an in-page section at [Selected callable inventory](../assets/public-function-call-flows-dashboard.html#selected-public-function-panel). It uses the `public_functions[].flow[]` JSON section and describes deduplicated callable-flow functions under `src/fabricops_kit`, including defined-but-not-used cleanup candidates that need verification. Test, docs, scripts, notebook, generated asset, and test-only helper noise is excluded.

### Select inventory assets

Use the selected callable inventory filters and multi-select controls to select one function/class, multiple helpers, all visible rows, or a scoped set of possible orphan records. Helper suggestions are review hints, not automatic delete or refactor commands.

### Export AI refactor packet

The dashboard exports one AI refactor packet from selected inventory assets. The packet includes the selected architecture scope, related public callable flow when applicable, related architecture findings, selected inventory assets, and compatibility mode.

## 5. AI refactor packets

When a function is worth refactoring, the Public Function Call Flows Dashboard can export focused cleanup packets as JSON or YAML.

The Public Function Call Flows Dashboard exports one `fabricops_public_function_call_flow_refactor_packet_v2` built from selected callable inventory assets. The packet also carries the selected architecture scope, related public callable flow when applicable, architecture findings, and compatibility mode.

The packet keeps the AI refactor focused on:

* the selected function
* the supporting code assets
* the identified architecture risks
* the compatibility mode
* the relevant test expectations

![Function Call Graph AI refactor package](../assets/fabricops-call-graph-ai-refactor-package.png)

![Function Call Graph AI refactor package detail](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

The cleanup packet gives AI a focused review surface so it can improve the implementation without losing the original intent.

<!-- Test compatibility breadcrumbs: [Public Function Call Flows Dashboard](../assets/public-function-call-flows-dashboard.html) [Selected callable inventory](../assets/public-function-call-flows-dashboard.html#selected-public-function-panel) -->
