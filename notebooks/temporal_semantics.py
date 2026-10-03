"""Temporal semantics: classify attribute types by their temporal meaning
and build stay/tenure intervals for overlap analysis.

This module is designed to be **package-ready**: it depends only on the
standard library and on a minimal ``build_biography`` interface. It does
not import from ``dehergne_util`` or any project-specific module, so it can
be lifted into ``timelink.api`` or ``timelink.analysis`` with minimal change.

Architecture:
  - ``TemporalRole``: enum classifying how an attribute type relates to time
  - ``TemporalVocabulary``: a mapping from attribute type → role
  - ``build_intervals()``: generic engine that walks a person's timeline
    and produces stay/tenure intervals using the vocabulary
  - ``detect_overlaps()``: generic interval-overlap detection
  - ``cluster_overlaps()``: group overlapping intervals into co-presence groups

See ``temporal_semantics_spec.md`` for the full specification.
"""

import re
from enum import Enum
from collections import defaultdict
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# TemporalRole: how an attribute type relates to time
# ---------------------------------------------------------------------------

class TemporalRole(Enum):
    """Classification of an attribute type's temporal semantics."""

    #: Begins a period of presence/tenure at a value.
    #: Creates or extends a segment.
    INTERVAL_START = "interval_start"

    #: Terminates the current period. Closes any open segment.
    INTERVAL_END = "interval_end"

    #: Implies presence for a duration (start = date, end = next evidence
    #: of leaving). Creates or extends a segment.
    INTERVAL = "interval"

    #: Present on this date only; does not start or end a period.
    #: Absorbed if within a segment; same-day interval if standalone.
    POINT = "point"

    #: Ongoing condition, not a temporal event. Ignored by the engine.
    STATUS = "status"

    #: An identifier (e.g. a reference number). Ignored by the engine.
    REFERENCE = "reference"


# Roles that participate in interval construction
_ACTIVE_ROLES = {
    TemporalRole.INTERVAL_START,
    TemporalRole.INTERVAL,
    TemporalRole.INTERVAL_END,
    TemporalRole.POINT,
}

# Roles that create/extend segments
_SEGMENT_ROLES = {TemporalRole.INTERVAL_START, TemporalRole.INTERVAL}

# Roles that close the current segment
_CLOSING_ROLES = {TemporalRole.INTERVAL_END}


# ---------------------------------------------------------------------------
# TemporalVocabulary: configurable mapping of attribute types to roles
# ---------------------------------------------------------------------------

class TemporalVocabulary:
    """Maps attribute type names to :class:`TemporalRole` values.

    Unlisted types default to :attr:`TemporalRole.STATUS` (ignored).
    The ``-x`` suffix is stripped before lookup so variant types inherit
    the base type's role.
    """

    def __init__(self, mapping: Optional[dict] = None):
        self._mapping = dict(mapping or {})

    def role_of(self, attr_type: str) -> TemporalRole:
        """Return the temporal role for an attribute type.

        Strips ``-x`` suffix for variant types. Unlisted types default
        to :attr:`TemporalRole.STATUS`.
        """
        t = str(attr_type).strip()
        base = re.sub(r"-x$", "", t)
        if base in self._mapping:
            return self._mapping[base]
        if t in self._mapping:
            return self._mapping[t]
        return TemporalRole.STATUS

    def is_active(self, attr_type: str) -> bool:
        """True if the type participates in interval construction."""
        return self.role_of(attr_type) in _ACTIVE_ROLES


# ---------------------------------------------------------------------------
# Default Dehergne vocabulary (project-specific; swap for another DB)
# ---------------------------------------------------------------------------

DEFAULT_VOCABULARY = TemporalVocabulary({
    # Places
    "estadia":                TemporalRole.INTERVAL,
    "chegada":                TemporalRole.INTERVAL_START,
    "partida":                TemporalRole.INTERVAL_END,
    "embarque":               TemporalRole.INTERVAL_END,
    "nascimento":             TemporalRole.INTERVAL_START,
    "morte":                  TemporalRole.INTERVAL_END,
    "baptizado":              TemporalRole.POINT,
    "residencia":             TemporalRole.INTERVAL,

    # Jesuit career
    "jesuita-entrada":        TemporalRole.INTERVAL_START,
    "jesuita-votos-local":    TemporalRole.POINT,
    "jesuita-ordenacao-padre": TemporalRole.POINT,
    "jesuita-cargo":          TemporalRole.INTERVAL,
    "jesuita-tarefa":         TemporalRole.INTERVAL,

    # Secular roles
    "cargo":                  TemporalRole.INTERVAL,
    "tarefa":                 TemporalRole.INTERVAL,
})


