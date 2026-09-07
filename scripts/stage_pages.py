#!/usr/bin/env python3
"""Stage the existing static website, including durable Journal Club assets."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stage(destination: Path, root: Path = ROOT) -> int:
    root = root.resolve()
    destination = destination.resolve()
    if destination == root or root in destination.parents or destination in root.parents:
        raise ValueError("Pages staging must be outside the source repository")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Pages staging directory must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    excluded_roots = {".git", ".github", "scripts", "tests", ".pytest_cache"}
    excluded_jc = {"posts", "templates"}
    copied = 0
    for source in root.rglob("*"):
        relative = source.relative_to(root)
        if relative.parts[0] in excluded_roots or "__pycache__" in relative.parts:
            continue
        if relative.parts[:1] == ("journal-club",) and len(relative.parts) > 1 and relative.parts[1] in excluded_jc:
            continue
        if source.is_symlink():
            raise ValueError(f"Unsupported symlink in Pages source: {relative}")
        if not source.is_file() or source.suffix == ".pyc" or source.name == ".gitkeep":
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    (destination / ".nojekyll").touch()
    print(f"Staged {copied} static files, including Journal Club assets, at {destination}")
    return copied


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    stage(parser.parse_args().destination)
