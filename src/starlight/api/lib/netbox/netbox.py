import logging
import os
import sys
import re
import pynetbox
import requests
import time

from lib.core_utilities import parse_configuration, get_key, split_string_by_char

from pprint import pprint


def get_netbox_api_endpoints():

    """
        Displays netbox endpoints. This is used to populate the above section when a newer version of Netbox has
          been released. As Netbox evolves, more endpoints may become available and/or endpoint names/urls may change.
        Note: This is formatted for direct copy-paste into the above ('query_type_to_endpoint_url') function.
    :return: Displays output similar to the 'query_type_to_endpoint_url' function.
    """

    success, configuration = parse_configuration(configuration='./api/lib/netbox/cfg/config.json')

    if not success:
        return False, configuration

    netbox_url = configuration['apis']['netbox_prod']['url']
    netbox_token = get_key(configuration['apis']['netbox_prod']['token'])
    nbs = netbox_session(netbox_url=netbox_url, netbox_token=netbox_token)
    root_results = nbs.get(f"{nbs.url}/api/").json()
    endpoint_list = {'endpoints': {}}

    for root_result in root_results:
        results = nbs.get(root_results[root_result]).json()
        if root_result == 'status':
            endpoint_list['endpoints'][root_result] = root_results[root_result]
            if 'netbox-version' in results:
                endpoint_list['endpoints_version'] = results['netbox-version']
        else:
            for result in results:
                if isinstance(results[result], str):
                    if nbs.url in results[result]:
                        endpoint_list['endpoints'][result] = results[result].replace(nbs.url, '')

    pprint(endpoint_list, width=200)
    sys.exit(0)


def netbox_session(netbox_token: str = None, netbox_url: str = None, ssl_verify: bool = False) -> requests.Session:

    """
        Initiates session to Netbox.
    """

    # Remove trailing '/' from Netbox URL (if one exists):
    if netbox_url is not None:
        if netbox_url[-1] == '/':
            netbox_url = netbox_url[:-1]

    s = requests.Session()
    if not ssl_verify:
        requests.packages.urllib3.disable_warnings()
        s.verify = False
    s.url = netbox_url
    s.headers['Content-Type'] = 'application/json'
    s.headers['Accept'] = 'application/json'
    s.headers['Authorization'] = f'Token {netbox_token}'

    return s


