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
            "These terms describe how FabricOps implements its Data Engineering and Governance practice. "
            "Where a broader industry concept exists, the definitions here describe how FabricOps uses it."
        ),
        [
            "FabricOps Starter Kit",
            "governance as code",
            "configuration-driven engineering",
            "data agreement",
            "enrichment",
            "guardrails",
            "enforcement",
            "guardrail result",
            "data contract",
            "full dataset",
            "incremental watermark",
            "incremental partition",
            "incremental subset",
        ],
    ),
    (
        "Microsoft Fabric concepts",
        (
            "Microsoft owns these product terms. FabricOps follows Microsoft Fabric terminology "
            "and links to Microsoft Learn as the source of truth."
        ),
        [
            "Microsoft Fabric",
            "workspace",
            "Lakehouse",
            "Warehouse",
            "notebook",
        ],
    ),
    (
        "Governance concepts",
        (
            "Established data-governance and security concepts. FabricOps keeps their standard meaning "
            "and only adds implementation context where relevant."
        ),
        [
            "data steward",
            "metadata",
            "data sensitivity",
            "PII",
            "data access",
            "data quality",
            "access control",
            "row-level security",
            "object-level security",
        ],
    ),
    (
        "Engineering concepts",
        (
            "Established data-engineering concepts. FabricOps keeps their standard meaning "
            "and states any FabricOps-specific constraint explicitly."
        ),
        [
            "configuration",
            "pipeline",
            "PySpark",
            "profile",
            "schema",
            "watermark",
            "parallel processing",
            "data modelling",
            "partition",
            "physical partitioning",
            "append",
            "overwrite",
            "slowly changing dimensions",
        ],
    ),
]

DISPLAY_NAMES = {
    "profile": "Profile",
    "metadata": "Metadata",
    "governance as code": "Governance as Code",
    "configuration-driven engineering": "Configuration-driven Engineering",
    "data steward": "Data Steward",
    "data agreement": "Data Agreement",
    "enrichment": "Enrichment",
    "data sensitivity": "Data Sensitivity",
    "data access": "Data Access",
    "data quality": "Data Quality",
    "guardrails": "Guardrails",
    "enforcement": "Enforcement",
    "guardrail result": "Guardrail Result",
    "data contract": "Data Contract",
    "access control": "Access Control",
    "row-level security": "Row-Level Security (RLS)",
    "object-level security": "Object-Level Security (OLS)",
    "workspace": "Workspace",
    "notebook": "Notebook",
    "configuration": "Configuration",
    "pipeline": "Pipeline",
    "parallel processing": "Parallel Processing",
    "full dataset": "Full Dataset",
    "incremental watermark": "Incremental Watermark",
    "incremental partition": "Incremental Partition",
    "incremental subset": "Incremental Subset",
    "watermark": "Watermark",
    "data modelling": "Data Modelling",
    "schema": "Schema",
    "partition": "Partition",
    "physical partitioning": "Physical Partitioning",
    "append": "Append",
    "overwrite": "Overwrite",
    "slowly changing dimensions": "Slowly Changing Dimensions (SCD)",
}


def _slug(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def _display_name(term: str) -> str:
    return DISPLAY_NAMES.get(term, term)


def _text(value: object) -> str:
    return html.escape(str(value), quote=False)


def build_glossary_page() -> str:
    """Return the generated glossary Markdown."""
    entries = json.loads(GLOSSARY_DATA_PATH.read_text(encoding="utf-8"))
    by_term = {str(entry["term"]): entry for entry in entries}

    ordered_terms = [term for _, _, terms in GLOSSARY_GROUPS for term in terms]
    missing = sorted(set(ordered_terms) - set(by_term))
    unassigned = sorted(set(by_term) - set(ordered_terms))
    duplicates = sorted({term for term in ordered_terms if ordered_terms.count(term) > 1})
    category_mismatches = sorted(
        (term, str(by_term[term]["category"]), group_name)
        for group_name, _, terms in GLOSSARY_GROUPS
        for term in terms
        if term in by_term and str(by_term[term]["category"]) != group_name
    )
    if missing or unassigned or duplicates or category_mismatches:
        raise RuntimeError(
            "Glossary groups must cover every canonical term exactly once and "
            "match its canonical category. "
            f"Missing={missing}; unassigned={unassigned}; duplicates={duplicates}; "
            f"category_mismatches={category_mismatches}."
        )

    lines = [
        "<!-- GENERATED FILE: edit docs/reference/_data/glossary.json or scripts/generate_glossary_page.py -->",
        "",
        "# FabricOps glossary",
        "",
        (
            "Use this page as the repository source of truth for FabricOps, Microsoft Fabric, "
            "Governance, and Data Engineering terminology."
        ),
        "",
        (
            "Definitions are grounded first in the current FabricOps implementation. Microsoft Fabric "
            "terms follow Microsoft terminology and link to Microsoft Learn. Established Governance and "
            "Engineering terms keep their standard meaning unless FabricOps explicitly documents a "
            "narrower implementation."
        ),
        "",
    ]

    for group_name, subtitle, terms in GLOSSARY_GROUPS:
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
        for term in terms:
            entry = by_term[term]
            aliases = [str(alias) for alias in entry.get("aliases", [])]
            summary = (
                f"<summary><strong>{_text(_display_name(term))}</strong> — "
                f"{_text(entry['short_definition'])}</summary>"
            )
            lines.extend(
                [
                    f'<details id="{_slug(term)}">',
                    summary,
                    f"<p>{_text(entry['long_definition'])}</p>",
                ]
            )
            learn_url = str(entry.get("learn_url") or "").strip()
            if learn_url:
                lines.append(
                    f'<p><strong>Microsoft Learn:</strong> '
                    f'<a href="{html.escape(learn_url, quote=True)}">'
                    "Official definition and documentation</a></p>"
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
