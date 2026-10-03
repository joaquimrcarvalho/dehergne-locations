# Extensions for the dehergne notebooks

import json
import re
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError

from timelink.kleio.utilities import convert_timelink_date, format_timelink_date


def _fmt_tl_date(date_str):
    """Format a Timelink date string for display, or '' for undated."""
    if not date_str or date_str in ("0", "00"):
        return ""
    try:
        return format_timelink_date(date_str)
    except Exception:
        return str(date_str)

locations_wikidata_info_file = (
    "../inferences/wikidata-references/locations_wikidata_info.xlsx"
)


def effective_id(model):
    """Return the effective id of an entity in a partially linked database.

    Implements ``COALESCE(real_entity_id, occurrence_id)``: if the entity is
    linked to a real entity (via ``model.links``), return the ``rid``;
    otherwise return the entity's own id (the occurrence IS the real entity).

    This is the Python equivalent of the ``linked_entities`` view (not yet
    implemented in timelink-py — see issue #90). Use this as the grouping
    key for any aggregation that should treat linked occurrences as one
    person.
    """
    for link in getattr(model, "links", []) or []:
        if link.rid:
            return link.rid
    return model.id


def normalize_persons(persons):
    """Deduplicate a set of persons by ``effective_id``.

    In a partially linked database, both an occurrence and its real entity
    may be present in the set. This function keeps one representative per
    effective id, preferring occurrences (fuller biography) over real entities.

    Returns a tuple ``(deduped_persons, occ_to_effective)`` where
    ``occ_to_effective`` is a dict mapping each original id to its
    effective id.
    """
    by_eff = {}
    occ_to_eff = {}
    for p in persons:
        eff = effective_id(p)
        occ_to_eff[p.id] = eff
        # prefer non-rentity (occurrence) when both map to the same eff_id
        existing = by_eff.get(eff)
        if existing is None or (
            getattr(existing, "pom_class", "") == "rentity"
            and getattr(p, "pom_class", "") != "rentity"
        ):
            by_eff[eff] = p
    return list(by_eff.values()), occ_to_eff


def calc_age_at(date_birth, today):
    """Compute the number of years between two dates"""
    # return None if either argument is None
    if date_birth is None or today is None:
        return None
    # Ensure the dates are datetime objects
    if not isinstance(date_birth, datetime):
        date_birth = convert_timelink_date(date_birth)
    if not isinstance(today, datetime):
        today = convert_timelink_date(today)

    if date_birth is None or today is None:
        return None

    # Compute the difference in years
    difference_in_years = (today - date_birth).days / 365.25
    return int(difference_in_years)


# Functions to deal with linked entities in comments, e.g. @wikidata: Q1234567

# Constants for regex patterns
WIKIDATA_PATTERN = r"@?wikidata:\s*(Q\d+)"  # Matches @wikidata:Q1234 or wikidata:Q1234
GENERIC_LINKED_PATTERN = r"@{}:\s*([A-Za-z0-9_]+)"  # Template for any provider


def _extract_id_from_string(text: str, pattern: str, flags: int = 0) -> str | None:
    """Core extraction function - single source of truth."""
    if not text:
        return None
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None


def extract_wikidata_from_string(text: str, if_missing=None) -> str:
    """Extract wikidata ID from any string."""
    result = _extract_id_from_string(text, WIKIDATA_PATTERN, re.IGNORECASE)
    return result if result is not None else if_missing


def get_linked_entity_id(
    comment_string: str, linked_data_provider: str, if_missing=None
) -> str:
    """Generic linked data provider extractor.

    Comments can contain links to other entities, such as wikidata,
    e.g. `@wikidata: Q1234567`.

    The general form is `@<provider>: <id>`, where `<provider>` is the name of
    the linked data provider (e.g. 'wikidata', 'geonames', etc.) and `<id>` is
    the identifier of the linked entity.

    If the comment does not contain a link to the specified provider,
    return value of argument if_missing

    Args:
        comment_string (str): The comment string to search for links.
        linked_data_provider (str): The name of the linked data provider
                                    (e.g. 'wikidata').
        if_missing: The value to return if no link is found. Defaults to None.
    Returns:
        str: The id of the linked entity, or `if_missing` if no link is found.

    """
    pattern = GENERIC_LINKED_PATTERN.format(re.escape(linked_data_provider))
    result = _extract_id_from_string(comment_string, pattern)
    return result if result is not None else if_missing


def geo_entity_wikidata_id(geo_entity, if_missing=""):
    """Check the extra_info field for wikidata links

    Returns a tuple of the cleaned comment and the wikidata id"""

    extra_info = getattr(geo_entity, "extra_info", {})

    # Build cleaned comment by removing wikidata references
    name_comment = extra_info.get("name", {}).get("comment", "")
    name_original = extra_info.get("name", {}).get("original", "")

    cleaned = re.sub(WIKIDATA_PATTERN, "", name_comment, flags=re.IGNORECASE).strip()
    if not cleaned:
        cleaned = re.sub(
            WIKIDATA_PATTERN, "", name_original, flags=re.IGNORECASE
        ).strip()

    wikidata_id = extract_wikidata_id(extra_info, if_missing=if_missing)
    return cleaned, wikidata_id


# extract wikidata id from extra_info dictionary
def extract_wikidata_id(extra_info: dict, if_missing=None) -> str:
    """Return a wikidata ID (e.g., Q1234) parsed from extra_info dict, or if_missing.

    Usage:

        places = entities_with_attribute(
                            entity_type='person',
                            show_elements=['name', 'groupname'],
                            the_type='birthplace',
                            column_name='place',
                            db=db
                            )
        places['wikidata_id'] = places['place.extra_info'].apply(extract_wikidata_id)

    """
    # Try multiple common key paths
    paths = [
        ("the_value", "comment"),
        ("the_value", "original"),
        ("name", "comment"),
        ("name", "original"),
        ("id", "comment"),
        ("id", "original"),
    ]

    for key1, key2 in paths:
        text = (
            extra_info.get(key1, {}).get(key2, "")
            if isinstance(extra_info, dict)
            else ""
        )
        if text:
            result = _extract_id_from_string(text, WIKIDATA_PATTERN, re.IGNORECASE)
            if result:
                return result

    return if_missing


