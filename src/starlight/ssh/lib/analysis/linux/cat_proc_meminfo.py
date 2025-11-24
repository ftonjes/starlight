

def analyze(output, collection=None):

    """

        Linux - 'cat /proc/meminfo' command analysis

    :param output: output from 'cat /proc/meminfo' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'cat /proc/meminfo' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'cat /proc/meminfo' output from a Linux device
    # Regex: '^cat /proc/meminfo$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'cat /proc/meminfo' command should be in string format."

    # START

    mem_info = {}
    for line in output.split('\n'):
        kv = line.replace(' kB', '').split(':')
        if len(kv) == 2:
            key = kv[0].replace('\t', '').strip()
            value = kv[1].strip()
            mem_info[key] = int(value)

    if len(mem_info) > 0:
        collection['mem_info'] = mem_info

    return True, collection
