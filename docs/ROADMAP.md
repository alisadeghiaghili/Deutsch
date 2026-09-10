# Roadmap

Priority order. Do not start a later item while an earlier P0 item is open.

## Now — v0.2.x (quality foundation)

| ID | Work | Exit criteria |
|----|------|----------------|
| Q1 | Rewrite corrupted Konjunktiv II file | Full German examples, no corruption placeholders |
| Q2 | Validator + wire into CI (blocking) | `python tools/validate_corpus.py` green locally and in Actions |
| Q3 | Critical form/gender/script fixes across A1–B2 | Known bad list empty |
| Q4 | Rename misnamed listening files; create or unlink `B2.md` | No dead internal links |
| Q5 | Quarantine root duplicates | Single path per document |
| Q6 | README + CHANGELOG truthfulness | Counts match tree |

## Next — v0.3.x (study path)

| ID | Work | Exit criteria |
|----|------|----------------|
| S1 | Per-level `resources.md` with named books, DW courses, podcast episodes, YouTube lessons | Every row has level + direct URL |
| S2 | Replace generic “watch YouTube” guidance in README | Concrete sequences A1→B2 |
| S3 | Listening packs: transcript/answer split | Usable as drills |

## Later — v0.4.x (system)

| ID | Work | Exit criteria |
|----|------|----------------|
| P1 | Unify verb/vocab schema across levels | One header family |
| P2 | Generate TSV decks from Markdown sources | One source of truth |
| P3 | Stretch vocabulary (B2/C1 academic) clearly labeled | No silent level inflation |

## Out of scope (for now)

- Full Anki package generation
- Audio assets
- Interactive trainer UI
