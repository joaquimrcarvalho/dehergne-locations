#!/usr/bin/env python3
"""
Read-only extraction: pull the Excel rows + the dated biographical events
for every person mentioned in the file, and cache to a JSON for the issue
generation step.

Sources (all read-only):
  - Excel: locations_names_no_wikidata_with_candidates.xlsx
  - SQLite: database/sqlite/dehergne.sqlite  (tables: persons, attributes)
"""
import json
import sqlite3
import unicodedata
from pathlib import Path

import openpyxl

ROOT = Path("/Users/jrc/mhk-home/sources/dehergne")
XLSX = Path(
    "/Users/jrc/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/"
    "271E7C16-1989-476C-8162-D4DF35617A76/locations_names_no_wikidata_with_candidates.xlsx"
)
DB = ROOT / "database/sqlite/dehergne.sqlite"
OUT = ROOT / "inferences/iloc-issues/data.json"

# attribute types that represent dated place / life events worth showing
PLACE_EVENT_TYPES = {
    "nascimento", "morte", "estadia", "chegada", "partida", "embarque",
    "jesuita-entrada", "jesuita-votos", "jesuita-votos-local",
    "jesuita-ordenacao-padre", "jesuita-ordenacao", "jesuita-cargo",
    "cargo", "tarefa", "jesuita-tarefa", "wicky", "wicky-viagem",
}
# types that carry an actual place (for the chronological itinerary table)
PLACE_TYPES = {
    "nascimento", "morte", "estadia", "chegada", "partida",
    "jesuita-entrada", "jesuita-votos-local", "jesuita-ordenacao-padre",
}


def fmt_date(d):
    """Timelink date YYYYMMDD -> readable. Handles '' / '0' / partial."""
    if not d or d == "0":
        return ""
    s = str(d).strip().rstrip(">").lstrip(">")
    # take only digits
    digits = "".join(c for c in s if c.isdigit())
    if not digits or len(digits) < 4 or digits == "0" * len(digits):
        return ""
    y = digits[:4]
    mo = digits[4:6] if len(digits) >= 6 else ""
    da = digits[6:8] if len(digits) >= 8 else ""
    parts = [y]
    if mo and mo != "00":
        parts.append(mo)
    if da and da != "00":
        parts.append(da)
    return "-".join(parts)


def norm_date(d):
    """Canonical date key so '1707' matches '17070000' (same logical date).

    Returns a tuple of non-zero components, e.g. ('1707',) or ('1706','01','14').
    """
    if not d:
        return ()
    s = str(d).strip().rstrip(">").lstrip(">")
    digits = "".join(c for c in s if c.isdigit())
    if len(digits) < 4:
        return (digits,)
    y = digits[:4]
    mo = digits[4:6] if len(digits) >= 6 else "00"
    da = digits[6:8] if len(digits) >= 8 else "00"
    parts = (y,)
    if mo and mo != "00":
        parts = parts + (mo,)
    if da and da != "00":
        parts = parts + (da,)
    return parts


def load_rows():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb["Sheet1"]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None and r[1] is None:
            continue
        rec = dict(zip(headers, r))
        rows.append(rec)
    return rows


def fetch_person(conn, pid):
    """Return a dict with name, sex, nationality, status, and dated events."""
    cur = conn.cursor()
    # header
    cur.execute("SELECT name, sex, obs FROM persons WHERE id=?", (pid,))
    prow = cur.fetchone()
    name = prow[0] if prow else pid
    sex = prow[1] if prow else ""

    # all attributes ordered by date
    cur.execute(
        "SELECT the_type, the_value, the_date, obs FROM attributes "
        "WHERE entity=? ORDER BY the_date, the_type",
        (pid,),
    )
    attrs = [dict(zip(["the_type", "the_value", "the_date", "obs"], row))
             for row in cur.fetchall()]

    # build map: for each base type, find the @wikidata companion.
    # Key by (base_type, normalized_date) so '1707' matches '17070000'.
    wd = {}
    for a in attrs:
        t = a["the_type"]
        if t.endswith("@wikidata"):
            base = t[:-len("@wikidata")]
            key = (base, norm_date(a["the_date"]))
            v = a["the_value"] or ""
            qid = v.rsplit("/", 1)[-1] if v else ""
            wd[key] = qid

    events = []
    for a in attrs:
        t = a["the_type"]
        if "@wikidata" in t:
            continue
        # attach the wikidata id only on an exact (type, normalized_date) match.
        # We deliberately do NOT do a year-only fallback: when several places
        # share a year (or are all undated = date '0'), a fuzzy match can attach
        # the wrong QID. The itinerary table then shows '—' for ambiguous cases,
        # which is safer than a wrong link.
        nd = norm_date(a["the_date"])
        qid = ""
        # only attempt a match if there is a real date AND exactly one WD entry
        # and one place event share this (type, nd) key (no ambiguity).
        if nd and nd != ("0",):
            matching_places = sum(1 for x in attrs
                                  if x["the_type"] == t
                                  and norm_date(x["the_date"]) == nd)
            if matching_places == 1:
                qid = wd.get((t, nd), "")
        events.append({
            "type": t,
            "value": a["the_value"],
            "date": a["the_date"],
            "date_fmt": fmt_date(a["the_date"]),
            "wikidata": qid,
            "obs": a["obs"] or "",
        })

    # quick facts
    def first(t):
        for a in attrs:
            if a["the_type"] == t:
                return a["the_value"]
        return ""
    nationality = first("nacionalidade")
    status = first("jesuita-estatuto")
    chinese_name = first("nome-chines")

    # the verbatim dehergne bio (concatenate obs of dehergne attrs)
    bio_chunks = [a["obs"] for a in attrs
                  if a["the_type"] == "dehergne" and a["obs"]]
    bio = "\n".join(bio_chunks).strip()

    # groupname from entities
    cur.execute("SELECT groupname FROM entities WHERE id=?", (pid,))
    erow = cur.fetchone()
    groupname = erow[0] if erow else ""

    return {
        "id": pid,
        "name": name,
        "sex": sex,
        "nationality": nationality,
        "status": status,
        "chinese_name": chinese_name,
        "groupname": groupname,
        "events": events,
        "bio": bio,
    }


def main():
    rows = load_rows()
    person_ids = sorted({r["id_col"] for r in rows if r["id_col"]})

    conn = sqlite3.connect(DB)
    persons = {}
    for pid in person_ids:
        try:
            persons[pid] = fetch_person(conn, pid)
        except Exception as e:
            print(f"WARNING: failed to fetch {pid}: {e}")
    conn.close()

    out = {
        "rows": rows,
        "persons": persons,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT}")
    print(f"  rows: {len(rows)}")
    print(f"  persons: {len(persons)}")
    # report any missing
    missing = [pid for pid in person_ids if pid not in persons]
    if missing:
        print(f"  MISSING: {missing}")


if __name__ == "__main__":
    main()
