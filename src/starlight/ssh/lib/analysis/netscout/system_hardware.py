import re


def analyze(output, collection=None):

    """

        Netscout - 'system hardware' command analysis

    :param output: output from 'system hardware' on a Netscout device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'system hardware' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'system hardware' output from a Netscout device
    # Regex: '^(sys|system) hardware'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'system hardware' command should be in string format."

    collection['host_vendor'] = 'Netscout'
    collection['_host_name_extraction'] = "^.*?@(.*?):/"
    collection['os_type'] = 'arb_os'

    # START

    tmp = re.search(r'\nSystem Model Number: (.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_model'] = tmp.group(1)

    tmp = re.search(r'\nSerial Number: (.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_serial_number'] = tmp.group(1)

    # Boot time: Tue Jan 12 14:29:18 2021, 967 days 19:58 ago
    # Boot time: Sun Aug 06 09:55:49 2023, 32 days 50 min ago
    tmp = re.search(
        r'Boot time: (Sun|Mon|Tue|Wed|Thu|Fri|Sat)\s.*?,( (\d+) days)? ((\d+)\smin|(\s?\d+):(\d+)) ago', output)
    if tmp:
        if tmp.group(5) is not None:
            collection['host_uptime'] = int(tmp.group(3)) * 86400 + int(tmp.group(5)) * 60
        else:
            collection['host_uptime'] = int(tmp.group(3)) * 86400 + int(tmp.group(6)) * 3600 + int(tmp.group(7)) * 60

    tmp = re.search(r'\nProcessor: (.*?)\n', output, re.MULTILINE)
    if tmp:
        collection['host_processor'] = tmp.group(1)

    tmp = re.compile(r'Memory Device: (\d+) (.*?) NODE \d+ (CPU\d+_)?DIMM_', re.MULTILINE)
    collection['host_total_memory'] = 0

    for memory, unit, _ in re.findall(tmp, output):
        collection['host_total_memory'] += int(memory)
        collection['host_total_memory_unit'] = unit

    return True, collection
