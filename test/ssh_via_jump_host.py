"""

    SSH via Jump Host - Example script to demostrate initiating a connection to a host via 'jump-host'.

"""

# Example log output:

# 18:12:26.139 Found 'JH_USERNAME' in keyring.
# 18:12:26.140 Found 'JH_PASSWORD' in keyring.
# 18:12:26.140 <JH_USERNAME>@1.1.1.1:22 (1): Attempting SSH connection...
# 18:12:26.539 <JH_USERNAME>@1.1.1.1:22 (1): Connection successfull. (0.40s)
# 18:12:26.539 <JH_USERNAME>@1.1.1.1:22 (1): Cipher: aes128-ctr, MAC: hmac-sha2-256, Version: SSH-2.0-OpenSSH_10.0, Compression: None
# 18:12:26.622 <JH_USERNAME>@1.1.1.1:22 (1): Found prompt '<JH_USERNAME>@starlight:~'.
# 18:12:26.625 Found 'SSH_USERNAME' in keyring.
# 18:12:26.627 Found 'SSH_PASSWORD' in keyring.
# 18:12:26.627 <JH_USERNAME>@1.1.1.1:22 (1): Session 1 allocated to '2.2.2.2:22022' (2)
# 18:12:26.627 <SSH_USERNAME>@2.2.2.2:22022 (2): Attempting SSH connection via '1.1.1.1:22'...
# 18:12:26.702 <SSH_USERNAME>@2.2.2.2:22022 (2): Connection successfull. (0.08s)
# 18:12:26.702 <SSH_USERNAME>@2.2.2.2:22022 (2): Cipher: aes128-ctr, MAC: hmac-sha2-256, Version: SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.13, Compression: None
# 18:12:26.784 <SSH_USERNAME>@2.2.2.2:22022 (2): Host appears to be a 'Linux' device! [Prompt]
# 18:12:26.796 <SSH_USERNAME>@2.2.2.2:22022 (2): Found prompt '<SSH_USERNAME>@interakt:~$ '.
# 18:12:26.796 <SSH_USERNAME>@2.2.2.2:22022 (2): Sending command 'date'...
# 18:12:26.809 <SSH_USERNAME>@2.2.2.2:22022 (2): Command 'date' completed. (0.01s)
# 18:12:26.822 <SSH_USERNAME>@2.2.2.2:22022 (2): Sending command 'cat /etc/os-release'...
# 18:12:26.835 <SSH_USERNAME>@2.2.2.2:22022 (2): Command 'cat /etc/os-release' completed. (0.01s)
# 18:12:26.848 <SSH_USERNAME>@2.2.2.2:22022 (2): SSH session disconnected.
# 18:12:26.848 <JH_USERNAME>@1.1.1.1:22 (1): Session 1 freed.
# 18:12:26.848 <JH_USERNAME>@1.1.1.1:22 (1): SSH session disconnected.

# Example output

# Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-79-generic x86_64)
# 
#  * Documentation:  https://help.ubuntu.com
#  * Management:     https://landscape.canonical.com
#  * Support:        https://ubuntu.com/pro
# 
# This system has been minimized by removing packages and content that are
# not required on a system that users do not log into.
# 
# To restore this content, you can run the 'unminimize' command.
# Last login: Sun Oct 26 18:43:46 2025 from 192.168.10.51
# <SSH_USERNAME>@<HOSTNAME>:~$ date
# Sun Oct 26 18:43:53 GMT 2025
# <SSH_USERNAME>@<HOSTNAME>:~$ cat /etc/os-release
# PRETTY_NAME="Ubuntu 24.04.3 LTS"
# NAME="Ubuntu"
# VERSION_ID="24.04"
# VERSION="24.04.3 LTS (Noble Numbat)"
# VERSION_CODENAME=noble
# ID=ubuntu
# ID_LIKE=debian
# HOME_URL="https://www.ubuntu.com/"
# SUPPORT_URL="https://help.ubuntu.com/"
# BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
# PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
# UBUNTU_CODENAME=noble
# LOGO=ubuntu-logo
# <SSH_USERNAME>@<HOSTNAME>:~$

import sys
from core.keyring_manager import get_key
from ssh.bin.session import SSHSession

# Initialize session to 'jump-host':
jump_host = SSHSession(
    host='1.1.1.1',                                       # Replace with your own jump-host IP or resolvable DNS name
    authentication=[
        {
            'username': get_key('JH_USERNAME'),           # Jump host login Username
            'password': get_key('JH_PASSWORD'),           # Jump host login Password
            'sudo_command': 'sudo bash',                  # Execute 'sudo bash' command after login, (root priviledges)
        }
    ]
)

# Try to connect:
jump_host.connect()                                       # Perform connection to remote host

if jump_host.status == 'connected':

    # Connect to host.
    try:
        ssh = SSHSession(
            host='2.2.2.2',                               # Replace with your own remote-host IP or resolvable DNS name
            authentication=[
                {
                    'username': get_key('SSH_USERNAME'),  # Host login username
                    'password': get_key('SSH_PASSWORD'),  # Host login password
                    'sudo_command': 'sudo bash'           # Get 'root' privledges (if needed)
                }
            ],
            port=22022,                                   # SSH port number (defaults to 22)
            connect_via=jump_host                         # The SSHSession object of the jump-host
        )
        ssh.connect()                                     # Perform connection to remote host
    except ValueError as err:
        print(f"Unable to connect to host, Error: '{err}'")
        sys.exit(1)
    else:
        command_list = ['date', 'cat /etc/os-release']    # List of commands to run on remote host (in order)
        if ssh.status == 'connected':                     # Ensure device is still connected before issuing commands
            for command in command_list:                  # Iterate through commands, one by one
                if ssh.ssh_error is None:                 # Check for errors. If error is not found, execute command
                    result = ssh.send_command(command)

        ssh.disconnect()                                  # Disconnect from the remote host
        jump_host.disconnect()                            # Disconnect from the jump-host
        print(ssh.history)                                # View ssh object properties of remote host
        sys.exit(0)                                       # Exit

else:
    print(f"Unable to connect to {jump_host.host}:{jump_host.port}, Error: '{jump_host.ssh_error}'")
    sys.exit(1)
