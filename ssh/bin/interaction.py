import time
from core.logger import logger
from ssh.bin.session import SSHSession, SessionManager
import threading
from pprint import pprint

def interaction(tasks):

    global jump_hosts

    threader = None
    max_direct_sessions= 10
    dsm = SessionManager(max_sessions=max_direct_sessions)  # Direct session manager

    for task_id, task in enumerate(tasks):

        jump_host = task.get('connect_via', None)

        if jump_host is not None:

            task['error'] = None
            if jump_host.get('host', None) is None:
                task['error'] = 'No host specified'
            if jump_host.get('authentication', None) is None:
                task['error'] = 'No authentication credentials specified'

            if task['error'] is None:

                del task['error']
                # Check if jump-host is already registered in the jump_hosts list, and if not - register it:
                if jump_host['host'] not in jump_hosts:
                    jump_host['is_jump_host'] = True
                    jump_hosts[jump_host['host']] = jump_host.copy()
                    threader = threading.Thread(target=ssh_worker, args=(jump_host,))
                    threader.daemon = True
                    threader.start()

                # Add task (without the jump-host information) to queue:
                jh_task = task
                jh_task['task_id'] = task_id + 1
                del jh_task['connect_via']
                jump_hosts[jump_host['host']]['session'].session_manager.queue.append(jh_task)

        else:

            session_id = dsm.get_next_available_session(session_id=task['task_id'])
            if session_id > 0:
                threader = threading.Thread(target=ssh_worker, args=(task,))
                threader.daemon = True
                threader.start()

    while True:

        for jh in jump_hosts:
            if isinstance(jump_hosts[jh], SSHSession):
                # print(f"{jump_hosts[jh].host}: {jump_hosts[jh].status} {jump_hosts[jh].session_manager.current_sessions}/{jump_hosts[jh].session_manager.max_sessions}")

                if jump_hosts[jh].session_manager.current_sessions < jump_hosts[jh].session_manager.max_sessions:

                    if len(jump_hosts[jh].session_manager.queue) > 0:
                        task = jump_hosts[jh].session_manager.queue.pop(0)
                        session_id = jump_hosts[jh].session_manager.get_next_available_session(session_id=task['task_id'])

                        if session_id > 0:
                            threader = threading.Thread(target=ssh_worker, args=(task,))
                            threader.daemon = True
                            threader.start()

        # Check if everything is done:

        # tasks_left = 0
        # for jh in jump_hosts:
        #     if isinstance(jump_hosts[jh], SSHSession):
        #         print(len(jump_hosts[jh].session_manager.queue))
        #         if len(jump_hosts[jh].session_manager.queue) > 0:
        #             tasks_left += len(jump_hosts[jh].session_manager.queue)
        #         else:
        #             jump_hosts[jh].disconnect()
        #
        # if tasks_left == 0:
        #     break

        time.sleep(0.01)

    exit()


def ssh_worker(session):

    global jump_hosts

    #  Determine if this is a jump-host
    is_jump_host = False
    if session.get('host') in jump_hosts:
        is_jump_host = True

    s = SSHSession(**session)
    if is_jump_host:
        jump_hosts[s.host]['session'] = s

    s.connect()

    if s.status == 'connected':

        # If this is a jump-host session and it's status is 'connected', we can use it to connect to other hosts:
        if is_jump_host:
            jump_hosts[s.host] = s  # Register that the jump-host is now 'connected'
            return

        # Normal hosts:
        if s.ssh_error is None:
            for command in s.command_list:
                if s.ssh_error is None:  # Check for errors. If error is not found, execute command
                    result = s.send_command(command)
            s.disconnect()

    if s.ssh_error is None and s.status == 'connected':
        pass

    for jh in jump_hosts:
        if isinstance(jump_hosts[jh], SSHSession):

            for session in jump_hosts[jh].session_manager.sessions:
                if jump_hosts[jh].session_manager.sessions[session].get('id') == s.task_id:
                    jump_hosts[jh].session_manager.sessions[session] = {
                        'activity': None, 'id': None, 'status': 'idle'}
                    jump_hosts[jh].session_manager.current_sessions -= 1

jump_hosts = {}  # List of active jump-hosts.


