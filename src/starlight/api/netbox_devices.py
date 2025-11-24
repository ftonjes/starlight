import os
import sys
import re
import pynetbox
import requests
import logging

from lib.core_utilities import parse_configuration, get_key
from pprint import pprint

requests.packages.urllib3.disable_warnings()


def convert_netbox_data(data, fields=None, show_fields=False):

    """
        Convert data from netbox API call into dictionary containing key/value pairs. Dictionary is one level deep,
          with deeper levels converted to 'dotted' format. e.g.: {'site': {'name': 'London', 'id': 10}} will be
          converted to {'site.name': 'London', 'site.id': 10}.

    :param data: List of dictionaries containing data returned from Netbox API call,
    :param fields: List of fields. These may contain a colon when titles should be renamed, e.g.: 'name:Name'. This
                     renames a field 'name' with 'Name'.
    :param show_fields: This is used to view what fields are returned from a Netbox API call (debugging).
    :return: Modified field_list, data
    """

    # The 'fields' list contains all the fields we wish to extract from the returned Netbox data. If the
    #   field contains a colon (':'), any text to the left is the name of the field(s) from the Netbox. The text to the
    #   right of the colon is used to change the name of the field, e.g.: The fields ['name:Name', 'region:Region']
    #   will return the name and region but rename the fields to 'Name' and 'Region'.
    # Note: This function only walks through a dictionary's top 5 levels. Anything deeper just returns the dictionary
    #   in text form (pprint's pformat funtion).
    # Note: Any top level property containing a list, e.g.: tags, will have a list propery added (tags.list) with
    #   a list of items
    # Note: Any key with a .url will have the 'url_api' key set to the URL value. Another key 'url' will be added
    #   without the '/api' component, so it links to the page in Netbox instead of the API url. e.g.:
    #      device_type.manufacturer.url: https://netbox.company.com/dcim/manufacturers/2,
    #      device_type.manufacturer.url_api: https://netbox.company.com/api/dcim/manufacturers/2/,
    new_field_list = []
    new_data = []

    field_dict = {}
    if fields is not None:
        for field in fields:
            tmp = re.search(r'^(.*?):(.*)$', field)
            if tmp:
                field_dict[tmp.group(1)] = tmp.group(2)
            else:
                field_dict[tmp.group(1)] = tmp.group(1)
            new_field_list.append(field_dict[tmp.group(1)])

    for item in data:
        new_fields = {}
        for field in item:
            current_key = field
            if item[field] is None:
                new_fields[current_key] = None
            elif isinstance(item[field], list):
                if len(item[field]) > 0:
                    new_fields[current_key] = item[field]
                    field_name = None
                    for field_index, sub_item in enumerate(item[field]):
                        if field_index == 0:
                            if 'display' in sub_item:
                                field_name = 'display'
                            elif 'name' in sub_item:
                                field_name = 'name'
                            elif 'slug' in sub_item:
                                field_name = 'slug'
                            if field_name is not None:
                                new_fields[f"{current_key}.list"] = ''
                        new_fields[f"{current_key}.list"] += f"{sub_item[field_name]}"
                        if field_index + 1 < len(item[field]):
                            new_fields[f"{current_key}.list"] += '\n'
                else:
                    new_fields[current_key] = None
            elif isinstance(item[field], dict):
                for field_2 in item[field]:
                    current_key_2 = f"{current_key}.{field_2}"
                    if item[field][field_2] is None:
                        new_fields[current_key_2] = None
                    elif isinstance(item[field][field_2], dict):
                        for field_3 in item[field][field_2]:
                            current_key_3 = f"{current_key}.{field_2}.{field_3}"
                            if item[field][field_2][field_3] is None:
                                new_fields[current_key_3] = None
                            elif isinstance(item[field][field_2][field_3], dict):
                                for field_4 in item[field][field_2][field_3]:
                                    current_key_4 = f"{current_key}.{field_2}.{field_3},{field_4}"
                                    if item[field][field_2][field_3][field_4] is None:
                                        new_fields[current_key_4] = None
                                    elif isinstance(item[field][field_2][field_3][field_4], dict):
                                        for field_5 in item[field][field_2][field_3][field_4]:
                                            current_key_5 = f"{current_key}.{field_2}.{field_3},{field_4},{field_5}"
                                            if item[field][field_2][field_3][field_4][field_5] is None:
                                                new_fields[current_key_5] = None
                                            elif isinstance(item[field][field_2][field_3][field_4][field_5], dict):
                                                new_fields[current_key_5] = pformat(
                                                    item[field][field_2][field_3][field_4][field_5])
                                            else:
                                                new_fields[current_key_5] = item[
                                                    field][field_2][field_3][field_4][field_5]
                                    else:
                                        if '.url' in current_key_3:
                                            new_fields[f"{current_key_4.replace('.url', '.url_api')}"] = item[
                                                field][field_2][field_3][field_4]
                                            new_fields[current_key_4] = item[
                                                field][field_2][field_3][field_4].replace('/api', '')[:-1]
                                        else:
                                            new_fields[current_key_4] = item[field][field_2][field_3][field_4]
                            else:
                                if '.url' in current_key_3:
                                    new_fields[f"{current_key_3.replace('.url', '.url_api')}"] = item[
                                        field][field_2][field_3]
                                    new_fields[current_key_3] = item[field][field_2][field_3].replace('/api', '')[:-1]
                                else:
                                    new_fields[current_key_3] = item[field][field_2][field_3]
                    else:
                        if '.url' in current_key_2:
                            new_fields[f"{current_key_2.replace('.url', '.url_api')}"] = item[field][field_2]
                            new_fields[current_key_2] = item[field][field_2].replace('/api', '')[:-1]
                        else:
                            new_fields[current_key_2] = item[field][field_2]
            else:
                if current_key == 'url':
                    new_fields['url_api'] = item[field]
                    new_fields[current_key] = item[field].replace('/api', '')[:-1]
                else:
                    new_fields[current_key] = item[field]

        if show_fields:
            pprint(new_fields, width=300)
            sys.exit(3)

        if fields is None:
            for field in new_fields:
                if field not in new_field_list:
                    new_field_list.append(field)
                    field_dict[field] = field

        tmp = {}
        for field in field_dict:
            if field in new_fields:
                tmp[field_dict[field]] = new_fields[field]

        new_data.append(tmp)

    return new_field_list, new_data

