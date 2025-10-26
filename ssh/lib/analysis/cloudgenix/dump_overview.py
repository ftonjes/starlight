import re
from datetime import datetime
from ssh.lib.analysis.utilities import uptime_to_seconds
from ssh.lib.analysis.utilities import date_time_delta


def analyze(output, collection=None):
    """

        Aruba - 'dump overview' command analysis

    :param output: output from 'dump overview' on an Aruba device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'dump overview' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'dump overview' output from an Cloudgenix device
    # Regex: '^dump overview$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'dump overview' command should be in string format."

    collection['host_vendor'] = 'Cloudgenix'
    collection['_host_name_extraction'] = r"^(.*?)#\s?$"

    # START

    tmp = re.search(r"^Hardware Model\s+: (.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(1).replace('ion ', '')

    tmp = re.search(r"^Software\s+: (.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_software_version'] = tmp.group(1)

    tmp = re.search(r"^Registration Name\s+: (.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_name'] = tmp.group(1)

    tmp = re.search(r"^Device ID\s+: (.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_serial_number'] = tmp.group(1)

    tmp = re.search(r"^Uptime\s+: (.*?)$", output, re.MULTILINE)
    if tmp:
        uptime_sec = 0
        tmp2 = re.search(r"^((\d+)h)?((\d+)m)?((.*?)s)?", tmp.group(1))
        if tmp2:
            if tmp2.group(2) is not None:
                uptime_sec += int(tmp2.group(2)) * 3600
            if tmp2.group(4) is not None:
                uptime_sec += int(tmp2.group(4)) * 60
            if tmp2.group(6) is not None:
                uptime_sec += int(float(tmp2.group(6)))
        collection['host_uptime'] = uptime_sec

    if 'os_type' not in collection:
        collection['os_type'] = 'cgx_os'

    return True, collection
