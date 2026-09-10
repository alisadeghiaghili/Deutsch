# Changelog

All notable changes to this study corpus are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows SemVer as in `POLICY.md`.

## [0.6.0] — blocking corpus gates in CI

### Added
- `tools/check_tsv_drift.py` — fail when committed TSV ≠ fresh Markdown export
- CI job steps: duplicate-lemma check + TSV drift check (both blocking)
- npm scripts: `check:tsv`, `gates`

### Changed
- `tools/find_duplicates.py` exits 1 when any duplicate lemma remains
- CI workflow name for the validator job is now **Corpus gates**

## [0.5.1] — plural corrections

### Added
- `tools/flag_plurals.py` — heuristic flags for invented mass/abstract plurals
- `tools/fix_plurals.py` — high-confidence plural cell corrections

### Fixed
- 76 plural cells across A1–B2 (e.g. die Mute/Stolze/Wuten/Trauern/Glücke/Softwares/Medizinien → `—` or correct plural)
- `Bewusstsein` plural `die Bewusstseins` → `—`

## [0.5.0] — corpus depth cleanup

### Added
- `tools/find_duplicates.py` — report duplicate lemmas
- `tools/cleanup_v05.py` — dedupe helper used for this pass
- B2 vocabulary: **Stretch (C1-leaning abstracts)** banner before science/philosophy/politics blocks
- npm script `dedupe:check`

### Changed
- Removed **~1.9k** duplicate vocabulary rows (A2 padded the most); unique lemmas only
- A1/A2 verb `Regular`/`Irregular` cells renamed to unified `Class` (`reg.` / `irr.` / `(sep)`)
- Verb/vocab TSV regenerated from the cleaned Markdown
- README measured counts updated after dedupe

### Fixed
- Exact duplicate lemmas across A1–B2 vocabulary and verb tables

## [0.4.0] — unified schema and generated TSV

### Added
- `docs/SCHEMA.md` — single verb/vocab column contract for all levels
- `tools/export_tsv.py` — regenerate `vocabulary-anki.tsv` and `verbs-anki.tsv` from Markdown
- `tools/migrate_verb_schema.py` — one-shot B1/B2 verb header migration
- npm script `export:tsv`

### Changed
- B1 and B2 `vocabulary/verbs.md` migrated to the unified verb header (German → Class → Frame → Example)
- B2 `vocabulary/words.md` Gender cells use `Maskulin`/`Feminin`/`Neutral`; header notes stretch academic vocabulary
- All four levels’ vocabulary/verb TSV decks regenerated from Markdown (single source of truth)
- package version 0.4.0

### Fixed
- B1 separable/regular mislabels during migration (e.g. `zugeben` → `irr. (sep)`, `einräumen` → `reg. (sep)`, `laufen` → `irr.` + `sein`)

## [0.3.1] — listening drills without inline answers

### Added
- `tools/split_listening_answers.py` — moves `question → answer` lines into companion Lösungen files
- `A2/listening/hoerverstehen-a2-loesungen.md` (grouped by Übung)
- `B2/listening/hoerverstehen-b2-loesungen.md` (comprehension + Diktat models)

### Fixed
- A2/B2 listening drills no longer spoil answers next to questions
- A1 phone phrase Persian gloss and listening heading typo
- A2 post-office dialogue: Tracking-Nummer spelling

## [0.3.0] — study resources

### Added
- Level-matched `resources.md` for A1, A2, B1, B2 with named coursebooks, DW course URLs, YouTube series, and podcasts
- README study path points at those resource files first

### Changed
- Study guidance no longer ends at generic channel names

## [0.2.0] — quality foundation

### Added
- `POLICY.md` — linguistic accuracy, schema, level placement, resource, and release rules
- `docs/ROADMAP.md` — sequenced next work
- Data validator (`tools/validate_corpus.py`) and mechanical repair helper (`tools/fix_corpus.py`)
- `B2/B2.md` grammar index
- `legacy/README.md` quarantine map for superseded root drafts

### Fixed
- Unusable `B1/grammar/konjunktiv2-erweitert.md` rewritten with intact German examples
- Wrong infinitives and Präteritum forms across A1/A2/B1 verb tables and flashcards
- False separable/regular labels on prefix verbs
- Wrong article/gender pairs in flashcards and vocabulary tables
- Mixed-script Persian glosses (Latin suffixes glued to Persian stems)
- Listening filenames (A2 file named a1, B2 spelling typo)
- Dead B2 index back-links from B2 grammar files
- README path claims and size claims aligned with the tree

### Changed
- CI: required corpus validator job; internal offline link check; markdownlint without full rule disable
- Root duplicate drafts moved under `legacy/`

## [0.1.0] — prior state

- CEFR folders A1–B2 with vocabulary, grammar, phrases, listening, DW notes, flashcards
- Early non-blocking markdownlint/link workflow
