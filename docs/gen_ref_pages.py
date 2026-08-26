"""Generate lightweight documentation pages from canonical documentation data."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import mkdocs_gen_files

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_PATH = ROOT / "docs" / "reference" / "_data" / "glossary.json"

GLOSSARY_GROUPS = [
    (
        "FabricOps concepts",
        "The small set of ideas that describe FabricOps as a governed Data Engineering practice.",
        [
            "FabricOps Starter Kit",
            "metadata",
            "governance as code",
            "configuration-driven engineering",
        ],
    ),
    (
        "Governance concepts",
        (
            "Terms encountered as Governance establishes ownership, expectations, "
            "rules, controls, and Production approval."
        ),
        [
            "data steward",
            "data agreement",
            "enrichment",
            "data sensitivity",
            "PII",
            "data access",
            "data quality",
            "guardrails",
            "enforcement",
            "guardrail result",
            "data contract",
            "access control",
            "row-level security",
            "object-level security",
        ],
    ),
    (
        "Engineering concepts",
        (
            "Terms encountered as Engineering sets up Fabric, builds pipelines, "
            "profiles data, and applies governed processing."
        ),
        [
            "Microsoft Fabric",
            "workspace",
            "Lakehouse",
            "Warehouse",
            "notebook",
            "configuration",
            "pipeline",
            "PySpark",
            "profile",
            "schema",
            "incremental load",
            "parallel processing",
            "data modelling",
            "partitioning",
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
    "incremental load": "Incremental Load",
    "data modelling": "Data Modelling",
    "partitioning": "Partitioning",
    "append": "Append",
    "overwrite": "Overwrite",
    "slowly changing dimensions": "Slowly Changing Dimensions (SCD)",
}


def _slug(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def _display_name(term: str) -> str:
    return DISPLAY_NAMES.get(term, term)


def _build_glossary_page() -> str:
    entries = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    by_term = {str(entry["term"]): entry for entry in entries}

    ordered_terms = [term for _, _, terms in GLOSSARY_GROUPS for term in terms]
    missing = sorted(set(ordered_terms) - set(by_term))
    unassigned = sorted(set(by_term) - set(ordered_terms))
    duplicates = sorted(
        {term for term in ordered_terms if ordered_terms.count(term) > 1}
    )
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
        "# FabricOps glossary",
        "",
        (
            "Use this page when a FabricOps, Governance, or Engineering term is "
            "unfamiliar. The definitions come directly from the canonical "
            "`docs/reference/_data/glossary.json` source."
        ),
        "",
        (
            "The order follows the FabricOps operating workflow so you can learn "
            "terminology close to where it appears in the Guided Demo."
        ),
        "",
    ]

    for group_name, subtitle, terms in GLOSSARY_GROUPS:
        lines.extend(
            [
                "<details>",
                "<summary>",
                f"<strong>{html.escape(group_name)}</strong><br>",
                f"<span>{html.escape(subtitle)}</span>",
                "</summary>",
                "",
            ]
        )
        for term in terms:
            entry = by_term[term]
            aliases = [str(alias) for alias in entry.get("aliases", [])]
            alias_text = ""
            if aliases:
                alias_text = (
                    "<p><strong>Also known as:</strong> "
                    f"{html.escape(', '.join(aliases))}</p>"
                )
            summary = (
                f"<summary><strong>{html.escape(_display_name(term))}</strong> — "
                f"{html.escape(str(entry['short_definition']))}</summary>"
            )
            lines.extend(
                [
                    f'<details id="{_slug(term)}">',
                    summary,
                    f"<p>{html.escape(str(entry['long_definition']))}</p>",
                    alias_text,
                    "</details>",
                    "",
                ]
            )
        lines.extend(["</details>", ""])

    return "\n".join(lines).rstrip() + "\n"


with mkdocs_gen_files.open("glossary.md", "w") as glossary_file:
    glossary_file.write(_build_glossary_page())
