import os
import sys
from ssh.bin.session import SSHSession

# Initialize session to 'jump-host':
jump_host = SSHSession(
    host='1.1.1.1',
    authentication=[
        {
            'username': os.environ['JH_USERNAME'],
            'password': os.environ['JH_PASSWORD'],
            'sudo_command': 'sudo bash'
        }
    ],
    port=22
)

# Try to connect:
jump_host.connect()

if jump_host.status == 'connected':

    # Connect to host
    try:
        ssh = SSHSession(
            host='2.2.2.2',
            authentication=[
                {
                    'username': os.environ['SSH_USERNAME'],
                    'password': os.environ['SSH_PASSWORD'],
                    'sudo_command': 'sudo bash'
                }
            ],
            port=22022,
            connect_via=jump_host
        )
        ssh.connect()
    except ValueError as err:
        print(f"Unable to connect to host, Error: '{err}'")
        sys.exit(1)
    else:
        command_list = ['date', 'ifconfig -a', 'cat /etc/os-release']
        if ssh.status == 'connected':
            for command in command_list:
                if ssh.ssh_error is None:
                    result = ssh.send_command(command)

        ssh.disconnect()        # Disconnect from the host
        jump_host.disconnect()  # Disconnect from the jump-host
        print(ssh.__dict__)     # View ssh object properties
        sys.exit(0)

else:
    print(f"Unable to connect to {jump_host.host}:{jump_host.port}, Error: '{jump_host.ssh_error}'")
    sys.exit(1)
