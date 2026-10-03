"""Biographical note generator (bilingual PT/EN).

Generates a prose biographical narrative from the structured timeline +
relations data produced by ``build_biography(model)``. See
``biographical_note_spec.md`` for the full specification.

Architecture (3 layers, per the spec):
  1. Engine      — walks the timeline, groups events, dispatches to templates
  2. Vocabulary  — database-specific templates + coded-value dictionaries
  3. Renderer    — joins sentences into paragraphs per language

The generator is reusable for other Timelink databases by swapping the
vocabulary tables (EVENT_TEMPLATES, CODED_VALUES, IDENTITY_ATTRIBUTES,
ITINERARY_TYPES, ROLE_PHRASES).
"""

import re
from collections import defaultdict

from dehergne_util import (
    build_biography,
    _note_for_bioitem,
    fetch_wikidata_labels,
    relation_label,
)
from timelink.kleio.utilities import format_timelink_date as _fmt_tl_date


# ---------------------------------------------------------------------------
# Layer 2: Vocabulary (Dehergne-specific)
# ---------------------------------------------------------------------------

# Event-type sentence templates. Placeholders:
#   {date}     formatted date string (may be empty for undated)
#   {place}    place name with modern label + wikilink
#   {value}    raw attribute value
#   {ship}     ship name (for embarkation)
#   {votos}    decoded vow label
#   {obs}      appended observation (source citation / note)
#   {em_place} / {in_place}: "em X" / "in X" (so we can omit place for unknown deaths)

EVENT_TEMPLATES = {
    "nascimento": {
        "pt": "Nasceu em {date} em {place}.{obs}",
        "en": "Born {date} in {place}.{obs}",
    },
    "morte": {
        "pt": "Faleceu em {date}{em_place}.{obs}",
        "en": "Died {date}{in_place}.{obs}",
    },
    "baptizado": {
        "pt": "Foi batizado em {date} em {place}.{obs}",
        "en": "Baptised {date} in {place}.{obs}",
    },
    "jesuita-entrada": {
        "pt": "Entrou na Companhia de Jesus em {place} em {date}.{obs}",
        "en": "Entered the Society of Jesus in {place} on {date}.{obs}",
    },
    "jesuita-ordenacao-padre": {
        "pt": "Foi ordenado padre em {place} em {date}.{obs}",
        "en": "Ordained priest in {place} on {date}.{obs}",
    },
    "jesuita-votos-local": {
        "pt": "Fez a profissão de {votos} em {place} em {date}.{obs}",
        "en": "Professed {votos} vows in {place} on {date}.{obs}",
    },
    "embarque": {
        "pt": "Embarcou para o Oriente no navio *{ship}* ({date}).{obs}",
        "en": "Embarked for the East on the ship *{ship}* ({date}).{obs}",
    },
    "chegada": {
        "pt": "Chegou a {place} ({date}).{obs}",
        "en": "Arrived in {place} ({date}).{obs}",
    },
    "partida": {
        "pt": "Partiu para {place} ({date}).{obs}",
        "en": "Departed for {place} ({date}).{obs}",
    },
    # free-text events: value is already a sentence fragment in PT
    "jesuita-cargo": {
        "pt": "{value} ({date}).{obs}",
        "en": "{value} ({date}).{obs}",
    },
    "cargo": {
        "pt": "{value} ({date}).{obs}",
        "en": "{value} ({date}).{obs}",
    },
    "jesuita-tarefa": {
        "pt": "{value} ({date}).{obs}",
        "en": "{value} ({date}).{obs}",
    },
    "tarefa": {
        "pt": "{value} ({date}).{obs}",
        "en": "{value} ({date}).{obs}",
    },
}

# Coded-value dictionaries (case-insensitive matching on the raw value)

VOWOS_LABELS = {
    "4V": {"pt": "quatro votos", "en": "four vows (professed)"},
    "3V": {"pt": "três votos", "en": "three vows (simple)"},
    "coadjutor espiritual": {"pt": "coadjutor espiritual",
                              "en": "spiritual coadjutor"},
    "coadjutor temporal": {"pt": "coadjutor temporal",
                            "en": "temporal coadjutor"},
    "professo": {"pt": "professo", "en": "professed"},
    "simples": {"pt": "votos simples", "en": "simple vows"},
}

ESTATUTO_LABELS = {
    "padre": {"pt": "Padre", "en": "priest (Father)"},
    "frade coadjutor": {"pt": "Irmão coadjutor", "en": "lay brother"},
    "escolástico": {"pt": "Escolástico", "en": "scholastic"},
    "noviço": {"pt": "Noviço", "en": "novice"},
    "frade": {"pt": "Irmão", "en": "brother"},
    "irmão donato": {"pt": "Irmão donato", "en": "donated brother"},
    "ex-jesuíta": {"pt": "Ex-jesuíta", "en": "former Jesuit"},
    "padre secular": {"pt": "Padre secular", "en": "secular priest"},
}

