# Extensions for the dehergne notebooks

import re
from datetime import datetime
from timelink.kleio.utilities import convert_timelink_date

locations_wikidata_info_file = \
    "../inferences/wikidata-references/locations_wikidata_info.xlsx"


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
    comment_string: str,
    linked_data_provider: str,
    if_missing=None
) -> str:
    """ Return the id of a linked entity from a comment string

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
    pattern = r'@' + re.escape(linked_data_provider) + r'\:\s*([A-Za-z0-9_]+)'
    match = re.search(pattern, comment_string)
    if match:
        return match.group(1)
    return if_missing

