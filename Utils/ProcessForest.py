# from typing import Dict, List
# import pandas as pd
# from Utils.ProcessNode import ProcessNode
#
#
# class ProcessForest:
#     def __init__(self):
#         self.active_processes: Dict[int, ProcessNode] = {}
#         self.dead_processes: List[ProcessNode] = []  # History of closed processes
#
#     def add_event(self, event) -> ProcessNode:
#         node = None
#
#         # --- 1. HANDLE PID REUSE & EXIT ---
#         if event.event_type_str == "PROCESS_EXIT":
#             # If the process exists, mark it as finished and remove from active
#             if event.pid in self.active_processes:
#                 node = self.active_processes[event.pid]
#                 node.add_event(event)
#                 # Archive it (It's dead now)
#                 self.dead_processes.append(node)
#                 del self.active_processes[event.pid]
#                 return node
#
#         # --- 2. GET OR CREATE NODE ---
#         if event.pid in self.active_processes:
#             # We know this process
#             node = self.active_processes[event.pid]
#
#             # Check for "Silent Reuse" (We missed the exit, but a new EXECVE happened)
#             # Logic: If it's an EXECVE and the comms are totally different and time gap is huge
#             # For simplicity here: We assume if it's in active, it's the same process
#             node.add_event(event)
#         else:
#             # NEW PROCESS DETECTED
#             node = ProcessNode(
#                 pid=event.pid,
#                 ppid=event.ppid,
#                 comm=event.comm,
#                 start_time=event.comm_timestamp
#             )
#             node.add_event(event)
#             self.active_processes[event.pid] = node
#
#             # --- 3. LINK TO PARENT ---
#             # We look for the PPID in our active list
#             if event.ppid in self.active_processes:
#                 parent = self.active_processes[event.ppid]
#                 parent.children.append(node)
#                 node.parent = parent
#             else:
#                 # 3a. Check if the parent recently died but is still in history
#                 parent = next((n for n in self.dead_processes if n.pid == event.ppid), None)
#
#                 # 3b. If completely unknown, create a PHANTOM PARENT!
#                 if not parent:
#                     # This is valid because the comm is permissive and we can get the comm
#                     # -rw-r--r--  1 stefan stefan 0 mar 30 11:26 comm
#                     real_comm = "<untracked_parent>"
#                     try:
#                         # Try to read the process name directly from the Linux kernel
#                         with open(f"/proc/{event.ppid}/comm", "r") as f:
#                             real_comm = f.read().strip()
#                     except Exception:
#                         # If the process already died too fast, or we don't have permission, keep the placeholder
#                         pass
#                     # We use ppid=0 and a placeholder name until we (hopefully) see a real event for it
#                     parent = ProcessNode(
#                         pid=event.ppid,
#                         ppid=0,
#                         comm=real_comm,
#                         start_time=event.comm_timestamp
#                     )
#                     self.active_processes[event.ppid] = parent
#
#                 # Link the child to the dead or phantom parent
#                 parent.children.append(node)
#                 node.parent = parent
#                 pass
#
#         return node
#
#     def print_tree(self, start_pid: int):
#         """
#         Prints the tree starting from a specific PID (like your bash 38635)
#         """
#         # We search in active AND dead processes to find the root
#         root = self.active_processes.get(start_pid)
#         if not root:
#             # Try to find it in history
#             for n in self.dead_processes:
#                 if n.pid == start_pid:
#                     root = n
#                     break
#
#         if not root:
#             print(f" PID {start_pid} not found in Forest.")
#             return
#
#         print(f"🌳 Process Tree for PID {start_pid} ({root.comm})")
#         self._recursive_print(root)
#
#     def _recursive_print(self, node: ProcessNode, depth: int = 0):
#         indent = "    " * depth
#         icon = "└─  " if depth > 0 else " "
#
#         # 1. Print The Process Node
#         print(f"{indent}{icon}PID: {node.pid} | Comm: {node.comm}")
#
#         # 2. Print The Events (What did this process DO?)
#         for evt in node.events:
#             # Formatting timestamp
#             ts = "Unknown"
#             try:
#                 # Assuming nanoseconds string
#                 ts = pd.to_datetime(int(evt.comm_timestamp), unit='ns').strftime('%H:%M:%S')
#             except:
#                 pass
#
#             # Formatting detail (Filename or Socket IP)
#             detail = ""
#             if evt.filename and evt.filename != "void":
#                 detail = f"File: {evt.filename}"
#             elif evt.ipv4 and evt.ipv4 != "0.0.0.0":
#                 detail = f"Net: {evt.ipv4}"
#
#             arrow = "  🔹"
#             if "EXECVE" in evt.event_type_str: arrow = "  "
#             if "EXIT" in evt.event_type_str: arrow = "  "
#             if "SOCKET" in evt.event_type_str: arrow = "  "
#             if "OPEN" in evt.event_type_str: arrow = "  "
#             if "AUTH" in evt.event_type_str: arrow = "  "
#
#             print(f"{indent}    {arrow} [{ts}] {evt.event_type_str} {detail}")
#
#         # 3. Recurse to Children
#         for child in node.children:
#             self._recursive_print(child, depth + 1)
#
#     def build_dataset(self):
#         rows = []
#
#         all_nodes = (
#                 list(self.active_processes.values())
#                 + self.dead_processes
#         )
#
#         for node in all_nodes:
#             vector = node.get_aggregated_vector()
#             rows.append(vector)
#
#         return pd.DataFrame(rows)

