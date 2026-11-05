#!/usr/bin/env python3
"""Generate or check the canonical FabricOps website colour and typography tokens."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "design" / "brand.json"
TARGET = ROOT / "docs" / "stylesheets" / "brand-tokens.css"


def render(tokens: dict) -> str:
    lines = ["/* Generated from design/brand.json by scripts/sync_brand_tokens.py. Do not edit by hand. */", ":root {"]
    for name, value in tokens["palette"].items():
        lines.append(f'  --fabricops-{name.replace("_", "-")}: {value};')
    gradient = tokens["gradient"]
    lines.append(f'  --fabricops-brand-gradient: linear-gradient({gradient["angle"]}, {gradient["start"]}, {gradient["end"]});')
    lines.append('  --fabricops-font-ui: "Segoe UI", Arial, sans-serif;')
    lines.append('  --fabricops-font-code: "Cascadia Code", Consolas, monospace;')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when committed CSS differs from source tokens")
    args = parser.parse_args()
    expected = render(json.loads(SOURCE.read_text(encoding="utf-8")))
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != expected:
            parser.error("brand-tokens.css is stale; run python scripts/sync_brand_tokens.py")
        print("Brand tokens verified.")
    else:
        TARGET.write_text(expected, encoding="utf-8")
        print(f"Updated {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
