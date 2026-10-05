# `create_data_agent`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Create and configure one native Fabric Data Agent from an activated Production table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agent/create_data_agent.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agent/create_data_agent.py#L8-L79">View on GitHub</a>
</div>

## Usage notes

Do not use for multi-table agents, relationship authoring, evaluation, or automatic publication.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def create_data_agent(
    table_id: str,
    target_workspace_id: str,
    display_name: str,
    description: str='FabricOps governed single-table Data Agent',
    config: Any=None,
    context: Mapping[str, Any] | None=None,
    spark_session: Any=None,
    token_provider: Callable[[], str]=default_token_provider,
    transport: Callable[[str, str, Mapping[str, Any] | None, str], FabricResponse]=http_request,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = create_data_agent(
...     "lakehouse||production||dbo||orders",
...     target_workspace_id="00000000-0000-0000-0000-000000000000",
...     display_name="Governed orders",
... )
>>> result["status"]
'configured'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str` | Yes | Canonical FabricOps identity for one activated Production table. |
| `target_workspace_id` | `str` | Yes | Fabric workspace in which to create the Data Agent. |
| `display_name` | `str` | Yes | Data Agent display name. |
| `description` | `str` | No | Data Agent item description. |
| `config` | `Any` | No | FabricOps configuration. The configured notebook value is used when omitted. |
| `context` | `Mapping[str, Any] \| None` | No | FabricOps runtime context used to resolve configuration and Spark. |
| `spark_session` | `Any` | No | Explicit Spark session used to read metadata. |
| `token_provider` | `Callable[[], str]` | No | Token provider integration boundary. Defaults to Fabric ``notebookutils``. |
| `transport` | `Callable[[str, str, Mapping[str, Any] \| None, str], FabricResponse]` | No | HTTP integration boundary, primarily for isolated testing. |

## Returns

Agent and datasource identities plus useful configuration status.

## Raises / Errors

Raises for invalid governed sources, authentication, permission, REST, malformed response, and LRO failures.

## Notes

<div class="reference-docstring-notes" markdown="1">

This Preview API requires a supported Fabric capacity, access to the Production
Lakehouse or Warehouse, and permission to create and configure Data Agents in
the target workspace. It builds governed consumer context from the active
Production Data Contract, renders deterministic instructions, creates a staging
datasource, selects one table, and applies the datasource and agent instructions.
It does not publish the agent.

</div>

## See also

No related guides documented.


<details>
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
