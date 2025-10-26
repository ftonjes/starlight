import re


def analyze(output, collection=None):

    """

        Netscout - 'ip interfaces show' command analysis

    :param output: output from 'ip interfaces show' on a Netscout device (type: str)
    :param collection: collection to which analyzed information is added to
    :return: collection with included analysis from 'ip interfaces show' command
    """

    # Version: 1.0 - Initial version
    # Description: Analyze 'ip interfaces show' output from a Netscout device
    # Regex: '^ip interfaces show$'

    # If no prior collection is specified, assume this is a new one:
    if collection is None:
        collection = {}
    elif not isinstance(collection, dict):
        return False, "Collection should be in 'dict' format."

    if not isinstance(output, str):
        return False, "Output from 'ip interfaces show' command should be in string format."

    tmp = re.compile(
        r'^(.*?\d+)\s+(.*?), Interface is (UP|DOWN), mtu (\d+)\n\s+Hardware: (.*?)\n(\s+Media: (.*?)( autoselect)?\n)?'
        r'\s+Status: (.*?)\n\s+Inet: (.*?) netmask (\d+\.\d+\.\d+\.\d+)(\sbroadcast (\d+\.\d+\.\d+\.\d+)|\sbroadcast)?'
        r'(\s+Inet6: (.*?:.*?) prefixlen (\d+)\n)?\s+Input: (\d+)\spkts, (\d+) bytes, (\d+) errors\n'
        r'\s+Output: (\d+)\spkts, (\d+) bytes, (\d+) errors(, (\d+) collisions)?\n'
        r'(\s+Interrupts: (\d+)\n)?(\s+Bypass to ((int|ext)\d+) (disabled|enabled)\n)?'
        r'(\s+SFP: (.*?)\n)?\n', re.MULTILINE | re.DOTALL)

    collection['interfaces'] = {}

    for name, if_type, oper_status, mtu, mac_addr, _, media, _, status, ip_v4_addr, ip_v4_mask, _, ip_v4_bcast, _, \
            ip_v6_addr, ip_v6_prefix, in_pkts, in_bytes, in_errs, out_pkts, out_bytes, out_errs, _, out_colls, \
            _, interupts, _, bypass_to_int, _, bypass_enabled, _, sfp in re.findall(tmp, output):

        collection['interfaces'][name] = {
            'type': if_type,
            'oper_status': oper_status.lower(),
            'mtu': int(mtu),
            'mac_addr': mac_addr,
            'media': media if media != '' else None,
            'ip_v4_address': ip_v4_addr,
            'ip_v4_mask': ip_v4_mask,
            'ip_v4_broadcast': ip_v4_bcast,
            'ip_v6_address': ip_v6_addr if ip_v6_addr != '' else None,
            'ip_v6_prefix_length': int(ip_v6_prefix) if ip_v6_prefix != '' else None,
            'input_pkts': int(in_pkts),
            'input_bytes': int(in_bytes),
            'input_errors': int(in_errs),
            'output_pkts': int(out_pkts),
            'output_bytes': int(out_bytes),
            'output_errors': int(out_errs),
            'output_collisions': int(out_colls) if out_colls != '' else None,
            'interupts': int(interupts) if interupts != '' else None,
            'bypass_enabled': True if bypass_enabled.lower() == 'enabled' else False,
            'bypass_interface': bypass_to_int if bypass_to_int != '' else None,
            'sfp': str(sfp).strip() if sfp != '' else None
        }
        tmp2 = re.search(r"^(Active )?(\d+)Mb/s (Full|Half)$", status)
        if tmp2:
            collection['interfaces'][name]['speed_mbps'] = tmp2.group(2)
            collection['interfaces'][name]['duplex'] = tmp2.group(3).lower()
            collection['interfaces'][name]['admin_status'] = 'up'
            collection['interfaces'][name]['status'] = 'Active'
        else:
            if status == 'Inactive':
                collection['interfaces'][name]['admin_status'] = 'down'
            else:
                collection['interfaces'][name]['admin_status'] = 'up'
            collection['interfaces'][name]['status'] = status

    return True, collection
