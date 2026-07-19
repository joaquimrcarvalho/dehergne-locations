#!/usr/bin/env python3
"""
Generate candidate-identification comments from the reviewer's notes in
columns O-U of the Excel file, and post them to the corresponding GitHub
issues. Each comment attributes the candidate to "Ai Yifang" and marks
confidence via the cell background color:
  green (FF92D050)  -> confident
  yellow (FFFFFF00) -> tentative / verify
  (no fill)         -> proposed
"""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import openpyxl

XLSX = Path(
    "/Users/jrc/Documents/RSD_Active_System/PROJECTS/Project-Linking West and East/"
    "6-Key Milestones/2026-07-14 Locations corrections/locations_names_no_wikidata_with_candidates.xlsx"
)
OUT = Path("/Users/jrc/mhk-home/sources/dehergne/inferences/iloc-issues")
COMMENTS = OUT / "comments"
COMMENTS.mkdir(exist_ok=True)
REPO = "joaquimrcarvalho/dehergne-repertoire"

GREEN = "FF92D050"
YELLOW = "FFFFFF00"

# --- reproduce the exact bucket categorization from generate_drafts.py ---
BUCKET_A = {1, 24, 28, 58, 60}
BUCKET_B = {  # row (1-based on ROWS) -> existing issue #
    2: 25, 3: 25, 4: 6, 6: 29, 7: 4, 8: 27, 12: 18, 13: 18,
    14: 33, 15: 33, 23: 28, 44: 14, 45: 14,
}
BUCKET_C = {5: 30, 19: 2, 20: 2}  # comment on existing issue

ROW_GROUP_OVERRIDE = {
    29: "pe-tsien-chan-group", 32: "pe-tsien-chan-group",
    34: "pe-tsien-chan-group", 55: "pe-tsien-chan-group",
    36: "rio-kan", 54: "rio-kan",
    30: "petit-tibet-kinchuen", 31: "petit-tibet-kinchuen",
}


def normalize_place(place):
    s = unicodedata.normalize("NFKD", place)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[«»\"'()\[\]]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def group_key(row_num, place):
    if row_num in ROW_GROUP_OVERRIDE:
        return ROW_GROUP_OVERRIDE[row_num]
    return normalize_place(place)


# --- load our extracted rows + the created-issues state ---
DATA = json.loads((OUT / "data.json").read_text())
ROWS = DATA["rows"]
state = json.loads((OUT / "created_issues.json").read_text())

# build group_key -> new issue number from created_issues.json (filename -> number)
# the draft files are NN-slug.md; map via the group's representative place -> filename
# Easier: re-derive group_key -> filename from the INDEX, then -> number.
index_text = (OUT / "INDEX.md").read_text()
# parse: | seq | [`NN-slug.md`](...) | title | ... | [#NUM](...) |
gk_to_num = {}
for m in re.finditer(
    r"^\|\s*(\d+)\s*\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|\s*(.+?)\s*\|\s*_see issue_\s*\|\s*_see issue_\s*\|\s*\[#(\d+)\]",
    index_text, re.MULTILINE):
    seq, fname, title, num = m.group(1), m.group(2), m.group(3), m.group(4)
    # title begins with the representative place; reconstruct group_key from the
    # actual rows that belong to this seq. Scan ROWS in D bucket to find which
    # group has this representative place.
    # We'll instead build gk->filename by re-grouping D rows.
    pass

# Re-group D rows exactly as generate_drafts.py did, picking the representative
# (max match_score) to map to the filename/seq.
D_rows = []
for i, rec in enumerate(ROWS, start=1):
    if i in BUCKET_A or i in BUCKET_B or i in BUCKET_C:
        continue
    D_rows.append((i, rec))

groups = defaultdict(list)
for i, rec in D_rows:
    groups[group_key(i, rec["place"])].append((i, rec))

ordered = sorted(groups.items(), key=lambda kv: kv[0])
# build gk -> (seq, fname, num)
gk_info = {}
for seq, (gk, rows) in enumerate(ordered, start=1):
    rep = max(rows, key=lambda ir: (ir[1].get("match_score") or 0))
    place = rep[1]["place"]
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", unicodedata.normalize(
        "NFKD", re.sub(r"[«»\"'(),]", "", place))).strip("-").lower()[:50] or "place"
    fname = f"{seq:02d}-{slug}.md"
    num = state.get(fname, {}).get("number")
    gk_info[gk] = {"seq": seq, "fname": fname, "num": num, "place": place}


