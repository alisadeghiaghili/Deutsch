#!/usr/bin/env python3
"""Export Anki TSV decks from Markdown vocabulary/verb tables.

Markdown tables are the source of truth. This tool normalizes known header
families into one output schema and writes tab-separated files under
``<level>/flashcards/``.

Output schemas
--------------
vocabulary-anki.tsv
    German, English, Persian, Gender, Article, Plural, Cases, Example

verbs-anki.tsv
    German, English, Persian, Präteritum, Perfekt, Auxiliary, Class, Frame, Example

Usage
-----
    python tools/export_tsv.py [--root PATH] [--level A1] [--dry-run]

Exit codes: 0 success, 1 parse/export failure.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LEVELS = ("A1", "A2", "B1", "B2")

GENDER_MAP = {
    "maskulin": "Maskulin",
    "m": "Maskulin",
    "m.": "Maskulin",
    "feminin": "Feminin",
    "f": "Feminin",
    "f.": "Feminin",
    "neutral": "Neutral",
    "neutrum": "Neutral",
    "n": "Neutral",
    "n.": "Neutral",
    "plural": "Plural",
}

CLASS_MAP = {
    "regular": "reg.",
    "reg": "reg.",
    "reg.": "reg.",
    "ja": "reg.",
    "yes": "reg.",
    "irregular": "irr.",
    "irr": "irr.",
    "irr.": "irr.",
    "nein": "irr.",
    "no": "irr.",
}


def split_row(line: str) -> list[str] | None:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|") and s.count("|") >= 3):
        return None
    if re.match(r"^\|[\s|:-]+\|$", s):
        return None
    cells = [c.strip() for c in s.strip("|").split("|")]
    if not cells:
        return None
    # drop pure separator
    if all(set(c) <= set("-: ") and c for c in cells):
        return None
    return cells


def is_header(cells: list[str]) -> bool:
    joined = " ".join(cells).lower()
    return any(
        key in joined
        for key in (
            "german",
            "english",
            "persian",
            "präteritum",
            "prateritum",
            "gender",
            "article",
        )
    )


def strip_emoji(text: str) -> str:
    # remove status emoji but keep the lemma
    out = re.sub(r"[🔵🔴🟢🟡⭐💡]\s*", "", text)
    return out.strip()


def article_from_lemma(lemma: str) -> tuple[str, str]:
    m = re.match(r"^(der|die|das)\s+(.+)$", lemma, re.I)
    if not m:
        return lemma.strip(), ""
    art = m.group(1).lower()
    rest = m.group(2).strip()
    return rest, art


def gender_from_article(article: str) -> str:
    return {"der": "Maskulin", "die": "Feminin", "das": "Neutral"}.get(article, "")


def normalize_class(value: str, prateritum: str) -> str:
    v = (value or "").strip().lower()
    base = CLASS_MAP.get(v, "")
    sep = " (sep)" if "sep" in v or value.lower().endswith("sep") else ""
    # B2: "reg." / "irr." already; A1: "Irregular (sep)" etc.
    if not base:
        if "irr" in v:
            base = "irr."
        elif "reg" in v:
            base = "reg."
        elif v in {"yes", "ja"}:
            # B1 Separable Yes with irregular stem?
            base = "irr." if re.search(r"\b(kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog|riet|bat)\b", prateritum, re.I) else "reg."
            sep = " (sep)"
        elif v in {"no", "nein"}:
            base = "irr." if re.search(r"\b(kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog|riet|bat|sprach)\b", prateritum, re.I) else "reg."
        else:
            base = value.strip() or "—"
    if "sep" in value.lower() and not sep:
        sep = " (sep)"
    # derive from form if Regular/empty but irregular stem present
    if base == "reg." and re.search(
        r"\b(kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog|riet|bat|sprach|schrieb)\b",
        prateritum,
        re.I,
    ):
        base = "irr."
    return f"{base}{sep}"


def parse_verbs(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    header: list[str] | None = None
    idx: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = split_row(line)
        if not cells:
            continue
        if is_header(cells) and header is None:
            header = [c.lower() for c in cells]
            for i, h in enumerate(header):
                idx[h] = i
            continue
        if header is None or is_header(cells):
            continue
        if len(cells) < 3:
            continue

        def get(*names: str) -> str:
            for n in names:
                for key, i in idx.items():
                    if n in key and i < len(cells):
                        return cells[i]
            return ""

        german = strip_emoji(get("german", "verb"))
        if not german or german.lower() in {"german", "#"}:
            continue
        # skip section-like rows
        if re.match(r"^#+\s", line.strip()):
            continue

        english = get("english")
        persian = get("persian")
        prateritum = get("präteritum", "prateritum", "past")
        perfect = get("perfekt", "perfect")
        # B2 "Perfekt (haben)" may only have haben form; Auxiliary separate or implied
        auxiliary = get("auxiliary", "aux")
        if not auxiliary:
            low = perfect.lower()
            if low.startswith("ist ") or " ist " in f" {perfect}":
                auxiliary = "sein"
            elif perfect:
                auxiliary = "haben"
        klass_src = get("class", "type", "regular", "separable")
        frame = get("frame", "case", "cases")
        example = get("example")

        # B1 Present (ich) is not needed for TSV export of forms
        # If Präteritum empty but Past (ich) present, already mapped via "past"
        if not prateritum:
            prateritum = get("past")
        if not perfect:
            perfect = get("perfect")

        rows.append(
            {
                "German": german,
                "English": english,
                "Persian": persian,
                "Präteritum": prateritum,
                "Perfekt": perfect,
                "Auxiliary": auxiliary,
                "Class": normalize_class(klass_src, prateritum),
                "Frame": frame.replace("Cases", "").strip() or "—",
                "Example": example,
            }
        )
    return rows


def parse_words(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    header: list[str] | None = None
    idx: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = split_row(line)
        if not cells:
            continue
        if is_header(cells) and "german" in " ".join(cells).lower() and header is None:
            header = [c.lower() for c in cells]
            for i, h in enumerate(header):
                idx[h] = i
            continue
        if header is None:
            continue
        if len(cells) < 4:
            continue

        def get(*names: str) -> str:
            for n in names:
                for key, i in idx.items():
                    if n in key and i < len(cells):
                        return cells[i]
            return ""

        raw = strip_emoji(cells[idx.get("german", 0)] if "german" in idx else cells[0])
        # skip adjective/verb filler rows
        if not raw:
            continue
        lemma, article_from_lemma_field = article_from_lemma(raw)
        gender = get("gender")
        gender_norm = GENDER_MAP.get(gender.strip().lower().rstrip("."), gender)
        article = get("article")
        if not article and article_from_lemma_field:
            article = article_from_lemma_field
            if not gender_norm:
                gender_norm = gender_from_article(article)
        # B2 style: lemma already "die Hypothese", Gender "f."
        if not gender_norm and article_from_lemma_field:
            gender_norm = gender_from_article(article_from_lemma_field)
        plural = get("plural")
        cases = get("case")
        example = get("example")
        if not lemma or lemma.lower() == "german":
            continue
        rows.append(
            {
                "German": lemma,
                "English": get("english"),
                "Persian": get("persian"),
                "Gender": gender_norm or "—",
                "Article": article or "—",
                "Plural": plural or "—",
                "Cases": cases or "—",
                "Example": example or "—",
            }
        )
    return rows


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str], dry: bool) -> None:
    lines = ["\t".join(fields)]
    for row in rows:
        lines.append("\t".join(row.get(f, "").replace("\t", " ").strip() for f in fields))
    text = "\n".join(lines) + "\n"
    if dry:
        print(f"DRY {path} rows={len(rows)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {path} rows={len(rows)}")


VERB_FIELDS = ["German", "English", "Persian", "Präteritum", "Perfekt", "Auxiliary", "Class", "Frame", "Example"]
WORD_FIELDS = ["German", "English", "Persian", "Gender", "Article", "Plural", "Cases", "Example"]


def export_level(root: Path, level: str, dry: bool) -> int:
    verbs = parse_verbs(root / level / "vocabulary" / "verbs.md")
    words = parse_words(root / level / "vocabulary" / "words.md")
    if not verbs and not words:
        print(f"ERROR: no rows parsed for {level}", file=sys.stderr)
        return 1
    write_tsv(root / level / "flashcards" / "verbs-anki.tsv", verbs, VERB_FIELDS, dry)
    write_tsv(root / level / "flashcards" / "vocabulary-anki.tsv", words, WORD_FIELDS, dry)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--level", choices=LEVELS, help="export one level only")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    levels = (args.level,) if args.level else LEVELS
    rc = 0
    for level in levels:
        rc |= export_level(root, level, args.dry_run)
    return rc


if __name__ == "__main__":
    sys.exit(main())
