import re


def analyze(output, collection=None):

    """

        Linux - 'ps -ef -w -w' command analysis

    :param output: output from 'ps -ef' on a Linux device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'ps -ef' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'ps -ef -w -w' output from a Linux device
    # Regex: '^ps -ef -w -w$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'ps -ef' command should be in string format."

    # START
    field_list = []
    processes = []

    for index, line in enumerate(output.split('\n')):

        row = line.split(' ')
        tmp = row.copy()
        for item in tmp:
            if item == '':
                row.remove('')

        if index == 0:
            field_list = row
        else:
            proc_info = {}
            for field_index, item in enumerate(row):
                if field_index <= len(field_list) - 1:
                    proc_info[field_list[field_index]] = item
                else:
                    proc_info[field_list[len(field_list) - 1]] = f"{proc_info[field_list[len(field_list) - 1]]} {item}"

            processes.append(proc_info)

    if len(processes) > 0:
        if 'linux' not in collection:
            collection['linux'] = {}
        collection['linux']['active_processes'] = processes

    return True, collection
