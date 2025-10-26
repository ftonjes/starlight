import re
import time
from ssh.lib.analysis.utilities import date_time_delta
from ssh.lib.analysis.utilities import uptime_to_seconds


def analyze(output, collection=None):
    """

        Riverbed - 'show version' command analysis

    :param output: output from 'show version' on an Arista device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show version' output from an Arista device
    # Regex: '^show version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show version' command should be in string format."

    # START

    tmp = re.search(r"^Arista\s+(.*?)\nHardware\s+version:\s+", output, re.MULTILINE | re.DOTALL)
    if tmp:
        collection['host_model'] = tmp.group(1)
        collection['host_vendor'] = 'Arista'
        collection['_host_name_extraction'] = "^(.*?)[>#]$"
        collection['os_type'] = 'arista_eos'

    tmp = re.compile(r'\b(.*?):\s+(.*)\n', re.MULTILINE)
    for item, value in re.findall(tmp, output):

        if item == 'Uptime':
            collection['host_uptime'] = uptime_to_seconds(value)
            collection['host_restarted'] = time.time() - collection['host_uptime']

        elif item == 'Total memory':
            collection['host_memory_total'] = value

        elif item == 'Free memory':
            collection['host_memory_free'] = value

        elif item == 'Serial number':
            collection['host_serial_number'] = value

        elif item == 'Software image version':
            collection['host_software_version'] = value
        else:
            collection[item.replace(' ', '_').lower()] = value

    return True, collection
