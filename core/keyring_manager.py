import sys
import keyring

from core.logger import logger


def get_key(keywrds):

    """
        Get Credentials: Obtain value for specific keys in the keyring. Returns true if found, or false if not.

        Note: On Windows systems, 'Internet or network address' and 'User name' should both be populated with the
                key name, e.g.: NETBOX_URL. The 'Password' should store the secure info. (password, token, etc.)
              On Mac systems, 'Name', 'Account'  and 'Where' are populated with the key name, e.g.: NETBOX_URL.

              To execute this module, make sure you are in the project root ('starlight' directory) and
                run 'python -m core.keyring_manager <ACTION> <KEY>'

        TODO: Test on Windows and Linux systems. Windows systems might have length limit for the 'value'

    """

    # Examples:
    
    # (starlight) user@hostname:starlight python -m core.keyring_manager get SSH_USERNAME
    # Value for key 'SSH_USERNAME' is 'username'.
    # (starlight) user@hostname:starlight python -m core.keyring_manager set SSH_RANDOM_KEY NOT_SO_RANDOM_VALUE
    # Value for key 'SSH_RANDOM_KEY' set.
    # (starlight) user@hostname:starlight python -m core.keyring_manager del SSH_RANDOM_KEY
    # Key 'SSH_RANDOM_KEY' deleted.
    # (starlight) user@hostname:starlight

    global checked_keyring_items

    if isinstance(keywrds, str):
        keywrds = [keywrds]

    if isinstance(keywrds, list):

        for keywrd in keywrds:

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
                            if keywrd not in checked_keyring_items:
                                checked_keyring_items.append(keywrd)
                                logger.debug(f"Found '{keywrd}' in keyring.")
                            return build_pw
                        else:
                            logger.warning(f"Unable to find '{keywrd}' in keyring.")
                            return False

            else:
                if keywrd not in checked_keyring_items:
                    checked_keyring_items.append(keywrd)
                    logger.debug(f"Found '{keywrd}' in keyring.")
                return pw

    return False


def set_key(key_name, key_value):

    """
        Set Credentials: Obtain value for specific key in the keyring.
    """

    try:
        if isinstance(key_name, str):
            keyring.set_password(key_name.upper().strip(), key_name.upper().strip(), str(key_value))
            logger.info(f"Set '{key_name}' key in keyring.")
            return True
        else:
            logger.warning(f"Error setting '{key_name}' key.")
            return False
    except (keyring.errors.KeyringError, keyring.errors.PasswordSetError) as e:
        logger.critical(f"Error setting '{key_name}' key.")
        return False


def del_key(key_name):
    """
        Delete Credentials: Remove key from the keyring.
    """
    if isinstance(key_name, str):
        try:
            keyring.delete_password(key_name.upper().strip(), key_name.upper().strip())
            logger.info(f"Deleted '{key_name}' key from keyring.")
            if key_name in checked_keyring_items:
                checked_keyring_items.remove(key_name)
            return True
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"Key '{key_name}' not found in keyring.")
    else:
        return False


def main():

    # SET - Set key to value
    if len(sys.argv) == 4:
        if sys.argv[1].lower() == 'set':
            result = set_key(sys.argv[2], sys.argv[3])
            if result:
                sys.stdout.write(f"Value for key '{sys.argv[2]}' set.\n")
                sys.exit(0)
            else:
                sys.stdout.write(f"Unable to set '{sys.argv[2]}'.\n")
                sys.exit(1)

    # DEL - Remove a key
    elif len(sys.argv) == 3:
        if sys.argv[1].lower() == 'del':
            result = del_key(sys.argv[2])
            if result:
                sys.stdout.write(f"Key '{sys.argv[2]}' deleted.\n")
                sys.exit(0)
            else:
                sys.stdout.write(f"Key '{sys.argv[2]}' was not found.\n")
                sys.exit(1)

        # GET - Get key value
        elif sys.argv[1].lower() == 'get':
            value = get_key(sys.argv[2])
            if value:
                sys.stdout.write(f"Value for key '{sys.argv[2]}' is '{value}'.\n")
                sys.exit(0)
            else:
                sys.stdout.write(f"Key '{sys.argv[2]}' was not found.\n")
                sys.exit(1)
        else:
            help_msg = True

    # Display 'Help' message
    sys.stdout.write(
        f"\n  Keyring Manager:\n\n    Usage: 'python -m keyring_manager.py (del|get|set) args.\n\n"
        f"        del <keyring name>\n"
        f"        get <keyring name>\n"
        f"        set <keyring name> <value>\n\n"
        f"  NOTE: Remember to source your python environment, and execute the above command from the 'starlight'"
        f" root.\n        For troubleshooting, see 'logs/starlight.log'.\n\n"
    )
    sys.exit(1)


checked_keyring_items = []  # Used to only log finding specific keys once.


if __name__ == "__main__":
    main()
