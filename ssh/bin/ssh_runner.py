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
