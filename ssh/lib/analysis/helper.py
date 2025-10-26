import re


"""

    This module is intended to help in identifying a device to then be able to redirect to the correct module.
    This is used only when the os_type is set to 'auto' (an indication that an attempt should be made to auto-detect.
    the device)

"""


def check_prompt(prompt, collection=None):

    # Some devices have prompts that can indicate what vendor produced it:
    # Information returned can be one of the following:
    #
    # vendor:                    Name of the vendor (str)
    # command_list:              Replace remaining command list (list)
    # extend_command_list:       Append commands at the end of the existing command list

    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(prompt, str):
        return False, "Prompt output should be in string format."

    valid = False
    extend_command_list = []
    prepend_command_list = []
    vendor = None
    might_be = []
    error = False
    prompt_filter = None

    # Check ssh_settings to see if host might use a Cisco version of SSH:
    if '_session_info' in collection:
        if 'ssh_settings' in collection['_session_info']:
            if 'version' in collection['_session_info']['ssh_settings']:
                if re.search(r"SSH.*-Cisco-\d", collection['_session_info']['ssh_settings']['version']):
                    if 'terminal length 0' not in prepend_command_list:
                        prepend_command_list.append('terminal length 0')
                    if 'show version' not in prepend_command_list:
                        prepend_command_list.append('show version')

                    # Cisco REGEX: ^(.*?)(\(.*?\))?([#>])(.*)$
                    # 1: Device Name 2: Config Mode 3: prompt 4: Command
                    prompt_filter = {
                        're': r'^((.*)\n)?(.*?(\((.*)\))?[#>](\s+)?)$', 'response': 1, 'prompt': 3, 'mode': 5}
                    vendor = 'Cisco'
                    valid = True

    # ::Palo Alto::  svc-ens-ipfabric-ro@tuisbl-04fwh01(active)>
    if re.search(r'^(.*?@(.*?)(\((.*)\))?>\s+)$', prompt):
        vendor = 'Palo Alto'
        prompt_filter = {
                're': r'^((.*)\n)?(.*?@(.*?)(\((.*)\))?[#>](\s+)?)$', 'response': 1, 'prompt': 3}
        if 'set cli scripting-mode on' not in prepend_command_list:
            prepend_command_list.append('set cli scripting-mode on')
        if 'show system info' not in prepend_command_list:
            prepend_command_list.append('show system info')
        valid = True

    # ::F5::  '<USER>@(<HOST>)(cfg-sync In Sync)(/S2-green-P:Standby)(/Common)(tmos)#' = f5 BIG-IP
    # F5 will have username in prompt, which is available in collection['_session_info']['authentication']:
    elif re.search(r'^.*?@\(.*?\)\(.*?\)\(.*?\)\(.*?\).*?\(.*?tmos.*?\).*?#\s?$', prompt):

        vendor = 'F5'
        prompt_filter = {
            're': r'^(.*?\n)?(<<username>>@\(.*?\)\(.*?\)\(.*?\)\(.*?\)\s?\(tmos\)#\s)$',
            'response': 1, 'prompt': 2}
        if 'show sys version' not in prepend_command_list:
            prepend_command_list.append('show sys version')
        if 'show sys hardware' not in prepend_command_list:
            prepend_command_list.append('show sys hardware')
        if "run util bash -c 'cat /proc/uptime'" not in prepend_command_list:
            prepend_command_list.append("run util bash -c 'cat /proc/uptime'")
        valid = True

    # ::F5:: When disk is full we see this erron on an F5:
    elif re.search(r"Can't create temp directory, /var.* No space left on device\)", prompt):
        vendor = 'F5'
        error = 'Device OS issue: No space left on device.'
        valid = True

    # ::Riverbed:: 'HOSTNAME > '
    elif re.search(r"^.*?\s>\s$", prompt):
        vendor = 'Riverbed'
        prompt_filter = {
            're': rf"^(.*?\n)?(.*?\s>\s)$", 'response': 1, 'prompt': 2}
        if 'show version' not in prepend_command_list:
            prepend_command_list.append('show version')
        if 'show info' not in prepend_command_list:
            prepend_command_list.append('show info')
        valid = True

    # ::Netscout / Arbor::
    # svc-ens-cspc-ro@ausyd9-01an01:/#
    elif re.search(r"^.*?@.*:/#\s+", prompt):
        vendor = 'Netscout'
        if 'system version' not in prepend_command_list:
            prepend_command_list.append('system version')
        if 'system hardware' not in prepend_command_list:
            prepend_command_list.append('system hardware')
        if 'ip interfaces show' not in prepend_command_list:
            prepend_command_list.append('ip interfaces show')
        if 'system license show' not in prepend_command_list:
            prepend_command_list.append('system license show')
        prompt_filter = {
            're': rf"^((.*)\n)?({collection['_session_info']['authentication']['username']}@.*?:/#\s+)$",
            'response': 1, 'prompt': 3}
        valid = True

    # ::Linux::
    elif re.search(r"^((.*)\n)?(\[(.*?)@(.*?)\s+?(.*?)][#$]\s+?)", prompt):
        prompt_filter = {'re': r'^((.*)\n)?(.*?@.*?)$', 'response': 1, 'prompt': 3}
        might_be.extend(['Linux'])
        if 'uname -a' not in prepend_command_list:
            prepend_command_list.append('uname -a')
        if 'cat /etc/os-release' not in prepend_command_list:
            prepend_command_list.append('cat /etc/os-release')
        if 'cat /proc/uptime' not in prepend_command_list:
            prepend_command_list.append('cat /proc/uptime')
        if 'cat /proc/meminfo' not in prepend_command_list:
            prepend_command_list.append('cat /proc/meminfo')
        if 'cat /proc/cpuinfo' not in prepend_command_list:
            prepend_command_list.append('cat /proc/cpuinfo')
        if 'ps -ef' not in prepend_command_list:
            prepend_command_list.append('ps -ef -w -w')
        valid = True

    # ::Linux::
    elif re.search(r"^((.*)\n)?((.*?)@(.*?):(.*?)#\s+?)", prompt):
        prompt_filter = {'re': r'^((.*)\n)?((.*?@.*?):(.*?)#\s+?)$', 'response': 1, 'prompt': 3}
        might_be.extend(['Linux'])
        if 'uname -a' not in prepend_command_list:
            prepend_command_list.append('uname -a')
        if 'cat /etc/os-release' not in prepend_command_list:
            prepend_command_list.append('cat /etc/os-release')
        if 'cat /proc/uptime' not in prepend_command_list:
            prepend_command_list.append('cat /proc/uptime')
        if 'cat /proc/meminfo' not in prepend_command_list:
            prepend_command_list.append('cat /proc/meminfo')
        if 'cat /proc/cpuinfo' not in prepend_command_list:
            prepend_command_list.append('cat /proc/cpuinfo')
        if 'ps -ef' not in prepend_command_list:
            prepend_command_list.append('ps -ef -w -w')
        valid = True

    # ::Cisco::, ::PaloAlto::, ::Cloudgenix::  or ::Arista:: (# or >)
    elif re.search(r"^(.*?[#>](\s+)?)$", prompt):
        if re.search(r">", prompt):
            if 'enable' not in prepend_command_list:
                prepend_command_list.append('enable')
        if 'terminal length 0' not in prepend_command_list:
            prepend_command_list.append('terminal length 0')
        if 'show version' not in prepend_command_list:
            prepend_command_list.append('show version')
        if 'dump overview' not in prepend_command_list:
            prepend_command_list.append('dump overview')
        prompt_filter = {'re': r'^((.*)\n)?(.*?[#>](\s+)?)$', 'response': 1, 'prompt': 3}
        might_be.extend(['cisco', 'arista', 'paloalto', 'cloudgenix'])
        valid = True

    # Linux Host Last login
    elif re.search(r"^Last login: .*? from (.*?)\n\$ $", prompt):
        prompt_filter = {'re': r'^(.*)?(.*?@.*?)$', 'response': 1, 'prompt': 2}
        might_be.extend(['Linux'])
        valid = True

    # ::Linux:: (or ::Opengear::)
    elif re.search(r"^(.*\$ )$", prompt):
        might_be.extend(['linux'])
        prompt_filter = {'re': r'^((.*)\n)?(.*?\$\s+)', 'response': 1, 'prompt': 3}
        if 'cat /etc/os-release' not in prepend_command_list:
            prepend_command_list.append('cat /etc/os-release')
        if 'uname -a' not in prepend_command_list:
            prepend_command_list.append('uname -a')
        if 'cat /proc/uptime' not in prepend_command_list:
            prepend_command_list.append('cat /proc/uptime')
        if 'cat /proc/meminfo' not in prepend_command_list:
            prepend_command_list.append('cat /proc/meminfo')
        if 'cat /proc/cpuinfo' not in prepend_command_list:
            prepend_command_list.append('cat /proc/cpuinfo')
        if 'ps -ef' not in prepend_command_list:
            prepend_command_list.append('ps -ef -w -w')
        valid = True

    # ::Aruba:: Wireless Controller
    elif re.search(r"^\((.*?)\)\s\*?#", prompt):
        might_be.extend(['aruba'])
        prompt_filter = {'re': r'^((.*)\n)?(\((.*?)\) \*?\#)$', 'response': 1, 'prompt': 3}
        if 'show version' not in prepend_command_list:
            prepend_command_list.append('show version')

    # Generic Errors:
    elif re.search(r"User '.*?' does not have shell access on this device", prompt):
        collection['error'] = "User does not have shell access on this device"

    # Remove duplicates from extend_command_list:
    tmp = []
    for command in extend_command_list:
        if command not in tmp:
            tmp.append(command)
    extend_command_list = tmp

    info = {'valid': valid, 'prompt': prompt}
    # if valid is False:
    #     error = f"Prompt not recognized: '{prompt}'"

    if error:
        info['error'] = error
    if len(extend_command_list) > 0:
        info['extend_command_list'] = extend_command_list
    if len(prepend_command_list) > 0:
        info['prepend_command_list'] = prepend_command_list
    if vendor is not None:
        info['vendor'] = vendor
    if len(might_be) > 0:
        info['might_be'] = might_be
    if prompt_filter is not None:
        info['prompt_filter'] = prompt_filter

    return info


