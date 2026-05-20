#!/usr/bin/env python3
"""
gitart.py — TAXOIN Contribution Graph Pixel Art

Creates backdated commits that spell "TAXOIN" in the GitLab/GitHub
contribution calendar heatmap.

Usage:
  # Preview only (no commits created):
  python scripts/gitart.py --preview

  # Create art and push to remote:
  python scripts/gitart.py \\
      --remote https://gitlab.com/YOURUSER/taxoin-art.git \\
      --email  your@email.com \\
      --name   "Your Name"

  # Use Monday as week start (for GitLab EU locales):
  python scripts/gitart.py --remote ... --email ... --dow 1

Requirements:
  - The --email must match a VERIFIED email on your GitLab/GitHub account
  - The target repo must be created on the server BEFORE running this script
  - Push the commits to the DEFAULT branch (main/master) for them to count
"""
from __future__ import annotations

import argparse
import datetime
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


# ── Pixel font 5×7 ───────────────────────────────────────────────────────────
# 7 rows (= days of week in contribution graph) × 5 cols (= weeks per letter)
# 1 = commit on that cell, 0 = no commit

FONT: dict[str, list[list[int]]] = {
    "T": [
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
    ],
    "A": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
    ],
    "X": [
        [1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1],
    ],
    "O": [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    "I": [
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1],
    ],
    "N": [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1],
        [1, 0, 0, 1, 1],
        [1, 0, 0, 0, 1],
    ],
}

WORD = "TAXOIN"
LETTER_WIDTH = 5
LETTER_GAP = 1     # empty columns between letters
PADDING_LEFT = 4   # empty weeks before first letter


# ── Grid builder ─────────────────────────────────────────────────────────────

def build_lit_cells(
    word: str = WORD,
    padding: int = PADDING_LEFT,
    gap: int = LETTER_GAP,
) -> list[tuple[int, int]]:
    """Return list of (week_offset, day_of_week) for all lit pixels."""
    cells: list[tuple[int, int]] = []
    col = padding
    for char in word:
        letter = FONT[char]
        for row in range(7):
            for lc in range(LETTER_WIDTH):
                if letter[row][lc]:
                    cells.append((col + lc, row))
        col += LETTER_WIDTH + gap
    return cells


def find_graph_start(today: datetime.date, dow: int = 0) -> datetime.date:
    """Find the first day of the leftmost visible week in the contribution graph.

    Args:
        today: Today's date
        dow:   First day of week — 0=Sunday (GitHub default), 1=Monday (EU GitLab)
    """
    start = today - datetime.timedelta(weeks=52)
    if dow == 0:  # align to Sunday
        # weekday(): Mon=0 … Sun=6
        sunday_offset = (start.weekday() + 1) % 7
        return start - datetime.timedelta(days=sunday_offset)
    else:          # align to Monday
        return start - datetime.timedelta(days=start.weekday())


def cells_to_dates(
    cells: list[tuple[int, int]],
    graph_start: datetime.date,
    intensity: int = 4,
) -> list[datetime.date]:
    """Convert (week, day) cells to concrete dates, repeated `intensity` times."""
    dates: list[datetime.date] = []
    for week, day in cells:
        date = graph_start + datetime.timedelta(weeks=week, days=day)
        for _ in range(intensity):
            dates.append(date)
    dates.sort()
    return dates


# ── ASCII preview ─────────────────────────────────────────────────────────────

def print_preview(word: str = WORD) -> None:
    cells = set(build_lit_cells(word))
    if not cells:
        return
    max_col = max(c for c, _ in cells)
    print(f"\n  Pixel art preview — '{word}'  ({max_col + 1} weeks wide)\n")
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for row in range(7):
        line = f"  {day_labels[row]}  "
        for col in range(max_col + 2):
            line += "█" if (col, row) in cells else "░"
        print(line)
    print()


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(*args: str, cwd: str, env: dict | None = None) -> str:
    full_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=full_env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed:\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


