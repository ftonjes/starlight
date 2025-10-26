import re


def analyze(output: str, collection=None):

    """

        Cisco - 'show environment' command analysis

    :param output: output from 'show environment' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show environment' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show environment' output from a Cisco device
    # Regex: '^show environment$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show environment' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous|Incomplete command).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    modules = {}

    tmp = re.search(
        r'\nModule\s+Sensor\s+Temperature\s+Status\s+\n--.*?--\n(.*?\n)\n', output, re.MULTILINE | re.DOTALL)
    if tmp:
        tmp2 = re.compile(r"(\d+)\s+(.*?)\s+(\d+)([CF])\s+\((\d+)\4,(\d+)\4,(\d+)\4\)\s+(.*?)\n")
        for num, name, temp, unit, warn, crit, shut, status in re.findall(tmp2, tmp.group(1)):

            if num not in modules:
                modules[num] = {}

            if name not in modules[num]:
                modules[num][name] = {}

            collection['sensor_temp_unit'] = unit
            modules[num][name]['temp'] = int(temp)
            modules[num][name]['warning'] = int(warn)
            modules[num][name]['critical'] = int(crit)
            modules[num][name]['shutdown'] = int(shut)
            modules[num][name]['status'] = status

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

    tmp = re.search(r'\nPower consumed by backplane\s+:\s+(\d+)\s+Watts\n', output)
    if tmp:
        collection['power_backplane_consumption_watts'] = int(tmp.group(1))

    tmp = re.search(r'\nSwitch Bandwidth Utilization\s+:\s+(\d+)%\n', output)
    if tmp:
        collection['switch_bandwidth_utilization_percent'] = int(tmp.group(1))

    tmp = re.search(r'\nSupervisor Led Color\s+:\s+(.*?)\n', output)
    if tmp:
        collection['supervisor_led_color'] = tmp.group(1)

    tmp = re.search(r'\nFantray\s+:\s+(.*?)\n', output)
    if tmp:
        collection['fantray_status'] = tmp.group(1)

    tmp = re.search(r'\nFantray removal timeout\s+:\s+(\d+)\n', output)
    if tmp:
        collection['fantray_removal_timeout'] = int(tmp.group(1))

    tmp = re.search(r'\nPower consumed by Fantray\s+:\s+(\d+)\s+Watts\n', output)
    if tmp:
        collection['power_fantray_consumption_watts'] = int(tmp.group(1))

    environment = {}
    current_collection = None

    for line in output.split('\n'):

        # Find collection name (usually no gaps at start with colon:
        find_collection = re.search(r'^(.*?):(\s+)?$', line)
        if find_collection:
            current_collection = find_collection.group(1)

        # Some collections have no colon at the end:
        elif len(line) <= 20 and not re.search(r':', line) and not re.search(r'^\s+', line):
            if line != '':
                current_collection = line

        elif re.search(r'^\s+module \d+\s.*?:', line):

            find_collection = re.search(r'^\s+(module \d+)\s+', line)
            if find_collection:
                current_collection = find_collection.group(1)

        # If we have a collection name, find the metrics under it:
        if current_collection:
            find_sensor = re.search(r'^\s+' + current_collection + r'\s(.*?):\s+(.*?)$', line)
            if find_sensor:
                if current_collection.replace(' ', '_').replace('-', '_').lower() not in environment:
                    environment[current_collection.replace(' ', '_').replace('-', '_').lower()] = {}

                find_second_sensor = re.search(
                    r'^(.*?), ' + current_collection + r'\s+(.*?):\s+(.*?)$', find_sensor.group(2))

                # Some lines contain more than one sensor / value:
                if find_second_sensor:

                    # 2 sensor metrics in one line, e.g. '  clock 2 OK: OK, clock 2 clock-inuse: not-in-use'
                    environment[current_collection.replace(
                        ' ', '_').replace('-', '_').lower()][
                        find_sensor.group(1).replace(' ', '_').replace(
                            '-', '_').lower()] = find_second_sensor.group(1)

                    environment[current_collection.replace(
                        ' ', '_').replace('-', '_').lower()][find_second_sensor.group(2).replace(
                            ' ', '_').replace('-', '_').lower()] = find_second_sensor.group(3)

                else:

                    # Only 1 sensor value in the line, e.g.: '  power-supply 1 fan-fail: OK'
                    environment[current_collection.replace(
                        ' ', '_').replace('-', '_').lower()][find_sensor.group(1).replace(
                            ' ', '_').replace('-', '_').lower()] = find_sensor.group(2)

        # Chassis metrics
        chassis = re.search(r'^chassis\s+(.*?):\s+(.*)$', line)
        if chassis:

            if 'chassis' not in environment:
                environment['chassis'] = {}

            environment['chassis'][chassis.group(1).replace(' ', '_').replace('-', '_').lower()] = chassis.group(2)

        # pick up the ambient temperature value and include it under 'chassis':
        ambient = re.search(r'^ambient temperature: <\s+(\d+[CF])', line)
        if ambient:
            environment['chassis']['ambient_temperature'] = ambient.group(1)

    # Iterate through all items and see if any of the values need enriching:
    for component in environment:

        for sensor in environment[component]:

            value = environment[component][sensor]

            # Temperature
            if re.search(r'^\d+[CF]$', value) and 'temperature' in sensor:
                value = {
                    'unit': value[-1],
                    'value': int(value[0:-1])}

            elif re.search(r'\d.*? [Ww]atts\s+\(.*?\d+\s+Amps.*\)$', value):
                tmp = re.search(r'^(\d.*?)\s[Ww]atts\s\(\s?(\d.*?)\s+Amps\s@\s(\d+)[Vv]\)$', value)
                if tmp:
                    value = {
                        'watts': float(tmp.group(1)),
                        'amps': float(tmp.group(2)),
                        'volts': float(tmp.group(3))}

            elif re.search(r'\d+\scfm', value):
                tmp = re.search(r'^(\d+)\scfm', value)
                if tmp:
                    value = {
                        'unit': 'cfm',
                        'value': int(tmp.group(1))}

            if value != environment[component][sensor]:
                environment[component][sensor] = value

    if environment != {}:

        collection['environment'] = environment

    return True, collection