def row_to_issue(row_num, place):
    """Return the GitHub issue number for a given 1-based ROWS row number."""
    if row_num in BUCKET_A:
        # row 1 -> bug #36; others have no issue
        return 36 if row_num == 1 else None
    if row_num in BUCKET_B:
        return BUCKET_B[row_num]
    if row_num in BUCKET_C:
        return BUCKET_C[row_num]
    gk = group_key(row_num, place)
    return gk_info.get(gk, {}).get("num")


# --- read the Excel reviewer notes (cols O-U) ---
wb_val = openpyxl.load_workbook(XLSX, data_only=True)
wb_sty = openpyxl.load_workbook(XLSX, data_only=False)
ws_val = wb_val["Sheet1"]
ws_sty = wb_sty["Sheet1"]

HDR = {15: "Chinese (from transliteration)", 16: "Place name candidate",
       17: "Pinyin", 18: "Wikidata code", 19: "Superior admin division",
       20: "Other geonames", 21: "Province"}


def cell_fill(r, c):
    f = ws_sty.cell(row=r, column=c).fill
    return f.fgColor.rgb if (f and f.patternType == "solid") else None


# collect candidate rows: Excel row r (2..) -> our ROWS index r-2 -> row_num r-1
candidate_rows = []  # (row_num, rec, vals, flags)
for r in range(2, ws_val.max_row + 1):
    vals = {c: ws_val.cell(row=r, column=c).value for c in range(15, 22)}
    if not any(v not in (None, "", " ") for v in vals.values()):
        continue
    row_num = r - 1  # 1-based on ROWS
    rec = ROWS[r - 2]
    flags = {c: cell_fill(r, c) for c in range(15, 22)
             if cell_fill(r, c) in (GREEN, YELLOW)}
    candidate_rows.append((row_num, rec, vals, flags))

# group by issue number
by_issue = defaultdict(list)
for row_num, rec, vals, flags in candidate_rows:
    num = row_to_issue(row_num, rec["place"])
    by_issue[num].append((row_num, rec, vals, flags))


def md(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def confidence_label(flags, vals):
    """Overall confidence for a row: green if any green, else yellow if any yellow, else proposed."""
    if any(f == GREEN for f in flags.values()):
        return "🟢 confident"
    if any(f == YELLOW for f in flags.values()):
        return "🟡 tentative — please verify"
    return "⚪ proposed"


# --- generate comment bodies ---
generated = []  # (issue_num, filename)
for num in sorted(by_issue, key=lambda n: (n is None, n)):
    rows = by_issue[num]
    body = []
    body.append("> Candidate identification contributed by **Ai Yifang**.")
    body.append("")
    for row_num, rec, vals, flags in rows:
        conf = confidence_label(flags, vals)
        body.append(f"### {md(rec['place'])} — {md(rec['name'])}  ·  {conf}")
        body.append("")
        body.append(f"`{rec.get('place.type','')}`, **{rec.get('place.date_inferred.formatted','')}** "
                    f"(`{rec['id_col']}`)")
        body.append("")
        any_field = False
        for c in range(15, 22):
            v = vals[c]
            if v is None or str(v).strip() == "":
                continue
            any_field = True
            fl = flags.get(c)
            mark = " 🟢" if fl == GREEN else (" 🟡" if fl == YELLOW else "")
            body.append(f"- **{HDR[c]}**: {md(v)}{mark}")
        # if only the bare '？' in Chinese column, note it
        if not any_field:
            body.append("- _(no candidate recovered; Chinese characters uncertain)_")
        body.append("")
    fname = COMMENTS / f"candidate-issue-{num}.md"
    fname.write_text("\n".join(body))
    generated.append((num, fname))

print(f"Generated {len(generated)} candidate comments:")
for num, fname in generated:
    print(f"  #{num}: {fname.name}")
