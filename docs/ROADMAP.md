# Roadmap

Priority order. Do not start a later item while an earlier open P0 item remains.

## Done

| Version | Work |
|---------|------|
| v0.2.0 | Policy, validator + blocking CI, critical linguistic fixes, renames, B2 index, legacy quarantine, README truthfulness |
| v0.3.0 | Per-level `resources.md` (A1–B2) with named books, DW URLs, YouTube series, podcasts; README study path |
| v0.3.1 | Listening drills separated from answer keys (S3) |
| v0.4.0 | Unified verb schema (B1/B2 migrated), `docs/SCHEMA.md`, TSV generated from Markdown via `tools/export_tsv.py` |

## Open

| ID | Work | Exit criteria |
|----|------|----------------|
| — | (none blocking) | — |

## Next — v0.5.x (content depth)

| ID | Work | Exit criteria |
|----|------|----------------|
| C1 | Deduplicate lemmas across vocabulary tables | No exact duplicate rows |
| C2 | Fix remaining weak/invented plurals against DWDS | Plural column trustworthy |
| C3 | Split B2 stretch (C1-ish) section from core B2 list | Clear two-block structure |
| C4 | A1/A2 verb Class column rename `Regular` → `reg.` for full header parity | Same header tokens all levels |

## Later

| ID | Work | Exit criteria |
|----|------|----------------|
| P4 | Optional CI job: fail if TSV differs from fresh export | Drift-proof decks |
| P5 | Grammar/phrases TSV export from Markdown | No hand-maintained decks |

## Out of scope (for now)

- Full Anki package generation
- Audio assets
- Interactive trainer UI
