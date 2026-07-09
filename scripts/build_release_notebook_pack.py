"""Build the version-specific Live notebook release pack."""

from __future__ import annotations

import argparse
from pathlib import Path

from release_inventory import build_notebook_pack
from release_inventory import read_package_version


def main() -> int:
    """Build the Live notebook release pack for a version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("version", nargs="?", default=read_package_version())
    parser.add_argument("--output-dir", default="dist")
    args = parser.parse_args()
    path = build_notebook_pack(args.version, Path(args.output_dir))
    print(f"Release notebook pack written: {path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
