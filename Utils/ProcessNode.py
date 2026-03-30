import re,math
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from Models.EventType import EventType
from Utils.utils import network_tools, target_devices
from Models.Event import Event

@dataclass
class ProcessNode:
    pid: int
    ppid: int
    comm: str
    start_time: int
    IP_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
    # The Tree Structure
    children: List['ProcessNode'] = field(default_factory=list)
    parent: Optional['ProcessNode'] = None

    # The Behavior History (All events this process generated)
    events: List['Event'] = field(default_factory=list)
    argv_context: Dict[str,float] = field(default_factory=dict)

    def add_event(self, event):
        self.events.append(event)
        # Update comm if it changes (e.g., after an execve)
        if event.comm and event.comm != self.comm:
            self.comm = event.comm

    @classmethod
    def calculate_entropy(cls,s):
        if not s: return 0
        p, lns = Counter(s), float(len(s))
        return -sum(count / lns * math.log(count / lns, 2) for count in p.values())

    def process_argv_context(self, argv_list: list):
        """Calculate the argv metrics context"""
        clean_args = [str(arg) for arg in argv_list if arg and str(arg).strip()]
        full_cmd = " ".join(clean_args)
        # full_cmd = " ".join(argv_list)

        entropy = self.calculate_entropy(full_cmd)

        self.argv_context = {
            'argv_has_network': 1 if ("http" in full_cmd or "://" in full_cmd) else 0,
            'argv_is_ip': 1 if self.IP_PATTERN.search(full_cmd) else 0,
            # Check for base64 keyword OR high entropy (obfuscation)
            'argv_has_encoding': 1 if ("base64" in full_cmd or entropy > 5.0) else 0,
            'argv_is_net_tool': 1 if any(t in full_cmd for t in network_tools) else 0,
            'argv_is_sudo': 1 if "sudo" in full_cmd else 0,
            'argv_entropy': entropy,
        }

    def get_execution_chain(self) -> str:
        """
        Builds a string showing the full commands executed in this tree.
        Example: "bash -> cp /bin/bash /tmp/.hidden_bash -> sudo chown root:root /tmp/.hidden_bash"
        """

        def get_full_cmd(node) -> str:
            # 1. Search the node's events for the EXECVE event to extract the raw argv
            for e in node.events:
                # We check event_type_str safely
                if "EXECVE" in str(e.event_type_str):
                    if isinstance(e.argv, list):
                        # Filter out empty padding strings and join with spaces
                        clean_args = [str(arg) for arg in e.argv if arg and str(arg).strip()]
                        if clean_args:
                            return " ".join(clean_args)

                        # Fallback just in case it's already a string
                    elif isinstance(e.argv, str) and e.argv.strip():
                        return e.argv.strip()

            # 2. Fallback to just the basic process name if no argv was captured
            return node.comm

        # Initialize the chain with the root node's full command
        root_cmd = get_full_cmd(self)
        chain = [root_cmd]

        def gather_children(node):
            for child in node.children:
                child_cmd = get_full_cmd(child)

                if child_cmd not in chain:
                    chain.append(child_cmd)

                gather_children(child)

        gather_children(self)
        return " -> ".join(chain)

    def get_aggregated_vector(self) -> Dict[str, float]:
        """
        Calculates the ML vector for this process, INCLUDING the combined
        behavior of all its child processes.
        """
        # 1. Get this specific node's isolated features
        agg_vector = self.to_ml_vector()

        # 2. Add all children's features recursively
        for child in self.children:
            child_vector = child.get_aggregated_vector()

            for key, value in child_vector.items():
                # Don't overwrite the parent's identity or raw score
                if key in ['pid', 'comm', 'ppid', 'risk_score']:
                    continue

                if isinstance(value, (int, float)):
                    # For boolean flags (1 or 0), if ANY child triggered it, the parent inherits it (OR logic)
                    if key.startswith('is_') or key.startswith('argv_'):
                        agg_vector[key] = max(agg_vector.get(key, 0), value)
                    # For counters sum them up
                    else:
                        agg_vector[key] = agg_vector.get(key, 0) + value

        # 3. RECALCULATE the parent's risk score using the full combined context of its children!
        agg_vector["risk_score"] = self.assign_risk_score(agg_vector)
        agg_vector["command_chain"] = self.get_execution_chain()
        return agg_vector

    @classmethod
    def extract_permission_changed(cls, old_mode: int, new_mode: int) -> Dict[str, int]:
        def get_parts(mode):
            other = mode % 10
            group = ( mode // 10 ) % 10
            user = ( mode // 100 ) % 10
            special = ( mode // 1000 ) % 10
            return special,user,group,other

        s_old, u_old, g_old, o_old = get_parts(old_mode)
        s_new, u_new, g_new, o_new = get_parts(new_mode)

        READ, WRITE, EXEC = 4, 2, 1

        changes = {
            # --- USER CHANGES ---
            'user_read_added': 1 if (u_new & READ) and not (u_old & READ) else 0,
            'user_write_added': 1 if (u_new & WRITE) and not (u_old & WRITE) else 0,
            'user_exec_added': 1 if (u_new & EXEC) and not (u_old & EXEC) else 0,

            'user_read_removed': 1 if (u_old & READ) and not (u_new & READ) else 0,
            'user_write_removed': 1 if (u_old & WRITE) and not (u_new & WRITE) else 0,
            'user_exec_removed': 1 if (u_old & EXEC) and not (u_new & EXEC) else 0,

            # --- GROUP CHANGES ---
            'group_write_added': 1 if (g_new & WRITE) and not (g_old & WRITE) else 0,
            'group_exec_added': 1 if (g_new & EXEC) and not (g_old & EXEC) else 0,

            'group_write_removed': 1 if (g_old & WRITE) and not (g_new & WRITE) else 0,
            'group_exec_removed': 1 if (g_old & EXEC) and not (g_new & EXEC) else 0,

            # --- OTHER (WORLD) CHANGES ---
            'world_read_added': 1 if (o_new & READ) and not (o_old & READ) else 0,
            'world_write_added': 1 if (o_new & WRITE) and not (o_old & WRITE) else 0,
            'world_exec_added': 1 if (o_new & EXEC) and not (o_old & EXEC) else 0,

            # --- SPECIAL BITS (SUID/SGID/STICKY) ---
            'suid_added': 1 if (s_new & 4) and not (s_old & 4) else 0,
            'suid_removed': 1 if (s_old & 4) and not (s_new & 4) else 0,
            'sgid_added': 1 if (s_new & 2) and not (s_old & 2) else 0,
            'sgid_removed': 1 if (s_old & 2) and not (s_new & 2) else 0,
            'sticky_added': 1 if (s_new & 1) and not (s_old & 1) else 0,
            'sticky_removed': 1 if (s_old & 1) and not (s_new & 1) else 0,
        }

        return changes

    # @staticmethod
    def assign_risk_score(self, vector: Dict[str, float]):
        score = 0.0

        # -------------------
        # LOW-LEVEL SIGNALS
        # -------------------
        score += 0.01 * vector.get('count_read_event', 0)
        score += 0.03 * vector.get('count_write_event', 0)
        score += 0.01 * vector.get('count_dir_creation_event', 0)
        score += 0.05 * vector.get('count_dir_remove_event', 0)
        score += 0.05 * vector.get('count_file_creation_event', 0)
        score += 0.05 * vector.get('count_link_event', 0)
        score += 0.05 * vector.get('count_symlink_event', 0)
        score += 0.1 * vector.get('count_mknod_create_event', 0)
        score += 0.5 * vector.get('count_rename_event', 0)

        # -------------------
        # AUTHENTICATION & USER EVENTS
        # -------------------
        score += 2.0 * vector.get('count_auth_event_successfully', 0)
        score += 6.0 * vector.get('count_auth_event_fails', 0)
        score += 2.0 * vector.get('count_passwd_change_event_successfully', 0)
        score += 6.0 * vector.get('count_passwd_change_event_fails', 0)
        score += 2.0 * vector.get('count_user_change_event_successfully', 0)
        score += 6.0 * vector.get('count_user_change_event_fails', 0)

        # -------------------
        # FILE MODIFICATIONS
        # -------------------
        score += 1.0 * vector.get('count_file_modification_event_successfully', 0)
        score += 3.0 * vector.get('count_file_modification_event_fails', 0)
        score += 2.0 * vector.get('count_owner_changed', 0)
        score += 1.5 * vector.get('count_group_changed', 0)

        # -------------------
        # PERMISSIONS
        # -------------------
        score += 2.0 * vector.get('count_suid_set', 0)
        score += 2.0 * vector.get('count_sgid_set', 0)
        score += 1.0 * vector.get('count_sticky_set', 0)
        score += 1.0 * vector.get('count_user_write_added', 0)
        score += 0.5 * vector.get('count_user_write_removed', 0)
        score += 0.5 * vector.get('count_user_read_added', 0)
        score += 0.5 * vector.get('count_user_read_removed', 0)
        score += 0.5 * vector.get('count_user_exec_added', 0)
        score += 0.5 * vector.get('count_user_exec_removed', 0)
        score += 0.5 * vector.get('count_group_write_added', 0)
        score += 0.5 * vector.get('count_group_write_removed', 0)
        score += 0.5 * vector.get('count_group_exec_added', 0)
        score += 0.5 * vector.get('count_group_exec_removed', 0)
        score += 0.5 * vector.get('count_world_write_been_added', 0)
        score += 0.5 * vector.get('count_world_read_been_added', 0)
        score += 0.5 * vector.get('count_world_exec_been_added', 0)

        # -------------------
        # SENSITIVE FILES & FAILS
        # -------------------
        score += 4.0 * vector.get('count_sensitive_file', 0)
        score += 3.0 * vector.get('count_is_linked_to_sensitive_file', 0)
        score += 4.0 * vector.get('count_linked_file_SGID_or_SUID', 0)
        score += 6.0 * vector.get('count_sensitive_file_access_fails', 0)

        # -------------------
        # SOCKET & NETWORK
        # -------------------
        score += 1.0 * vector.get('count_socket_create_event', 0)
        score += 1.0 * vector.get('count_socket_connect_event_successfully', 0)
        score += 3.0 * vector.get('count_socket_connect_event_fails', 0)
        score += 1.5 * vector.get('count_external_ip', 0)
        score += 2.0 * vector.get('is_priviliged_port', 0)

        # -------------------
        # DEVICE / PERSISTENCE / MEMORY
        # -------------------
        score += 6.0 * vector.get('is_dev_backdoor', 0)
        score += 5.0 * vector.get('is_fake_device', 0)
        score += 3.0 * vector.get('is_in_memory_path', 0)

        # -------------------
        # FILE TIME FLAGS
        # -------------------
        score += 0.5 * vector.get('count_atime_flag_been_set', 0)
        score += 0.5 * vector.get('count_modified_time_been_changed', 0)

        # -------------------
        # DIRECTORY FLAGS
        # -------------------
        score += 1.0 * vector.get('is_current_dir_world_writable', 0)
        score += 1.0 * vector.get('is_target_dir_world_writable', 0)
        score += 1.0 * vector.get('is_cross_user_link', 0)

        # -------------------
        # ARGV CONTEXT
        # -------------------
        score += 2.0 * vector.get('argv_has_network', 0)
        score += 3.0 * vector.get('argv_is_ip', 0)
        score += 3.0 * vector.get('argv_has_encoding', 0)
        score += 2.0 * vector.get('argv_is_net_tool', 0)
        score += 2.0 * vector.get('argv_is_sudo', 0)
        score += vector.get('argv_entropy', 0) * 0.5

        # -------------------
        # VOLUME & THRESHOLD PENALTIES (Automated Attacks)
        # -------------------
        # Brute Force Indicator (SSH / su / sudo brute force)
        if vector.get('count_auth_event_fails', 0) > 5:
            score += 15.0

        # Ransomware / Wiper Indicator (Massive renames or deletions)
        if vector.get('count_rename_event', 0) > 20:
            score += 20.0
        if vector.get('count_dir_remove_event', 0) > 20:
            score += 15.0

        # Aggressive Enumeration / Scanners
        if vector.get('count_sensitive_file_access_fails', 0) > 10:
            score += 10.0

        # -------------------
        # ADVANCED COMBINATION RULES (Attack Chains)
        # -------------------
        # Original Combinations
        if vector.get('argv_is_net_tool', 0) and vector.get('argv_has_encoding', 0):
            score += 6.0
        if vector.get('is_in_memory_path', 0) and vector.get('count_external_ip', 0):
            score += 7.0
        if vector.get('count_sensitive_file', 0) and vector.get('count_file_modification_event_successfully', 0):
            score += 5.0
        if vector.get('count_suid_set', 0) and vector.get('count_owner_changed', 0):
            score += 8.0
        if vector.get('count_external_ip', 0) and vector.get('argv_is_sudo', 0):
            score += 4.0
        if vector.get('count_sensitive_file_access_fails', 0) and vector.get('count_file_modification_event_successfully', 0):
            score += 7.0
        if vector.get('is_dev_backdoor', 0) and vector.get('is_in_memory_path', 0):
            score += 8.0
        if vector.get('count_linked_file_SGID_or_SUID', 0) and vector.get('count_file_modification_event_successfully', 0):
            score += 7.0

        # NEW: Exfiltration Combinations
        if vector.get('count_read_event', 0) > 10 and vector.get('count_external_ip', 0) > 0:
            score += 8.0
        if vector.get('count_sensitive_file', 0) > 0 and vector.get('argv_is_net_tool', 0):
            score += 10.0

        # NEW: Stealth & Evasion Combinations (Timestomping & Obfuscation)
        if vector.get('count_was_modified_time_changed', 0) > 0 and vector.get('count_sensitive_file', 0) > 0:
            score += 10.0
        if vector.get('count_do_not_update_atime', 0) > 0 and vector.get('count_read_event', 0) > 0:
            score += 6.0
        if vector.get('argv_is_sudo', 0) and vector.get('argv_has_encoding', 0):
            score += 8.0

        # NEW: Privilege Escalation Combinations
        if vector.get('count_suid_set', 0) > 0 and vector.get('is_target_dir_world_writable', 0):
            score += 12.0
        if vector.get('count_sensitive_file', 0) > 0 and (vector.get('count_world_write_been_added', 0) or vector.get('count_world_read_been_added', 0)):
            score += 15.0
        if vector.get('is_cross_user_link', 0) and vector.get('count_sensitive_file', 0) > 0:
            score += 9.0

        # NEW: Malicious Server / Bind Shell Combinations
        # A process created a socket, bound to a privileged port, but was NOT launched via sudo/root
        if vector.get('count_socket_create_event', 0) > 0 and vector.get('is_priviliged_port', 0) > 0 and vector.get('argv_is_sudo', 0) == 0:
            score += 7.0

        # score = score / (1 + len(self.events) * 0.03)
        if score > 0:
            score = math.log1p(score)
        return score

    def to_ml_vector(self) -> Dict[str, float]:
        vector = {
            # 'pid' : self.pid,
            # 'ppid' : self.ppid,
            # 'comm' : self.comm,
            'command_chain' : str,
            # Sum features
            'count_read_event' : 0,
            'count_write_event' : 0,
            # 'count_failed_events_total': 0,
            'count_sensitive_file_access_fails': 0,
            'count_socket_connect_event_successfully' : 0,#
            'count_socket_connect_event_fails': 0,#
            'count_socket_create_event' : 0,
            'count_file_modification_event_successfully': 0,#
            'count_file_modification_event_fails' : 0,#
            'count_file_creation_event' : 0,
            'count_link_event' : 0,
            'count_symlink_event' : 0,
            'count_dir_creation_event' : 0,
            'count_dir_remove_event' : 0,
            # --- IN JOS
            'count_mknod_create_event' : 0,
            'count_rename_event' : 0,
            'count_auth_event_successfully' : 0,
            'count_auth_event_fails': 0,
            'count_passwd_change_event_successfully' : 0,
            'count_passwd_change_event_fails': 0,
            'count_user_change_event_successfully' : 0,
            'count_user_change_event_fails': 0,
            'count_do_not_update_atime':0,
            'count_was_modified_time_changed' : 0,
            # Ownership change
            'count_owner_changed': 0,
            'count_group_changed': 0,
            # File mode changing
            # Special
            'count_suid_set' : 0,
            'count_suid_cleared': 0,
            'count_sgid_set': 0,
            'count_sgid_cleared': 0,
            'count_sticky_set': 0,
            'count_sticky_cleared': 0,
            # User
            'count_user_write_added' : 0,
            'count_user_write_removed' : 0,
            'count_user_read_added': 0,
            'count_user_read_removed': 0,
            'count_user_exec_added': 0,
            'count_user_exec_removed': 0,
            # Group
            'count_group_write_added': 0,
            'count_group_write_removed': 0,
            'count_group_exec_added': 0,
            'count_group_exec_removed': 0,
            # Other
            'count_world_write_been_added': 0,
            'count_world_read_been_added': 0,
            'count_world_exec_been_added': 0,


            # socket metadata
            'count_external_ip' : 0,
            'is_priviliged_port' : 0,

            # file metadata
            'count_sensitive_file' : 0,
            "count_is_linked_to_sensitive_file": 0,
            "count_linked_file_SGID_or_SUID": 0,
            # 'count_file_uid_difference' : 0,
            # 'count_file_gid_difference': 0,
            'count_atime_flag_been_set' : 0,
            'count_modified_time_been_changed' : 0,

            # link and symlink flags
            "is_current_dir_world_writable" : 0,
            "is_target_dir_world_writable" : 0,
            "is_in_memory_path" : 0,
            "is_cross_user_link" : 0,
            "is_dev_backdoor" : 0,
            "is_fake_device" : 0,

            # argv_context
            'argv_has_network': 0,
            'argv_is_ip': 0,
            'argv_has_encoding': 0,
            'argv_is_net_tool': 0,
            'argv_is_sudo': 0,
            'argv_entropy': 0,
        }

        # if events empty return
        if not self.events:
            return vector

        for e in self.events:
            if e.event_type == EventType.EVENT_EXECVE.value:
                # Aici de adaugat ca poate un execve genereaza alte n
                # Poate de adaugat daca atinge sensitive_files
                print(e.argv)
                self.process_argv_context(e.argv)
                vector.update(self.argv_context)
            elif e.event_type == EventType.EVENT_FILE_OPEN_AND_WRITE_EXIT.value:
                vector['count_write_event'] += 1
                if e.is_success == 0 and e.is_sensitive_file == 1:
                    vector['count_sensitive_file_access_fails'] += 1
            elif e.event_type == EventType.EVENT_FILE_OPEN_AND_READ_EXIT.value:
                vector['count_read_event'] += 1
                if e.is_success == 0 and e.is_sensitive_file == 1:
                    vector['count_sensitive_file_access_fails'] += 1
            elif e.event_type == EventType.EVENT_INODE_CREATE.value:
                vector['count_file_creation_event'] += 1
            elif e.event_type == EventType.EVENT_INODE_LINK.value:
                vector['count_link_event'] += 1
                if e.uid != e.old_uid:
                    vector['is_cross_user_link'] = 1
                if e.is_success == 0:
                    vector['count_sensitive_file_access_fails'] += 1
            elif e.event_type == EventType.EVENT_INODE_SYMLINK.value:
                vector['count_symlink_event'] += 1
                if e.is_success == 0:
                    vector['count_sensitive_file_access_fails'] += 1
            elif e.event_type == EventType.EVENT_INODE_MKDIR.value:
                vector['count_dir_creation_event'] += 1
            elif e.event_type == EventType.EVENT_INODE_RMDIR.value:
                vector['count_dir_remove_event'] += 1
            elif e.event_type == EventType.EVENT_INODE_RENAME.value:
                if e.is_success == 0:
                    vector['count_sensitive_file_access_fails'] += 1
                vector['count_dir_remove_event'] += 1
            elif e.event_type == EventType.EVENT_SOCKET_CREATION.value:
                vector['count_socket_create_event'] += 1
            elif e.event_type == EventType.EVENT_SOCKET_CONNECT_OUTBOUND.value:
                if e.is_sock_success == 1:
                    vector['count_socket_connect_event_successfully'] += 1
                else:
                    vector['count_socket_connect_event_fails'] += 1
                if e.ipv4 not in ['0.0.0.0', '127.0.0.1', '255.255.255.255']:
                    vector['count_external_ip'] += 1
                if e.port != 65535:
                    if e.port < 1024:
                        vector['is_priviliged_port'] += 1
            elif e.event_type == EventType.EVENT_INODE_MKNOD.value:
                vector['count_mknod_create_event'] += 1
            elif e.event_type == EventType.EVENT_INODE_RENAME.value:
                vector['count_rename_event'] += 1
            elif e.event_type == EventType.EVENT_AUTH.value:
                if e.is_auth_success == 1:
                    vector['count_auth_event_successfully'] += 1
                else:
                    vector['count_auth_event_fails'] += 1
            elif e.event_type == EventType.EVENT_PASSWD_CHANGE.value:
                if e.is_auth_success == 1:
                    vector['count_passwd_change_event_successfully'] += 1
                else:
                    vector['count_passwd_change_event_fails'] += 1
            elif e.event_type == EventType.EVENT_CHANGE_USER.value:
                if e.is_auth_success == 1:
                    vector['count_user_change_event_successfully'] += 1
                else:
                    vector['count_user_change_event_fails'] += 1
            if e.old_uid != e.new_uid:
                vector['count_owner_changed'] += 1
            if e.old_gid != e.new_gid:
                vector['count_group_changed'] += 1

            permission_changes = self.extract_permission_changed(e.mode_transformed, e.new_mode_transformed)

            if e.event_type == EventType.EVENT_INODE_SETATTR.value:
                if e.is_success == 1:
                    vector['count_file_modification_event_successfully'] += 1
                else:
                    vector['count_file_modification_event_fails'] += 1
                if e.is_success == 0:
                    vector['count_sensitive_file_access_fails'] += 1
                for key, value in permission_changes.items():
                    # User permission
                    if key == "user_read_added" and value == 1:
                        vector['count_user_read_added'] += 1
                    if key == "user_write_added" and value == 1:
                        vector['count_user_write_added'] += 1
                    if key == "user_exec_added" and value == 1:
                        vector['count_user_exec_added'] += 1
                    if key == "user_read_removed" and value == 1:
                        vector['count_user_read_removed'] += 1
                    if key == "user_write_removed" and value == 1:
                        vector['count_user_write_removed'] += 1
                    if key == "user_exec_removed" and value == 1:
                        vector['count_user_exec_removed'] += 1
                    # Group permission
                    if key == "group_write_added" and value == 1:
                        vector['count_group_write_added'] += 1
                    if key == "group_exec_added" and value == 1:
                        vector['count_group_exec_added'] += 1
                    if key == "group_write_removed" and value == 1:
                        vector['count_group_write_removed'] += 1
                    if key == "group_exec_removed" and value == 1:
                        vector['count_group_exec_removed'] += 1
                    # Other permissions
                    if key == "world_read_added" and value == 1:
                        vector['count_world_read_been_added'] += 1
                    if key == "world_write_added" and value == 1:
                        vector['count_world_write_been_added'] += 1
                    if key == "world_exec_added" and value == 1:
                        vector['count_world_exec_been_added'] += 1
                    # SUID , SGID and Sticky bit
                    if key == "suid_added" and value == 1:
                        vector['count_suid_set'] += 1
                    if key == "suid_removed" and value == 1:
                        vector['count_suid_cleared'] += 1
                    if key == "sgid_added" and value == 1:
                        vector['count_sgid_set'] += 1
                    if key == "sgid_removed" and value == 1:
                        vector['count_sgid_cleared'] += 1
                    if key == "sticky_added" and value == 1:
                        vector['count_sticky_set'] += 1
                    if key == "sticky_removed" and value == 1:
                        vector['count_sticky_cleared'] += 1

            if e.is_sensitive_file == 1:
                vector['count_sensitive_file'] += 1
            if e.is_linked_to_sensitive_file == 1:
                vector['count_is_linked_to_sensitive_file'] += 1
            if e.is_linked_file_SGID_or_SUID == 1:
                vector['count_linked_file_SGID_or_SUID'] += 1

            if e.do_not_update_atime == 1:
                vector['count_do_not_update_atime'] += 1
            if e.was_modified_time_changed == 1:
                vector['count_was_modified_time_changed'] += 1

            # bool flags
            # here it depends on moving! e.g. score based on from to where it is moved
            if e.is_current_dir_world_writable == 1:
                vector['is_current_dir_world_writable'] = 1
            if e.is_target_dir_world_writable == 1:
                vector['is_target_dir_world_writable'] = 1
            if e.filename.__contains__("/dev/shm"):
                vector['is_in_memory_path'] = 1

            is_device = e.file_type in ["CHAR_DEVICE", "BLOCK_DEVICE"]
            in_dev_path = e.filename.startswith("/dev/")

            if is_device and not in_dev_path:
                vector['is_dev_backdoor'] = 1

            if e.file_type == "REGULAR" and e.filename in target_devices:
                vector['is_fake_device'] = 1

        vector["risk_score"] = self.assign_risk_score(vector)
        return vector

    def compute_score(self):
        vector = self.to_ml_vector()
        score = self.assign_risk_score(vector)
        return score

