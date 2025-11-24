import os
import sys
import sqlite3
import logging
import re
import json


from ssh.lib.analysis.utilities import get_key
from ssh.bin.interakt import parse_configuration, tasks
from pprint import pprint


def inventory(nb_filter=None):

    """

        Netbox Devices (netbox_devices.py)

    :return: inventory (dict)
    """

    # Version: 1.0 - Initial version
    # Description: Netbox Inventory
    # Inventory: Netbox Devices

    # Find any existing record where the IP address matches:
    # sql_query = f"SELECT error, job_info FROM devices WHERE result != 'Success'"
    # successful, search_result = sql(sql_query)
    #
    # csv = "'Name', 'IP', 'Role', 'Type', 'Manufacturer', 'Platform', 'Region', 'Error'\n"
    # for item in search_result:
    #     i = json.loads(item[1])
    #     csv += f"'{i['parameters']['netbox_device_name']}',"
    #     csv += f"'{i['host']}',"
    #     csv += f"'{i['parameters']['netbox_device_role']}',"
    #     csv += f"'{i['parameters']['netbox_device_type']}',"
    #     csv += f"'{i['parameters']['netbox_manufacturer']}',"
    #     csv += f"'{i['parameters']['netbox_platform']}',"
    #     csv += f"'{i['parameters']['netbox_region']}',"
    #     csv += f"'{item[0]}'\n"
    #
    # with open('ssh_issues.csv', 'w') as csvfile:
    #     csvfile.writelines(csv)
    #
    # exit()

    sql_query = f"SELECT job_info FROM devices WHERE result != 'Success'"
    successful, search_result = sql(sql_query)

    failed_inventory = []

    if successful:
        for task_item in search_result:
            item = json.loads(task_item[0])

            task = {
                # 'authentication': item['authentication'],
                'authentication': ['devices'],
                'command_list': item['command_list'],
                'host': item['host'],
                # 'jump_hosts': item['jump_host_filter'],
                'jump_hosts': {"region": item["parameters"]["netbox_region"].lower()},
                'os_type': item['os_type'],
                'parameters': item['parameters'],
                'policy': item['policy'],
                'type': 'ssh'}

            failed_inventory.append(task)

    return True, failed_inventory


def sql(query, data=None):

    global ssh_configuration

    # Only process database calls if configuration includes database info:
    if 'database' in ssh_configuration:
        if 'file' in ssh_configuration['database']:
            try:
                db = sqlite3.connect(database=ssh_configuration['database']['file'])
                c = db.cursor()

            except sqlite3.Error as err:

                logger.critical(
                    "Error while trying to connect to Database, Error '%s'.", err)
                sys.exit(1)

            sql_con_error = False

            # Work out if data was sent along with the query or not:
            if data is None:

                # No data was sent with query:
                try:
                    c.execute(query)
                    db.commit()
                except Exception as db_err:
                    sql_con_error = db_err

            else:

                if isinstance(data, list):

                    # Data contains a list so requires an 'executemany' statement:
                    try:
                        c.executemany(query, data)
                        db.commit()
                    except Exception as db_err:
                        sql_con_error = db_err

                else:

                    # Single execute data was sent along with the query:
                    try:
                        c.execute(query, data)
                        db.commit()
                    except Exception as db_err:
                        sql_con_error = db_err

            # Check for errors:
            if sql_con_error is not False:

                logger.critical('SQL ERROR:')
                logger.critical("QUERY:\n\n%s\n", query)
                if data is not None:
                    logger.critical("DATA:\n\n%s\n", data)
                    if isinstance(data, list) or isinstance(data, tuple):
                        for item in data:
                            logger.critical(" %s (%s)", item, type(item).__name__)
                logger.critical("ERROR:\n\n%s\n", sql_con_error)
                return False, sql_con_error

            else:

                output = []
                try:
                    output = c.fetchall()
                except sqlite3.Error as err:
                    logger.debug(f"Unable to execute SQL query, Error: '{err}'")
                else:
                    db.close()

                if len(output) > 0:
                    db.close()
                    return True, list(output)

                else:
                    db.close()
                    return True, []


# Start

# Set up logging:
logger = logging.getLogger('interakt')

# Get configuration from file:
ssh_configuration = parse_configuration(configuration="ssh/cfg/configuration.json")