def get_via_requests(
        query_type: str = 'devices', netbox_filter: dict = None, ordering: list = None, post_processing: dict = None,
        limit: int = None, netbox_url: str = None, netbox_token: str = None, netbox_page_size: int = 1000,
        set_key: str = None, merge_data: dict = None, logger: logging.Logger = None, show_fields: list = None):

    """
        Get inventory from Netbox using REST API

        :param query_type: API endpoint name (for full list see 'query_type_to_endpoint_url' function,
        :param netbox_filter: Netbox filter e.g.: {'status': 'active', 'manufacturer': 'cisco'},
        :param ordering: Netbox order string used to sort fields e.g.: ['site', 'name'],
        :param post_processing: Netbox post processing function e.g.: {'status': 'active'},
        :param limit: Maximum number of records to return,
        :param set_key: Instead of a list of dicts, a dict of dicts is returned with set_key as primary key,
        :param merge_data: Used to enrich data with additional information.
        :param netbox_url: Netbox URL. This can be used when 'NETBOX_URL' environment variable is not set.
        :param netbox_token: Netbox Token. This can be used when 'NETBOX_TOKEN' environment variable is not set.
        :param netbox_page_size: Number of records to return per page during API calls
        :param show_fields: List of fields to include in the output
        :param logger: Logger instance

        Outputs True or False based on succes, (output: dict, field_list: list)

    """

    # For merge_data, you can provide a list of dicts containing {"key": <KEY>, "data": <DICT>}.
    # And example would be when requesting devices from Netbox, and additional site information is needed.
    # e.g.: {"data": sites, "key": "site.id"}:
    #   "data" refers to a dictionary from a previous get_via_requests request, and
    #   "key" refers to which key the "data" is using as it's primary key (eg. site id).
    # Fields found in "data" which do not exist, will be added.
    # There is also an option to remove 'custom_fields.' from any field name (makes referencing easier).

    success, configuration = parse_configuration(configuration='./api/lib/netbox/cfg/config.json')
    if not success:
        return False, configuration

    success, endpoints = parse_configuration(configuration='./api/lib/netbox/cfg/endpoints.json')
    if not success:
        return False, endpoints

    if netbox_url is None or netbox_url.lower() == 'prod':
        netbox_url = configuration['apis']['netbox_prod']['url']
    elif netbox_url.lower() == 'dev':
        netbox_url = configuration['apis']['netbox_dev']['url']
    if netbox_url[-1] == '/':  # Remove trailing '/' from base url (if one exists).
        netbox_url = netbox_url[:-1]

    if netbox_token is None:
        netbox_token = get_key(configuration['apis']['netbox_prod']['token'])

    if netbox_filter is not None:
        filter_name = None
        if isinstance(netbox_filter, str):
            if netbox_filter in configuration['filters']:
                filter_name = netbox_filter
                if 'query_type' in configuration['filters'][filter_name]:
                    if query_type is None:
                        query_type = configuration['filters'][filter_name]['query_type']
                if 'ordering' in configuration['filters'][filter_name]:
                    if ordering is None:
                        ordering = configuration['filters'][filter_name]['post_processing']
                if 'post_processing' in configuration['filters'][filter_name]:
                    if post_processing is None:
                        post_processing = configuration['filters'][filter_name]['post_processing']
                if 'show_fields' in configuration['filters'][filter_name]:
                    if show_fields is None:
                        show_fields = configuration['filters'][filter_name]['show_fields']

            if 'netbox_filter' in configuration['filters'][filter_name]:
                netbox_filter = configuration['filters'][filter_name]['netbox_filter']

    nbs = netbox_session(netbox_url=netbox_url, netbox_token=netbox_token)

    # Make sure limit is > 0
    if limit is not None:
        if limit < netbox_page_size:
            netbox_page_size = limit
        if limit <= 0 or not isinstance(limit, int):
            limit = None

    # Get API endpoint for query type:
    if query_type in endpoints['endpoints']:
        url = endpoints['endpoints'][query_type]
    else:
        return False, f"The API endpoint '{query_type}' is not valid."

    base_query = f"{netbox_url}{url}"
    url_operator = '?'

    # The 'query_string' variable contains 'filter' information, e.g.: '/api/dcim/devices/?status=active&region=nasa'
    #   used to restrict the output returned from Netbox. (e.g.: Devices with 'active' status and in 'nasa' region.)
    # See: https://netboxlabs.com/docs/netbox/en/stable/reference/filtering/#filtering-objects
    query_string = ''
    if netbox_filter is not None and isinstance(netbox_filter, dict):
        for index, query_item in enumerate(netbox_filter):
            if isinstance(netbox_filter[query_item], list):
                for item in netbox_filter[query_item]:
                    query_string += (
                        f"{url_operator}{query_item}{'=' if netbox_filter[query_item][0:2] != '__' else ''}{item}")
                    url_operator = '&'
            else:
                if isinstance(netbox_filter[query_item], str):
                    query_string += (
                        f"{url_operator}{query_item}{'=' if netbox_filter[query_item][0:2] != '__' else ''}"
                        f"{netbox_filter[query_item]}")
                elif isinstance(netbox_filter[query_item], bool):
                    query_string += f"{url_operator}{query_item}={netbox_filter[query_item]}"
                url_operator = '&'

    # The 'limit_string' variable contains the maximum number of records to return. This is the total number of
    #   records to return. This is not to be confused with netbox_page_size, which limites the number of entries
    #   returned per API call.
    limit_string = f"{url_operator}limit={netbox_page_size}"
    url_operator = '&'

    # The 'ordering_string' variable contains the field names and sort direction to be applied to the data returned
    #   by Netbox. (e.g.: 'api/dcim/devices/?limit=20&status=active&region=nasa&ordering=-id' which sorts the Netbox
    #   results in descending netbox id order.
    # See: https://netboxlabs.com/docs/netbox/en/stable/reference/filtering/#ordering-objects
    ordering_string = ''
    if ordering is not None:
        ordering_string = f'{url_operator}ordering='
        for item in ordering:
            ordering_string += f"{item},"
        ordering_string = ordering_string[:-1]

    url = f"{base_query}{ordering_string}{query_string}{limit_string}"

    # Get info via API:
    if set_key is not None:
        result = {}
    else:
        result = []
    all_done = False

    filtered_count = 0
    total_count = 0
    new_field_list = []

    while not all_done:
        try:
            output = split_string_by_char(string=f"Fetching {url}...", max_length=100, seperators=['&', '&2C'])
            for index, line in enumerate(output):
                logger.debug(('' if index == 0 else '  ') + line)
            response = nbs.get(url).json()
        except Exception as err:
            return False, f"Unable to execute '{url}' due to error: '{err}'."
        else:
            if 'results' not in response:
                return False, format(response)

            if 'count' in response:
                total_count = response['count']

            url = response['next']
            for index, item in enumerate(response['results']):

                # Convert to dotted notation:
                processed_item = convert_to_dotted_notation(item, hide_custom_fields=False)

                # If we need to merge (enrich) data:
                if merge_data:
                    if isinstance(merge_data, dict):
                        merge_data = [merge_data]
                    for merge_data_item in merge_data:
                        if merge_data_item["key"] in processed_item:
                            for merge_item in merge_data_item['data'][processed_item[merge_data_item["key"]]]:
                                if f"{merge_data_item["key"].rsplit('.', 1)[0]}.{merge_item}" not in processed_item:
                                    processed_item[f"{merge_data_item["key"].rsplit('.', 1)[0]}.{merge_item}"] = (
                                        merge_data_item['data'][processed_item[merge_data_item["key"]]][merge_item])

                # Check for post_processing (further filtering of items):
                if post_processing is not None:

                    # If there is post processing, check if the item passes all the criteria. Skip the item if not.
                    if filter_result(post_filter=post_processing, data=processed_item, logger=logger):
                        filtered_count += 1
                        continue

                # Work out which fields to use and also substitute field names with configurable ones (if enabled).
                if show_fields is not None:
                    temp_dict = {}
                    for field in show_fields:
                        if ':' in field:
                            tmp = re.search(r"^(.*?)(:(.*?))?(:(.*?))?$", field)
                            if tmp:
                                field, name, metric = tmp.group(1), tmp.group(3), tmp.group(5)
                                if index == 0:
                                    if tmp.group(3) is not None:
                                        new_field_list.append(tmp.group(3))
                                    elif tmp.group(1) is not None:
                                        new_field_list.append(tmp.group(1))
                                if field in processed_item:
                                    if metric is None:
                                        temp_dict[name] = processed_item[field]
                                    else:
                                        if metric.lower() == 'addr':
                                            temp_dict[name] = processed_item[field].split('/')[0]
                                        elif metric.lower() == 'cidr':
                                            temp_dict[name] = int(processed_item[field].split('/')[1])
                                        elif metric.lower() == 'int':
                                            try:
                                                temp_dict[name] = int(processed_item[field])
                                            except ValueError:
                                                temp_dict[name] = processed_item[field]
                                            except TypeError:
                                                temp_dict[name] = None
                                        elif metric.lower() == 'float':
                                            try:
                                                temp_dict[name] = float(processed_item[field])
                                            except ValueError:
                                                temp_dict[name] = processed_item[field]
                                            except TypeError:
                                                temp_dict[name] = None
                                        elif metric.lower() == 'str':
                                            temp_dict[name] = str(processed_item[field])
                                        else:
                                            temp_dict[name] = processed_item[field]
                                    if set_key is not None:
                                        if field == set_key:
                                            set_key = set_key
                                else:
                                    temp_dict[name] = None
                        else:
                            temp_dict[field] = processed_item[field]
                            new_field_list.append(field)

                    processed_item = temp_dict.copy()

                else:
                    for field in processed_item:
                        if field not in new_field_list:
                            new_field_list.append(field)

                # If 'set_key' is specified, change output to a dict of dicts with the key set to 'set_key':
                if set_key is not None:
                    if set_key in processed_item:
                        result[processed_item[set_key]] = processed_item
                    else:
                        return False, f"The property '{set_key}' is not valid for '{query_type}' query type."
                else:
                    result.append(processed_item)

                # Check if we have requested a limited number of records/items:
                if limit is not None:
                    if len(result) >= limit:
                        all_done = True
                        break

            if url is None:

                all_done = True

    logger.debug(
        f"    returned: {len(result)}"
        f"{f" out of {total_count} records" if total_count != len(result) else ' records'}"
        f"{f" (filtered {filtered_count})." if filtered_count > 0 else '.'}")

    return True, (result, new_field_list)