# ── Main logic ────────────────────────────────────────────────────────────────

def create_art(
    remote_url: str,
    email: str,
    author_name: str,
    dates: list[datetime.date],
    work_dir: str,
    branch: str = "main",
) -> None:
    print(f"\n  Initialising repo in {work_dir}")
    git("init", "-b", branch, cwd=work_dir)
    git("config", "user.email", email, cwd=work_dir)
    git("config", "user.name", author_name, cwd=work_dir)
    git("remote", "add", "origin", remote_url, cwd=work_dir)

    art_file = Path(work_dir) / "art.txt"
    total = len(dates)

    for i, date in enumerate(dates):
        date_str = date.strftime("%Y-%m-%dT12:00:00 +0000")
        art_file.write_text(f"TAXOIN pixel commit #{i + 1}\n{date}\n")
        git("add", "art.txt", cwd=work_dir)
        git(
            "commit", "-m", f"TAXOIN #{i + 1}",
            cwd=work_dir,
            env={
                "GIT_AUTHOR_DATE":     date_str,
                "GIT_COMMITTER_DATE":  date_str,
                "GIT_AUTHOR_NAME":     author_name,
                "GIT_AUTHOR_EMAIL":    email,
                "GIT_COMMITTER_NAME":  author_name,
                "GIT_COMMITTER_EMAIL": email,
            },
        )
        if (i + 1) % 20 == 0 or i + 1 == total:
            pct = (i + 1) / total * 100
            print(f"  [{i + 1:>4}/{total}] {date}  ({pct:.0f}%)")

    print(f"\n  Pushing to {remote_url} ...")
    git("push", "-u", "origin", branch, "--force", cwd=work_dir)
    print("  Done! ✓  Check your profile contribution graph.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TAXOIN contribution graph pixel art generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--remote",   help="Git remote URL (already created on server)")
    parser.add_argument("--email",    help="Author email — must match your GitLab/GitHub account")
    parser.add_argument("--name",     default="TAXOIN", help="Author display name")
    parser.add_argument("--branch",   default="main",   help="Default branch name")
    parser.add_argument("--intensity", type=int, default=4,
                        help="Commits per lit pixel: 1=light, 4=dark (default 4)")
    parser.add_argument("--dow",       type=int, default=0, choices=[0, 1],
                        help="Week start day: 0=Sunday (GitHub), 1=Monday (EU GitLab)")
    parser.add_argument("--dir",       default=None,
                        help="Work directory path (default: auto temp dir, deleted after push)")
    parser.add_argument("--preview",   action="store_true",
                        help="Print ASCII preview and exit — no commits created")
    args = parser.parse_args()

    print_preview()

    if args.preview:
        return

    if not args.remote or not args.email:
        parser.error("--remote and --email are required (or use --preview)")

    today = datetime.date.today()
    graph_start = find_graph_start(today, dow=args.dow)
    cells = build_lit_cells()
    dates = cells_to_dates(cells, graph_start, intensity=args.intensity)

    print(f"  Today:         {today}")
    print(f"  Graph start:   {graph_start}  (dow={'Sun' if args.dow == 0 else 'Mon'})")
    print(f"  Art date range:{dates[0]}  →  {dates[-1]}")
    print(f"  Total commits: {len(dates)}  (intensity={args.intensity})")
    print(f"  Email:         {args.email}")

    cleanup = args.dir is None
    work_dir = args.dir or tempfile.mkdtemp(prefix="taxoin-art-")

    try:
        create_art(
            remote_url=args.remote,
            email=args.email,
            author_name=args.name,
            dates=dates,
            work_dir=work_dir,
            branch=args.branch,
        )
    finally:
        if cleanup and Path(work_dir).exists():
            shutil.rmtree(work_dir)
            print(f"  Temp dir cleaned up.")


if __name__ == "__main__":
    main()
