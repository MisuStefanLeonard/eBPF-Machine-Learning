import json
import os
import struct
import subprocess
import time
from typing import Union
import joblib
import pandas as pd
import redis
import xgboost
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier

from Models.Event import Event
from Utils.ProcessForest import ProcessForest
from Utils.ProcessNode import ProcessNode

cwd = os.getcwd()
scripts_dir_path = os.path.join(cwd,f"gatheredCsv/scripts_results")

mlModels = os.path.join(cwd, "ML_Models")
randomForestModelPath = os.path.join(mlModels, "RandomForest_model.joblib")
xgBoostModelPath = os.path.join(mlModels, "XGBoost_model.json")
vectorizerPath =  os.path.join(mlModels, "tfidf_vectorizer.joblib")
pinned_map_path = "/sys/fs/bpf/self_pid_map"
# models loading and tfidf vectorizer
xgBoostModel = xgboost.XGBClassifier()
xgBoostModel.load_model(xgBoostModelPath)
randomForestModel:RandomForestClassifier = joblib.load(randomForestModelPath)
vectorizer:TfidfVectorizer(max_features=20) = joblib.load(vectorizerPath)
scripts_files_csv = os.listdir(scripts_dir_path)
pd.set_option('display.max_columns', None)

STREAM_KEY = "file_events"
process_forest_rt = ProcessForest()
event_rt = None

def tryOnCsv(csv):
    df = pd.read_csv(csv, keep_default_na=False)
    process_forest = ProcessForest()
    records = df.to_dict(orient='records')
    events = [Event.from_dict(event) for event in records]
    for event in events:
        process_forest.add_event(event)

    for pid,node in process_forest.active_processes.items():
        process_forest.print_tree(pid)

    return process_forest

def buildForestAndPredictRT(currentNode:ProcessNode,
                            model:Union[RandomForestClassifier,XGBClassifier]
                            ,model_name:str ,
                            commChainVectorizer:TfidfVectorizer):
    try:
        print(f"PREDICTING WITH {model_name}")
        nodeVector = currentNode.get_aggregated_vector()
        df = pd.DataFrame([nodeVector])
        command_chain_str = df['command_chain'].fillna("").values[0]
        chain_features = vectorizer.transform([command_chain_str]).toarray()
        chain_df = pd.DataFrame(chain_features, columns=[f"chain_{w}" for w in commChainVectorizer.get_feature_names_out()])
        final_df = pd.concat([df.reset_index(drop=True), chain_df.reset_index(drop=True)], axis=1)
        if 'command_chain' in final_df.columns:
            final_df = final_df.drop(columns=['command_chain'])

        prediction = model.predict(final_df)[0]

        if prediction == 1:
            probabilities = model.predict_proba(final_df)[0]
            confidence = probabilities[1] * 100
            print(
                f"🚨 [MALICIOUS DETECTED] PID: {currentNode.pid} | Conf: {confidence:.1f}% | Comm: {currentNode.comm} | Chain: {command_chain_str}")
        else:
            print(f"✅ [Benign] PID {currentNode.pid} ({currentNode.comm}) finished cleanly.")

    except Exception as e:
        print(f"❌ Error evaluating PID {currentNode.pid}: {e}")

def injectPythonPidIntoBpfMap():
    currentPid = os.getpid()
    key_hex = " ".join(f"0x{b:02x}" for b in struct.pack("<I", 1))
    val_hex = " ".join(f"0x{b:02x}" for b in struct.pack("<I", currentPid))

    cmd = f"sudo bpftool map update pinned {pinned_map_path} key {key_hex} value {val_hex}"
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Successfully injected Python PID ({currentPid}) using bpftool!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to update map via bpftool: {e.stderr.decode().strip()}")

# if __name__ == "__main__":
#     for file in scripts_files_csv:
#         print("*******************************")
#         print("*******************************")
#         print(f"***** {file} ******")
#         print("*******************************")
#         print("*******************************")
#
#         currentCsvPath = os.path.join(scripts_dir_path, file)
#         processForest = tryOnCsv(currentCsvPath)
#         df_built = processForest.build_dataset()
#         name_scores = f"{file.split(".")[0]}_scores.csv"
#         df_built.to_csv(f"ScoresAssignedCSV/{name_scores}", index=False)

