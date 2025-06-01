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


def get_linked_entity_id(
    comment_string: str, linked_data_provider: str, if_missing=None
) -> str:
    """Return the id of a linked entity from a comment string

    Comments often contain links to other entities, such as wikidata,
    e.g. `@wikidata: Q1234567`.

    The general form is `@<provider>: <id>`, where `<provider>` is the name of
    the linked data provider (e.g. 'wikidata', 'geonames', etc.) and `<id>` is
    the identifier of the linked entity.

    If the comment does not contain a link to the specified provider,

    Args:
        comment_string (str): The comment string to search for links.
        linked_data_provider (str): The name of the linked data provider
                                    (e.g. 'wikidata').
        if_missing: The value to return if no link is found. Defaults to None.
    Returns:
        str: The id of the linked entity, or `if_missing` if no link is found.

    """
    if comment_string is None:
        return if_missing
    pattern = r"@" + re.escape(linked_data_provider) + r"\:\s*([A-Za-z0-9_]+)"
    match = re.search(pattern, comment_string)
    if match:
        return match.group(1)
    return if_missing


def get_wikidata_id(geo_entity, if_missing=""):
    """Check the obs field for wikidata links

    Returns a tuple of the cleaned comment and the wikidata id"""
    extra_info = geo_entity.extra_info
    name_comment = extra_info.get("name", {}).get("comment", "")
    name_original = extra_info.get("name", {}).get("original", "")

    pattern = r"@wikidata\:\s*(Q[0-9]*)"
    wikidata_in_comment = re.findall(pattern, name_comment)
    comment_without_wikidata = re.sub(pattern, "", name_comment)
    # Sometimes the wikidata id is in the original name
    wikidata_in_original = re.findall(pattern, name_original)
    original_without_wikidata = re.sub(pattern, "", name_original)
    return comment_without_wikidata + original_without_wikidata, (
        wikidata_in_comment[0]
        if wikidata_in_comment
        else wikidata_in_original[0] if wikidata_in_original else if_missing
    )


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
        r"latitude:\s*([-\d.]+),\s*longitude:\s*([-\d.]+)",
        comment, flags=re.IGNORECASE
    )
    if m:
        lat, lon = m.groups()
        return (float(lat), float(lon))

    # 3. signed decimal degrees with +/− signs
    m = re.search(
        r"([-+]?\d+(?:\.\d+)?),\s*([-+]?\d+(?:\.\d+)?)",
        comment, flags=re.IGNORECASE
    )
    if m:
        lat, lon = m.groups()
        return (float(lat), float(lon))

    # 4. DMS format
    dms = re.search(
        r'(\d+)°(\d+)\'(\d+\.?\d*)"([NS])[\s,]+(\d+)°(\d+)\'(\d+\.?\d*)"([EW])',  # noqa: E501
        comment
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
