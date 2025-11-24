import re


def analyze(output, collection=None):

    """

        Linux - 'uname -a' command analysis

    :param output: output from 'uname -a' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'uname -a' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'uname -a' output from a Linux device
    # Regex: '^uname -a$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'uname -a' command should be in string format."

    # START

    tmp = re.search(r'^[Ll]inux\s+(.*?)\s+(\d.*?)\s+(.*?\d+:\d+:\d+.*?\d+)\s+(.*?)\s+(.*?\s+)?(.*?\s+)?(.*?)$', output)
    if tmp:
        collection['host_system_name'] = tmp.group(1)
        collection['linux'] = {
            'kernel_release': tmp.group(2),
            'kernel_version': tmp.group(3),
            'processor_type': tmp.group(4),
            'hardware_platform': tmp.group(5),
            'architecture': tmp.group(6),
            'os_type': tmp.group(7)}

        if re.search(r'^arm', tmp.group(4)):
            collection['prepend_command_list'] = ['cat /etc/version']

    else:
        tmp = re.search(r'^[Ll]inux\s+(.*?)\s+(\d.*?)\s+(.*)\s+(.*?)\s+?(.*?\s+)?(.*?)$',
                        output)
        if tmp:
            collection['host_system_name'] = tmp.group(1)
            collection['linux'] = {
                'kernel_release': tmp.group(2),
                'kernel_version': tmp.group(3),
                'processor_type': tmp.group(4),
                'os_type': tmp.group(5)}

    collection['host_vendor'] = 'Linux'
    collection['os_type'] = 'linux'

    return True, collection
