#!/usr/bin/env python3
"""Render a source-pinned video from the verified R factor-score receipt."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "demo"
RECEIPT = ROOT / "research-output" / "factor-score-receipt.csv"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def fftext(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def draw(text: str, x: int, y: int, size: int, color: str = "white", bold: bool = False) -> str:
    font = FONT_BOLD if bold else FONT
    return (
        f"drawtext=fontfile={font}:text='{fftext(text)}':x={x}:y={y}:"
        f"fontsize={size}:fontcolor={color}"
    )


def scene(path: Path, filters: list[str], duration: float) -> None:
    run(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", f"color=c=#09111f:s=1280x720:d={duration}:r=25",
        "-vf", ",".join(filters),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
    )


def main() -> None:
    if not RECEIPT.exists():
        raise SystemExit("Run Rscript verified_factor_scores.R first")
    for command in ("ffmpeg", "git"):
        if shutil.which(command) is None:
            raise SystemExit(f"Missing required command: {command}")

    with RECEIPT.open(newline="", encoding="utf-8") as handle:
        values = {row["key"]: row["value"] for row in csv.DictReader(handle)}

    source_sha = os.environ.get("DEMO_SOURCE_SHA") or subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    run("git", "merge-base", "--is-ancestor", source_sha, "HEAD")

    OUT.mkdir(parents=True, exist_ok=True)
    work = OUT / ".render"
    work.mkdir(exist_ok=True)
    scenes: list[Path] = []

    common = [
        "drawbox=x=0:y=0:w=1280:h=12:color=#5eead4:t=fill",
        draw("ADVANCED ECONOMETRICS I", 72, 52, 24, "#5eead4", True),
        draw("Verified historical-data workflow", 72, 648, 20, "#94a3b8"),
        draw("No causal, forecasting, or performance claim", 764, 648, 18, "#64748b"),
    ]

    p = work / "01.mp4"
    scene(p, common + [
        draw("One-factor queue model", 72, 148, 58, "white", True),
        draw("Posterior scoring, not a raw average", 72, 224, 34, "#cbd5e1"),
        "drawbox=x=72:y=330:w=340:h=156:color=#13243b:t=fill",
        draw(values["rows"], 105, 354, 62, "#5eead4", True),
        draw("complete observations", 105, 426, 23, "#cbd5e1"),
        "drawbox=x=444:y=330:w=340:h=156:color=#13243b:t=fill",
        draw("5", 477, 354, 62, "#60a5fa", True),
        draw("ride measurements", 477, 426, 23, "#cbd5e1"),
        "drawbox=x=816:y=330:w=340:h=156:color=#13243b:t=fill",
        draw("0", 849, 354, 62, "#a78bfa", True),
        draw("optimizer exit code", 849, 426, 23, "#cbd5e1"),
    ], 3.7)
    scenes.append(p)

    p = work / "02.mp4"
    filters = common + [
        draw("Canonicalized factor loadings", 72, 116, 42, "white", True),
        draw("Sign-normalized for reproducible receipts", 72, 170, 24, "#94a3b8"),
    ]
    rides = ["PeterPan", "SpaceMtn", "HauntedMansion", "SplashMtn", "WinniePooh"]
    labels = ["Peter Pan", "Space Mountain", "Haunted Mansion", "Splash Mountain", "Winnie the Pooh"]
    colors = ["#5eead4", "#60a5fa", "#a78bfa", "#38bdf8", "#34d399"]
    max_loading = max(float(values[f"loading_{ride}"]) for ride in rides)
    for index, (ride, label, color) in enumerate(zip(rides, labels, colors)):
        y = 248 + index * 68
        loading = float(values[f"loading_{ride}"])
        width = int(520 * loading / max_loading)
        filters.extend([
            draw(label, 72, y - 4, 21, "#dbeafe"),
            f"drawbox=x=315:y={y}:w={width}:h=26:color={color}:t=fill",
            draw(f"{loading:.2f}", 860, y - 4, 22, "white", True),
        ])
    scene(p, filters, 4.2)
    scenes.append(p)

    p = work / "03.mp4"
    filters = common + [
        draw("Highest posterior crowding score", 72, 110, 42, "white", True),
        draw(f"{values['top_date']} at {int(float(values['top_hour'])):02d}:00", 72, 164, 30, "#5eead4", True),
    ]
    waits = [float(values[f"wait_{ride}"]) for ride in rides]
    max_wait = max(waits)
    for index, (label, wait, color) in enumerate(zip(labels, waits, colors)):
        y = 238 + index * 68
        width = int(600 * wait / max_wait)
        filters.extend([
            draw(label, 72, y - 4, 21, "#dbeafe"),
            f"drawbox=x=315:y={y}:w={width}:h=26:color={color}:t=fill",
            draw(f"{wait:.0f} min", 950, y - 4, 22, "white", True),
        ])
    scene(p, filters, 4.2)
    scenes.append(p)

    p = work / "04.mp4"
    scene(p, common + [
        draw("Method correction", 72, 110, 42, "white", True),
        "drawbox=x=72:y=210:w=510:h=220:color=#13243b:t=fill",
        draw("Posterior score", 108, 245, 25, "#5eead4", True),
        draw(values["posterior_score"], 108, 292, 54, "white", True),
        draw("Uses fitted specific variances", 108, 366, 20, "#94a3b8"),
        "drawbox=x=614:y=210:w=510:h=220:color=#13243b:t=fill",
        draw("Archived shortcut", 650, 245, 25, "#fb7185", True),
        draw(values["naive_score"], 650, 292, 54, "white", True),
        draw("Unweighted standardized average", 650, 366, 20, "#94a3b8"),
        draw("Same top row here; corrected scores follow the fitted covariance.", 72, 488, 26, "#dbeafe"),
        draw("Regression checks: exact one-off match • finite scores • pinned timestamp", 72, 536, 21, "#94a3b8"),
    ], 4.2)
    scenes.append(p)

    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{path.name}'\n" for path in scenes), encoding="utf-8")
    mp4 = OUT / "factor-score-demo.mp4"
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(mp4))
    gif = OUT / "factor-score-demo.gif"
    run(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4),
        "-vf", "fps=10,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
        "-loop", "0", str(gif),
    )
    poster = OUT / "factor-score-poster.png"
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "8", "-i", str(mp4), "-frames:v", "1", str(poster))

    runtime_paths = [
        "standby.RData", "verified_factor_scores.R", "scripts/render_factor_demo.py",
        ".github/workflows/coursework.yml",
    ]
    manifest = {
        "scope": "Committed historical queue data; one-factor statistical reproduction only",
        "source_commit": source_sha,
        "source_blobs": {
            path: subprocess.check_output(["git", "rev-parse", f"{source_sha}:{path}"], cwd=ROOT, text=True).strip()
            for path in runtime_paths
        },
        "receipt": dict(values),
        "artifacts": {},
    }
    for path in (mp4, gif, poster):
        manifest["artifacts"][path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    (OUT / "capture.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    shutil.rmtree(work)
    print(f"Rendered {mp4.name}, {gif.name}, and {poster.name} from {source_sha}")


if __name__ == "__main__":
    main()
