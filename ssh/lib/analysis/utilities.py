import os
import datetime
import re
import keyring
from pprint import pprint

""" 

    utilities.py - Library of common functions used by the parser scripts. 

"""


def get_creds(keywrd):

    """
        Get Credentials: First check keyring to find credential information. If it is not found, then check if the
                           environment variable exists and use that. If neither are found, return False.

        Note: On Windows systems, 'Internet or network address' and 'User name' should both be populated with the
                key name, e.g.: NETBOX_URL. The 'Password' should store the secure info. (password, token, etc.)
    """

    if keywrd in os.environ:
        return os.environ[keywrd]

    pw = keyring.get_password(keywrd, keywrd)
    if pw is None:
        build_pw = ''
        for n in range(1, 999):
            keywrd_id = f"{keywrd}_{str(n)}"
            pw = keyring.get_password(keywrd_id, keywrd_id)
            if pw is not None:
                build_pw += pw
            else:
                if build_pw != '':
                    return build_pw
                else:
                    return False
    else:
        return pw

    return False


def date_time_delta(start_time, end_time):

    """

        Works out the time (in seconds) between two datetime timestamps.

    :param start_time: Start time in datetime() format.
    :param end_time: End time in datetime() format.
    :return: delta in seconds
    """

    seconds = divmod((end_time - start_time).days * 86400 + (end_time - start_time).seconds, 60)
    delta = seconds[0] * 60 + seconds[1]

    return delta


def uptime_to_seconds(uptime):

    """

        Convert uptime to seconds. (difference in seconds between now and converted seconds)

    :param uptime: string containing uptime e.g.: '628d 3h 39m 8s'
    :return: number of seconds
    """

    seconds = 0
    uptime = f" {uptime} "
    tmp = re.search(r'(\d+) year', uptime)
    if tmp:
        seconds += int(tmp.group(1)) * 31536000
    tmp = re.search(r'(\d+) week', uptime)
    if tmp:
        seconds += int(tmp.group(1)) * 604800
    tmp = re.search(r'(\d+) day', uptime)
    if tmp:
        seconds += int(tmp.group(1)) * 86400
    tmp = re.search(r'^ (\d+)d ', uptime)
    if tmp:
        seconds = int(tmp.group(1)) * 86400
    tmp = re.search(r'(\d+) hour| (\d+)h ', uptime)
    if tmp:
        seconds += int(tmp.group(1)) * 3600 if tmp.group(1) is not None else int(tmp.group(2)) * 3600
    tmp = re.search(r'(\d+) minute| (\d+)m ', uptime)
    if tmp:
        seconds += int(tmp.group(1)) * 60 if tmp.group(1) is not None else int(tmp.group(2)) * 60

    tmp = re.search(r'(\d+) second| (\d+)s ', uptime)
    if tmp:
        seconds += int(tmp.group(1)) if tmp.group(1) is not None else int(tmp.group(2))

    return seconds


def list_to_string(item_list, and_or='and', quote='"'):

    """

        Converts a list of strings into a string. e.g.: ['A', 'B', 'C'] becomes "'A', 'B' or 'C'." if and_or is 'or'.

    :param item_list: List of items
    :param and_or: Use 'and' or 'or' between last and second-last item.
    :param quote: Use single or
    :return: string
    """

    list_str = ''
    for index, item in enumerate(item_list):

        list_str += f"{quote}{item}{quote}"

        if index < (len(item_list) - 2):

            list_str += ', '

        elif index == len(item_list) - 2:

            if and_or in ['and', 'or']:
                list_str += f' {and_or} '
            else:
                list_str += f', '

    return list_str


def seconds_to_summary_string(seconds, granularity=3):

    intervals = (('y', 31557600), ('w', 604800), ('d', 86400), ('h', 3600), ('m', 60), ('s', 1))
    seconds = int(seconds)

    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{}{}".format(value, name))

    return ', '.join(result[:granularity])