# Identity attributes (undated) — order matters for the opening line
IDENTITY_ATTRIBUTES = [
    ("nome-chines", {"pt": "nome chinês: {value}",
                      "en": "Chinese name: {value}"}),
    ("nome-japones", {"pt": "nome japonês: {value}",
                       "en": "Japanese name: {value}"}),
]

# Event types that get grouped into itinerary lists when consecutive
ITINERARY_TYPES = {"estadia"}

# Itinerary sentence templates (for grouped stays)
ITINERARY_TEMPLATE = {
    "pt": {"single": "Residiu em {items}.",
           "multi":  "Residiu em {items}."},
    "en": {"single": "Resided in {items}.",
           "multi":  "Resided in {items}."},
}

# Types that are reference IDs (not narrated as events, but may be footnoted)
REFERENCE_TYPES = {"wicky", "wicky-viagem"}

# Family role values that get a dedicated "Filho de X e de Y" sentence
FAMILY_ROLES = {"pai", "mae"}


# ---------------------------------------------------------------------------
# Layer 1: Engine
# ---------------------------------------------------------------------------

def _decoded_votos(value, lang):
    """Decode a jesuita-votos code to a display label."""
    if not value:
        return ""
    key = str(value).strip().lower()
    if key in VOWOS_LABELS:
        return VOWOS_LABELS[key][lang]
    return str(value)


def _decoded_estatuto(value, lang):
    """Decode a jesuita-estatuto value to a display label."""
    if not value:
        return ""
    key = str(value).strip().lower()
    if key in ESTATUTO_LABELS:
        return ESTATUTO_LABELS[key][lang]
    return str(value)


def _format_place(value, wd_qid, wd_labels, lang):
    """Format a place name for the narrative.

    The place name itself links to the local wikidata page (QID), so the
    link is associated with the name rather than shown as a separate visible
    token. When the modern Wikidata label differs from the transcribed
    value, it appears in parentheses after the link.

    Examples:
        [Coimbra](Q45412)
        [Cantão](Q16572) (Guangzhou)
        [Nan-tch'ang fou](Q171943) (Nanchang)
        Trancoso, diocese de Viseu      (no QID — plain text)
        (desconhecido)                  (value was '?')
    """
    if not value or str(value).strip() == "?":
        return "(desconhecido)" if lang == "pt" else "(unknown)"
    val = str(value).strip()
    if wd_qid:
        label_info = wd_labels.get(wd_qid, {})
        label = (label_info or {}).get("label")
        if label and label.lower() != val.lower():
            return f"[{val}]({wd_qid}) ({label})"
        return f"[{val}]({wd_qid})"
    return val


def _obs_suffix(obs, lang):
    """Format an obs/comment string as a parenthetical suffix."""
    obs = (obs or "").strip()
    if not obs:
        return ""
    # flatten newlines, escape pipe chars (for table compatibility if needed)
    obs = obs.replace("\n", " ").replace("|", "\\|").strip()
    if len(obs) > 200:
        obs = obs[:197] + "…"
    return f" ({obs})"


def _render_event_sentence(entry, lang, wd_labels, model, votos_lookup):
    """Render a single timeline entry as a sentence in the given language.

    Returns the sentence string, or '' if the type is not narrated.
    """
    t = entry["type"]
    # strip -x suffix for template lookup, mark as variant
    base_type = re.sub(r"-x$", "", t)
    is_variant = t != base_type

    if base_type in REFERENCE_TYPES:
        return ""  # not narrated

    template = EVENT_TEMPLATES.get(base_type)
    if not template:
        return ""  # unknown type — silently skip

    # compute date_str from the raw date
    raw_date = entry.get("date", "")
    date_str = ""
    if raw_date and raw_date not in ("0", "00"):
        try:
            date_str = _fmt_tl_date(raw_date)
        except Exception:
            date_str = str(raw_date)
    if is_variant and date_str:
        date_str += " (alt.)" if lang == "en" else " (var.)"

    value = entry.get("value") or ""
    place = _format_place(value, entry.get("wd_qid"), wd_labels, lang)
    obs = _obs_suffix(entry.get("obs", ""), lang)

    # build the em_place / in_place for morte (omits place if unknown)
    if value and str(value).strip() != "?":
        em_place = f" em {place}"
        in_place = f" in {place}"
    else:
        em_place = ""
        in_place = ""

    # decode votos for jesuita-votos-local
    votos = ""
    if base_type == "jesuita-votos-local" and votos_lookup:
        votos_decoded = votos_lookup.get(entry.get("date"))
        if votos_decoded:
            votos = votos_decoded.get(lang, "")
        if not votos:
            votos = "votos" if lang == "pt" else "vows"

    tpl = template.get(lang, template.get("en", ""))
    sentence = tpl.format(
        date=date_str,
        place=place,
        value=value,
        ship=value,
        votos=votos,
        obs=obs,
        em_place=em_place,
        in_place=in_place,
    )
    # collapse double spaces
    sentence = re.sub(r"  +", " ", sentence).strip()
    # fix " ." -> "."
    sentence = sentence.replace(" .", ".")
    return sentence


