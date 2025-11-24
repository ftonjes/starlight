import re
from datetime import datetime


def analyze(output, collection=None):

    """

        F5 - 'check_version' command analysis

    :param output: output from 'check_version' on an Opengear device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'check_version' command
    """

    # Version: 1.0 - Initial version
    # Description: Get information from an Opengear device using 'check_version' output
    # Regex: '^check_version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'check_version' command should be in string format."

    # START

    # OpenGear/CM71xx Version 4.13.1 00000a00 -- Wed Nov 23 22:09:45 UTC 2022
    tmp = re.search(r'^OpenGear/(.*?)\s+Version\s+(\d+.*)\s+(.*?)\s+--', output)
    if tmp:
        collection['host_vendor'] = 'Opengear'
        collection['host_software_version'] = tmp.group(2)

    return True, collection