# RTIDS -- PART

from typing import Dict, List
import pandas as pd
from predictionAlgorithm.Utils.ProcessNode import ProcessNode

# for the future maybe add this : (bash, timestamp)- > evaluate -> bash gets prunned -> than (bash,new_timestamp_addedd) and evaluate
class ProcessForest:
    def __init__(self):
        self.active_processes: Dict[int, ProcessNode] = {}
        self.dead_processes: List[ProcessNode] = []

    def add_event(self, event) -> ProcessNode:
        # 1. Handle Process Exit
        if event.event_type_str == "PROCESS_EXIT":
            if event.pid in self.active_processes:
                node = self.active_processes[event.pid]
                node.add_event(event)
                self.dead_processes.append(node)
                del self.active_processes[event.pid]
                return node

        # 2. Get or Create the Node for the current event
        if event.pid in self.active_processes:
            node = self.active_processes[event.pid]
            node.add_event(event)
        else:
            node = ProcessNode(
                pid=event.pid,
                ppid=event.ppid,
                comm=event.comm,
                start_time=event.comm_timestamp
            )
            node.add_event(event)
            self.active_processes[event.pid] = node

            # 3. LINK TO PPID (The Critical Part)
            parent = self.active_processes.get(event.ppid)

            if not parent:
                # If parent isn't in active, check history
                parent = next((n for n in self.dead_processes if n.pid == event.ppid), None)

                if not parent:
                    # Parent is totally untracked (the 'bash' that was already running)
                    real_comm = "<untracked_parent>"
                    try:
                        with open(f"/proc/{event.ppid}/comm", "r") as f:
                            real_comm = f.read().strip()
                    except:
                        pass

                    parent = ProcessNode(
                        pid=event.ppid,
                        ppid=0,
                        comm=real_comm,
                        start_time=event.comm_timestamp
                    )
                    # Keep this phantom parent active so other children can find it
                self.active_processes[event.ppid] = parent

            # Establish the link
            node.parent = parent
            if node not in parent.children:
                parent.children.append(node)

        return node

    def prune_tree(self, root_pid: int):
        if root_pid not in self.active_processes:
            return
        root_node = self.active_processes[root_pid]

        def collect_pids(node):
            pids = [node.pid]
            for child in node.children:
                pids.extend(collect_pids(child))
            return pids

        for p in collect_pids(root_node):
            self.active_processes.pop(p, None)
        self.dead_processes.append(root_node)
