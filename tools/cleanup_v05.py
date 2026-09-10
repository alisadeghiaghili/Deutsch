#!/usr/bin/env python3
"""v0.5 maintenance: dedupe lemmas, normalize A1/A2 verb Class, tag B2 stretch."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("A1", "A2", "B1", "B2")


def split_row(line: str) -> list[str] | None:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|") and s.count("|") >= 3):
        return None
    if re.match(r"^\|[\s|:-]+\|$", s):
        return None
    cells = [c.strip() for c in s.strip("|").split("|")]
    if all(set(c) <= set("-: ") and c for c in cells):
        return None
    return cells


def join_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def lemma_key(cell: str) -> str:
    c = re.sub(r"[🔵🔴🟢🟡⭐💡]\s*", "", cell).strip()
    c = re.sub(r"^(der|die|das)\s+", "", c, flags=re.I)
    c = re.sub(r"\s*\(Adj\.\).*$", "", c)
    c = re.sub(r"\s*\(sich\).*$", "", c)
    return c.casefold().strip()


def row_quality(cells: list[str]) -> int:
    score = 0
    for c in cells:
        if c and c not in {"—", "-", ""}:
            score += len(c)
    return score


def is_header(cells: list[str]) -> bool:
    j = " ".join(cells).lower()
    return "german" in j and ("english" in j or "persian" in j)


def dedupe_file(path: Path) -> tuple[int, int]:
    """Remove later duplicate lemmas; keep the richest row for each key."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    out: list[str] = []
    best: dict[str, tuple[int, int]] = {}  # key -> (quality, out_index)
    removed = 0
    total_data = 0
    for line in lines:
        cells = split_row(line)
        if not cells or is_header(cells):
            out.append(line if line.endswith("\n") else line + "\n")
            continue
        key = lemma_key(cells[0])
        if not key:
            out.append(line if line.endswith("\n") else line + "\n")
            continue
        total_data += 1
        q = row_quality(cells)
        if key not in best:
            best[key] = (q, len(out))
            out.append(line if line.endswith("\n") else line + "\n")
            continue
        prev_q, idx = best[key]
        if q > prev_q:
            # replace previous row content (keep line ending style)
            ending = "\n" if out[idx].endswith("\n") else ""
            out[idx] = join_row(cells) + ending
            best[key] = (q, idx)
            removed += 1
        else:
            removed += 1
    path.write_text("".join(out), encoding="utf-8", newline="\n")
    return total_data, removed


REGULAR_MAP = {
    "regular": "reg.",
    "irregular": "irr.",
    "regular (sep)": "reg. (sep)",
    "irregular (sep)": "irr. (sep)",
    "regular (refl)": "refl.",
    "irregular (refl)": "refl.",
    "regular (sep, refl)": "refl. (sep)",
}


def normalize_verb_class(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    changed = 0

    def repl_row(line: str) -> str:
        nonlocal changed
        cells = split_row(line)
        if not cells or is_header(cells):
            return line
        # find Regular-like cell
        for i, c in enumerate(cells):
            cl = c.strip().lower()
            if cl in REGULAR_MAP:
                cells[i] = REGULAR_MAP[cl]
                changed += 1
                ending = "\n" if line.endswith("\n") else ""
                return join_row(cells) + ending
        return line

    out_lines = [repl_row(ln) for ln in text.splitlines(keepends=True)]
    text2 = "".join(out_lines)
    # header Regular → Class, Cases → Frame
    text2 = text2.replace("| Regular | Cases | Example |", "| Class | Frame | Example |")
    text2 = text2.replace("| Regular | Cases |", "| Class | Frame |")
    if text2 != text:
        path.write_text(text2, encoding="utf-8", newline="\n")
    return changed


STRETCH_HEADINGS = {
    "philosophie (philosophy)",
    "philosophy",
    "wissenschaft (science)",
    "science",
    "politik (politics)",
    "politics",
}


def tag_b2_stretch(path: Path) -> bool:
    """Insert a stretch banner before philosophy/science blocks if missing."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if "## Stretch" in text:
        return False
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    inserted = False
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^##\s+(.+)$", line.strip())
        if m and m.group(1).strip().casefold() in STRETCH_HEADINGS:
            if not inserted:
                out.append("## Stretch (C1-leaning abstracts)\n")
                out.append("\n")
                out.append(
                    "The blocks below (science / philosophy / politics abstracts) sit **above general B2**.\n"
                )
                out.append(
                    "Use them after core B2 vocabulary, not as the main exam word list.\n\n"
                )
                inserted = True
            out.append(line)
        else:
            out.append(line)
        i += 1
    if inserted:
        path.write_text("".join(out), encoding="utf-8", newline="\n")
    return inserted


def main() -> None:
    print("=== Dedupe vocabulary/verbs ===")
    for level in LEVELS:
        for rel in ("vocabulary/words.md", "vocabulary/verbs.md"):
            path = ROOT / level / rel
            if not path.exists():
                continue
            total, removed = dedupe_file(path)
            print(f"{path.relative_to(ROOT)}: data_rows={total} removed_or_replaced={removed}")

    print("\n=== Normalize A1/A2 verb Class labels ===")
    for level in ("A1", "A2"):
        path = ROOT / level / "vocabulary" / "verbs.md"
        n = normalize_verb_class(path)
        print(f"{path.relative_to(ROOT)}: class_cells_updated={n}")

    print("\n=== B2 stretch banner ===")
    path = ROOT / "B2" / "vocabulary" / "words.md"
    ok = tag_b2_stretch(path)
    print(f"inserted={ok}")


if __name__ == "__main__":
    main()