# extract from the "comment" column
def extract_coordinates(comment):
    """
    Parse various coordinate formats from text comment
    and return a tuple (lat, lon).

    Supported formats:
      1. 'coordinates: <lat><N/S>, <lon><E/W>'
      2. 'latitude: <decimal>, longitude: <decimal>'
      3. Signed decimal degrees: '<+ or -><decimal>, <+ or -><decimal>'
      4. DMS: '<deg>°<min>'<sec>"<N/S> <deg>°<min>'<sec>"<E/W>'
    """
    if not comment:
        return None
    # Return None if comment does not contain
    # "coordinates:" nor "latitude:" nor "longitude:"
    if not re.search(
        r"coordinates:|latitude:|longitude:", comment, flags=re.IGNORECASE
    ):
        return None

    # 1. explicit coordinate tag
    m = re.search(
        r"coordinates:\s*([-\d.]+)([NS]),\s*([-\d.]+)([EW])",
        comment,
        flags=re.IGNORECASE,
    )
    if m:
        lat, ns, lon, ew = m.groups()
        lat = float(lat) * (1 if ns == "N" else -1)
        lon = float(lon) * (1 if ew == "E" else -1)
        return (lat, lon)

    # 2. labeled decimal degrees
    m = re.search(
        r"latitude:\s*([-\d.]+),\s*longitude:\s*([-\d.]+)", comment, flags=re.IGNORECASE
    )
    if m:
        lat, lon = m.groups()
        return (float(lat), float(lon))

    # 3. signed decimal degrees with +/− signs
    m = re.search(
        r"([-+]?\d+(?:\.\d+)?),\s*([-+]?\d+(?:\.\d+)?)", comment, flags=re.IGNORECASE
    )
    if m:
        lat, lon = m.groups()
        return (float(lat), float(lon))

    # 4. DMS format
    dms = re.search(
        r'(\d+)°(\d+)\'(\d+\.?\d*)"([NS])[\s,]+(\d+)°(\d+)\'(\d+\.?\d*)"([EW])',  # noqa: E501
        comment,
    )
    if dms:
        d, m1, s, ns, D, m2, s2, ew = dms.groups()

        def dms_to_decimal(deg, minu, sec, hemi):
            dd = float(deg) + float(minu) / 60 + float(sec) / 3600
            return dd * (1 if hemi in ("N", "E") else -1)

        lat = dms_to_decimal(d, m1, s, ns)
        lon = dms_to_decimal(D, m2, s2, ew)
        return (lat, lon)

    raise ValueError(f"Could not parse coordinates from comment: {comment}")


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two points in decimal degrees.

    Returns ``None`` if any of the four coordinates is None.

    Used to compare a historical gazetteer point (e.g. TGAZ) against a
    modern one (e.g. Wikidata) to judge whether the two identify the same
    place.
    """
    if any(v is None for v in (lat1, lon1, lat2, lon2)):
        return None
    from math import radians, sin, cos, asin, sqrt

    R = 6371.0  # mean Earth radius in km
    rlat1, rlat2 = radians(lat1), radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


# ---------------------------------------------------------------------------
# CHGIS Temporal Gazetteer (TGAZ) client
# ---------------------------------------------------------------------------
# The CHGIS TGAZ is a read-only REST service over the China Historical GIS
# placename database (Harvard & Fudan University). It records historical
# Chinese place names with the years during which each name was in use, the
# administrative parent unit, the feature type and coordinates.
#
# Useful for the Dehergne project (Jesuits in China 1552-1800) because it
# resolves place names *to the correct historical period* -- something
# Wikidata, which mostly carries the modern name, does not do.
#
# NOTE on the host: the official documentation still points at
# maps.cga.harvard.edu, but that host is dead (GitHub Pages 404). The service
# moved to chgis.hudci.org, used below.

TGAZ_BASE_URL = "https://chgis.hudci.org/tgaz"
TGAZ_VALID_YEARS = (-222, 1911)  # documented valid range of the database


def tgaz_query(name=None, year=None, feature_type=None, source=None,
               parent=None, fmt="json", timeout=20):
    """Faceted search against the CHGIS Temporal Gazetteer.

    Args:
        name (str): placename spelling. **Required** in practice: although
            the official docs list ``yr``, ``ftyp``, ``src`` and ``p`` as
            independent facets, the live server returns an empty body for
            any query that does not include a name. Chinese characters and
            pinyin work; European spellings (e.g. "Macau") generally do not
            -- prefer the Chinese form (澳门) or pinyin ("Aomen"). Spaces
            are allowed.
        year (int): year of existence. Historical records cover the range
            -222 to 1911 (see TGAZ_VALID_YEARS).
        feature_type (str): feature type / class of placename, e.g. 'fu',
            'xian', 'cun zhen'.
        source (str): data source, e.g. 'CHGIS', 'RAS'.
        parent (str): immediate parent jurisdiction, e.g. 'Guangzhou Fu'.
        fmt (str): output format: 'json' (default), 'xml', 'html', 'rdf'.
        timeout (int): request timeout in seconds.

    Returns:
        The parsed response. For fmt='json' (the default) this is a dict
        with keys 'placenames' (list of records), 'count of total results',
        etc. For other formats a raw string is returned.

    Raises:
        ValueError: if no ``name`` is supplied, or the year is outside the
            documented range.
        URLError: if the request fails.
    """
    if not name:
        raise ValueError(
            "tgaz_query requires a name (the TGAZ server returns no results "
            "for queries without a placename)"
        )
    params = {"n": name}
    if year is not None:
        year = int(year)
        lo, hi = TGAZ_VALID_YEARS
        if year < lo or year > hi:
            raise ValueError(
                f"year {year} outside TGAZ valid range {lo}..{hi}"
            )
        params["yr"] = year
    if feature_type is not None:
        params["ftyp"] = feature_type
    if source is not None:
        params["src"] = source
    if parent is not None:
        params["p"] = parent
    if fmt is not None:
        params["fmt"] = fmt

    url = f"{TGAZ_BASE_URL}/placename?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "dehergne-tgaz/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")

    if fmt == "json":
        # The server sometimes answers 200 OK with an empty body (for
        # unsupported facet combinations). Treat that as "no results"
        # rather than crashing on json.loads("").
        if not raw.strip():
            return {
                "system": "CHGIS - Harvard University & Fudan University",
                "memo": f"Empty response for query matching key "
                        f"'{name}%'",
                "count of displayed results": "0",
                "count of total results": "0",
                "placenames": [],
            }
        return json.loads(raw)
    return raw


def tgaz_get(sys_id, fmt="json", timeout=20):
    """Fetch the canonical record for a TGAZ place by its sys_id.

    sys_id values are minted with the prefix ``hvd_`` (for example the
    CHGIS ID 32180 corresponds to TGAZ ID hvd_32180).

    Note: the canonical endpoint uses a path-based format selector
    (``placename/<fmt>/<id>``), unlike the faceted search which takes
    ``fmt`` as a query parameter.

    Args:
        sys_id (str): TGAZ identifier, e.g. 'hvd_161491'.
        fmt (str): output format: 'json' (default), 'xml', 'html', 'rdf'.
        timeout (int): request timeout in seconds.

    Returns:
        Parsed dict for fmt='json', otherwise the raw response string.

    The JSON canonical record is richer than a faceted-search hit: it
    carries a ``spellings`` list (traditional + simplified Chinese and
    pinyin), a ``feature_type`` object, a ``temporal`` span, ``spatial``
    coordinates and ``part-of`` relationships.
    """
    if not sys_id:
        raise ValueError("sys_id is required")
    url = f"{TGAZ_BASE_URL}/placename/{fmt}/{sys_id}"
    req = Request(url, headers={"User-Agent": "dehergne-tgaz/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    if fmt == "json":
        return json.loads(raw)
    return raw


def tgaz_results_to_records(response):
    """Normalize the JSON response from :func:`tgaz_query` into a list of
    dicts with clean keys.

    The TGAZ JSON uses keys with spaces
    (``"count of total results"``, ``"xy coordinates"``, etc.) which are
    awkward to use. This returns plain, pythonic keys:

        name, transcription, sys_id, uri, year_from, year_to,
        parent_sys_id, parent_name, feature_type, object_type,
        lon, lat, data_source

    Args:
        response: dict returned by tgaz_query(..., fmt='json').

    Returns:
        list[dict]: one dict per placename record (may be empty).
    """
    placenames = response.get("placenames", []) if isinstance(response, dict) else []
    records = []
    for p in placenames:
        years = p.get("years", "")
        year_from, year_to = None, None
        if "~" in years:
            parts = years.split("~")
            year_from = _to_int(parts[0])
            year_to = _to_int(parts[1]) if len(parts) > 1 else None
        lon, lat = _parse_xy(p.get("xy coordinates", ""))
        records.append({
            "name": p.get("name", ""),
            "transcription": p.get("transcription", ""),
            "sys_id": p.get("sys_id", ""),
            "uri": p.get("uri", ""),
            "year_from": year_from,
            "year_to": year_to,
            "years": years.strip(),
            "parent_sys_id": p.get("parent sys_id", ""),
            "parent_name": p.get("parent name", ""),
            "feature_type": p.get("feature type", ""),
            "object_type": p.get("object type", ""),
            "lon": lon,
            "lat": lat,
            "data_source": p.get("data source", ""),
        })
    return records


def tgaz_results_to_dataframe(response):
    """Return TGAZ JSON results as a pandas DataFrame.

    Thin wrapper around :func:`tgaz_results_to_records` plus
    ``pandas.DataFrame``. Importing pandas is deferred so the rest of this
    module does not depend on it.

    Args:
        response: dict returned by tgaz_query(..., fmt='json').

    Returns:
        pandas.DataFrame: one row per placename record.
    """
    import pandas as pd

    return pd.DataFrame(tgaz_results_to_records(response))


def _to_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _parse_xy(xy):
    """Split a 'lon, lat' string into a (lon, lat) pair of floats."""
    if not xy:
        return None, None
    parts = xy.split(",")
    if len(parts) != 2:
        return None, None
    return _to_float(parts[0]), _to_float(parts[1])


def _to_float(value):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Biography rendering helpers for the markdown templates.
#
# model.dated_bio() returns {date_str: [bioitems]} where bioitems include
# both the base attributes (e.g. "estadia") AND their "@wikidata" companions
# (e.g. "estadia@wikidata"), the latter carrying the resolved entity URL.
# The companions frequently use a zero-padded date (e.g. "17070000") while
# the base uses the short form ("1707"), so pairing must normalize by year.
#
# build_biography() returns a structure with three parts:
#   - timeline : [{date, date_str, items:[...]}]  one entry per date, each
#                item = {type, value, obs, wikidata} with the @wikidata link
#                MERGED into the base attribute (no duplicate rows)
#   - source   : [bioitem]  the "dehergne" verbatim source-text entries,
#                pulled out of the timeline
# ---------------------------------------------------------------------------

import re as _re


def _norm_year(date_str):
    """Extract a 4-digit year key from a Timelink date string, or ''."""
    if not date_str:
        return ""
    digits = "".join(c for c in str(date_str) if c.isdigit())
    if len(digits) >= 4 and digits[:4].isdigit():
        return digits[:4]
    return ""


def _qid_from_url(url):
    """Q-id from a wikidata URL or 'Qxxxx' string, else None."""
    if not url:
        return None
    s = str(url)
    m = _re.search(r"(Q\d+)", s)
    return m.group(1) if m else None


def _clean_obs(obs):
    """Clean an attribute observation for display.

    Strips Kleio triple-quote delimiters ('\"\"\"'), leading/trailing
    whitespace, and removes the common indentation that comes from multi-line
    Kleio obs blocks (so the text flows naturally as a paragraph)."""
    if not obs:
        return ""
    s = str(obs)
    # remove triple quotes
    s = s.replace('"""', "")
    # split into lines, strip per-line indentation, drop blank leading/trailing
    lines = s.splitlines()
    # determine minimum indentation of non-blank lines (to dedent)
    nonblank = [ln for ln in lines if ln.strip()]
    if nonblank:
        indent = min(len(ln) - len(ln.lstrip()) for ln in nonblank)
        lines = [ln[indent:] if len(ln) >= indent else ln for ln in lines]
    s = "\n".join(lines).strip()
    return s


