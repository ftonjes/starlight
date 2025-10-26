import os
import keyring

import ssh.bin.logger as logger


def get_creds(keywrds):

    """
        Get Credentials: First check keyring to find credential information. If it is not found, then check if the
                           environment variable exists and use that. If neither are found, return False.

        Note: On Windows systems, 'Internet or network address' and 'User name' should both be populated with the
                key name, e.g.: NETBOX_URL. The 'Password' should store the secure info. (password, token, etc.)
    """

    if isinstance(keywrds, str):
        keywrds = [keywrds]

    if isinstance(keywrds, list):

        for keywrd in keywrds:

            if keywrd in os.environ:
                logger.debug(f"'{keywrd}' environment variable already set.")
                continue

            pw = keyring.get_password(keywrd, keywrd)
            if pw is None:
                build_pw = ''

                # We support long strings using keys with keyname_<set_number>, e.g. tokens
                for n in range(1, 999):
                    keywrd_id = f"{keywrd}_{str(n)}"
                    pw = keyring.get_password(keywrd_id, keywrd_id)
                    if pw is not None:
                        build_pw += pw
                    else:
                        if build_pw != '':
                            logger.info(f"Set '{keywrd}' environment variable.")
                            os.environ[keywrd] = build_pw
                        else:
                            logger.critical(f"Error setting '{keywrd}' environment variable.")
                            return False

            else:
                logger.info(f"Set '{keywrd}' environment variable.")
                os.environ[keywrd] = pw

        return True

    logger.critical("Error: 'keywrds' parameter should contain either a single string or list of strings.")
    return False
