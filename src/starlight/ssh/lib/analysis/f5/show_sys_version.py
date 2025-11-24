import re
import datetime
import pprint


def analyze(output, collection=None):

    """

        F5 - 'show sys version' command analysis

    :param output: output from 'show sys version' on an F5 device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show sys version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show sys version' output from a F5 device
    # Regex: '^show sys version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show sys version' command should be in string format."

    collection['host_vendor'] = 'F5'
    collection['_host_name_extraction'] = r"^.*?@\((.*?)\).*"
    collection['os_type'] = 'f5_tmos'

    # START

    tmp = re.compile(r'\s\s(.*?)\s+(.*)(\n|\b)', re.MULTILINE)
    for item, value, _ in re.findall(tmp, output):

        if item == 'Version':
            collection['host_software_version'] = value.strip()
        elif item == 'Edition':
            collection['host_software_revision'] = value.strip()
        elif item == 'Build':
            collection['host_software_build'] = value.strip()
        elif item == 'Date':
            collection['host_software_date'] = value.strip()

    find_error = re.search(r'Broadcast message from', output)
    if find_error:
        collection['_error'] = "Broadcast message interuption"
        return False, collection

    return True, collection
