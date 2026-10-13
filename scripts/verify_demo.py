#!/usr/bin/env python3
"""Fail closed when source or published demo artifacts drift."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "demo"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    capture = json.loads((OUT / "capture.json").read_text(encoding="utf-8"))
    source = capture["source_commit"]
    subprocess.run(["git", "merge-base", "--is-ancestor", source, "HEAD"], cwd=ROOT, check=True)
    for path, expected in capture["source_blobs"].items():
        actual = subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()
        if actual != expected:
            raise SystemExit(f"Source drift: {path}: {actual} != {expected}")
    for name, expected in capture["artifacts"].items():
        path = OUT / name
        if path.stat().st_size != expected["bytes"] or sha256(path) != expected["sha256"]:
            raise SystemExit(f"Artifact drift: {name}")
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-v", "error", "-i", str(path),
            "-f", "null", "-",
        ], check=True)
    print(f"Verified source {source} and {len(capture['artifacts'])} complete artifacts")


if __name__ == "__main__":
    main()
