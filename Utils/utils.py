MAX_ARGS_CAPTURED = 8
MAX_ARGV_LEN = 64
MAX_CHAR_LEN = 256
TYPE = 16
UNIX_PATH_MAX = 108
MAX_BUFFER_SIZE = 512
network_tools = ["curl","wget","nc", "scp", "ssh", "tcpdump", "nmap"]
target_devices = ["/dev/null", "/dev/zero", "/dev/random", "/dev/urandom", "/dev/console"]
agg_rules = {
    # --- ID (Keep Context) ---
    'comm': 'first',

    # --- Sum (Activity Volume) ---
    'evt_type_is_read': 'sum',
    'evt_type_is_write': 'sum',
    'evt_type_is_exec': 'sum',
    'evt_type_is_connect': 'sum',
    'evt_type_is_socket_create': 'sum',
    'is_external_ip': 'sum',
    'was_file_created': 'sum',
    'was_file_modified': 'sum',
    'was_dir_removed': 'sum',
    'was_permission_changed': 'sum',
    'was_owner_changed': 'sum',
    'was_group_changed': 'sum',
    'is_hidden_file': 'sum',
    'is_temp_directory': 'sum',
    'argv_has_network': 'sum',
    'argv_is_ip': 'sum',
    'argv_is_net_tool': 'sum',

    # --- Max (Red Flags / Binary States) ---
    'is_privileged_port': 'max',      # Connecting to port 22/80/443 is common, knowing IF it did is enough
    'is_sensitive_file': 'max',       # Once is enough to trigger alert
    'was_suid_changed': 'max',        # Critical security event
    'was_sgid_changed': 'max',
    'is_dev_backdoor': 'max',         # Hard red flag
    'is_fake_device': 'max',
    'is_linked_to_sensitive_file': 'max',
    'is_linked_file_SGID_or_SUID': 'max',
    'is_in_memory_path': 'max',
    'is_privilege_escalation': 'max',
    'argv_is_sudo': 'max',
    'is_target_dir_world_writable': 'max',
    'is_current_dir_world_writable': 'max',

    # --- Max (Outlier Stats) ---
    'argv_entropy': 'max',            # We care about the most obfuscated command
    'argv_length': 'max'              # We care about the longest payload
}