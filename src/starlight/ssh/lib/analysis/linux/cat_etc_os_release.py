import re


def analyze(output, collection=None):

    """

        Linux - 'cat /etc/os-release' command analysis

    :param output: output from 'cat /etc/os-release' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'cat /etc/os-release' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'cat /etc/os-release' output from a Linux device
    # Regex: '^cat /etc/os-release$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'cat /etc/os-release' command should be in string format."

    if output == "cat: can't open '/etc/os-release': No such file or directory":
        collection['_error'] = "cat: can't open '/etc/os-release': No such file or directory"

    # START
    tmp = re.compile(r'^(.*?)=[\'"](.*)[\'"]$', re.MULTILINE)
    for key, value in tmp.findall(output):
        if 'linux' not in collection:
            collection['linux'] = {}
        if 'os_release' not in collection['linux']:
            collection['linux']['os_release'] = {}

        collection['linux']['os_release'][key.lower()] = value.strip()

    vendor_list = ['Oracle', 'Redhat', 'Debian', 'Ubuntu', 'FreeBSD', 'CentOS Linux']

    if 'linux' in collection:
        if 'os_type' in collection:
            if collection['os_type'] is None:
                collection['os_type'] = 'linux'
        else:
            collection['os_type'] = 'linux'
        if 'os_release' in collection['linux']:
            if 'host_software_type' not in collection:
                collection['host_software_type'] = 'Linux'
            if 'pretty_name' in collection['linux']['os_release']:
                collection['host_model'] = collection['linux']['os_release']['pretty_name']
                for vendor in vendor_list:
                    if vendor.lower() in collection['linux']['os_release']['pretty_name'].lower():
                        collection['host_vendor'] = vendor
                        break
            if 'version' in collection['linux']['os_release']:
                collection['host_software_version'] = collection['linux']['os_release']['version']
            if 'variant' in collection['linux']['os_release']:
                collection['host_software_release_type'] = collection['linux']['os_release']['variant']

    return True, collection
