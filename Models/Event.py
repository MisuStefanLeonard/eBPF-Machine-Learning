from dataclasses import  dataclass,field
from typing import List

from Models.EventType import EventType


@dataclass
class Event:
    # Generics
    durations_ns : int
    event_type : EventType
    event_type_str : str
    uid : int
    username : str
    gid : int
    groupname : str
    pid : int
    ppid : int
    exit_code : int
    argv : List[str]
    filename : str
    comm : str
    exe : str
    # Auth
    is_auth_success : int
    is_switching_user : int
    is_switching_root : int
    is_changing_password : int
    is_root_command : int
    name : str
    rhost : str
    rname : str
    login_type : str
    # Socket
    protocol_family : int
    socket_type : int
    protocol : int
    peer_pid : int
    peer_uid : int
    peer_gid : int
    backlog : int
    ifindex : int
    ipv4 : str
    local_ipv4_socket_addr : str
    port : int
    is_important_port : int
    kernel_sock : int
    is_sock_success : int
    local_socket_port : int
    ipv6 : str
    local_ipv6_socket_addr : str
    path : str
    # File event
    old_mtime : int
    new_mtime : int
    old_ctime : int
    new_ctime : int
    old_atime : int
    new_atime : int
    comm_timestamp : int
    mode : int
    new_mode : int
    mode_transformed : int
    new_mode_transformed : int
    old_uid : int
    new_uid : int
    old_gid : int
    new_gid : int
    dev_major : int
    dev_minor : int
    dev_major_new : int
    dev_minor_new : int
    rdev_major : int
    rdev_minor : int
    rdev_major_new : int
    rdev_minor_new : int
    is_success : int
    do_not_update_atime : int
    was_file_created : int
    was_file_modified : int
    is_sensitive_file : int
    is_symlink : int
    was_suid_changed : int
    suid_set : int
    suid_cleared : int
    was_sgid_changed : int
    sgid_set : int
    sgid_cleared : int
    was_sticky_changed : int
    sticky_set : int
    sticky_cleared : int
    was_permission_changed : int
    was_owner_changed : int
    was_group_changed : int
    was_creation_time_changed : int
    was_access_time_changed : int
    was_modified_time_changed : int
    is_target_dir_world_writable : int
    is_linked_file_SGID_or_SUID : int
    is_linked_to_sensitive_file : int
    is_cross_user_link : int
    was_dir_removed : int
    is_current_dir_world_writable : int
    file_type : str
    file_type_new : str
    new_filename : str

    @classmethod
    def from_dict(cls, data:dict):
        valid_keys = {k: v for k, v in data.items() if k in cls.__annotations__}
        if "duration_ns" in valid_keys and isinstance(valid_keys["duration_ns"], str):
            valid_keys["duration_ns"] = int(valid_keys["duration_ns"])
        if "mode_transformed" in valid_keys and isinstance(valid_keys["mode_transformed"], str):
            valid_keys["mode_transformed"] = int(valid_keys["mode_transformed"])
        if "new_mode_transformed" in valid_keys and isinstance(valid_keys["new_mode_transformed"], str):
            valid_keys["new_mode_transformed"] = int(valid_keys["new_mode_transformed"])

        return cls(**valid_keys)