def _value_comment(bioitem):
    """Extract the extra info attached to a bioitem's value, for display in
    the Note column.

    Kleio stores two kinds of per-value metadata in
    ``extra_info["the_value"]``:
      * ``original`` — the verbatim source wording when the transcriber
        normalized/translated the value (e.g. value="Trier" but the source
        reads "Trèves"; value="Bago, Birmânia" but source reads "Pégou").
      * ``comment`` — the inline ``#`` comment (source citations, notes,
        original wording) which may include ``@wikidata:Qxxxx`` refs.

    The ``@wikidata`` refs are shown separately as the resolved ``→`` link,
    so they are stripped here. We surface BOTH the original wording and the
    comment remainder, labeled so a reader can tell them apart.

    Returns '' if there is neither an original wording nor a comment.
    """
    ei = getattr(bioitem, "extra_info", None)
    if not ei:
        return ""
    if isinstance(ei, str):
        try:
            import json as _json
            ei = _json.loads(ei)
        except Exception:
            return ""
    try:
        tv = ei.get("the_value", {}) or {}
    except Exception:
        return ""
    original = (tv.get("original") or "").strip()
    comment = (tv.get("comment") or "").strip()
    # strip @wikidata:Qxxxxx references from the comment (shown separately)
    comment = _re.sub(r"@wikidata:Q\d+\s*", "", comment).strip()
    parts = []
    if original and original != "?":
        parts.append(f"original: {original}")
    if comment:
        parts.append(comment)
    return "; ".join(parts)


def _note_for_bioitem(bioitem):
    """Note text for a timeline/relations row, combining all available
    per-attribute metadata:

      * ``obs`` — the explicit obs= field (transcriber notes)
      * ``original`` — verbatim source wording from extra_info (when the
        value was normalized/translated)
      * ``comment`` — the inline # comment from extra_info (citations,
        notes), with @wikidata refs stripped (shown separately)

    All three are distinct channels and can co-occur; they are joined with
    '; ' so nothing is lost. Empty parts are omitted.
    """
    parts = []
    obs = _clean_obs(bioitem.obs)
    if obs:
        parts.append(obs)
    vc = _value_comment(bioitem)
    if vc:
        parts.append(vc)
    return "; ".join(parts)


