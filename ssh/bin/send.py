"""

    SSH Send (send.py): Sends a command via an active SSH session.

"""

import time
import re

import core.logger as logger
from ssh.bin.identify import id_by_prompt, auto_reponse
from ssh.bin.utilities import strip_ansi

from pprint import pprint


def send_command(self, command: str):

    """

        Send a single command to a connected device over SSH.

    """

    output = {'command': command}

    if isinstance(command, str):

        logger_prefix = f'{self.username}@{self.host}:{self.port}'
        if self.session_id > 0:
            logger_prefix += f" ({self.session_id})"

        # Check session is active and ready for commands:
        inv_shell = None
        try:
            inv_shell = self.session_object
        except OSError as err:
            logger.debug("%s: OS Error: '%s'!", logger_prefix, err)
            self.ssh_error = 'OS Error'
        except EOFError as err:
            logger.debug("%s: EOF Error: '%s'!", logger_prefix, err)
            self.ssh_error = 'EOF Error'
        except ConnectionResetError as err:
            logger.debug("%s: Connection Reset Error: '%s'!", logger_prefix, err)
            self.ssh_error = 'Connection Reset'
        except (SystemExit, KeyboardInterrupt):
            pass
        except Exception as err:
            logger.debug("%s: Connection Error: '%s'!", logger_prefix, err)
            self.ssh_error = str(err)

        if self.ssh_error is not None:
            output['ssh_error'] = self.ssh_error.strip()
            return output

        logger.debug("%s: Sending command '%s'...", logger_prefix, command)
        output['time_sent'] = time.time()
        self.session_object_interact_time = time.time()
        self.session_object.send(command + '\n')

        ssh_output = ''
        cmd_raw = b''
        found_prompt = False
        output['prompt'] = ''
        auto_response_cleanup = []

        while not found_prompt and self.ssh_error is None:

            while inv_shell.recv_ready():
                timer = 0
                raw_input = inv_shell.recv(65536)
                self.raw += raw_input
                cmd_raw += raw_input

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

                output['prompt'] = ssh_output.split('\n')[-1]

            if output['prompt'] != '' and not self.ssh_error and not found_prompt:

                output['time_completed'] = time.time()
                output['output'] = ssh_output.replace(output['prompt'], '')
                if '\n' in output['output']:
                    if output['output'][-1] == '\n':
                        output['output'] = output['output'][0:-1]

                # See if we can identify what devices this might be based on the prompt:
                identified = id_by_prompt(output['prompt'])
                if identified:
                    self.prompt = identified
                    found_prompt = True
                    self.ssh_error = None

                    # Check output for known errors:
                    if 'known_errors' in self.prompt:
                        for error_re in self.prompt['known_errors']:
                            tmp = re.search(error_re, output['output'], re.MULTILINE | re.DOTALL)
                            if tmp:
                                self.ssh_error = tmp.group(1).strip().capitalize()
                                logger.warning(
                                    "%s: Command '%s' failed, error: '%s'. (%.2fs)",
                                    logger_prefix, command, self.ssh_error,
                                    output['time_completed'] - output['time_sent'])
                                break

                    if not self.ssh_error:
                        logger.debug(
                            "%s: Command '%s' completed. (%.2fs)",
                            logger_prefix, command, output['time_completed'] - output['time_sent'])

                # Check for any auto-response content:
                auto_reply = auto_reponse(output['prompt'])
                if auto_reply:
                    logger.debug(
                        "%s: Found '%s', replied with '%s'.",
                        logger_prefix, auto_reply['found'], auto_reply['reply_with'])
                    self.session_object.send(auto_reply['reply_with'])
                    self.session_object_interact_time = time.time()
                    if 'clean' in auto_reply:
                        auto_response_cleanup.append(auto_reply['clean'])
                    output['prompt'] = ''

            # Check for when SSH session gets closed/disconnected:
            if self.session_object.closed:

                # Don't report error if we used a command to close the session on purpose, e.g.: 'exit':
                if command.lower() in ['exit', 'quit', 'logout']:
                    output['time_closed'] = time.time()
                    logger.debug(
                        "%s: Sesssion closed. (%.2fs)",
                        logger_prefix, output['time_closed'] - output['time_sent'])
                    self.session_object_closed_time = output['time_closed']
                    break
                else:
                    # Session closed due to error:
                    self.ssh_error = "Connection lost"
                    output['time_failed'] = time.time()
                    logger.debug(
                        "%s: Connection lost. (%.2fs)",
                        logger_prefix, output['time_failed'] - output['time_sent'])
                    self.session_object_closed_time = output['time_failed']
                    break

            # Cater for when a session takes too long (e.g.: Not seeing expected prompt)
            if (time.time() - self.session_object_start_time) > self.session_object_timeout:
                self.ssh_error = "Timed out. No prompt detected."
                output['time_failed'] = time.time()
                break

            # time.sleep(0.01)  # Sleep a little to give the CPU a break!

        # Remove instances where there are 'DEL' keystrokes followed by spaces, and again 'DEL' keystrokes. This
        #   happens when replying to the 'more' type prompts:
        # if len(auto_response_cleanup) > 0:
        #     for r in auto_response_cleanup:
        #         print(f">> '{r}'")
        #         ssh_output = re.sub(r, '', ssh_output)

        self.history += ssh_output
        self.session_object_interact_time = time.time()
        # Remove the command from the start and prompt from the end of the output:
        output['raw_output'] = re.sub(
            rb'\r\n.*?$', b'', cmd_raw.replace(rb'' + (command + '\r\n').encode('utf-8'), b''))

    else:
        self.ssh_error = f"Error: The 'send_command' function accepts only a string."
        output['time_failed'] = time.time()

    # Generate output
    if self.ssh_error is None:
        output['error'] = self.ssh_error

    tmp = output['output'].split('\r\n')
    for index, item in enumerate(tmp):
        tmp[index] = item.replace('\r', '')
    if tmp[0] == command:
        tmp.pop(0)
    output['output'] = '\n'.join(tmp)

    return output
