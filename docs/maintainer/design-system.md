# FabricOps visual identity

Canonical source: [`design/brand.json`](../../design/brand.json). This file is the reference for website colours, documentation illustrations, engineering diagrams, governance diagrams, and future visual artifacts. The MkDocs CSS token sheet is generated using `python scripts/sync_brand_tokens.py`; use `--check` in validation.

## Brand direction

A quiet white base with a **blue → purple** gradient for high-level brand surfaces. Keep the actual information solid and readable. Engineering is blue; Governance is purple. Green is reserved for confirmed success, amber for warning and red for errors. Avoid teal as the brand accent.

Use Segoe UI with Arial fallback throughout the website and diagrams. Use Cascadia Code / Consolas for function signatures, field names and API snippets. Apply one restrained radius scale, consistent alignment and generous whitespace.

Do not invent a company logo. The name FabricOps Starter Kit is a text wordmark only unless a real approved logo is provided. Illustrations and SVGs must not invent icons presented as official logos.

## SVG rules

Use the repository skill at `.agents/skills/fabricops-visual-design/SKILL.md` and the external [Diagram Design skill](https://github.com/cathrynlavery/diagram-design). Start from actual code and the glossary, select the correct visual grammar, and keep each diagram focused. SVGs should be editable source, not raster images embedded in SVG wrappers. Distinguish published/Preview features. Prefer diagrams that teach by example rather than giant lists of cards.

A diagram's heading is usually the surrounding page section; don't repeat a large headline inside every SVG unless it adds context in standalone viewing.

## Existing styles

`docs/stylesheets/fabric-theme.css` is the website theme owner. Its colours must reference the generated `--fabricops-*` variables rather than a competing hardcoded palette. For module widgets, keep semantic Engineering-blue and Governance-purple tokens and their native Fabric UI geometry. Do not retroactively recolour historical versioned media.
