import os
import sys
import re
import pynetbox
import requests

from lib.core_utilities import parse_configuration, get_key
from pprint import pprint

requests.packages.urllib3.disable_warnings()


def get_inventory(nb_filter=None, logger=False):

    """

        Netbox Devices (netbox_devices.py)

    :param nb_filter: netbox filter in dictionary format
    :param logger: logger object for logging
    :return: inventory (dict)
    """

    success, configuration = parse_configuration(configuration='./api/cfg/configuration.json')

    if not success:
        return false, configuration

    nb = pynetbox.api(
        configuration['apis']['netbox_prod']['url'],
        get_key(configuration['apis']['netbox_prod']['token']))

    nb.http_session = requests.session()
    nb.http_session.verify = False

    if nb_filter is None:
        nb_filter = 'all'

    if nb_filter in filter_list:
        try:
            nb_devices = nb.dcim.devices.filter(
                **filter_list[nb_filter])
        except Exception as err:
            return False, f"Netbox Error: '{err}'"
    else:
        return False, f"Invalid Netbox Filter '{nb_filter}'"

    nb_sites = {x.id: x for x in nb.dcim.sites.all()}
    nb_regions = {x.id: x for x in nb.dcim.regions.all()}
    nb_inventory = []

    # Filter out unwanted devices (224.x, duplicates, etc):
    filtered_nb_devices = []
    ip_v4a_ddresses = {}    # list of ip_v4_addresses
    found_duplicate = False

    for device in nb_devices:
        if re.search(r'^224\.0\.', device.primary_ip.address.split('/')[0]):  # Skip multicast addresses
            continue
        if device.primary_ip.address.split('/')[0] not in ip_v4a_ddresses:
            ip_v4a_ddresses[device.primary_ip.address.split('/')[0]] = []
        ip_v4a_ddresses[device.primary_ip.address.split('/')[0]].append(device)
        if len(ip_v4a_ddresses[device.primary_ip.address.split('/')[0]]) <= 1:
            filtered_nb_devices.append(device)
        else:
            if not found_duplicate:
                logger.debug(f'Found duplicates:')
                found_duplicate = True
            logger.debug(
                f"  {device.name} ({device.primary_ip.address.split('/')[0]}/"
                f"{ip_v4a_ddresses[device.primary_ip.address.split('/')[0]][0].id}) -> Netbox ID {device.id}.")

    for index, device in enumerate(filtered_nb_devices):

        # Mapping from Netbox to Interakt OS names
        os_mapping = {
            'IOS-XE': {'os_type': 'cisco_ios'},
            'Cisco IOS': {'os_type': 'cisco_ios'},
            # 'Cisco ASA': {'os_type': 'cisco_asa'},
            'Cisco NX-OS': {'os_type': 'cisco_nxos'},
            # 'Juniper Junos': {'os_type': 'junios'},
            'CGXOS': {'os_type': 'cgx_os'},
            'TMOS': {'os_type': 'f5_tmos'},
            # 'RiOS': {'os_type': 'rios'},
            'OG-OS': {'os_type': 'og_os'},
            'Arista EOS': {'os_type': 'arista_eos'},
            'ArubaOS': {'os_type': 'aruba_os'},
            'ExtrahopOS': {'os_type': 'eh_os'},
            'PAN-OS': {'os_type': 'pan_os'},
            # 'Arbor ArbOS': {'os_type': 'arb_os'}
        }

        netbox_platform = device.platform.name if device.platform is not None else None
        if netbox_platform not in os_mapping:
            continue
        else:
            if device.primary_ip is None:
                continue

        # Work out what auth to use per device type:
        auth = 'devices'
        command_list = []
        interakt_os_type = os_mapping[netbox_platform]['os_type']
        if interakt_os_type in ['pan_os']:
            auth = 'ipfabric_ro'
            command_list.extend(
                [
                    'set cli scripting-mode on',
                    'show system info',
                    # 'show arp all',
                    # 'show arp management',
                    # 'show system resources',
                    # 'show high-availability state',
                    # 'show system services',
                    'show interface all',
                    # 'show interface ethernet1/1',
                    # 'show interface vlan',
                    # 'show system state filter-pretty sw.dev.runtime.ifmon.port-states',
                    'show config merged',
                    'show system environmentals',
                    # 'show config pushed-shared-policy vsys vsys1',
                    # 'request license info'
                ])
        if interakt_os_type in ['arista_eos']:
            command_list.extend(
                [
                    'terminal length 0',
                    'show version',
                    'show vlan',
                    'show cdp neighbors',
                    'show ip interface brief',
                    'show running-config'
                ])
        elif interakt_os_type == 'cisco_ios':
            command_list.extend(
                [
                    'terminal length 0',
                    'show version',
                    'show vlan',
                    'show power',
                    'show module all',
                    'show cdp neighbors',
                    'show ip interface brief',
                    'show platform',
                    'show hardware',
                    'show snmp community',
                    'show running-config',
                    # '/EXEC check_compliance/'
                ]
            )
        elif interakt_os_type == 'cisco_nxos':
            command_list.extend(
                [
                    'terminal length 0',
                    'show version',
                    'show vlan',
                    'show power',
                    'show module all',
                    'show cdp neighbors',
                    'show ip interface brief',
                    'show platform',
                    'show hardware',
                    'show snmp community',
                    'show running-config',
                    # '/EXEC check_compliance/'
                ]
            )
        elif interakt_os_type == 'og_os':
            command_list.extend(
                [
                    'cat /proc/uptime',
                    'config -g config',
                    'showserial',
                    'ip -s -s -d link',
                    'setfset',
                    'ip address',
                    'ntpq -pn',
                    'cat /proc/meminfo',
                    'cat /proc/cpuinfo',
                    'check_version',
                    'cat /proc/uptime',
                    'uname -a',
                    'cat /etc/os-release'
                    # '/EXEC opengear_checks/'
                ]
            )
        elif interakt_os_type == 'f5_tmos':
            auth = 'ens-rw'  # On some devices ens-ro does not have access to excecute bash
            command_list.extend(
                [
                    'show sys version',
                    'show sys hardware',
                    "run util bash -c 'cat /proc/uptime'",
                    'cd /Common; show net arp all',
                    'cd /Common; list auth partition',
                    'cd /Common; list net self recursive',
                    'cd /Common; show cm device',
                    'cd /Common; show sys tmm-info raw',
                    'cd /Common; show net interface all-properties',
                    'cd /Common; show net trunk all-properties',
                    'cd /Common; list net vlan recursive',
                    'cd /Common; show net self recursive',
                    'cd /Common; show sys cluster all-properties',
                    'cd /Common; list net tunnels all-properties recursive',
                    'cd /Common; list net tunnels ipsec recursive',
                    'cd /Common; list net tunnels ipip recursive',
                    'cd /Common; list net tunnels gre recursive',
                    'cd /Common; list /sys management-ip',
                    # 'cd /Common; list ltm virtual recursive',        # Takes a while
                    'cd /Common; show net route recursive',
                    'list /sys management-route',
                    'cd /Common; list /net route-domain',
                    # 'imish -r 0',                                    # Errors out
                    'cd /Common; list net trunk all-properties',
                    'cd /Common; run util bash -c "tmsh list sys snmp all-properties"',
                    'cd /Common; run util bash -c "ntpq -np"',
                    'cd /Common; list /auth password-policy all-properties',
                    # 'cd /Common; show ltm virtual recursive',        # Takes a while
                    # 'cd /Common; show ltm pool detail recursive',    # Takes a while
                    'cd /Common; list ltm snatpool recursive',
                    'cd /Common; list /sys syslog remote-servers',
                    'cd /Common; list /sys sflow receiver all-properties',
                    'cd /Common; show sys sflow data-source',
                    'cd /Common; list sys dns'
                ]
            )
        elif interakt_os_type == 'aruba_os':
            auth = 'ipfabric_ro'
            command_list.extend(
                [
                    'no paging',
                    'show version',
                    'show inventory',
                    'show slots',
                    'show interface',
                    'show lldp neighbor',
                    'show ap active',
                    # 'show running-config'
                ]
            )
        elif interakt_os_type == 'cgx_os':
            # auth = 'cgx_ssh_ro'
            auth = 'ipfabric_ro'
            command_list.extend(
                [
                    'dump overview'
                ]
            )

        # Only accept site criticality value of 1 - 4.
        site_criticality = None
        if nb_sites[device.site.id].custom_fields['criticality'] in ['1', '2', '3', '4']:
            site_criticality = int(nb_sites[device.site.id].custom_fields['criticality'])

        # Cater for when site_employees has None, '' or other invalid info:
        try:
            site_employees = int(nb_sites[device.site.id].custom_fields['total_employees'])
        except (TypeError, ValueError):
            site_employees = None

        if device.platform.name in ['ArubaOS', 'PAN-OS', 'CGXOS']:
            jh = {'display': "IPFabric"}
        else:
            jh = {'region': nb_regions[nb_sites[device.site.id].region.id].parent.name.lower()}

        nb_inventory.append({
            'host': device.primary_ip.address.split('/')[0],
            # If we use 'region', we effectively have 3 queues, 1 for each region. Not as efficient as using 'role',
            #   specifically if there are more in one region than others. Once a region is complete, free 'spots' are
            #   not used by the remaining regions. When using 'role' we test from any available region, and all 'spots'
            #   are in use at all times, until the last device is checked.

            # 3 queues - 1 for each region
            'jump_hosts': jh,

            # 'jump_hosts': {'role': 'automation'},       # 1 queue - for all regions usually faster
            'authentication': auth,
            "type": "ssh",
            "policy": 'first-success',
            'os_type': interakt_os_type,
            "parameters": {
                "netbox_region": nb_regions[nb_sites[device.site.id].region.id].parent.name,
                "netbox_sub_region": nb_sites[device.site.id].region.name,
                "netbox_ens_location_code": nb_sites[device.site.id].custom_fields['ens_location_code'],
                "netbox_site_criticality": site_criticality,
                "netbox_site_employees": site_employees,
                "netbox_site_city": nb_sites[device.site.id].custom_fields['city'],
                "netbox_site_name": nb_sites[device.site.id].name,
                "netbox_site_tenant": nb_sites[device.site.id].tenant.name if nb_sites[
                    device.site.id].tenant is not None else None,
                "netbox_facility_number": nb_sites[device.site.id].facility,
                "netbox_site_id": nb_sites[device.site.id].id,
                "netbox_device_id": device.id,
                "netbox_device_name": device.name,
                "netbox_device_tags": device.tags,
                "netbox_device_type": device.device_type.display,
                "netbox_device_role": device.role.name,
                "netbox_os_type": device.platform.name if device.platform is not None else None,
                "netbox_status": device.status.label,
                "netbox_device_tenant": device.tenant.name if device.tenant is not None else None,
                "netbox_model": device.device_type.model,
                "netbox_manufacturer": device.device_type.manufacturer.name,
                "netbox_platform": device.platform.name if device.platform is not None else None
            },
            "command_list": command_list,
        })

    return True, nb_inventory


