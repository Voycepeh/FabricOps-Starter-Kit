"""Generate the committed FabricOps glossary page from canonical glossary data."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_DATA_PATH = ROOT / "docs" / "reference" / "_data" / "glossary.json"
GLOSSARY_PAGE_PATH = ROOT / "docs" / "glossary.md"

GLOSSARY_GROUPS = [
    (
        "FabricOps concepts",
        (
            "Terms that describe how FabricOps implements its governed engineering practice. "
            "These definitions are the FabricOps meaning used throughout this repository."
        ),
        [
            "fabricops-starter-kit",
            "data-agreement",
            "data-contract",
            "enrichment",
            "guardrails",
            "enforcement",
            "guardrail-result",
            "governance-as-code",
            "configuration-driven-engineering",
            "full-dataset",
            "incremental-watermark",
            "incremental-partition",
            "incremental-subset",
        ],
    ),
    (
        "Microsoft Fabric concepts",
        (
            "Microsoft Fabric terms. Definitions follow Microsoft terminology where possible "
            "and link to the relevant Microsoft Learn documentation."
        ),
        [
            "microsoft-fabric",
            "workspace",
            "lakehouse",
            "warehouse",
            "notebook",
            "medallion-architecture",
        ],
    ),
    (
        "Data Governance concepts",
        (
            "Established governance terms used by FabricOps. The definitions keep their broader "
            "governance meaning and describe FabricOps usage only where relevant."
        ),
        [
            "metadata",
            "data-steward",
            "data-sensitivity",
            "pii",
            "data-access",
            "data-quality",
            "access-control",
            "row-level-security",
            "object-level-security",
        ],
    ),
    (
        "Data Engineering concepts",
        (
            "Established engineering terms used by FabricOps. The definitions keep their broader "
            "engineering meaning and call out FabricOps behaviour only where it materially matters."
        ),
        [
            "configuration",
            "pipeline",
            "pyspark",
            "profile",
            "schema",
            "watermark",
            "parallel-processing",
            "data-modelling",
            "partition",
            "physical-partitioning",
            "append",
            "overwrite",
            "slowly-changing-dimensions",
        ],
    ),
]

DISPLAY_NAMES = {
    "fabricops-starter-kit": "FabricOps Starter Kit",
    "data-agreement": "Data Agreement",
    "data-contract": "Data Contract",
    "enrichment": "Enrichment",
    "guardrails": "Guardrails",
    "enforcement": "Enforcement",
    "guardrail-result": "Guardrail Result",
    "governance-as-code": "Governance as Code",
    "configuration-driven-engineering": "Configuration-driven Engineering",
    "full-dataset": "Full Dataset",
    "incremental-watermark": "Incremental Watermark",
    "incremental-partition": "Incremental Partition",
    "incremental-subset": "Incremental Subset",
    "microsoft-fabric": "Microsoft Fabric",
    "workspace": "Workspace",
    "lakehouse": "Lakehouse",
    "warehouse": "Warehouse",
    "notebook": "Notebook",
    "medallion-architecture": "Medallion Architecture",
    "metadata": "Metadata",
    "data-steward": "Data Steward",
    "data-sensitivity": "Data Sensitivity",
    "pii": "PII",
    "data-access": "Data Access",
    "data-quality": "Data Quality",
    "access-control": "Access Control",
    "row-level-security": "Row-Level Security (RLS)",
    "object-level-security": "Object-Level Security (OLS)",
    "configuration": "Configuration",
    "pipeline": "Pipeline",
    "pyspark": "PySpark",
    "profile": "Profile",
    "schema": "Schema",
    "watermark": "Watermark",
    "parallel-processing": "Parallel Processing",
    "data-modelling": "Data Modelling",
    "partition": "Partition",
    "physical-partitioning": "Physical Partitioning",
    "append": "Append",
    "overwrite": "Overwrite",
    "slowly-changing-dimensions": "Slowly Changing Dimensions (SCD)",
}

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _text(value: object) -> str:
    return html.escape(str(value), quote=False)


def load_glossary_entries() -> list[dict[str, object]]:
    """Load and validate canonical glossary entries."""
    entries = json.loads(GLOSSARY_DATA_PATH.read_text(encoding="utf-8"))
    ids = [str(entry.get("id") or "") for entry in entries]
    if any(not ID_PATTERN.fullmatch(entry_id) for entry_id in ids):
        raise RuntimeError("Every glossary entry must define a stable lowercase kebab-case id.")
    if len(ids) != len(set(ids)):
        raise RuntimeError("Glossary ids must be unique.")

    ordered_ids = [entry_id for _, _, group_ids in GLOSSARY_GROUPS for entry_id in group_ids]
    missing = sorted(set(ordered_ids) - set(ids))
    unassigned = sorted(set(ids) - set(ordered_ids))
    duplicates = sorted({entry_id for entry_id in ordered_ids if ordered_ids.count(entry_id) > 1})
    by_id = {str(entry["id"]): entry for entry in entries}
    category_mismatches = sorted(
        (entry_id, str(by_id[entry_id]["category"]), group_name)
        for group_name, _, group_ids in GLOSSARY_GROUPS
        for entry_id in group_ids
        if entry_id in by_id and str(by_id[entry_id]["category"]) != group_name
    )
    if missing or unassigned or duplicates or category_mismatches:
        raise RuntimeError(
            "Glossary groups must cover every canonical id exactly once and match its category. "
            f"Missing={missing}; unassigned={unassigned}; duplicates={duplicates}; "
            f"category_mismatches={category_mismatches}."
        )
    return entries


def build_glossary_page() -> str:
    """Return the generated glossary Markdown."""
    entries = load_glossary_entries()
    by_id = {str(entry["id"]): entry for entry in entries}

    lines = [
        "<!-- GENERATED FILE: edit docs/reference/_data/glossary.json or scripts/generate_glossary_page.py -->",
        "",
        "# FabricOps glossary",
        "",
        (
            "This glossary is the canonical terminology source for FabricOps documentation. "
            "When a term is repeated elsewhere in the repository, its meaning should come from "
            "`docs/reference/_data/glossary.json` rather than being independently redefined."
        ),
        "",
        (
            "Terms are grouped by where their meaning comes from: FabricOps, Microsoft Fabric, "
            "Data Governance, or Data Engineering."
        ),
        "",
    ]

    for group_name, subtitle, group_ids in GLOSSARY_GROUPS:
        lines.extend(
            [
                "<details>",
                "<summary>",
                f"<strong>{_text(group_name)}</strong><br>",
                f"<span>{_text(subtitle)}</span>",
                "</summary>",
                "",
            ]
        )
        for entry_id in group_ids:
            entry = by_id[entry_id]
            aliases = [str(alias) for alias in entry.get("aliases", [])]
            display_name = DISPLAY_NAMES.get(entry_id, str(entry["term"]))
            lines.extend(
                [
                    f'<details id="{entry_id}">',
                    (
                        f"<summary><strong>{_text(display_name)}</strong> — "
                        f"{_text(entry['short_definition'])}</summary>"
                    ),
                    f"<p>{_text(entry['long_definition'])}</p>",
                ]
            )
            source_url = str(entry.get("source_url") or "").strip()
            if source_url:
                lines.append(
                    f'<p><strong>Microsoft Learn:</strong> <a href="{html.escape(source_url, quote=True)}">'
                    "Official documentation</a></p>"
                )
            if aliases:
                lines.append(f"<p><strong>Also known as:</strong> {_text(', '.join(aliases))}</p>")
            lines.extend(["</details>", ""])
        lines.extend(["</details>", ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    """Write the generated glossary page."""
    GLOSSARY_PAGE_PATH.write_text(build_glossary_page(), encoding="utf-8")


if __name__ == "__main__":
    main()