def check_banner(banner, collection=None):

    # Some devices have content in the welcome banner/motd that can indicate what vendor produced it:
    # Information returned can be one of the following:
    #
    # vendor:                    Name of the vendor (str)
    # distribution:              Name of Distribution (if applicable)

    if not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(banner, str):
        return False, "Banner output should be in string format."

    if re.search(r"Welcome to Ubuntu|ubuntu.com", banner, re.MULTILINE | re.DOTALL):
        return {'vendor': 'Linux', 'distribution': 'Ubuntu'}

    elif re.search(r"OPNsense|opnsense.org", banner, re.MULTILINE | re.DOTALL):
        return {'vendor': 'Linux', 'distribution': 'OPNsense'}

    elif re.search(r"ESXi [Ss]hell|VMware|vmware.com", banner, re.MULTILINE | re.DOTALL):
        return {'vendor': 'Linux', 'distribution': 'VMware'}

    if re.search(r"Debian", banner, re.MULTILINE | re.DOTALL):
        return {'vendor': 'Linux', 'distribution': 'Debian'}


def analyze(command, output):

    """

        Checks command output and returns a dictionary containing vendor and additional instructions:
          extend_command_list: Adds commands to execute to help identify the device.

    :param command: name of command that was executed
    :param output: raw output from SSH session
    :return: single string containing name of vendor (which is used to determine which module to use for identification)
    """

    # Detect when output indicates the command is not a valid one:
    if re.search(r'([Ss]yntax [Ee]rror|[Ii]nvalid [Cc]ommand)|: [Cc]ommand not found|: [Pp]ermission denied', output):
        return {'_error': output.strip()}

    if command == 'show version':

        # print(output)
        # Cisco IOS Software, C2951 Software (C2951-UNIVERSALK9-M), Version 15.6(3)M8, RELEASE SOFTWARE (fc2)

        # ::Cisco:: Nexus, IOS
        if re.search(
                r'(Cisco Nexus Operating System \(NX-OS\) Software|'
                r'IOS \(tm\) .*? Software \(.*?\), Version .*?, .*\n|'
                r'Cisco\s+.*?\s+\(.*?\),\s+[Vv]ersion\s+.*?(,)?\s+.*?|'
                r'Cisco IOS Software)', output, re.MULTILINE | re.DOTALL):

            return {'vendor': 'Cisco'}

        # ::Riverbed::
        elif re.search(r'Product name:\s+rbt_.*?\n\nProduct model:\s+.*?\s+\(', output, re.MULTILINE | re.DOTALL):

            return {'vendor': 'Riverbed', 'prepend_command_list': ['show info']}

        # ::Arista::
        elif re.search(r'Arista .*?\nHardware version:.*?\nSerial number:', output, re.MULTILINE | re.DOTALL):

            return {'vendor': 'Arista', 'prepend_command_list': ['show info']}

    elif command in ['sys version', 'system version']:

        # ::Netscout:: Arbor Edge Defense
        if re.search(r'Version: Arbor Edge Defense', output):

            return {'vendor': 'Netscout', 'prepend_command_list': ['system hardware']}

    return None


