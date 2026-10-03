# Specification: Biographical Note Generator

**Status:** Draft
**Purpose:** Define a reusable approach for generating bilingual (or multi-lingual) prose biographical notes from structured prosopography data in a Timelink database. The spec is database-agnostic: any Timelink-based project can adapt it by providing its own vocabulary tables and templates.

---

## 1. Overview

A **biographical note** is a short narrative (1–4 paragraphs) that summarizes a person's life from their structured attributes and relations. It is generated automatically from the same data that populates the Timeline and Relations tables, rendered as readable prose rather than a table.

The note is inserted at the top of the entity's markdown page, before the structured Timeline. It gives a reader the "story" at a glance; the tables below provide detail and links.

### Design principles

1. **Data-driven, not rule-per-person.** The generator walks the timeline once and emits sentences based on attribute *type*. No hand-written biography per person.
2. **Vocabulary is configurable.** Event-type templates, coded-value labels, and identity attributes are defined in tables that can be swapped for a different database, language, or source tradition.
3. **Bilingual / multilingual.** The generator produces parallel sections (e.g. PT + EN) from the same data. Adding a language means adding a column of templates, not rewriting the engine.
4. **Links preserved.** Place names, persons, and QIDs in the prose carry the same markdown links as the Timeline tables, so the narrative is navigable.
5. **Faithful to source.** The transcribed value (romanization, original wording) is the primary form shown; the modern/wikidata name appears in parentheses when it differs. Source comments (`obs`) are appended to the relevant sentence.

---

## 2. Inputs

The generator consumes the output of `build_biography(model)` (see `dehergne_util.py`), which returns:

```
{
  timeline: [ { date, entries: [ { type, value, obs, wd_qid, wd_url,
                                   source_entity, occ_num, bioitem } ] } ],
  relations: [ { rel_type, role, direction, other_id, other_name,
                 date, date_str, obs } ],
  notes: [ { type, value, obs, source_entity } ],
  is_real_entity: bool,
  occurrences_map: { occ_id: { num, id, name } },
  real_person_ids: [str],
}
```

It also needs:
- The model object (for identity attributes: name, nationality, status).
- Access to the Wikidata label cache (for place-name resolution).
- A `db` session if place-name resolution requires fetching labels.

---

## 3. Architecture

The generator is split into three layers:

### Layer 1 — Engine (database-agnostic)
Walks the timeline chronologically, groups consecutive events of the same type, and dispatches each event to a template lookup. Produces a list of "sentence groups" (one per event type or itinerary block).

```
engine(timeline, vocabulary) -> [SentenceGroup]
```

A `SentenceGroup` is `{ type, sentences: [{lang: str}] }` — each event produces one sentence per language.

### Layer 2 — Vocabulary (database-specific, configurable)
A `Vocabulary` object/table holding:
- `EVENT_TEMPLATES`: maps attribute type → sentence template per language.
- `CODED_VALUES`: maps coded values (e.g. vow codes, status) → display labels per language.
- `IDENTITY_ATTRIBUTES`: which undated attributes form the opening identity line and in what order.
- `ITINERARY_TYPES`: which event types should be grouped into itinerary lists (e.g. `estadia`).
- `ROLE_LABELS`: maps relation roles → labels per language and direction (reuses the existing `ROLE_LABEL_OUT`/`ROLE_LABEL_IN` maps).

### Layer 3 — Renderer (language-specific)
Joins sentence groups into paragraphs per language, inserts links, formats place names, and produces the final markdown sections.

```
render(sentence_groups, identity, relations, languages) -> markdown_string
```

---

## 4. Vocabulary configuration

This is the part a new project overrides. Below is the Dehergne-specific vocabulary; a different database provides its own.

### 4.1 Event templates

Each template is a dict `{lang: template_string}` with placeholders:
- `{date}` — formatted date
- `{place}` — place name with modern label + link
- `{value}` — the raw attribute value
- `{obs}` — appended observation/note
- `{ship}` — ship name (for embarkation)

| Type | PT | EN |
|---|---|---|
| `nascimento` | `Nasceu em {date} em {place}.` | `Born {date} in {place}.` |
| `morte` | `Faleceu em {date}{em_place}.` | `Died {date}{in_place}.` |
| `baptizado` | `Foi batizado em {date} em {place}.` | `Baptised {date} in {place}.` |
| `jesuita-entrada` | `Entrou na Companhia de Jesus em {place} em {date}.` | `Entered the Society of Jesus in {place} on {date}.` |
| `jesuita-ordenacao-padre` | `Foi ordenado padre em {place} em {date}.` | `Ordained priest in {place} on {date}.` |
| `jesuita-votos-local` | `Fez a profissão de {votos} em {place} em {date}.` | `Professed {votos} vows in {place} on {date}.` |
| `embarque` | `Embarcou para o Oriente no navio *{ship}* ({date}).` | `Embarked for the East on the ship *{ship}* ({date}).` |
| `chegada` | `Chegou a {place} ({date}).` | `Arrived in {place} ({date}).` |
| `partida` | `Partiu para {place} ({date}).` | `Departed for {place} ({date}).` |
| `jesuita-cargo` | `{value} ({date}).` | `{value} ({date}).` |
| `cargo` | `{value} ({date}).` | `{value} ({date}).` |
| `jesuita-tarefa` | `{value} ({date}).` | `{value} ({date}).` |
| `tarefa` | `{value} ({date}).` | `{value} ({date}).` |

