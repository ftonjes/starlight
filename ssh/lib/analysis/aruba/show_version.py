import re
from datetime import datetime
from ssh.lib.analysis.utilities import uptime_to_seconds
from ssh.lib.analysis.utilities import date_time_delta


def analyze(output, collection=None):
    """

        Aruba - 'show version' command analysis

    :param output: output from 'show version' on an Aruba device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show version' output from an Aruba device
    # Regex: '^show version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show version' command should be in string format."

    collection['host_vendor'] = 'Aruba'
    collection['_host_name_extraction'] = r"^\((.*?)\) \*?\#$"

    # START

    tmp = re.search(r'^ArubaOS \(MODEL: (.*?)\), Version (.*?)\s', output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(1).replace('Aruba', '')
        collection['host_software_version'] = tmp.group(2)

    tmp = re.search(
        r"^Switch uptime is (\d.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_uptime'] = uptime_to_seconds(tmp.group(1))
        collection['host_restarted'] = datetime.now().timestamp() - collection['host_uptime']

    if 'os_type' not in collection:
        collection['os_type'] = 'aruba_os'

    return True, collection
