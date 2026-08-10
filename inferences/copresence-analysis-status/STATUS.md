# Temporal Semantics & Co-presence Analysis — Status

**Date:** 2026-08-04
**Session:** sess_a24850bc

## Overview

Two modules were built: a **generic temporal-semantics engine** (`temporal_semantics.py`) that classifies attribute types by their temporal meaning and builds stay/tenure intervals, and a **co-presence analysis** (`copresence.py`) that uses the engine to detect who was at the same place at the same time, with rendering (tables, Mermaid Gantt charts) and network export.

The design is modular: the engine depends only on the standard library, and the project-specific vocabulary (which attribute types mean what) is a swappable configuration table. The engine is intended for future inclusion in the timelink-py package.

## What was done

### 1. Temporal semantics engine (`temporal_semantics.py`)

A package-ready module implementing the classification described in `temporal_semantics_spec.md`.

**Core types:**
- `TemporalRole` — enum with 6 values:
  - `INTERVAL_START` — begins a period (e.g. `chegada`, `jesuita-entrada`)
  - `INTERVAL_END` — terminates the current period (e.g. `partida`, `embarque`, `morte`)
  - `INTERVAL` — implies presence for a duration (e.g. `estadia`, `jesuita-cargo`)
  - `POINT` — present on this date only (e.g. `jesuita-votos-local`, `jesuita-ordenacao-padre`)
  - `STATUS` — ongoing condition, not temporal (e.g. `nacionalidade`)
  - `REFERENCE` — an identifier (e.g. `wicky`, `wicky-viagem`)
- `TemporalVocabulary` — maps attribute type names → roles (with `-x` suffix stripping)
- `Interval` — data class for a stay/tenure interval
- `DEFAULT_VOCABULARY` — the Dehergne-specific vocabulary table

**Generic engine functions:**
- `build_intervals(timeline, person_id, person_name, vocabulary, grouping_fn)` — walks a person's timeline and produces intervals
  - `grouping_fn` parameter: determines what intervals group by
  - `_place_grouping_fn` (default) → groups by Wikidata QID → place co-presence
  - `role_grouping_fn` → groups by `(type, value)` → role/office succession
- `detect_overlaps(intervals)` — generic interval-overlap detection

**Interval estimation rules:**
- A stay starts at the date of any `INTERVAL`/`INTERVAL_START` event
- It ends at the earliest of: next `INTERVAL_END` event (`embarque`/`partida`), next event at a different grouping key, `morte` date, or `start + 15 years` cap (for persons with no death date)
- Consecutive same-key events merge into one segment
- `POINT` events are absorbed if within an existing segment, or create a same-day `[date, date]` interval if standalone
- Persons with return visits (Macau → Goa → Macau) produce multiple disjoint intervals
- Intervals longer than 30 years are flagged as potential data gaps

**Dependencies:** `re`, `enum`, `collections`, `typing` (stdlib only). No project-specific imports. Ready for `timelink.api` or `timelink.analysis`.

### 2. Co-presence analysis (`copresence.py`)

Thin wrapper over the temporal-semantics engine with project-specific features:

**Person normalization (partially linked databases):**
- `effective_id(model)` — implements `COALESCE(real_entity_id, occurrence_id)` in Python
- `normalize_persons(persons)` — deduplicates by effective_id (linked occurrences collapse)
- Applied at the entry point of all analyses

**Interval estimation:**
- `estimate_stay_intervals(model)` — calls `build_intervals` with the place grouping function and the default Dehergne vocabulary

**Overlap detection:**
- `detect_copresence(persons)` — normalizes persons, builds intervals, detects overlaps per QID
- Returns `{ qid: [copresence_pairs] }`

**Rendering outputs:**
1. **Co-presence table** — persons grouped by decade of overlap, on each QID wikidata page
2. **Mermaid Gantt chart** — all persons' stays at a place, full time range, rendered natively by Obsidian/GitHub
3. **NetworkX graph export:**
   - `build_copresence_network(persons)` → person-person graph (nodes=persons, edges=co-presence, weight=years overlapped)
   - `build_bipartite_network(persons)` → person-place graph (person nodes + place nodes, edges="stayed_at")
   - GraphML export for Gephi/Cytoscape
   - JSON export for Obsidian/D3

