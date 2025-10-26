import re


def analyze(output, collection=None):

    """

        Cisco - 'show lldp neighbors' command analysis

    :param output: output from 'show lldp neighbors' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show lldp neighbors' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show lldp neighbors' output from a Cisco device
    # Regex: '^show lldp neighbors$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show lldp neighbors' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    neighbors = {}
    if 'neighbors' not in collection:
        collection['neighbors'] = {}

    if 'lldp' not in collection['neighbors']:
        collection['neighbors']['lldp'] = {}

    # If LLDP is not enabled we don't want to show LLDP info:
    if re.search(r'% LLDP is not enabled', output):
        collection['neighbors']['lldp'] = 'LLDP is not enabled'

    else:

        # TODO: Create similar output to that of the 'show cdp neighbor' output
        collection['neighbors']['lldp'] = neighbors

    return True, collection
