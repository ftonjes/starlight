import re
import requests
from datetime import datetime
from lib.core_utilities import parse_configuration, get_key
from pprint import pprint
import pytz
import json


requests.packages.urllib3.disable_warnings()


class ServiceNowSession:

    def __init__(self):

        success, configuration = parse_configuration(configuration='./api/cfg/configuration.json')
        if success:

            self.url = configuration['apis']['service_now_uat']['url']
            self.session = requests.Session()
            self.session.headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'}
            self.session.auth = (
                get_key(configuration['apis']['service_now_uat']['username']),
                get_key(configuration['apis']['service_now_uat']['password']))
            self.session.verify = False

        else:
            self.url = None
            self.error = configuration

    def close(self):
        self.session.close()


def get_user_info(email: str = None, value: str = None, fields: list = None):

    """
        Get user information from Service NOW
    """

    # Either the 'email' or 'value' can be used. Optionally, specific fields can be returned only.
    # Note: When using 'email' a list of dicts are returned, while value returns a single dict.
    sn = ServiceNowSession()
    endpoint = f"{sn.url}/api/now/table/sys_user"
    if email is not None and value is None:
        endpoint += f"?email={email}"
    if value is not None and email is None:
        endpoint += f"/{value}"
    if fields is not None:
        endpoint += f"{'&' if email is not None else '?'}sysparm_fields={','.join(fields)}"

    try:
        result = sn.session.get(url=endpoint)
    except requests.exceptions.RequestException as err:
        return False, err

    return True, result.json()['result']


def get_chg(chg):

    """
        Get CHG information from Service NOW
    """

    if not re.search(r'^CHG\d+$', chg):
        return False, "Change Reference should be in the format 'CHG00012345'."

    sn = ServiceNowSession()
    try:
        result = sn.session.get(url=f"{sn.url}/api/sn_chg_rest/change?number={chg}")
    except requests.exceptions.RequestException as err:
        return False, err

    sn.close()

    return True, result.json()['result'][0]


def request_change_approval(chg: str):

    # Move the CHG into Approval phase (emulate clicking 'Request Approval' button
    sn = ServiceNowSession()
    try:
        result = sn.session.patch(
            url=f"{sn.url}/api/sn_chg_rest/change/standard/{template_sys_id}",
            data=json.dumps(payload)
        )
    except requests.exceptions.RequestException as err:
        return False, err

    sn.close()
    return True, result.json()


def create_new_standard_change(
        start_date,
        end_date,
        cfg_type: str = None,
        device_list: list = None,
        timezone: str = None,
        requestor: str = None,
        template_id: str = None
):

    # Calculate time-related information
    from_tz = pytz.timezone(timezone)
    to_tz = pytz.UTC
    date_format = "%Y-%m-%d %H:%M:%S"
    start_utc_date = datetime.strftime(from_tz.localize(start_date).astimezone(to_tz), date_format)
    end_utc_date = datetime.strftime(from_tz.localize(end_date).astimezone(to_tz), date_format)

    payload = {
        # "state": "Scheduled",
        "requested_by": requestor,
        "short_description": f"XTC Device Managment Standards Compliance Remediation - {cfg_type.upper()}",
        "start_date": start_utc_date,
        "end_date": end_utc_date,
    }

    sn = ServiceNowSession()
    try:
        result = sn.session.post(
            url=f"{sn.url}/api/sn_chg_rest/change/standard/{template_id}",
            data=json.dumps(payload)
        )
    except requests.exceptions.RequestException as err:
        return False, err

    pprint(result.json())

    if 'error' in result.json():
        if 'detail' in result.json()['error']:
            if result.json()['error']['detail'] != '':
                sn.close()
                return False, f"ServiceNOW error: '{result.json()['error']['detail']}'"
            else:
                sn.close()
                return False, f"ServiceNOW error: '{result.json()['error']['message']}'"

    sn.close()
    print(f"ServiceNOW change {result.json()['result']['number']['value']} created.")

    return True, result.json()['result']


