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
| v0.5.1 | Invented plural corrections (C2, 76 cells) |
| v0.6.0 | Blocking CI gates: validator + zero duplicates + TSV drift (P4+C5) |

## Open

| ID | Work | Exit criteria |
|----|------|----------------|
| — | (none blocking) | — |

## Next — v0.7.x candidates

| ID | Work | Exit criteria |
|----|------|----------------|
| P5 | Grammar/phrases TSV export from Markdown Q/A sections | No hand-maintained decks |
| C3 | Physically move B2 stretch sections to a separate file | Core list file stays B2-general |
| C6 | Case-frame accuracy pass on verbs (`antworten auf+Akk`, etc.) | Frames match examples |
| C7 | Spot-fix remaining `f.`/`n.` leftovers and weak-masculine notes | Gender column fully trustworthy |

## Later

| ID | Work | Exit criteria |
|----|------|----------------|
| C8 | Optional DWDS spot-check script for high-risk lemmas | Script + report |
| C9 | Listening B1: add short transcripts for question packs | Usable without external audio |

## Out of scope (for now)

- Full Anki package generation
- Audio assets
- Interactive trainer UI
