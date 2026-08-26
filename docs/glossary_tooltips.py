"""Expose canonical glossary short definitions as site-wide MkDocs tooltips."""

from __future__ import annotations

from scripts.generate_glossary_page import DISPLAY_NAMES, load_glossary_entries


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


def build_glossary_tooltip_markdown() -> str:
    """Return Python-Markdown abbreviation definitions from canonical glossary data."""
    return "\n".join(
        f"*[{label}]: {definition}" for label, definition in glossary_tooltip_definitions().items()
    )


def on_page_markdown(markdown: str, **_kwargs) -> str:
    """Append canonical glossary abbreviations to every rendered documentation page."""
    tooltip_markdown = build_glossary_tooltip_markdown()
    return f"{markdown.rstrip()}\n\n{tooltip_markdown}\n"
