import re


def analyze(output, collection=None):
    """

        Riverbed - 'show version' command analysis

    :param output: output from 'show version' on an Arista device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'dump overview' output from a Palo Alto Cloudgenix device
    # Regex: '^dump overview$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show version' command should be in string format."

    # print(output)

    tmp = re.search(r'^Hardware Model(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(2)
        collection['host_vendor'] = 'Palo Alto'
        collection['_host_name_extraction'] = "^(.*?)[>#]$"
        collection['os_type'] = 'cgx_os'

    tmp = re.search(r'^Software(\t)+:\s(.*)$', output, re.MULTILINE)
    if tmp:
        collection['host_software_version'] = tmp.group(2)

    tmp = re.search(r'^Hardware Version(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['host_hardware_version'] = tmp.group(2)

    tmp = re.search(r'^Device ID(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['host_serial_number'] = tmp.group(2)

    tmp = re.search(r'^Registration State(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['host_registered_state'] = tmp.group(2)

    tmp = re.search(r'^Uptime(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        total_uptime = 0
        tmp2 = re.search(r'((\d+)h)?((\d+)m)?((\d+)\.\d+s)?', tmp.group(2))
        if tmp2:
            total_uptime += int(tmp2.group(2)) * 3600 if tmp2.group(2) is not None else 0
            total_uptime += int(tmp2.group(4)) * 60 if tmp2.group(4) is not None else 0
            total_uptime += int(tmp2.group(6)) if tmp2.group(6) is not None else 0

        collection['host_uptime'] = total_uptime

    tmp = re.search(r'^Role(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['host_role'] = tmp.group(2)

    tmp = re.search(r'^Site Mode(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['site_mode'] = tmp.group(2)

    tmp = re.search(r'^Site State(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['site_state'] = tmp.group(2)

    tmp = re.search(r'^Controller Connection(\t)+:\s(.*?)$', output, re.MULTILINE)
    if tmp:
        collection['controller_connection'] = tmp.group(2)

    tmp = re.search(r'^Controller(\t)+:\s(.*?)\nMIC Certificate', output, re.MULTILINE | re.DOTALL)
    if tmp:
        collection['controller'] = tmp.group(2).replace('\n', '')

    return True, collection
