## Goal
Create GitHub issues at `joaquimrcarvalho/dehergne-repertoire` for the ~60 unidentified locations in `locations_names_no_wikidata_with_candidates.xlsx`, with each issue's body summarizing the involved person's biography (dated places) for context. Sample format already approved: `Shaohing` issue shown above.

## Data source
60 rows (1 sheet, 14 cols). Key cols: `id_col` (person id), `place`, `place.type`, `place.date_inferred`, `groupname`, `candidate_id/name/score`, `name`. Biography context pulled read-only from SQLite at `database/sqlite/dehergne.sqlite` via `SELECT the_type, the_value, the_date FROM attributes WHERE entity=? AND the_type IN (...) ORDER BY the_date`, joining `@wikidata` companion rows to show which places are already linked.

## Categorization of all 60 rows
- **Bucket A — Data quality / non-toponym (5 rows):** 1 (`17010220`), 24 (Mogor), 28 (Oriente), 58 («apud Sinas»), 60 (À missão). → Report only in INDEX; +1 separate **bug** issue for row 1 (date leaked into place field — transcription error).
- **Bucket B — Existing OPEN issue (13 rows, 9 places):** Aquilon→#25, Ascitano→#6, Chang-tsin Yüansi→#29, Chayüankow→#4, Choui San Kia→#27, Katsusa→#18, Ko-li-tsem→#33, Cuama→#28, Tarahumaras→#14. → Skip (already tracked).
- **Bucket C — Existing issue, add comment (5 rows, 4 places):** Lofeu→#2 (closed), Chang-si→#30 (closed), Kasuza/Arima→#18, Pé-pou Linkiang→#31 (closed). → Draft a **comment** per issue with the new person's biography context (shown to user before posting). No duplicate issues.
- **Bucket D — NEW issues (37 rows → 33 unique places):** Create 33 issues, label `iloc`, English body. Multi-person places consolidated: Pe-tsien-chan/Pé-tsiuen-chan/«Pe tsien schan» (3 rows, region discrepancy flagged in body), Petit Tibet «Kinchuen» (2 rows), Rio Kan (2 rows incl. Matteo Ricci referido).

## Issue format (approved sample)
- **Title:** `Place — Person, year` (e.g. `Shaohing — Cyr Contancin, vows 1706`)
- **Body (English):** "Place to identify" (place name, type, date, source romanization, candidate guess if any) → "Person" (id, name, nationality, status) → "Places in the biography" (chronological markdown table: Date | Event | Place | Wikidata, with ❗️ on the missing one) → "Source note" (verbatim French/Latin quote from the `dehergne` obs) → "Task" (one line: add `@wikidata:Qxxx`).
- **Candidate guesses:** For the 11 rows with `candidate_id`, include as `Tentative: Qxxxxx (score 0.xx) — verify`.

## Execution steps
1. **Pull all biographies (read-only).** For each unique person id in Buckets B/C/D, run the dated-events SQL query against `dehergne.sqlite`. One Python script writes a dict `{person_id: {name, events:[(type,value,date,wd)]}}` cached to a local JSON for reuse.
2. **Draft locally** — generate one markdown file per new issue under `inferences/iloc-issues/<NN>-<place-slug>.md` (NN = sequence), plus `inferences/iloc-issues/INDEX.md` listing all 33 with status, and sections for Buckets A/B/C. Also write comment drafts under `inferences/iloc-issues/comments/issue-<N>.md` for Bucket C, and one bug-issue draft for row 1.
3. **Show the user the INDEX + 2-3 representative draft bodies** (one straightforward, one multi-person consolidated, one with a candidate guess) for final format sign-off.
4. **Create on GitHub** (only after user confirms the drafts):
   - `gh issue create --repo joaquimrcarvalho/dehergne-repertoire --label iloc --title ... --body-file ...` for each of the 33 new + 1 bug issue.
   - `gh issue comment <N> --repo ... --body-file ...` for the 4 Bucket-C comments.
   - Capture each created issue number and write it back into `INDEX.md`.
5. **Final report** to user: counts created/commented/skipped, links to the new issues, and the Bucket-A data-quality list for manual triage.

## Tooling notes
- Read-only source access (Excel via openpyxl, SQLite via sqlite3, `.cli` via grep for source notes) — no edits to source data.
- All GitHub writes via `gh` CLI (user already authenticated as `joaquimrcarvalho`, scopes include `repo`).
- No changes to `.cli` files or the database. Output artifacts live only under `inferences/iloc-issues/`.
- If any place turns out to already have a matching issue I missed, the dedup check (title + label `iloc` listing) runs again right before creation to prevent duplicates.