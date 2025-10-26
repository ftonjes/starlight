import re


def info():

    """

        This module parses the output of the 'show interface' command executed on Cisco devices, and returns the
          information in dictionary format. The fields returned may differ due to different interface types and/or
          features available.

    """

    return {
        'author': {'name': 'Frank Tonjes', 'email': "infy101@hotmail.com"},
        'auto_parse': r'^show interface$',
        'description': "This module parses the output of the 'show interface' command executed on Cisco devices,"
                       " and returns the information in dictionary format.",
        'version': '1.0',
        'vendor': 'Cisco',
        'requires': {
            'output': {'description': "Output from 'show interface' command.", 'type': 'string'},
        },
        'optional': {
            'options': {'description': "Additional processing options.", 'type': 'list'},
            'collection': 'Existing token to which information is to be added to. (dict)'
        },
        'provides': {
            'devices': [{
                'interfaces_active': {'description': "List of active interfaces on device.", 'type': 'list'},
                'interfaces_shut': {
                    'description': "List of administratively shut interfaces on the device.", 'type': 'list'},
                'interfaces_down': {
                    'description': "List of interfaces names which are enabled, but down.", 'type': 'list'},
                'interfaces_reserved': {
                    'description': "List of reserved interfaces with '=RESERVED=' in the description.", 'type': 'list'},
                'interfaces_disabled': {
                    'description': "List of disabled interfaces with '=DISABLED=' in the description.", 'type': 'list'},
            }],
            'interfaces': [{
                'interface_name': {'description': "Interface name.", 'type': 'string'},
                'admin_status': {'description': "Administrative status", 'type': 'string'},
                'arp_timeout': {'description': "ARP timeout HH:MM:SS", 'type': 'string'},
                'arp_type': {'description': "ARP type", 'type': 'string'},
                'babbles': {'description': "Number of babbles", 'type': 'integer'},
                'bia': {'description': "burnt-in MAC address 0000.00aa.bbcc", 'type': 'string'},
                'bw': {'description': "Bandwith in MB", 'type': 'integer'},
                'collisions': {'description': "Number of collisions", 'type': 'integer'},
                'crc_errors': {'description': "Number of CRC errors", 'type': 'integer'},
                'deferred': {'description': "Number of deferred packets", 'type': 'integer'},
                'description': {'description': "Interface description", 'type': 'string'},
                'dly': {'description': "Delay in milliseconds", 'type': 'integer'},
                'duplex': {'description': "Duplex", 'type': 'string'},
                'encapsulation': {'description': "Encapsulation", 'type': 'string'},
                'five_min_input_rate_bits_sec': {
                    'description': "Five minute input rate bits per second", 'type': 'integer'},
                'five_min_input_rate_packets_sec': {
                    'description': "Five minute input rate packets per second", 'type': 'integer'},
                'five_min_output_rate_bits_sec': {
                    'description': "Five minute output rate bits per second", 'type': 'integer'},
                'five_min_output_rate_packets_sec': {
                    'description': "Five minute output rate packets per second", 'type': 'integer'},
                'frame_errors': {'description': "Number of frame errors", 'type': 'integer'},
                'giants': {'description': "Giant packets", 'type': 'integer'},
                'hardware': {'description': "Hardware type", 'type': 'string'},
                'index': {'description': "Interface index", 'type': 'integer'},
                'input_errors': {'description': "Number of input errors", 'type': 'integer'},
                'input_flow_control_active': {'description': "Is flow control active", 'type': 'boolean'},
                'input_queue_drops': {
                    'description': "Number of input queue drops since the last time the counters were cleared",
                    'type': 'integer'},
                'input_queue_flushes': {
                    'description': "Number of input queue flushes since the last time the counters were cleared",
                    'type': 'integer)'},
                'input_queue_max': {
                    'description': "Number of maximum input queue since the last time the counters were cleared",
                    'type': 'integer)'},
                'input_queue_size': {'description': "Input queue size", 'type': 'integer'},
                'interface_resets': {
                    'description': "Number of interface resets since the last time the counters were cleared",
                    'type': 'integer)'},
                'ip_v4_address': {'description': "IPv4 address", 'type': 'string'},
                'ip_v4_mask': {'description': "IPv4 CIDR mask", 'type': 'integer'},
                'keepalive_sec': {'description': "Keepalive interval in seconds", 'type': 'integer'},
                'last_clearing_show_interface_counters': {
                    'description': "Last time counters were cleared", 'type': 'string'},
                'last_input': {'description': "Last time since input", 'type': 'string'},
                'last_output': {'description': "Last time since output", 'type': 'string'},
                'last_output_hang': {'description': "Last time since output hang", 'type': 'string'},
                'mac_address': {'description': "MAC address", 'type': 'string'},
                'media_type': {'description': "Media type", 'type': 'string'},
                'mtu': {'description': "Maximum transmission unit", 'type': 'integer'},
                'multicast': {'description': "Number of multicast packets", 'type': 'integer'},
                'no_carrier': {'description': "Number of 'no carrier' errors", 'type': 'integer'},
                'operational_status': {'description': "Operational status", 'type': 'string'},
                'output_buffer_failures': {
                    'description': "Number of output buffer failures since the last time the counters were cleared",
                    'type': 'integer'},
                'output_buffers_swapped_out': {
                    'description': "Number of output buffers swapped out since the last time the counters were cleared",
                    'type': 'integer'},
                'output_errors': {
                    'description': "Number of output errors since the last time the counters were cleared",
                    'type': 'integer)'},
                'output_queue_max': {
                    'description': "Maximum output queue since the last time the counters were cleared",
                    'type': 'integer)'},
                'output_queue_size': {'description': "Output queue size", 'type': 'integer'},
                'packets_input': {'description': "Number of input packets", 'type': 'integer'},
                'packets_input_bytes': {'description': "Total bytes of input packets", 'type': 'integer'},
                'packets_input_no_buffer': {'description': "Number of input no buffer failures", 'type': 'integer'},
                'packets_output': {'description': "Number of output packets", 'type': 'integer'},
                'packets_output_bytes': {'description': "Total output in bytes", 'type': 'integer'},
                'packets_output_underruns': {'description': "Total number of output underruns", 'type': 'integer'},
                'pause_input': {'description': "Number of times input was paused", 'type': 'integer'},
                'pause_output': {'description': "Number of times output was paused", 'type': 'integer'},
                'queueing_strategy': {'description': "Queueing strategy", 'type': 'string'},
                'reliability': {'description': "Link reliability", 'type': 'integer'},
                'runts': {'description': "Number of runts", 'type': 'integer'},
                'rx_load': {'description': "RX load", 'type': 'integer'},
                'speed': {'description': "Speed", 'type': 'string'},
                'speed_unit': {'description': "Speed unit of measure", 'type': 'string'},
                'status': {'description': "Interface status", 'type': 'string'},
                'throttles': {'description': "Number of throttles", 'type': 'integer'},
                'total_output_drops': {'description': "Number of dropped output packets", 'type': 'integer'},
                'tx_load': {'description': "TX load", 'type': 'integer'},
                'unknown_protocol_drops': {
                    'description': "Total number of packets dropped due to unknown protocol", 'type': 'integer'},
                'unnumbered_using_address': {'description': "Unnumbered using IPv4 Address", 'type': 'string'},
                'unnumbered_using_interface': {'description': "Unnumbered using interface", 'type': 'string'},
                'watchdog': {'description': "Number of watchdog packets", 'type': 'integer'}}]
        }
    }


