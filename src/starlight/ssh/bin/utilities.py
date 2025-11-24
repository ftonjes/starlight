import re


def strip_ansi(text):

    """

        Strips AXTC escape codes from text.

    :param text: text containing escape codes
    :return: string
    """

    axtc_regex = r'\x1B(?:[@-Z\\-_][0-9];~\x07|\[[0-?]*[ -/]*[@-~])'
    axtc_escape = re.compile(axtc_regex, flags=re.IGNORECASE)

    return axtc_escape.sub('', text)
