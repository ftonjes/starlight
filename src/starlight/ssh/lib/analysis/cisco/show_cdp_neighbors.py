import re


def analyze(output, collection=None):

    """

        Cisco - 'show cdp neighbors' command analysis

    :param output: output from 'show cdp neighbors' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show cdp neighbors' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show cdp neighbors' output from a Cisco device
    # Regex: '^show cdp neighbors$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show cdp neighbors' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    neighbors = []

    tmp = re.search(r'Total (cdp )?entries displayed( )?: (\d+)$', output)
    if tmp:
        collection['neighbor_count'] = int(tmp.group(3))

    codes = {}
    tmp = re.search(r"Capability Codes:(.*?\n)\n", output, re.MULTILINE | re.DOTALL)
    if tmp:
        tmp2 = re.compile(r"(.{1,2}) - (.*?)([,\n])", re.MULTILINE)
        for letter, description, _ in re.findall(tmp2, tmp.group(1)):
            codes[letter.strip()] = description.strip()

    tmp = re.search(
        r"\nDevice(\s|-)ID\s+Local Intrfce\s+H(o)?ldtme\s+Capability\s+Platform\s+Port ID\n", output,
        re.MULTILINE | re.DOTALL)
    if tmp:
        tmp2 = re.compile(
            r"^(.*?)\n?\s{2,}(.*?)\s{2,}(\d+)\s{2,}(.*?)\s{2,}(.*?)\s+(.*?)$", re.MULTILINE)
        for remote_device, remote_int, hold_time, capability, platform, local_int in re.findall(tmp2, output):

            serial_number = None
            tmp3 = re.search(r"^(.*)\((.*?)\)$", remote_device)
            if tmp3:
                remote_device = tmp3.group(1)
                serial_number = tmp3.group(2)

            capabilities_list = []
            for item in codes:
                if item in capability:
                    capabilities_list.append(codes[item])

            neigh_info = {
                'device': remote_device,
                'platform': platform,
                'capability': capabilities_list,
                'local_interface': local_int.strip(),
                'remote_interface': remote_int.strip(),
                'hold_time': hold_time}

            if serial_number:
                neigh_info['serial_number'] = serial_number

            neighbors.append(neigh_info)

    if (isinstance(neighbors, list) and len(neighbors) > 0) or re.search(r'CDP not enabled', output):

        if 'neighbors' not in collection:
            collection['neighbors'] = {}

        if 'cdp' not in collection['neighbors']:
            collection['neighbors']['cdp'] = {}

    # If CDP is not enabled we don't want to show CDP info:
    if re.search(r'CDP not enabled', output):

        collection['neighbors']['cdp'] = 'CDP is not enabled'

    else:
        if len(neighbors) > 0:
            collection['neighbors']['cdp'] = neighbors

    return True, collection
