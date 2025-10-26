import re
import datetime
import pprint


def analyze(output, collection=None):

    """

        Cisco - 'show vlan' command analysis

    :param output: output from 'show vlan' on a Cisco device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'show vlan' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'show vlan' output from a Cisco device
    # Regex: '^show vlan$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'show vlan' command should be in string format."

    collection['host_vendor'] = 'Cisco'
    collection['_host_name_extraction'] = "^(.*?)[>#]"

    # Check for error messages:
    find_error = re.search(r'(% (Invalid|Ambiguous).*)(\n)?', output)
    if find_error:
        collection['_error'] = find_error.group(1)
        return False, collection

    # START

    vlans = {}

    tmp = re.search(
        r'\nVLAN\s+Name\s+Status\s+Ports\n--.*?--\n(.*?\n)\n',
        output, re.MULTILINE | re.DOTALL)

    if tmp:
        tmp2 = re.compile(
            r'^(\d+) +(.*?) +(\S+)(\n|( +.*?\n)((\s+Gi\d+.*?/\d+)*)\n|( +.*?\n))', re.MULTILINE)

        for vlan_id, name, status, members, _, _, _, _ in re.findall(tmp2, tmp.group(1)):

            members = members[:-1].replace(' ', '').replace('\n', ',').split(',')

            # Remove any 'blank' members
            if '' in members:
                members.remove('')

            # Replace list with None
            if len(members) == 0:
                members = None

            # Add vlan info
            vlans[int(vlan_id)] = {
                'name': name,
                'status': status,
                'members': members}

    tmp = re.search(
        r'\nVLAN +Type +SAID +MTU +Parent +RingNo +BridgeNo +Stp +BrdgMode +Trans1 +Trans2\n--.*?--\n(.*?\n)\n',
        output, re.MULTILINE | re.DOTALL)

    if tmp:
        tmp2 = re.compile(
            r'^(\d+) +(.*?) +(\d+) +(\d+) +(-|\d+) +(-|\d+) +(-|\d+) +(-|\S+) +(-|\S+) +(-|\d+) +(-|\d+)',
            re.MULTILINE)

        for vlan_id, vlan_type, said, mtu, parent, ring_no, bridge_no, stp, brdg_mode, trans1, trans2 in re.findall(
                tmp2, tmp.group(1)):

            if int(vlan_id) not in vlans:
                vlans[int(vlan_id)] = {}

            vlans[int(vlan_id)]['type'] = vlan_type
            vlans[int(vlan_id)]['said'] = int(said)
            vlans[int(vlan_id)]['mtu'] = int(mtu)
            if parent != '-':
                vlans[int(vlan_id)]['parent'] = int(parent)
            if ring_no != '-':
                vlans[int(vlan_id)]['ring_number'] = int(ring_no)
            if bridge_no != '-':
                vlans[int(vlan_id)]['bridge_number'] = int(bridge_no)
            if stp != '-':
                vlans[int(vlan_id)]['stp'] = stp
            if ring_no != '-':
                vlans[int(vlan_id)]['bridge mode'] = brdg_mode

            vlans[int(vlan_id)]['trans_1'] = int(trans1)
            vlans[int(vlan_id)]['trans_2'] = int(trans2)

    collection['vlans'] = vlans

    return True, collection
