def parse_configuration(configuration=None, include_modules=False):
    """
        Obtains configuration of all components associated with the interaction with devices using SSH.

    :configuration: configuration to use for task execution,
    :include_modules: include obtaining information for all available modules
    :return: dict containing configuration information.
    """

    cfg = {}
    if configuration is None:
        try:
            with open('api/cfg/configuration.json', encoding='utf-8', mode='r') as config_file:
                cfg = json.load(config_file)
        except FileNotFoundError:
            pass

    else:
        if isinstance(configuration, dict):
            cfg = configuration
        elif isinstance(configuration, str):
            try:
                with open(configuration, encoding='utf-8', mode='r') as config_file:
                    cfg = json.load(config_file)
            except json.decoder.JSONDecodeError:
                print(f"ERROR: Configuration file '{configuration}' contains invalid JSON syntax.")
            except FileNotFoundError:
                print("ERROR: Invalid configuration (File Not Found)")
                pass

            if cfg is None:
                try:
                    cfg = json.load(configuration)
                except AttributeError:
                    logger.critical("ERROR: Invalid configuration")
                except json.decoder.JSONDecodeError:
                    print("Error with JSON")
                    exit()

    # Check the configuration and remove any invalid authentication profiles from the authentication profile groups:
    warnings = []
    if 'authentication_profiles' in cfg:
        valid_authentication_profiles = list(cfg['authentication_profiles'].keys())
        if 'authentication_profile_groups' in cfg:
            for profile_group in cfg['authentication_profile_groups']:
                for profile in cfg['authentication_profile_groups'][profile_group]:
                    if profile not in valid_authentication_profiles:
                        msg = (
                            f"Authentication profile group '{profile_group}' contains invalid authentication"
                            f" profile '{profile}'.")
                        if msg not in warnings:
                            warnings.append(msg)
                        cfg['authentication_profile_groups'][profile_group].remove(profile)

    # Add the list of loaded modules and ambiguous modules to the configuration:
    if include_modules:
        cfg['modules'], cfg['module_list'] = manage_modules()

    return cfg
