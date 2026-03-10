# Extensions for the dehergne notebooks

import re
from datetime import datetime
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
