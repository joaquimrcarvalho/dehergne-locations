# Extensions for the dehergne notebooks

import json
import re
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError

from timelink.kleio.utilities import convert_timelink_date

locations_wikidata_info_file = (
    "../inferences/wikidata-references/locations_wikidata_info.xlsx"
)


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
