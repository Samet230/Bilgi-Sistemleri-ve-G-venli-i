import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.metrics import classification_report
from sklearn.impute import SimpleImputer

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
MODELS_DIR = os.path.join(BASE_PATH, "models") # Overwrite current models (backup is is v1)
REPORT_FILE = os.path.join(MODELS_DIR, "training_report_nlp.txt")

# Define features for each dataset
# text_cols: columns to be joined and TF-IDF'd
# num_cols: columns to be passed through/scaled
DATASETS = [
    {
        "name": "YOUSEF", 
        "path": r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv", 
        "target": "label",
        # Leakage Removal: status='Faulted' is a result. event_type='Security' might be ok but 'attack_type' is target.
        # Strict Mode: Use only 'ocpp_message' and time. 
        "features_text": ["ocpp_message"],
        "features_num": ["time_delta_ms"]
    },
    {
        "name": "SAMET",
        "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv",
        "target": "label",
        # Leakage Removal: action='Bloklandı', level='SALDIRI' are results.
        # Use only 'detail'.
        "features_text": ["detail"],
        "features_num": []
    },
    {
        "name": "EMİRHAN",
        "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv",
        "target": "label",
        # Leakage Removal: action, rule_id give it away.
        # Use only 'message'.
        "features_text": ["message"],
        "features_num": []
    },
    {
        "name": "ATAKAN",
        "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv",
        "target": "label",
        "features_text": [],
        "features_num": ["load_kw"]
    },
    {
        "name": "İBRAHİM",
        "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv",
        "target": "label",
        # Leakage Removal: Use only 'detail'.
        "features_text": ["detail"],
        "features_num": []
    },
    {
        "name": "SUZAN",
        "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv",
        "target": "label",
        # Leakage Removal: status='Suspicious' is leakage.
        "features_text": ["ocpp_message"],
        "features_num": ["price_eur_kwh", "energy_kwh", "power_kw"]
    },
    {
        "name": "İREM",
        "path": r"Raporlar\İREM_BSG\network_traffic_features.csv",
        "target": "label",
        # Irem is mostly numeric features
        "features_text": [], 
        "features_num": ["length", "protocol_ip", "protocol_tcp", "protocol_udp", "protocol_can", "can_id_anomaly"] # Assuming these represent the features
    },
    {
        "name": "EMİRHNT",
        "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv",
        "target": "label",
        "features_text": ["Durum"],
        "features_num": ["Tuketim_kWh", "UygulananTarife", "OlmasiGerekenTarife"]
    },
    {
        "name": "MİRAÇ",
        "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv",
        "target": "label",
        "features_text": ["input_name", "input_plate", "reason"],
        "features_num": ["energy_kwh", "duration_min", "avg_power_kw"]
    }
]

def train_nlp_model(ds):
    full_path = os.path.join(BASE_PATH, ds['path'])
    model_path = os.path.join(MODELS_DIR, f"nlp_model_{ds['name']}.joblib")
    
    if not os.path.exists(full_path):
        return f"File Not Found: {full_path}"
        
    try:
        df = pd.read_csv(full_path)
        
        # Prepare targets
        y = df[ds['target']]
        
        # Prepare Feature matrix X
        # flexible container
        X = pd.DataFrame()
        
        # 1. Text Features: Combine into single string column "combined_text"
        if ds['features_text']:
            # Ensure cols exist
            valid_cols = [c for c in ds['features_text'] if c in df.columns]
            if valid_cols:
                # Fill NaN with empty string and join
                X['text_blob'] = df[valid_cols].astype(str).fillna('').agg(' '.join, axis=1)
            else:
                X['text_blob'] = ""
        
        # 2. Numeric Features
        if ds['features_num']:
            valid_nums = [c for c in ds['features_num'] if c in df.columns]
            for c in valid_nums:
                # Force numeric
                X[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
        # --- Build Pipeline ---
        transformers = []
        
        # Text Transformer
        if 'text_blob' in X.columns:
            transformers.append(
                ('text', TfidfVectorizer(max_features=1000, stop_words='english'), 'text_blob')
            )
            
        # Numeric Transformer
        if ds['features_num']:
            # We need to pass list of column names to ColumnTransformer
            valid_nums = [c for c in ds['features_num'] if c in X.columns]
            if valid_nums:
                transformers.append(
                    ('num', SimpleImputer(strategy='constant', fill_value=0), valid_nums)
                )
        
        if not transformers:
            return "No valid features defined."
            
        preprocessor = ColumnTransformer(transformers, remainder='drop')
        
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train
        pipeline.fit(X_train, y_train)
        
        # Evaluate
        score = pipeline.score(X_test, y_test)
        
        # Save
        joblib.dump(pipeline, model_path)
        
        return f"Model Saved: {model_path} | Accuracy: {score:.4f} | Features: Text={len(ds.get('features_text',[]))} Num={len(ds.get('features_num',[]))}"

    except Exception as e:
        return f"Error: {e}"

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("NLP MODEL TRAINING REPORT\n")
    f.write("=========================\n")
    
    for ds in DATASETS:
        f.write(f"\nTraining {ds['name']}...\n")
        res = train_nlp_model(ds)
        f.write(f"  -> {res}\n")

print(f"Done. Report at {REPORT_FILE}")
