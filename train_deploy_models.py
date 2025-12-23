import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
MODELS_DIR = os.path.join(BASE_PATH, "models")
REPORT_FILE = os.path.join(MODELS_DIR, "training_report.txt")

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

DATASETS = [
    {"name": "YOUSEF", "path": r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv", "target": "label", "detail_col": "attack_type", "type": "OCPP_Security"},
    {"name": "SUZAN", "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv", "target": "label", "detail_col": "reason", "type": "Energy_Fraud"},
    {"name": "MİRAÇ", "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv", "target": "label", "detail_col": "reason", "type": "Registration_Anomaly"},
    {"name": "İREM", "path": r"Raporlar\İREM_BSG\network_traffic_features.csv", "target": "label", "detail_col": "label", "type": "CAN_Bus_Network"},
    {"name": "EMİRHAN", "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv", "target": "label", "detail_col": "message", "type": "K8s_Security"},
    {"name": "SAMET", "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv", "target": "label", "detail_col": "detail", "type": "IDS_IPS"},
    {"name": "EMİRHNT", "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv", "target": "label", "detail_col": None, "type": "Time_Drift_Billing"},
    {"name": "İBRAHİM", "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv", "target": "label", "detail_col": "attack_type", "type": "System_Time_Anomaly"},
    {"name": "ATAKAN", "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv", "target": "label", "detail_col": "attack_type", "type": "Load_Manipulation"},
]

def train_model(ds):
    full_path = os.path.join(BASE_PATH, ds['path'])
    model_path = os.path.join(MODELS_DIR, f"rf_model_{ds['name']}.joblib")
    encoder_path = os.path.join(MODELS_DIR, f"encoders_{ds['name']}.joblib")
    
    result_log = ""
    
    if not os.path.exists(full_path):
        return f"ERROR: File not found {full_path}"

    try:
        df = pd.read_csv(full_path)
        
        # 1. Prepare Target (y)
        # We want to predict not just 0/1 but the specific Type if possible for explanation
        # But some datasets only have 0/1 label reliably.
        # Strategy: Train on 'label' (Binary) for high accuracy detection.
        # Explanation logic can be derived from features or a secondary lookup.
        # User asked for accuracy, so Binary Classification is safest for the core model.
        
        y = df[ds['target']]
        X = df.drop(columns=[ds['target']])
        
        # Determine if we can do multi-class (Attack Type) prediction?
        # If detail_col exists and has more than 1 class, let's try to encode IT as target?
        # NO, user wants detection first. Let's stick to Binary Random Forest for robustness.
        # But identifying "Hangi Sorun" implies we need the detail.
        # Let's Encode features first.
        
        le_dict = {}
        
        # Handle Target Encoding if it's string (like 'pivot', 'normal')
        target_encoder = LabelEncoder()
        if y.dtype == 'object':
             y = target_encoder.fit_transform(y.astype(str))
             le_dict['target_label'] = target_encoder

        # Preprocess Features (X)
        X_encoded = X.copy()
        drop_cols = []
        
        for col in X_encoded.columns:
            if X_encoded[col].dtype == 'object':
                if X_encoded[col].nunique() > 1000:
                    # Too many unique values (e.g. detailed timestamps, unique IDs), likely noise for RF
                    drop_cols.append(col)
                else:
                    le = LabelEncoder()
                    X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
                    le_dict[col] = le
            else:
                 X_encoded[col] = X_encoded[col].fillna(0)

        if drop_cols:
            X_encoded = X_encoded.drop(columns=drop_cols)
            result_log += f"  - Dropped High-Cardinality Cols: {drop_cols}\n"

        # Split
        X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        # Evaluate
        y_pred = rf.predict(X_test)
        report = classification_report(y_test, y_pred)
        
        # Save Artifacts
        joblib.dump(rf, model_path)
        joblib.dump(le_dict, encoder_path)
        
        result_log += f"  - Model Saved: {model_path}\n"
        result_log += f"  - Accuracy: {rf.score(X_test, y_test):.4f}\n"
        result_log += f"  - Classification Report:\n{report}\n"
        
        return result_log

    except Exception as e:
        return f"CRITICAL ERROR: {e}"

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("TRAINING REPORT: RANDOM FOREST MODELS\n")
    f.write("=====================================\n\n")
    
    for ds in DATASETS:
        f.write(f"TRAINING MODEL FOR: {ds['name']} ({ds['type']})\n")
        f.write("-" * 50 + "\n")
        log = train_model(ds)
        f.write(log + "\n\n")

print(f"Training complete. Report saved at {REPORT_FILE}")
