import re


def analyze(output, collection=None):

    """

        Netscout - 'showserial' command analysis

    :param output: output from 'showserial' on an Opengear device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'showserial' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'showserial' output from an Opengear device
    # Regex: '^showserial$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'showserial' command should be in string format."

    collection['host_vendor'] = 'Opengear'
    collection['os_type'] = 'og_os'

    # START

    # Shows just the serial number
    if 'command not found' not in output:
        collection['host_serial_number'] = str(output).strip()

    return True, collection
