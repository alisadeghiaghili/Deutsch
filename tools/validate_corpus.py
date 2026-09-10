#!/usr/bin/env python3
"""Validate the German study corpus for structural and linguistic red flags.

Checks (blocking by default):
  - encoding corruption characters and mixed-script Persian glosses
  - vocabulary rows: gender emoji vs Gender/Article coherence
  - known-bad infinitives / Präteritum patterns
  - TSV flashcards: header presence, field count, mixed-script Persian
  - listening filenames match folder level
  - internal markdown links that point at missing files under the repo

Usage:
  python tools/validate_corpus.py [--root PATH] [--warn-only]

Exit codes:
  0 = clean (or --warn-only)
  1 = validation errors
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

CORRUPTION = re.compile(r"[断]|[^\x00-\x7F؀-ۿݐ-ݿऀ-ॿ一-鿿]")
# Persian block + common punctuation; Latin 'den/ten/en' glued to Persian is a defect
MIXED_PERSIAN = re.compile(r"[؀-ۿ]+(?:den|ten|en)\b")
# Latin letters that appear *inside* a Persian-looking token after a space-run of Persian
KARDEN = re.compile(r"کرden|دادen|گفten|یافten|شناسen")

GENDER_EMOJI = {
    "🔵": ("Maskulin", "der"),
    "🔴": ("Feminin", "die"),
    "🟢": ("Neutral", "das"),
}

# Heuristics: Class field must not claim regular when Präteritum shows ablaut
IRREG_STEMS = re.compile(
    r"\b(kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog|sprach|schrieb|aß|trank|"
    r"schlief|fuhr|riet|bat|riet|wuchs|schmolz|gefror|erkannte?|lief)\b",
    re.I,
)

KNOWN_BAD_INFINITIVES = {
    "funktionen": "funktionieren",
    "emissionieren": "emittieren",
}

KNOWN_BAD_PRATERITUM = {
    "ernytete": "erntete",
    "camperte": "campete",
    "tadte": "tadelte",
    "gärtner": "gärtnerte (as Präteritum of gärtnern)",
}

# Only flag wrong *lemma article* (start of German cell or TSV field), not correct plurals
# (e.g. plural "die Fieber" of das Fieber is valid).
KNOWN_BAD_GENDER_ROWS = [
    (re.compile(r"^\|\s*die Fieber\b"), "das Fieber"),
    (re.compile(r"\| die Fieber\t"), "das Fieber"),
    (re.compile(r"^\|\s*die Reisepass\b"), "der Reisepass"),
    (re.compile(r"\| die Reisepass\t"), "der Reisepass"),
    (re.compile(r"^\|\s*das Fußball\b"), "der Fußball"),
    (re.compile(r"\| das Fußball\t"), "der Fußball"),
    (re.compile(r"^\|\s*die Zoll\b"), "der Zoll"),
    (re.compile(r"\| die Zoll\t"), "der Zoll"),
    (re.compile(r"^\|\s*das Lebenslauf\b"), "der Lebenslauf"),
    (re.compile(r"\| das Lebenslauf\t"), "der Lebenslauf"),
]


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def err(self, path: Path, line_no: int, msg: str) -> None:
        self.errors.append(f"{path.as_posix()}:{line_no}: {msg}")

    def warn(self, path: Path, line_no: int, msg: str) -> None:
        self.warnings.append(f"{path.as_posix()}:{line_no}: {msg}")


def is_md_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 3


def cells(line: str) -> list[str]:
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def check_text_corruption(path: Path, text: str, report: Report) -> None:
    for i, line in enumerate(text.splitlines(), 1):
        if "断" in line:
            report.err(path, i, "encoding corruption character 断")
        if KARDEN.search(line):
            report.err(path, i, f"mixed-script Persian gloss: {KARDEN.search(line).group(0)!r}")
        # detect Persian + Latin suffix glued: e.g. کرden
        for m in re.finditer(r"[؀-ۿ]{2,}(?:den|ten|en)\b", line):
            report.err(path, i, f"mixed-script Persian suffix: {m.group(0)!r}")


def check_known_bad_german(path: Path, text: str, report: Report) -> None:
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for bad, good in KNOWN_BAD_INFINITIVES.items():
            if re.search(rf"\|\s*{re.escape(bad)}\s*\|", line):
                report.err(path, i, f"invalid infinitive {bad!r} → {good}")
        for bad, good in KNOWN_BAD_PRATERITUM.items():
            if re.search(rf"\|\s*{re.escape(bad)}\s*\|", line) or f" {bad} " in line:
                # only flag inside verb-table-looking rows
                if line.strip().startswith("|") and "Regular" in line or "irr" in low or "reg" in low:
                    report.err(path, i, f"suspicious Präteritum/form {bad!r} → {good}")
        for pat, good in KNOWN_BAD_GENDER_ROWS:
            if pat.search(line):
                report.err(path, i, f"wrong article/gender pattern → {good}")


def check_vocab_gender(path: Path, text: str, report: Report) -> None:
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if not is_md_table_row(line):
            continue
        parts = cells(line)
        if len(parts) < 5:
            continue
        first = parts[0]
        emoji = None
        for e in GENDER_EMOJI:
            if first.startswith(e) or first == e or first.lstrip().startswith(e):
                emoji = e
                break
        if not emoji and not first.startswith("die") and not first.startswith("der") and not first.startswith("das"):
            continue
        # find Gender-like cell
        gender_cell = ""
        article_cell = ""
        for idx, p in enumerate(parts):
            pl = p.lower()
            if pl in {"maskulin", "feminin", "neutral", "neutrum", "plural"} or pl in {"m.", "f.", "n."}:
                gender_cell = p
            if pl in {"der", "die", "das", "—", "-", ""} and idx > 1:
                # Article often immediately after Gender
                if gender_cell and not article_cell:
                    article_cell = p
        if emoji and gender_cell:
            expected_gender, expected_art = GENDER_EMOJI[emoji]
            g_norm = gender_cell.lower().replace("neutrum", "neutral")
            if expected_gender.lower() not in g_norm and g_norm not in {"m.", "f.", "n."}:
                # allow Neutral vs neutrum already handled
                if not (emoji == "🟢" and "neutral" in g_norm or emoji == "🟢" and "neutrum" in gender_cell.lower()):
                    report.err(
                        path,
                        i,
                        f"emoji {emoji} expects {expected_gender}, Gender cell is {gender_cell!r}",
                    )
            if article_cell and article_cell in {"der", "die", "das"} and article_cell != expected_art:
                report.err(
                    path,
                    i,
                    f"emoji {emoji} expects article {expected_art}, found {article_cell!r}",
                )


def check_verb_class_vs_form(path: Path, text: str, report: Report) -> None:
    for i, line in enumerate(text.splitlines(), 1):
        if not is_md_table_row(line):
            continue
        parts = cells(line)
        if len(parts) < 6:
            continue
        # Heuristic: header contains Präteritum
        joined = " | ".join(parts)
        if "Präteritum" in joined and "German" in parts[0]:
            continue
        prateritum = ""
        klass = ""
        for p in parts:
            if re.match(r"^(reg\.|irr\.|Regular|Irregular)", p, re.I):
                klass = p
        # Präteritum is often 4th column after German English Persian
        if len(parts) >= 4:
            prateritum = parts[3]
        if klass.lower().startswith("reg") and prateritum:
            if IRREG_STEMS.search(prateritum):
                report.err(
                    path,
                    i,
                    f"class {klass!r} but Präteritum {prateritum!r} looks irregular",
                )
        # Regular (sep) with kam/fuhr/ging etc.
        if "sep" in klass.lower() and klass.lower().startswith("reg") and IRREG_STEMS.search(prateritum or ""):
            report.err(path, i, f"separable verb labeled regular with irregular form {prateritum!r}")


def check_tsv(path: Path, report: Report) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.err(path, 0, "file is not valid UTF-8")
        return
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        report.err(path, 0, "empty TSV")
        return
    header_fields = len(lines[0].split("\t"))
    # Q/A decks (grammar, phrases) are two-column; verb/vocab decks need a full header
    if header_fields < 2:
        report.err(path, 1, "TSV missing header")
    elif header_fields == 2 and path.name.startswith(("vocabulary", "verbs")):
        report.err(path, 1, "vocabulary/verbs TSV needs a multi-column header")
    for i, line in enumerate(lines, 1):
        if KARDEN.search(line) or re.search(r"[؀-ۿ]{2,}(?:den|ten|en)\b", line):
            report.err(path, i, "mixed-script Persian in TSV")
        if "geve " in line or " geve " in line:
            report.err(path, i, "typo: geve (expected gebe)")
        n = len(line.split("\t"))
        # allow ragged only as warning for data rows if close
        if i > 1 and n not in {header_fields, header_fields - 1, header_fields + 1}:
            report.err(path, i, f"field count {n} != header {header_fields}")


def check_listening_names(root: Path, report: Report) -> None:
    for level in ("A1", "A2", "B1", "B2"):
        folder = root / level / "listening"
        if not folder.is_dir():
            continue
        for f in folder.glob("*.md"):
            name = f.name.lower()
            if level.lower() not in name and "aussprache" not in name:
                report.err(f, 0, f"listening filename does not mention level {level}")
            if "hoerversthen" in name:
                report.err(f, 0, "typo hoerversthen → hoerverstehen")


def check_internal_links(root: Path, report: Report) -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for md in root.rglob("*.md"):
        if any(part in {"legacy", "tools", "docs"} for part in md.parts):
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            for m in link_re.finditer(line):
                target = m.group(1)
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                # strip anchor
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                resolved = (md.parent / path_part).resolve()
                try:
                    resolved.relative_to(root.resolve())
                except ValueError:
                    continue
                if not resolved.exists():
                    report.err(md, i, f"broken internal link → {target}")


def iter_content_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("**/*.md", "**/*.tsv"):
        for p in root.glob(pattern):
            if any(part in {".git", "node_modules", "legacy", "tools", "docs"} for part in p.parts):
                continue
            files.append(p)
    return sorted(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()
    report = Report()

    for path in iter_content_files(root):
        if path.suffix == ".tsv":
            check_tsv(path, report)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        check_text_corruption(path, text, report)
        check_known_bad_german(path, text, report)
        if "vocabulary" in path.parts and path.name == "words.md":
            check_vocab_gender(path, text, report)
        if path.name == "verbs.md":
            check_verb_class_vs_form(path, text, report)

    check_listening_names(root, report)
    check_internal_links(root, report)

    print(f"Scanned root: {root}")
    print(f"Errors: {len(report.errors)}  Warnings: {len(report.warnings)}")
    for e in report.errors[:200]:
        print(f"ERROR {e}")
    if len(report.errors) > 200:
        print(f"... and {len(report.errors) - 200} more errors")
    for w in report.warnings[:50]:
        print(f"WARN  {w}")

    if report.errors and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
