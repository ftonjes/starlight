import re


def analyze(output, collection=None):

    """

        Linux - 'cat /etc/*-release' command analysis

    :param output: output from 'cat /etc/*-release' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'cat /etc/*-release' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'cat /etc/*-release' output from a Linux device
    # Regex: '^cat /etc/\*-release$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'cat /etc/*-release' command should be in string format."

    # START

    # NOTE: This output varies depending on linux distribution:
    linux_info = {}
    for item in output.split('\n'):
        tmp = re.search(r'^(.*?)=(.*)$', item)
        if tmp:
            linux_info[tmp.group(1).lower()] = tmp.group(2).replace('"', '')

    if len(linux_info) > 0:
        collection['linux_info'] = linux_info

    return True, collection
