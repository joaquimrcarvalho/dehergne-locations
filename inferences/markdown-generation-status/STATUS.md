# Markdown Template Generation — Status

**Date:** 2026-08-04
**Session:** sess_a24850bc

## What was done

Built a complete markdown-export pipeline that renders Timelink biographical records (Person + REntity) to Obsidian-compatible markdown with YAML frontmatter, bilingual biographical notes, structured timelines, linked index pages, and Wikidata place aggregation.

### Template architecture

```
templates/markdown/base/
├── entity_default_markdown.j2     ← entry point (switches to narrative)
├── entity_default_narrative.j2    ← main page structure
├── entity_frontmatter.j2          ← YAML frontmatter (Obsidian properties)
├── entity_bio_note.j2             ← bilingual biographical note (PT + EN)
├── entity_links_narrative.j2      ← identification/links table
├── entity_timeline_narrative.j2   ← timeline + relations + notes sections
├── entity_contains_narrative.j2   ← contained entities
└── (entity_attr_rel.j2, entity_links.j2, etc. — legacy/unused)
```

### Key features implemented

1. **YAML frontmatter** (Obsidian properties)
   - Entity metadata as queryable properties (id, description, class, source, sex, nome, etc.)
   - `real_person_ids` for Person records; `occurrences` for REntity records
   - None-safe: omits fields that are null (important for REntity)
   - Validated across all 2183 entities — 0 YAML parse errors

2. **Biographical note** (new section at top)
   - Bilingual PT + EN prose narrative generated from timeline + relations
   - Configurable vocabulary (templates per event type, per language)
   - Place names link to local wikidata pages: `[Coimbra](Q45412)`
   - Itinerary grouping (consecutive stays → single sentence)
   - Identity line (name + Chinese name + nationality + Jesuit status)
   - See `notebooks/biographical_note_spec.md` for the full spec

3. **Timeline table** (structured events)
   - Type column links to type-summary pages
   - Value column links to value__type index pages
   - Wikidata shown as local wikilinks: `→ [[Q171943]]`
   - Note column surfaces obs + value-comments + original wording + date-comments
   - Occ column (REntity only) links to the source occurrence
   - `@wikidata` companions merged onto single rows (positional pairing by year)

4. **Relations table**
   - Dated, sorted chronologically
   - Direction-aware (out/in) with human labels (Father, Mother, Companion, etc.)
   - Correct REntity relation resolution (origin checked against occurrence set)

5. **Notes section**
   - Generic (driven by `NOTE_TYPES = {"dehergne", "nota", "bibliografia"}`)
   - Triple-quotes and indentation cleaned from Kleio obs blocks

6. **Index pages** (in `index/` subfolder)
   - **value__type pages** (e.g. `Coimbra__jesuita-entrada.md`) — aggregate all persons sharing an attribute/value, deduped by effective_id, with chronological table
   - **type summary pages** (e.g. `estadia.md`) — all distinct values for a type with entity counts, linking to value pages
   - **wikidata/QID pages** (e.g. `Q45412.md`) — all romanization variants of a modern place unified, with variant list, single chronological table, co-presence section, Mermaid Gantt chart
   - Readable filenames (accents preserved, only `/` `:` stripped)
   - Type-based exclusion (`nome`, `nacionalidade`, `wicky` excluded from value pages)

7. **Co-presence analysis** (on QID pages + standalone network export)
   - Interval estimation from stay events (with embarque/partida as terminators)
   - Overlap detection between persons at the same place
   - Co-presence table grouped by decade
   - Mermaid Gantt chart (all persons, full time range)
   - NetworkX graph export (GraphML) — person-person and bipartite person-place

### Python modules

```
notebooks/
├── dehergne_util.py          ← core helpers (build_biography, effective_id,
│                                normalize_persons, index generators, wikidata
│                                label cache, wikidata page renderer)
├── biographical_note.py      ← bilingual prose generator
├── copresence.py             ← co-presence engine (wraps temporal_semantics)
├── temporal_semantics.py     ← generic interval engine (package-ready)
├── biographical_note_spec.md ← spec for the note generator
└── temporal_semantics_spec.md ← spec for temporal roles + interval engine
```

### Notebook

`notebooks/people-search-display.ipynb` (cell 8) — the export pipeline:
- Imports all generators + helpers
- Registers Jinja2 globals (build_biography, relation_label, value_link, type_link, generate_biographical_note)
- Expands persons with identification links
- Renders entity pages + index + wikidata + copresence network
- Configurable flags: `generate_index`, `follow_identification`

## What needs to be done

### Immediate (data quality / polish)
- [ ] **Duplicate Chinese names** in bio-note identity line when multiple `nome-chines` exist
- [ ] **Free-text tasks** (`jesuita-tarefa`) not translated to EN (passed through in PT)
- [ ] **Complex dates** (`>1580`, `<1623`, `1585:1589`) render as raw strings in bio notes (depends on timelink-py issue #92)
- [ ] **Long itineraries** (30+ stays like Ricci) produce a very long single paragraph — could split by decade
- [ ] **ROLE_LABEL_OUT["esposa"] = "Husband of"** bug in dehergne_util.py (should be "Wife of")

### Near-term
- [ ] **Role/office succession analysis** using `role_grouping_fn` — "who was Superior of the China mission at the same time"
- [ ] **Type-summary pages** for `jesuita-cargo` and `cargo` (currently only place types have summaries)
- [ ] **Mermaid Gantt for role succession** on cargo type-summary pages
- [ ] **Filtering** in the notebook: select persons by date range, place, nationality
- [ ] **Obsidian Dataview queries** to leverage the frontmatter properties

### Future (requires timelink-py changes)
- [ ] **`linked_entities` view** in timelink-py (issue #90) — would replace the Python `effective_id()` helper
- [ ] **Complex date support** in timelink-py (issue #92) — proper sorting + display of ranges/relative dates
- [ ] **`date_extra_info` consumption** in the importer — parse the Kleio JSON into structured columns
- [ ] **Temporal vocabulary in Kleio `.str` files** — define temporal roles at the source level so any project gets them automatically
- [ ] **Package `temporal_semantics.py`** into timelink-py (`timelink.analysis` or similar)

### Sample output location
```
inferences/markdown/samples/
├── *.md                         ← entity biography pages (755 in current sample)
├── copresence.graphml           ← person-person co-presence network
├── copresence_bipartite.graphml ← person-place bipartite network
└── index/
    ├── *.md                     ← value__type index pages (2278)
    ├── estadia.md, nascimento.md, ...  ← type summary pages (6)
    └── wikidata/
        ├── Q45412.md            ← Coimbra (389 co-presence pairs)
        ├── Q956.md              ← Beijing (2555 pairs)
        ├── Q14773.md            ← Macau (6127 pairs)
        ├── Q1171.md             ← Goa (518 pairs)
        ├── Q597.md              ← Lisboa (1171 pairs)
        ├── Q179948.md           ← Évora (76 pairs)
        └── ...                  ← 645 total wikidata pages
```
