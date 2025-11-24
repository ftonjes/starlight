import re
import datetime
import pprint


def analyze(output, collection=None):

    """

        F5 - 'run util bash -c' command analysis

    :param output: output from 'run util bash -c' on an F5 device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'run util bash -c' command
    """

    # NOTE: Commands 'run util bash -c uptime' for device uptime will not run without administration permissions.

    # Version: 1.0 - Initial version
    # Description: Analyze 'run util bash -c' output from a F5 device
    # Regex: '^run util bash -c .*$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'run util bash -c' command should be in string format."

    collection['host_vendor'] = 'F5'
    collection['_host_name_extraction'] = r"^.*?@\((.*?)\).*"
    collection['os_type'] = 'f5_tmos'

    # START
    tmp = re.search(r"^run util bash -c (.*)$", collection['_session_info']['executed_command'])
    if tmp:
        parameter = tmp.group(1).strip()

        if parameter == "'cat /proc/uptime'":

            # 7663946.54 11417068.62
            tmp = re.search(r'^(\d+.*)\s+(\d+.*?)$', output)
            if tmp:
                collection['host_uptime'] = int(float(tmp.group(1)))

        elif parameter == 'uptime':
            # 14:27:37 up 88 days, 16:57,  1 user,  load average: 3.25, 3.08, 2.74
            tmp = re.search(
                r'^\s+(\d+:\d+:\d+)\s+up\s+(.*),\s+(\d+)\susers?,\s+load average:\s(\d+.*?),\s(\d+.*?),\s(\d+.*?)$',
                output)
            if tmp:

                collection['host_current_time'] = tmp.group(1)
                collection['host_uptime'] = tmp.group(2)
                collection['host_currently_connected_users'] = int(tmp.group(3))
                collection['host_cpu_load'] = (float(tmp.group(4)), float(tmp.group(5)), float(tmp.group(6)))

    find_error = re.search(r'Broadcast message from', output)
    if find_error:
        collection['_error'] = "Broadcast message interuption"
        return False, collection

    return True, collection
