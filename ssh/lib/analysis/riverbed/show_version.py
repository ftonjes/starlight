import re
import time
from ssh.lib.analysis.utilities import uptime_to_seconds


def analyze(output, collection=None):
    """

        Riverbed - 'show version' command analysis

    :param output: output from 'show version' on a Riverbed device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show version' output from a Riverbed device
    # Regex: '^show version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show version' command should be in string format."

    collection['host_vendor'] = 'Riverbed'
    collection['_host_name_extraction'] = r"^(.*?)\s\>\s$"

    # START

    tmp = re.compile(r'\b(.*?):\s+(.*)\n', re.MULTILINE)
    for item, value in re.findall(tmp, output):

        #             collection['host_uptime'] = uptime_to_seconds(value)
        #             collection['host_restarted'] = time.time() - collection['host_uptime']

        if item == 'Product name':
            collection['product'] = value
            collection['os_type'] = 'rbt_os'
        elif item == 'Product release':
            collection['host_software_version'] = value
        elif item == 'Build arch':
            collection['host_software_arch'] = value
        elif item == 'Built by':
            collection['host_software_built_by'] = value
        elif item == 'Build ID':
            collection['host_software_release'] = value
        elif item == 'Product model':
            collection['host_platform'] = 'tmos'
            tmp = re.search(r"^(.*?)\s\((.*)\)$", value)
            if tmp:
                collection['host_series'] = tmp.group(1)
                collection['host_model'] = tmp.group(2)
        elif item == 'Build date':
            collection['host_software_compiled'] = int(time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S')))

        elif item == 'Uptime':
            collection['host_uptime'] = uptime_to_seconds(value)
            collection['host_restarted'] = time.time() - collection['host_uptime']

        elif item == 'Number of CPUs':
            collection[item] = int(value)
        elif item == 'System memory':
            tmp = re.search(r"^(\d+) MB used / (\d+) MB free / (\d+) MB total$", value)
            if tmp:
                collection['host_memory_used'] = int(tmp.group(1))
                collection['host_memory_free'] = int(tmp.group(2))
                collection['host_memory_total'] = int(tmp.group(3))
        else:
            collection[item] = value

    return True, collection