def analyze(output, collection=None):

    """

        Cisco - 'show interface' command analysis

    :param output: output from 'show interface' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show interface' command
    """
    # Version: 1.0 - Initial version
    # Description: Analyze 'show interface' output from a Cisco device
    # Regex: '^show interface$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show interface' command should be in string format."

    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    # Add an extra line so regex can catch the last interface!
    output += '\n'

    collection['interfaces_active'] = []
    collection['interfaces_disabled'] = []
    collection['interfaces_down'] = []
    collection['interfaces_reserved'] = []
    collection['interfaces_shut'] = []

    interfaces = {}
    count = 0

    interface = re.compile(
        r'^([A-Za-z].*?[0-9]) is (administratively )?(up|down|initializing), line protocol is (up|down)'
        r'( , Autostate Enabled| \(spoofing\)| \(connected\)| \(notconnect\)| \(disabled\)| \(err-disabled\)| )? ?\n'
        r'(.*?output buffers swapped out)\n', re.MULTILINE | re.DOTALL)

    for if_name, _, admin_state, oper_state, if_message, if_payload in re.findall(interface, output):

        count += 1
        interfaces[if_name] = {'operational_status': oper_state, 'index': count, 'admin_status': admin_state}

        mod_port = None
        tmp = re.search(r'(\d+/.*)$', if_name)
        if tmp:
            mod_port = tmp.group(1).split('/')

        try:
            interfaces[if_name]
        except KeyError:
            interfaces[if_name] = {'mod_port': mod_port}

        if interfaces[if_name]['admin_status'] == 'down':

            if re.search(r'^down', interfaces[if_name]['operational_status']):

                collection['interfaces_shut'].append(if_name)
                interfaces[if_name]['status'] = 'shut'

        elif interfaces[if_name]['admin_status'] == 'up':

            if re.search(r'^up', interfaces[if_name]['operational_status']):
                collection['interfaces_active'].append(if_name)
                interfaces[if_name]['status'] = 'active'

            else:
                collection['interfaces_down'].append(if_name)
                interfaces[if_name]['status'] = 'down'

        if if_message == ' (connected)':
            interfaces[if_name]['connected'] = True
        elif if_message == ' (notconnect)':
            interfaces[if_name]['connected'] = False

        if_blk = re.search(
            r'^\s+Hardware is (.*?), address is\s+(.*?)( \(bia (.*?)\))?$', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['hardware'] = if_blk.group(1)
            interfaces[if_name]['mac_address'] = if_blk.group(2)
            if if_blk.group(4):
                interfaces[if_name]['bia'] = if_blk.group(4)

        if_blk = re.search(
            r'^\s+Interface is unnumbered\. Using address of (.*?) \((.*?)\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['unnumbered_using_interface'] = if_blk.group(1)
            interfaces[if_name]['unnumbered_using_address'] = if_blk.group(2)

        if_blk = re.search(r'^\s+Description: (.*?)$', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['description'] = if_blk.group(1)
            if '=DISABLED=' in if_blk.group(1):
                collection['interfaces_disabled'].append(if_name)
            elif '=RESERVED=' in if_blk.group(1):
                collection['interfaces_reserved'].append(if_name)

        if_blk = re.search(r'^\s+Internet address is (.*?)/(\d+)$', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['ip_v4_address'] = if_blk.group(1)
            interfaces[if_name]['ip_v4_mask'] = int(if_blk.group(2))

        if_blk = re.search(
            r'^\s+MTU (.*?) bytes, +BW (.*?) Kbit/sec, DLY (.*?) usec,', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['mtu'] = int(if_blk.group(1))
            interfaces[if_name]['bw'] = int(if_blk.group(2))
            interfaces[if_name]['dly'] = int(if_blk.group(3))

        if_blk = re.search(
            r'^\s+reliability (\d+)/255, txload (\d+)/255, rxload (\d+)/255$', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['reliability'] = int(if_blk.group(1))
            interfaces[if_name]['tx_load'] = int(if_blk.group(2))
            interfaces[if_name]['rx_load'] = int(if_blk.group(3))

        if_blk = re.search(r'^\s+Encapsulation (.*?),', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['encapsulation'] = if_blk.group(1)

        if_blk = re.search(r'^\s+Keepalive (set \((\d+) sec\))\n', if_payload, re.MULTILINE)
        if if_blk:
            if if_blk.group(1) == 'not set':
                interfaces[if_name]['keepalive_sec'] = 'not set'
            else:
                interfaces[if_name]['keepalive_sec'] = int(if_blk.group(2))

        if_blk = re.search(r'^\s+Tunnel linestate evaluation (.*?),', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_linestate_evaluation'] = if_blk.group(1)

        if_blk = re.search(r'^\s+Tunnel source (.*?) \((.*?)\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_source_ip_v4_address'] = if_blk.group(1)
            interfaces[if_name]['tunnel_source_interface'] = if_blk.group(2)

        if_blk = re.search(r'^\s+Tunnel protocol/transport (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_protocol_transport'] = if_blk.group(1)

        if_blk = re.search(r'^\s+Key (.*?), sequencing (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_protocol_transport_key'] = if_blk.group(1)
            interfaces[if_name]['tunnel_protocol_transport_sequencing'] = if_blk.group(2)

        if_blk = re.search(r'^\s+Checksumming of packets (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_protocol_transport_checksumming'] = if_blk.group(1)

        if_blk = re.search(r'^\s+Tunnel TTL (\d+), Fast tunneling (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_ttl'] = int(if_blk.group(1))
            interfaces[if_name]['tunnel_fast_tunneling'] = if_blk.group(2)

        if_blk = re.search(r'^\s+Tunnel transport MTU (\d+) bytes\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_transport_mtu_bytes'] = int(if_blk.group(1))

        if_blk = re.search(r'^\s+Tunnel transmit bandwidth (\d+) \((.*?)\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_transmit_bandwidth'] = int(if_blk.group(1))
            interfaces[if_name]['tunnel_transmit_bandwidth_unit'] = if_blk.group(2)

        if_blk = re.search(r'^\s+Tunnel receive bandwidth (\d+) \((.*?)\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_receive_bandwidth'] = int(if_blk.group(1))
            interfaces[if_name]['tunnel_receive_bandwidth_unit'] = if_blk.group(2)

        if_blk = re.search(r'^\s+Tunnel protection via (.*?) \(profile \"(.*?)\"\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['tunnel_protection_via'] = if_blk.group(1)
            interfaces[if_name]['tunnel_protection_profile'] = if_blk.group(2)

        if_blk = re.search(
            r'^\s+(Auto-duplex|Auto Duplex|Full Duplex|Full-duplex|Half Duplex),'
            r' (Auto Speed|Auto-speed|\d+.*?b.s.*?)(, link type is (.*?))?(, media type is (.*?))?\n',
            if_payload, re.MULTILINE)
        if if_blk:
            if if_blk.group(1) in ['Auto-duplex', 'Auto Duplex']:
                interfaces[if_name]['duplex'] = 'auto'
            elif if_blk.group(1) in ['Full Duplex', 'Full-duplex']:
                interfaces[if_name]['duplex'] = 'full'
            elif if_blk.group(1) == 'Half Duplex':
                interfaces[if_name]['duplex'] = 'half'

            if if_blk.group(2) in ['Auto-speed', 'Auto Speed']:
                interfaces[if_name]['speed'] = 'auto'
            else:
                tmp = re.search(r'^(\d+)(.*?b.s)', if_blk.group(2))
                if tmp:
                    interfaces[if_name]['speed'] = tmp.group(1)
                    interfaces[if_name]['speed_unit'] = tmp.group(2).replace('b/s', 'bps')

            if if_blk.group(3) is not None:
                interfaces[if_name]['link_type'] = if_blk.group(4)

            if if_blk.group(5) is not None:
                interfaces[if_name]['media_type'] = if_blk.group(6)

        if_blk = re.search(
            r'^\s+input flow-control is (.*?), output flow-control is (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['input_flow_control'] = if_blk.group(1)
            interfaces[if_name]['output_flow_control'] = if_blk.group(2)

        if_blk = re.search(
            r'^\s+Input flow-control is (on|off), output flow-control is (on|off)$', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['input_flow_control_active'] = True if if_blk.group(1) == 'on' else False
            interfaces[if_name]['output_flow_control_active'] = True if if_blk.group(2) == 'on' else False

        if_blk = re.search(
            r'^\s+output flow-control is (.*?), input flow-control is (.*?)$', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['input_flow_control_active'] = True if if_blk.group(1) == 'on' else False
            interfaces[if_name]['output_flow_control_active'] = True if if_blk.group(2) == 'on' else False

        if_blk = re.search(
            r'^\s+ARP type: (.*?), ARP Timeout (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['arp_type'] = if_blk.group(1)
            interfaces[if_name]['arp_timeout'] = if_blk.group(2)

        if_blk = re.search(
            r'Last input (.*?), output (.*?), output hang (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['last_input'] = if_blk.group(1)
            interfaces[if_name]['last_output'] = if_blk.group(2)
            interfaces[if_name]['last_output_hang'] = if_blk.group(3)

        if_blk = re.search(r'^\s+Last clearing of "show interface" counters (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['last_clearing_show_interface_counters'] = if_blk.group(1)

        if_blk = re.search(
            r'^\s+Input queue: (\d+)/(\d+)/(\d+)/(\d+) \(size/max/drops/flushes\);'
            r' Total output drops: (\d+)',
            if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['input_queue_size'] = int(if_blk.group(1))
            interfaces[if_name]['input_queue_max'] = int(if_blk.group(2))
            interfaces[if_name]['input_queue_drops'] = int(if_blk.group(3))
            interfaces[if_name]['input_queue_flushes'] = int(if_blk.group(4))
            interfaces[if_name]['total_output_drops'] = int(if_blk.group(5))

        if_blk = re.search(r'^\s+Queueing strategy: (.*?)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['queueing_strategy'] = if_blk.group(1)

        if_blk = re.search(
            r'^\s+Output queue: (\d+)/(\d+)/(\d+)/(\d+) \(size/max total/threshold/drops\)',
            if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['output_queue_size'] = int(if_blk.group(1))
            interfaces[if_name]['output_queue_max'] = int(if_blk.group(2))
            interfaces[if_name]['output_queue_drops'] = int(if_blk.group(3))
            interfaces[if_name]['output_queue_flushes'] = int(if_blk.group(4))

        if_blk = re.search(r'^\s+Output queue: (\d+)/(\d+) \(size/max\)', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['output_queue_size'] = int(if_blk.group(1))
            interfaces[if_name]['output_queue_max'] = int(if_blk.group(2))

        if_blk = re.search(
            r'^\s+5 minute input rate (\d+) bits/sec, (\d+) packets/sec', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['five_min_input_rate_bits_sec'] = int(if_blk.group(1))
            interfaces[if_name]['five_min_input_rate_packets_sec'] = int(if_blk.group(2))

        if_blk = re.search(
            r'^\s+5 minute output rate (\d+) bits/sec, (\d+) packets/sec', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['five_min_output_rate_bits_sec'] = int(if_blk.group(1))
            interfaces[if_name]['five_min_output_rate_packets_sec'] = int(if_blk.group(2))

        if_blk = re.search(
            r'^\s+(\d+) packets input, (\d+) bytes, (\d+) no buffer\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['packets_input'] = int(if_blk.group(1))
            interfaces[if_name]['packets_input_bytes'] = int(if_blk.group(2))
            interfaces[if_name]['packets_input_no_buffer'] = int(if_blk.group(3))

        if_blk = re.search(r'^\s+Received (\d+) broadcasts \((\d+) multicasts\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['received_broadcasts'] = int(if_blk.group(1))
            interfaces[if_name]['received_multicasts'] = int(if_blk.group(2))

        if_blk = re.search(
            r'^\s+(\d+) runts, (\d+) giants, (\d+) throttles ?\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['runts'] = int(if_blk.group(1))
            interfaces[if_name]['giants'] = int(if_blk.group(2))
            interfaces[if_name]['throttles'] = int(if_blk.group(3))

        if_blk = re.search(
            r'^\s+(\d+) input errors, (\d+) CRC, (\d+) frame, (\d+) overrun, (\d+) ignored\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['input_errors'] = int(if_blk.group(1))
            interfaces[if_name]['crc_errors'] = int(if_blk.group(2))
            interfaces[if_name]['frame_errors'] = int(if_blk.group(3))
            interfaces[if_name]['overruns'] = int(if_blk.group(4))
            interfaces[if_name]['ignored'] = int(if_blk.group(5))

        if_blk = re.search(
            r'^\s+(\d+) watchdog, (\d+) multicast, (\d+) pause input\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['watchdog'] = int(if_blk.group(1))
            interfaces[if_name]['multicast'] = int(if_blk.group(2))
            interfaces[if_name]['pause_input'] = int(if_blk.group(3))

        if_blk = re.search(
            r'^\s+(\d+) input packets with dribble condition detected\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['input_packets_dribble_condition'] = int(if_blk.group(1))

        if_blk = re.search(
            r'^\s+(\d+) packets output, (\d+) bytes, (\d+) underruns\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['packets_output'] = int(if_blk.group(1))
            interfaces[if_name]['packets_output_bytes'] = int(if_blk.group(2))
            interfaces[if_name]['packets_output_underruns'] = int(if_blk.group(3))

        if_blk = re.search(r'^\s+Output (\d+) broadcasts \((\d+) multicasts\)\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['output_broadcasts'] = int(if_blk.group(1))
            interfaces[if_name]['output_multicasts'] = int(if_blk.group(2))

        if_blk = re.search(
            r'^\s+(\d+) output errors, (\d+) collisions, (\d+) interface resets\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['output_errors'] = int(if_blk.group(1))
            interfaces[if_name]['collisions'] = int(if_blk.group(2))
            interfaces[if_name]['interface_resets'] = int(if_blk.group(3))

        if_blk = re.search(
            r'^\s+(\d+) unknown protocol drops\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['unknown_protocol_drops'] = int(if_blk.group(1))

        if_blk = re.search(
            r'^\s+(\d+) babbles, (\d+) late collision, (\d+) deferred\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['babbles'] = int(if_blk.group(1))
            interfaces[if_name]['late_collision'] = int(if_blk.group(2))
            interfaces[if_name]['deferred'] = int(if_blk.group(3))

        if_blk = re.search(
            r'^\s+(\d+) lost carrier, (\d+) no carrier, (\d+) pause output\n', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['lost_carrier'] = int(if_blk.group(1))
            interfaces[if_name]['no_carrier'] = int(if_blk.group(2))
            interfaces[if_name]['pause_output'] = int(if_blk.group(3))

        if_blk = re.search(
            r'^\s+(\d+) output buffer failures, (\d+) output buffers swapped out', if_payload, re.MULTILINE)
        if if_blk:
            interfaces[if_name]['output_buffer_failures'] = int(if_blk.group(1))
            interfaces[if_name]['output_buffers_swapped_out'] = int(if_blk.group(2))

        if mod_port:
            if len(mod_port) > 1:
                if 'modules' in collection:
                    if mod_port[0] in collection['modules']:
                        collection['modules'][mod_port[0]]['interfaces'][if_name] = interfaces[if_name]
                        del interfaces[if_name]

    ci = None
    b2 = False
    for line in output.split('\n'):
        cur_int = re.search(r'^(.*?) is (up|down), line protocol', line)
        if cur_int:
            pi = ci
            ci = cur_int.group(1)
            if b2:
                try:
                    interfaces[pi]['bound_to_int']
                except KeyError:
                    interfaces[pi]['bound_to_int'] = []
                interfaces[pi]['bound_to_int'].append(ci)
                b2 = False
        if re.search(r'^Bound to:$', line):
            b2 = True
        multilink_bundle = re.search(r'^\s+Link is a member of Multilink bundle (.*?)$', line)
        if multilink_bundle:
            try:
                interfaces[multilink_bundle.group(1)]['multilink_bundle']
            except KeyError:
                interfaces[multilink_bundle.group(1)]['multilink_bundle'] = []
            if ci not in interfaces[multilink_bundle.group(1)]['multilink_bundle']:
                interfaces[multilink_bundle.group(1)]['multilink_bundle'].append(ci)
        bound_to_int = re.search(r'^\s+Bound to (.*?) VCD: \d+', line)
        if bound_to_int:
            try:
                interfaces[bound_to_int.group(1)]['bound_to']
            except KeyError:
                interfaces[bound_to_int.group(1)]['bound_to'] = []
            if ci not in interfaces[bound_to_int.group(1)]['bound_to']:
                interfaces[bound_to_int.group(1)]['bound_to'].append(ci)

    if len(interfaces) == 0:

        interface = re.compile(
            r'^([A-Za-z].*?[0-9]) is (up|down)(\s+\((.*?)\))?(.*?pause)\n\n', re.MULTILINE | re.DOTALL)

        for if_name, oper_state, _, error_msg, if_payload in re.findall(interface, output + "\n\n"):

            count += 1
            interfaces[if_name] = {'operational_status': oper_state, 'index': count}

            tmp = get_interface_details(if_name)
            if tmp:

                if if_name not in interfaces:
                    interfaces[if_name] = {}

                interfaces[if_name]['aliases'] = tmp['aliases']
                interfaces[if_name]['physical'] = tmp['physical']

            interfaces[if_name]['admin_status'] = 'up'
            tmp = re.search(r'(admin state is |line protocol is )(up|down)', if_payload)
            if tmp:
                interfaces[if_name]['admin_status'] = tmp.group(2)

            tmp = re.search(r', autostate (enabled)\n', if_payload)
            if tmp:
                interfaces[if_name]['autostate_enabled'] = True if tmp.group(1) == 'enabled' else False

            if_blk = re.search(r'^\s+\((.*?)\)\n', if_payload)
            if if_blk:
                interfaces[if_name]['operational_state_comment'] = if_blk.group(1).strip()

            if_blk = re.search(r'\s+Belongs to (.*?)\n', if_payload)
            if if_blk:
                interfaces[if_name]['belongs_to'] = if_blk.group(1).strip()

            line_proto = re.search(r'^, line protocol is (up|down)', if_payload)
            if line_proto:
                interfaces[if_name]['admin_status'] = line_proto.group(1)

            if_blk = re.search(r'admin state is (.*?)(,(.*?))?(,?)\n', if_payload)
            if if_blk:
                interfaces[if_name]['admin_status'] = if_blk.group(1)
                if if_blk.group(2) is not None:
                    interfaces[if_name]['admin_state_comment'] = if_blk.group(2).strip() if \
                        if_blk.group(2).strip() != '' else None

            if interfaces[if_name]['admin_status'] == 'down':

                if 'operational_status' in interfaces[if_name]:

                    if re.search(r'^down', interfaces[if_name]['operational_status']):
                        collection['interfaces_shut'].append(if_name)
                        interfaces[if_name]['status'] = 'shut'

            elif interfaces[if_name]['admin_status'] == 'up':

                if 'operational_status' in interfaces[if_name]:

                    if re.search(r'^up', interfaces[if_name]['operational_status']):
                        collection['interfaces_active'].append(if_name)
                        interfaces[if_name]['status'] = 'active'

                    else:
                        collection['interfaces_down'].append(if_name)
                        interfaces[if_name]['status'] = 'down'

            if_blk = re.search(
                r'\s+Hardware(:| is)\s+(.*?), address(:| is)\s+(.*?)( \(bia (.*?)\))?\n', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['hardware'] = if_blk.group(2)
                interfaces[if_name]['mac_address'] = if_blk.group(4)
                interfaces[if_name]['built_in_address'] = if_blk.group(6)

            if_blk = re.search(r'^\s+Internet Address is (.*?)/(\d+)$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['ip_v4_address'] = if_blk.group(1)
                interfaces[if_name]['ip_v4_mask'] = int(if_blk.group(2))

            if_blk = re.search(r'^\s+Description: (.*?)$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['description'] = if_blk.group(1)
                if '=DISABLED=' in if_blk.group(1):
                    collection['interfaces_disabled'].append(if_name)
                elif '=RESERVED=' in if_blk.group(1):
                    collection['interfaces_reserved'].append(if_name)

            if_blk = re.search(
                r'^\s+MTU (.*?) bytes, BW (\d+) (Kbit/sec|Kbit ), DLY (\d+) usec', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['mtu'] = int(if_blk.group(1))
                interfaces[if_name]['bandwidth'] = int(if_blk.group(2))
                interfaces[if_name]['delay'] = int(if_blk.group(4))

            if_blk = re.search(
                r'^\s+reliability (\d+)/255, txload (\d+)/255, rxload (\d+)/255$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['reliability'] = int(if_blk.group(1))
                interfaces[if_name]['tx_load'] = int(if_blk.group(2))
                interfaces[if_name]['rx_load'] = int(if_blk.group(3))

            if_blk = re.search(r'^\s+Members in this channel: (.*?)\n\s+', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['channel_members'] = if_blk.group(1).split(', ')

            if_blk = re.search(r'^\s+Last clearing of "show interface" counters (.*?)\n', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['last_clearing_show_interface_counters'] = if_blk.group(1)

            if_blk = re.search(r'^\s+Encapsulation (.*?),', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['encapsulation'] = if_blk.group(1)

            if_blk = re.search(
                r'^\s+(full|half)-duplex,\s+(\d+)\s+(.*?)b/s$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['duplex'] = if_blk.group(1)
                interfaces[if_name]['speed'] = if_blk.group(2)
                interfaces[if_name]['speed_metric'] = if_blk.group(3)

            if_blk = re.search(
                r'^\s+auto-duplex,\s+auto-speed$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['duplex'] = 'auto'
                interfaces[if_name]['speed'] = 'auto'

            if_blk = re.search(
                r'^\s+Auto-Negotiation is turned (on|off)$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['auto_negotiation_active'] = True if if_blk.group(1) == 'on' else False

            if_blk = re.search(
                r'^\s+Auto-Negotiation is turned (on|off)\s+FEC mode is (.*?)$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['auto_negotiation_active'] = True if if_blk.group(1) == 'on' else False
                interfaces[if_name]['fec_mode'] = if_blk.group(2).lower()

            if_blk = re.search(
                r'^\s+Auto-mdix is turned (on|off)$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['auto_mdix'] = True if if_blk.group(1) == 'on' else False

            if_blk = re.search(
                r'^\s+EtherType is (0x.*?)(\s+)?$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['ether_type'] = if_blk.group(1)

            if_blk = re.search(
                r'^\s+Port mode is (.*?)(\s+)?$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['port_mode'] = if_blk.group(1)

            if_blk = re.search(
                r'^\s+Beacon is turned (on|off)(\s+)?$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['beacon_active'] = True if if_blk.group(1) == 'on' else False

            if_blk = re.search(
                r'^\s+Switchport monitor is (on|off)(\s+)?$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['switchport_monitor'] = True if if_blk.group(1) == 'on' else False

            if_blk = re.search(
                r'^\s+Active connector: (.*?)$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['active_connector'] = if_blk.group(1)

            if_blk = re.search(
                r'^\s+Input queue: (\d+)/(\d+)/(\d+)/(\d+) \(size/max/drops/flushes\);'
                r' Total o.*t drops: (\d+)',
                if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['input_queue_size'] = int(if_blk.group(1))
                interfaces[if_name]['input_queue_max'] = int(if_blk.group(2))
                interfaces[if_name]['input_queue_drops'] = int(if_blk.group(3))
                interfaces[if_name]['input_queue_flushes'] = int(if_blk.group(4))
                interfaces[if_name]['total_output_drops'] = int(if_blk.group(5))

            if_blk = re.search(
                r'^\s+Output queue: (\d+)/(\d+)/(\d+)/(\d+) \(size/max total/threshold/drops\)',
                if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['output_queue_size'] = int(if_blk.group(1))
                interfaces[if_name]['output_queue_max'] = int(if_blk.group(2))
                interfaces[if_name]['output_queue_drops'] = int(if_blk.group(3))
                interfaces[if_name]['output_queue_flushes'] = int(if_blk.group(4))

            if_blk = re.search(r'^\s+Output queue: (\d+)/(\d+) \(size/max\)', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['output_queue_size'] = int(if_blk.group(1))
                interfaces[if_name]['output_queue_max'] = int(if_blk.group(2))

            if_blk = re.search(
                r'^\s+5 minute input rate (\d+) bits/sec, (\d+) packets/sec', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['five_min_input_rate_bits_sec'] = int(if_blk.group(1))
                interfaces[if_name]['five_min_input_rate_packets_sec'] = int(if_blk.group(2))

            if_blk = re.search(
                r'^\s+5 minute output rate (\d+) bits/sec, (\d+) packets/sec', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['five_min_output_rate_bits_sec'] = int(if_blk.group(1))
                interfaces[if_name]['five_min_output_rate_packets_sec'] = int(if_blk.group(2))

            if_blk = re.search(
                r'^\s+1 minute input rate (\d+) bits/sec, (\d+) packets/sec$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['one_min_input_rate_bits_sec'] = int(if_blk.group(1))
                interfaces[if_name]['one_min_input_rate_packets_sec'] = int(if_blk.group(2))

            if_blk = re.search(
                r'^\s+1 minute output rate (\d+) bits/sec, (\d+) packets/sec$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['one_min_output_rate_bits_sec'] = int(if_blk.group(1))
                interfaces[if_name]['one_min_output_rate_packets_sec'] = int(if_blk.group(2))

            if_blk = re.search(
                r'\s(\d+) input packets (\d+) unicast packets (\d+) multicast packets\n\s+(\d+) '
                r'broadcast packets (\d+) bytes',
                if_payload, re.MULTILINE | re.DOTALL)
            if if_blk:
                interfaces[if_name]['input_packets'] = int(if_blk.group(1))
                interfaces[if_name]['input_unicast_packets'] = int(if_blk.group(2))
                interfaces[if_name]['input_multicast_packets'] = int(if_blk.group(3))
                interfaces[if_name]['input_broadcast_packets'] = int(if_blk.group(4))
                interfaces[if_name]['input_bytes'] = int(if_blk.group(5))

            if_blk = re.search(
                r'\s(\d+) output packets (\d+) unicast packets (\d+) multicast packets\n\s+(\d+) '
                r'broadcast packets (\d+) bytes',
                if_payload, re.MULTILINE | re.DOTALL)
            if if_blk:
                interfaces[if_name]['output_packets'] = int(if_blk.group(1))
                interfaces[if_name]['output_unicast_packets'] = int(if_blk.group(2))
                interfaces[if_name]['output_multicast_packets'] = int(if_blk.group(3))
                interfaces[if_name]['output_broadcast_packets'] = int(if_blk.group(4))
                interfaces[if_name]['output_bytes'] = int(if_blk.group(5))

            tmp = re.compile(
                r'\s+(\d+) seconds input rate (\d+) bits/sec, (\d+) packets/sec\n'
                r'\s+\1 seconds output rate (\d+) bits/sec, (\d+) packets/sec\n', re.MULTILINE | re.DOTALL)
            for rate, input_bps, input_pps, output_bps, output_pps in re.findall(tmp, if_payload):
                interfaces[if_name][rate + '_sec_input_rate_bps'] = int(input_bps)
                interfaces[if_name][rate + '_sec_input_rate_pps'] = int(input_pps)
                interfaces[if_name][rate + '_sec_output_rate_bps'] = int(output_bps)
                interfaces[if_name][rate + '_sec_output_rate_pps'] = int(output_pps)

            if_blk = re.search(
                r'\s+RX\n\s+(\d+) unicast packets\s+(\d+) multicast packets\s+(\d+) broadcast packets\n'
                r'\s+(\d+) input packets\s+(\d+) bytes\n'
                r'\s+(\d+) jumbo packets\s+(\d+) storm suppression bytes\n'
                r'\s+(\d+) runts\s+(\d+) giants\s+(\d+) CRC\s+(\d+) no buffer\n'
                r'\s+(\d+) input error\s+(\d+) short frame\s+(\d+) overrun\s+(\d+) underrun\s+(\d+) ignored\n'
                r'\s+(\d+) watchdog\s+(\d+) bad etype drop\s+(\d+) bad proto drop\s+(\d+) if down drop\n'
                r'\s+(\d+) input with dribble\s+(\d+) input discard\n'
                r'\s+(\d+) Rx pause\n',
                if_payload, re.MULTILINE | re.DOTALL
            )
            if if_blk:
                interfaces[if_name]['rx_unicast_packets'] = int(if_blk.group(1))
                interfaces[if_name]['rx_multicast_packets'] = int(if_blk.group(2))
                interfaces[if_name]['rx_broadcast_packets'] = int(if_blk.group(3))
                interfaces[if_name]['rx_input_packets'] = int(if_blk.group(4))
                interfaces[if_name]['rx_bytes'] = int(if_blk.group(5))
                interfaces[if_name]['rx_jumbo_packets'] = int(if_blk.group(6))
                interfaces[if_name]['rx_storm_suppression_packets'] = int(if_blk.group(7))
                interfaces[if_name]['rx_runts'] = int(if_blk.group(8))
                interfaces[if_name]['rx_giants'] = int(if_blk.group(9))
                interfaces[if_name]['rx_crc'] = int(if_blk.group(10))
                interfaces[if_name]['rx_no_buffer'] = int(if_blk.group(11))
                interfaces[if_name]['rx_input_error'] = int(if_blk.group(12))
                interfaces[if_name]['rx_short_frame'] = int(if_blk.group(13))
                interfaces[if_name]['rx_overrun'] = int(if_blk.group(14))
                interfaces[if_name]['rx_underrun'] = int(if_blk.group(15))
                interfaces[if_name]['rx_ignored'] = int(if_blk.group(17))
                interfaces[if_name]['rx_watchdog'] = int(if_blk.group(17))
                interfaces[if_name]['rx_bad_etype_drop'] = int(if_blk.group(18))
                interfaces[if_name]['rx_bad_proto_drop'] = int(if_blk.group(19))
                interfaces[if_name]['rx_if_down_drop'] = int(if_blk.group(20))
                interfaces[if_name]['rx_input_with_dribble'] = int(if_blk.group(21))
                interfaces[if_name]['rx_input_discard'] = int(if_blk.group(22))
                interfaces[if_name]['rx_pause'] = int(if_blk.group(23))

            if_blk = re.search(
                r'\s+TX\n\s+(\d+) unicast packets\s+(\d+) multicast packets\s+(\d+) broadcast packets\n'
                r'\s+(\d+) output packets\s+(\d+) bytes\n'
                r'\s+(\d+) jumbo packets\n'
                r'\s+(\d+) output error\s+(\d+) collision\s+(\d+) deferred\s+(\d+) late collision\n'
                r'\s+(\d+) lost carrier\s+(\d+) no carrier\s+(\d+) babble\s+(\d+) output discard\n'
                r'\s+(\d+) Tx pause',
                if_payload, re.MULTILINE | re.DOTALL
            )
            if if_blk:
                interfaces[if_name]['tx_unicast_packets'] = int(if_blk.group(1))
                interfaces[if_name]['tx_multicast_packets'] = int(if_blk.group(2))
                interfaces[if_name]['tx_broadcast_packets'] = int(if_blk.group(3))
                interfaces[if_name]['tx_input_packets'] = int(if_blk.group(4))
                interfaces[if_name]['tx_bytes'] = int(if_blk.group(5))
                interfaces[if_name]['tx_jumbo_packets'] = int(if_blk.group(6))
                interfaces[if_name]['tx_output_error'] = int(if_blk.group(7))
                interfaces[if_name]['tx_collision'] = int(if_blk.group(8))
                interfaces[if_name]['tx_deferred'] = int(if_blk.group(9))
                interfaces[if_name]['tx_late_collision'] = int(if_blk.group(10))
                interfaces[if_name]['tx_lost_carrier'] = int(if_blk.group(11))
                interfaces[if_name]['tx_no_carrier'] = int(if_blk.group(12))
                interfaces[if_name]['tx_babble'] = int(if_blk.group(13))
                interfaces[if_name]['tx_output_discard'] = int(if_blk.group(14))
                interfaces[if_name]['tx_pause'] = int(if_blk.group(15))

            if_blk = re.search(
                r'^\s+(\d+) interface resets$', if_payload, re.MULTILINE)
            if if_blk:
                interfaces[if_name]['interface_resets'] = if_blk.group(1)

    if 'interfaces' not in collection:
        collection['interfaces'] = {}

    for interface in interfaces:
        if interface not in collection['interfaces']:
            collection['interfaces'][interface] = {}

        collection['interfaces'][interface].update(interfaces[interface])

    return True, collection


def get_interface_details(name):

    """

        Obtain additional information based on interface names. E.g. Interface name aliases, physical vs. logical, etc.

    :param name: Name of interface
    :return:
    """

    tmp = re.search(r'^(.*?)(\d+.*)$', name)
    if tmp:
        if_type, if_num = tmp.group(1), tmp.group(2)
        physical = True

        if if_type == 'Ethernet':
            res = ['e' + if_num, 'Et' + if_num, 'Eth' + if_num]
        elif if_type == 'BRI':
            res = ['bri' + if_num, 'BRI ' + if_num]
        elif if_type == 'NVI':
            res = ['nvi' + if_num, 'NVI ' + if_num]
        elif if_type == 'Embedded-Service-Engine':
            res = []
        elif if_type == 'Service-Engine':
            res = []
        elif if_type == 'Cellular':
            res = []
        elif if_type == 'ISM':  # Integrated/Internal Service Module
            res = []
        elif if_type == 'FastEthernet':
            res = ['Fa' + if_num, 'Fas' + if_num]
        elif if_type == 'Loopback':
            res = ['lo' + if_num]
        elif if_type == 'Async':
            res = ['Async' + if_num, 'As' + if_num]
        elif if_type == 'ucse':
            res = ['ucse' + if_num, 'Uc' + if_num]
        elif if_type == 'GMPLS':
            res = ['Gmpls' + if_num, 'Gm' + if_num]
        elif if_type == 'HundredGigE':
            res = ['Hun' + if_num, 'Hu' + if_num]
        elif if_type == 'GigabitEthernet':
            res = ['Gig' + if_num, 'Gi' + if_num]
        elif if_type == 'TenGigabitEthernet':
            res = ['Ten' + if_num, 'Te' + if_num]
        elif if_type == 'TwoGigabitEthernet':
            res = ['Two' + if_num, 'Tw' + if_num]
        elif if_type == 'TwentyFiveGigE':
            res = ['TwentyFiveGigabitEthernet' + if_num, 'Twe' + if_num]
        elif if_type == 'AppGigabitEthernet':
            res = ['App' + if_num, 'App ' + if_num]
        elif if_type == 'Tunnel':
            res = ['tun' + if_num, 'tun ' + if_num]
        elif if_type == 'FiveGigabitEthernet':
            res = ['FiveGigE' + if_num]
        elif if_type == 'FortyGigabitEthernet':
            res = ['FortyGigE' + if_num, 'For ' + if_num]
        elif if_type.lower() == 'port-channel':
            res = ['Po' + if_num]
            physical = False
        elif if_type.lower() == 'vlan':
            res = ['vlan' + if_num, 'Vlan ' + if_num]
            physical = False
        elif if_type == 'mgmt':
            res = ['mgmt' + if_num]
            physical = False
        elif if_type == 'Serial':
            res = ['s' + if_num, 'Ser' + if_num, 'Ser ' + if_num]
        else:
            print(f"New interface type '{if_type}' - {name}")
            res = []

        return {'aliases': res, 'physical': physical}

    else:

        return None
