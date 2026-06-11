from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from fabricops_kit.config import (
    AIPromptConfig,
    DataAgreementConfig,
    FrameworkConfig,
    NotebookRuntimeConfig,
    PathConfig,
)
from fabricops_kit.fabric_input_output import FabricStore


def store(kind: str = "lakehouse", *, env: str = "dev", name: str | None = None) -> FabricStore:
    return FabricStore(
        env=env,
        workspace_id=f"{env}-workspace",
        item_id=f"{env}-{kind}-item",
        name=name or f"{kind}_{env}",
        kind=kind,
    )


def framework_config() -> FrameworkConfig:
    return FrameworkConfig(
        path_config=PathConfig(
            paths={
                "dev": {
                    "source": store("lakehouse", name="lh_source_dev"),
                    "unified": store("lakehouse", name="lh_unified_dev"),
                    "product": store("warehouse", name="wh_product_dev"),
                    "metadata": store("lakehouse", name="lh_metadata_dev"),
                    "warehouse": store("warehouse", name="wh_product_dev"),
                }
            }
        ),
        notebook_runtime_config=NotebookRuntimeConfig(),
        ai_prompt_config=AIPromptConfig(),
        data_agreement_config=DataAgreementConfig(),
    )


def agreement_config(*, metadata_tables: dict[str, str] | None = None) -> SimpleNamespace:
    from fabricops_kit.data_agreement import DATA_AGREEMENT_EVIDENCE_TABLE, DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE

    return SimpleNamespace(
        path_config=SimpleNamespace(paths={"dev": {"metadata": store("lakehouse", name="lh_metadata_dev")}}),
        data_agreement_config=DataAgreementConfig(
            metadata_tables=metadata_tables
            or {
                "data_steward": DATA_STEWARD_TABLE,
                "data_agreement": DATA_AGREEMENT_TABLE,
                "data_agreement_evidence": DATA_AGREEMENT_EVIDENCE_TABLE,
            },
            data_steward_widget={
                "visible_columns": ["steward_name", "steward_role", "contact", "effective_from", "effective_to"],
                "custom_fields": [{"key": "group", "label": "Group", "type": "text"}],
            },
            data_agreement_widget={
                "visible_columns": [
                    "agreement_name",
                    "domain",
                    "steward_id",
                    "recipient",
                    "start_date",
                    "expiry_date",
                    "business_purpose",
                    "approved_usage_internal",
                    "approved_usage_external",
                    "approved_usage_research",
                ],
                "custom_fields": [
                    {"key": "consumer_group", "label": "Consumer group", "type": "select", "options": ["ODI"]}
                ],
            },
            steward_role_options=["Data Owner", "Data Steward", "Governance Reviewer"],
        ),
    )


def steward_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "steward_id": "steward-001",
        "steward_name": "Configured Steward",
        "steward_role": "Data Steward",
        "contact": "steward@example.com",
        "effective_from": "2026-01-01",
        "effective_to": "",
        "is_active": True,
    }
    row.update(overrides)
    return row


def agreement_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "agreement_name": "Orders Agreement",
        "domain": "Operations",
        "steward_id": "steward-001",
        "recipient": "Internal analytics team",
        "start_date": "2026-01-01",
        "expiry_date": "2026-12-31",
        "business_purpose": "Governed reporting",
        "approved_usage_internal": "Approved internal reporting only",
        "approved_usage_external": "",
        "approved_usage_research": "",
    }
    row.update(overrides)
    return row


@dataclass
class FakeFrame:
    rows: list[dict[str, Any]]
    columns: list[str] | None = None

    def __post_init__(self) -> None:
        if self.columns is None:
            self.columns = list(self.rows[0]) if self.rows else []

    def limit(self, count: int) -> "FakeFrame":
        return FakeFrame(self.rows[:count], columns=list(self.columns or []))


class FakeSpark:
    def __init__(self) -> None:
        self.source_rows: list[list[dict[str, Any]]] = []

    def createDataFrame(self, rows, schema=None):  # noqa: N802
        if schema is not None:
            columns = schema.fieldNames()
            shaped_rows = [dict(zip(columns, row)) if not isinstance(row, dict) else row for row in rows]
            self.source_rows.append(shaped_rows)
            return FakeFrame(shaped_rows, columns=columns)
        rows = list(rows)
        self.source_rows.append(rows)
        return FakeFrame(rows)
