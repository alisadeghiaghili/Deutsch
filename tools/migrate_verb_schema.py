#!/usr/bin/env python3
"""Rewrite B1/B2 verb tables into the unified POLICY schema.

One-shot migration helper used for v0.4. Safe to delete after the tables
are rewritten; export_tsv.py remains the ongoing generator.
"""

from __future__ import annotations

import re
from pathlib import Path

UNIFIED_HEADERS = [
    "German",
    "English",
    "Persian",
    "Präteritum",
    "Perfekt",
    "Auxiliary",
    "Class",
    "Frame",
    "Example",
]
UNIFIED = "| " + " | ".join(UNIFIED_HEADERS) + " |"
SEP = "|" + "|".join(["--------"] * len(UNIFIED_HEADERS)) + "|"

IRREG_STEM = re.compile(
    r"\b(kam|fuhr|ging|stieg|lud|gab|nahm|stand|zog|riet|bat|sprach|schrieb|"
    r"bestritt|erkannte?|begriff|dachte|erfuhr|empfahl|"
    r"entwarf|fand|fing|bot|wog|entschied|beschrieb)\b",
    re.I,
)


def strip_emoji(text: str) -> str:
    return re.sub(r"[🔵🔴🟢🟡⭐💡]\s*", "", text).strip()


def split_cells(line: str) -> list[str] | None:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|") and s.count("|") >= 3):
        return None
    parts = [c.strip() for c in s.strip("|").split("|")]
    if all(set(c) <= set("-: ") and c for c in parts):
        return None
    return parts


def derive_auxiliary(perfect: str) -> str:
    p = perfect.strip().lower()
    if p.startswith("ist ") or p.startswith("ist"):
        return "sein"
    if "ist " in p:
        return "sein"
    if perfect.strip():
        return "haben"
    return "—"


def class_from_b1(separable: str, prateritum: str) -> str:
    sep = " (sep)" if separable.strip().lower() in {"yes", "ja", "true"} else ""
    if IRREG_STEM.search(prateritum):
        return f"irr.{sep}"
    # also treat stem-vowel changes like bestritt, dachte as irregular when present
    return f"reg.{sep}" if not IRREG_STEM.search(prateritum) else f"irr.{sep}"


def class_from_b2(type_cell: str, prateritum: str) -> str:
    t = type_cell.strip().lower()
    sep = " (sep)" if "sep" in t else ""
    if "irr" in t or IRREG_STEM.search(prateritum):
        base = "irr."
    elif "reg" in t:
        base = "reg."
    else:
        base = "irr." if IRREG_STEM.search(prateritum) else "reg."
    # correct reg. labels that are actually irregular by form
    if base == "reg." and IRREG_STEM.search(prateritum):
        base = "irr."
    return f"{base}{sep}"


def parse_b1_table(lines: list[str]) -> list[dict[str, str]]:
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in lines:
        cells = split_cells(line)
        if not cells:
            continue
        joined = " ".join(cells).lower()
        if "german" in joined and header is None:
            header = [c.lower() for c in cells]
            continue
        if header is None:
            continue
        if len(cells) < 7:
            continue
        german, english, persian, present, past, perfect, separable = cells[:7]
        prateritum = past or present
        rows.append(
            {
                "German": strip_emoji(german),
                "English": english,
                "Persian": persian,
                "Präteritum": prateritum,
                "Perfekt": perfect,
                "Auxiliary": derive_auxiliary(perfect),
                "Class": class_from_b1(separable, prateritum),
                "Frame": "—",
                "Example": "—",
            }
        )
    return rows


def parse_b2_table(lines: list[str]) -> list[dict[str, str]]:
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in lines:
        cells = split_cells(line)
        if not cells:
            continue
        joined = " ".join(cells).lower()
        if "german" in joined and header is None:
            header = [c.lower() for c in cells]
            continue
        if header is None:
            continue
        if len(cells) < 7:
            continue
        german, english, persian, typ, prateritum, perfect, partizip = cells[:7]
        example = cells[7] if len(cells) > 7 else "—"
        rows.append(
            {
                "German": strip_emoji(german),
                "English": english,
                "Persian": persian,
                "Präteritum": prateritum,
                "Perfekt": perfect,
                "Auxiliary": derive_auxiliary(perfect),
                "Class": class_from_b2(typ, prateritum),
                "Frame": "—",
                "Example": example or "—",
            }
        )
    return rows


def rewrite(level: str, parser) -> None:
    path = Path(level) / "vocabulary" / "verbs.md"
    text = path.read_text(encoding="utf-8")
    sections: list[tuple[str, list[str]]] = []
    current = "General"
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if buf:
                sections.append((current, buf))
            current = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    if buf:
        sections.append((current, buf))

    out = [
        f"# {level} Verben / Verbs",
        "",
        "> Unified verb schema (see POLICY.md).",
        "> Regenerate TSV: `python tools/export_tsv.py`",
        "",
    ]
    total = 0
    for title, body in sections:
        rows = parser(body)
        if not rows:
            continue
        out.append(f"## {title}")
        out.append("")
        out.append(UNIFIED)
        out.append(SEP)
        for row in rows:
            out.append("| " + " | ".join(row[h] or "—" for h in UNIFIED_HEADERS) + " |")
            total += 1
        out.append("")
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"{level}: {total} rows")


if __name__ == "__main__":
    rewrite("B1", parse_b1_table)
    rewrite("B2", parse_b2_table)
