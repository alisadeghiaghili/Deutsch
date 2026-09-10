#!/usr/bin/env python3
"""Split inline listening answers out of drill files into Lösungen companions.

For each *hoerverstehen*.md under A1–B2 listening/:
  - rewrite `N. question → answer` lines as `N. question`
  - collect answers into `hoerverstehen-*-loesungen.md`
  - add a check-first banner if the drill file has exercises

Usage:
  python tools/split_listening_answers.py [--root PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# "1. text → answer" or "1. text → answer"
Q_ARROW = re.compile(r"^(\s*)(\d+\.\s+)(.+?)\s*→\s*(.+?)\s*$")


def process_file(path: Path, dry: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out_lines: list[str] = []
    answers: list[str] = []
    changed = False
    exercise_no = 0

    for line in lines:
        m = Q_ARROW.match(line)
        if m:
            indent, num, question, answer = m.groups()
            exercise_no += 1
            out_lines.append(f"{indent}{num}{question}")
            answers.append(f"{num.strip()} **{question.strip()}** → {answer.strip()}")
            changed = True
            continue
        out_lines.append(line)

    if not changed:
        return False

    level = path.parent.parent.name  # A1/A2/...
    stem = path.stem  # e.g. hoerverstehen-a2
    sol_name = f"{stem}-loesungen.md"
    sol_path = path.parent / sol_name

    header = [
        f"# Lösungen — {stem.replace('-', ' ').title()}",
        "",
        f"Answer key for [`{path.name}`]({path.name}).",
        "Listen and answer **twice** before opening this file.",
        "",
        "پاسخ‌نامه: فقط بعد از دو بار گوش دادن و پاسخ نوشتن، این فایل را باز کنید.",
        "",
        "---",
        "",
        "## Answers / پاسخ‌ها",
        "",
    ]
    body = "\n".join(answers) + "\n"
    sol_content = "\n".join(header) + body

    # Banner in drill file after H1
    banner = [
        "",
        "> **Drill mode:** questions only. Answer key: "
        f"[`{sol_name}`]({sol_name}) — open only after you answered on paper.",
        "",
        "> **حالت تمرین:** فقط سؤال‌ها. پاسخ‌نامه در "
        f"[`{sol_name}`]({sol_name}) — پس از پاسخ‌نگاری باز کنید.",
        "",
    ]
    # insert after first heading line
    inserted = False
    final: list[str] = []
    for line in out_lines:
        final.append(line)
        if not inserted and line.startswith("#"):
            final.extend(banner)
            inserted = True

    if not dry:
        path.write_text("\n".join(final) + "\n", encoding="utf-8", newline="\n")
        sol_path.write_text(sol_content, encoding="utf-8", newline="\n")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    n = 0
    for level in ("A1", "A2", "B1", "B2"):
        folder = root / level / "listening"
        if not folder.is_dir():
            continue
        for md in folder.glob("hoerverstehen*.md"):
            if md.name.endswith("-loesungen.md"):
                continue
            if process_file(md, args.dry_run):
                n += 1
                print(f"{'would split' if args.dry_run else 'split'}: {md}")
    print(f"files: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