def _group_timeline(timeline):
    """Walk the timeline and produce a flat list of (kind, payload) items.

    Kinds:
      'event'    — a single timeline entry (with 'date' injected from group)
      'group'    — a list of consecutive entries of an ITINERARY_TYPE
    """
    items = []
    current_group = []
    group_type = None

    for grp in timeline:
        grp_date = grp.get("date", "")
        for entry in grp.get("entries", []):
            # inject the group's date into the entry (entries don't carry it)
            if "date" not in entry or entry["date"] is None:
                entry["date"] = grp_date
            t = entry.get("type", "")
            base = re.sub(r"-x$", "", t)
            if base in ITINERARY_TYPES:
                if group_type != base:
                    # flush previous group
                    if current_group:
                        items.append(("group", current_group))
                    current_group = [entry]
                    group_type = base
                else:
                    current_group.append(entry)
            else:
                # flush any open group
                if current_group:
                    items.append(("group", current_group))
                    current_group = []
                    group_type = None
                items.append(("event", entry))
    # flush trailing group
    if current_group:
        items.append(("group", current_group))

    return items


# ---------------------------------------------------------------------------
# Layer 3: Renderer
# ---------------------------------------------------------------------------

def _build_identity(model, bio, lang, wd_labels):
    """Build the opening identity line.

    Combines name + Chinese/Japanese name + nationality + Jesuit status.
    """
    parts = []
    name = model.get_description()
    parts.append(f"**{name}**")

    # identity attributes (Chinese name, etc.)
    for attr_type, label_tpl in IDENTITY_ATTRIBUTES:
        for grp in bio["timeline"]:
            if grp["date"] not in ("0", "00"):
                continue
            for e in grp["entries"]:
                if e["type"] == attr_type and e.get("value"):
                    parts.append(label_tpl[lang].format(value=e["value"]))

    # nationality
    nat = None
    estatuto = None
    for grp in bio["timeline"]:
        if grp["date"] not in ("0", "00"):
            continue
        for e in grp["entries"]:
            if e["type"] == "nacionalidade" and e.get("value"):
                nat = e["value"]
            if e["type"] == "jesuita-estatuto" and e.get("value"):
                estatuto = e["value"]

    # build the descriptive phrase
    desc_parts = []
    if nat:
        if lang == "pt":
            desc_parts.append(f"jesuíta de {nat}")
        else:
            desc_parts.append(f"Jesuit from {nat}")
    if estatuto:
        label = _decoded_estatuto(estatuto, lang)
        if label:
            desc_parts.append(label)
    if desc_parts:
        parts.append(", ".join(desc_parts))

    # join: "Name (Chinese name: X), jesuíta português, Padre."
    # the parenthetical identity attributes go in parens after the name
    main_name = parts[0]
    extras = parts[1:]
    if extras:
        # separate the parenthetical-name-extras from the descriptive parts
        paren_extras = []
        desc_extras = []
        for attr_type, _ in IDENTITY_ATTRIBUTES:
            for ex in list(extras):
                tpl_check = dict((a, l) for a, l in IDENTITY_ATTRIBUTES)
                if attr_type in tpl_check and any(
                    kw in ex for kw in ["nome chinês", "Chinese name",
                                        "nome japonês", "Japanese name"]):
                    paren_extras.append(ex)
                    extras.remove(ex)
        if paren_extras:
            desc_extras = extras
            identity = f"{main_name} ({'; '.join(paren_extras)})"
            if desc_extras:
                identity += f", {', '.join(desc_extras)}"
        else:
            identity = f"{main_name}, {', '.join(extras)}"
    else:
        identity = main_name

    return identity + "."


def _render_itinerary(entries, lang, wd_labels):
    """Render a group of stays as a single itinerary sentence."""
    items = []
    for e in entries:
        place = _format_place(e.get("value"), e.get("wd_qid"), wd_labels, lang)
        date_str = ""
        raw_date = e.get("date", "")
        if raw_date and raw_date not in ("0", "00"):
            try:
                date_str = _fmt_tl_date(raw_date)
            except Exception:
                date_str = str(raw_date)
        if date_str:
            items.append(f"{place} ({date_str})")
        else:
            items.append(place)
    items_str = ", ".join(items)
    return ITINERARY_TEMPLATE[lang]["multi"].format(items=items_str)


