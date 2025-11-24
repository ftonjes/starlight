import pprint
import time
import itertools

from starlight.core.logger import logger
from .connect import connect
from .send import send_command
from .disconnect import disconnect
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
            connect_via=None,
            is_jump_host: bool = False,
            command_list: list = None,
            max_sessions: int = 10,
            task_id: int = None,
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
        self.task_id = task_id                         # The task_id (used to update session manager once task complete)

        if command_list is None:
            self.command_list = []
        elif isinstance(command_list, str):
            self.command_list = [command_list]
        elif isinstance(command_list, list):
            self.command_list = command_list
        else:
            raise TypeError("Command list must contain a single command, or list of commands.")

        if is_jump_host:

            # Set up session manager for jump-host:
            if not hasattr(self.jump_host, 'session_manager'):
                self.session_manager = SessionManager(max_sessions=max_sessions)

        # If we see connect_via, then we need to use the session manager to manage the connects via this host:
        # else:
        #
        #     # If connect_via is a dict, we need to connect to the jump-host before we can initiate the session to the
        #     #   remote host:
        #
        #     jh_session_id = connect_via.session_manager.get_next_available_session(self.session_id)
        #     if jh_session_id > 0:
        #         logger.debug(
        #             f"%s@%s:%s (%s): Session %s allocated to '%s:%s' (%s)", self.jump_host.username,
        #             self.jump_host.host, self.jump_host.port, self.jump_host.session_id, jh_session_id, self.host,
        #             self.port, self.session_id)
        #     else:
        #         self.ssh_error = f"Jump host '{self.jump_host.host}' has no sessions available."
        #         return

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
        self.queue = []

        self.sessions = {}
        for session in range(max_sessions):
            self.sessions[session + 1] = {
                "id": None,
                "status": 'idle',
                "activity": None
            }

    def get_next_available_session(self, session_id: int = None):

        # Checks if there is an available session to connect via. Returns an available session id, or 0 if all are busy.
        if self.current_sessions <= self.max_sessions:
            for index, session in enumerate(range(1, self.max_sessions + 1)):
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
