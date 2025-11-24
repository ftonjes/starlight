import re


def analyze(output, collection=None):

    """

        Netscout - 'system version' command analysis

    :param output: output from 'system version' on a Netscout device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'system version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'system version' output from a Netscout device
    # Regex: '^(sys|system) version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'system version' command should be in string format."

    # START

    tmp = re.search(r'Version: Arbor Edge Defense\s+(\d.*?\d)\s\(build (.*?)\)', output, re.MULTILINE)
    if tmp:
        collection['host_vendor'] = 'Netscout'
        collection['_host_name_extraction'] = "^.*?@(.*?):/"
        collection['os_type'] = 'arb_os'
        collection['host_software_version'] = tmp.group(1)
        collection['host_software_revision'] = tmp.group(2)

    return True, collection
