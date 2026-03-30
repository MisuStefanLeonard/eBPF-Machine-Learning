# ML training 

# TOC

- [Prerequisites](#disclaimer)
- [Language](#language)
- [Installation](#i-installation)

### DISCLAIMER
- Prefferably use `python 3.13` since the project was made with this
- Prefferably you're sitting on ubuntu 24.04
- Please go check [eBPF_log_collector](https://github.com/MisuStefanLeonard/eBPF_log_collector) first then continue with this repo

### LANGUAGE
- **first part** = [eBPF_log_collector](https://github.com/MisuStefanLeonard/eBPF_log_collector)

```bash
cat /etc/lsb-release

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.4 LTS"

uname -a

Linux stefan-Latitude-7480 6.8.0-106-generic #106-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 07:58:08 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux


```
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
#### Create the list file `/etc/apt/sources.list.d/mongodb-org-8.2.list` for your version of Ubuntu.

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
                          - A lot of scanning on the system (e.g touching sensitive files from `/etc/ , /var/ , etc`)
                          - 


