def _is_linkable_value(value, the_type=None):
    """Should an attribute value become an index link?

    Exclusion is primarily by attribute TYPE (see EXCLUDE_ATTRIBUTE_VALUE_INDEX):
    e.g. nome/nome-chines/nacionalidade are excluded because names are unique
    per person. Numerical values like wicky/wicky-viagem ARE linkable when
    their type is not excluded.

    Values are still skipped when they are empty, '?', or too long to be a
    useful category (> 80 chars).
    """
    if the_type is not None and the_type in EXCLUDE_ATTRIBUTE_VALUE_INDEX:
        return False
    if value is None:
        return False
    s = str(value).strip()
    if not s or s == "?":
        return False
    # too long -> free-text sentence, not an indexable category
    if len(s) > 80:
        return False
    return True


def _slug_for_value(value):
    """Filesystem-safe slug for an attribute value (for value__type notes).

    Preserves accented letters, spaces, punctuation (so filenames stay
    readable: "1º médico na corte de Sigismundo III"), but replaces the
    few characters that are illegal in filenames or that break markdown
    links: '/' and ':' (path separators) and newline."""
    s = str(value).strip()
    # replace only the characters that are problematic on the filesystem
    # or in markdown link targets
    table = str.maketrans({"/": "-", "\\": "-", ":": "-", "\n": " ", "\r": " "})
    return s.translate(table)


def value_link(the_type, value, base_url=""):
    """Markdown link to the index page for an attribute/value pair.

    Returns a '[value](value__type)' link (value first, so notes sort
    alphabetically by value), or the bare value if it should not be linked
    (see _is_linkable_value). `base_url` is an optional prefix for the note
    location (e.g. 'attributes/')."""
    if not _is_linkable_value(value, the_type):
        return str(value)
    slug = f"{_slug_for_value(value)}__{the_type}"
    # wrap the target in <...> so spaces/punctuation don't break the link
    return f"[{value}](<{base_url}{slug}>)"


def type_link(the_type, base_url=""):
    """Markdown link to the type summary page (one page per attribute type
    listing all values and their entity counts).

    Returns '[type](type)' if the type has a summary page (see
    SUMMARY_ATTRIBUTE_TYPES), else the bare type name."""
    if the_type in SUMMARY_ATTRIBUTE_TYPES:
        return f"[{the_type}]({base_url}{the_type})"
    return the_type


# Attribute types whose value+obs carry a free-text note (the verbatim source
# text, transcriber notes, etc.) rather than a structured event. These are
# pulled out of the timeline into the "Notes" section. Extend as needed.
NOTE_TYPES = {"dehergne", "nota", "bibliografia"}

# Attribute types excluded from the value__type index (their values are not
# useful as aggregating index pages: names are unique per person, nationality
# is already captured by other facets). NOTE: numerical values like wicky and
# wicky-viagem ARE relevant, so they are NOT excluded here.
EXCLUDE_ATTRIBUTE_VALUE_INDEX = {"nome", "nome-chines", "nacionalidade", "wicky"}

# Attribute types for which a summary page is generated (one page per type,
# listing all distinct values with their entity counts, each linking to the
# corresponding value__type page). Add types as needed.
SUMMARY_ATTRIBUTE_TYPES = {"jesuita-entrada", "nascimento", "morte",
                           "estadia", "chegada", "partida"}

# Relation types that represent record-linkage / entity-resolution metadata,
# not biographical relationships. Moved to the "Identification" section
# (alongside model.links) rather than the Relations section.
IDENTIFICATION_REL_TYPES = {"identification"}

# Relation types excluded entirely (not shown anywhere).
EXCLUDED_REL_TYPES = {"function-in-act"}


