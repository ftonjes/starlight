# Authentication profiles: Lists of credentials used to authenticate until successful login. Use this when multiple
#   credentials are used within an organization. Order these from most used to least used.

# Types of "username" and "password" values:
#   If value is a dict:
#     "key": Use keyring manager to obtain username and/or password
#     "env": Use environment to get username and/or password
#   If value is a string:
#     Use literal values for username and/or password

# Example configuration file

CONFIG = {
    "devices": {
        "defaults": {
            "connection_timeout": 30,
            "session_timeout": 180,
            "compression": false,
            "retries": 1,
            "retry_interval": 5,
            "max_concurrent_sessions_per_host": 1,
            "max_direct_connections": 10
        }
    },
    "jump_hosts": {
        "hosts": [
            {
                "host": "jh_mac",
                "port": 22,
                "description": "Jump Host",
                "authentication": "ssh_mac_svr_rw",
                "region": "EMEA"
            }
        ],
        "defaults": {
            "compression": true,
            "max_connections": 1,
            "authentication": ["ssh_mac_svr_rw"],
            "port": 22,
            "keepalive": 180,
            "connection_timeout": 30,
            "session_timeout": 180,
            "retries": 1,
            "retry_interval": 5
        }
    },
    "authentication": {
        "profiles": [
            {
                "name": "ssh_ubuntu_rw",
                "description": "Ubuntu Servers",
                "username": {"key": "SSH_LINUX_SRV_USERNAME"},
                "password": {"key": "SSH_LINUX_SRV_PASSWORD"},
                "sudo command": "sudo bash"
            },
            {
                "name": "ssh_opnsense_ro",
                "description": "OPNSense Firewalls",
                "username": {"key": "SSH_OPNSENSE_USERNAME"},
                "password": {"key": "SSH_OPNSENSE_PASSWORD"}
            },
            {
                "name": "ssh_mac_svr_rw",
                "description": "Mac Server",
                "username": {"key": "SSH_MAC_SRV_USERNAME"},
                "password": {"key": "SSH_MAC_SRV_PASSWORD"},
                "sudo command": "sudo bash"
            }
        ]
    }
}
