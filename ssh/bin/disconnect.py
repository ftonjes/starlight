"""

    SSH 'Disconnection' (disconnect.py): Handles the termination of an SSH session

"""

import time

import ssh.bin.logger as logger


def disconnect(self):

    """

        Disconnects an active SSH session.

    """

    self.session_end_time = time.time()
    self.session_object.close()
    logger_prefix = f'{self.username}@{self.host}:{self.port}'
    if self.session_id > 0:
        logger_prefix += f" ({self.session_id})"
    logger.debug('%s: SSH session disconnected.', logger_prefix)

    if self.jump_host is not None:
        jh_logger_prefix = f'{self.jump_host.username}@{self.jump_host.host}:{self.jump_host.port}'
        if self.jump_host.session_id > 0:
            jh_logger_prefix += f" ({self.jump_host.session_id})"
        jh_session_id = self.jump_host.session_manager.free_session(self.session_id)
        logger.debug("%s: Session %s freed.", jh_logger_prefix, jh_session_id)

    return True
