import re


def analyze(output, collection=None):

    """

        F5 - 'cat /proc/uptime' command analysis

    :param output: output from 'cat /proc/uptime' on an Opengear device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'cat /proc/uptime' command
    """

    # Version: 1.0 - Initial version
    # Description: Get uptime from an Opengear device using 'cat /proc/uptime' output
    # Regex: '^cat /proc/uptime$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'cat /proc/uptime' command should be in string format."

    # START

    # 7663946.54 11417068.62
    tmp = re.search(r'^(\d+.*)\s+(\d+.*?)$', output)
    if tmp:
        collection['host_uptime'] = int(float(tmp.group(1)))

    return True, collection