def build_biography(model, follow_identification=False, db=None):
    """Process model.dated_bio() into structured parts for rendering.

    Returns a dict:
        {
          "timeline":   [ {"date": "1707", "entries": [ {type,value,obs,
                            pom_class, wd_qid, wd_url, bioitem}, ... ]}, ... ],
          "relations":  [ {role, direction, other_id, other_name, rel_type,
                            date}, ... ],   # biographical family/social links
          "notes":      [ {type, value, obs}, ... ],   # NOTE_TYPES attributes
          "identifications": [ {other_id, other_name, role, rel_type}, ... ],
                            # record-linkage "same as" relations
          "real_person_ids": [str, ...],   # model.links rid values (merged ids)
          "real_persons":  [ {id, name, description}, ... ],   # if follow_identification
          "occurrences":   [ {entity_id, entity_name, rule}, ... ], # all cluster members
        }

    NOTE_TYPES attributes (default: dehergne, nota) are separated from the
    timeline into `notes`. IDENTIFICATION_REL_TYPES relations (default:
    identification) are separated from `relations` into `identifications`.
    EXCLUDED_REL_TYPES (default: function-in-act) are dropped entirely.

    If `follow_identification=True` (requires `db`, an open SQLAlchemy
    session OR an engine), for each real-person id the corresponding "real
    entity" record is fetched (`real_persons`) together with ALL the
    occurrences in the same merged cluster (`occurrences`, from the links
    table).
    """
    dated_bio = model.dated_bio()
    my_id = model.id

    # Pass 1: collect notes + relations; pair @wikidata companions to their
    # base attributes. Kleio emits a base attribute and its @wikidata companion
    # with (usually) the same date, but: (a) the companion may come before OR
    # after the base within the date group, and (b) the companion sometimes
    # carries a zero-padded date (e.g. '15750000') while the base uses the short
    # form ('1575'), putting them in different date groups.
    #
    # Strategy: group ALL bioitems by NORMALIZED YEAR, then within each year,
    # match the i-th base attribute of a type to the i-th @wikidata companion
    # of that type (they appear in the same order). This is robust to ordering
    # and to the short/zero-padded date discrepancy, and avoids the collision
    # that a plain (type, year) index suffers when two places share a year.
    notes = []
    relations = []
    identifications = []

    # bucket bioitems by normalized year
    by_year = _defaultdict(list)
    for date, bioitems in dated_bio.items():
        yr = _norm_year(date)
        for b in bioitems:
            by_year[yr].append(b)

    # within each year, pair base attributes with @wikidata companions by type
    # and position; collect notes and relations in the same pass.
    wd_for_bioitem = {}   # id(base bioitem) -> (qid, url)
    for yr, bioitems in by_year.items():
        # gather, per base type, the base bioitems and the companion qids in
        # the order they appear
        bases = _defaultdict(list)    # base_type -> [bioitem, ...]
        comps = _defaultdict(list)    # base_type -> [(qid, url), ...]
        for b in bioitems:
            t = b.the_type
            if t in NOTE_TYPES:
                continue   # handled below
            if t.endswith("@wikidata"):
                base = t[: -len("@wikidata")]
                qid = _qid_from_url(b.the_value)
                if base and qid:
                    comps[base].append((qid, b.the_value))
            elif b.pom_class == "attribute":
                bases[t].append(b)
        # pair positionally
        for base_type, base_items in bases.items():
            comp_list = comps.get(base_type, [])
            for i, b in enumerate(base_items):
                if i < len(comp_list):
                    wd_for_bioitem[id(b)] = comp_list[i]

    # now walk dated_bio (in date order) to collect notes + relations, and
    # build the timeline (Pass 2 uses wd_for_bioitem).
    for date, bioitems in dated_bio.items():
        for b in bioitems:
            t = b.the_type
            if t in NOTE_TYPES:
                notes.append({"type": t, "value": b.the_value,
                              "obs": _clean_obs(b.obs),
                              "source_entity": getattr(b, "entity", None)})
            elif b.pom_class == "relation":
                if t in EXCLUDED_REL_TYPES:
                    continue
                rel = {
                    "rel_type": t,
                    "role": b.the_value,
                    "date": date,
                    "date_str": _fmt_tl_date(date),
                    "obs": _clean_obs(b.obs),
                    "bioitem": b,
                }
                if b.origin == my_id:
                    rel["direction"] = "out"
                    rel["other_id"] = b.destination
                    rel["other_name"] = b.dest_name
                else:
                    rel["direction"] = "in"
                    rel["other_id"] = b.origin
                    rel["other_name"] = b.org_name
                if t in IDENTIFICATION_REL_TYPES:
                    identifications.append(rel)
                else:
                    relations.append(rel)

    # Pass 2: build the timeline from attribute bioitems only (relations,
    # @wikidata companions and NOTE_TYPES are handled separately).
    # For REntity records, each bioitem's `entity` attribute is the source
    # occurrence id; we collect these into a numbered occurrences map so the
    # template can link each timeline row back to the occurrence it came from.
    is_real_entity = (getattr(model, "pom_class", "") == "rentity")
    occ_order = {}   # occurrence_id -> sequential number (1-based)
    timeline = []
    for date, bioitems in sorted(dated_bio.items(), key=lambda kv: kv[0]):
        items = []
        for b in bioitems:
            t = b.the_type
            if t in NOTE_TYPES or t.endswith("@wikidata"):
                continue
            if b.pom_class != "attribute":
                continue   # relations rendered in their own section
            entry = {
                "type": t,
                "value": b.the_value,
                "obs": _note_for_bioitem(b),
                "pom_class": b.pom_class,
                "wd_qid": None,
                "wd_url": None,
                "source_entity": getattr(b, "entity", None),
            }
            wd = wd_for_bioitem.get(id(b))
            if wd:
                entry["wd_qid"] = wd[0]
                entry["wd_url"] = wd[1]
            # number the source occurrence (for the Occ column)
            if entry["source_entity"]:
                if entry["source_entity"] not in occ_order:
                    occ_order[entry["source_entity"]] = len(occ_order) + 1
                entry["occ_num"] = occ_order[entry["source_entity"]]
            else:
                entry["occ_num"] = None
            entry["bioitem"] = b
            items.append(entry)
        if items:
            timeline.append({"date": date, "entries": items})

    # Real-person (merged) ids from model.links (record linkage).
    real_person_ids = []
    for l in getattr(model, "links", []) or []:
        if l.rid:
            real_person_ids.append(l.rid)

    # Optionally fetch the real-entity records + all occurrences in the
    # same merged cluster, using the timelink REntity model.
    real_persons = []
    occurrences = []
    if follow_identification and real_person_ids and db is not None:
        from timelink.api.models.rentity import REntity
        from timelink.api.models import Entity
        # accept either a session or an engine; ensure we have a session
        session = db
        owns_session = False
        if not hasattr(session, "get"):
            session = db.session() if hasattr(db, "session") else db
            owns_session = True
        try:
            for rid in real_person_ids:
                rentity = session.get(REntity, rid)
                if rentity is None:
                    continue
                real_persons.append({
                    "id": rid,
                    "description": rentity.get_description() or rid,
                    "status": str(rentity.status) if rentity.status else "",
                })
                # full cluster of occurrences (id strings), excluding self
                for occ_id in rentity.get_occurrences():
                    if occ_id == model.id:
                        continue
                    occ_entity = session.get(Entity, occ_id)
                    occ_name = (occ_entity.get_description()
                                if occ_entity else occ_id)
                    occurrences.append({
                        "entity_id": occ_id,
                        "entity_name": occ_name,
                        "real_id": rid,
                    })
        finally:
            if owns_session:
                session.close()

    # sort relations chronologically (undated last)
    relations.sort(key=lambda r: (not r.get("date"), r.get("date", "")))

    # occurrences_map: for REntity records, the numbered map of source
    # occurrence ids -> {num, name} used by the timeline "Occ" column.
    occurrences_map = {}
    if is_real_entity:
        for occ_id, num in occ_order.items():
            occurrences_map[occ_id] = {"num": num, "id": occ_id, "name": occ_id}

    # occurrences_list: the same, pre-sorted by num, for easy template iteration.
    occurrences_list = sorted(occurrences_map.values(), key=lambda o: o["num"])

    return {
        "is_real_entity": is_real_entity,
        "timeline": timeline,
        "relations": relations,
        "notes": notes,
        "identifications": identifications,
        "real_person_ids": real_person_ids,
        "real_persons": real_persons,
        "occurrences": occurrences,
        "occurrences_map": occurrences_map,
        "occurrences_list": occurrences_list,
    }


# Maps a relation role (the_value) + direction to a human label.
# Roles are in Portuguese (the transcription language).
ROLE_LABEL_OUT = {
    # the person IS this role, relating TO `other`
    "pai": "Father of",
    "mae": "Mother of",
    "marido": "Husband of",
    "mulher": "Wife of",
    "esposa": "Husband of",
    "filho": "Son of",
    "filha": "Daughter of",
    "irmao": "Brother of",
    "irma": "Sister of",
    "tio": "Uncle of",
    "sobrinho": "Nephew of",
    "primo": "Cousin of",
    "avo": "Grandfather of",
    "neto": "Grandson of",
    "companheiro": "Companion of",
    "amigo": "Friend of",
    "mestre": "Teacher of",
    "discipulo": "Disciple of",
}
ROLE_LABEL_IN = {
    # the person is the TARGET; `other` holds this role
    "pai": "Father",
    "mae": "Mother",
    "marido": "Husband",
    "mulher": "Wife",
    "esposa": "Wife",
    "filho": "Son",
    "filha": "Daughter",
    "irmao": "Brother",
    "irma": "Sister",
    "tio": "Uncle",
    "sobrinho": "Nephew (is uncle of this person)",
    "primo": "Cousin",
    "avo": "Grandfather",
    "neto": "Grandson",
    "companheiro": "Companion",
    "amigo": "Friend",
    "mestre": "Teacher",
    "discipulo": "Disciple",
}


def relation_label(rel):
    """Human label for a relation dict (from build_biography). Falls back to
    the raw role if unknown."""
    role = (rel.get("role") or "").strip().lower()
    table = ROLE_LABEL_OUT if rel.get("direction") == "out" else ROLE_LABEL_IN
    label = table.get(role)
    if label:
        return label
    # fallback: "<Role> (<direction>)"
    return f"{rel.get('role','?')} ({rel.get('direction','?')})"



