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

The Function Call Graph is a reviewer workflow for checking public callable functions before cleanup work becomes permanent. It helps reviewers open the dashboard, inspect the selected public function flow, understand architecture signals, and export a focused AI refactor packet when cleanup is needed.

<div align="center" markdown>

[Open Public Function Call Flows Dashboard](../assets/public-function-call-flows-dashboard.html){ .md-button .md-button--primary }
[View JSON Contract](_data/public-function-call-flows.json){ .md-button }

</div>

## Review workflow

Use this page as the entry point for the current callable architecture review flow.

```text
Repository code
→ agent reads AGENTS.md and public-function-call-flows.json
→ agent edits function-level source code
→ scanner regenerates public-function-call-flows.json
→ dashboard and reference pages consume the refreshed JSON
```

The dashboard is the main reviewer surface. The JSON contract is the generated data source behind the dashboard and reference pages.

This flow is not a hard architecture enforcement gate. It is an agent and reviewer feedback loop:

* agents inspect the committed call-flow JSON before editing public functions or helpers
* agents treat source code as the source of truth if the JSON drifts
* agents rerun the scanner after function-level source changes
* the refreshed JSON updates the dashboard and generated reference surfaces
* reviewers use the dashboard to decide whether cleanup is needed

## 1. Open the dashboard

Start from the dashboard when reviewing public callable architecture.

![Public Function Call Flows Dashboard](../assets/fabricops-call-graph-dashboard.png)

The dashboard helps reviewers:

* see all public callable functions in one place
* select a public function and inspect its call tree
* jump from the call tree to the callable inventory
* scope the inventory around the selected function and its nested dependencies
* spot architecture violations, wide flows, deep flows, and helper cleanup candidates
* export focused AI refactor packets for the selected cleanup scope

The public function table is the top-level review surface. Selecting a public function scopes the rest of the dashboard around that callable flow.

## 2. Review the selected public function flow

For each selected public function, review the call tree before jumping into the callable inventory.

The call tree shows how the public callable reaches supporting functions. This keeps the public function as the review owner while still letting reviewers inspect shared helpers and private helpers inside the selected flow.

The key metrics are:

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

## 3. Use architecture signals to decide cleanup

The generated contract keeps deterministic architecture signals available for the dashboard and docs. These signals guide review and cleanup; they are not presented here as a standalone enforcement gate.

### Public flow signals

| Signal | Calculation | Reviewer action |
|---|---|---|
| Large width/depth | Width > 10 or Depth > 5 | Review whether the public callable has become too wide or too deeply nested. |
| Architecture violation | Any Type 1 to Type 6 architecture violation appears in the callable flow | Review boundary shape before helper cleanup. |

### Architecture violation types

| Type | Rule | Why it matters |
|---|---|---|
| Type 1 | Public function calls another public function directly | Public callables should own their workflow rather than chaining public entry points. |
| Type 2 | Shared function calls a public function directly | Shared helpers should not depend on public entry points. |
| Type 3 | Private function calls a public function directly | Private implementation details should not call public entry points. |
| Type 4 | Shared function calls a private function from another file | Shared helpers should not reach into another file’s private implementation. |
| Type 5 | Private function calls a private function from another file | Private helpers should stay file-local. |
| Type 6 | Private function calls a shared function directly | Private implementation details may need boundary review if they depend outward on shared helpers. |

### Inventory suggestions

| Suggestion | Calculation | Reviewer action |
|---|---|---|
| Inline candidate | Called by exactly one parent, not used elsewhere, not recursive, not called multiple times by the same parent | Consider absorbing the helper into its caller. |
| Promote to shared | Private function called by more than one distinct caller | Consider moving it to a shared helper boundary. |

## 4. Export a focused AI refactor packet

When a selected public function has cleanup signals, use the dashboard export workflow to create a focused packet for AI-assisted review or refactoring.

![AI refactor packet export](../assets/fabricops-call-graph-ai-refactor-package.png)

The export should keep the packet focused on the selected public callable flow rather than dumping the whole repository. The goal is to give AI enough context to suggest a safe cleanup plan without making the prompt too large or vague.

![AI refactor packet contents](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

Use the export packet for:

* public functions with architecture violations
* public functions with large width or depth
* selected call flows with many helper layers
* private helpers that can be inlined into their owner
* private helpers that should become shared helpers

## 5. How is all these set up? 
![Public Function Call Flows Dashboard Setup](../assets/fabricops-call-graph-setup.png)

`docs/reference/_data/public-function-call-flows.json` is the generated architecture contract consumed by the dashboard and generated reference pages.

The JSON contract is generated by:

* [`scripts/generate_public_function_call_flows_json.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_public_function_call_flows_json.py)

The generator scans the source code and identifies:

* public callable functions
* supporting private functions
* shared helpers
* classes
* internal methods
* dependency edges between functions and modules

The generator writes:

* [public-function-call-flows.json](_data/public-function-call-flows.json)

The repository source code and JSON generator remain authoritative if a committed JSON snapshot drifts.

## 6. Agent runs the generator upon function change

`AGENTS.md` is the operating guide for Codex and other agent contributions. It tells agents to use the public call-flow JSON as a planning and review contract before changing function-level source code.

Before changing a public callable, shared helper, private helper, callable classification, or generated reference contract, agents should check the relevant entries in `public-function-call-flows.json` to understand the current public callable scope, callees, helper reachability, source locations, architecture signals, cleanup signals, and defined-but-not-used functions.

When changing function-level source code, agents must run:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

Agents commit the regenerated `docs/reference/_data/public-function-call-flows.json` when the change affects callable structure, source locations, public exports, helper relationships, architecture classification, or public function flow metrics.

## 7. The generators are separated , json, dashboard , individual function pages

Generator ownership is split across focused scripts:

| Script | Owns |
|---|---|
| `scripts/generate_public_function_call_flows_json.py` | Generated JSON architecture contract at `docs/reference/_data/public-function-call-flows.json`. |
| `scripts/generate_public_function_call_flows_dashboard.py` | Published dashboard frontend at `docs/assets/public-function-call-flows-dashboard.html`. |
| `scripts/generate_individual_function_reference_pages.py` | Generated individual reference pages under `docs/api/reference/` and `docs/reference/index.md`. It does not own this standalone explanatory page. |

The dashboard should consume the generated JSON instead of recalculating architecture data itself. This keeps one source of truth for the dashboard and docs.

For function-level source changes that affect callable structure, update the source and scanner rules first, then regenerate and commit only `docs/reference/_data/public-function-call-flows.json` unless the PR is explicitly scoped as a generated-reference refresh.

Do not commit generated dashboard HTML or individual function pages in ordinary source cleanup PRs unless the PR is intentionally refreshing those generated surfaces.
