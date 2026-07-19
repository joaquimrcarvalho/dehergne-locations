# Dehergne Répertoire — Project Analysis Report

> Generated: 2026-07-13
> Branch analyzed: `mbook-air`
> Tools: filesystem inspection, git history, Kleio source parsing

## What this project is

A **digital humanities / prosopography** project: a structured, queryable transcription of Joseph Dehergne's *Répertoire des Jésuites de Chine de 1552 à 1800* (1973), the standard biographical dictionary of Jesuit missionaries in China. It's built on **Timelink** (historical DB system) using **Kleio notation** as the transcription language, with Python/Jupyter for analysis. Part of the Macao Polytechnic University research project *"Linking the West and the East…"* (RP/CIPFIC-01/2023).

## Scale of the dataset (measured from the sources)

| Metric | Count |
|---|---|
| `.cli` source files | 29 (a–z + abbreviations + 1644/1701 location maps) |
| Total lines transcribed | ~29,300 |
| Distinct persons (`n$`) | **973** main entries |
| Referenced persons (`referido$`) | **850** |
| `mesmo_que` / `xmesmo_que` identity links | 69 |
| Life-story attributes (`ls$`) | ~18,800 |
| Distinct Wikidata place IDs linked | **1,106** |

**Top attribute types**: `estadia` (stay, 3,636), `dehergne` (full text, 1,435), `jesuita-estatuto` (1,327), `nacionalidade` (1,120), `nascimento` (1,012), `morte` (886), `embarque` (781), `wicky`/`wicky-viagem` (voyage fleet reconstruction).

**Nationalities (top)**: Portugal 431, France 184, China 177, Italy 125, Spain 43 — consistent with Dehergne's stated scope (French mission + Macau/Goa procurators).

## Architecture & workflow

```
sources/*.cli  ──[Kleio server 12.9]──▶  .xml/.rpt/.err  ──[import]──▶  SQLite
   (transcription)                                              │
identifications/  ◀──────────── entity resolution (.idf) ────────┤
inferences/  ──◀  Excel/CSV/markdown exports + maps  ◀────────── Jupyter notebooks
```

Four-phase pipeline (transcription → translation → importation → identification), as documented in both AGENTS.md and the Qoder Repowiki. All Kleio `.err` files report **0 errors / 0 warnings** — the corpus is in a clean, validated state. Database: 52 MB SQLite (`dehergne.sqlite`), ~33k entities / ~27k attributes.

## Documentation assets (3 overlapping layers)

1. **`AGENTS.md`** — accurate, current, well-structured agent/workspace instructions (10 KB). Matches the actual repo.
2. **`.github/copilot-instructions.md`** — older, leaner variant; partly references a fork name ("Dehergne-Locations") and lists notebooks that no longer exist (e.g. `location-analysis.ipynb`, `location-analysis-cleaned.ipynb`).
3. **`.qoder/repowiki/`** — an auto-generated, sourced wiki (~35 markdown docs across Project Overview, Processing Pipeline, Transcription System, Data Enrichment, Analysis Tools, Best Practices, Contribution Guidelines). Well-cited with `file://` references; committed at `2232767 "Qoder repowiki added"`.

These three overlap heavily. They're consistent in substance but **diverge on notebook filenames**, which is the main drift.

## Analysis tooling

Notebooks are the primary interface (`notebooks/README.md` is a good index). Key ones: `9-tutorial.ipynb`, `dehergne_analysis.ipynb`, `location-analysis-new.ipynb`, `jesuit-networks.ipynb`, `wicki-viagens.ipynb`, `wikidata-linked-data.ipynb`, `residences.ipynb`. Shared helpers live in `dehergne_util.py` (wikidata/coordinate extraction, age calc) — clean, well-tested-looking code. Two standalone itinerary-map generators (`inferences/Itineraries/*.py`) produce Folium HTML maps (Bento de Góis, Dionisio Ferreira).

## Issues worth flagging

1. **🔴 Accidental home-directory leak committed to repo.** A literal `~/` directory exists at repo root (committed in `bda3ae9 "Update settings"`) containing `~/Library/Application Support/opencode/opencode.json` — an MCP config for a `zotero-mcp` server. This is junk from a `~` that wasn't shell-expanded. Not in `.gitignore`. Should be removed from history (or at least `git rm`'d and gitignored).