# ---------------------------------------------------------------------------
# Date parsing helpers (minimal — delegates to timelink when available)
# ---------------------------------------------------------------------------

def _date_sort_key(the_date):
    """Extract an 8-digit YYYYMMDD integer from a Timelink date string.

    Handles extended date notation:
      - ``YYYYMMDD``, ``YYYYMM00``, ``YYYY0000``  → as-is
      - ranges (``1580:1640``)                    → first part before ``:``
      - ``>YYYY`` / ``<YYYY``                     → digits after stripping
      - decimal (``15800000.3``)                  → integer part before ``.``
      - ``0`` / empty                             → ``None`` (undated)
    """
    if not the_date:
        return None
    s = str(the_date).strip()
    if not s or s == "0":
        return None
    s = s.split(":")[0]
    s = s.split(".")[0]
    s = s.lstrip("><")
    if not s.isdigit() or len(s) < 4:
        return None
    return int(s.ljust(8, "0")[:8])


def _date_to_iso(sort_key):
    """Convert an 8-digit YYYYMMDD integer to an ISO-ish string."""
    if sort_key is None:
        return ""
    s = str(sort_key)
    y, mo, da = s[:4], s[4:6], s[6:8]
    if mo == "00" and da == "00":
        return y
    if da == "00":
        return f"{y}-{mo}"
    return f"{y}-{mo}-{da}"


def _add_years(sort_key, years):
    if sort_key is None:
        return None
    y = int(str(sort_key)[:4]) + years
    return int(f"{y:04d}" + str(sort_key)[4:])


# ---------------------------------------------------------------------------
# Interval and Overlap data structures
# ---------------------------------------------------------------------------

class Interval:
    """A stay/tenure interval at a grouping key (QID, office, etc.)."""

    __slots__ = ("person_id", "person_name", "group_key", "group_label",
                 "start", "end", "start_str", "end_str",
                 "is_open", "is_flagged", "is_point", "event_type")

    def __init__(self, person_id, person_name, group_key, group_label,
                 start, end, event_type, is_point=False):
        self.person_id = person_id
        self.person_name = person_name
        self.group_key = group_key        # e.g. "Q45412" or ("jesuita-cargo", "Superior...")
        self.group_label = group_label    # human-readable label for the group
        self.start = start
        self.end = end
        self.start_str = _date_to_iso(start)
        self.end_str = _date_to_iso(end)
        self.is_open = False
        self.is_flagged = False
        self.is_point = is_point
        self.event_type = event_type

    def to_dict(self):
        """Serialise to a plain dict (for template rendering, JSON export)."""
        return {s: getattr(self, s) for s in self.__slots__}


# Configuration constants (module-level, overridable)
MAX_OPEN_YEARS = 15
FLAG_LONG_YEARS = 30


# ---------------------------------------------------------------------------
# Generic interval engine
# ---------------------------------------------------------------------------

