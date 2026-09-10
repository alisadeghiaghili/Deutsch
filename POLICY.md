# Content Integrity Policy

This repository is a personal CEFR German study corpus (A1–B2) with Persian glosses.
Accuracy beats volume. A wrong gender or verb form is worse than a missing entry.

## 1. Versioning

| Field | Rule |
|-------|------|
| Scheme | SemVer `MAJOR.MINOR.PATCH` |
| `MINOR` | New level folders, schema changes, large verified vocabulary batches, resource packs |
| `PATCH` | Linguistic corrections, renames, docs, CI, tooling |
| Tags | `vX.Y.Z` on `main` after merge |
| Releases | GitHub Release notes from `CHANGELOG.md` section for that version |
| Current | See `CHANGELOG.md` head and latest git tag |

## 2. Linguistic accuracy (non-negotiable)

1. **German is source of truth for forms.** Verify infinitive, gender, plural, Präteritum, Partizip II, auxiliary, and case/preposition frame against a standard reference (Duden, DWDS, PONS, Langenscheidt) before merge.
2. **No invented plurals.** Mass and abstract nouns (Mut, Stolz, Wut, Trauer, Glück, Fleisch, Mehl, Software…) get plural only if the dictionary lists one. Otherwise leave plural as `—`.
3. **No fake verbs or adjectives-as-verbs.** Entries like `funktionen`, `appetitlich` (as verb), `emissionieren` are invalid.
4. **Case frames on verbs** must match the construction used in the example (`antworten auf + Akk.`, `hoffen auf + Akk.`). Blank is better than wrong.
5. **Persian glosses** must be Persian script only. Mixed tokens such as `کردن` are production defects and must be fixed on sight.
6. **Encoding corruption** (CJK placeholders, mojibake, truncated cells) makes a file unusable; rewrite from the intact language column, do not ship.
7. **Gender emoji** must match the Gender/Article column: 🔵 Maskulin, 🔴 Feminin, 🟢 Neutral, 🟡 Plural-only.

## 3. Schema (single layout per artifact type)

### Vocabulary table (`vocabulary/words.md`)

| German | English | Persian | Gender | Article | Plural | Cases |
|--------|---------|---------|--------|---------|--------|-------|

- `Gender`: `Maskulin` \| `Feminin` \| `Neutral` \| `Plural` (German words, not `m./f./n.`).
- `Article`: `der` \| `die` \| `das` \| `—`.
- `Plural`: full plural with article, or `—`.
- `Cases`: for nouns usually `—` or a note only when irregular (e.g. weak masculine). Do not stamp `[Nom][Akk][Dat][Gen]` on every row.
- Do not mix adjectives or verbs into noun tables. Use a dedicated table/file.

### Verb table (`vocabulary/verbs.md`)

| German | English | Persian | Präteritum | Perfekt | Auxiliary | Class | Frame | Example |
|--------|---------|---------|------------|---------|-----------|-------|-------|---------|

- `Class`: `reg.` \| `irr.` \| `reg. (sep)` \| `irr. (sep)` \| `refl.` — **must match** the Präteritum/Partizip shown.
- `Frame`: e.g. `[Akk]`, `[Dat]`, `[Präp: auf+Akk]`, `—`.
- `Perfekt`: full form with auxiliary (`hat gegeben` / `ist gegangen`).

### Flashcards

- One **source of truth** per level: the `.md` vocabulary/verb/grammar tables.
- TSV is **generated or mechanically checked** against those tables; do not hand-edit three parallel decks.
- TSV header required. Columns stable. No column shift.

## 4. Level placement (CEFR)

| Topic | Default level |
|-------|----------------|
| Present, cases, articles, Perfekt, modals, trennbar, basic questions | A1 |
| Präteritum of common verbs, Nebensätze, Relativsätze, adjective declension | A2 |
| Passiv, Konjunktiv II (wishes/politeness), Konjunktiv I (Indirekte Rede), Wortbildung, Idiome | B1 |
| Complex Passiv, extended Konjunktiv I/II, Stilistik, Textstrukturen, formal correspondence | B2 |

- Content **far above** the folder level (e.g. Epistemologie, Ontologie in B2 general lists) is out of scope unless marked as `stretch`.
- Flashcards for a level must match that level, not A1 survival phrases under B1.

## 5. Study resources

For every topic or skill area, resources must be **level-matched and specific**:

1. Book / chapter / unit name (not “a grammar book”).
2. Podcast or series **episode** title when possible.
3. Direct URL (DW, YouTube, podcast site) that a learner can open.
4. One-line “why this level” note.

Generic names (“YouTube”, “some podcast”) are not acceptable.

## 6. Repository hygiene

1. No duplicate root drafts of leveled content. One path per document.
2. No `moved to …` stubs that point at missing files.
3. Filenames match level and spelling: `hoerverstehen-a2.md`, not `hoerverstehen-a1.md` inside `A2/`.
4. Index links must resolve (`B2.md` must exist or links must be removed).
5. README counts are **measured** (script or documented count), not aspirational.

## 7. Quality gates (CI)

1. Data validator must pass (gender/article coherence, mixed-script Persian, corruption characters, TSV shape, class vs form heuristics).
2. Markdown lint for structure (headings, tables) may warn, but **validator failures block merge**.
3. Link check should fail the job on broken **internal** links; external flaky hosts may be allowlisted.
4. `continue-on-error: true` is not allowed on the validator job.

## 8. Commits, PRs, releases

1. Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `refactor:`, `content:`.
2. Prefer `content:` for linguistic corrections (subject in English, imperative).
3. One PR ≈ one focused week of work; state version impact in the PR body.
4. After merge to `main`: tag `vX.Y.Z`, write GitHub Release, update `CHANGELOG.md`.
5. Delete merged branches.
6. History must read as personal study engineering — no automation badges, co-authors, or generated-file disclaimers.

## 9. Definition of done (per release)

- [ ] Validator green in CI
- [ ] No known wrong German forms in touched files
- [ ] README counts match files
- [ ] CHANGELOG section for the version
- [ ] Tag + GitHub Release
- [ ] Next-step backlog updated (`docs/ROADMAP.md`)