filter_list = {
    'all': {
        'status': ['staged', 'active', 'planned'],
        'has_primary_ip': True,
        'manufacturer': ['aruba', 'arista', 'opengear', 'cisco', 'f5', 'palo-alto']
    },
    'cisco': {
        'status': ['staged', 'active', 'planned'],
        'manufacturer': ['cisco'],
        'has_primary_ip': True
    },
    'f5': {
        'status': ['staged', 'active', 'planned'],
        '|manufacturer': ['f5'],
        'has_primary_ip': True
    },
    # CGX devices no longer work using SSH
    # 'cloudgenix': {
    #     'status': ['staged', 'active', 'planned'],
    #     'platform': ['cgxos'],
    #     'has_primary_ip': True
    # },
    'aruba': {
        'status': ['staged', 'active', 'planned'],
        'manufacturer': ['aruba'],
        'has_primary_ip': True
    },
    'arista': {
        'status': ['staged', 'active', 'planned'],
        'manufacturer': ['arista'],
        'has_primary_ip': True
    },
    'opengear': {
        'status': ['staged', 'active', 'planned'],
        'manufacturer': ['opengear'],
        'has_primary_ip': True
    },
    'palo-alto': {
        'status': ['staged', 'active', 'planned'],
        'manufacturer': ['palo-alto'],
        'platform': ['pan-os'],
        'has_primary_ip': True
    },
    'custom': {
        'status': ['staged', 'active', 'planned'],
        'name': [
            'AUSYD9-01CE01', 'AUSYD9-01CE02'
        ],
        'has_primary_ip': True
    },
    'xtc-security': {
        'status': ['staged', 'active', 'planned'],
        'tenant_id': 56,
        'has_primary_ip': True
    }
}