if __name__ == "__main__":
    redisClient = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, protocol=3)
    last_id = "$"
    print(f"Listening for events on stream: {STREAM_KEY}...")

    ##
    SWEEP_INTERVAL = 20
    STALE_TIMEOUT = 50
    last_sweep_time = time.time()
    pidLastSeen = {}

    # Injects the python program pid into the eBPF program
    injectPythonPidIntoBpfMap()
    ##
    def get_root_node(current_node):
        root = current_node
        while root.parent is not None:
            root = root.parent
        return root

    while True:
        try:
            # streams = redisClient.xread({STREAM_KEY : last_id}, count=1, block=0)
            streams = redisClient.xread({STREAM_KEY : last_id}, count=100, block=1000) # type: ignore

            if streams:
                # noinspection PyTypeChecker
                for stream_name,messages in streams.items():
                    if isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], list):
                        current_messages = messages[0]  # Unwrap the outer list
                    else:
                        current_messages = messages

                    for message_id,data in current_messages:
                        # Update last id
                        last_id = message_id
                        if 'data' in data:
                            raw_json = data['data']
                            try:
                                event_json = json.loads(raw_json)
                                evt = Event.from_dict(event_json)

                                ##
                                pidLastSeen[evt.pid] = time.time()

                                # Add the node to the process_forest
                                node = process_forest_rt.add_event(evt)

                                if evt.event_type_str == "PROCESS_EXIT":
                                    root_node = get_root_node(node)

                                    # 🚨 FIX 2: Evaluate the whole tree from the top down!
                                    buildForestAndPredictRT(root_node, xgBoostModel, "XGBoost", vectorizer)
                                    buildForestAndPredictRT(root_node, randomForestModel, "RandomForest", vectorizer)

                                    # 🚨 FIX 3: DO NOT remove from dead_processes!
                                    # We just clean up the timestamp tracker to save memory.
                                    if evt.pid in pidLastSeen:
                                        del pidLastSeen[evt.pid]


                            except json.JSONDecodeError:
                                print(f"Error: Invalid JSON in message {message_id}")

            ##
            currentTime = time.time()
            if currentTime - last_sweep_time > SWEEP_INTERVAL:

                # We use a set to store the PIDs of the roots, because PIDs are integers (hashable!)
                root_pids_to_evaluate = set()
                # We also keep a temporary dictionary so we can look up the root node using its PID later
                root_nodes_map = {}

                for pid in list(process_forest_rt.active_processes.keys()):
                    node = process_forest_rt.active_processes[pid]
                    last_seen = pidLastSeen.get(pid, currentTime)

                    # Scenario A: Stale Cleanup
                    if currentTime - last_seen > STALE_TIMEOUT:
                        print(f"🧹 [CLEANUP] PID {pid} is stale. Removing...")

                        # Find the root
                        root = get_root_node(node)

                        # Add the PID to the set, and save the actual node in our map
                        root_pids_to_evaluate.add(root.pid)
                        root_nodes_map[root.pid] = root

                        # Remove the stale child from memory
                        del process_forest_rt.active_processes[pid]
                        if pid in pidLastSeen:
                            del pidLastSeen[pid]

                    # Scenario B: Active Long-Running
                    else:
                        pass

                # Loop through the unique root PIDs and evaluate them!
                for root_pid in root_pids_to_evaluate:
                    root_node = root_nodes_map[root_pid]
                    buildForestAndPredictRT(root_node, xgBoostModel, "XGBoost", vectorizer)
                    buildForestAndPredictRT(root_node, randomForestModel, "RandomForest", vectorizer)

                last_sweep_time = time.time()
        except KeyboardInterrupt:
            print("Stopping...")
            break
        except redis.ConnectionError:
            print("Redis connection lost, retrying...")


