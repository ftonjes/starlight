import re
import datetime
import pprint


def analyze(output, collection=None):

    """

        Cisco - 'show running-config' command analysis

    :param output: output from 'show running-config' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show running-config' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show running-config' output from a Cisco device
    # Regex: '^show running-config$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show running-config' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    return True, collection