# ---------------------------------------------------------------------------
# Index-note generation for value__type pages.
#
# For each (value, type) pair that is linkable (see _is_linkable_value), an
# index note aggregates every person having that attribute/value, with the
# dated occurrences sorted chronologically. The note filename is
# "<value>__<type>.md" so they sort alphabetically by value.
# ---------------------------------------------------------------------------

from collections import defaultdict as _defaultdict


def index_note_filename(the_type, value):
    """Filename for the index note of a (type, value) pair, or None if the
    value is not linkable."""
    if not _is_linkable_value(value, the_type):
        return None
    return f"{_slug_for_value(value)}__{the_type}.md"


def collect_index_entries(persons):
    """Scan an iterable of ORM persons/rentities and return, for each linkable
    (type, value) pair, a list of chronologically-sorted occurrences.

    Returns: { (type, value): [ {date, date_str, person_id, person_name,
                                  real_entity_id}, ... ] }

    Deduplication: when the same attribute instance (same date+type+value)
    appears in both a Person occurrence AND its aggregated REntity, only ONE
    row is kept — attributed to the Person occurrence (the actual source
    record), with the real-entity id recorded in `real_entity_id`. This
    prevents the index from listing the same event twice (once per record).

    `persons` is iterated once; each entity's dated_bio() is read.
    """
    from timelink.kleio.utilities import format_timelink_date as _fmt

    # Build a map: occurrence_id -> real_entity_id (from each entity's links)
    occ_to_real = {}
    for p in persons:
        for l in getattr(p, "links", []) or []:
            # a Person's link.rid is its real entity; a REntity's link.entity
            # is one of its occurrences.
            if getattr(p, "pom_class", "") == "rentity":
                occ_to_real[l.entity] = l.rid
            elif l.rid:
                occ_to_real[p.id] = l.rid

    index = _defaultdict(dict)  # key -> {dedup_key: entry}
    for p in persons:
        is_re = (getattr(p, "pom_class", "") == "rentity")
        db = p.dated_bio()
        pid = p.id
        pname = p.get_description()
        real_id = pid if is_re else occ_to_real.get(pid)
        for date, bioitems in db.items():
            for b in bioitems:
                if b.pom_class != "attribute":
                    continue
                t = b.the_type
                if t in NOTE_TYPES or t.endswith("@wikidata"):
                    continue
                if not _is_linkable_value(b.the_value, t):
                    continue
                key = (t, str(b.the_value).strip())
                # the source occurrence this bioitem came from (for rentities)
                src = getattr(b, "entity", None) or pid
                src_real = occ_to_real.get(src, real_id)
                # dedup key: (date, real_entity_or_source) so the same event
                # from a person and its rentity collapses to one row.
                dedup = (date, src_real or src)
                dstr = "" if (not date or date in ("0", "00")) else _fmt(date)
                entry = {
                    "date": date,
                    "date_str": dstr,
                    "person_id": src if is_re else pid,
                    "person_name": pname,
                    "real_entity_id": src_real,
                }
                # prefer a Person occurrence over a REntity row when both exist
                existing = index[key].get(dedup)
                if existing is None or (existing.get("real_entity_id") ==
                                        existing.get("person_id") and not is_re):
                    index[key][dedup] = entry

    # flatten to lists and sort chronologically
    flat = {}
    for key, dmap in index.items():
        lst = list(dmap.values())
        lst.sort(key=lambda e: (e["date"] == "", e["date"], e["person_id"]))
        flat[key] = lst
    return flat


def render_index_note(the_type, value, entries):
    """Render the markdown body for a value__type index note."""
    lines = []
    lines.append(f"# {value}")
    lines.append("")
    # link back to the type summary page if one exists
    if the_type in SUMMARY_ATTRIBUTE_TYPES:
        lines.append(f"Attribute type: [`{the_type}`]({the_type})")
    else:
        lines.append(f"Attribute type: `{the_type}`")
    lines.append("")
    persons = {e["person_id"] for e in entries}
    lines.append(f"{len(entries)} occurrence(s) in {len(persons)} person(s).")
    lines.append("")
    lines.append("| Date | Person | Entity id | Real entity |")
    lines.append("|------|--------|-----------|-------------|")
    for e in entries:
        d = e["date_str"] or "—"
        pid = e["person_id"]
        reid = e.get("real_entity_id")
        re_cell = f"[{reid}]({reid})" if reid and reid != pid else "—"
        lines.append(f"| {d} | {e['person_name']} | [{pid}]({pid}) | {re_cell} |")
    lines.append("")
    return "\n".join(lines)


def generate_index_notes(persons, output_dir, *, overwrite=True):
    """Generate value__type index notes for all linkable attribute/value pairs
    found across `persons`, writing them into `output_dir`.

    Returns a dict {filename: count} of written notes (count = occurrences).

    Set `overwrite=False` to skip notes that already exist.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    index = collect_index_entries(persons)
    written = {}
    for (the_type, value), entries in index.items():
        fname = index_note_filename(the_type, value)
        if not fname:
            continue
        path = os.path.join(output_dir, fname)
        if not overwrite and os.path.exists(path):
            continue
        body = render_index_note(the_type, value, entries)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        written[fname] = len(entries)
    return written


def collect_type_summaries(persons):
    """For each SUMMARY_ATTRIBUTE_TYPES type, collect the distinct values and
    the count of DISTINCT entities having each value.

    Returns: { type: [ {value, count}, ... ] } sorted by count desc then value.
    """
    index = collect_index_entries(persons)
    summaries = _defaultdict(lambda: _defaultdict(set))
    for (the_type, value), entries in index.items():
        if the_type not in SUMMARY_ATTRIBUTE_TYPES:
            continue
        for e in entries:
            summaries[the_type][value].add(e["person_id"])
    result = {}
    for the_type, value_map in summaries.items():
        rows = [{"value": v, "count": len(ents)}
                for v, ents in value_map.items()]
        rows.sort(key=lambda r: (-r["count"], r["value"]))
        result[the_type] = rows
    return result


def render_type_summary(the_type, rows):
    """Render the markdown body for a per-type summary page."""
    total_values = len(rows)
    total_entities = sum(r["count"] for r in rows)
    lines = []
    lines.append(f"# {the_type}")
    lines.append("")
    lines.append(f"Summary of `{the_type}` attribute values across the exported set.")
    lines.append(f"{total_values} distinct value(s), {total_entities} occurrence(s).")
    lines.append("")
    lines.append("| Value | Entities |")
    lines.append("|-------|----------|")
    for r in rows:
        slug = _slug_for_value(r["value"])
        lines.append(f"| {r['value']} | [{r['count']}]({slug}__{the_type}) |")
    lines.append("")
    return "\n".join(lines)


def generate_type_summaries(persons, output_dir, *, overwrite=True):
    """Generate one summary page per SUMMARY_ATTRIBUTE_TYPES type.

    Returns a dict {filename: num_values} of written pages.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    summaries = collect_type_summaries(persons)
    written = {}
    for the_type, rows in summaries.items():
        fname = f"{the_type}.md"
        path = os.path.join(output_dir, fname)
        if not overwrite and os.path.exists(path):
            continue
        body = render_type_summary(the_type, rows)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        written[fname] = len(rows)
    return written


