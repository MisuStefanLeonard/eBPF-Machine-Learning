# from dataclasses import  dataclass
# from datetime import datetime

# @dataclass
# class EventMLEntry:
#     # --- Identifiers ---
#     comm: str
#     # filename: str
#     # comm_timestamp: datetime

#     # --- Action Flags (Explicit Types) ---
#     evt_type_is_read: int  # <--- NEW
#     evt_type_is_write: int  # <--- NEW
#     evt_type_is_exec: int  # <--- NEW
#     evt_type_is_connect: int  # <--- NEW
#     evt_type_is_socket_create: int

#     # --- Network Context (Critical Gap Filled) ---
#     is_external_ip: int  # <--- NEW
#     is_privileged_port: int  # <--- NEW (or is_privileged_port)


#     # --- File Metadata (Existing) ---
#     mode_transformed: int
#     new_mode_transformed: int
#     is_file_uid_different: int
#     is_file_gid_different: int
#     is_sensitive_file: int

#     # --- Permission Changes (Existing) ---
#     was_suid_changed: int
#     suid_set: int
#     suid_cleared: int
#     was_sgid_changed: int
#     sgid_set: int
#     sgid_cleared: int
#     was_sticky_changed: int
#     was_permission_changed: int
#     was_owner_changed: int
#     was_group_changed: int

#     # --- Time & Content (Existing) ---
#     was_access_time_changed: int
#     was_modified_time_changed: int
#     was_file_created: int
#     was_file_modified: int

#     # --- Path Heuristics (Expanded) ---
#     is_target_dir_world_writable: int
#     is_current_dir_world_writable: int
#     is_temp_directory: int  # <--- NEW (/tmp, /var/tmp)
#     is_hidden_file: int  # <--- NEW (starts with .)
#     is_in_memory_path: int  # <--- NEW (/dev/shm)

#     # --- Security Indicators (Existing + Enhanced) ---
#     # rdev_major or rdev_minor > 0 and sits outside /dev/
#     # A hardware dev node exists outside the /dev
#     is_dev_backdoor: int
#     # filename in ["/dev/null" , "/dev/random] and file_type == REGU;AR
#     is_fake_device: int
#     is_linked_file_SGID_or_SUID: int
#     is_linked_to_sensitive_file: int
#     is_cross_user_link: int
#     is_symlink: int
#     was_dir_removed: int

#     # --- Execution Context (NEW) ---
#     # is_script_engine: int  # <--- NEW (python, bash, etc)
#     is_privilege_escalation: int  # <--- NEW (switching user)
#     argv_has_network: int
#     argv_is_ip: int
#     # argv_is_encoding: int  # Renamed for clarity
#     argv_entropy: int
#     argv_is_net_tool: int
#     argv_is_sudo: int
#     argv_length: int