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

The Function Call Graph has one maintainer-facing dashboard: the Function Call Graph Dashboard. That dashboard combines public callable flows, architecture checks, the runtime inventory, and cleanup packet export into one review surface.

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
* [Function Call Graph Dashboard runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory)
* [function-call-graph.json](_data/function-call-graph.json)

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

The Function Call Graph Dashboard is a review surface for public callable cleanup.

It does not treat every signal as a failure. Broken rules are boundary breaks, while the other signals are maintainability review hints that help reviewers decide where to inspect next.

| Signal | What it means | Reviewer action |
|---|---|---|
| Broken rule | An architecture rule is broken and must be fixed first. Examples include a public callable calling another public callable, a shared helper calling a public function, or a helper reaching into a private helper owned by another file. | Fix this first before helper cleanup. |
| Too many steps | Depth is 4 or more. Depth means how many call steps away the public function reaches. | Check whether the chain can be flattened or made easier to follow. |
| Too many helpers | Width is greater than 10. Width means direct calls from this public callable. | Check whether the function has become too wide or hard to reason about. |
| Shared helper | The helper is used by more than one public function. | Treat this as informational unless the callable also exceeds width or depth thresholds. |
| Maybe combine | The helper may be too small, too specific, or only useful to one caller. | Decide whether to keep the helper, move it to shared logic, or merge it into the caller. |

The key distinction is:

| Type | Meaning |
|---|---|
| Broken rule | A boundary rule is broken and should be fixed. |
| Maintainability signal | The code may still be valid, but it deserves review before refactoring. |

The preferred public callable shape is still:

```text
public owner file → shared.py → internal implementation details
```

The pattern that usually needs review is:

```text
public callable → helper → helper → helper
```

The dashboard keeps public-function review focused on `Contains architecture violation`, `Large depth / width`, and healthy public functions. Depth means how many call steps away the public function reaches. Width means direct calls from this public callable. Scope means total unique runtime assets in this selected architecture scope, including nested/transitive support assets.

### Too many helpers

A public callable can become hard to reason about when it pulls in too many downstream helpers.

![Too many helpers](../assets/fabricops-bad-example-large-surface-area.png)

### Too many steps

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

### Choose architecture scope

Start with the architecture scope table. Choose a public callable flow, **All runtime assets**, or **Others / Cannot trace back to a public callable**. Public callable scopes keep the existing flow review, while the special scopes let maintainers inspect package-level runtime assets without restoring a separate inventory page.

### Inspect call graph when available

When the selected scope is a public callable, the dashboard shows the callable dependency tree, direct/transitive helper details, and architecture findings. The special runtime scopes show a clear no-flow message instead of inventing a fake public call graph.

### Review runtime inventory

The runtime inventory is an in-page section at [Runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory). It uses the `function_inventory` JSON section and describes deduplicated runtime code assets under `src/fabricops_kit`, including unreachable runtime assets that need verification. Test, docs, scripts, notebook, generated asset, and test-only helper noise is excluded.

### Select inventory assets

Use the runtime inventory filters and multi-select controls to select one function/class, multiple helpers, all visible rows, or a scoped set of possible orphan records. Helper suggestions are review hints, not automatic delete or refactor commands.

### Export AI refactor packet

The dashboard exports one AI refactor packet from selected inventory assets. The packet includes the selected architecture scope, related public callable flow when applicable, related architecture findings, selected inventory assets, and compatibility mode.

## 5. AI refactor packets

When a function is worth refactoring, the Function Call Graph Dashboard can export focused cleanup packets as JSON or YAML.

The Function Call Graph Dashboard exports one `fabricops_runtime_refactor_packet` built from selected runtime inventory assets. The packet also carries the selected architecture scope, related public callable flow when applicable, architecture findings, and compatibility mode.

The packet keeps the AI refactor focused on:

* the selected function
* the supporting code assets
* the identified architecture risks
* the compatibility mode
* the relevant test expectations

![Function Call Graph AI refactor package](../assets/fabricops-call-graph-ai-refactor-package.png)

![Function Call Graph AI refactor package detail](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

The cleanup packet gives AI a focused review surface so it can improve the implementation without losing the original intent.

<!-- Test compatibility breadcrumbs: [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html) [Runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory) -->
