#!/usr/bin/env python3
"""
Generate local draft issues + INDEX.md from data.json.

Categorization (per approved plan):
  A: data-quality / non-toponym -> report only (+ 1 bug issue for date-in-place-field)
  B: existing OPEN issue         -> skip
  C: existing issue, add comment -> draft a comment
  D: NEW                         -> draft a new issue (group multi-person places)

Output: inferences/iloc-issues/
  NN-<slug>.md         (new issue drafts, Bucket D)
  bug-*.md             (bug issue draft, Bucket A row 1)
  comments/issue-<N>.md (Bucket C comment drafts)
  INDEX.md
"""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path("/Users/jrc/mhk-home/sources/dehergne")
OUT = ROOT / "inferences/iloc-issues"
COMMENTS = OUT / "comments"
COMMENTS.mkdir(exist_ok=True)

DATA = json.loads((OUT / "data.json").read_text())
ROWS = DATA["rows"]
PERSONS = DATA["persons"]

# attribute types that carry an actual place (shown in the chronological itinerary)
PLACE_TYPES = {
    "nascimento", "morte", "estadia", "chegada", "partida",
    "jesuita-entrada", "jesuita-votos-local", "jesuita-ordenacao-padre",
}

# ---------------------------------------------------------------------------
# Categorization tables (derived from cross-referencing against the 34 existing
# issues at joaquimrcarvalho/dehergne-repertoire)
# ---------------------------------------------------------------------------

# Bucket A: data-quality / non-toponym rows -> skip creating location issues
BUCKET_A = {
    1:  ("date leaked into place field", "BUG"),
    24: ("'Mogor' generic region (Mughal empire), not a single toponym", "SKIP"),
    28: ("'Oriente' generic region 'the East', not a toponym", "SKIP"),
    58: ("'apud Sinas' = 'among the Chinese' (generic), not a toponym", "SKIP"),
    60: ("'À missão' = 'to the mission' (generic), not a toponym", "SKIP"),
}

# Bucket B: existing OPEN issue already tracks this place -> skip
# key = row number (1-based as shown to user), value = (place, issue#)
BUCKET_B = {
    2:  ("Aquilon", 25),
    3:  ("Aquilon", 25),
    4:  ("Ascitano", 6),
    6:  ("Chang-tsin do Yüansi, Hou-pei", 29),
    7:  ("Chayüankow, Hukwang", 4),
    8:  ("Choui tcheou San Kia", 27),
    12: ("Katsusa, Japão", 18),
    13: ("Katsusa, Japão", 18),
    14: ("Ko-li-tsem do Kiating, Kiangnan", 33),
    15: ("Ko-li-tsem do Kiating, Kiangnan", 33),
    23: ("Missão dos Rios de Cuama", 28),
    44: ("Tarahumaras, México", 14),
    45: ("Tarahumaras, México", 14),
}

# Bucket C: existing (possibly closed) issue -> add a comment, no new issue
# key = row number, value = (place, issue#, note)
BUCKET_C = {
    5:  ("Chang-si", 30, "issue #30 (closed) discusses Chan-si / Q46913 vs Q47974"),
    19: ("Lofeu", 2, "issue #2 (closed) - new person context (Romain Hinderer)"),
    20: ("Lofeu", 2, "issue #2 (closed) - new person context (Romain Hinderer)"),
    36: ("Rio Kan", 0, "no exact issue; treat as NEW instead (see note)"),  # promote to D
    11: ("Kasuza, Arima, Japão", 18, "issue #18 is about Katsusa; Kasuza/Arima may be distinct -> NEW"),
    # 33 Pe-pou -> check
}

# Promote row 11 (Kasuza, Arima) and 36 (Rio Kan) to NEW since they are distinct
# from the existing issues; remove from C.
for rn in (11, 36):
    BUCKET_C.pop(rn, None)

