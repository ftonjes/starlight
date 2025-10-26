import re
import datetime


def analyze(output, collection=None):

    """

        Cisco - 'show snmp mib ifmib ifindex' command analysis.

    :param output: output from 'show snmp mib ifmib ifindex' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show snmp mib ifmib ifindex' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show snmp mib ifmib ifindex' output from a Cisco device
    # Regex: '^show snmp mib ifmib ifindex$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show snmp mib ifmib ifindex' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    for line in output.split('\n'):

        tmp = re.search(r'^(.*?): Ifindex = (\d+)$', line)
        if tmp:
            if 'ontrolled' not in tmp.group(1):

                if 'interfaces' not in collection:
                    collection['interfaces'] = {}

                if tmp.group(1) not in collection['interfaces']:
                    collection['interfaces'][tmp.group(1)] = {}

                collection['interfaces'][tmp.group(1)]['snmp_interface_oid'] = tmp.group(2)

    return True, collection