def _render_relations(relations, lang):
    """Render the relations as 1–2 sentences.

    Family relations (pai/mae) get a dedicated sentence.
    Other relations are listed.
    """
    if not relations:
        return ""

    family = []
    others = []
    for rel in relations:
        role = (rel.get("role") or "").strip().lower()
        if role in FAMILY_ROLES:
            family.append(rel)
        else:
            others.append(rel)

    sentences = []

    # family sentence
    if family:
        links = []
        for rel in family:
            name = rel.get("other_name", "?")
            oid = rel.get("other_id", "")
            links.append(f"[{name}]({oid})")
        if lang == "pt":
            role_word = "Filho de" if any(
                r.get("role", "").lower() == "pai" for r in family) else "De"
            sentences.append(f"{role_word} {' e de '.join(links)}.")
        else:
            role_word = "Son of" if any(
                r.get("role", "").lower() == "pai" for r in family) else "Of"
            sentences.append(f"{role_word} {' and '.join(links)}.")

    # other relations
    if others:
        items = []
        for rel in others:
            name = rel.get("other_name", "?")
            oid = rel.get("other_id", "")
            label = relation_label(rel)
            date_str = rel.get("date_str", "") or ""
            if date_str:
                items.append(f"[{name}]({oid}) ({label}, {date_str})")
            else:
                items.append(f"[{name}]({oid}) ({label})")
        if lang == "pt":
            sentences.append(
                f"Esteve ligado a {', '.join(items)}.")
        else:
            sentences.append(
                f"Connected to {', '.join(items)}.")

    return " ".join(sentences)


def _render_language(model, bio, grouped_items, wd_labels, lang, votos_lookup):
    """Render the full narrative for one language."""
    paragraphs = []

    # identity line
    identity = _build_identity(model, bio, lang, wd_labels)
    paragraphs.append(identity)

    # body sentences from grouped timeline
    body = []
    for kind, payload in grouped_items:
        if kind == "event":
            sentence = _render_event_sentence(
                payload, lang, wd_labels, model, votos_lookup)
            if sentence:
                body.append(sentence)
        elif kind == "group":
            body.append(_render_itinerary(payload, lang, wd_labels))

    if body:
        # join body into one paragraph (could split into multiple paragraphs
        # by event category in future; for now one paragraph)
        paragraphs.append(" ".join(body))

    # relations
    rel_sentence = _render_relations(bio.get("relations", []), lang)
    if rel_sentence:
        paragraphs.append(rel_sentence)

    return "\n\n".join(p for p in paragraphs if p)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_biographical_note(model, db=None, languages=("pt", "en")):
    """Generate a bilingual biographical note as a markdown string.

    Parameters:
        model       — the ORM entity (Person or REntity)
        db          — optional DB session (for REntity follow_identification)
        languages   — tuple of language codes to render (default PT + EN)

    Returns a markdown string with ``### Biographical note`` header and
    per-language subsections, or '' if there's not enough data.
    """
    bio = build_biography(model, follow_identification=(db is not None),
                          db=db)

    # collect all QIDs we'll need labels for
    qids = set()
    for grp in bio["timeline"]:
        for e in grp["entries"]:
            if e.get("wd_qid"):
                qids.add(e["wd_qid"])
    qids = list(qids)
    wd_labels = fetch_wikidata_labels(qids) if qids else {}

    # build a votos-lookup: date -> decoded votos label
    # (so jesuita-votos-local can reference the matching jesuita-votos)
    votos_lookup = {}
    for grp in bio["timeline"]:
        for e in grp["entries"]:
            if e["type"] == "jesuita-votos" and e.get("value"):
                date = e.get("date", "0")
                decoded = {}
                for lang in languages:
                    decoded[lang] = _decoded_votos(e["value"], lang)
                votos_lookup[date] = decoded

    # group the timeline into events + itinerary blocks
    grouped_items = _group_timeline(bio["timeline"])

    # render each language
    lang_sections = []
    lang_headers = {"pt": "Português", "en": "English",
                    "es": "Español", "fr": "Français"}
    for lang in languages:
        text = _render_language(model, bio, grouped_items, wd_labels, lang,
                                votos_lookup)
        if text.strip():
            header = lang_headers.get(lang, lang.title())
            lang_sections.append(f"## {header}\n\n{text}")

    if not lang_sections:
        return ""

    return "### Biographical note\n\n" + "\n\n".join(lang_sections)