# Remaining genuine Bucket C (comment on existing issue)
BUCKET_C_FINAL = {
    5:  ("Chang-si", 30),
    19: ("Lofeu", 2),
    20: ("Lofeu", 2),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[«»\"'(),]", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:50] or "place"

def row_num(r):
    return ROWS.index(r) + 1

EVENT_LABEL = {
    "nascimento": "birth",
    "morte": "death",
    "estadia": "stay",
    "chegada": "arrival",
    "partida": "departure",
    "embarque": "embarkation",
    "jesuita-entrada": "entered Jesuits",
    "jesuita-votos": "vows",
    "jesuita-votos-local": "vows location",
    "jesuita-ordenacao-padre": "ordination",
    "jesuita-ordenacao": "ordination",
    "jesuita-cargo": "office",
    "cargo": "office",
    "tarefa": "task",
    "jesuita-tarefa": "task",
    "wicky": "Wicki #",
    "wicky-viagem": "fleet #",
}

TYPE_LABEL = {
    "estadia": "stay (estadia)",
    "jesuita-votos-local": "vows location (jesuita-votos-local)",
    "morte": "death (morte)",
    "chegada": "arrival (chegada)",
}

def md_escape(s):
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()

def itinerary_table(pid, target_places=None, target_place=None,
                    target_type=None, target_date=None):
    """Markdown chronological table of dated place events.

    Rows whose place value is in `target_places` (a set of normalized place
    strings) OR matches (target_place, target_type, target_date) are marked
    with the ❗️ missing marker.
    """
    p = PERSONS.get(pid)
    if not p:
        return f"_(person {pid} not found)_\n"
    # normalize the target set for robust matching
    target_set = set()
    if target_places:
        target_set = {normalize_place(tp) for tp in target_places}
    if target_place:
        target_set.add(normalize_place(target_place))
    seen = set()
    lines = ["| Date | Event | Place | Wikidata |",
             "|------|-------|-------|----------|"]
    for e in p["events"]:
        t = e["type"]
        if t not in PLACE_TYPES:
            continue
        val = e["value"] or ""
        if not val or val == "?":
            continue
        key = (t, val, e["date"])
        if key in seen:
            continue
        seen.add(key)
        date = e["date_fmt"] or "—"
        label = EVENT_LABEL.get(t, t)
        wd = e["wikidata"]
        is_target = (normalize_place(val) in target_set
                     and (target_type is None or t == target_type)
                     and (target_date is None or e["date"] == target_date))
        if not target_set:
            is_target = False
        wdcell = f"❗️ **missing**" if is_target else (wd if wd else "—")
        place_cell = f"**{md_escape(val)}**" if is_target else md_escape(val)
        lines.append(f"| {date} | {label} | {place_cell} | {wdcell} |")
    return "\n".join(lines) + "\n"

def person_header(pid):
    p = PERSONS.get(pid, {})
    name = p.get("name", pid)
    parts = [f"**{name}** (`{pid}`)"]
    extra = []
    if p.get("status"):
        extra.append(p["status"])
    if p.get("nationality"):
        extra.append(p["nationality"])
    if p.get("chinese_name"):
        extra.append(f"Chinese name: {p['chinese_name']}")
    if p.get("groupname") == "referido":
        extra.append("**referido** (person referenced, not the missionary)")
    deh = next((e["value"] for e in p.get("events", [])
                if e["type"] == "dehergne"), "")
    if deh:
        extra.append(f"Dehergne P. {deh}")
    if extra:
        parts.append(" · ".join(extra))
    return " — ".join(parts)

def source_note(pid, place):
    """Extract the relevant snippet from the dehergne obs for context.

    Finds the first occurrence of the place (or a fragment of it) in the
    verbatim biography and returns a ~400-char window around it, rather than
    trying to split into sentences (French abbreviations like 'janv.', 'prov.',
    'P.' defeat naive sentence splitting).
    """
    p = PERSONS.get(pid, {})
    bio = p.get("bio", "")
    if not bio:
        return ""
    # pick a search fragment: prefer the part before the first comma, minus
    # guillemets/quotes; ensure it's at least 4 chars
    frag = place.split(",")[0].strip()
    frag = re.sub(r"[«»\"'\(\)]", "", frag).strip()
    candidates = [frag]
    if len(frag) < 4:
        candidates = [place]
    # also try words from the place
    words = [w for w in re.sub(r"[«»\"'\(\),]", " ", place).split() if len(w) >= 4]
    candidates += words
    low = bio.lower()
    pos = -1
    for c in candidates:
        if c:
            pos = low.find(c.lower())
            if pos >= 0:
                break
    if pos < 0:
        # no match: return the first 400 chars
        snippet = bio[:400]
    else:
        start = max(0, pos - 150)
        end = min(len(bio), pos + 350)
        snippet = bio[start:end]
        if start > 0:
            snippet = "…" + snippet
        if end < len(bio):
            snippet = snippet + "…"
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet

def candidate_line(rec):
    cid = rec.get("candidate_id")
    cname = rec.get("candidate_name")
    score = rec.get("match_score")
    if cid:
        sc = f"{float(score):.2f}" if score else "?"
        return f"Tentative candidate: `{cid}` ({cname}, score {sc}) — verify."
    return None

# ---------------------------------------------------------------------------
# Group rows into NEW issues (Bucket D) by normalized place
# ---------------------------------------------------------------------------

A_ROWS = set(BUCKET_A)
B_ROWS = set(BUCKET_B)
C_ROWS = set(BUCKET_C_FINAL)

def normalize_place(place):
    """Lowercase, strip diacritics/punct, collapse a few known variants."""
    s = unicodedata.normalize("NFKD", place)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[«»\"'()\[\]]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Explicit row -> group overrides for places whose romanizations differ too
# much for fuzzy matching, but which refer to the same toponym.
ROW_GROUP_OVERRIDE = {
    29: "pe-tsien-chan-group",   # Pe-tsien-chan, China
    32: "pe-tsien-chan-group",   # Petsiuenchan, Houkouang
    34: "pe-tsien-chan-group",   # Pé-tsiuen-chan, Hukwang
    55: "pe-tsien-chan-group",   # « Pe tsien schan »
    36: "rio-kan",               # Rio Kan
    54: "rio-kan",               # rio Kan (Matteo Ricci referido)
    30: "petit-tibet-kinchuen",  # Petit Tibet «Kinchuen»
    31: "petit-tibet-kinchuen",  # Petit Tibet «Kinchuen»
}

# Known place-grouping keys (consolidate variants into one issue)
def group_key(row_num, place):
    if row_num in ROW_GROUP_OVERRIDE:
        return ROW_GROUP_OVERRIDE[row_num]
    return normalize_place(place)

new_rows = []
for i, rec in enumerate(ROWS, start=1):
    if i in A_ROWS or i in B_ROWS or i in C_ROWS:
        continue
    new_rows.append((i, rec))

# group by group_key
groups = defaultdict(list)
for i, rec in new_rows:
    gk = group_key(i, rec["place"])
    groups[gk].append((i, rec))

print(f"Bucket D (NEW) rows: {len(new_rows)} -> {len(groups)} unique place groups")

# ---------------------------------------------------------------------------
# Generate NEW issue drafts
# ---------------------------------------------------------------------------

new_drafts = []  # list of (seq, filename, title, slug)

def year_of(rec):
    d = rec.get("place.date_inferred.formatted") or ""
    m = re.match(r"(\d{4})", str(d))
    return m.group(1) if m else ""

def type_short(rec):
    t = rec.get("place.type") or ""
    return {
        "estadia": "stay",
        "jesuita-votos-local": "vows",
        "morte": "death",
        "chegada": "arrival",
    }.get(t, t)

# order groups alphabetically by first place for stable numbering
ordered_groups = sorted(groups.items(), key=lambda kv: kv[0])

for seq, (gk, rows) in enumerate(ordered_groups, start=1):
    # representative rec = the one with highest candidate score, else first
    rep = max(rows, key=lambda ir: (ir[1].get("match_score") or 0))
    ri, rec = rep
    place = rec["place"]
    # title: if multiple distinct persons, "Place (N persons)"
    person_ids = []
    for _, r in rows:
        if r["id_col"] not in person_ids:
            person_ids.append(r["id_col"])
    if len(person_ids) == 1:
        p = PERSONS.get(person_ids[0], {})
        pname = p.get("name", person_ids[0])
        yr = year_of(rec)
        title = f"{place} — {pname}, {type_short(rec)} {yr}".strip()
    else:
        title = f"{place} ({len(person_ids)} persons)"

    slug = slugify(place)
    fname = f"{seq:02d}-{slug}.md"
    body = []
    body.append(f"# Place to identify")
    body.append("")
    # one block per row in the group
    for idx, (i, r) in enumerate(rows, 1):
        t = TYPE_LABEL.get(r["place.type"], r["place.type"])
        body.append(f"**{md_escape(r['place'])}** — `{t}`, **{r.get('place.date_inferred.formatted','')}** (`{r.get('place.date_inferred','')}`)")
        cline = candidate_line(r)
        if cline:
            body.append(f"- {cline}")
        if r.get("place.original"):
            body.append(f"- Original transcription: {md_escape(r['place.original'])}")
        body.append("")
    body.append("## Person(s)")
    body.append("")
    # collect all place values in this group (for highlighting all variants)
    all_group_places = [r["place"] for _, r in rows]
    for pid in person_ids:
        body.append(person_header(pid))
        body.append("")
        body.append("### Places in the biography (chronological)")
        body.append("")
        # mark every place-event whose value matches any place in this group
        body.append(itinerary_table(pid, target_places=all_group_places))
        note = source_note(pid, place)
        if note:
            body.append("**Source note** (Dehergne):")
            body.append(f"> {md_escape(note)}")
            body.append("")
    body.append("## Task")
    body.append("")
    body.append(f"Confirm the Wikidata ID for **{md_escape(place)}** and add it via "
                f"`@wikidata:Qxxxxx` in the source `.cli` file(s).")
    body.append("")
    (OUT / fname).write_text("\n".join(body))
    new_drafts.append((seq, fname, title, slug, gk, len(rows), person_ids))

# ---------------------------------------------------------------------------
# Generate Bucket-C comment drafts
# ---------------------------------------------------------------------------

comment_drafts = []
# group C rows by issue number
c_by_issue = defaultdict(list)
for rn in sorted(C_ROWS):
    place, issue = BUCKET_C_FINAL[rn]
    rec = ROWS[rn - 1]
    c_by_issue[issue].append((rn, place, rec))

for issue, items in c_by_issue.items():
    body = []
    body.append("Additional context for this place from another biographical record:")
    body.append("")
    for rn, place, rec in items:
        pid = rec["id_col"]
        body.append(f"### {md_escape(place)} — {PERSONS.get(pid,{}).get('name',pid)}")
        body.append("")
        t = TYPE_LABEL.get(rec["place.type"], rec["place.type"])
        body.append(f"`{t}`, **{rec.get('place.date_inferred.formatted','')}** (`{pid}`)")
        cline = candidate_line(rec)
        if cline:
            body.append(f"- {cline}")
        body.append("")
        body.append("Places in the biography (chronological):")
        body.append("")
        body.append(itinerary_table(pid, target_place=place,
                                    target_type=rec["place.type"],
                                    target_date=rec["place.date_inferred"]))
        note = source_note(pid, place)
        if note:
            body.append(f"> {md_escape(note)}")
            body.append("")
    fname = COMMENTS / f"issue-{issue}.md"
    fname.write_text("\n".join(body))
    comment_drafts.append((issue, fname.name))

# ---------------------------------------------------------------------------
# Generate Bucket-A bug issue draft (row 1: date in place field)
# ---------------------------------------------------------------------------

bug_body = []
r1 = ROWS[0]
bug_body.append("# Data quality: date string in place field")
bug_body.append("")
bug_body.append(f"Row in `locations_names_no_wikidata_with_candidates.xlsx` has the **place** column "
                f"set to `{r1['place']}` (a date string `17010220`), for the attribute "
                f"`{r1.get('place.type','')}` of person `{r1['id_col']}` ({PERSONS.get(r1['id_col'],{}).get('name','')}).")
bug_body.append("")
bug_body.append("This is a transcription/parsing artefact — a date leaked into the place-name field — "
               "not an unidentified toponym. The corresponding source `.cli` line should be checked:")
bug_body.append("")
bug_body.append("```")
bug_body.append(f"ls${r1.get('place.type','')}/.../{r1.get('place.date_inferred','')}")
bug_body.append("```")
bug_body.append("")
p = PERSONS.get(r1["id_col"], {})
bug_body.append(f"Person: **{p.get('name','')}** (`{r1['id_col']}`)")
bug_body.append("")
bug_body.append("### Places in the biography (chronological)")
bug_body.append("")
bug_body.append(itinerary_table(r1["id_col"]))
bug_body.append("**Task**: inspect the `.cli` source, fix the place value, and re-import. "
                "Then this row will leave the unidentified-locations set.")
bug_body.append("")
(OUT / "bug-01-date-in-place-field.md").write_text("\n".join(bug_body))

# ---------------------------------------------------------------------------
# INDEX.md
# ---------------------------------------------------------------------------

idx = []
idx.append("# Unidentified locations — issue generation index")
idx.append("")
idx.append(f"Source: `locations_names_no_wikidata_with_candidates.xlsx` (60 rows). ")
idx.append("Generated from biographical context in `database/sqlite/dehergne.sqlite`.")
idx.append("")
idx.append("## Summary")
idx.append("")
idx.append(f"| Bucket | Description | Rows | Issues |")
idx.append(f"|--------|-------------|------|--------|")
idx.append(f"| A | Data quality / non-toponym | {len(A_ROWS)} | 1 bug issue (drafted) + 4 reported |")
idx.append(f"| B | Existing OPEN issue (skip) | {len(B_ROWS)} | 0 (already tracked) |")
idx.append(f"| C | Existing issue → comment | {len(C_ROWS)} | {len(comment_drafts)} comment drafts |")
idx.append(f"| D | NEW issues | {len(new_rows)} | **{len(new_drafts)} new issue drafts** |")
idx.append(f"| **Total** | | **{len(A_ROWS)+len(B_ROWS)+len(C_ROWS)+len(new_rows)}** | |")
idx.append("")
idx.append("## Bucket D — NEW issues (drafted)")
idx.append("")
idx.append("| # | File | Title | Rows | Persons | GitHub issue |")
idx.append("|---|------|-------|------|---------|--------------|")
for seq, fname, title, slug, gk, nrows, pids in new_drafts:
    idx.append(f"| {seq} | [`{fname}`](./{fname}) | {title} | {nrows} | {len(pids)} | _pending_ |")
idx.append("")
idx.append("## Bucket C — Comments on existing issues (drafted)")
idx.append("")
idx.append("| File | Existing issue |")
idx.append("|------|---------------|")
for issue, fname in comment_drafts:
    idx.append(f"| [`{fname}`](./comments/{fname}) | #{issue} |")
idx.append("")
idx.append("## Bucket A — Data quality / non-toponym (reported)")
idx.append("")
idx.append("| Row | Place | Person | Issue type | Note |")
idx.append("|-----|-------|--------|-----------|------|")
for rn in sorted(A_ROWS):
    note, kind = BUCKET_A[rn]
    rec = ROWS[rn-1]
    idx.append(f"| {rn} | `{rec['place']}` | `{rec['id_col']}` | {kind} | {note} |")
idx.append("")
idx.append("Bug issue draft: [`bug-01-date-in-place-field.md`](./bug-01-date-in-place-field.md)")
idx.append("")
idx.append("## Bucket B — Already tracked by an existing OPEN issue (skipped)")
idx.append("")
idx.append("| Row | Place | Existing issue |")
idx.append("|-----|-------|----------------|")
for rn in sorted(B_ROWS):
    place, issue = BUCKET_B[rn]
    idx.append(f"| {rn} | `{place}` | #{issue} |")
idx.append("")

(OUT / "INDEX.md").write_text("\n".join(idx))

print(f"\nGenerated {len(new_drafts)} new issue drafts, {len(comment_drafts)} comment drafts, 1 bug draft.")
print(f"INDEX: {OUT/'INDEX.md'}")
