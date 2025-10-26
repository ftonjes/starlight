import re
from datetime import datetime
from ssh.lib.analysis.utilities import date_time_delta
from ssh.lib.analysis.utilities import uptime_to_seconds


def analyze(output: str, collection):

    """
    
        Cisco - 'show version' command analysis
    
    :param output: output from 'show version' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show version' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show version' output from a Cisco device
    # Regex: '^show version$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show version' command should be in string format."

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    if re.search(r"Cisco Nexus Operating System \(NX-OS\) Software", output, re.MULTILINE):
        collection['os_type'] = 'cisco_nxos'
        collection['host_vendor'] = 'Cisco'

    # IOS (tm) s72033_rp Software (s72033_rp-ADVENTERPRISEK9_WAN-M), Version 12.2(18)SXF11, RELEASE SOFTWARE (fc1)
    tmp = re.search(r"IOS \(tm\) (.*?) Software \((.*?)\), Version (.*?), (.*)\n", output, re.MULTILINE | re.DOTALL)
    if tmp:
        collection['host_software_name'] = tmp.group(1).replace('  ', ' ')
        collection['host_software_type'] = tmp.group(2)
        collection['host_software_version'] = tmp.group(3)
        collection['host_software_release_type'] = tmp.group(4)
        collection['os_type'] = 'cisco_ios'
        collection['host_vendor'] = 'Cisco'

    # Cisco IOS Software [Gibraltar], Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.12.4
    #   , RELEASE SOFTWARE (fc5)
    # Cisco IOS Software, IOS-XE Software, Catalyst 4500 L3 Switch  Software (cat4500es8-UNIVERSALK9-M)
    #   , Version 03.08.04.E RELEASE SOFTWARE (fc2)
    tmp = re.search(
        r"^(Cisco\s+.*?)\s+\((.*?)\),\s+[Vv]ersion\s+(.*?)(,)?\s+(.*?)$", output, re.MULTILINE)
    if tmp:
        collection['host_software_name'] = tmp.group(1).replace('  ', ' ')
        collection['host_software_type'] = tmp.group(2)
        collection['host_software_version'] = tmp.group(3)
        collection['host_software_release_type'] = tmp.group(5)
        collection['host_vendor'] = 'Cisco'

    if re.search(r'(Cisco IOS Software|Cisco Internetwork Operating System Software)', output, re.MULTILINE):
        collection['os_type'] = 'cisco_ios'
        collection['host_vendor'] = 'Cisco'

    elif re.search(r'Cisco Nexus Operating System \(NX-OS\) Software', output):
        collection['os_type'] = 'cisco_nxos'
        collection['host_software_name'] = 'Cisco Nexus Operating System (NX-OS) Software'

    if 'os_type' in collection:

        if collection['os_type'] == 'cisco_ios':

            tmp = re.search(
                r'^Cisco\s+(.*?)\s+\(revision\s+(\d+.*?)\) with (\d+)K/(\d+)K bytes of memory',
                output, re.MULTILINE)
            if tmp:
                collection['host_model'] = tmp.group(1)
                collection['host_model_revision'] = tmp.group(2)
                collection['host_memory'] = int(tmp.group(3)) + int(tmp.group(4))
                collection['host_memory_unit'] = 'K'

            # cisco WS-C4510R+E (MPC8572) processor (revision 10) with 2097152K bytes of physical memory.
            tmp = re.search(
                r"^[Cc]isco\s+(.*?)(\s+\((.*?)\))?(\s+processor)?(\s+\(revision\s+(.*?)\))?\s+with\s+(.*?)"
                r"\s+bytes of( physical)? memory\.$", output, re.MULTILINE)
            if tmp:
                if tmp.group(1) is not None:
                    collection['host_model'] = tmp.group(1)

                if tmp.group(3) is not None:

                    tmp2 = re.search(r"^revision\s(.*)$", tmp.group(3))
                    if tmp2:
                        collection['host_processor_revision'] = tmp2.group(1)
                    else:
                        collection['host_processor_model'] = tmp.group(3)

                if tmp.group(6) is not None:
                    collection['host_processor_revision'] = tmp.group(6)

                collection['host_memory_physical'] = tmp.group(7).replace('K', '').replace('M', '')

            tmp = re.search(r"^\sCPU:\s+(.*?),\sVersion: (\d.*),\s\(.*\)$", output, re.MULTILINE)
            if tmp:
                collection['host_processor_revision'] = tmp.group(1)
                collection['host_processor_version'] = tmp.group(2)

            tmp = re.search(r"^\sCORE:\s+(.*?),\sVersion: (\d.*),\(.*\)$", output, re.MULTILINE)
            if tmp:
                collection['host_processor_core_type'] = tmp.group(1)
                collection['host_processor_core_version'] = tmp.group(2)

            tmp = re.search(r"^\sCPU:(.*?[MG]Hz),\sCCB:(\d.*MHz),\sDDR:(\d.*MHz)$", output, re.MULTILINE)
            if tmp:
                collection['host_processor_speed'] = tmp.group(1)
                collection['host_processor_ccb_speed'] = tmp.group(2)
                collection['host_processor_ddr_speed'] = tmp.group(3)

            # INMUM1-12AS01 uptime is 21 weeks, 3 days, 11 hours, 28 minutes
            tmp = re.search(
                r"^(.*?) uptime is (\d.*?)$", output, re.MULTILINE)
            if tmp:
                collection['host_system_name'] = tmp.group(1).strip()
                collection['host_uptime'] = uptime_to_seconds(tmp.group(2))
                collection['host_restarted'] = datetime.now().timestamp() - collection['host_uptime']

            tmp = re.search(r"\nCompiled\s+(.*?)\s+by\s+.*\n", output, re.MULTILINE)
            if tmp:
                collection['host_software_compiled'] = datetime.strptime(tmp.group(1), '%a %d-%b-%y %H:%M').timestamp()

            # System restarted at 14:02:21 GMT Wed Nov 13 2019
            tmp = re.search(r"System restarted at\s+(\d+:\d+:\d+.*?\d+)\n", output, re.MULTILINE)
            if tmp:
                try:
                    collection['host_restarted'] = datetime.strptime(
                        tmp.group(1), '%H:%M:%S %Z %a %b %d %Y').timestamp()
                except ValueError:
                    pass
                else:
                    collection['host_uptime'] = datetime.now().timestamp() - collection['host_restarted']

            tmp = re.search(r'^Processor board ID\s+(.*?)$', output, re.MULTILINE)
            if tmp:
                collection['host_processor_board_id'] = tmp.group(1)
                collection['host_serial_number'] = tmp.group(1)

            tmp = re.search(r'^(\d+)(KM) bytes of non-volatile configuration memory.$', output, re.MULTILINE)
            if tmp:
                collection['host_non_volatile_configuration_memory'] = int(tmp.group(1))
                collection['host_non_volatile_configuration_memory_unit'] = tmp.group(2)

            tmp = re.search(r'^(\d+)([KM]) bytes of physical memory.$', output, re.MULTILINE)
            if tmp:
                collection['host_physical_memory'] = int(tmp.group(1))
                collection['host_physical_memory_unit'] = tmp.group(2)

            tmp = re.search(r'^(Last reset from|Last reload reason: )(.*?)$', output, re.MULTILINE)
            if tmp:
                collection['host_last_reload_reason'] = str(tmp.group(2)).lower()

            tmp = re.search(r'^System image file is "(.*?)"$', output, re.MULTILINE)
            if tmp:
                collection['host_system_image_file'] = str(tmp.group(1)).lower()

            tmp = re.search(r'^ROM: (.*?)$', output, re.MULTILINE)
            if tmp:
                collection['host_rom_version'] = str(tmp.group(1)).lower()

            tmp = re.search(r'^(.*?)\s+CPU at (\d.*?[MG]Hz), Supervisor (.*?)$', output, re.MULTILINE)
            if tmp:
                collection['host_processor_speed'] = tmp.group(2)
                collection['host_supervisor_version'] = tmp.group(3)

            tmp = re.search(r'^(\d.*?)([KM])\sbytes of ATA System CompactFlash 0 \((.*)\)$', output, re.MULTILINE)
            if tmp:
                collection['host_compactflash'] = int(tmp.group(1))
                collection['host_compactflash_unit'] = tmp.group(2)
                collection['host_compactflash_access_mode'] = tmp.group(3).replace(
                    'Read', 'R').replace('Write', 'W')

            # Deal with stacked switches:
            tmp = re.search(r"(Switch\s+Ports\s+Model.*?)\n\n", output, re.MULTILINE | re.DOTALL)
            if tmp:
                for line in tmp.group(1).split('\n'):
                    tmp2 = re.search(r"^([* ])\s+(\d+) (\d+)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)$", line)
                    if tmp2:

                        if 'stack' not in collection:
                            collection['stack'] = {}

                        if int(tmp2.group(2)) not in collection['stack']:
                            collection['stack'][int(tmp2.group(2))] = {}

                        collection['stack'][int(tmp2.group(2))]['port_count'] = int(tmp2.group(3))
                        collection['stack'][int(tmp2.group(2))]['model'] = tmp2.group(4)
                        collection['stack'][int(tmp2.group(2))]['software_version'] = tmp2.group(5).strip()
                        collection['stack'][int(tmp2.group(2))]['software_image'] = tmp2.group(6).strip()
                        collection['stack'][int(tmp2.group(2))]['mode'] = tmp2.group(7)

                        if tmp2.group(1) == '*':
                            collection['stack'][int(tmp2.group(2))]['root'] = True

                            # Find the stack collection for 'root' switch:
                            tmp3 = re.search(
                                r"\n\n(Base Ethernet.*?\nSystem Serial Number\s+:\s+.*?\n)\n\nSwitch", output,
                                re.MULTILINE | re.DOTALL)
                            if tmp3:
                                for cfg_line in tmp3.group(1).split('\n'):
                                    if cfg_line == '':
                                        continue
                                    colon_loc = cfg_line.find(' : ')
                                    metric = cfg_line[0:colon_loc].strip().replace(' ', '_').lower()
                                    value = cfg_line[colon_loc + 2:].strip()
                                    if value == '':
                                        value = None
                                    collection['stack'][int(tmp2.group(2))][metric] = value

            # Additional stack info:
            tmp = re.compile(r"^Switch\s(\d+)\n(.*?Last reload reason\s+:\s.*?\n)$", re.MULTILINE | re.DOTALL)
            for switch_no, switch_info in re.findall(tmp, output):

                if 'stack' not in collection:
                    collection['stack'] = {}

                if int(switch_no) not in collection['stack']:
                    collection['stack'][int(switch_no)] = {}

                for cfg_line in switch_info.split('\n'):

                    # Remove unwanted lines
                    if cfg_line == '' or re.search(r"^---.*---$", cfg_line):
                        continue

                    # Find ':' colon and work out metric/value pairs:
                    colon_loc = cfg_line.find(' : ')
                    metric = cfg_line[0:colon_loc].strip().replace(' ', '_').lower()
                    value = cfg_line[colon_loc + 2:].strip()
                    if value == '':
                        value = None

                    # Switch uptime
                    if metric == 'switch_uptime':

                        collection['stack'][int(switch_no)]['uptime'] = int(uptime_to_seconds(value))
                        collection['stack'][int(switch_no)]['restarted'] = datetime.now().timestamp() - collection[
                            'stack'][int(switch_no)]['uptime']

                    else:
                        collection['stack'][int(switch_no)][metric] = value

            tmp = re.search(
                r"---\nTechnology-package\s+.*?---\n(.*?\n)\n\nSmart Licensing Status: (.*?)\n\n",
                output, re.MULTILINE | re.DOTALL)
            if tmp:
                collection['license'] = {'smart_licensing_status': tmp.group(2)}
                for cfg_line in tmp.group(1).split('\n'):
                    tmp2 = re.search(r"^(.*?) {2,}\t(.*?) {2,}\t (.*?)$", cfg_line)
                    if tmp2:
                        collection['license'][tmp2.group(1)] = {
                            'description': tmp2.group(2),
                            'next_reboot': tmp2.group(3).strip()}
            else:
                tmp = re.search(
                    r"\nLicense Information for\s+.*?\n(\s+License Level: .*\n\s+Next reboot license Level: .*?)\n\n",
                    output, re.MULTILINE | re.DOTALL)
                if tmp:
                    collection['license'] = {}
                    for cfg_line in tmp.group(1).split('\n'):
                        tmp2 = re.search(r"^\s+(License Level:|Next reboot license Level:)\s+(.*)$", cfg_line)
                        if tmp2:
                            tmp3 = re.search(r"^(.*?)\s+Type:\s+(.*)$", tmp2.group(2))
                            if tmp3:
                                collection['license'][tmp3.group(1)] = {'type': str(tmp3.group(2)).lower()}
                            else:
                                collection['license']['next_reboot'] = tmp2.group(2)

            tmp = re.search(
                r"---\nTechnology\s+.*?---\n(.*?\n)\nConfiguration register is (.*?)\n",
                output, re.MULTILINE | re.DOTALL)
            if tmp:

                if 'license' not in collection:
                    collection['license'] = {}

                for cfg_line in tmp.group(1).split('\n'):

                    tmp2 = re.search(r"^(.*?) {2,}(.*?) {2,}(.*?) {2,} (.*?)$", cfg_line)
                    if tmp2:
                        if tmp2.group(2) != 'None':

                            if tmp2.group(1) not in collection['license']:
                                collection['license'][tmp2.group(1)] = {}

                            collection['license'][tmp2.group(1)]['package'] = str(tmp2.group(2)).lower()
                            collection['license'][tmp2.group(1)]['type'] = str(tmp2.group(3)).lower()
                            collection['license'][tmp2.group(1)]['next_reboot'] = str(tmp2.group(4)).lower()

                    collection['host_config_register'] = tmp.group(2)

            # Interface counts
            tmp = re.compile(r"^(\d+)\s+(.*?)\s+interface(s)?$", re.MULTILINE)

            if 'totals' not in collection:
                collection['totals'] = {}

            if 'interfaces' not in collection['totals']:
                collection['totals']['interfaces'] = {}

            for total, interface_name, _ in re.findall(tmp, output):
                collection['totals']['interfaces'][interface_name] = int(total)

            tmp = re.search(r"^(\d+)\s+terminal line(s)?$", output, re.MULTILINE)
            if tmp:
                collection['totals']['interfaces']['terminal lines'] = tmp.group(1)

            tmp = re.search(r"^(\d+)\s+Channelized E1/PRI port(s)?$", output, re.MULTILINE)
            if tmp:
                collection['totals']['interfaces']['Channelized E1/PRI'] = tmp.group(1)

            tmp = re.search(r"---\nDevice#\s+.*?SN\n---.*?---\n(.*?)\n\n", output, re.MULTILINE | re.DOTALL)
            if tmp:
                tmp2 = re.search(r'^.*?\s+\t\s+(.*?)\s+(.*?)\s+$', tmp.group(1))
                if tmp2:
                    collection['host_serial_number'] = tmp2.group(2)

        elif collection['os_type'] == 'cisco_nxos':

            tmp = re.search(r"\s+([Ss]ystem:\s+version\s+|NXOS:\s+version\s+)(.*)\n", output, re.MULTILINE)
            if tmp:
                collection['host_software_version'] = tmp.group(2).strip()

            tmp = re.search(r"^\s+kickstart:\s+version\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_kickstart_software_version'] = tmp.group(1).strip()

            tmp = re.search(r"^\s+BIOS:\s+version\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_bios_version'] = tmp.group(1).strip()

            tmp = re.search(r"^\s+kickstart image file is:\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_kickstart_image_file'] = tmp.group(1).strip()

            tmp = re.search(r"^\s+system image file is:\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_system_image_file'] = tmp.group(1).strip()

            tmp = re.search(r"^\s+kickstart compile time:\s+(.*?)\s\[.*?]$\n", output, re.MULTILINE)
            if tmp:
                collection['host_kickstart_image_compile_time'] = datetime.strptime(
                    tmp.group(1), '%m/%d/%Y %H:%M:%S').timestamp()

            tmp = re.search(r"^\s+system compile time:\s+(.*?)\s\[.*?]$\n", output, re.MULTILINE)
            if tmp:
                collection['host_system_image_compile_time'] = datetime.strptime(
                    tmp.group(1), '%m/%d/%Y %H:%M:%S')

            tmp = re.search(r"^\s+Processor Board ID\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_serial_number'] = tmp.group(1)

            tmp = re.search(r"^\s+Device name:\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_system_name'] = tmp.group(1).strip()

            tmp = re.search(r"^\s+Reason:\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_last_reload_reason'] = tmp.group(1)

            tmp = re.search(r"^Kernel uptime is\s+(.*?)\n", output, re.MULTILINE)
            if tmp:
                collection['host_uptime'] = uptime_to_seconds(tmp.group(1))
                collection['host_restarted'] = datetime.now().timestamp() - collection['host_uptime']

            tmp = re.search(r"^Hardware\n\s+cisco\s+(Nexus.*?)(\s+\(.*?\))?\n", output, re.MULTILINE)
            if tmp:
                collection['host_model'] = tmp.group(1).strip()
                tmp2 = re.search(r'^(Nexus.*?)\s+(.*)\s+(chassis)?', collection['host_model'])
                if tmp2:
                    collection['host_family'] = tmp2.group(1)
                    collection['host_model'] = tmp2.group(2)

    # Check if there are any commands that were added by the helper, that need removing:
    if 'host_vendor' in collection:
        if collection['host_vendor'] == 'Cisco':
            collection['remove_next_command_list'] = ['dump overview']

    return True, collection
