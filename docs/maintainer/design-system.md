# FabricOps visual identity

Canonical source: [`design/brand.json`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/design/brand.json). This file is the reference for website colours, documentation illustrations, engineering diagrams, governance diagrams, and future visual artifacts. The MkDocs CSS token sheet is generated using `python scripts/sync_brand_tokens.py`; use `--check` in validation.

## Brand direction

A quiet white base with a **blue → purple** gradient for high-level website brand surfaces only. Diagrams use **neutral black/slate as the default**, with light neutral surfaces. Blue selectively marks Engineering emphasis. Purple appears when Governance is an actual actor, approval or handoff, not as the next colour in an Engineering sequence. Green communicates success or accepted, amber warning, red errors, rejection or blocked work. Do not add decorative colours to normal pipeline stages.

Use Segoe UI with Arial fallback throughout the website and diagrams. Use Cascadia Code / Consolas for function signatures, field names and API snippets. Apply one restrained radius scale, consistent alignment and generous whitespace.

Do not invent a company logo. The name FabricOps Starter Kit is a text wordmark only unless a real approved logo is provided. Illustrations and SVGs must not invent icons presented as official logos.

## SVG rules

Use the repository skill at `.agents/skills/fabricops-visual-design/SKILL.md` and the external [Diagram Design skill](https://github.com/cathrynlavery/diagram-design). Start from actual code and the glossary, select the correct visual grammar, and keep each diagram focused. SVGs should be editable source, not raster images embedded in SVG wrappers. Distinguish published/Preview features. Prefer diagrams that teach by example rather than giant lists of cards.

A diagram's heading is usually the surrounding page section; don't repeat a large headline inside every SVG unless it adds context in standalone viewing.

## Icon and logo workflow

Use [SVG Icon Generator](https://awesomeskill.ai/skill/claude-code-plugins-plus-skills-svg-icon-generator) through `.agents/skills/fabricops-svg-icons/SKILL.md` when creating or editing an icon or a specifically requested logo proposal. The upstream skill is generic guidance; our wrapper defines reusable strokes, sizes, icon semantics, accessibility and QA. An icon must never be introduced as an official FabricOps logo. Logo adoption requires explicit approval. All diagrams still use the separate Diagram Design skill.

## Existing styles

`docs/stylesheets/fabric-theme.css` is the website theme owner. Its colours must reference the generated `--fabricops-*` variables rather than a competing hardcoded palette. For module widgets, keep semantic Engineering-blue and Governance-purple tokens and their native Fabric UI geometry. Do not retroactively recolour historical versioned media.