# ---------------------------------------------------------------------------
# Wikidata (QID) index pages.
#
# One page per Wikidata QID (e.g. Q14773.md) aggregating every person/event
# linked to that modern place, across ALL attribute types and romanizations.
# This unifies the many transcribed variants (e.g. "Macau", "Macau (Colégio)",
# "Macao" -> Q14773) into a single page, and surfaces mis-linked values
# (e.g. a "Cambodja" estadia wrongly tagged Q14773).
#
# The modern label ("Macau") is fetched from the Wikidata API and cached to a
# JSON file so repeated runs don't re-fetch.
# ---------------------------------------------------------------------------

import json as _json
import os as _os
import urllib.request as _urlreq
from pathlib import Path as _Path


# default location for the QID-label cache (relative to the notebooks/ cwd)
_WD_LABEL_CACHE = "../inferences/wikidata-references/wd_labels_cache.json"


def _load_wd_cache(cache_path):
    if cache_path and _os.path.exists(cache_path):
        try:
            return _json.loads(_Path(cache_path).read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_wd_cache(cache, cache_path):
    if not cache_path:
        return
    _Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    _Path(cache_path).write_text(_json.dumps(cache, ensure_ascii=False, indent=1),
                                encoding="utf-8")


def fetch_wikidata_labels(qids, cache_path=_WD_LABEL_CACHE, languages=("en", "pt")):
    """Fetch labels + descriptions for a set of QIDs from the Wikidata API,
    using a JSON cache to avoid re-fetching. Returns {qid: {label, description}}.

    Fetches in batches of up to 50 QIDs per API call (the Wikidata API limit).
    Only QIDs not already in the cache are fetched.
    """
    import time as _time
    cache = _load_wd_cache(cache_path)
    qids = list(qids)
    todo = [q for q in qids if q and q not in cache]
    lang = "|".join(languages)
    # batch in groups of 50
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        ids_param = "|".join(batch)
        url = (f"https://www.wikidata.org/w/api.php?action=wbgetentities"
               f"&ids={ids_param}&props=labels|descriptions"
               f"&languages={lang}&format=json")
        req = _urlreq.Request(url, headers={"User-Agent": "dehergne-project/1.0 (research)"})
        try:
            with _urlreq.urlopen(req, timeout=30) as r:
                data = _json.load(r)
        except Exception as e:
            # on failure, mark these as unknown so we don't retry forever
            for q in batch:
                cache[q] = {"label": None, "description": f"(fetch error: {e})"}
            _time.sleep(1)
            continue
        entities = data.get("entities", {})
        for q in batch:
            ent = entities.get(q, {})
            label = None
            for l in languages:
                lbl = ent.get("labels", {}).get(l, {})
                if lbl:
                    label = lbl.get("value")
                    break
            desc = None
            for l in languages:
                dsc = ent.get("descriptions", {}).get(l, {})
                if dsc:
                    desc = dsc.get("value")
                    break
            cache[q] = {"label": label, "description": desc}
        _time.sleep(1)  # be polite to the API
    _save_wd_cache(cache, cache_path)
    # return only the requested qids
    return {q: cache.get(q, {"label": None, "description": None}) for q in qids}


def collect_wikidata_entries(persons):
    """Scan persons/rentities and return, per QID, a list of dated occurrences.

    Returns: { qid: [ {date, date_str, person_id, person_name, the_type,
                        value, source_entity, real_entity_id}, ... ] }

    Uses the SAME positional @wikidata pairing logic as build_biography
    (bucket by normalized year, match i-th base to i-th companion) so that
    the right QID is attached to the right value.
    """
    from timelink.kleio.utilities import format_timelink_date as _fmt

    # build occ -> real id map
    occ_to_real = {}
    for p in persons:
        for l in getattr(p, "links", []) or []:
            if getattr(p, "pom_class", "") == "rentity":
                occ_to_real[l.entity] = l.rid
            elif l.rid:
                occ_to_real[p.id] = l.rid

    # bucket bioitems by normalized year (per entity)
    by_year_entity = _defaultdict(lambda: _defaultdict(list))
    for p in persons:
        yr_map = _defaultdict(list)
        for date, bioitems in p.dated_bio().items():
            yr = _norm_year(date)
            for b in bioitems:
                yr_map[yr].append(b)
        for yr, bioitems in yr_map.items():
            for b in bioitems:
                by_year_entity[p.id][yr].append(b)

    # dedup: when the same event (date+value+type+qid) appears in both a Person
    # occurrence AND its aggregated REntity, keep only one row — attributed to
    # the Person occurrence (the actual source record). Keyed by
    # (date, real_entity_or_source, type, value) within each QID.
    index = _defaultdict(dict)
    for p in persons:
        pid = p.id
        is_re = (getattr(p, "pom_class", "") == "rentity")
        pname = p.get_description()
        yr_groups = by_year_entity.get(pid, {})
        for yr, bioitems in yr_groups.items():
            # positional pairing within this year
            bases = _defaultdict(list)
            comps = _defaultdict(list)
            for b in bioitems:
                t = b.the_type
                if t in NOTE_TYPES:
                    continue
                if t.endswith("@wikidata"):
                    base = t[: -len("@wikidata")]
                    qid = _qid_from_url(b.the_value)
                    if base and qid:
                        comps[base].append((qid, b.the_value))
                elif b.pom_class == "attribute":
                    bases[t].append(b)
            for base_type, base_items in bases.items():
                comp_list = comps.get(base_type, [])
                for i, b in enumerate(base_items):
                    if i >= len(comp_list):
                        break
                    qid, wd_url = comp_list[i]
                    src = getattr(b, "entity", None) or pid
                    src_real = occ_to_real.get(src, occ_to_real.get(pid))
                    dstr = ""
                    date = getattr(b, "the_date", "0")
                    if date and date not in ("0", "00"):
                        try:
                            dstr = _fmt(date)
                        except Exception:
                            dstr = str(date)
                    entry = {
                        "date": date or "0",
                        "date_str": dstr,
                        "person_id": src if is_re else pid,
                        "person_name": pname,
                        "the_type": base_type,
                        "value": b.the_value,
                        "real_entity_id": src_real,
                    }
                    dedup = (date or "0", src_real or src, base_type,
                             str(b.the_value).strip())
                    # prefer Person over REntity when both exist
                    existing = index[qid].get(dedup)
                    if existing is None or (existing.get("real_entity_id") ==
                                            existing.get("person_id")
                                            and not is_re):
                        index[qid][dedup] = entry
    # flatten to lists and sort chronologically
    flat = {}
    for qid, dmap in index.items():
        lst = list(dmap.values())
        lst.sort(key=lambda e: (e["date"] == "", e["date"], e["person_id"]))
        flat[qid] = lst
    return flat


def _year_of(date_str):
    """Extract a 4-digit year from a Timelink date string, or None."""
    if not date_str:
        return None
    m = _re.match(r"(\d{4})", str(date_str))
    return int(m.group(1)) if m else None


def render_wikidata_note(qid, label_info, entries, copresence=None,
                         copresence_intervals=None):
    """Render the markdown body for a per-QID index page.

    Layout:
      1. Title (modern label + QID), description, wikidata link.
      2. List of all transcribed variants (romanizations) found, with date
         range, so the spelling inventory and its time span are visible.
      3. A single chronological table of all occurrences, with the variant
         inline as a column — so temporal drift in spelling is readable per
         person/event without flipping between sections.
      4. Co-presence section (if copresence data provided for this QID).
      5. Mermaid Gantt chart of stays (if copresence_intervals provided).
    """
    label = label_info.get("label") if label_info else None
    desc = label_info.get("description") if label_info else None
    title = f"{label} ({qid})" if label else qid
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    if desc:
        lines.append(f"*{desc}*")
        lines.append("")
    lines.append(f"Wikidata: [{qid}](https://www.wikidata.org/wiki/{qid})")
    lines.append("")

    # group by romanization (value) for the variant inventory
    by_value = _defaultdict(list)
    for e in entries:
        by_value[e["value"]].append(e)
    n_persons = len({e["person_id"] for e in entries})
    lines.append(f"{len(entries)} occurrence(s) across "
                 f"{len(by_value)} transcribed value(s), {n_persons} person(s).")
    lines.append("")

    # --- variant list at the top (date range, no table) ---
    lines.append("**Transcribed variants:**")
    lines.append("")
    variant_info = []
    for val, es in by_value.items():
        ys = [y for y in (_year_of(e["date"]) for e in es) if y]
        variant_info.append({
            "value": val, "n": len(es),
            "first": min(ys) if ys else None,
            "last": max(ys) if ys else None,
        })
    variant_info.sort(key=lambda r: (r["first"] is None, r["first"] or 0, r["value"]))
    for v in variant_info:
        if v["first"]:
            lines.append(f"- `{v['value']}` ({v['n']}×, {v['first']}–{v['last']})")
        else:
            lines.append(f"- `{v['value']}` ({v['n']}×, undated)")
    lines.append("")

    # --- single chronological table, variant inline ---
    # entries come already sorted chronologically from collect_wikidata_entries
    lines.append("| Date | Variant | Person | Type | Entity id | Real entity |")
    lines.append("|------|---------|--------|------|-----------|-------------|")
    for e in entries:
        d = e["date_str"] or "—"
        reid = e.get("real_entity_id")
        re_cell = f"[{reid}]({reid})" if reid and reid != e["person_id"] else "—"
        lines.append(f"| {d} | {e['value']} | "
                     f"{e['person_name']} "
                     f"| {e['the_type']} | [{e['person_id']}]({e['person_id']}) | {re_cell} |")
    lines.append("")

    # --- co-presence section (if data provided) ---
    if copresence:
        from copresence import render_copresence_section
        section = render_copresence_section(qid, label_info, copresence)
        if section:
            lines.append(section)

    # --- Mermaid Gantt chart (if intervals provided) ---
    if copresence_intervals:
        from copresence import render_timeline_mermaid
        chart = render_timeline_mermaid(qid, label_info, copresence_intervals)
        if chart:
            lines.append(chart)

    return "\n".join(lines)


def generate_wikidata_notes(persons, output_dir, *, cache_path=_WD_LABEL_CACHE,
                            overwrite=True, compute_copresence=True):
    """Generate one index page per QID found across `persons`.

    If ``compute_copresence`` is True (default), also computes stay intervals
    and co-presence data once, then adds a co-presence section + Mermaid
    Gantt chart to each QID page that has overlapping stays.

    Returns a dict {filename: count} of written pages.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    index = collect_wikidata_entries(persons)
    qids = list(index.keys())
    labels = fetch_wikidata_labels(qids, cache_path=cache_path) if qids else {}

    # compute co-presence data once (if requested)
    copresence_data = None
    intervals_by_qid = None
    if compute_copresence:
        try:
            from copresence import detect_copresence, estimate_stay_intervals
            from collections import defaultdict as _dd
            copresence_data = detect_copresence(persons)
            # collect intervals per QID for the Gantt chart, using NORMALIZED
            # persons (one per effective_id) so linked occurrences don't
            # produce duplicate Gantt bars.
            norm_persons, _ = normalize_persons(persons)
            all_intervals = _dd(lambda: _dd(dict))  # group_key -> {eff_id_key: iv}
            for p in norm_persons:
                for iv in estimate_stay_intervals(p):
                    if iv["start"] is not None:
                        key = (iv["person_id"], iv["start"])
                        all_intervals[iv["group_key"]][key] = iv
            intervals_by_qid = {qid: list(d.values())
                                for qid, d in all_intervals.items()}
        except Exception as e:
            # co-presence is optional; don't fail the whole export
            import logging
            logging.warning(f"Co-presence computation skipped: {e}")

    written = {}
    for qid, entries in index.items():
        fname = f"{qid}.md"
        path = os.path.join(output_dir, fname)
        if not overwrite and os.path.exists(path):
            continue
        body = render_wikidata_note(
            qid, labels.get(qid), entries,
            copresence=copresence_data,
            copresence_intervals=(intervals_by_qid or {}).get(qid))
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        written[fname] = len(entries)
    return written


def expand_with_identifications(persons, session):
    """Expand a set of persons with their record-linkage cluster.

    For each person in `persons` that has a real-entity identification, add:
      - the REntity (real person) itself, so it gets its own markdown page
        and contributes its own attributes to the index
      - all OTHER occurrences of the same real entity (the co-occurrences,
        e.g. the *referido* stubs that mention the same person)

    Returns a list of ORM objects (Person and REntity instances), deduped,
    preserving the session's identity map (all objects come from `session`).

    This is meant to run ONCE, before looping persons for template rendering
    and before generate_index_notes(), so that:
      - every occurrence gets a markdown page
      - the index notes link back to the full expanded set
      - real entities also appear as (thin) pages and index contributors
    """
    from timelink.api.models.rentity import REntity

    # index original persons by id to dedupe
    by_id = {}
    for p in persons:
        by_id[p.id] = p

    # collect ids to fetch (occurrences + real entities) without mutating
    # the input while iterating
    to_fetch = []  # (id, kind)  kind in {"rentity","occurrence"}
    for p in list(persons):
        for l in getattr(p, "links", []) or []:
            rid = l.rid
            if not rid:
                continue
            to_fetch.append((rid, "rentity"))
            rentity = session.get(REntity, rid)
            if rentity is not None:
                for occ_id in rentity.get_occurrences():
                    if occ_id and occ_id not in by_id:
                        to_fetch.append((occ_id, "occurrence"))

    # fetch and merge
    from timelink.api.models import Entity
    for eid, kind in to_fetch:
        if eid in by_id:
            continue
        obj = session.get(REntity if kind == "rentity" else Entity, eid)
        if obj is not None:
            by_id[eid] = obj

    return list(by_id.values())
