import re


def analyze(output, collection=None):

    """

        Cisco - 'show ip route summary' command analysis

    :param output: output from 'show ip route summary' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show ip route summary' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show ip route summary' output from a Cisco device
    # Regex: '^show ip route summary$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show ip route summary' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    if 'routing' not in collection:
        collection['routing'] = {}

    tmp = re.search(
        r'^IP routing table name is (.*?) +\(0x\d\)\nIP routing table maximum-paths is (\d+)\n'
        r'Route Source +Networks +Subnets +Replicates +Overhead +Memory \(bytes\)\n(.*)$',
        output, re.MULTILINE | re.DOTALL)

    if tmp:
        collection['routing']['table_name'] = tmp.group(1)
        collection['routing']['table_maximum_paths'] = tmp.group(2)

        routing = {}
        for line in tmp.group(3).split('\n'):

            tmp2 = re.search(r'^(.*?) {2,}(\d+) {2,}( +|\d+) {2,}( +|\d+) {2,}( +|\d+) {2,}(\d+)$', line)
            if tmp2:

                routing[tmp2.group(1)] = {'networks': int(tmp2.group(2)), 'memory': int(tmp2.group(6))}
                if tmp2.group(3) != ' ':
                    routing[tmp2.group(1)]['subnets'] = int(tmp2.group(3))
                if tmp2.group(4) != ' ':
                    routing[tmp2.group(1)]['replicates'] = int(tmp2.group(4))
                if tmp2.group(5) != ' ':
                    routing[tmp2.group(1)]['overhead'] = int(tmp2.group(5))

        collection['routing']['summary'] = routing

    return True, collection
