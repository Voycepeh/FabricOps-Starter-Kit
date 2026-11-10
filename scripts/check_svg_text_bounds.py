#!/usr/bin/env python3
"""Conservative SVG text-container overflow guard for FabricOps diagrams.

This is a lightweight static preflight; browser render inspection is still required.
Checks the nearest enclosing SVG rect when a text anchor lies within a panel.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from xml.etree import ElementTree as ET


def estimate_width(label: str, font_size: float) -> float:
    """Conservative advance-width estimate for Segoe UI / sans and API labels."""
    def advance(c: str) -> float:
        if c == " ":
            return 0.32
        if c in "MW@":
            return 0.92
        if c in "il1.,():":
            return 0.34
        return 0.63

    return sum(advance(c) for c in label) * font_size


def attr(node: ET.Element, name: str, default: str = "0") -> float:
    """Read a numeric SVG attribute with a fallback value."""
    return float(node.attrib.get(name, default))


def inspect(path: Path) -> list[str]:
    """Inspect SVG text positions and return potential bounds violations."""
    root = ET.parse(path).getroot()
    if not root.tag.endswith("svg"):
        return [f"{path}: expected SVG root"]
    boxes = []
    texts = []
    for node in root.iter():
        name = node.tag.rsplit("}", 1)[-1]
        if name == "rect":
            boxes.append((attr(node, "x"), attr(node, "y"), attr(node, "width"), attr(node, "height")))
        elif name == "text" and node.text and node.text.strip():
            texts.append(node)
    problems = []
    for node in texts:
        label = "".join(node.itertext()).strip()
        x, y, size = attr(node, "x"), attr(node, "y"), attr(node, "font-size", "16")
        anchor = node.attrib.get("text-anchor", "start")
        width = estimate_width(label, size)
        left = x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x
        right = left + width
        candidates = sorted(
            (b for b in boxes
             if b[0] <= x <= b[0] + b[2]
             and b[1] + size * 0.5 <= y <= b[1] + b[3] + size * 0.2),
            key=lambda b: b[2] * b[3],
        )
        if candidates:
            bx, by, bw, bh = candidates[0]
            if left < bx + 8 or right > bx + bw - 8:
                problems.append(f"{path}: text {label!r} at x={x:g} may overflow "
                                f"panel [{bx:g}, {bx+bw:g}] (estimated [{left:.1f}, {right:.1f}])")
    return problems


def main() -> None:
    """Run the SVG text bounds validation command."""
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths or sorted(Path("docs/assets/engineering").glob("*.svg"))
    errors = []
    for path in paths:
        errors += inspect(path)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"SVG text preflight passed for {len(paths)} file(s). Browser visual review is still required.")


if __name__ == "__main__":
    main()
