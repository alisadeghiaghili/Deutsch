#!/usr/bin/env python3
"""Apply safe, mechanical corpus repairs.

Only rewrites patterns that are unambiguous production defects:
  - Persian cells ending with Latin den/ten/en → کردن / دادن / گفتن / بودن / افتادن / ایستادن
  - Regular (sep) labels on clearly irregular Präteritum forms → Irregular (sep)
  - Known bad German strings (das Fußball, Dasitz, geve, Beispil, …)
  - Vocabulary emoji forced to match Gender column when Gender is explicit

Usage:
  python tools/fix_corpus.py [--root PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Persian stem + latin ending → full Persian
SUFFIX_MAP = [
    (re.compile(r"([؀-ۿ]{1,6})den\b"), r"\1دن"),
    (re.compile(r"([؀-ۿ]{1,6})ten\b"), r"\1تن"),
    (re.compile(r"([؀-ۿ]{1,6})en\b"), r"\1ن"),
]

# After den→دن, some already-partial stems: کردن is کر+دن. Good.
# Arabic yeh variants in source: کرden uses Persian ک and ر.

IRREG_SEP = re.compile(
    r"\| Regular \(sep\) \|([^\n]*)\| (kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog|brach|sprach)",
    re.I,
)

KNOWN_REPLACEMENTS = [
    (r"\bdas Fußball\b", "der Fußball"),
    (r"\*\*Dasitz, bitte\.\*\*", "**Die Rechnung, bitte.**"),
    (r"\bDasitz, bitte\.", "Die Rechnung, bitte."),
    (r"\| Beispil \|", "| Beispiel |"),
    (r"Ich geve ", "Ich gebe "),
    (r"\bdie Aquarell\b", "das Aquarell"),
    (r"\| die Fieber\t", "| das Fieber\t"),  # TSV lemma field
    (r"\| die Reisepass\t", "| der Reisepass\t"),
    (r"\| die Zoll\t", "| der Zoll\t"),
    (r"\| das Lebenslauf\t", "| der Lebenslauf\t"),
    (r"\| das Semester\t", "| das Semester\t"),
]


def fix_persian_suffixes(text: str) -> str:
    out = text
    for pat, rep in SUFFIX_MAP:
        out = pat.sub(rep, out)
    # normalize Arabic Yeh in کرden path leftovers: already handled by unicode
    out = out.replace("كرden", "کردن").replace("كرden", "کردن")
    out = out.replace("كرden", "کردن")
    # Arabic kaf + reh + den
    out = out.replace("كَرden", "کردن")
    out = re.sub(r"كرden", "کردن", out)
    out = re.sub(r"([كک])رden", r"\1ردن", out)
    return out


def fix_regular_sep(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return m.group(0).replace("Regular (sep)", "Irregular (sep)", 1)

    # only when Präteritum in same row contains irregular stem — handled by regex capture
    return re.sub(
        r"\| Regular \(sep\) \|[^\n]*?\| (?:kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog) [a-zäöüß]+",
        lambda m: m.group(0).replace("Regular (sep)", "Irregular (sep)", 1),
        text,
        flags=re.I,
    )


def fix_known(text: str) -> str:
    for pat, rep in KNOWN_REPLACEMENTS:
        text = re.sub(pat, rep, text)
    return text


def fix_emoji_by_gender(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        if not line.lstrip().startswith("|"):
            out.append(line)
            continue
        parts = line.strip().strip("|").split("|")
        if len(parts) < 5:
            out.append(line)
            continue
        gender = ""
        for p in parts[1:4]:
            pl = p.strip().lower()
            if pl in {"maskulin", "feminin", "neutral", "neutrum", "plural"}:
                gender = pl
                break
        if not gender:
            out.append(line)
            continue
        want = {
            "maskulin": "🔵",
            "feminin": "🔴",
            "neutral": "🟢",
            "neutrum": "🟢",
            "plural": "🟡",
        }[gender]
        # replace leading emoji in first cell
        first = parts[0]
        first_new = first
        for e in ("🔵", "🔴", "🟢", "🟡"):
            if first_new.startswith(e) or first_new.startswith(e + " "):
                first_new = want + first_new[len(e) :]
                break
        else:
            # no emoji — leave (do not invent)
            out.append(line)
            continue
        if first_new != first:
            parts[0] = first_new
            new_line = "| " + " | ".join(parts) + " |"
            if line.endswith("\n"):
                new_line += "\n"
            out.append(new_line)
        else:
            out.append(line)
    return "".join(out)


def process_file(path: Path, dry: bool) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    orig = text
    text = fix_persian_suffixes(text)
    text = fix_regular_sep(text)
    text = fix_known(text)
    if path.name == "words.md" and "vocabulary" in path.parts:
        text = fix_emoji_by_gender(text)
    if text != orig:
        if not dry:
            path.write_text(text, encoding="utf-8", newline="\n")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    changed = 0
    for path in sorted(root.rglob("*")):
        if path.suffix not in {".md", ".tsv"}:
            continue
        if any(part in {".git", "node_modules", "legacy", "tools", "docs"} for part in path.parts):
            continue
        changed += process_file(path, args.dry_run)
    print(f"{'Would change' if args.dry_run else 'Changed'} {changed} files under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
