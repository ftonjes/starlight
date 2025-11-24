import re
import datetime


def analyze(output: str, collection=None):

    """

        Cisco - 'show cdp neighbors' command analysis

    :param output: output from 'show cdp neighbors' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show cdp neighbors' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show cdp neighbors' output from a Cisco device
    # Regex: '^show cdp neighbors detail$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show cdp neighbors' command should be in string format."

    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # Start

    neighbors = []

    n_compile = re.compile(
        r"--\n(Device ID: .*?\n)(\n--|\n\nTotal cdp entries displayed)",
        re.MULTILINE | re.DOTALL)

    for n_block, _ in re.findall(n_compile, output):

        device = {}

        tmp2 = re.search(r'Device ID: (.*?)\n', n_block)
        neigh_name = None
        if tmp2:
            neigh_name = tmp2.group(1)
        device['name'] = neigh_name

        tmp2 = re.search(r"\nEntry address\(es\): \n(.*?)\nPlatform", n_block, re.MULTILINE | re.DOTALL)
        if tmp2:
            tmp3 = re.search(r"IP address: (\d+\.\d+\.\d+\.\d+)", tmp2.group(1))
            if tmp3:
                device['ip_v4_address'] = tmp3.group(1)

        tmp2 = re.search(r"\nEntry address\(es\): \n(.*?)\nPlatform", n_block, re.MULTILINE | re.DOTALL)
        if tmp2:

            ip_v6_regex = r"""IPv6 address: (([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|
                ([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:)
                {1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1
                ,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}
                :){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{
                1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA
                -F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a
                -fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0
                -9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,
                4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}
                :){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9
                ])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0
                -9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]
                |1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]
                |1{0,1}[0-9]){0,1}[0-9]))"""

            tmp3 = re.search(r"" + ip_v6_regex, tmp2.group(1))
            if tmp3:
                device['ip_v6_address'] = tmp3.group(1)

        tmp2 = re.search(r"\nManagement address\(es\): \n(.*?)\n", n_block, re.MULTILINE | re.DOTALL)
        if tmp2:
            tmp3 = re.search(r"IP address: ()", tmp2.group(1))
            if tmp3:
                device['management_ip_v4_address'] = tmp3.group(1)
            else:
                device['management_ip_v4_address'] = None

        tmp2 = re.search(r'Platform:\s+(.*?),\s+Capabilities:\s+(.*)\n', n_block)
        if tmp2:
            device['platform'] = tmp2.group(1)
            device['capabilities'] = tmp2.group(2).strip().split(' ')

            # Fix 'Two-port Mac Relay' into one list item instead of 3 seperate items:
            if 'Two-port' in device['capabilities']:
                device['capabilities'].remove('Mac')
                device['capabilities'].remove('Relay')
                device['capabilities'].remove('Two-port')
                device['capabilities'].append('Two-port Mac Relay')

        tmp2 = re.search(r'Interface: (.*?),\s+Port ID \(outgoing port\):\s+(.*?)\n', n_block)
        if tmp2:
            device['remote_interface'] = tmp2.group(1).strip()
            device['local_interface'] = tmp2.group(2).strip()

        tmp2 = re.search(r'Holdtime\s+:\s+(.*?)\n', n_block)
        if tmp2:
            device['hold_time'] = tmp2.group(1)

        tmp2 = re.search(r'\nVersion\s+:\n(.*?)\n\n', n_block, re.MULTILINE | re.DOTALL)
        if tmp2:
            device['description'] = tmp2.group(1)

            tmp3 = re.search(r"\nCompiled\s+(.*?)\s+by\s+.*$", tmp2.group(1), re.MULTILINE)
            if tmp3:

                device['software_compiled'] = int(
                    datetime.datetime.strptime(tmp3.group(1), '%a %d-%b-%y %H:%M').timestamp() * 1000)

            tmp3 = re.search(
                r"^(Cisco\s+.*?)\s+\((.*?)\),\s+[Vv]ersion\s+(.*?)(,)?\s+(.*?)$",
                tmp2.group(1), re.MULTILINE)
            if tmp3:
                device['software_name'] = tmp3.group(1)
                device['software_type'] = tmp3.group(2)
                device['software_version'] = tmp3.group(3)
                device['software_release_type'] = tmp3.group(5)

                if re.search(r'Catalyst\s.*\sSwitch', tmp3.group(1)):
                    collection['type'] = 'switch'

                if re.search(r'cisco ios software', tmp3.group(1).lower()):
                    collection['platform'] = 'cisco_ios'

        neighbors.append(device)

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
