"""Deprecated standalone helper for manually maintained notebook assets."""

from __future__ import annotations


def main() -> int:
    """Explain that notebook packs are outside the formal package release."""
    print(
        "Notebook templates are manually maintained living applications and are not "
        "built, frozen, or published as FabricOps package release assets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
