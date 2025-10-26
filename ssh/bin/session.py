import pprint
import time
import itertools

from core.logger import logger
from ssh.bin.connect import connect
from ssh.bin.interaction import send_command
from ssh.bin.disconnect import disconnect
from pprint import pprint


class SSHSession:

    """
        SSHSession
    """

    session_id = itertools.count()
    next(session_id)                                   # Start session_id from 1 (not 0)

    def __init__(
            self,
            host: str,
            authentication: list | dict,
            port: int = 22,
            connection_timeout: int = 10,
            session_timeout: int = 180,
            retries: int = 2,
            retry_interval: int = 15,
            compression: bool = False,
            vendor: str = None,
            description: str = None,
            connect_via=None
    ):

        self.host = host                               # Name or IP address of host
        if isinstance(authentication, dict):
            self.authentication = [authentication]     # Single authentication profile (dict)
        else:
            self.authentication = authentication       # Multiple authentication profiles (list of dicts)
        self.port = port                               # SSH port
        self.connection_timeout = connection_timeout   # SSH Connection timeout
        self.session_object_timeout = session_timeout  # SSH session timeout
        self.retries = retries                         # Number of connection retries
        self.retry_interval = retry_interval           # Number of seconds between retries
        self.compression = compression                 # Use SSH compression
        self.vendor = vendor                           # Assume vendor
        self.keepalive_interval = 120                  # Send keepalive every n seconds
        self.description = description                 # Description of host used for logging
        self.session_id = next(SSHSession.session_id)  # Session ID
        self.session_object_start_time = None          # Time connection established
        self.session_object = None                     # Paramiko 'invoke_shell' session object
        self.status = None                             # Status
        self.session_object_interact_time = None       # Time of last comms to/from device
        self.session_object_closed_time = None         # Time session closed
        self.ssh_error = None                          # SSH Error
        self.raw = b''                                 # Raw SSH output
        self.prompt = ''                               # Current prompt info
        self.history = ''                              # Session history

        self.jump_host = connect_via                   # Connect via this SSHSession session (SSHSession object)

        # If we see connect_via, then we need to use the session manager to manage the connects via this host:
        if self.jump_host is not None:

            # Set up session manager for jump-host:
            if not hasattr(self.jump_host, 'session_manager'):
                connect_via.session_manager = SessionManager()

            jh_session_id = connect_via.session_manager.get_next_available_session(self.session_id)
            if jh_session_id > 0:
                logger.debug(
                    f"%s@%s:%s (%s): Session %s allocated to '%s:%s' (%s)", self.jump_host.username,
                    self.jump_host.host, self.jump_host.port, self.jump_host.session_id, jh_session_id, self.host,
                    self.port, self.session_id)
            else:
                self.ssh_error = f"Jump host '{self.jump_host.host}' has no sessions available."
                return

    def __repr__(self):
        return f"SSHSession_{self.host}:{self.port}"

    def connect(self):
        return connect(self)

    def send_command(self, command_list):
        return send_command(self, command_list)

    def disconnect(self):
        return disconnect(self)

    def send_keepalive(self):
        if not self.session_object.closed:
            if time.time() - self.session_object_start_time > self.keepalive_interval:
                self.session_object.send('')
                self.session_object_interact_time = time.time()


class SessionManager:

    def __init__(
            self,
            max_sessions: int = 10,                    # Maximum number of sessions
            connection_timeout: int = 30,              # Default connection timeout for connections via this host
            session_timeout: int = 180,                # Default session timeout for connections via this host
            retries: int = 2,                          # Default number of retries for connections via this host
            retry_interval: int = 15,                  # Default retry interval for connections via this host
            compression: bool = False,                 # Default compression for connections via this host
    ):

        self.defaults = {
            "connection_timeout": connection_timeout,
            "default_session_timeout": session_timeout,
            "default_retries": retries,
            "default_retry_interval": retry_interval,
            "default_compression": compression
        }
        self.current_sessions = 0
        self.max_sessions = max_sessions

        self.sessions = {}
        for session in range(max_sessions):
            self.sessions[session + 1] = {
                "id": None,
                "status": 'idle',
                "activity": None
            }

    def get_next_available_session(self, session_id: int):

        # Checks if there is an available session to connect via. Returns an available session id, or 0 if all are busy.
        if self.current_sessions < self.max_sessions:
            for index, session in enumerate(range(1, self.max_sessions)):
                if self.sessions[index + 1]['status'] == 'idle':
                    self.sessions[index + 1]['status'] = 'allocated'
                    self.sessions[index + 1]['activity'] = time.time()
                    self.sessions[index + 1]['id'] = session_id
                    self.current_sessions += 1
                    return index + 1

        return 0

    def find_session(self, session_id: int):
        for jh_session in self.sessions:
            if self.sessions[jh_session]['id'] == session_id:
                return jh_session
        return 0


    def free_session(self, session_id: int):
        jh_session_id = self.find_session(session_id)
        if jh_session_id > 0:
            self.sessions[jh_session_id]['status'] = 'idle'
            self.sessions[jh_session_id]['id'] = None
            self.sessions[jh_session_id]['activity'] = None
            self.current_sessions -= 1
            return jh_session_id
        return 0


