from pathlib import Path
import re
import runpy

GENERATOR = Path("scripts/generate_individual_function_reference_pages.py")
INDEX = Path("docs/reference/metadata.md")

text = GENERATOR.read_text(encoding="utf-8")

overview_pattern = r"def parse_metadata_reference_overview\(\) -> list\[str\]:\n.*?\n\n\ndef parse_metadata_reference_contract"
overview_replacement = '''def parse_metadata_reference_overview() -> list[str]:
    """Parse the concise Metadata Table Overview content."""
    namespace = runpy.run_path(str(DOCS_METADATA_PATH))
    intro = str(namespace.get("METADATA_REFERENCE_OVERVIEW_INTRO", "")).strip()
    caption = str(namespace.get("METADATA_REFERENCE_MODEL_DIAGRAM_CAPTION", "")).strip()
    diagram = str(namespace.get("METADATA_REFERENCE_MODEL_DIAGRAM", "")).strip()
    if not intro or not caption or not diagram:
        raise RuntimeError("Metadata reference overview content must include intro, caption, and diagram")
    return [intro, "", caption, "", diagram]


def parse_metadata_reference_contract'''
text, count = re.subn(overview_pattern, overview_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"Expected one metadata overview parser block, found {count}")

helper_marker = "def _metadata_column_counts(\n"
helpers = r'''def _metadata_index_key_html(fields: list[str]) -> str:
    """Return compact HTML for a metadata card primary key."""
    if not fields:
        return "Not defined in the current implementation."
    return ' <span class="metadata-table-card__key-separator">+</span> '.join(
        f"<code>{html_escape(field)}</code>" for field in fields
    )


def _metadata_index_relationships(
    table_name: str,
    table_models: dict[str, dict[str, Any]],
) -> list[tuple[str, str, str]]:
    """Return exact parent-to-child field relationships for one metadata table card."""
    relationships: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for child_table, child_model in table_models.items():
        for foreign_key in child_model.get("foreign_keys", []):
            if child_table == table_name:
                relationship = (
                    f"{foreign_key['referenced_table']}.{foreign_key['referenced_field']}",
                    "1 → N",
                    f"{table_name}.{foreign_key['local_field']}",
                )
            elif foreign_key["referenced_table"] == table_name:
                relationship = (
                    f"{table_name}.{foreign_key['referenced_field']}",
                    "1 → N",
                    f"{child_table}.{foreign_key['local_field']}",
                )
            else:
                continue
            if relationship not in seen:
                seen.add(relationship)
                relationships.append(relationship)
    return relationships


def render_metadata_reference_index(
    table_models: dict[str, dict[str, Any]],
    reference_order: list[str],
    table_purposes: dict[str, str],
) -> str:
    """Render the compact, clickable metadata model landing page."""
    lines = [
        "# List of Metadata Tables",
        "",
        *parse_metadata_reference_overview(),
        "",
        "## Metadata tables",
        "",
        "<style>",
        ".metadata-table-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin: 1.25rem 0 2rem; }",
        ".metadata-table-card { display: flex; flex-direction: column; gap: .55rem; padding: 1rem 1.1rem; border: 1px solid rgba(0, 150, 136, .24); border-radius: .7rem; background: rgba(0, 150, 136, .055); color: inherit !important; text-decoration: none !important; box-shadow: 0 1px 2px rgba(0, 0, 0, .04); transition: border-color .15s ease, background .15s ease, transform .15s ease; }",
        ".metadata-table-card:hover { border-color: rgba(0, 150, 136, .48); background: rgba(0, 150, 136, .085); transform: translateY(-1px); }",
        ".metadata-table-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; }",
        ".metadata-table-card__title { font-family: var(--md-code-font-family); font-size: .82rem; font-weight: 700; color: var(--md-primary-fg-color); overflow-wrap: anywhere; }",
        ".metadata-table-card__arrow { flex: 0 0 auto; font-size: 1rem; color: var(--md-primary-fg-color); }",
        ".metadata-table-card__purpose { line-height: 1.45; }",
        ".metadata-table-card__meta { display: grid; grid-template-columns: 6.4rem minmax(0, 1fr); gap: .5rem; align-items: start; font-size: .84rem; line-height: 1.4; }",
        ".metadata-table-card__meta strong, .metadata-table-card__relationships-label { color: var(--md-default-fg-color--light); font-size: .74rem; letter-spacing: .02em; text-transform: uppercase; }",
        ".metadata-table-card__relationships { display: flex; flex-direction: column; gap: .35rem; padding-top: .15rem; }",
        ".metadata-table-card__relationship { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; font-size: .76rem; line-height: 1.35; }",
        ".metadata-table-card__relationship code { font-size: .72rem; overflow-wrap: anywhere; }",
        ".metadata-table-card__cardinality { font-weight: 700; color: var(--md-primary-fg-color); white-space: nowrap; }",
        ".metadata-table-card__empty { font-size: .8rem; color: var(--md-default-fg-color--light); }",
        "@media (max-width: 720px) { .metadata-table-grid { grid-template-columns: 1fr; gap: .8rem; } .metadata-table-card { padding: .9rem 1rem; } .metadata-table-card__meta { grid-template-columns: 5.6rem minmax(0, 1fr); } }",
        "</style>",
        "",
        '<div class="metadata-table-grid">',
    ]
    for table_name in reference_order:
        slug = table_name.lower()
        model = table_models[table_name]
        purpose = _metadata_table_purpose(table_name, table_purposes)
        relationships = _metadata_index_relationships(table_name, table_models)
        lines.extend([
            f'<a class="metadata-table-card" href="metadata/{slug}.md" aria-label="Open {html_escape(table_name)} schema">',
            '  <span class="metadata-table-card__header">',
            f'    <span class="metadata-table-card__title">{html_escape(table_name)}</span>',
            '    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>',
            '  </span>',
            f'  <span class="metadata-table-card__purpose">{html_escape(purpose)}</span>',
            '  <span class="metadata-table-card__meta">',
            '    <strong>Grain</strong>',
            f'    <span>{html_escape(str(model["grain"]))}</span>',
            '  </span>',
            '  <span class="metadata-table-card__meta">',
            '    <strong>Primary key</strong>',
            f'    <span>{_metadata_index_key_html(model["primary_key"])}</span>',
            '  </span>',
            '  <span class="metadata-table-card__relationships">',
            '    <span class="metadata-table-card__relationships-label">Relationships</span>',
        ])
        if relationships:
            for parent, cardinality, child in relationships:
                lines.extend([
                    '    <span class="metadata-table-card__relationship">',
                    f'      <code>{html_escape(parent)}</code>',
                    f'      <span class="metadata-table-card__cardinality">{html_escape(cardinality)}</span>',
                    f'      <code>{html_escape(child)}</code>',
                    '    </span>',
                ])
        else:
            lines.append('    <span class="metadata-table-card__empty">No immediate logical relationship is defined.</span>')
        lines.extend(['  </span>', '</a>'])
    lines.extend(['</div>', ''])
    return "\n".join(lines).rstrip() + "\n"


'''
if helper_marker not in text:
    raise SystemExit("Could not find metadata column-count helper marker")