2. **✅ RESOLVED (2026-07-13) — `.kleio.json` admin tokens purged from history.**
   - **Scope found:** `.kleio.json` was tracked before being gitignored, across **18 commits**, containing **17 distinct historical `kleio_admin_token` values** (Kleio regenerates the token on every server setup). An additional **2 older tokens** had leaked in full into committed notebook outputs (`nacionality_analysis.ipynb`, `dehergne_analysis.ipynb`) — Timelink's `print_info()` truncates tokens to 5 chars + `...` in most notebooks, but these two captured the full 32-char string.
   - **Total secret values purged: 19** (17 from `.kleio.json` + 2 from notebook output).
   - **Action taken:** `git filter-repo` with (a) `--paths-from-file --invert-paths` to remove `.kleio.json` and `sources/.kleio.json` from every commit, then (b) `--replace-text` to redact all 19 token strings + the `kleio_admin_token` key name → `***REMOVED-KLEIO-TOKEN***` / `***REMOVED***` across all history (1212 commits).
   - **Verification (all clean):** `kleio_admin_token` string count in all history = **0**; all 19 token values = **not findable** via `git log -S`; 37 redaction markers landed; `.kleio.json` paths absent from every commit; working `.kleio.json` files restored to disk (Kleio needs them) and remain gitignored.
   - **Remotes:** filter-repo strips remotes; all three (`origin`, `locations`, `template`) were re-added — **without** the embedded GitHub PAT that was previously in the `origin` URL (`https://mhk-timelink:ee2bd4…@github.com/…`). That PAT is now removed from local git config.
   - **Not done (by design — user decision):** no force-push. The tokens remain in the remote history on `origin/main` and the `locations` fork. Since these are localhost-only Kleio tokens (`http://localhost:8088`) and Kleio auto-rotates them, risk is low. **Live token rotation = restart the Kleio server** (it generates a fresh token on setup).
   - **⚠️ Side effect to be aware of:** history rewrite changed ~all commit SHAs. Any other local clone of this repo will need a fresh `git clone` (or `git fetch && git reset --hard`) — `git pull` will diverge.

3. **🟡 Documentation drift on notebook names.** `notebooks/README.md` and `copilot-instructions.md` reference `location-analysis.ipynb` and `location-analysis-cleaned.ipynb`, but the actual files are `location-analysis-new.ipynb` plus two `*-deprecated.ipynb`. Newcomers will hit dead links.

4. **🟡 Notebook output bloat.** `residences.ipynb` is **11 MB**, `jesuit-entry.ipynb` and `jesuit-networks.ipynb` ~1 MB each — full HTML/rendered output committed. `.html` and `.dot` are gitignored but `.ipynb` outputs are not. Consider `nbstripout` or a clear "clear outputs before commit" policy.

5. **🟢 `.python-version` says 3.12.11** — consistent with AGENTS.md. `.venv/` is correctly gitignored.

6. **🟢 Stray files**: `notebooks/-- SQLite.sql` (leading dashes — awkward to handle on CLI), several `.old` Kleio backups in `sources/` (gitignored, so harmless), `notebooks/throttle.ctrl`, `notebooks/apicache/`.

7. **🟢 Branch hygiene**: working branch is `mbook-air`; many stale local branches (`temp`, `2025-09-23-code-review`, etc.) and 4 remotes (`origin`, `locations`, `template`, …). The only uncommitted change is a routine re-run of `0-kleio-files.ipynb` (new container name/token, attribute count 26837→26835) — **noise, not a real edit**.

## Strengths

- Corpus is **clean and validated** (zero Kleio errors across all files).
- **Strong linked-data layer**: 1,106 distinct Wikidata IDs + GeoNames links + a dedicated locations fork (`dehergne-locations`).
- **Enrichment beyond the source**: fleet-number recovery from Wicki/Boxer turns isolated entries into travel-companion networks — a genuinely valuable scholarly contribution.
- Documentation is genuinely good and multi-layered; AGENTS.md in particular is accurate and useful for agents.
- Clear licensing (CC BY-NC-SA 4.0 for data, MIT for Timelink).

## Suggested next steps

1. ✅ **DONE (2026-07-13)** — `~` leak removed from disk and history; `~/` added to `.gitignore`.
2. ✅ **DONE (2026-07-13)** — Kleio admin tokens purged from local history (19 values + key name); `.kleio.json` untracked and restored to disk; embedded GitHub PAT removed from `origin` remote URL. **Outstanding owner actions:**
   - **Rotate the live Kleio token** by restarting the Kleio server (it auto-generates a new token on setup).
   - **Rotate/revoke the GitHub PAT** (`ee2bd4…`) that was embedded in the `origin` URL — it's no longer in local git config but may still be valid on GitHub. Re-authenticate via git credential helper or SSH.
   - **Decide on remotes:** local history no longer matches `origin`/`locations` (SHAs diverged after rewrite). If you want the purge reflected on GitHub, force-push (`git push --force origin main` etc.); otherwise the tokens remain in remote history only.
3. Sync notebook names in `notebooks/README.md` + `copilot-instructions.md` to reality (and decide whether the three "deprecated/old/original" variants should be archived or deleted).
4. Add `nbstripout` (pre-commit) to stop committing 11 MB of notebook output. *(Note: token leak into notebook output would not have happened if outputs were stripped — strong argument for adopting this.)*
