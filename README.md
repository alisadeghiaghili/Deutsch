# Deutsch Lernen — Personal German Study Notes

Bilingual (Persian/English) German reference organized by CEFR level (A1–B2).

Accuracy rules, schema, and release process: see [`POLICY.md`](POLICY.md).  
Planned work: [`docs/ROADMAP.md`](docs/ROADMAP.md).  
Change history: [`CHANGELOG.md`](CHANGELOG.md).

## Structure

```
Deutsch/
├── A1/ … A2/ … B1/ … B2/
│   ├── vocabulary/     # words.md + verbs.md
│   ├── grammar/        # topic files (A1 also has vhs-a1-zielpunkte.md)
│   ├── flashcards/     # Markdown decks + Anki-importable TSV
│   ├── phrases/        # everyday expressions
│   ├── listening/      # comprehension / pronunciation
│   └── dw/             # Deutsche Welle course pointers
├── B2/B2.md            # B2 grammar index
├── tools/              # corpus validator and repair helpers
├── legacy/             # superseded root drafts (do not study from these)
├── POLICY.md
├── CHANGELOG.md
└── README.md
```

## Target audience

Persian speakers learning German from A1 through B2.

## Measured content size

Approximate table data rows (vocabulary/verbs) and grammar file counts:

| Level | Vocabulary rows | Verb rows | Grammar files |
|-------|----------------:|----------:|--------------:|
| A1 | ~788 | ~105 | 22 |
| A2 | ~2440 | ~160 | 10 |
| B1 | ~1240 | ~180 | 10 |
| B2 | ~390 | ~215 | 10 |

Counts are approximate (header/separator rows excluded). Prefer the files over README if they disagree after a large edit; re-run a row count before claiming new totals.

## How to study

1. Start at `A1/vocabulary/words.md` and `A1/vocabulary/verbs.md`.
2. Work through `A1/grammar/` in a sensible order (articles → cases → modals → Perfekt/Partizip → word order).
3. Drill `A1/flashcards/` (import TSV into Anki: tab-separated).
4. Use `A1/listening/` and `A1/phrases/` for sound and daily chunks.
5. Follow `A1/dw/` for Deutsche Welle course fit.
6. Repeat the same path for A2, then B1, then B2 (`B2/B2.md` indexes advanced grammar).

## Vocabulary table format

| German | English | Persian | Gender | Article | Plural | Cases |
|--------|---------|---------|--------|---------|--------|-------|

Color: 🔵 Maskulin · 🔴 Feminin · 🟢 Neutral · 🟡 Plural-only

## Verb table format

| German | English | Persian | Präteritum | Perfekt | Auxiliary | Class | Frame | Example |
|--------|---------|---------|------------|---------|-----------|-------|-------|---------|

`Class` is `reg.` / `irr.` / `reg. (sep)` / `irr. (sep)` / `refl.` and must match the forms shown.

## Anki

Each level’s `flashcards/` folder contains TSV files. Import in Anki with **Tab** as separator.  
TSV is a convenience export of the Markdown tables; fix errors in Markdown first.

## Quality gate

```bash
python tools/validate_corpus.py --root .
```

This checks corruption characters, mixed-script Persian, article/gender coherence, obvious verb-form mistakes, TSV shape, listening filenames, and internal links. CI runs the same script on every push/PR.

## Sources

- Starten wir! A1–B2 (primary coursebook path)
- Hueber / official word lists
- Deutsche Welle: Nicos Weg, Deutsch warum nicht?
- Busuu, Duolingo, Memrise (supplementary)
- VHS A1 curriculum notes

## License / use

Personal study notes. Verify critical grammar against Duden or DWDS before exam use.