text = text.replace(helper_marker, helpers + helper_marker, 1)

text, count = re.subn(
    r'\n    index_lines = \[\n        "# List of Metadata Tables",\n        "",\n        \*parse_metadata_reference_overview\(\),\n        "",\n    \]\n',
    '\n',
    text,
    count=1,
)
if count != 1:
    raise SystemExit(f"Expected one metadata index start block, found {count}")

text, count = re.subn(
    r'\n        index_lines\.extend\(\[\n.*?\n        \]\)\n\n        rows = metadata_table_schema_rows',
    '\n        rows = metadata_table_schema_rows',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"Expected one metadata index card block, found {count}")

old_write = '    METADATA_REFERENCE_INDEX_PATH.write_text("\\n".join(index_lines).rstrip() + "\\n", encoding="utf-8")'
new_write = '''    METADATA_REFERENCE_INDEX_PATH.write_text(
        render_metadata_reference_index(table_models, reference_order, table_purposes),
        encoding="utf-8",
    )'''
if old_write not in text:
    raise SystemExit("Could not find metadata index write block")
text = text.replace(old_write, new_write, 1)
GENERATOR.write_text(text, encoding="utf-8")

namespace = runpy.run_path(str(GENERATOR), run_name="metadata_reference_generator")
metadata = runpy.run_path("scripts/reference_docs_metadata.py")
content = namespace["render_metadata_reference_index"](
    metadata["METADATA_TABLE_MODELS"],
    metadata["METADATA_REFERENCE_ORDER"],
    metadata["METADATA_TABLE_PURPOSES"],
)
INDEX.write_text(content, encoding="utf-8")
