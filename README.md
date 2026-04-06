# TOC

- [**Prerequisites**](#disclaimer)
- [**Language**](#language)
- [**Installation**](#i-installation)
- [**Documentation**](#2-official-documentation)
    - [**_File structure_**](#i-file-structure)
    - [**_Algorithm explanation_**](#i-algorithm-explanation)
        - [**`utils.py`**](#1-utilspy)
        - [**`ProcessNode.py`**](#2-processnodepy)
        - [**`ProcessForest.py`**](#3-processforestpy)
    - [**_Machine learning algorithm_**](#ii-machine-learning-algorithm)
        - [**`RandomForest`**](#i-randomforest)
        - [**`XGBoost`**](#ii-xgboost)
        - [**`Results`**](#iii-results)
    - [**_Drawbacks_**](#iii-drawbacks)


### DISCLAIMER
- Prefferably use `python 3.13` since the project was made with this
- Prefferably you're sitting on ubuntu 24.04
```bash
cat /etc/lsb-release

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.4 LTS"

uname -a

Linux stefan-Latitude-7480 6.8.0-106-generic #106-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 07:58:08 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux


```
- Please go check [eBPF_log_collector](https://github.com/MisuStefanLeonard/eBPF_log_collector) first then continue with this **repository**.

### LANGUAGE
- **first part** = [eBPF_log_collector](https://github.com/MisuStefanLeonard/eBPF_log_collector)


## I. Installation

### 1.CREATE VENV

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 2.REQUIREMENTS - INSTALLING

```bash
python -m pip install -r requirements.txt
```

### 3. INSTALLING MONGODB ON LOCALHOST ([docs](https://www.mongodb.com/docs/manual/administration/install-community/?linux-distribution=ubuntu&linux-package=default&operating-system=linux&search-linux=with-search-linux))

#### Run this
```bash
sudo apt-get install gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
```
##### Create the list file `/etc/apt/sources.list.d/mongodb-org-8.2.list` for your version of Ubuntu.

```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.2.list
sudo apt-get update
```

#### Run this to install mongodb-community edition

```bash
sudo apt-get install -y mongodb-org
```

#### Start mongo service

```bash
sudo systemctl start mongod
```

#### If you receive an error similar to the following when starting mongod:

`Failed to start mongod.service: Unit mongod.service not found.`

#### Run this

```bash
sudo systemctl daemon-reload
```
#### Verify that MongoDB has started successfully.

```bash
sudo systemctl status mongod
● mongod.service - MongoDB Database Server
     Loaded: loaded (/usr/lib/systemd/system/mongod.service; disabled; preset: >
     Active: active (running) since Thu 2026-03-19 10:21:36 EET; 1min 36s ago

/* rest of the output ommited */

```

## 2. Official documentation
- So, if you walked through the [eBPF_log_collector](https://github.com/MisuStefanLeonard/eBPF_log_collector), than we can start here, because this part, which is **part II** depends heavily on the **first part**.If you did not, please go take a look. It's a 45min/1hour lecture.
- This project, as I said in the line above, is the continuation of the project as a whole, more specifically, the **machine learning** part.
- What logs I collected myself, I tuned them and feed them into a **ML** algorithm.
  - Let's take a look at the **file structure**.
- ### I. File structure
    ```bash
    .
    ├── dataEngineering.py
    ├── gatheredCsv
    │   ├── general_logs.csv
    │   └── scripts_results
    │       ├── beroot.csv
    │       ├── cron_job_with_network.csv
    │       ├── cron_job_without_network.csv
    │       ├── dummyScriptWithReadHook.csv
    │       ├── exfiltration.csv
    │       ├── fake_data_dev_with_exfiltration_on_c2server.csv
    │       ├── general_logs_cleaned.csv
    │       ├── hijack.csv
    │       ├── link_pass_attack_with_pass.csv
    │       ├── log_collector.csv
    │       ├── log_wiper.csv
    │       ├── malware.csv
    │       ├── perm_tamper.csv
    │       ├── shadow_user.csv
    │       ├── ssh_keytampering.csv
    │       ├── SUID_privilege_escalation.csv
    │       ├── user_hunter.csv
    │       └── watcher.csv
    ├── __init__.py
    ├── ML_Models
    │   ├── RandomForest_model.joblib
    │   ├── tfidf_vectorizer.joblib
    │   └── XGBoost_model.json
    ├── Models
    │   ├── EventMLEntry.py
    │   ├── Event.py
    │   └── EventType.py
    ├── Plots
    │   ├── RandomForest_confusion_matrix.png
    │   ├── RandomForest_feature_importance.png
    │   ├── RandomForest_metrics.png
    │   ├── RandomForest_pr_curve.png
    │   ├── RandomForest_roc_curve.png
    │   ├── XGBoost_confusion_matrix.png
    │   ├── XGBoost_feature_importance.png
    │   ├── XGBoost_metrics.png
    │   ├── XGBoost_pr_curve.png
    │   └── XGBoost_roc_curve.png
    ├── README.md
    ├── requirements.txt
    ├── runProgram.py
    ├── ScoresAssignedCSV
    │   ├── beroot_scores.csv
    │   ├── cron_job_with_network_scores.csv
    │   ├── cron_job_without_network_scores.csv
    │   ├── dummyScriptWithReadHook_scores.csv
    │   ├── exfiltration_scores.csv
    │   ├── fake_data_dev_with_exfiltration_on_c2server_scores.csv
    │   ├── finalDfTraining
    │   │   └── finalDfTraining.csv
    │   ├── general_logs_cleaned_scores.csv
    │   ├── hijack_scores.csv
    │   ├── labeled
    │   │   ├── beroot_scores_labeled.csv
    │   │   ├── cron_job_with_network_scores_labeled.csv
    │   │   ├── cron_job_without_network_scores_labeled.csv
    │   │   ├── dummyScriptWithReadHook_scores_labeled.csv
    │   │   ├── exfiltration_scores_labeled.csv
    │   │   ├── fake_data_dev_with_exfiltration_on_c2server_scores_labeled.csv
    │   │   ├── general_logs_cleaned_scores_labeled.csv
    │   │   ├── hijack_scores_labeled.csv
    │   │   ├── link_pass_attack_with_pass_scores_labeled.csv
    │   │   ├── log_collector_scores_labeled.csv
    │   │   ├── log_wiper_scores_labeled.csv
    │   │   ├── malware_scores_labeled.csv
    │   │   ├── perm_tamper_scores_labeled.csv
    │   │   ├── shadow_user_scores_labeled.csv
    │   │   ├── ssh_keytampering_scores_labeled.csv
    │   │   ├── SUID_privilege_escalation_scores_labeled.csv
    │   │   ├── user_hunter_scores_labeled.csv
    │   │   └── watcher_scores_labeled.csv
    │   ├── labeledWithTfIdfVectorizer
    │   │   ├── beroot_scores_TfIdfVectorizer.csv
    │   │   ├── cron_job_with_network_scores_TfIdfVectorizer.csv
    │   │   ├── cron_job_without_network_scores_TfIdfVectorizer.csv
    │   │   ├── dummyScriptWithReadHook_scores_TfIdfVectorizer.csv
    │   │   ├── exfiltration_scores_TfIdfVectorizer.csv
    │   │   ├── fake_data_dev_with_exfiltration_on_c2server_scores_TfIdfVectorizer.csv
    │   │   ├── general_logs_cleaned_scores_TfIdfVectorizer.csv
    │   │   ├── hijack_scores_TfIdfVectorizer.csv
    │   │   ├── link_pass_attack_with_pass_scores_TfIdfVectorizer.csv
    │   │   ├── log_collector_scores_TfIdfVectorizer.csv
    │   │   ├── log_wiper_scores_TfIdfVectorizer.csv
    │   │   ├── malware_scores_TfIdfVectorizer.csv
    │   │   ├── perm_tamper_scores_TfIdfVectorizer.csv
    │   │   ├── shadow_user_scores_TfIdfVectorizer.csv
    │   │   ├── ssh_keytampering_scores_TfIdfVectorizer.csv
    │   │   ├── SUID_privilege_escalation_scores_TfIdfVectorizer.csv
    │   │   ├── user_hunter_scores_TfIdfVectorizer.csv
    │   │   └── watcher_scores_TfIdfVectorizer.csv
    │   ├── link_pass_attack_with_pass_scores.csv
    │   ├── log_collector_scores.csv
    │   ├── log_wiper_scores.csv
    │   ├── malware_scores.csv
    │   ├── perm_tamper_scores.csv
    │   ├── shadow_user_scores.csv
    │   ├── ssh_keytampering_scores.csv
    │   ├── SUID_privilege_escalation_scores.csv
    │   ├── user_hunter_scores.csv
    │   └── watcher_scores.csv
    └── Utils
        ├── ProcessForest.py
        ├── ProcessNode.py
        └── utils.py
    ```
    - The file `dataEngineering.py` is the main file that was used for training/testing. In there the data is prepared to be feed into the **ML** algorithm. We'll come into more details on the training later.
    - The directory `gatheredCsv` are the main `.csv` file logs that we were used for training.They include also some `beningn` logs in the file `general_logs_cleaned` which was generated , from the previous part, [eBPF_log_collector](https://github.com/MisuStefanLeonard/eBPF_log_collector), using the file `filter_logs_2.txt`. These are all benign logs, and I cleaned them a little bit. Why ? Because most of the commands were for other **distros**. The rest of the `.csv` files are simulated attacks , **simple ones**, created by me. The files are also in the **first part**.
    - The directory `ML_Models` hold the `2` models that I used to train on. I choose `RandomForest` and `XGBoost` because of their decision tree algorithm. They do very well on classifying data (especially **binary**), so they were a perfect choice.
    - The directory `Models` hold 2 classes and 1 enum. `Event.py` which is how the **log** is received from **first part** ([language](#language)). The `EventType.py` which is also from the **first part** [(language)](#language) and are the **events** gathered. 
    - **`EventType.py`**
        ```python
        from enum import Enum

        class EventType(Enum):
            EVENT_FILE_OPEN_AND_WRITE_EXIT = 1
            EVENT_FILE_OPEN_AND_READ_EXIT = 2
            EVENT_EXECVE = 3
            EVENT_PROCESS_EXIT = 4
            EVENT_INODE_SETATTR = 5
            EVENT_INODE_CREATE = 6
            EVENT_INODE_LINK = 7
            EVENT_INODE_SYMLINK = 8
            EVENT_INODE_MKDIR = 9
            EVENT_INODE_RMDIR = 10
            EVENT_INODE_MKNOD = 11
            EVENT_INODE_RENAME = 12
            EVENT_AUTH = 13
            EVENT_PASSWD_CHANGE = 14
            EVENT_CHANGE_USER = 15
            EVENT_SOCKET_CREATION = 16
            EVENT_SOCKET_BIND = 17
            EVENT_SOCKET_CONNECT_OUTBOUND = 18
            EVENT_SOCKET_LISTEN = 19
            EVENT_SOCKET_ACCEPT = 20


        ```
    - **`Event.py`**
        ```python
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

        ```
    - The directory `Plots` hold the plots for the training on each algorithm. They include the `metrics`,`confusion_matrix`,`feature_importance score`,`pr_curve`, `roc_curve`. The default metrics for evaluating a **ML algorithm** capability.
    - The directory `ScoresAssignedCSV` hold a lot of data. Let's check it out.
        - All the files that are not in a directory are the same `.csv` from earlier, but now with a new column added `risk_score`. We will come back later and explain more about this `risk_score`.
        <a id="risk-score"></a>
        - The files inside the `labeled` directory are the same `.csv` from earlier with the `risk_score` column, but now **labeled** (suspicious / benign).
        - The files inside the `labeledWithTfIdfVectorizer` are the same `.csv` from the line **above**, but now with the `TfIdfVectorizer` added. Why would you add something like this here ? Because, one of the algorithm metrics is the `chain_of_commands` and since you cannot feed **strings** into a mathematical algorithm, we need to transform it. So yeah, that is why I used it.
        - And in the `finalDfTraining` directory is the **final csv** that was used for training/testing.
        - All these files that I talked about above can we obtained by running the `dataEngineering.py`.
        - And the last directory, called `Utils` is the **base** on how the ML algorithm detects suspicious activites, suspicious **chain of commands**, etc. Let's check it out.
    - This includes three files: `ProcessForest.py`, `ProcessNode.py` and `utils.py`. We will talk about them now.
        - ### I. Algorithm explanation.
            #### **1.** `utils.py`
            - Here we defined some **constants** that we used across the program, such as `network_tools`, `target_devices`.
            - These are used to calculate the `risk_score` we talked about earlier.
            - Whether a network tool was used, or if the targeted devices is in `/dev`
                ```python
                network_tools = ["curl","wget","nc", "scp", "ssh", "tcpdump", "nmap"]
                target_devices = ["/dev/null", "/dev/zero", "/dev/random", "/dev/urandom", "/dev/console"]
                ```
            #### **2.** `ProcessNode.py`
            - This file is the **bread**. The **butter** is the `ProcessForest.py`, we will talk about it after.
            - How I tried to think the prediction algorithm was in a **tree** like structure. What do I mean by that?
            - Let's take an example : 
                - User does `sudo cat /etc/passwd`
                - `mkdir test`
                - `cd test`
                - `touch script.sh`
                - `chmod +x script.sh`
                - `cd ..`
                - `rm -rf test`
                - So this all have the same parent , which is `bash` for the current case. All of these must be linked under their **parent**, which is `bash` here.
                - I also added a **safe-lock**. In case someone writes in terminal these commands , and than they do not write anything for 5 mins, the chain will be marked as stale , get **evaluated** and predicted.
                - Here I also calculated the `risk_score` (as explained [earlier](#risk-score)) and used it to label each entry as **suspicious** or **benign**.  
                ```python
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
                ```
                - As you can see, the values are **subjective**. Which means that maybe you would add other **metrics** here.
                - Let's take a look on how I decided the **risk_score**.
                - If you remember correctly from the **first part (see [language](#language))**, I defined some events. Let's remember them. If you will check the `Models/EventType.py` there is an **enum** there. These are the events.
                ```python
                from enum import Enum

                class EventType(Enum):
                    EVENT_FILE_OPEN_AND_WRITE_EXIT = 1
                    EVENT_FILE_OPEN_AND_READ_EXIT = 2
                    EVENT_EXECVE = 3
                    EVENT_PROCESS_EXIT = 4
                    EVENT_INODE_SETATTR = 5
                    EVENT_INODE_CREATE = 6
                    EVENT_INODE_LINK = 7
                    EVENT_INODE_SYMLINK = 8
                    EVENT_INODE_MKDIR = 9
                    EVENT_INODE_RMDIR = 10
                    EVENT_INODE_MKNOD = 11
                    EVENT_INODE_RENAME = 12
                    EVENT_AUTH = 13
                    EVENT_PASSWD_CHANGE = 14
                    EVENT_CHANGE_USER = 15
                    EVENT_SOCKET_CREATION = 16
                    EVENT_SOCKET_BIND = 17
                    EVENT_SOCKET_CONNECT_OUTBOUND = 18
                    EVENT_SOCKET_LISTEN = 19
                    EVENT_SOCKET_ACCEPT = 20
                ```                 
                - From here, I took the **count** metric from **almost** all of this events. Some of them are combined into one, or not.
                - So for example, look at the **file modification** :
                    ```python
                    # -------------------
                    # FILE MODIFICATIONS
                    # -------------------
                    score += 1.0 * vector.get('count_file_modification_event_successfully', 0)
                    score += 3.0 * vector.get('count_file_modification_event_fails', 0)
                    score += 2.0 * vector.get('count_owner_changed', 0)
                    score += 1.5 * vector.get('count_group_changed', 0)
                    ```
                    - In this metrics, events like `EVENT_FILE_OPEN_AND_WRITE_EXIT_` , `EVENT_INODE_SETATTR` get incorporated and tracked.
                - Let's move forward now. Than we look at the same **count** metrics , but on **permission** (e.g **file tampering**)
                    - **suid/sgid/sticky bit set/unset**
                    - **file permission**
                    - **write** user permission granted
                    - **read** user permission granted
                    - **exec** user permission granted
                    - **write** group write permission granted
                    - **exec** group write permission granted
                    - **world write** permission granted
                    - **world read** permission granted
                    - **world exec** permission granted
                    ```python
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
                    ```
                - Also , we check if the files that are being tampered , are from the **sensitive list**.
                - To refresh your memory, in the **first part**(see [language](#language)), we got a `.txt` file called `sensitive_files.txt`. I included a default list in there, but you can add , than re-train the whole model if you wish.
                - Very important, in this file everything is **pattern matched**. So if your file path is `/etc/passwd` and in your list is a `/etc/' , it will get **matched**.
                    ```txt
                    /etc/
                    /tmp/
                    /var/
                    /.ssh/
                    /bin/
                    /usr/bin/
                    /sbin/
                    /lib/
                    /usr/lib/
                    /var/tmp/
                    /.bashrc/
                    ```
                - The code:
                    ```python
                    # -------------------
                    # SENSITIVE FILES & FAILS
                    # -------------------
                    score += 4.0 * vector.get('count_sensitive_file', 0)
                    score += 3.0 * vector.get('count_is_linked_to_sensitive_file', 0)
                    score += 4.0 * vector.get('count_linked_file_SGID_or_SUID', 0)
                    score += 6.0 * vector.get('count_sensitive_file_access_fails', 0)
                    ```
                - We then look into **socket** , **dev/persistence/memory**, **file time flags**, and **directory flags**.
                    - We count the socket events and give them a score
                    - We check if we got an **in memory** attack , or a **fake dev** or something that is **persisted** into our system.
                    - File time flags (e.g the flag **O_NOATIME** being set)
                    - Than the **directory flags**:
                    - `is_current_dir_world_writable`, 
                    - `is_target_dir_world_writable`, 
                    - `is_cross_user_link` (if the user `stefan` used a `ln` to a file owned by `stefan2`)
                    - The last 3 lines , are all **boolean** params. It would be pointless to **count** them as the **socket** ones, because they alone are **suspicious**
                    ```python
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
                    ```
                - Moving on , other very important metrics are the **_argv_context_**.
                    ```python
                    # -------------------
                    # ARGV CONTEXT
                    # -------------------
                    score += 2.0 * vector.get('argv_has_network', 0)
                    score += 3.0 * vector.get('argv_is_ip', 0)
                    score += 3.0 * vector.get('argv_has_encoding', 0)
                    score += 2.0 * vector.get('argv_is_net_tool', 0)
                    score += 2.0 * vector.get('argv_is_sudo', 0)
                    score += vector.get('argv_entropy', 0) * 0.5
                    ```
                - We defined two functions called `def calculate_entropy(self)` and `def process_arg_context()`
                - As you can read, one processes the context of our **argv** and the other one calculates the **entropy**, which is a powerfull metric. Why did I choose the entropy? The entropy of our context is very useful because if a user does **encodes** or **obfuscates** a script or a file, we will get a **high entropy**, which was calculated using the **_Shannon Entropy_**. This tells us how **probable** is that that piece of information to be there.
                - Formula : $$H = -\sum_{i=1}^{n} p_i \log_2(p_i)$$
                    ```python
                    @classmethod
                    def calculate_entropy(cls,s):
                        if not s: return 0
                        p, lns = Counter(s), float(len(s))
                        return -sum(count / lns * math.log(count / lns, 2) for count in p.values())

                    def process_argv_context(self, argv_list: list):
                        """Calculate the argv metrics context"""
                        clean_args = [str(arg) for arg in argv_list if arg and str(arg).strip()]
                        full_cmd = " ".join(clean_args)

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
                    ```
                - We also check if there is a **network tool** used, if the user is downloading something from an **endpouint**, which also can be suspicious.
                - For the final metrics, we check **suspicious combinations**:
                    - A lot of auth events fails -> May indicate a brutforce
                    - A lot of **renaming** or **dir removal** -> May indicate ransomware/wiping 
                    - A lot of scanning on the system (e.g touching sensitive files from `/etc/ , /var/ , etc`) -> May indicate scanning for bypassing different security measures , either from `bins` or in general
                    - We then look at combination of more **suspicious** activities such as:
                    - **Attack chains**
                        - `argv_is_net_tool` with `argv_has_encoding`
                        - `is_in_memory_path` with `count_external_ip`
                        - `count_sensitive_file` with `count_file_modification_event_successfully`
                        - `count_suid_set` with `count_owner_changed`
                        - `count_external_ip` with `argv_is_sudo`
                        - `count_sensitive_file_access_fails` with `count_file_modification_event_successfully`
                        - `is_dev_backdoor` with `is_in_memory_path`
                        - `count_linked_file_SGID_or_SUID` with `count_file_modification_event_successfully`
                    - **Exfiltration chains**
                        ```python
                            if vector.get('count_read_event', 0) > 10 and vector.get('count_external_ip', 0) > 0:
                            score += 8.0
                        if vector.get('count_sensitive_file', 0) > 0 and vector.get('argv_is_net_tool', 0):
                            score += 10.0
                        ```
                    - **Stealth & Evasion**
                        ```python
                        if vector.get('count_was_modified_time_changed', 0) > 0 and vector.get('count_sensitive_file', 0) > 0:
                            score += 10.0
                        if vector.get('count_do_not_update_atime', 0) > 0 and vector.get('count_read_event', 0) > 0:
                            score += 6.0
                        if vector.get('argv_is_sudo', 0) and vector.get('argv_has_encoding', 0):
                            score += 8.0
                        ```
                    - **Privilege Escalation**
                        ```python
                        if vector.get('count_suid_set', 0) > 0 and vector.get('is_target_dir_world_writable', 0):
                            score += 12.0
                        if vector.get('count_sensitive_file', 0) > 0 and (vector.get('count_world_write_been_added', 0) or vector.get('count_world_read_been_added', 0)):
                            score += 15.0
                        if vector.get('is_cross_user_link', 0) and vector.get('count_sensitive_file', 0) > 0:
                            score += 9.0
                        ```
                    - **Malicious Server / Shell binding**
                        ```python
                        if vector.get('count_socket_create_event', 0) > 0 and vector.get('is_priviliged_port', 0) > 0 and vector.get('argv_is_sudo', 0) == 0:
                            score += 7.0
                        ```
            - Than for the final score calculation I **normalized** it using the `log1p`. Because we can have a benign script or commands that may perform a lot of reads and writes , but are not harmfull (e.g `systemd` checkups), only if the **score** is bigger than 0.
                ```python
                if score > 0:
                    score = math.log1p(score)
                ```
            - Than going next, we need to transform all this logs that I gathered into a **vector** that our algorithm can understand. The logs that we captured with the **first part** (see [language](https://github.com/MisuStefanLeonard/eBPF_log_collector)) are **raw** and the information is not alligned with our requirements.
            - For that I devised the function called `to_ml_vector()` that will transform everything as our ML requires.
                ```python
                def to_ml_vector(self) -> Dict[str, float]:
                vector = {
                    'command_chain' : str,
                    # Sum features
                    'count_read_event' : 0,
                    'count_write_event' : 0,
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

                ```
            - I also tracked the `command_chain` for a tree of processes based on the **parent pid**.
                ```python

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
                ```
            - Next, we cummulate the **risk_score** for the suspicious activity based on an `aggregated vector`. Every event that it's linked to the **parent event** is aggregated into the **vector** that will be fed into the **ML algorithm**.
                ```python
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
                ```
        #### **3. `ProcessForest.py`**
        - Now we will talk about the algorithm that builds the **tree** of processes. Eveything will get linked to the **root** process of it's own, but we also maintain a list of the `dead_processes` and `active_processes`.
        - We also handle the **pid reuse** and **exit**.
        - There is also two functions `print_tree` and `_recursive_print`. These were used to nicely view the process linkage.
        - Than we also got the function `build_dataset` that returns our vector prepared into a **dataframe** to feed to the algorithm.
            ```python
            from typing import Dict, List
            import pandas as pd
            from Utils.ProcessNode import ProcessNode


            class ProcessForest:
                def __init__(self):
                    self.active_processes: Dict[int, ProcessNode] = {}
                    self.dead_processes: List[ProcessNode] = []  # History of closed processes

            def add_event(self, event) -> ProcessNode:
                node = None

                # --- 1. HANDLE PID REUSE & EXIT ---
                if event.event_type_str == "PROCESS_EXIT":
                    # If the process exists, mark it as finished and remove from active
                    if event.pid in self.active_processes:
                        node = self.active_processes[event.pid]
                        node.add_event(event)
                        # Archive it (It's dead now)
                        self.dead_processes.append(node)
                        del self.active_processes[event.pid]
                        return node

                # --- 2. GET OR CREATE NODE ---
                if event.pid in self.active_processes:
                    # We know this process
                    node = self.active_processes[event.pid]

                    # Check for "Silent Reuse" (We missed the exit, but a new EXECVE happened)
                    # Logic: If it's an EXECVE and the comms are totally different and time gap is huge
                    # For simplicity here: We assume if it's in active, it's the same process
                    node.add_event(event)
                else:
                    # NEW PROCESS DETECTED
                    node = ProcessNode(
                        pid=event.pid,
                        ppid=event.ppid,
                        comm=event.comm,
                        start_time=event.comm_timestamp
                    )
                    node.add_event(event)
                    self.active_processes[event.pid] = node

                    # --- 3. LINK TO PARENT ---
                    # We look for the PPID in our active list
                    if event.ppid in self.active_processes:
                        parent = self.active_processes[event.ppid]
                        parent.children.append(node)
                        node.parent = parent
                    else:
                        # 3a. Check if the parent recently died but is still in history
                        parent = next((n for n in self.dead_processes if n.pid == event.ppid), None)

                        # 3b. If completely unknown, create a PHANTOM PARENT!
                        if not parent:
                            # This is valid because the comm is permissive and we can get the comm
                            # -rw-r--r--  1 stefan stefan 0 mar 30 11:26 comm
                            real_comm = "<untracked_parent>"
                            try:
                                # Try to read the process name directly from the Linux kernel
                                with open(f"/proc/{event.ppid}/comm", "r") as f:
                                    real_comm = f.read().strip()
                            except Exception:
                                # If the process already died too fast, or we don't have permission, keep the placeholder
                                pass
                            # We use ppid=0 and a placeholder name until we (hopefully) see a real event for it
                            parent = ProcessNode(
                                pid=event.ppid,
                                ppid=0,
                                comm=real_comm,
                                start_time=event.comm_timestamp
                            )
                            self.active_processes[event.ppid] = parent

                        # Link the child to the dead or phantom parent
                        parent.children.append(node)
                        node.parent = parent
                        pass

                return node

            def print_tree(self, start_pid: int):
                """
                Prints the tree starting from a specific PID (like your bash 38635)
                """
                # We search in active AND dead processes to find the root
                root = self.active_processes.get(start_pid)
                if not root:
                    # Try to find it in history
                    for n in self.dead_processes:
                        if n.pid == start_pid:
                            root = n
                            break

                if not root:
                    print(f" PID {start_pid} not found in Forest.")
                    return

                print(f"🌳 Process Tree for PID {start_pid} ({root.comm})")
                self._recursive_print(root)

            def _recursive_print(self, node: ProcessNode, depth: int = 0):
                indent = "    " * depth
                icon = "└─  " if depth > 0 else " "

                # 1. Print The Process Node
                print(f"{indent}{icon}PID: {node.pid} | Comm: {node.comm}")

                # 2. Print The Events (What did this process DO?)
                for evt in node.events:
                    # Formatting timestamp
                    ts = "Unknown"
                    try:
                        # Assuming nanoseconds string
                        ts = pd.to_datetime(int(evt.comm_timestamp), unit='ns').strftime('%H:%M:%S')
                    except:
                        pass

                    # Formatting detail (Filename or Socket IP)
                    detail = ""
                    if evt.filename and evt.filename != "void":
                        detail = f"File: {evt.filename}"
                    elif evt.ipv4 and evt.ipv4 != "0.0.0.0":
                        detail = f"Net: {evt.ipv4}"

                    arrow = "  🔹"
                    if "EXECVE" in evt.event_type_str: arrow = "  "
                    if "EXIT" in evt.event_type_str: arrow = "  "
                    if "SOCKET" in evt.event_type_str: arrow = "  "
                    if "OPEN" in evt.event_type_str: arrow = "  "
                    if "AUTH" in evt.event_type_str: arrow = "  "

                    print(f"{indent}    {arrow} [{ts}] {evt.event_type_str} {detail}")

                # 3. Recurse to Children
                for child in node.children:
                    self._recursive_print(child, depth + 1)

            def build_dataset(self):
                rows = []

                all_nodes = (
                        list(self.active_processes.values())
                        + self.dead_processes
                )

                for node in all_nodes:
                    vector = node.get_aggregated_vector()
                    rows.append(vector)

                return pd.DataFrame(rows)

            ```
- ### II. Machine Learning Algorithm
    - Now we will talk about the **ML algorithms** that I used, data preparation, results and more and more.
    - Let's take a look into the `dataEngineering.py`. In this file we prepare the data to feed into the algorithm. How we prepare it ?
    - We prepare the **directories** required and we **label** the data. What is in the file `general_logs_cleaned_scores` is `benign` only. The rest of the dataset is `suspicious`. Than at the end, we prepare a final dataset composed of total of **155 benign entries** and **1011 suspicious entires** having a total of **1166** entries.
        ```python
        # Setup Directories
        modelsPath = os.path.join(cwd, "ML_Models")
        plotsPath = os.path.join(cwd, "Plots")
        predictionsPath = os.path.join(cwd, "Predictions")
        trainingPath = os.path.join(cwd, "ScoresAssignedCSV/finalDfTraining")
        dirs = [modelsPath, plotsPath, predictionsPath, trainingPath]

        for createDir in dirs:
            os.makedirs(createDir, exist_ok=True)

        # ==========================================
        # 1. LOAD AND LABEL DATA
        # ==========================================
        dataframes = []
        for script in sorted(os.listdir(raw_csv_path)):
            script_path = os.path.join(raw_csv_path, script)
            if os.path.isfile(script_path):
                df = pd.read_csv(script_path)

                # Labeling
                if "general_logs_cleaned_scores" in script:
                    df["label"] = "benign"
                else:
                    df["label"] = "suspicious"

                dataframes.append(df)

        # Combine ALL data BEFORE applying TF-IDF
        finalDf = pd.concat(dataframes, ignore_index=True)

        ```
    - In the next step, we apply the `TF-IDF` for our **command_chain** so that our algorithm can learn how to understand the **command_chain** and how to use it as a metric, a very important one. We then save the `.csv`.
        ```python
        # ==========================================
        # 2. APPLY TF-IDF GLOBALLY
        # ==========================================
        # Replace NaNs with empty string to prevent crashes
        finalDf['command_chain'] = finalDf['command_chain'].fillna("")

        vectorizer = TfidfVectorizer(max_features=20)
        chain_features = vectorizer.fit_transform(finalDf['command_chain']).toarray()
        joblib.dump(vectorizer, os.path.join(modelsPath, "tfidf_vectorizer.joblib"))
        chain_df = pd.DataFrame(chain_features, columns=[f"chain_{w}" for w in vectorizer.get_feature_names_out()])

        # Combine features and drop the raw text columns
        finalDf = pd.concat([finalDf, chain_df], axis=1)
        finalDf = finalDf.drop(columns=['command_chain'])  # Drop comm too if it's still text

        # Save the final training dataset
        finalDf.to_csv(os.path.join(trainingPath, "finalDfTraining.csv"), index=False)
        ```
    - Data preparation was made usng the **train_test_split**. We also use an encode to enchode our **benign** and **suspicious** labels.
        ```python
        random_state = 90
        X = finalDf.drop(columns=['label'])
        y = finalDf['label']

        # encoding
        encoder = LabelEncoder()
        y = encoder.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
        ```
    - The functions that we'll return our metrics , simple one. Just plotting all the required metrics to evaluate the models
        ```python
        # ==========================================
        # 3. GET METRICS FUNCTION
        # ==========================================
        def getMetrics(model, X_testF, y_testF, model_name, plots_dir):
            print(f"\n--- Generating Metrics for {model_name} ---")
            predictions = model.predict(X_testF)

            # 1. Calculate Metrics
            metrics_data = {
                "Accuracy": accuracy_score(y_testF, predictions),
                "Recall": recall_score(y_testF, predictions, average='macro', zero_division=0),
                "Precision": precision_score(y_testF, predictions, average='macro', zero_division=0),
                "F1 Score": f1_score(y_testF, predictions, average='macro', zero_division=0)
            }

            # 2. Plot & Save Metrics Table
            metrics_df = pd.DataFrame(list(metrics_data.items()), columns=['Metric', 'Score'])
            metrics_df['Score'] = metrics_df['Score'].apply(lambda x: f"{x:.4f}")

            fig, ax = plt.subplots(figsize=(6, 3))
            ax.axis('off')
            table = ax.table(cellText=metrics_df.values, colLabels=metrics_df.columns, loc='center', cellLoc='center')
            table.scale(1, 2.5)
            table.set_fontsize(12)
            for (row, col), cell in table.get_celld().items():
                if row == 0: cell.set_text_props(weight='bold')
            plt.title(f'{model_name} Performance', pad=20, fontsize=14, fontweight='bold')
            plt.savefig(os.path.join(plots_dir, f"{model_name}_metrics.png"), dpi=300, bbox_inches='tight')
            plt.close()

            # 3. Plot & Save Confusion Matrix
            cm = confusion_matrix(y_testF, predictions, labels=[0, 1])
            plt.figure(figsize=(6, 5))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                        xticklabels=["benign", "suspicious"],
                        yticklabels=["benign", "suspicious"])
            plt.title(f'{model_name} Confusion Matrix', pad=15, fontsize=14, fontweight='bold')
            plt.xlabel('Predicted', fontweight='bold')
            plt.ylabel('Actual Truth', fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, f"{model_name}_confusion_matrix.png"), dpi=300, bbox_inches='tight')
            plt.close()

            # 4. Plot & Save Precision-Recall Curve
            if hasattr(model, "predict_proba"):
                pos_class_idx = list(model.classes_).index(1)
                y_probs = model.predict_proba(X_testF)[:, pos_class_idx]

                precision, recall, thresholds = precision_recall_curve(y_testF, y_probs, pos_label=1)
                pr_auc = auc(recall, precision)

                plt.figure(figsize=(8, 6))
                plt.plot(recall, precision, color='purple', lw=2, label=f'PR curve (AUC = {pr_auc:.4f})')

                # Baseline is the ratio of positive instances
                baseline = sum(y_testF) / len(y_testF)
                plt.plot([0, 1], [baseline, baseline], color='navy', lw=2, linestyle='--',
                        label=f'Baseline ({baseline:.2f})')

                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('Recall (True Positive Rate)', fontweight='bold')
                plt.ylabel('Precision (Positive Predictive Value)', fontweight='bold')
                plt.title(f'{model_name} Precision-Recall Curve', pad=15, fontsize=14, fontweight='bold')
                plt.legend(loc="lower left")
                plt.grid(alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(plots_dir, f"{model_name}_pr_curve.png"), dpi=300, bbox_inches='tight')
                plt.close()

            # 5. Plot Feature Importance
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                fi_df = pd.DataFrame({'Feature': X_testF.columns, 'Importance': importances})
                fi_df = fi_df.sort_values(by='Importance', ascending=False).head(20)  # Keeping it to top 20 for readability

                plt.figure(figsize=(10, 6))
                sns.barplot(x='Importance', y='Feature', data=fi_df, palette='viridis')
                plt.title(f'{model_name} 20 Important Features')
                plt.xlabel('Importance Score')
                plt.ylabel('Feature')
                plt.tight_layout()
                plt.savefig(os.path.join(plots_dir, f"{model_name}_feature_importance.png"), dpi=300, bbox_inches='tight')
                plt.close()

            # 6. Plot & Save ROC Curve and AUC
            if hasattr(model, "predict_proba"):
                pos_class_idx = list(model.classes_).index(1)
                y_probs = model.predict_proba(X_testF)[:, pos_class_idx]

                fpr, tpr, thresholds = roc_curve(y_testF, y_probs, pos_label=1)
                roc_auc = auc(fpr, tpr)

                plt.figure(figsize=(8, 6))
                plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
                plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('False Positive Rate', fontweight='bold')
                plt.ylabel('True Positive Rate', fontweight='bold')
                plt.title(f'{model_name} ROC Curve', pad=15, fontsize=14, fontweight='bold')
                plt.legend(loc="lower right")
                plt.grid(alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(plots_dir, f"{model_name}_roc_curve.png"), dpi=300, bbox_inches='tight')
                plt.close()

            print(f"All plots for {model_name} saved in {plots_dir}")
        ```
    ##### I. RandomForest 
    - For the first model, I used RandomForest. Based on decision trees, it can have a veey good way to predict and work on classification tasks, especially binary ones.
    - I choose a balanced number for the estimators , `500` and than we saved the model. We'll discuss about the `getMetrics` function in a bit.
        ```python
        # Train Random Forest
        print("Training Random Forest...")
        randomForestName = "RandomForest"
        rfModel = RandomForestClassifier(n_estimators=500, random_state=random_state, class_weight='balanced', n_jobs=-1)
        rfModel.fit(X_train, y_train)

        #save model
        joblib.dump(rfModel, os.path.join(modelsPath, f"{randomForestName}_model.joblib"))
        getMetrics(model=rfModel, X_testF=X_test, y_testF=y_test, model_name=randomForestName, plots_dir=plotsPath)
        ```
    ##### II. XGBoost
    - For the second model, I used XGBoost. Like **RandomForest** based on decision trees, but here the trees (shallow trees) are built **sequentially** to reduce the bias. RandomForest builds them in **parallel, multiple and INDEPENDENT** trees.
        - I used a **RandomizedSearchCV** because I did not have that much power to train, but still got some powerfull metrics. Just like on **RandomForest**, we save the model and proceed.
    - Let's take a look at the code:
        ```python
        print("Training XGBoost...")
        XGBoostName = "XGBoost"
        param_grid = {
            'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2],
            'max_depth': [3, 5, 7, 10],
            'gamma': [0, 0.1, 0.2],
            'subsample': [0.5, 0.7, 0.8],
            'colsample_bytree': [0.5, 0.7, 0.8],
            'scale_pos_weight': [1] # classes are pretty imbalanced
        }

        # 2. Initialize the base model
        xgb_model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            n_estimators=500  # You can adjust the number of trees
        )

        # 3. Set up the Grid Search with Cross Validation
        # cv=5 means 5-fold cross-validation
        random_search = RandomizedSearchCV(
            estimator=xgb_model,
            param_distributions=param_grid,
            n_iter=50,
            scoring='roc_auc',
            cv=5,
            n_jobs=-1,
            verbose=1,
            random_state=random_state
        )

        print(f"Training {XGBoostName} and searching for best parameters...")
        # Assuming you have your training data ready as X_train and y_train
        random_search.fit(X_train, y_train)

        # 4. Extract the best model and print results
        print("Best parameters found: ", random_search.best_params_)
        print("Best CV score: ", random_search.best_score_)

        best_model = random_search.best_estimator_

        # 5. Save the best model XGBOOST
        # Best
        # parameters
        # found: {'subsample': 0.8, 'scale_pos_weight': 1, 'max_depth': 7, 'learning_rate': 0.1, 'gamma': 0.1,
        #         'colsample_bytree': 0.7}
        model_filename = f"{XGBoostName}_model.json"
        best_model.save_model(os.path.join(modelsPath, f"{model_filename}"))
        print(f"Best model saved successfully as {model_filename}")

        getMetrics(best_model,X_testF=X_test, y_testF=y_test, model_name=XGBoostName, plots_dir=plotsPath)
        ```
    ##### III. Results
    - The metrics I choose were the classic ones, for both the algorithms. 
        - `confusion_matrix`
        - `feature_importance`
        - `precision`, `recall`, `accuaracy`, `f1 score`
        - `precision-recall curve`
        - `roc curve`
    - The images will be put in the same order as **ABOVE**.
    - `RandomForest`
        ![confusion_matrix](/Plots/RandomForest_confusion_matrix.png)
        ![feature_importance](/Plots/RandomForest_feature_importance.png)
        ![metrics](/Plots/RandomForest_metrics.png)
        ![pr_curve](/Plots/RandomForest_pr_curve.png)
        ![roc_curve](/Plots/RandomForest_roc_curve.png)
    - `XGBoost`
        ![confusion_matrix](/Plots/XGBoost_confusion_matrix.png)
        ![feature_importance](/Plots/XGBoost_feature_importance.png)
        ![metrics](/Plots/XGBoost_metrics.png)
        ![pr_curve](/Plots/XGBoost_pr_curve.png)
        ![roc_curve](/Plots/XGBoost_roc_curve.png)
            
    - ### III. Drawbacks
        - **_Small dataset_**. Hence I used a very small dataset, around 1200 entries, very few **benign** entries also, and also applying the **TF-IDF**, if there are some new commands entered, the algorithm will not know and predict bad. If I will gather a bigger dataset or if you do , you can retrain !
        - Not an expert in ML engineering. Those were the metrics that I considered useful for this task. Of course , they can be fine-tuned more, but this was all I got.
    
    - ### IV. Real-time-detection branch
      - There is a branch called `real_time_detection`. This is the branch that was used for the real-time-detection all together program along with the interface.
      - It includes only the `ML_Models`, `Models`, and `Utils`, all that is needed for the detection. This branch will be cloned on the main repository which links them all together.
