import re


def analyze(output, collection=None):

    """

        Cisco - 'show module all' command analysis

    :param output: output from 'show module all' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show module all' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show module all' output from a Cisco device
    # Regex: '^show module all$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show module all' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    modules = {}
    tmp = re.search(
        r'Mod\s+Ports\s+Card\s+Type\s+Model\s+Serial\sNo.\n--.*?--\n(.*?)\n\n', output, re.MULTILINE | re.DOTALL)
    if tmp:

        for line in tmp.group(1).split('\n'):

            tmp2 = re.search(r"^\s+(\d+)\s{2,}(\d+)\s+(.*?)\s+(\S+)\s+(\S+)$", line)
            if tmp2:

                module_id = int(tmp2.group(1))
                if module_id not in modules:
                    modules[module_id] = {}

                modules[module_id]['ports'] = int(tmp2.group(2))
                modules[module_id]['card_type'] = tmp2.group(3)
                modules[module_id]['model'] = tmp2.group(4)
                modules[module_id]['serial_number'] = tmp2.group(5)

    tmp = re.search(
        r'Mod\s+MAC\s+addresses\s+Hw\s+Fw\s+Sw\s+Status\n--.*?--\n(.*?)\n\n', output, re.MULTILINE | re.DOTALL)
    if tmp:

        for line in tmp.group(1).split('\n'):
            tmp2 = re.search(r"^\s+(\d+)\s+(.*?)\s+to\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*)", line)

            module_id = int(tmp2.group(1))
            if module_id not in modules:
                modules[module_id] = {'interfaces': {}}

            modules[module_id]['mac_addresses_from'] = tmp2.group(2)
            modules[module_id]['mac_addresses_to'] = tmp2.group(3)
            modules[module_id]['hardware_version'] = tmp2.group(4)
            modules[module_id]['firmware_version'] = tmp2.group(5)
            modules[module_id]['software_version'] = tmp2.group(6)
            modules[module_id]['status'] = tmp2.group(7)

    tmp = re.search(
        r'Mod\s+Sub-Module\s+Model\s+Serial\s+Hw\s+Status\s?\n--.*?--\n(.*?)\n\n', output, re.MULTILINE | re.DOTALL)

    if tmp:
        for line in tmp.group(1).split('\n'):

            tmp2 = re.search(r"^\s+(\d+)\s{2,}(.*)\s+(\S+)\s+(\S+)\s+(\d.*?)\s+(.*?)$", line)
            module_id = int(tmp2.group(1))

            if module_id not in modules:
                modules[module_id] = {}
            if 'sub_modules' not in modules[module_id]:
                modules[module_id]['sub_modules'] = {}

            next_id = len(modules[module_id]['sub_modules']) + 1
            modules[module_id]['sub_modules'][next_id] = {
                'name': tmp2.group(2).strip(),
                'model': tmp2.group(3).strip(),
                'serial_number': tmp2.group(4).strip(),
                'hardware_version': tmp2.group(5).strip(),
                'status': tmp2.group(6).strip()
            }

    tmp = re.search(
        r'Mod\s+Online Diag Status\s?\n--.*?--\n(.*)$', output, re.MULTILINE | re.DOTALL)

    if tmp:
        for line in tmp.group(1).split('\n'):

            tmp2 = re.search(r"^\s+(\d+)\s{2,}(.*)$", line)
            if tmp2:
                module_id = int(tmp2.group(1))
                modules[module_id]['online_diag_status'] = tmp2.group(2)

    collection['modules'] = modules

    return True, collection