### 3. Results on the current sample (669 persons: Coimbra + Beijing + Macau + Goa + Lisboa + Évora)

| Place | QID | Co-presence pairs |
|---|---|---|
| Macau | Q14773 | 6,127 |
| Beijing | Q956 | 2,555 |
| Lisboa | Q597 | 1,171 |
| Goa | Q1171 | 518 |
| Coimbra | Q45412 | 389 |
| Évora | Q179948 | 76 |

| Network | Nodes | Edges |
|---|---|---|
| Person-person | 535 | 10,590 |
| Bipartite (person-place) | 550 persons + 576 places | 2,644 |

### 4. Specification documents

- `notebooks/temporal_semantics_spec.md` — full design spec: temporal roles, vocabulary, interval algorithm, applications (places, roles, voyages), architecture, migration path to timelink-py
- `notebooks/biographical_note_spec.md` — spec for the prose note generator

## What needs to be done

### Near-term (using existing engine)
- [ ] **Role/office succession analysis** — use `role_grouping_fn` to detect overlapping tenures of offices (`jesuita-cargo`, `cargo`). E.g. "who was Superior of the China mission at the same time" → Gantt chart of office holders on the type-summary page
- [ ] **Ship/voyage co-travel** — group by `wicky-viagem` to find who sailed on the same fleet. Requires a voyage-mode interval logic (embarkation → arrival)
- [ ] **Performance optimization** — for the full DB (2132 persons), the O(n²) overlap detection at Macau (~900 events) produces ~100K pairs. A sweep-line algorithm would reduce to O(n log n)
- [ ] **Open-interval handling** — persons with no death date (58.5% of DB) get capped at +15 years. This cap could be configurable or derived from last-known-activity
- [ ] **Interval quality flags** — surface flagged intervals (>30yr data gaps) in the UI for review
- [ ] **Network enrichment** — add nationality, birth/death dates, Jesuit status as node attributes for community detection
- [ ] **Temporal filtering** — "who was at Macau in the 1620s?" (date-range query on intervals)
- [ ] **Bipartite projection** — Gephi can project person-place to place-place (which places share the most people) or person-person (already have this)

### Future (requires timelink-py changes)
- [ ] **Package `temporal_semantics.py`** into `timelink.analysis` — the engine is stdlib-only and ready
- [ ] **`linked_entities` view** (issue #90) — replace the Python `effective_id()` with a DB-level COALESCE join
- [ ] **Complex date support** (issue #92) — `date_sort_value` as a numeric column for correct sorting of `>1580`/`<1623`/ranges
- [ ] **Temporal vocabulary in `.str` files** — define `temporal_role` as an attribute of Kleio structure elements so the vocabulary is data-driven, not hardcoded
- [ ] **`date_extra_info` consumption** — parse Kleio's JSON date metadata into structured columns at import time

### Methodological notes
- The co-presence is **"plausible overlap," not "definitely met."** Stay intervals are estimated from sparse dates (year-only, partial). The QID pages include a method note explaining this.
- **Point events** (vows, ordination) correctly register as same-day presences without implying long stays.
- **The interval cap** (+15 years for persons with no death date) prevents open-ended intervals from spuriously overlapping everyone later. This affects 58.5% of the DB.
- **Deduplication** via `effective_id` handles the partially-linked database correctly: linked occurrences (5% of persons) collapse to their real entity; unlinked persons (94%) are their own real entity.

## Files

```
notebooks/
├── temporal_semantics.py       ← generic engine (package-ready, stdlib only)
├── temporal_semantics_spec.md  ← design specification
├── copresence.py               ← co-presence analysis (wraps the engine)
└── dehergne_util.py            ← effective_id(), normalize_persons(), index/wikidata generators
```

## Network files (current sample)

```
inferences/markdown/samples/
├── copresence.graphml              ← person-person (535 nodes, 10,590 edges)
└── copresence_bipartite.graphml    ← person-place (550+576 nodes, 2,644 edges)
```
