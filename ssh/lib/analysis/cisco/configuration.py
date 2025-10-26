"""

    Configuration for Cisco devices

"""


# Identify device by SSH version
SSH_VERSIONS = [
    {
        'regex': r'^(SSH-.*?-Cisco-\d.*?)$',
        'vendor': 'cisco'
    }
]

# RegEx to detect prompts
SSH_PROMPTS = [
    {
        'regex': r'^((.*?)(#|>))$',
        'extract': ['prompt', 'hostname', 'mode'],
        'vendor': 'cisco',
        'commands': ['show version'],
        'known_errors': [r'^bash: .*?: (command not found)$']
        }
]

# Console activity to auto-respond to:
SSH_AUTO_RESPONSE = [
    {
        'regex': r'^ --More-- $',
        'send': ' ',
    }
]