def ssh_worker(task):

    """

        Worker that interacts with an SSH session to a host.

    :param task: dictionary containing task information
    :return:

    """

    # Set up SSHSession with connection info:
    task.ssh_session = SSHSession(
        host=task.host,
        port=task.ssh_port,
        compression=task.ssh_compression,
        authentication=task.authentication,
        session_timeout=task.ssh_session_timeout,
        retries=task.ssh_retries,
        retry_interval=task.ssh_retry_interval,
        jump_host=task.jump_host if hasattr(task, 'jump_host') else None,
        command_list=task.command_list.copy(),
        os_type=task.os_type if task.os_type is not None else None,
        vendor=task.vendor if task.vendor is not None else None,
        task_id=task.task_id,
        fail_on_first_error=task.fail_on_first_error)

    # For some reason the task.jump_host changes after the s.connect() function is called, which closes the wrong
    #   task when the worker is complete. For now we create a different variable (jh_task) to take note of the
    #   origional task.jump_host value. (might be threading-related)
    jh_task = None
    if hasattr(task, 'jump_host'):
        if task.jump_host is not None:
            jh_task = task.jump_host

    # Try to connect and catch any errors if there are any:
    s = task.ssh_session  # SSHSession object
    s.connect()

    if s.ssh_error is None and s.connect_success:

        # SSH connection successful:
        if hasattr(task, 'vendor'):
            if task.vendor is not None:
                s.vendor = task.vendor
                logger.debug("%s@%s:%s: Assuming device vendor is '%s'.", s.username, s.host, s.port, s.vendor)

        # Interact with the SSH session:
        s.interact()
        s.disconnect()

        host_session_duration = s.session_end_time - s.session_start_time
        task.status = 'complete'
        task.time_completed = time.time()

        if len(s.executed_commands) > 0:
            if len(s.successful_commands) > 0:
                if len(s.failed_commands) > 0:
                    logger.info(
                        "%s@%s:%s (%s): ✔️ SSH session successful, but one or more commands experienced issues."
                        " (active for %.2fs)",
                        s.username, s.host, s.port, s.task_id, host_session_duration)
                    s.session_success = True

                else:
                    logger.info(
                        "%s@%s:%s (%s): ✔️ SSH session successful. (active for %.2fs)",
                        s.username, s.host, s.port, s.task_id, host_session_duration)
                    s.session_success = True

                if s.vendor is None and s.os_type is None:
                    logger.warning(
                        "%s@%s:%s (%s): ⚠️Unknown device. Auto-detect was unable to work out the vendor or model of"
                        " the device. (active for %.2fs)", s.username, s.host, s.port, s.task_id, host_session_duration)

        elif len(s.executed_commands) == 0:
            if len(s.command_list) == 0:
                logger.info(
                    "%s@%s:%s (%s): ✔️ SSH session successful. (active for %.2fs)",
                    s.username, s.host, s.port, s.task_id, host_session_duration)
                s.session_success = True
            else:
                logger.warning(
                    "%s@%s:%s (%s): ✔️ SSH session successful, but no commands were executed. (active for %.2fs)",
                    s.username, s.host, s.port, s.task_id, host_session_duration)

    else:

        # Unsuccessful connection with no errors:
        task.status = 'failed'

        if len(s.ssh_error) == 0:
            s.ssh_error = 'Unknown error.'

        s.session_success = False
        task.time_failed = time.time()
        logger.info(
            "%s@%s:%s (%s): ❌ SSH session failed after %s, error: \"%s\".", s.username, s.host, s.port,
            s.task_id, f"{(time.time() - s.session_initialized):.2f}s", s.ssh_error)

    # Information obtaiened during session:
    tasks['queued'][task.task_id] = s.interaktion

    # Create dictionary containing additional info that might be needed later:
    field_list = ['authenticated_with', 'connect_success', 'executed_commands', 'failed_commands', 'parameters',
                  'found_prompt_time', 'host_name', 'interact_time', 'local_ip_v4_address', 'local_ip_v4_port',
                  'prompt', 'prompt_filter', 'session_end_time', 'session_initialized', 'session_start_time',
                  'session_success', 'ssh_login_messages', 'successful_commands', 'vendor', 'welcome_prompt', 'raw',
                  'resolved_name', 'ip_v4_address']

    for item in field_list:
        if hasattr(s, item):
            if '_session_info' not in tasks['queued'][task.task_id]:
                tasks['queued'][task.task_id]['_session_info'] = {}
            tasks['queued'][task.task_id]['_session_info'][item] = getattr(s, item)

    if s.resolved_name is not None:
        tasks['queued'][task.task_id]['_session_info']['resolved_name'] = s.resolved_name  # DNS name of host

    # Clean up task activity:
    if task.status in ['complete', 'failed']:
        if hasattr(task, 'jump_host'):
            for task_id in task.history:
                if task.history[task_id]['status'] == 'waiting':
                    task.history[task_id]['status'] = 'skipped'
        else:
            if task.history['status'] == 'waiting':
                task.history['status'] = 'skipped'

    logger.debug(
        "%s@%s:%s (%s): Task completed. (%s)", s.username, s.host, s.port, s.task_id,
        'Success' if s.session_success else 'Failed')

    task.success = True
    task.time_completed = time.time()
    if jh_task is not None:
        sessions[jh_task][task.queue_id]['status'] = 5 if task.status == 'complete' else 6
    else:
        sessions[0][task.queue_id]['status'] = 5 if task.status == 'complete' else 6