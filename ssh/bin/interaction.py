from ssh.bin.session import SSHSession

def interaction(tasks):

    for task in tasks:

        task['error'] = None
        jump_host = task.get('jump_host', None)

        if jump_host.get('host', None) is None:
            task['error'] = 'No host specified'
        if jump_host.get('authentication', None) is None:
            task['error'] = 'No authentication credentials specified'

        if task['error'] is None:
            pass



jump_hosts = {}


