"""

    SSH directly to a host - Example script to demostrate initiating a connection to a host.

"""

# Example log output:

# 18:12:26.140 <SSH_USERNAME>@1.1.1.1:22022 (1): Attempting SSH connection...
# 18:12:26.539 <SSH_USERNAME>@1.1.1.1:22022 (1): Connection successfull. (0.40s)
# 18:12:26.539 <SSH_USERNAME>@1.1.1.1:22022 (1): Cipher: aes128-ctr, MAC: hmac-sha2-256, Version: SSH-2.0-OpenSSH_10.0, Compression: None
# 18:12:26.622 <SSH_USERNAME>@1.1.1.1:22022 (1): Found prompt '<SSH_USERNAME>@<HOSTNAME>:~'.
# 18:12:26.796 <SSH_USERNAME>@1.1.1.1:22022 (1): Sending command 'date'...
# 18:12:26.809 <SSH_USERNAME>@1.1.1.1:22022 (1): Command 'date' completed. (0.01s)
# 18:12:26.822 <SSH_USERNAME>@1.1.1.1:22022 (1): Sending command 'cat /etc/os-release'...
# 18:12:26.835 <SSH_USERNAME>@1.1.1.1:22022 (1): Command 'cat /etc/os-release' completed. (0.01s)
# 18:12:26.848 <SSH_USERNAME>@1.1.1.1:22022 (1): SSH session disconnected.

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
# Last login: Sun Oct 26 18:43:46 2025 from 10.10.10.10
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


# Initialize session to host:
host = SSHSession(
    host='1.1.1.1',  # Replace with your host IP or resolvable DNS name
    authentication=[
        {
            'username': get_key('JH_USERNAME'),           # Host login Username
            'password': get_key('JH_PASSWORD'),           # Host login Password
            'sudo_command': 'sudo bash',                  # Execute 'sudo bash' command after login, (root priviledges)
        }
    ]
)

# Try to connect:
host.connect()  # Perform connection to host

if host.status == 'connected':

    command_list = ['date', 'cat /etc/os-release']        # List of commands to run on host (in order)
    if host.status == 'connected':                        # Ensure device is still connected before issuing commands
        for command in command_list:                      # Iterate through commands, one by one
            if host.ssh_error is None:                    # Check for errors. If error is not found, execute command
                result = host.send_command(command)

    host.disconnect()                                     # Disconnect from the host
    print(host.history)                                   # View ssh object properties of host
    sys.exit(0)                                           # Exit