def filter_result(post_filter: dict, data: dict, logger: logging.Logger = None):

    skip = False
    for item in post_filter:
        if item not in data:
            continue

        found_value = data[item]
        operator = post_filter[item]['operator']
        filter_value = post_filter[item]['value']

        if found_value:
            if operator in ['>', '<', '>=', '<=']:
                if not isinstance(filter_value, int | str):
                    return False, (
                        f"CONFIGURATION: Cannot use type '{type(filter_value).__name__}' ({filter_value})"
                        f" when using the '{operator}' operator, use a string or number instead.")
            if operator in ['=', '!=']:   # Equal to or not equal to
                if isinstance(filter_value, list):
                    if operator == '=':
                        if found_value not in filter_value:
                            skip = True
                    elif operator == '!=':
                        if found_value in filter_value:
                            skip = True
                elif isinstance(filter_value, str | int):
                    if operator == '=':
                        if found_value != filter_value:
                            skip = True
                    elif operator == '!=':
                        if found_value == filter_value:
                            skip = True
            elif operator == '>':        # Greater than
                if isinstance(found_value, str | int):
                    if int(found_value) <= int(filter_value):
                        skip = True
            elif operator == '<':        # Less than
                if int(found_value) >= int(filter_value):
                    skip = True
            elif operator == '>=':       # Greater than or equal to
                if int(found_value) < int(filter_value):
                    skip = True
            elif operator == '<=':       # Less than or equal to
                if int(found_value) > int(filter_value):
                    skip = True
            elif operator == 're':       # Matches RegEx
                if not re.search(r'' + filter_value, found_value):
                    skip = True
            elif operator == '!re':      # Does not match RegEx
                if re.search(r'' + filter_value, found_value):
                    skip = True

        if skip:
            if operator not in ['re', 'nre']:
                logger.debug(
                    f"    Removing '{data['id']}' ({item} = "
                    f"{'\'' + found_value + '\'' if isinstance(found_value, str) else found_value})")
            else:
                logger.debug(
                    f"    Removing '{data['id']}' ({item} "
                    f"{'does not match' if operator == 're' else 'matches'} RegEx '{filter_value}')")
            break
    if skip:
        return True

    return False


