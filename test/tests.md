# Test scripts

To test these scripts, move them to the project root and execute them.

`NOTE`

* Some of the scripts rely on certain keys to be present in your keychain/credential manager. Check the logs located in 'starlight/logs' for any error messages.
* This example uses the 'keyring manager' module to store/retreive passwords from the local credential manager/keychain. You can use 'os.environ' if these values are stored in the environment, or update the code to retrieve credentials from 3rd party tools like HashiCorp Vault (hvac). 

## ssh_directly_to_host.py

* This script illustrates connecting to a single host.

## ssh_via_jump_host.py

* This script illustrates connecting to a single host via a 'jump-host'.
