import re


def analyze(output, collection=None):

    """

        Linux - 'cat /etc/version' command analysis

    :param output: output from 'cat /etc/version' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'cat /etc/version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'cat /etc/version' output from a Linux device
    # Regex: '^cat /etc/version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'cat /etc/version' command should be in string format."

    # START
    prepend_command_list = []

    # NOTE: A lot of vendors run linux, so we need to look and change the vendor appropriately:

    # OpenGear/CM71xx Version 4.5.0 b9bc8238 -- Fri Apr 26 00:31:07 UTC 2019
    tmp = re.search(r'^OpenGear/(.*?)\s+Version\s+(.*?)\s+(.*?)\s+--\s+(.*?)$', output)
    if tmp:
        collection['host_model'] = tmp.group(1)
        collection['host_software_version'] = tmp.group(2)
        collection['host_software_revision'] = tmp.group(3)
        collection['host_vendor'] = 'Opengear'
        collection['os_type'] = 'og_os'

        collection['remove_next_command_list'] = ['uname -a']
        if 'config -g config' not in prepend_command_list:
            prepend_command_list.append('config -g config')
        if 'showserial' not in prepend_command_list:
            prepend_command_list.append('showserial')
        # if 'cat /proc/uptime' not in prepend_command_list:
        #     prepend_command_list.append('cat /proc/uptime')

    tmp = re.search(f"^Linux (.*?)\s+(.*?).*\s+(x86_64)\s+(x86_64)\s+(x86_64)\s+(.*?)$", output)
    if tmp:
        collection['host_name'] = tmp.group(1)
        collection['host_software_version'] = tmp.group(2)
        collection['host_architecture'] = tmp.group(3)
        collection['host_vendor'] = 'Linux'
        collection['os_type'] = 'linux'

        # Get additional OS information
        prepend_command_list.append('cat /etc/os-release')

    if len(prepend_command_list) > 0:
        collection['prepend_command_list'] = prepend_command_list

    return True, collection
