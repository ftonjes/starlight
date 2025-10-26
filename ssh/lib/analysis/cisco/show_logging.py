import re
from pprint import pprint
from ssh.lib.processors.write_to_sqlite3_db import sql


def analyze(output, collection=None):

    """

        Cisco - 'show logging' command analysis

    :param output: output from 'show logging' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show logging' command
    """
    # Version: 1.0 - Initial version
    # Description: Analyze 'show logging' output from a Cisco device
    # Regex: '^show logging$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show interface' command should be in string format."

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    collection['log_messages'] = []
    # START

    # Add an extra line so regex can catch the last interface!
    output += '\n'

    syslog_msg_types = []
    search_str = re.compile(r'(.*?)\s+(%[A-Z].*?-\d+-.*?):\s(.*?)\n')
    for timestamp, log_type, info in re.findall(search_str, output):
        if log_type not in syslog_msg_types:
            syslog_msg_types.append(log_type)
            sql_qry = "INSERT INTO syslog (msg_type, info) VALUES (?, ?)"
            sql_vals = [log_type, info]
            sql(sql_qry, tuple(sql_vals, ))

    return True, collection