def get_via_pynetbox(

        query_type: str = None, netbox_filter: dict = None, ordering: list = None,
        netbox_url: str = None, netbox_token: str = None, logger: logging.Logger = None):

    """
        Get inventory from Netbox using pynetbox

        :param query_type: API endpoint name (for full list see 'query_type_to_endpoint_url' function,
        :param netbox_filter: Netbox filter e.g.: {'status': 'active', 'manufacturer': 'cisco'},
        :param ordering: Netbox order string used to sort fields e.g.: ['site', 'name'],
        :param limit: Maximum number of records to return,
        :param netbox_url: Netbox URL. This can be used when 'NETBOX_URL' environment variable is not set.
        :param netbox_token: Netbox Token. This can be used when 'NETBOX_TOKEN' environment variable is not set.
        :param netbox_page_size: Number of records to return per page during API calls
        :param logger: Logger instance

    """

    success, configuration = parse_configuration(configuration='./api/lib/netbox/cfg/config.json')
    if not success:
        logger.critical(f"Unable to open main configuration file '{configuration}'")
        return false, configuration

    if netbox_url is None or netbox_url.lower() == 'prod':
        netbox_url = configuration['apis']['netbox_prod']['url']
    elif netbox_url.lower() == 'dev':
        netbox_url = configuration['apis']['netbox_dev']['url']
    if netbox_url[-1] == '/':  # Remove trailing '/' from base url (if one exists).
        netbox_url = netbox_url[:-1]

    if netbox_token is None:
        netbox_token = get_key(configuration['apis']['netbox_prod']['token'])

    # Check if filter has been defined in the API configuration under 'netbox -> filters':
    description = None
    if netbox_filter is not None:
        if isinstance(netbox_filter, str):
            if netbox_filter in configuration['filters']:
                filter_name = netbox_filter
                if 'query_type' in configuration['filters'][filter_name]:
                    query_type = configuration['filters'][filter_name]['query_type']
                if 'netbox_filter' in configuration['filters'][filter_name]:
                    netbox_filter = configuration['filters'][filter_name]['netbox_filter']
                if 'ordering' in configuration['filters'][filter_name]:
                    ordering = configuration['filters'][filter_name]['ordering']
                if 'description' in configuration['filters'][filter_name]:
                    description = configuration['filters'][filter_name]['description']

    # verify that the API endpoint is valid:
    if query_type in endpoints['endpoints']:
        url = endpoints['endpoints'][query_type]
    else:
        return False, f"The API endpoint '{query_type}' is not valid."

    # Perform API call using pynetbox:
    nb = pynetbox.api(netbox_url, netbox_token if netbox_token is not None else get_key(
        configuration['apis']['netbox_prod']['token']))

    nb.http_session = requests.session()
    nb.http_session.verify = False

    if netbox_filter is None:
        netbox_filter = {}

    if not description:
        logger.info('Obtaining information from Netbox...')
    else:
        logger.info(f"Obtaining {description}..")

    if not url.startswith('/api/'):
        logger.critical(f"URL '{url}' does not start with '/api/'.")
    api_endpoints = url[1:-1].split('/')[1:-1]

    nb_obj = nb
    for api_endpoint in api_endpoints:
        if hasattr(nb, api_endpoint):
            nb_obj = getattr(nb_obj, api_endpoint.replace('-', '_'))
        else:
            return False, f'API endpoint "{api_endpoint}" is not available.'
    try:
        requests.packages.urllib3.disable_warnings()
        # Check what type of value the endpoint refers to:
        result = getattr(nb_obj, query_type)
        if isinstance(result, pynetbox.core.endpoint.Endpoint):
            # Only process when type is an Endpoint
            result = getattr(nb_obj, query_type).filter(**netbox_filter)
        else:
            return False, f"API endpoint '{query_type}' is not valid. (Type: '{type(result).__name__}')."
    except Exception as err:
        return False, f"Netbox Error: '{err}'"
    else:
        return True, result


