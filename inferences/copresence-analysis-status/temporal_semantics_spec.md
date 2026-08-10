# Specification: Temporal Semantics for Attribute Types

**Status:** Draft for discussion
**Purpose:** Define a general framework for classifying attribute types by their temporal meaning, so that interval-overlap analyses (co-presence, role succession, tenure) can be applied to any attribute — not just places.

---

## 1. Problem

The co-presence analysis currently hardcodes which attribute types are "stay events," "point events," or "terminating events." This is specific to places and to the Dehergne database.

But the same interval-overlap logic applies to many questions:

- **Place co-presence:** "Who was in Coimbra at the same time?" (current implementation)
- **Role succession:** "Who held the office of Superior of the China mission, and when did their tenures overlap?" (e.g., `jesuita-cargo`)
- **Status co-presence:** "Who was a novice at the same time?" (e.g., `jesuita-estatuto`)
- **Ship co-travel:** "Who was on the same voyage?" (e.g., `embarque` + `wicky-viagem`)

Each of these requires knowing, for a given attribute type:
- Does it **start** a period? (arrival, entering office)
- Does it **end** a period? (departure, death, term end)
- Is it a **point in time**? (vows ceremony, ordination)
- Does it imply a **duration** without explicit start/end? (a "stay" or "tenure")
- Is it a **status** with no temporal bounds? (nationality, gender)

## 2. Proposed classification

Each attribute type is assigned a **temporal role** from this enum:

| Role | Meaning | Interval behavior | Examples |
|---|---|---|---|
| `INTERVAL_START` | Begins a period of presence/tenure at a value | Creates/extends a segment | `chegada` (arrival), `jesuita-entrada` (entering), `nascimento` (birth) |
| `INTERVAL_END` | Terminates the current period | Closes any open segment | `partida` (departure), `embarque` (boarding), `morte` (death) |
| `INTERVAL` | Implies presence for a duration (start = date, end = next evidence of leaving) | Creates/extends a segment | `estadia` (stay), `estadia-x` (variant stay), `residencia` (residence) |
| `POINT` | Present on this date only; does not start or end a period | Absorbed if within a segment; same-day interval if standalone | `jesuita-votos-local` (vows location), `jesuita-ordenacao-padre` (ordination), `baptizado` (baptism) |
| `STATUS` | Ongoing condition, not a temporal event | Not used for interval computation | `nacionalidade`, `jesuita-estatuto`, `nome`, `sexo` |
| `REFERENCE` | An identifier, not an event | Not used for interval computation | `wicky`, `wicky-viagem` |

### Notes on the roles

- `INTERVAL` vs `INTERVAL_START`: An `INTERVAL` type (like `estadia`) implies the person was there for *some* time — we just don't know how long, so we estimate from the next event. An `INTERVAL_START` type (like `chegada`) explicitly marks the *beginning* of presence. In practice both create segments; the distinction matters for rendering ("arrived in X" vs "stayed in X").

- `INTERVAL_END` types close whatever segment is open, regardless of the end event's own value/QID. This is how `embarque` and `partida` work: they mean "the person left," not "the person is now at the ship/departure point."

- `POINT` types are crucial for ceremonies and milestones. They confirm presence without claiming the person lived there. A vows ceremony at Coimbra means "present on that day," not "residing in Coimbra."

## 3. Configuration: the temporal vocabulary

The classification is defined in a table that can be swapped for a different database. This is the Dehergne-specific vocabulary:

```python
TEMPORAL_ROLES = {
    # Places
    "estadia":              "INTERVAL",
    "estadia-x":            "INTERVAL",
    "chegada":              "INTERVAL_START",
    "partida":              "INTERVAL_END",
    "embarque":             "INTERVAL_END",
    "nascimento":           "INTERVAL_START",
    "morte":                "INTERVAL_END",
    "baptizado":            "POINT",
    "residencia":           "INTERVAL",

    # Jesuit career
    "jesuita-entrada":      "INTERVAL_START",
    "jesuita-votos-local":  "POINT",
    "jesuita-ordenacao-padre": "POINT",
    "jesuita-cargo":        "INTERVAL",       # holding an office
    "jesuita-tarefa":       "INTERVAL",       # a task assignment
    "jesuita-tarefa-x":     "INTERVAL",

    # Secular roles
    "cargo":                "INTERVAL",        # holding a civil/ecclesiastical office
    "tarefa":               "INTERVAL",        # a task

    # Non-temporal
    "nacionalidade":        "STATUS",
    "jesuita-estatuto":     "STATUS",
    "nome":                 "STATUS",
    "nome-chines":          "STATUS",
    "wicky":                "REFERENCE",
    "wicky-viagem":         "REFERENCE",
}
```