def build_intervals(timeline, person_id, person_name, *,
                    vocabulary=DEFAULT_VOCABULARY,
                    grouping_fn: Callable = None,
                    max_open_years: int = MAX_OPEN_YEARS,
                    flag_long_years: int = FLAG_LONG_YEARS):
    """Walk a person's timeline and produce stay/tenure intervals.

    Parameters:
        timeline:   the ``timeline`` list from ``build_biography(model)``
                    — ``[{date, entries: [{type, value, wd_qid, ...}]}]``
        person_id:  the effective id of the person
        person_name: display name
        vocabulary: a :class:`TemporalVocabulary`
        grouping_fn: a function ``(entry) -> (group_key, group_label)``
                    that extracts the grouping key and label from a timeline
                    entry. Default: uses ``entry["wd_qid"]`` and
                    ``entry["value"]`` (place-based co-presence).
        max_open_years: cap for intervals with no end evidence
        flag_long_years: flag intervals longer than this (data-gap review)

    Returns a list of :class:`Interval` objects.
    """
    if grouping_fn is None:
        grouping_fn = _place_grouping_fn

    # Build flat chronological list of classified events
    events = []
    prev_date = None
    for grp in timeline:
        grp_date = grp.get("date", "0")
        grp_key = _date_sort_key(grp_date)
        for e in grp.get("entries", []):
            t = e.get("type", "")
            role = vocabulary.role_of(t)
            if role not in _ACTIVE_ROLES:
                continue

            key = grp_key
            if key is None and prev_date is not None:
                key = prev_date  # forward-fill
            if key is not None:
                prev_date = key

            gk, gl = grouping_fn(e)
            if gk is None:
                continue

            events.append({
                "date_key": key,
                "role": role,
                "type": t,
                "group_key": gk,
                "group_label": gl,
            })

    events.sort(key=lambda x: (x["date_key"] or 0, x["type"]))
    if not events:
        return []

    # Find morte date for capping
    morte_key = None
    for ev in events:
        # morte has INTERVAL_END role; check by type as well
        if "morte" in ev["type"] and ev["date_key"]:
            morte_key = ev["date_key"]
            break

    # Build segments
    segments = []
    current = None
    for ev in events:
        role = ev["role"]

        if role in _CLOSING_ROLES:
            if current and current["end"] is None:
                current["end"] = ev["date_key"]
                segments.append(current)
                current = None
            continue

        gk = ev["group_key"]

        if role == TemporalRole.POINT:
            if current and current["group_key"] == gk:
                pass  # absorbed
            else:
                if current:
                    segments.append(current)
                    current = None
                segments.append({
                    "group_key": gk, "group_label": ev["group_label"],
                    "start": ev["date_key"], "end": ev["date_key"],
                    "type": ev["type"], "is_point": True,
                })
        else:
            # INTERVAL or INTERVAL_START
            if current and current["group_key"] == gk:
                current["end"] = None
            else:
                if current:
                    segments.append(current)
                current = {
                    "group_key": gk, "group_label": ev["group_label"],
                    "start": ev["date_key"], "end": None,
                    "type": ev["type"], "is_point": False,
                }
    if current:
        segments.append(current)

    # Compute interval ends
    intervals = []
    for i, seg in enumerate(segments):
        start = seg["start"]
        is_point = seg.get("is_point", False)

        if is_point and start is not None:
            intervals.append(Interval(
                person_id, person_name, seg["group_key"], seg["group_label"],
                start, start, seg["type"], is_point=True))
            continue

        if start is None:
            continue

        end = None
        for j in range(i + 1, len(segments)):
            if segments[j]["group_key"] != seg["group_key"]:
                end = segments[j]["start"]
                break

        is_open = False
        is_flagged = False
        if end is None:
            if morte_key and morte_key > start:
                end = morte_key
            else:
                end = _add_years(start, max_open_years)
                is_open = True

        if start and end:
            years = (end - start) // 10000
            if years > flag_long_years:
                is_flagged = True

        iv = Interval(
            person_id, person_name, seg["group_key"], seg["group_label"],
            start, end, seg["type"])
        iv.is_open = is_open
        iv.is_flagged = is_flagged
        intervals.append(iv)

    return intervals


# Default grouping function: place-based (by Wikidata QID)
def _place_grouping_fn(entry):
    """Extract (qid, place_name) from a timeline entry. Returns (None, None)
    if no QID is present."""
    qid = entry.get("wd_qid")
    if not qid:
        return None, None
    return qid, entry.get("value", qid)


# Role-based grouping function: (type, value)
def role_grouping_fn(entry):
    """Extract ((type, value), value) from a timeline entry.

    Groups by the combination of attribute type and value — e.g. all
    'Superior da missão da China' cargo attributes group together.
    """
    t = entry.get("type", "")
    v = entry.get("value", "")
    if not v or v == "?":
        return None, None
    return (t, v), v


# ---------------------------------------------------------------------------
# Overlap detection (generic)
# ---------------------------------------------------------------------------

def detect_overlaps(intervals, include_open=False):
    """Detect overlapping intervals, grouped by group_key.

    Parameters:
        intervals: a list of :class:`Interval` objects
        include_open: if False (default), open/capped intervals are excluded

    Returns ``{group_key: [overlap_dict, ...]}`` where each overlap is:
        ``{a_id, a_name, b_id, b_name, key, label, ov_start, ov_end,
           ov_start_str, ov_end_str}``
    """
    by_group = defaultdict(list)
    for iv in intervals:
        if iv.is_open and not include_open:
            continue
        if iv.start is None:
            continue
        by_group[iv.group_key].append(iv)

    result = defaultdict(list)
    for key, ivs in by_group.items():
        ivs.sort(key=lambda x: x.start)
        n = len(ivs)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = ivs[i], ivs[j]
                if a.person_id == b.person_id:
                    continue
                if a.start < b.end and b.start < a.end:
                    ov_s = max(a.start, b.start)
                    ov_e = min(a.end, b.end)
                    result[key].append({
                        "a_id": a.person_id, "a_name": a.person_name,
                        "b_id": b.person_id, "b_name": b.person_name,
                        "key": key, "label": a.group_label,
                        "ov_start": ov_s, "ov_end": ov_e,
                        "ov_start_str": _date_to_iso(ov_s),
                        "ov_end_str": _date_to_iso(ov_e),
                    })
    return dict(result)
