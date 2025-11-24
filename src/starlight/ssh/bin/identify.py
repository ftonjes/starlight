"""

    Identify devices via SSH using prompt, verion, headers, banner, etc using regular expressions.

"""

import re


def id_by_prompt(prompt_string):

    # Check prompt to determine information about the host:
    for prompt in SSH_PROMPTS:
        # print(prompt['regex'])
        tmp = re.search(prompt['regex'], prompt_string)
        if tmp:
            result = {}
            for key in prompt.keys():
                if key == 'extract':
                    for item_index, item in enumerate(prompt[key]):
                        try:
                            result[item] = tmp.group(item_index + 1)
                        except AttributeError:
                            pass
                else:
                    result[key] = prompt[key]
            return result

    return False


def id_by_ssh_version(version_string):

    # Check version string to determine information about device.
    for string in SSH_VERSIONS:
        tmp = re.search(string['regex'], version_string)
        if tmp:
            result = {}
            for key in string.keys():
                result[key] = string[key]
            return result

    return False


def auto_reponse(prompt_string):

    # Auto-respond to output configured with 'SSH_AUTO_RESPONSE'
    response = False
    for prompt in SSH_AUTO_RESPONSE:
        tmp = re.search(prompt['find'], prompt_string)
        if tmp:
            prompt['found'] = tmp.group(0)
            return prompt

    return response


# Identify device by SSH version
SSH_VERSIONS = [
{
        'regex': r'^(SSH-.*?-Cisco-\d.*?)$',
        'vendor': 'cisco'
    },
    {
        'regex': r'^(SSH-.*[Uu]buntu\d.*?)$',
        'vendor': 'ubuntu'
    },

]

# Identify properties by SSH prompt
SSH_PROMPTS = [

    # Aruba Wireless Controllers
    {
        'regex': r'^(\((.*?)\)\s+\*#)$',
        'extract': ['prompt', 'hostname'],
        'vendor': 'Aruba',
        'commands': ['show version', 'show inventory'],
        'known_errors': [r'% (Invalid input detected) at \'\^\' marker\.']
    },

    # Linux hosts
    {
        'regex': r'^((.+)@(.+):(.*?)\$\s+)$',
        'extract': ['prompt', 'username', 'hostname', 'path'],
        'vendor': 'linux',
        'os': 'linux',
        'shell': 'bash',
        'commands': ['cat /etc/os-release', 'echo $SHELL'],
        'known_errors': [
            r'^bash: .*?: (command not found)$',
            r'^.*?: can\'t open \'.*?\': (No such file or directory)',
        ]
    },
    {
        'regex': r'^(\$\s+)$',
        'extract': ['prompt'],
        'os': 'linux',
        'shell': 'ksh',
        'commands': ['cat /etc/os-release', 'echo $SHELL'],
        'known_errors': [
            r'^bash: .*?: (command not found)$',
            r'^.*?: can\'t open \'.*?\': (No such file or directory)',
        ]
    },

    # Apple MacOS
    {
        'regex': r'^((.*?)@(.*?):(.*))\s+$',
        'extract': ['prompt', 'username', 'hostname', 'path'],
        'os': 'darwin',
        'shell': 'bash',
        'commands': ['cat /etc/os-release', 'echo $SHELL'],
        'known_errors': [
            r'^bash: .*?: (command not found)$',
            r'^.*?: can\'t open \'.*?\': (No such file or directory)',
        ]
    },

    # F5 devices
    {
        'regex': r'^((.*?)@\((.*?)\)\(.*?\)\(.*?\)\(.*?\)\s?\(tmos\)#\s+)$',
        'extract': ['prompt', 'username', 'hostname'],
        'vendor': 'f5',
        'commands': ['show sys version', 'show sys hardware', 'show info'],
        'known_errors': []
    },

    # Cisco or Arista devices
    {
        'regex': r'^((.*?)(#|>))$',
        'extract': ['prompt', 'hostname', 'mode'],
        'vendor': 'arista|cisco',
        'commands': ['show version'],
        'known_errors': []
    },

    # User '.*?' does not have shell access on this device  (Opengear)
]

# Console activity to auto-respond to
SSH_AUTO_RESPONSE = [
    {
        'find': r'^--More-- \(q\) quit \(u\) pageup \(/\) search \(n\) repeat $',
        'reply_with': ' ',
        'clean': r'--More-- \(q\) quit \(u\) pageup \(/\) search \(n\) repeat\s{51}'
    },
    {
        'find': r'^ --More-- $',
        'reply_with': ' ',
        'clean': r' --More-- (\x08){9}\s+(\x08){8}'
    },
    {
        'find': r'Display all \d+ items\? \(y/n\)\s+$',
        'reply_with': 'y',
    },
    {
        'find': r'^---\(less\s+\d+%\)---$',
        'reply_with': ' ',
    },
    {
        'find': r'^lines \d+-\d+ |lines \d+-\d+/\d+ \(END\) $',
        'reply_with': ' ',
    },
    {
        'find': r'^\(END\)$',
        'reply_with': 'q',
    },
]
