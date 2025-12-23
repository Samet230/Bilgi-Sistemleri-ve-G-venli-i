import pandas as pd
import numpy as np
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
OUTPUT_FILE = os.path.join(BASE_PATH, "ml_benchmark_results.txt")

# Define datasets and their target columns
# We will use 'label' as the primary binary target for detection,
# but we will also try to predict 'attack_type' (multi-class) if available for explanation.
DATASETS = [
    {"name": "YOUSEF", "path": r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv", "target": "label", "detail_col": "attack_type"},
    {"name": "SUZAN", "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv", "target": "label", "detail_col": "reason"},
    {"name": "MİRAÇ", "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv", "target": "label", "detail_col": "reason"},
    {"name": "İREM", "path": r"Raporlar\İREM_BSG\network_traffic_features.csv", "target": "label", "detail_col": "label"}, # label is the type here
    {"name": "EMİRHAN", "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv", "target": "label", "detail_col": "message"},
    {"name": "SAMET", "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv", "target": "label", "detail_col": "detail"},
    {"name": "EMİRHNT", "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv", "target": "label", "detail_col": None},
    {"name": "İBRAHİM", "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv", "target": "label", "detail_col": "attack_type"},
    {"name": "ATAKAN", "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv", "target": "label", "detail_col": "attack_type"},
]

MODELS = {
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
}

def preprocess_and_train(df_path, name, target_col):
    full_path = os.path.join(BASE_PATH, df_path)
    if not os.path.exists(full_path):
        return f"FILE NOT FOUND: {full_path}"

    try:
        df = pd.read_csv(full_path)
        
        # Check target
        if target_col not in df.columns:
            return f"Target '{target_col}' not found."

        # Drop non-feature columns (like timestamps if not processed)
        # For simplicity in this benchmark, we drop timestamp and string columns that are too unique
        # We will LabelEncode categorical columns
        
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Preprocessing
        le = LabelEncoder()
        
        # Handle string targets (like 'normal', 'pivot' in IREM)
        # Verify if y is numeric
        if y.dtype == 'object':
            y = le.fit_transform(y.astype(str))
            
        # Process Features
        # Drop columns with too many unique values (IDs, Timestamps) as they cause overfitting/noise
        for col in X.columns:
            if X[col].dtype == 'object':
                if X[col].nunique() > 500: # Drop high cardinality
                    X = X.drop(columns=[col])
                else:
                    X[col] = le.fit_transform(X[col].astype(str))
            else:
                X[col] = X[col].fillna(0) # Fill numeric NaNs

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        results = {}
        for model_name, model in MODELS.items():
            start_time = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start_time
            
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            results[model_name] = {
                "Accuracy": acc,
                "F1": f1,
                "Time": train_time
            }
            
        return results

    except Exception as e:
        return f"ERROR: {e}"

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("ML MODEL BENCHMARK REPORT\n")
    f.write("=========================\n\n")

    overall_scores = {m: {"acc": [], "time": []} for m in MODELS}

    for ds in DATASETS:
        f.write(f"DATASET: {ds['name']}\n")
        f.write("-" * 20 + "\n")
        
        res = preprocess_and_train(ds['path'], ds['name'], ds['target'])
        
        if isinstance(res, str):
            f.write(f"  -> {res}\n\n")
            continue
            
        best_model = None
        best_score = -1
        
        for m_name, metrics in res.items():
            f.write(f"  -> {m_name:<20} | Acc: {metrics['Accuracy']:.4f} | F1: {metrics['F1']:.4f} | Time: {metrics['Time']:.4f}s\n")
            
            # Aggregate for overall winner
            overall_scores[m_name]["acc"].append(metrics['Accuracy'])
            overall_scores[m_name]["time"].append(metrics['Time'])
            
            if metrics['Accuracy'] > best_score:
                best_score = metrics['Accuracy']
                best_model = m_name
        
        f.write(f"  🏆 WINNER for {ds['name']}: {best_model}\n\n")

    f.write("OVERALL SUMMARY\n")
    f.write("===============\n")
    for m_name, stats in overall_scores.items():
        if stats["acc"]:
            avg_acc = np.mean(stats["acc"])
            avg_time = np.mean(stats["time"])
            f.write(f"{m_name:<20} | Avg Acc: {avg_acc:.4f} | Avg Time: {avg_time:.4f}s\n")

print(f"Benchmark complete. Results saved to {OUTPUT_FILE}")
