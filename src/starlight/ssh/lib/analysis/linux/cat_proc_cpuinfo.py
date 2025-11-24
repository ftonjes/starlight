import re
import pprint


def analyze(output, collection=None):

    """

        Linux - 'cat /proc/cpuinfo' command analysis

    :param output: output from 'cat /proc/cpuinfo' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'cat /proc/cpuinfo' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'cat /proc/cpuinfo' output from a Linux device
    # Regex: '^cat /proc/cpuinfo$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'cat /proc/cpuinfo' command should be in string format."

    # START

    tmp = re.compile(r'(processor.*?)\n\n', re.MULTILINE | re.DOTALL)
    cpu_info = {}
    current_cpu = None
    for cpu in re.findall(tmp, output + '\n\n'):
        info = {}
        for line in cpu.split('\n'):
            kv = line.split(':')
            key = kv[0].replace('\t', '').strip()
            value = kv[1].strip()
            if re.search(r'^\d+$', value):
                value = int(kv[1])
            elif value == '':
                value = None
            elif value.lower() == 'yes':
                value = True
            elif value.lower() == 'no':
                value = False
            if key in ['flags', 'bugs']:
                value = sorted(kv[1].strip().split(' '))

            if key == 'processor':
                if value not in cpu_info:
                    cpu_info[value] = {}
                    current_cpu = value
            else:
                info[key] = value

        cpu_info[current_cpu] = info

    if len(cpu_info) > 0:
        collection['cpu_info'] = cpu_info

    return True, collection