def os_type_to_vendor():

    """
        OS type (os_type) to vendor / os_name mappings:

        'os_type': name of OS type used to analyze interactive SSH session output
        'identifier': Matches directory in /ssh/lib/analysis,
        'vendor': Vendor name (reporting and logs) and
        'os_name': Name of operating system (reporting and logs)
        'prompt_filter': Used to 'catch' the prompt when interacting with the device:
          're': contains the regular expression syntax,
          'response': Which matching regex group hosts the response/output of the most recent command,
          'prompt': The matching regex group containing the prompt,
          'mode': The 'mode' the device is in: e.g. when configuring the device (e.g. config)

    :return:
    """

    return {
            'cisco_ios': {'identifier': 'cisco', 'vendor': 'Cisco', 'os_name': 'IOS', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?(\((.*)\))?[#>](\s+)?)$', 'response': 1, 'prompt': 3, 'mode': 5}, 'commands': [
                'terminal length 0', 'show version']},
            'cisco_nxos': {'identifier': 'cisco', 'vendor': 'Cisco', 'os_name': 'NXOS', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?(\((.*)\))?[#>](\s+)?)$', 'response': 1, 'prompt': 3, 'mode': 5}},
            'arista_eos': {'identifier': 'arista', 'vendor': 'Arista', 'os_name': 'EOS', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?[#>](\\s+)?)$', 'response': 1, 'prompt': 3, 'mode': 5}},
            'f5_tmos': {'identifier': 'f5', 'vendor': 'F5', 'os_name': 'TMOS', 'prompt_filter': {
                're': r'^(.*?\n)?(<<username>>@\(.*?\)\(.*?\)\(.*?\)\(.*?\)\s?\(tmos\)#\s)$',
                'response': 1, 'prompt': 2}, 'commands': [
                'show sys version', 'show sys hardware', "run util bash -c 'cat /proc/uptime'"]},
            'arb_os': {'identifier': 'netscout', 'vendor': 'Netscout', 'os_name': 'Arbor OS', 'prompt_filter': {
                're': r'^((.*)\\n)?(svc-ens-auto-ro@.*?:/#\\s+)$', 'response': 1, 'prompt': 3}, 'commands': [
                'system version', 'system hardware']},
            'og_os': {'identifier': 'opengear', 'vendor': 'Opengear', 'os_name': 'OG_OS', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?\$\s+)', 'response': 1, 'prompt': 3}, 'commands': [
                'config -g config', 'showserial', 'cat /proc/uptime', 'config --show-config', 'config export']},
            'rb_steelhead': {'identifier': 'riverbed', 'vendor': 'Riverbed', 'os_name': 'RiOS', 'prompt_filter': {
                're': r'^(.*?\\n)?(.*?\\s>\\s)$', 'response': 1, 'prompt': 2}, 'commands': [
                'show version', 'show info']},
            'linux': {'identifier': 'linux', 'vendor': 'Linux', 'os_name': 'Linux', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?@.*?)$', 'response': 1, 'prompt': 3}, 'commands': [
                'cat /etc/version', 'uname -a']},
            'cgx_os': {'identifier': 'cloudgenix', 'vendor': 'Palo Alto', 'os_name': 'Cloudgenix OS', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?[#>](\s+)?)$', 'response': 1, 'prompt': 3}, 'commands': [
                'dump overview']},
            'aruba_os': {'identifier': 'aruba', 'vendor': 'Aruba', 'os_name': 'Aruba OS', 'prompt_filter': {
                're': r'^((.*)\n)?(\((.*?)\) \*?\#)$', 'response': 1, 'prompt': 3}, 'commands': [
                'show version']},
            'pan_os': {'identifier': 'paloalto', 'vendor': 'Palo Alto', 'os_name': 'PAN_OS', 'prompt_filter': {
                're': r'^((.*)\n)?(.*?@(.*?)(\((.*)\))?[#>](\s+)?)$', 'response': 1, 'prompt': 3}, 'commands': [
                'set cli scripting-mode on', 'show system info']},
           }
