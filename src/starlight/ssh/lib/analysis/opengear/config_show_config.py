import re


def analyze(output, collection=None):

    """

        Netscout - 'config --show-config' command analysis

    :param output: output from 'config --show-config' on an Opengear device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'config --show-config' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'config --show-config' output from an Opengear device
    # Regex: '^config --show-config$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'config -show-config' command should be in string format."

    # START

    tmp = re.search(
        r'\nEntity system/admin_info\n.*?\s+hostname\s+(.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_system_name'] = tmp.group(1).strip()

    tmp = re.search(r'\nEntity system/info\n\s+model_name\s+(.*?)\n\s+serial_number\s+(.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(1).strip()
        collection['host_serial_number'] = tmp.group(2).strip()
        collection['host_vendor'] = 'Opengear'
        collection['os_type'] = 'og_os'

    tmp = re.search(
        r'\nEntity system/version\n\s+firmware_version\s+(.*?)\n\s+rest_api_version\s+(.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_software_version'] = tmp.group(1).strip()
        collection['host_rest_api_version'] = tmp.group(2).strip()

    return True, collection
