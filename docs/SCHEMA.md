# Unified corpus schemas

Markdown vocabulary/verb tables are the **source of truth**.
Anki TSV files under `*/flashcards/` are **generated**.

## Generate TSV

```bash
python tools/export_tsv.py --root .
# or one level:
python tools/export_tsv.py --root . --level A1
```

CI does not regenerate TSV automatically; regenerate after editing Markdown and commit both.

## Verb table (all levels)

| German | English | Persian | Präteritum | Perfekt | Auxiliary | Class | Frame | Example |
|--------|---------|---------|------------|---------|-----------|-------|-------|---------|

- **Class:** `reg.` \| `irr.` \| `reg. (sep)` \| `irr. (sep)` \| `refl.`
  Must match the Präteritum/Partizip shown. Separable prefix verbs keep `(sep)`.
- **Perfekt:** full form including auxiliary (`hat gegeben` / `ist gegangen`) or `habe X` / `ist X` style consistently used in that level file.
- **Auxiliary:** `haben` \| `sein` \| `—`
- **Frame:** case or preposition frame, e.g. `[Akk]`, `[Präp: auf+Akk]`, or `—`

### Legacy headers (pre-v0.4/v0.5, still parsed by the exporter)

| Level | Old header family |
|-------|-------------------|
| A1/A2 (pre-v0.5) | German \| English \| Persian \| Präteritum \| Perfekt \| Auxiliary \| **Regular** \| **Cases** \| Example |
| B1 (old) | German \| English \| Persian \| Present (ich) \| Past (ich) \| Perfect \| Separable |
| B2 (old) | German \| English \| Persian \| Type \| Präteritum \| Perfekt (haben) \| Partizip II \| Example |

As of v0.5.0, A1/A2 use unified `Class` / `Frame` tokens (`reg.`, `irr.`, `(sep)`).
B1/B2 verb files were migrated to the unified header in v0.4.0.
The exporter still accepts older `Regular`/`Irregular` values if reintroduced.

## Vocabulary table (all levels)

| German | English | Persian | Gender | Article | Plural | Cases |
|--------|---------|---------|--------|---------|--------|-------|

- **Gender:** `Maskulin` \| `Feminin` \| `Neutral` \| `Plural`
- **Article:** `der` \| `die` \| `das` \| `—`
- **Plural:** plural with article, or `—` if not used
- **Cases:** only when irregular or informative; otherwise `—`

Exported TSV also includes an `Example` column (`—` when the Markdown table has none).

## Flashcard files

| File | Generated from |
|------|----------------|
| `vocabulary-anki.tsv` | `vocabulary/words.md` |
| `verbs-anki.tsv` | `vocabulary/verbs.md` |

Grammar/phrases TSV remain hand-maintained Q/A decks (2 columns: Question, Answer).

## Stretch / advanced vocabulary

B2 academic philosophy-science items that sit above general B2 are marked with the existing legend emoji `🔴` (new/hard). Future work should add an explicit `stretch` section rather than silently mixing C1 terms into core lists.
