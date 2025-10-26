import re


def analyze(output, collection=None):

    """

        Cisco - 'show mac address' command analysis

    :param output: output from 'show mac address' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show mac address' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show mac address' output from a Cisco device
    # Regex: '^show mac address$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show mac address' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    mac_list = []

    # Iterate through output and extract mac address info
    for key, vlan, mac_address, mac_type, learn, age, ports in re.findall(
            r'^(.*?) +(\d+) +([a-f0-9]+\.[a-f0-9]+\.[a-f0-9]+) +([a-z]+) +(Yes|No) +(\d+|-) +(.*?)$',
            output, re.MULTILINE):

        mac_item = {}
        # key (first column) can contain '*', 'R', 'S' or 'D'
        if 'S' in key:
            mac_item['secure_entry'] = True
        if 'R' in key:
            mac_item['routers_gateway_mac_address'] = True
        if 'D' in key:
            mac_item['duplicate_mac_address_entry'] = True
        if '*' in key:
            mac_item['primary _entry'] = True

        mac_item['vlan'] = int(vlan)
        mac_item['mac_address'] = mac_address
        mac_item['address_type'] = mac_type
        mac_item['learn'] = True if learn == 'Yes' else False
        if age != '-':
            mac_item['age'] = int(age)
        mac_item['ports'] = ports

        mac_list.append(mac_item)

    collection['mac_address_list'] = mac_list

    return True, collection