Variants (`-x` suffix) reuse the base template; an "(alt.)"/"(var.)" marker is appended to the date.

### 4.2 Coded-value dictionaries

For types whose `value` is a code rather than free text:

**`jesuita-votos`** (vow code → label):

| Code | PT | EN |
|---|---|---|
| `4V` | `quatro votos` | `four vows (professed)` |
| `3V` | `três votos` | `three vows (simple)` |
| `Coadjutor Espiritual` | `coadjutor espiritual` | `spiritual coadjutor` |
| `Coadjutor Temporal` | `coadjutor temporal` | `temporal coadjutor` |

Case-insensitive matching; unknown codes fall back to the raw value.

**`jesuita-estatuto`** (status → label), used in the identity line:

| Value | PT | EN |
|---|---|---|
| `Padre` | `Padre` | `priest (Father)` |
| `Frade Coadjutor` / `Frade coadjutor` | `Irmão coadjutor` | `lay brother` |
| `Escolástico` | `Escolástico` | `scholastic` |
| `Noviço` | `Noviço` | `novice` |
| `Irmão donato` | `Irmão donato` | `donated brother` |

### 4.3 Identity attributes (undated, opening line)

The opening sentence combines selected undated attributes in a fixed order:

| Order | Attribute | PT label | EN label |
|---|---|---|---|
| 1 | `nome` (or description) | (the name itself) | (the name itself) |
| 2 | `nome-chines` | `nome chinês: {value}` | `Chinese name: {value}` |
| 3 | `nacionalidade` | `{value}` (adjective form) | `{value}` (adjective form) |
| 4 | `jesuita-estatuto` | `{coded_label}` | `{coded_label}` |

Example: `**António de Almeida** (nome chinês: Mei Ngan-tong Li-Sieou), jesuíta português, Padre.`

### 4.4 Itinerary grouping

Event types listed in `ITINERARY_TYPES` (default: `["estadia"]`) are grouped when ≥ 2 consecutive events of that type appear. The group renders as a single sentence with a comma-separated list:

- PT: `Residiu em Macau (1585), Cantão (1585), Shaoshing (1586).`
- EN: `Resided in Macau (1585), Canton (1585), Shaoshing (1586).`

Non-consecutive stays (interrupted by other events) start a new group.

### 4.5 Role labels (relations)

Reuses the existing `ROLE_LABEL_OUT` / `ROLE_LABEL_IN` dicts from `dehergne_util.py` for the EN side. The PT side uses the raw role value (the source is already in Portuguese).

Family relations (`pai`, `mae`) get a dedicated sentence: "Filho de X e de Y." / "Son of X and Y."

Non-family relations are listed: "Esteve ligado a X (role, date), Y (role, date)." / "Connected to X (role, date), Y (role, date)."

---

## 5. Place-name formatting

A `format_place(value, wd_qid, labels, lang)` helper produces:

| Condition | Output |
|---|---|
| value present, QID present, label differs from value | `«{value}» ({label}) [[{qid}]]` |
| value present, QID present, label matches/absent | `«{value}» [[{qid}]]` |
| value present, no QID | `«{value}»` |
| value is `?` | `(unknown)` / `(desconhecido)` |

The wikilink `[[{qid}]]` resolves to the local wikidata index page.

---

## 6. Output structure

```markdown
### Biographical note

## Português

{identity line}

{formation paragraph: entry, ordination, vows}

{voyage + arrival paragraph: embarkation, arrival}

{itinerary paragraph: grouped stays}

{offices/tasks paragraph}

{death sentence}

{relations sentence(s)}

## English

{parallel English text}
```

Empty paragraphs (no data for that event type) are omitted. A minimal person (only birth + death) produces 2 sentences per language.

---

## 7. Adapting to a different database

To reuse this generator for a different Timelink project:

1. **Provide a `Vocabulary`** with the project's event types, coded values, and identity attributes. This is a single Python dict/dataclass.
2. **Provide language templates** for each event type in the project's source language + target language(s).
3. **Set `ITINERARY_TYPES`** to whatever attribute represents residence/stay in that project.
4. **Set `IDENTITY_ATTRIBUTES`** to the undated attributes that form the opening line.
5. The engine, renderer, and place-name formatter are reused unchanged.

Example: a database of Portuguese merchants (not Jesuits) would replace `jesuita-entrada` with `entrada-empresa`, `jesuita-estatuto` with `cargo-empresa`, and drop the vows/ordination templates entirely.

---

## 8. Limitations and future work

- **Date quality.** Complex dates (`>1580`, `<1623`, `1585:1589`) are not yet properly sorted or rendered (tracked in timelink-py issue #92). Until then, the narrative uses the raw `the_date` string, which may produce "Born in <1623" rather than "Born before 1623".
- **Free-text events.** Types like `jesuita-tarefa` carry full sentence fragments ("Abre a missão do Carnate"). These are passed through verbatim; no grammar correction is attempted.
- **Dedup on REntity.** When generating for an `REntity`, events from multiple occurrences may duplicate. The generator should apply the same dedup as the index pages.
- **Gender.** The generator currently uses masculine forms ("Born", "Nasceu"). If the database includes female persons, a `sex` field on the model should drive pronoun/adjective agreement.
