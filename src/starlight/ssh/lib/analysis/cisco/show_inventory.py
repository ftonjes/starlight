import re


def analyze(output, collection=None):

    """

        Cisco - 'show inventory' command analysis

    :param output: output from 'show inventory' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show inventory' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show inventory' output from a Cisco device
    # Regex: '^show inventory$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show inventory' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    inventory = []

    for name, descr, pid, vid, serial in re.findall(
            r'NAME: \"(.*?)\", DESCR: \"(.*?)\"\nPID: +(.*?) +, +VID: +(.*?), +SN: +(.*?) *\n', output,
            re.MULTILINE | re.DOTALL):
        inventory.append({
            'name': name.strip(),
            'description': descr,
            'pid': pid.strip() if pid not in ['Unspecified', ''] else None,
            'vid': vid.strip() if vid not in ['Unspecified', ''] else None,
            'serial_number': serial})

    if len(inventory) > 0:
        collection['inventory'] = inventory

    return True, collection
