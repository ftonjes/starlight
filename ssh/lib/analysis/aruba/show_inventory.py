import re
import time
from ssh.lib.analysis.utilities import uptime_to_seconds


def analyze(output, collection=None):
    """

        Aruba - 'show inventory' command analysis

    :param output: output from 'show inventory' on an Aruba device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show inventory' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show inventory' output from an Aruba device
    # Regex: '^show inventory$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show inventory' command should be in string format."

    collection['host_vendor'] = 'Aruba'
    collection['_host_name_extraction'] = r"^\((.*?)\) \*?\#$"

    # START

    tmp = re.search(r"^System Serial#\s+: (.*?) \(Date:", output, re.MULTILINE)
    if tmp:
        collection['host_serial_number'] = tmp.group(1)

    tmp = re.search(r"^SC Model#\s+: (.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(1).replace('Aruba', '')

    return True, collection
