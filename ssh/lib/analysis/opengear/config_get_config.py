import re


def analyze(output, collection=None):

    """

        Netscout - 'config -g config' command analysis

    :param output: output from 'config -g config' on an Opengear device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'config -g config' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'config -g config' output from an Opengear device
    # Regex: '^config -g config$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'config -g config' command should be in string format."

    # START

    tmp = re.search(r'\nconfig\.system\.name\s+(.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_system_name'] = tmp.group(1).strip()
        collection['host_vendor'] = 'Opengear'
        collection['os_type'] = 'og_os'

    tmp = re.search(r'\nconfig\.system\.model\s+(.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(1).strip()

    # Port configuration
    collection['console_ports'] = {}
    find_ports = re.compile(r'^config\.ports\.port(\d+)\.(.*?)\s+(.*?)$', re.MULTILINE | re.DOTALL)
    for port_no, attrib, value in re.findall(find_ports, output):

        if int(port_no) not in collection['console_ports']:
            collection['console_ports'][int(port_no)] = {}

        if re.search(r'^(\d+)$', value):
            value = int(value)

        collection['console_ports'][int(port_no)][attrib] = value

    return True, collection
