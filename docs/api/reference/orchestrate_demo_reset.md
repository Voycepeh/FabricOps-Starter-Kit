# `orchestrate_demo_reset`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Preview or reset the dedicated Guided Demo to Day 1.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Preview is the default. reset=True discards all dedicated demo metadata, including frozen Contracts and activations, and resets only the eleven named business tables. This Preview API still requires live Fabric acceptance.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
from fabricops_kit import setup_notebook, orchestrate_demo_reset

context = setup_notebook()
RESET_DEMO = False
orchestrate_demo_reset(reset=RESET_DEMO)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def orchestrate_demo_reset(*, reset: bool=False) -> None
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `reset` | `bool` | No | `False` | False prints configured store identities, metadata row counts and the eleven business tables in scope without writing. True opts into the destructive reset after all preflight checks pass. Only booleans are accepted; strings and integers are rejected. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
from fabricops_kit import setup_notebook, orchestrate_demo_reset
context = setup_notebook()
RESET_DEMO = False  # Set True only to discard the dedicated demo state.
orchestrate_demo_reset(reset=RESET_DEMO)
```

</div>

## Returns

None
    Prints a preview or verified reset summary, including actual removed
    metadata counts. ``RESET COMPLETE`` is printed only after verification.

## Raises / Errors

ValueError
    If reset is not a boolean.
RuntimeError
    If notebook setup is not ready, required stores or metadata schemas
    are invalid, non-demo references are found, fixtures
    are unavailable, or reset verification fails. Fabric/Spark permission,
    transport and storage failures propagate; correct the cause and rerun.

## Notes

<div class="reference-docstring-notes" markdown="1">

True clears all current canonical metadata rows in the dedicated item,
including frozen Contracts, activations, approvals, promotion history,
Runs and Processing State. Saved submissions, Dry Run evidence and notebook
snapshots in its three native lifecycle folders are removed too. Table
definitions remain; no metadata migration is performed.

Four Day 1 tables are overwritten, Orders CSV is validated and retained,
and five Silver outputs plus the obsolete Bronze Orders table are removed in the reserved
``demo`` schemas of the configured Bronze/Silver stores. The Gold customer_summary
table is retained with zero rows when present. Other business
tables and source files are preserved. Exact demo table/workspace references,
artifact contents, fixture counts and catalog locations are
checked before deletion. A dedicated name alone cannot prove ownership;
never share this Metadata item or these eleven tables with other projects.

Missing outputs and repeated resets are supported. A failure may leave a
partial reset: this operation is not atomic across tables/stores. Stop all
writers, correct the reported cause and rerun. Deployed notebooks, schedules
and apps are not removed. Live Fabric acceptance is still required.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call after ``setup_notebook()`` with the package being validated installed.
The configured logical ``Metadata`` store must select a manually created,
schema-enabled Lakehouse named ``demo_metadata``, reserved exclusively for
this walkthrough. Stop all demo executions and schedules before resetting.

</div>

## See also

- [Prepare and reset the demo](../../guided-demo/00C-prepare-demo-data-with-fabricops-io.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/orchestrate_demo_reset.py:240`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/orchestrate_demo_reset.py#L240-L444">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |


</details>
