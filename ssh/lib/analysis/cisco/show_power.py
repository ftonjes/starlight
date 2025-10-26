import re


def analyze(output, collection=None):

    """

        Cisco - 'show power' command analysis

    :param output: output from 'show power' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show power' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show power' output from a Cisco device
    # Regex: '^show power$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show power' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    tmp = re.search(
        r'\nSupply\s+Model\sNo\s+Type\s+Status\s+Sensor\s+Status\n--.*?--\n(.*?\n)\n',
        output, re.MULTILINE | re.DOTALL)
    if tmp:
        collection['power_supply'] = {}
        tmp2 = re.compile(r"(PS\d+)(-(\d))?\s{2,6}(.*?)\s{2,}(.*?)\s{2,}(.*?)\s(\s+|\s+(.*?)\s+(.*?)\s+)\n")
        for ps_no, toggle, sub_id, model_no, typ, status, _, fan, inline in re.findall(tmp2, tmp.group(1)):

            if ps_no not in collection['power_supply']:
                collection['power_supply'][ps_no] = {}

            if toggle == '':

                collection['power_supply'][ps_no] = {
                    'model_no': model_no,
                    'type': typ,
                    'status': status,
                    'fan_status': fan,
                    'inline_status': inline,
                    'supplies': {}}

            else:

                if 'supplies' not in collection['power_supply'][ps_no]:
                    collection['power_supply'][ps_no]['supplies'] = {}

                collection['power_supply'][ps_no]['supplies'][sub_id] = {'type': typ, 'status': status}

    tmp = re.search(r'\nPower supplies needed by system\s+:\s+(\d+)\n', output)
    if tmp:
        collection['power_supplies_needed'] = int(tmp.group(1))

    tmp = re.search(r'\nPower supplies currently available\s+:\s+(\d+)\n', output)
    if tmp:
        collection['power_supplies_available'] = int(tmp.group(1))

    tmp = re.search(r'\nSystem Power \(12V\)\s+(\d+)\s+(\d+)\n', output)
    if tmp:
        collection['power_system_used'] = int(tmp.group(1))
        collection['power_system_available'] = int(tmp.group(2))

    tmp = re.search(r'\nInline Power \(-50V\)\s+(\d+)\s+(\d+)\n', output)
    if tmp:
        collection['power_inline_used'] = int(tmp.group(1))
        collection['power_inline_available'] = int(tmp.group(2))

    tmp = re.search(r'\nBackplane Power \(3\.3V\)\s+(\d+)\s+(\d+)\n', output)
    if tmp:
        collection['power_backplane_used'] = int(tmp.group(1))
        collection['power_backplane_available'] = int(tmp.group(2))

    tmp = re.search(r'\nTotal\s+(\d+)\s+\(not to exceed Total Maximum Available = (\d+)\)\n', output)
    if tmp:
        collection['power_total_used'] = int(tmp.group(1))
        collection['power_total_available'] = int(tmp.group(2))

    power = {}

    for item in output.split('\n'):

        tmp = re.search(r'^system power (.*?) = +([0-9.]+) Watts \(([0-9.]+) Amps @ (\d+)V\)$', item)
        if tmp:
            power[tmp.group(1)] = {
                'watts': float(tmp.group(2)), 'amps': float(tmp.group(3)), 'volts': float(tmp.group(4))}

        tmp = re.search(r'^(\d+) +(.*?) +([0-9.]+) +([0-9.]+) +([A-Za-z]+) +([A-Za-z]+) +([A-Za-z]+) ?$', item)
        if tmp:
            power[f'power_supply_{tmp.group(1)}'] = {
                'type': tmp.group(2),
                'power_capacity_watts': float(tmp.group(3)),
                'power_capacity_amps': float(tmp.group(4)),
                'power_supply_fan_status': tmp.group(5),
                'power_output_status': tmp.group(6),
                'power_operational_state': tmp.group(7)}

        tmp = re.search(r'^(\d+) +([A-Z][A-Za-z\-0-9]+) +([0-9.]+) +([0-9.]+) +([A-Za-z\-]+)$', item)
        if tmp:
            power[f'fan_{tmp.group(1)}'] = {
                'type': tmp.group(2),
                'power_capacity_watts': float(tmp.group(3)),
                'power_capacity_amps': float(tmp.group(4)),
                'power_operational_state': tmp.group(5)}

        tmp = re.search(
            r'^(\d+) +(\(Redundant Sup\)|[A-Z][A-Za-z\-0-9]+) +(-|[0-9.]+) +(-|[0-9.]+)'
            r' +([0-9.]+) +([0-9.]+) +(-|[A-Za-z]+) +(-|[A-Za-z]+) ?$', item)
        if tmp:

            # If the 'module' information was previously collected include this informaton in that section
            if 'modules' in collection:

                if int(tmp.group(1)) not in collection['modules']:
                    collection['modules'][int(tmp.group(1))] = {}

                collection['modules'][int(tmp.group(1))]['model'] = tmp.group(2)

                if tmp.group(3) != '-':
                    collection['modules'][int(tmp.group(1))]['power_requested_watts'] = float(tmp.group(3))
                if tmp.group(4) != '-':
                    collection['modules'][int(tmp.group(1))]['power_requested_amps'] = float(tmp.group(4))

                collection['modules'][int(tmp.group(1))]['power_allocated_watts'] = float(tmp.group(5))
                collection['modules'][int(tmp.group(1))]['power_allocated_amps'] = float(tmp.group(6))
                if tmp.group(7) != '-':
                    collection['modules'][int(tmp.group(1))]['power_admin_state'] = tmp.group(7)
                if tmp.group(8) != '-':
                    collection['modules'][int(tmp.group(1))]['power_operational_state'] = tmp.group(8)

            if 'modules' not in power:
                power['modules'] = {}

            power['modules'][int(tmp.group(1))] = {
                'model': tmp.group(2),
                'power_allocated_watts': float(tmp.group(5)),
                'power_allocated_amps': float(tmp.group(6))}
            if tmp.group(3) != '-':
                power['modules'][int(tmp.group(1))]['power_requested_watts'] = float(tmp.group(3))
            if tmp.group(4) != '-':
                power['modules'][int(tmp.group(1))]['power_requested_amps'] = float(tmp.group(4))
            if tmp.group(7) != '-':
                power['modules'][int(tmp.group(1))]['power_admin_state'] = tmp.group(7)
            if tmp.group(8) != '-':
                power['modules'][int(tmp.group(1))]['power_operational_state'] = tmp.group(8)

        tmp = re.search(r'^system auxiliary power mode = (.*?)', item)
        if tmp:
            power['auxiliary_power_mode'] = tmp.group(1)

        tmp = re.search(r'^system auxiliary redundancy operationally = +(.*?)$', item)
        if tmp:
            power['auxiliary_redundancy_operationally'] = tmp.group(1)

    collection['power'] = power

    return True, collection
