"""Shared deterministic context and Microsoft Fabric Data Agent integration."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.pipeline.shared import resolve_active_data_contract, resolve_catalogue_table_identity

FABRIC_API_ROOT = "https://api.fabric.microsoft.com/v1"
FABRIC_AUDIENCE = "https://api.fabric.microsoft.com"


class FabricDataAgentError(RuntimeError):
    """Report a failed or malformed Microsoft Fabric Data Agent operation."""


@dataclass(frozen=True)
class FabricResponse:
    """Small HTTP response value used at the Fabric REST boundary."""

    status: int
    headers: Mapping[str, str]
    body: Mapping[str, Any] | None


def _text(value: Any) -> str:
    return str(value or "").strip()


def consumer_context(config: Any, table_id: str, *, spark_session: Any = None) -> dict[str, Any]:
    """Assemble safe consumer context from one active Production contract."""
    identity = resolve_catalogue_table_identity(config, "prod", table_id, spark_session=spark_session)
    contract = resolve_active_data_contract(config, "prod", table_id, spark_session=spark_session, required=True)
    payload = contract["contract_payload"]
    table = payload["table"]
    if _text(table.get("table_id")) != _text(identity.get("table_id")):
        raise RuntimeError("Active Data Contract and Production Catalogue identity do not match.")

    store = get_store(config, "prod", _text(identity.get("layer")))
    if store.kind not in {"lakehouse", "warehouse"}:
        raise ValueError(f"Data Agent source type {store.kind!r} is unsupported.")
    if store.kind != _text(identity.get("store_type")).casefold():
        raise ValueError("Configured Production store type does not match the governed Catalogue asset.")

    enrichments = [
        dict(row) for group in (payload.get("enrichment") or {}).values() for row in group
        if isinstance(row, Mapping) and _text(row.get("value"))
    ]
    table_enrichment = {
        _text(row.get("enrichment_type")): _text(row.get("value"))
        for row in enrichments if not _text(row.get("column_id"))
    }
    column_enrichment: dict[str, dict[str, str]] = {}
    for row in enrichments:
        column_id = _text(row.get("column_id"))
        if column_id:
            column_enrichment.setdefault(column_id, {})[_text(row.get("enrichment_type"))] = _text(row.get("value"))

    columns = []
    for column in sorted(table.get("columns") or [], key=lambda item: _text(item.get("column_name")).casefold()):
        values = column_enrichment.get(_text(column.get("column_id")), {})
        columns.append({
            "name": _text(column.get("column_name")),
            "data_type": _text(column.get("data_type")),
            **({"description": values["Description"]} if values.get("Description") else {}),
            **({"business_terms": values["Business Term"]} if values.get("Business Term") else {}),
            **({"classification": values["Classification"]} if values.get("Classification") else {}),
            **({"sensitivity": values["Sensitive Data"]} if values.get("Sensitive Data") else {}),
        })

    rules = []
    for rule in sorted(payload.get("guardrails") or [], key=lambda item: (_text(item.get("guardrail_type")), _text(item.get("rule_id")))):
        if rule.get("is_active", True) is False:
            continue
        rules.append({key: rule[key] for key in ("guardrail_type", "rule_type", "column_id", "action", "severity", "rule_parameters") if rule.get(key) not in (None, "", {})})

    return {
        "table_id": _text(table_id),
        "environment": "prod",
        "contract": {
            "contract_id": _text(contract.get("contract_id")),
            "contract_version": int(contract.get("contract_version") or 0),
            "agreement_id": _text(contract.get("agreement_id")),
            "agreement_version": _text(contract.get("agreement_version")),
        },
        "source": {
            "type": store.kind,
            "workspace_id": store.workspace_id,
            "item_id": store.item_id,
            "schema": _text(identity.get("schema")) or None,
            "table": _text(identity.get("table_name")),
        },
        "description": table_enrichment.get("Description", ""),
        "grain": table_enrichment.get("Grain", ""),
        "business_rules": table_enrichment.get("Business Rules", ""),
        "classification": table_enrichment.get("Classification", ""),
        "known_limitations": table_enrichment.get("Known Limitations", ""),
        "freshness": table.get("scheduled_refresh") or {},
        "columns": columns,
        "guardrails": rules,
    }


def instruction_text(context: Mapping[str, Any]) -> dict[str, str]:
    """Render concise, stable agent and datasource instructions."""
    source = context["source"]
    qualified = ".".join(part for part in (_text(source.get("schema")), _text(source.get("table"))) if part)
    agent = (
        "Use only the configured governed Production table. Do not infer undocumented business meaning, "
        "relationships, or classifications. State when the available metadata cannot answer a question."
    )
    lines = [f"Table: {qualified}."]
    for label, key in (("Purpose", "description"), ("Grain", "grain"), ("Business rules", "business_rules"),
                       ("Classification", "classification"), ("Known limitations", "known_limitations")):
        if _text(context.get(key)):
            lines.append(f"{label}: {_text(context[key])}")
    lines.append("Columns:")
    for column in context.get("columns") or []:
        detail = [f"type={_text(column.get('data_type'))}"]
        for key in ("description", "business_terms", "classification", "sensitivity"):
            if _text(column.get(key)):
                detail.append(f"{key.replace('_', ' ')}={_text(column[key])}")
        lines.append(f"- {_text(column.get('name'))}: " + "; ".join(detail))
    if context.get("guardrails"):
        lines.append("Governed rules:")
        for rule in context["guardrails"]:
            lines.append("- " + json.dumps(rule, sort_keys=True, separators=(",", ":")))
    return {"agent": agent, "datasource": "\n".join(lines)}


def default_token_provider() -> str:
    """Acquire a Fabric token from the active notebook runtime."""
    try:
        import notebookutils  # type: ignore
        token = notebookutils.credentials.getToken(FABRIC_AUDIENCE)
    except (ImportError, AttributeError, RuntimeError) as exc:
        raise FabricDataAgentError("Fabric notebook authentication is unavailable; run in Fabric with an authorized caller.") from exc
    if not _text(token):
        raise FabricDataAgentError("Fabric notebook authentication returned an empty access token.")
    return str(token)


def http_request(method: str, url: str, body: Mapping[str, Any] | None, token: str) -> FabricResponse:
    """Send one authenticated request to the fixed Microsoft Fabric API host."""
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, method=method, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed Fabric API root
            raw = response.read().decode()
            return FabricResponse(response.status, dict(response.headers.items()), json.loads(raw) if raw else None)
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise FabricDataAgentError(f"Fabric API {method} failed with HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise FabricDataAgentError(f"Fabric API {method} request failed: {exc.reason}") from exc


def _header(headers: Mapping[str, str], name: str) -> str:
    return next((_text(value) for key, value in headers.items() if key.casefold() == name.casefold()), "")


def fabric_request(
    method: str, path: str, body: Mapping[str, Any] | None, *, token: str,
    transport: Callable[[str, str, Mapping[str, Any] | None, str], FabricResponse] = http_request,
    sleep: Callable[[float], None] = time.sleep,
) -> Mapping[str, Any]:
    """Execute one Fabric REST request and await a returned long-running operation."""
    response = transport(method, f"{FABRIC_API_ROOT}{path}", body, token)
    if response.status not in {200, 201, 202}:
        raise FabricDataAgentError(f"Fabric API returned unexpected HTTP {response.status}: {response.body!r}")
    if response.status != 202:
        if not isinstance(response.body, Mapping):
            raise FabricDataAgentError("Fabric API returned a malformed success response.")
        return response.body
    operation = _header(response.headers, "Location") or _header(response.headers, "Operation-Location")
    if not operation:
        raise FabricDataAgentError("Fabric API accepted the request without an operation location.")
    for _ in range(120):
        retry = float(_header(response.headers, "Retry-After") or 2)
        sleep(max(retry, 0))
        response = transport("GET", operation, None, token)
        payload = response.body
        if response.status != 200 or not isinstance(payload, Mapping):
            raise FabricDataAgentError("Fabric long-running operation returned a malformed response.")
        status = _text(payload.get("status")).casefold()
        if status in {"succeeded", "completed"}:
            result = payload.get("result")
            return result if isinstance(result, Mapping) else payload
        if status in {"failed", "cancelled", "canceled"}:
            raise FabricDataAgentError(f"Fabric long-running operation {status}: {payload.get('error')!r}")
    raise FabricDataAgentError("Fabric long-running operation did not finish before the polling limit.")


def provision_data_agent(
    context: Mapping[str, Any], *, target_workspace_id: str, display_name: str,
    description: str, token_provider: Callable[[], str] = default_token_provider,
    transport: Callable[[str, str, Mapping[str, Any] | None, str], FabricResponse] = http_request,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Create and configure one native Data Agent using the documented staging resources."""
    token = token_provider()
    instructions = instruction_text(context)
    base = f"/workspaces/{target_workspace_id}/dataAgents"
    agent = fabric_request("POST", base, {"displayName": display_name, "description": description}, token=token, transport=transport, sleep=sleep)
    agent_id = _text(agent.get("id"))
    if not agent_id:
        raise FabricDataAgentError("Fabric create Data Agent response did not include an id.")
    staging = f"{base}/{agent_id}/staging"
    source = context["source"]
    datasource = fabric_request("POST", f"{staging}/dataSources", {
        "displayName": _text(source.get("table")), "type": str(source.get("type")).title(),
        "itemReference": {
            "referenceType": "ById",
            "workspaceId": source.get("workspace_id"),
            "itemId": source.get("item_id"),
        },
    }, token=token, transport=transport, sleep=sleep)
    datasource_id = _text(datasource.get("id"))
    if not datasource_id:
        raise FabricDataAgentError("Fabric create datasource response did not include an id.")
    fabric_request("PATCH", f"{staging}/dataSources/{datasource_id}", {
        "instructions": instructions["datasource"],
    }, token=token, transport=transport, sleep=sleep)
    elements = fabric_request(
        "GET", f"{staging}/dataSources/{datasource_id}/elements", None,
        token=token, transport=transport, sleep=sleep,
    )
    values = elements.get("value")
    if not isinstance(values, list):
        raise FabricDataAgentError("Fabric datasource elements response did not include a value list.")
    requested_table = _text(source.get("table")).casefold()
    requested_schema = _text(source.get("schema")).casefold()
    matches = []
    for element in values:
        if not isinstance(element, Mapping):
            continue
        element_name = _text(element.get("name") or element.get("displayName")).casefold()
        element_schema = _text(element.get("schema") or element.get("schemaName")).casefold()
        element_type = _text(element.get("type") or element.get("elementType")).casefold()
        if (
            element_name == requested_table
            and (not requested_schema or element_schema == requested_schema)
            and (not element_type or element_type == "table")
        ):
            matches.append(element)
    if len(matches) != 1:
        raise FabricDataAgentError(
            f"Fabric datasource must expose exactly one matching table element for "
            f"{source.get('schema') or '<default>'}.{source.get('table')}; found {len(matches)}."
        )
    element_id = _text(matches[0].get("id"))
    if not element_id:
        raise FabricDataAgentError("Fabric datasource table element did not include an id.")
    fabric_request(
        "PATCH", f"{staging}/dataSources/{datasource_id}/elements/{element_id}",
        {"isSelected": True}, token=token, transport=transport, sleep=sleep,
    )
    configured = fabric_request(
        "PATCH", f"{staging}/settings", {"aiInstructions": instructions["agent"]},
        token=token, transport=transport, sleep=sleep,
    )
    return {
        "agent_id": agent_id, "datasource_id": datasource_id,
        "workspace_id": target_workspace_id,
        "display_name": display_name,
        "status": _text(configured.get("status")) or "configured",
        "source_table_id": context["table_id"],
    }


def configured_context(config: Any | None, context: Mapping[str, Any] | None) -> tuple[Any, Any]:
    """Resolve package configuration and Spark from the normal FabricOps runtime context."""
    resolved_config, _, runtime = resolve_fabric_context(config=config, env="prod", context=dict(context or {}))
    return resolved_config, runtime.get("spark")
