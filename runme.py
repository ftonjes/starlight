import os
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
        pass
    else:
        command_list = ['date', 'ifconfig -a', 'cat /etc/os-release']
        if ssh.status == 'connected':
            for command in command_list:
                if ssh.ssh_error is None:
                    result = ssh.send_command(command)

        ssh.disconnect()
        jump_host.disconnect()
        print(ssh.__dict__)  # View ssh object properties
