import re
import pprint


def analyze(output, collection=None):

    """

        F5 - 'show sys hardware' command analysis

    :param output: output from 'show sys hardware' on an F5 device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show sys hardware' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show sys hardware' output from a F5 device
    # Regex: '^show sys hardware$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show sys hardware' command should be in string format."

    collection['host_vendor'] = 'F5'
    collection['_host_name_extraction'] = r"^.*?@\((.*?)\).*"
    collection['os_type'] = 'f5_tmos'

    # START

    tmp = re.search(r'^Appliance Fan Status\n\s+Index\s+Status\n(.*?)\n$', output, re.MULTILINE | re.DOTALL)
    if tmp:
        for line in tmp.group(1).split('\n'):
            tmp2 = re.search(r'^\s+(\d+)\s+(.*?)$', line)
            if tmp2:
                if 'environmental' not in collection:
                    collection['environmental'] = {}
                if 'fans' not in collection['environmental']:
                    collection['environmental']['fans'] = {}
                collection['environmental']['fans'][tmp2.group(1)] = tmp2.group(2)

    # Appliance Information
    tmp = re.search(r'^\s+Maximum MAC Count\s+(\d+)$', output)
    if tmp:
        collection['appliance_max_mac_count'] = int(tmp.group(1))
    tmp = re.search(r'^\s+Registration Key\s+(.*)$', output)
    if tmp:
        if tmp.group(1) != '-':
            collection['appliance_registration_key'] = tmp.group(1).strip()

    # Appliance Power Supply Status
    tmp = re.search(
        r'^Appliance Power Supply Status\n\s+Index\s+Status\s+Current\n(.*?)\n$', output, re.MULTILINE | re.DOTALL)
    if tmp:
        for line in tmp.group(1).split('\n'):
            tmp2 = re.search(r'^\s+(\d+)\s+(.*?)\s+(.*)$', line)
            if tmp2:
                if 'environmental' not in collection:
                    collection['environmental'] = {}
                if 'power_supplies' not in collection['environmental']:
                    collection['environmental']['power_supplies'] = {}
                if tmp2.group(1) not in collection['environmental']['power_supplies']:
                    collection['environmental']['power_supplies'][tmp2.group(1)] = {}
                collection['environmental']['power_supplies'][tmp2.group(1)]['status'] = tmp2.group(2)
                collection['environmental']['power_supplies'][tmp2.group(1)]['current'] = tmp2.group(3)

    # Inlet Temperature Status
    tmp = re.search(r'^Inlet Temperature Status\n\s+Index.*?Location\n(.*?)\n$', output, re.MULTILINE | re.DOTALL)
    if tmp:
        for line in tmp.group(1).split('\n'):
            tmp2 = re.search(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)$', line)
            if tmp2:
                if 'environmental' not in collection:
                    collection['environmental'] = {}
                if 'inlet_sensors' not in collection['environmental']:
                    collection['environmental']['inlet_sensors'] = {}
                if tmp2.group(1) not in collection['environmental']['inlet_sensors']:
                    collection['environmental']['inlet_sensors'][tmp2.group(1)] = {}
                collection['environmental']['inlet_sensors'][tmp2.group(1)]['low_limit_deg_c'] = int(tmp2.group(2))
                collection['environmental']['inlet_sensors'][tmp2.group(1)]['temp_deg_c'] = int(tmp2.group(3))
                collection['environmental']['inlet_sensors'][tmp2.group(1)]['high_limit_deg_c'] = int(tmp2.group(4))
                collection['environmental']['inlet_sensors'][tmp2.group(1)]['location'] = tmp2.group(5)

    # Hardware Version Information
    tmp = re.compile(r'Hardware Version Information\n(.*?)\n(\s+)\n\n', re.MULTILINE | re.DOTALL)
    hardware = []
    for hw_info in re.findall(tmp, output):
        info = {}
        for line in hw_info[0].split('\n'):
            tmp = re.search(r'^(\s+)(.*?)\s{2,}(.*)$', line)
            if tmp:
                if tmp.group(2) not in ['Parameters', '']:

                    # Create found key into a more friendlier name (lower caps, underscores, no spaces, etc):
                    key = re.sub('(?<!^)(?=[A-Z])', '_', tmp.group(2)).lower().replace(' ', '_').replace(
                        '__', '_').replace('cpu_m_hz', 'cpu_mhz')

                    # Some sections have more than one item of hardware under them (e.g.: power supplies):
                    if key == 'name':
                        if len(info) > 2:
                            hardware.append(info)
                            info = {}

                    # Clean up values (int, float, str):
                    int_list = ['cpu_sockets', 'cpu_stepping']
                    float_list = ['cpu_mhz']
                    if key in int_list:
                        info[key] = int(tmp.group(3).strip())
                    elif key in float_list:
                        cleaned = re.sub(r'\.0+', '', tmp.group(3).strip())
                        if f'{float(tmp.group(3).strip()):g}' == cleaned:
                            info[key] = int(cleaned)
                        else:
                            info[key] = float(tmp.group(3).strip())
                    else:
                        info[key] = tmp.group(3).strip()

        hardware.append(info)

    if len(hardware) > 0:
        if 'hwardware' not in collection:
            collection['hardware'] = hardware

    # Platform
    tmp = re.search(r'\nPlatform\n(.*?\n\n)', output, re.MULTILINE | re.DOTALL)
    if tmp:
        tmp2 = re.search(r'\s+Name\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_model'] = tmp2.group(1).strip()
        tmp2 = re.search(r'\s+BIOS Revision\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_bios_revision'] = tmp2.group(1).strip()
        tmp2 = re.search(r'\s+Base MAC\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_base_mac'] = tmp2.group(1).strip()

    # System Information
    tmp = re.search(r'\nSystem Informatio.*?\n(.*?\n\n)', output + '\n', re.MULTILINE | re.DOTALL)
    if tmp:
        tmp2 = re.search(r'\s+Type\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_type_code'] = tmp2.group(1).strip()
        tmp2 = re.search(r'\s+(Appliance|Chassis) Serial\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_serial_number'] = tmp2.group(2).strip()
        tmp2 = re.search(r'\s+(Part Number|Level 200/400 Part)\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_part_number'] = tmp2.group(2).strip()
        tmp2 = re.search(r'\s+Host Board Serial\s+(.*)\n', tmp.group(1))
        if tmp2:
            collection['host_board_serial_number'] = tmp2.group(1).strip()
        tmp2 = re.search(r'\s+Host Board Part Revision\s+(.*?)\n', tmp.group(1))
        if tmp2:
            collection['host_board_part_revision'] = tmp2.group(1).strip() if tmp2.group(1).strip() != '' else None

    find_error = re.search(r'Broadcast message from', output)
    if find_error:
        collection['_error'] = "Broadcast message interuption"
        return False, collection

    # END

    return True, collection
