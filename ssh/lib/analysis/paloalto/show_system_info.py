import re


def analyze(output, collection=None):
    """

        Palo Alto - 'show system info' command analysis

    :param output: output from 'show system info' on an Arista device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show system info' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show system info' output from a Palo Alto Firewall device
    # Regex: '^show system info$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show system info' command should be in string format."

    output_list = output.split('\n')
    for line in output_list:
        tmp = re.search(r'^(.*?):\s+(.*)$', line)
        if tmp:
            item_name = tmp.group(1).replace('-', '_')
            value = tmp.group(2)

            if item_name == 'serial':
                item_name = 'host_serial_number'
            elif item_name == 'hostname':
                item_name = 'host_system_name'
            elif item_name == 'uptime':
                item_name = 'host_uptime'
                total_uptime = 0
                tmp2 = re.search(r'^(\d+) days', tmp.group(2))
                if tmp2:
                    total_uptime = int(tmp2.group(1)) * 86400
                tmp2 = re.search(r'(\d\d):(\d\d):(\d\d)', tmp.group(2))
                if tmp2:
                    total_uptime += int(tmp2.group(1)) * 3600
                    total_uptime += int(tmp2.group(2)) * 60
                    total_uptime += int(tmp2.group(3))
                value = total_uptime
            elif item_name == 'sw_version':
                item_name = 'host_software_version'
            elif item_name == 'model':
                item_name = 'host_model'

            collection[item_name] = value

    if 'dlp' in collection and 'url_db' in collection and 'app_version' in collection:
        collection['os_type'] = 'pan_os'
        collection['host_vendor'] = 'Palo Alto'

    return True, collection