### Default role

Attribute types not listed in the table default to `STATUS` (not used for interval computation). This is safe — unclassified types are ignored rather than producing spurious intervals.

## 4. Application: place co-presence (current)

The existing co-presence analysis, reconfigured to use the temporal vocabulary:

- **Grouping key:** the `@wikidata` QID attached to the attribute value
- **Interval construction:** uses `INTERVAL`, `INTERVAL_START`, `INTERVAL_END`, `POINT` roles exactly as currently implemented
- **Result:** "who was at the same QID at the same time"

No change to the algorithm — just the vocabulary table replaces the hardcoded sets.

## 5. Application: role/office co-presence (new)

The same engine, reconfigured:

- **Grouping key:** the `(type, value)` pair — e.g. `("jesuita-cargo", "Superior da missão da China")` or `("cargo", "Bispo de Nanquim")`
- **Interval construction:** identical — `INTERVAL` types create segments, `POINT` types are absorbed/standalone
- **Result:** "who held the same office at the same time" → succession chains, overlap detection

Example query: "Who was Superior of the China mission, and when did their tenures overlap?"

This would produce a timeline/Gantt for the office, showing each holder's tenure as a bar — directly analogous to the place co-presence Gantt, but for roles.

### Value normalization for roles

Role values need light normalization to group equivalent offices:
- `Superior da missão da China` ≈ `Superior da missão da China` (exact match)
- `Bispo de Nanquim` ≈ `Bishop of Nanjing` (may need cross-language mapping)
- `Visitador` = `Visitador de todas as missões jesuítas das Índias` (subset/superset?)

For the first implementation, exact `(type, value)` matching is sufficient. A normalization layer can be added later.

## 6. Application: ship/voyage co-travel (new)

- **Grouping key:** `(wicky-viagem value)` — the fleet/voyage number
- **Interval construction:** `embarque` as `INTERVAL_END` (boarding = leaving port) + `chegada` as `INTERVAL_START` (arriving at destination). The voyage itself is the interval between embarkation and arrival.
- **Result:** "who was on the same ship/voyage"

This requires a different interval logic (voyage = `embarque date` to `chegada date`, not place-based). It's a future extension; the temporal vocabulary supports it but the interval engine would need a "voyage mode."

## 7. Architecture

```
temporal_semantics.py
├── TEMPORAL_ROLES          # the vocabulary table (configurable)
├── temporal_role(attr_type) → role enum
├── build_intervals(model, grouping_key="qid") → [Interval]
│   # generic: walks timeline, uses temporal roles to build segments
│   # grouping_key: "qid" for places, "(type,value)" for roles
├── detect_overlaps(intervals) → [Overlap]
│   # generic interval-overlap detection
└── render_overlaps(...)    # table + Gantt (reuses existing renderers)

copresence.py
├── (thin wrapper)
├── detect_copresence(persons) → calls build_intervals with grouping_key="qid"
└── detect_role_overlap(persons, office_type) → calls build_intervals with grouping_key="(type,value)"
```

The interval engine (`build_intervals`) becomes generic: it takes a temporal vocabulary + a grouping-key extractor, and produces intervals. The co-presence and role-overlap analyses are just different configurations of the same engine.

## 8. Migration path

1. **Extract `TEMPORAL_ROLES`** into a new `temporal_semantics.py` module.
2. **Refactor `copresence.py`** to import the vocabulary and use `temporal_role()` instead of hardcoded sets.
3. **Generalize `build_intervals`** to accept a `grouping_key` function.
4. **Add `detect_role_overlap`** as a new entry point.
5. **Add role-overlap sections** to the type-summary pages (e.g. the `jesuita-cargo.md` summary page shows a succession Gantt for each office).

No change to existing outputs until step 5 — steps 1–4 are pure refactoring.

## 9. Limitations

- **Value normalization** for roles (cross-language, subset/superset offices) is out of scope for v1.
- **The temporal vocabulary is manual.** It could eventually be derived from the Kleio structure file (`.str`), where each element could carry a `temporal_role` attribute. But that requires changes to the Kleio format spec.
- **Overlapping roles** (one person holding two offices simultaneously) produce multiple intervals at different keys — handled naturally by the engine.