def convert_to_dotted_notation(data, hide_custom_fields=False):

    """
        Convert data from netbox API call into dictionary containing key/value pairs. Dictionary is one level deep,
          with deeper levels converted to 'dotted' format. e.g.: {'site': {'name': 'London', 'id': 10}} will be
          converted to {'site.name': 'London', 'site.id': 10}.

    :param hide_custom_fields: Remove the prefixed 'custom_fields.' from any custom fields.
    :param data: List of dictionaries containing data returned from Netbox API call,
    :return: dictionary containing 'converted' data
    """

    # Note: This function only walks through a dictionary's top 5 levels. Anything deeper just returns the dictionary
    #   in text form (pprint's pformat funtion).
    # Note: Any top level property containing a list, e.g.: tags, will have a list propery added (tags.list) with
    #   a list of items
    # Note: Any key with a .url will have the 'url_api' key set to the URL value. Another key 'url' will be added
    #   without the '/api' component, so it links to the page in Netbox instead of the API url. e.g.:
    #      device_type.manufacturer.url: https://netbox.company.com/dcim/manufacturers/2/,
    #      device_type.manufacturer.url_api: https://netbox.company.com/api/dcim/manufacturers/2/,
    # Note: An additional field 'tag_list' is created when there is a 'tag' attribute. This allows easy access to
    #         the list of tags.
    ignore_fields = ['config_context']  # Don't traverse into dictionaries when these keys are found.
    nb_dict = {}

    # Traverse through netbox object and convert to dictionary.
    for field in data:
        if isinstance(field, tuple):
            current_key = field[0]
            value = field[1]
        else:
            current_key = field
            if field == 'tags':
                if isinstance(data[field], list):
                    if len(data[field]) == 0:
                        value = None
                        nb_dict['tag_list'] = []
                    else:
                        tag_list = []
                        for item in data[field]:
                            if 'display' in item:
                                tag_list.append(item['display'])
                        nb_dict['tag_list'] = tag_list if len(tag_list) > 0 else []

            value = data[field]
        if current_key in ignore_fields:
            continue
        elif value is None:
            nb_dict[current_key] = None
        elif isinstance(value, list):
            if len(value) > 0:
                nb_dict[current_key] = value
                field_name = None
                for field_index, sub_item in enumerate(value):
                    if field_index == 0:
                        if 'display' in sub_item:
                            field_name = 'display'
                        elif 'name' in sub_item:
                            field_name = 'name'
                        elif 'slug' in sub_item:
                            field_name = 'slug'
                        if field_name is not None:
                            nb_dict[f"{current_key}.list"] = ''
                    if field_name is not None:
                        nb_dict[f"{current_key}.list"] += f"{sub_item[field_name]}"
                        if field_index + 1 < len(value):
                            nb_dict[f"{current_key}.list"] += '\n'
            else:
                nb_dict[current_key] = None
        elif isinstance(value, dict | list):
            for field_2 in value:
                value_2 = value[field_2]
                current_key_2 = f"{current_key}.{field_2}"
                if hide_custom_fields:
                    if current_key == 'custom_fields':
                        current_key_2 = field_2
                if value_2 is None:
                    nb_dict[current_key_2] = None
                if current_key_2 in ignore_fields:
                    continue
                elif isinstance(value_2, dict):
                    for field_3 in value_2:
                        value_3 = value_2[field_3]
                        current_key_3 = f"{current_key}.{field_2}.{field_3}"
                        if value_3 is None:
                            nb_dict[current_key_3] = None
                        if current_key_3 in ignore_fields:
                            continue
                        elif isinstance(value_3, dict):
                            for field_4 in value_3:
                                value_4 = value_3[field_4]
                                current_key_4 = f"{current_key}.{field_2}.{field_3},{field_4}"
                                if value_4 is None:
                                    nb_dict[current_key_4] = None
                                if current_key_4 in ignore_fields:
                                    continue
                                elif isinstance(value_4, dict):
                                    for field_5 in value_4:
                                        value_5 = value_4[field_5]
                                        current_key_5 = f"{current_key}.{field_2}.{field_3},{field_4},{field_5}"
                                        if value_5 is None:
                                            nb_dict[current_key_5] = None
                                        if current_key_5 in ignore_fields:
                                            continue
                                        elif isinstance(value_5, dict):
                                            nb_dict[current_key_5] = pformat(value_5)
                                        else:
                                            nb_dict[current_key_5] = value_5
                                else:
                                    nb_dict[current_key_4] = value_4
                        else:
                            nb_dict[current_key_3] = value_3
                else:
                    nb_dict[current_key_2] = value_2
        else:
            nb_dict[current_key] = value

    return nb_dict
