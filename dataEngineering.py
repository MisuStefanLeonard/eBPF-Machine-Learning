import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score, recall_score, precision_score, confusion_matrix, f1_score, roc_curve,auc, precision_recall_curve
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

cwd = os.getcwd()
raw_csv_path = os.path.join(cwd, "ScoresAssignedCSV")
try:
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

    print("Am ajuns aici primul")

    # Combine ALL data BEFORE applying TF-IDF
    finalDf = pd.concat(dataframes, ignore_index=True)

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
    print("Am ajuns aici ")


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

        print(f"✅ All plots for {model_name} saved in {plots_dir}")

    # ==========================================
    # 4. TRAIN ALGORITHM & CALL METRICS
    # ==========================================
    random_state = 90
    X = finalDf.drop(columns=['label'])
    y = finalDf['label']

    # encoding
    encoder = LabelEncoder()
    y = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

    # Train Random Forest
    print("Training Random Forest...")
    randomForestName = "RandomForest"
    rfModel = RandomForestClassifier(n_estimators=500, random_state=random_state, class_weight='balanced', n_jobs=-1)
    rfModel.fit(X_train, y_train)

    #save model
    joblib.dump(rfModel, os.path.join(modelsPath, f"{randomForestName}_model.joblib"))
    getMetrics(model=rfModel, X_testF=X_test, y_testF=y_test, model_name=randomForestName, plots_dir=plotsPath)

    # Train XGBoost
    print("Training XGBoost...")
    XGBoostName = "XGBoost"
    param_grid = {
        'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2],
        'max_depth': [3, 5, 7, 10],
        'gamma': [0, 0.1, 0.2],
        'subsample': [0.5, 0.7, 0.8],
        'colsample_bytree': [0.5, 0.7, 0.8],
        'scale_pos_weight': [1]  # Adjust this if your classes are highly imbalanced
    }

    # 2. Initialize the base model
    # Use XGBRegressor instead if you are predicting continuous numbers
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



except Exception as e:
    print(e)