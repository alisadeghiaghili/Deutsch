# Changelog

All notable changes to this study corpus are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows SemVer as in `POLICY.md`.

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
