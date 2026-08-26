"""Expose canonical glossary short definitions as site-wide MkDocs tooltips."""

from __future__ import annotations

import re

from scripts.generate_glossary_page import DISPLAY_NAMES, load_glossary_entries

GLOSSARY_LINK_PATTERN = re.compile(
    r"\[(?P<label>[^\]]+)\]\((?:\.\./)*glossary\.md#(?P<entry_id>[a-z0-9-]+)\)"
)
GLOSSARY_DEFINITION_LINE_PATTERN = re.compile(
    r"(?m)^(?P<indent>[ \t]*)"
    r"\[(?P<label>[^\]]+)\]\((?:\.\./)*glossary\.md#(?P<entry_id>[a-z0-9-]+)\)"
    r"[ \t]+—[ \t]+.*?(?P<trailing>[ \t]{2})?$"
)


def _valid_glossary_ids() -> set[str]:
    return {str(entry["id"]) for entry in load_glossary_entries()}


def glossary_tooltip_definitions() -> dict[str, str]:
    """Return display labels mapped to canonical glossary short definitions."""
    definitions: dict[str, str] = {}
    for entry in load_glossary_entries():
        entry_id = str(entry["id"])
        term = str(entry["term"])
        short_definition = str(entry["short_definition"])
        labels = [term, DISPLAY_NAMES.get(entry_id, term)]
        for alias in entry.get("aliases", []):
            label = str(alias)
            labels.append(label)
            if label == label.lower():
                labels.append(label.title())

        for label in dict.fromkeys(labels):
            existing = definitions.get(label)
            if existing is not None and existing != short_definition:
                raise RuntimeError(f"Glossary tooltip label {label!r} maps to multiple definitions.")
            definitions[label] = short_definition
    return definitions


def resolve_glossary_links(markdown: str) -> str:
    """Render glossary-ID references as plain terms backed by canonical tooltips."""
    valid_ids = _valid_glossary_ids()

    def validate(entry_id: str) -> None:
        if entry_id not in valid_ids:
            raise RuntimeError(f"Unknown glossary id referenced by documentation: {entry_id}")

    def replace_definition_line(match: re.Match[str]) -> str:
        validate(match.group("entry_id"))
        trailing = match.group("trailing") or ""
        return f"{match.group('indent')}{match.group('label')}{trailing}"

    def replace_link(match: re.Match[str]) -> str:
        validate(match.group("entry_id"))
        return match.group("label")

    rendered = GLOSSARY_DEFINITION_LINE_PATTERN.sub(replace_definition_line, markdown)
    return GLOSSARY_LINK_PATTERN.sub(replace_link, rendered)


def build_glossary_tooltip_markdown() -> str:
    """Return Python-Markdown abbreviation definitions from canonical glossary data."""
    return "\n".join(
        f"*[{label}]: {definition}" for label, definition in glossary_tooltip_definitions().items()
    )


def on_page_markdown(markdown: str, **_kwargs) -> str:
    """Resolve glossary references and append canonical tooltip definitions."""
    rendered = resolve_glossary_links(markdown)
    tooltip_markdown = build_glossary_tooltip_markdown()
    return f"{rendered.rstrip()}\n\n{tooltip_markdown}\n"
