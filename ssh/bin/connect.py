"""

    SSH 'Connect' (connect.py): Handles initial connection to a device using SSH.

    Returns True, if login is successful, or False if not. Updates SSHSession object properties.

"""

import time
import socket
import paramiko
import re

import core.logger as logger
from ssh.bin.identify import id_by_prompt, id_by_ssh_version
from ssh.bin.utilities import strip_ansi

def connect(self):

    """
        Initiate SSH session
    :return: True if succcess, false if not
    """

    tries = 0
    tries_text = {0: '1st', 1: '2nd', 2: '3rd', 3: '4th', 4: '5th'}
    stop_retries = False

    self.status = 'connecting'
    self.session_object = paramiko.SSHClient()
    self.session_object.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Iterate through authentication 'profiles':
    for auth_item in self.authentication:

        while tries < self.retries:

            attempt_text = ''
            if tries in tries_text:
                if tries > 0:
                    attempt_text = f' ({tries_text[tries]} attempt)'

            ssh_error = None
            connect_start = time.time()
            self.session_object_start_time = time.time()

            self.username = auth_item.get('username')
            if 'sudo_command' in auth_item:
                if 'password' in auth_item and 'sudo_password' not in auth_item:
                    auth_item['sudo_password'] = auth_item['password']

            logger_prefix = f'{self.username}@{self.host}:{self.port}'
            if self.session_id > 0:
                logger_prefix += f" ({self.session_id})"

            try:

                if self.jump_host is None:

                    # Direct connection
                    logger.debug("%s: Attempting SSH connection...%s", logger_prefix, attempt_text)

                    self.session_object.connect(
                        look_for_keys=True,  # Set this to look for locally stored SSH keys (known_hosts).
                        hostname=self.host,
                        port=self.port,
                        timeout=self.connection_timeout,
                        username=self.username,
                        password=auth_item.get('password'),
                        allow_agent=False,
                        compress=self.compression,
                        banner_timeout=self.connection_timeout,
                    )

                else:

                    jump_host = self.jump_host

                    # Connection via jump-host
                    logger.debug(
                        "%s: Attempting SSH connection via '%s'...%s", logger_prefix,
                        jump_host.description if jump_host.description is not None
                        else f"{jump_host.host}:{jump_host.port}", attempt_text)

                    jump_host_transport = self.jump_host.session_object.get_transport()
                    jump_host_channel = jump_host_transport.open_channel(
                        kind='direct-tcpip',
                        dest_addr=(self.host, self.port),
                        src_addr=(jump_host.host, jump_host.port),
                        timeout=self.connection_timeout)

                    self.session_object.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.username,
                        password=auth_item.get('password'),
                        look_for_keys=False,
                        timeout=self.connection_timeout,
                        sock=jump_host_channel,
                        compress=self.compression,
                        banner_timeout=self.connection_timeout,
                        allow_agent=False)

            except (SystemExit, KeyboardInterrupt):
                pass
            except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException,
                    FileNotFoundError, ConnectionResetError, EOFError, socket.error, Exception) as err:

                ssh_error = str(err)

            else:

                transport = self.session_object.get_transport()
                if transport.remote_compression == 'none':
                    compression_text = "None"
                else:
                    compression_text = f"'{transport.remote_compression}'"

                self.status = 'connected'

                # Direct connection to non jump-host
                logger.debug(
                    "%s: Connection successfull. (%.2fs)", logger_prefix, time.time() - connect_start)

                logger.debug(
                    "%s: Cipher: %s, MAC: %s, Version: %s, Compression: %s", logger_prefix,
                    transport.remote_cipher, transport.remote_mac, transport.remote_version, compression_text)

                # self.ssh_mac = transport.remote_mac
                # self.ssh_version = transport.remote_version
                # self.ssh_cipher = transport.remote_cipher
                # self.ssh_compression = None if compression_text == 'None' else compression_text
                #
                # self.local_ip_v4_address = self.jump_host.get_transport().sock.getsockname()[0]
                # self.local_ip_v4_port = self.jump_host.get_transport().sock.getsockname()[1]
                identified = id_by_ssh_version(transport.remote_version)

                if identified:
                    self.vendor = identified['vendor']
                    logger.debug(
                        "%s: Host OS vendor appears to be '%s'. [SSH Version]",
                        logger_prefix, identified['vendor'].capitalize())

                # Get initial banner:
                try:
                    get_banner = transport.get_banner()
                except (SystemExit, KeyboardInterrupt):
                    pass
                except (paramiko.SSHException, paramiko.ssh_exception.SSHException, Exception) as err:
                    logger.warning("\n\nBANNER ERROR: {%s} -> {%s}\n\n", self.host, err)
                else:
                    if get_banner is not None:
                        self.history += strip_ansi(get_banner.decode('utf-8'))
                # Get welcome prompt:
                inv_shell = None
                try:
                    inv_shell = self.session_object.invoke_shell()
                except EOFError as err:
                    logger.debug("%s: EOF Error: '%s'!", logger_prefix, err)
                    ssh_error = 'EOF Error'
                except ConnectionResetError as err:
                    logger.debug("%s: Connection Reset Error: '%s'!", logger_prefix, err)
                    ssh_error = 'Connection Reset'
                except (SystemExit, KeyboardInterrupt):
                    pass
                except Exception as err:
                    logger.debug("%s: Connection Error: '%s'!", logger_prefix, err)
                    ssh_error = str(err)

                ssh_output = ''
                found_prompt = False
                timer = 0
                current_prompt = ''

                while not found_prompt and ssh_error is None:

                    while inv_shell.recv_ready():
                        timer = 0
                        raw_input = inv_shell.recv(65536)
                        self.raw += raw_input

                        # Check if data was received and if so, set the retries to 0:
                        ssh_output += strip_ansi(raw_input.decode('utf-8', 'ignore'))
                        self.session_object_interact_time = time.time()

                        # if re.search(r"% Authentication failed", ssh_output, re.MULTILINE | re.DOTALL):
                        #     ssh_error = "Authentication failed"
                        #     break
                        #
                        # # Opengear device: User has no shell access on device.
                        # if re.search(r"User '.*?' does not have shell access on this device", ssh_output):
                        #     ssh_error = f"User '{self.username}' does not have shell access on this device"
                        #     break

                        current_prompt = ssh_output.split('\n')[-1]

                    if current_prompt != '':
                        if not ssh_error:
                            if not found_prompt:

                                # Try to identify device using prompt
                                identified = id_by_prompt(current_prompt)
                                if identified:
                                    self.prompt = identified
                                    found_prompt = True
                                    if self.vendor is None:
                                        if 'vendor' in identified:
                                            vendor_string = ''
                                            if '|' in identified['vendor']:
                                                for index, n in enumerate(identified['vendor'].split('|')):
                                                    if index == 0:
                                                        vendor_string += n.capitalize()
                                                    elif index == len(identified['vendor'].split('|')) - 1:
                                                        vendor_string += f"' or '{n.capitalize()}"
                                                    else:
                                                        vendor_string += f"', '{n.capitalize()}"
                                            else:
                                                vendor_string += identified['vendor'].capitalize()
                                            logger.debug(
                                                "%s: Host appears to be a '%s' device! [Prompt]", logger_prefix,
                                                vendor_string)

                    if inv_shell.closed:
                        self.ssh_error = "Connection lost"
                        break

                    if (time.time() - self.session_object_start_time) > self.connection_timeout:
                        self.history = strip_ansi(self.raw.decode('utf-8'))
                        self.prompt = current_prompt
                        self.ssh_error = "Timed out. Unknown prompt."
                        stop_retries = True
                        break

                    time.sleep(0.01)
                    timer += 1

                self.session_object_interact_time = time.time()

                if found_prompt:

                    # Check output if it contains known errors:
                    self.session_object = inv_shell
                    self.history += ssh_output
                    self.ssh_error = None
                    logger.debug("%s: Found prompt '%s'.", logger_prefix, self.prompt['prompt'])
                    return True

            if ssh_error is not None:

                # Clean/convert error message:
                self.status = 'error'
                if not isinstance(ssh_error, str):
                    ssh_error = str(ssh_error).strip()
                if len(ssh_error) > 0:
                    if ssh_error[-1] == '.':
                        ssh_error = ssh_error[:-1]
                if 'getaddrinfo failed' in ssh_error:
                    ssh_error = f"Unable to resolve '{self.host}'."
                elif ssh_error in ['timed out', 'Timeout opening channel']:
                    ssh_error = 'Connection timed out'

                self.ssh_error = ssh_error

                # Check for specific type of errors and don't retry the same authentication again:
                if re.search(
                        r"^(Authentication failed|^Bad authentication type; allowed types:|"
                        r"^Device OS issue: No space left on device|ChannelException(2, 'Connect failed'))",
                        self.ssh_error):
                    # Don't retry this error on the same jump-host, but try other authentication profiles:
                    stop_retries = True

                # ChannelException(2, 'Connect failed') usually means ACL is preventing access:
                # e.g.: ssh: connect to host 1.1.1.1 port 22: Permission denied
                if self.ssh_error == "ChannelException(2, 'Connect failed')":
                    self.ssh_error = 'Permission denied'  # ACL restricted

                logger.debug("%s: Error '%s'.", logger_prefix, self.ssh_error)

            if stop_retries:
                tries = self.retries

            else:
                tries += 1

        # Reset error and tries/stop_retries for next authentication type
        self.ssh_error = None
        tries = 0
        stop_retries = False


    return False

