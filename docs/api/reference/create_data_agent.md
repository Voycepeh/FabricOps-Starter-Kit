# `create_data_agent`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Create and configure one native Fabric Data Agent from an activated Production table.


## Usage notes

Use to create a Data Agent from one activated Production table.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = create_data_agent(table_id, target_workspace_id=workspace_id, display_name="Governed orders")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def create_data_agent(
    table_id: str,
    target_workspace_id: str,
    display_name: str,
    *,
    description: str='FabricOps governed single-table Data Agent',
    config: Any=None,
    context: Mapping[str, Any] | None=None,
    spark_session: Any=None,
    token_provider: Callable[[], str]=default_token_provider,
    transport: Callable[[str, str, Mapping[str, Any] | None, str], FabricResponse]=http_request,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_id` | `str` | Yes | `—` | Canonical FabricOps identity for one activated Production table. |
| `target_workspace_id` | `str` | Yes | `—` | Fabric workspace in which to create the Data Agent. |
| `display_name` | `str` | Yes | `—` | Data Agent display name. |
| `description` | `str` | No | `'FabricOps governed single-table Data Agent'` | Data Agent item description. |
| `config` | `Any` | No | `None` | FabricOps configuration. The configured notebook value is used when omitted. |
| `context` | `Mapping[str, Any] \| None` | No | `None` | FabricOps runtime context used to resolve configuration and Spark. |
| `spark_session` | `Any` | No | `None` | Explicit Spark session used to read metadata. |
| `token_provider` | `Callable[[], str]` | No | `default_token_provider` | Token provider integration boundary. Defaults to Fabric ``notebookutils``. |
| `transport` | `Callable[[str, str, Mapping[str, Any] \| None, str], FabricResponse]` | No | `http_request` | HTTP integration boundary, primarily for isolated testing. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = create_data_agent(
    "lakehouse||production||dbo||orders",
    target_workspace_id="00000000-0000-0000-0000-000000000000",
    display_name="Governed orders",
)
result["status"]
```

```text
'configured'
```

</div>

## Returns

dict[str, Any]
    Created agent and datasource identities, workspace, display name, source
    ``table_id``, and the final useful configuration status.

## Raises / Errors

ValueError
    If inputs or governed Production source metadata are invalid.
FabricDataAgentError
    If authentication, permissions, a Fabric REST request, response validation,
    or long-running operation fails. Fabric error details are retained.

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

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_agent/create_data_agent.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agent/create_data_agent.py#L8-L79">View on GitHub</a>
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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.5 |


</details>
