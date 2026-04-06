import os
import struct
import subprocess
from typing import Union

import joblib
import pandas as pd
import xgboost
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from predictionAlgorithm.Utils import ProcessNode
from predictionAlgorithm.Utils.ProcessForest import ProcessForest
from predictionAlgorithm.ClassModels.Event import Event
from predictionAlgorithm.Utils.constants import network_tools, target_devices

pinned_map_path = "/sys/fs/bpf/self_pid_map"
process_forest_rt = ProcessForest()
cwd = os.getcwd()
cwdML = os.path.join(cwd, "predictionAlgorithm")

# paths
mlModels = os.path.join(cwdML, "MLModels")
randomForestModelPath = os.path.join(mlModels, "RandomForest_model.joblib")
xgBoostModelPath = os.path.join(mlModels, "XGBoost_model.json")
vectorizerPath =  os.path.join(mlModels, "tfidf_vectorizer.joblib")


# models loading
xgBoostModel = xgboost.XGBClassifier()
xgBoostModel.load_model(xgBoostModelPath)
randomForestModel:RandomForestClassifier = joblib.load(randomForestModelPath)
# vectorizer:TfidfVectorizer(max_features=20) = joblib.load(vectorizerPath)
vectorizer: TfidfVectorizer = joblib.load(vectorizerPath)
MAX_ARGS_CAPTURED = 8
MAX_ARGV_LEN = 64
MAX_CHAR_LEN = 256
TYPE = 16
UNIX_PATH_MAX = 108
MAX_BUFFER_SIZE = 512


def get_root_node(current_node):
    root = current_node
    while root.parent is not None:
        root = root.parent
    return root


def injectPythonPidIntoBpfMap():
    currentPid = os.getpid()

    script_path = os.path.join(os.getcwd(), "predictionAlgorithm/Utils/injectPidIntoMap.sh")

    cmd = f"sudo {script_path} {currentPid}"

    try:
        subprocess.run(cmd.split(), check=True, capture_output=True, text=True)
        print(f" Successfully injected Python PID ({currentPid}) via bash script!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update map via script: {e.stderr.strip()}")

def buildForestAndPredictRT(currentNode: ProcessNode,
                            model: Union[RandomForestClassifier, XGBClassifier],
                            model_name: str,
                            commChainVectorizer: TfidfVectorizer):
    try:
        nodeVector = currentNode.get_aggregated_vector()
        df = pd.DataFrame([nodeVector])
        command_chain_str = df['command_chain'].fillna("").values[0]
        chain_features = vectorizer.transform([command_chain_str]).toarray()
        chain_df = pd.DataFrame(chain_features,
                                columns=[f"chain_{w}" for w in commChainVectorizer.get_feature_names_out()])
        final_df = pd.concat([df.reset_index(drop=True), chain_df.reset_index(drop=True)], axis=1)

        if 'command_chain' in final_df.columns:
            final_df = final_df.drop(columns=['command_chain'])

        prediction = model.predict(final_df)[0]
        probabilities = model.predict_proba(final_df)[0]
        confidence = probabilities[prediction] * 100

        # Get the root node to provide a consistent ID for the chain
        root_node = get_root_node(currentNode)

        # Return data for BOTH benign and malicious
        return {
            "root_pid": root_node.pid,
            "root_start": root_node.start_time,
            "pid": currentNode.pid,
            "comm": currentNode.comm,
            "confidence": f"{confidence:.1f}%",
            "model_name": model_name,
            "command_chain": command_chain_str,
            "is_malicious": bool(prediction == 1)  # Boolean flag for frontend
        }

    except Exception as e:
        print(f" Error evaluating PID {currentNode.pid}: {e}")