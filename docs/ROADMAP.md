# Roadmap

Priority order. Do not start a later item while an earlier open P0 item remains.

## Done

| Version | Work |
|---------|------|
| v0.2.0 | Policy, validator + blocking CI, critical linguistic fixes, renames, B2 index, legacy quarantine, README truthfulness |
| v0.3.0 | Per-level `resources.md` (A1–B2) with named books, DW URLs, YouTube series, podcasts |
| v0.3.1 | Listening drills separated from answer keys (S3) |
| v0.4.0 | Unified verb schema, `docs/SCHEMA.md`, TSV generated from Markdown |
| v0.5.0 | Exact-lemma dedupe (~1.9k rows), A1/A2 `Class` token parity, B2 stretch banner |

## Open

| ID | Work | Exit criteria |
|----|------|----------------|
| C2 | Spot-check remaining invented plurals against DWDS/Duden | High-risk abstract/mass nouns corrected |

## Next — v0.6.x candidates

| ID | Work | Exit criteria |
|----|------|----------------|
| C2a | Scripted plural flags (`die Mute`, `die Softwares`, …) → curated fix list | Script + applied fixes |
| P4 | CI: fail if TSV differs from fresh `export_tsv.py` output | Drift-proof decks |
| P5 | Grammar/phrases TSV export from Markdown Q/A sections | No hand-maintained decks |
| C5 | Dedupe check in CI (`find_duplicates.py` must report 0) | Prevent re-padding |

## Later

| ID | Work | Exit criteria |
|----|------|----------------|
| C3 | Physically move B2 stretch sections to a separate file | Core list file stays B2-general |
| C6 | Case-frame accuracy pass on verbs (`antworten auf+Akk`, etc.) | Frames match examples |

## Out of scope (for now)

- Full Anki package generation
- Audio assets
- Interactive trainer UI
