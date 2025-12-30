import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
MODELS_DIR = os.path.join(BASE_PATH, "models_ensemble")
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

REPORT_FILE = os.path.join(MODELS_DIR, "ensemble_training_report.txt")

# Unified Leakage-Free Config
DATASETS = [
    {
        "name": "YOUSEF", 
        "path": r"Raporlar\YOUSEF_BSG\Logs\dataset.csv",  # Original file with rich data
        "target": "label",
        "features_text": ["event_type", "attack_type"], # Rich columns from original
        "features_num": ["time_delta_ms", "blocked"]
    },
    {
        "name": "SAMET",
        "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv",
        "target": "label",
        "features_text": ["detail"], # pure text
        "features_num": []
    },
    {
        "name": "EMİRHAN",
        "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv",
        "target": "label",
        "features_text": ["message"], # pure text
        "features_num": []
    },
    {
        "name": "ATAKAN",
        "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol_BSG\expanded_logs.csv",
        "target": "label",
        "features_text": [],
        "features_num": ["load_kw"]
    },
    {
        "name": "İBRAHİM",
        "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv",
        "target": "label",
        "features_text": ["detail"],
        "features_num": []
    },
    {
        "name": "SUZAN",
        "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv",
        "target": "label",
        "features_text": ["ocpp_message"],
        "features_num": ["price_eur_kwh", "energy_kwh", "power_kw"]
    },
    {
        "name": "İREM",
        "path": r"Raporlar\İREM_BSG\network_traffic_features.csv",
        "target": "label",
        "features_text": [],
        "features_num": ["length", "protocol_ip", "protocol_tcp", "protocol_udp", "protocol_can", "can_id_anomaly"]
    },
    {
        "name": "MİRAÇ",
        "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv",
        "target": "label",
        "features_text": ["input_name", "input_plate", "reason"], # Name/Plate might vary, Reason is key usually
        "features_num": ["energy_kwh", "duration_min", "avg_power_kw"]
    },
    {
        "name": "EMİRHNT",
        "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv",
        "target": "label",
        "features_text": ["Durum"], 
        "features_num": ["Tuketim_kWh", "UygulananTarife", "OlmasiGerekenTarife"]
    },
    {
        "name": "ALİ",
        "path": r"Raporlar\ALİ_GİRİŞ_BSG\ali_logs_parsed.csv",
        "target": "label",
        "features_text": ["action", "status"],  # RemoteStopTransaction = Attack
        "features_num": []
    }
]

def train_ensemble_for_dataset(ds):
    full_path = os.path.join(BASE_PATH, ds['path'])
    if not os.path.exists(full_path):
        return f"Skipped {ds['name']}: File not found"

    try:
        df = pd.read_csv(full_path)
        
        # Normalize Labels to 0/1 (Fix for Irem and others with string labels)
        if df[ds['target']].dtype == 'object':
            df[ds['target']] = df[ds['target']].apply(lambda x: 0 if str(x).lower() == 'normal' else 1)
            
        y = df[ds['target']]
        
        # Prepare X with concatenated text column for NLP
        X = pd.DataFrame()
        
        # 1. Text Blob (for NLP)
        if ds['features_text']:
            valid_cols = [c for c in ds['features_text'] if c in df.columns]
            if valid_cols:
                X['text_blob'] = df[valid_cols].astype(str).fillna('').agg(' '.join, axis=1)
            else:
                X['text_blob'] = ""
        else:
             # Ensure column exists even if empty, for pipeline consistency
             X['text_blob'] = ""

        # 2. Numerics (for RF/GBM)
        # Note: RF can use Text vectors too if we vectorizer them.
        # But "Model A (RF) = Numeric Expert" implies we feed it numerics + maybe OHE categories?
        # For simplicity and ensemble diversity:
        # - NLP Model uses Tfidf on 'text_blob'.
        # - RF/GBM use Numeric columns + Maybe 'text_blob' vectorized?
        # Let's give ALL features to ALL models but different processing.
        # Actually proper ensemble usually differs in Algorithm.
        # We will make 3 Pipelines:
        # 1. Pipeline_NLP: Tfidf on text_blob -> RF Classifier
        # 2. Pipeline_RF: Scaler on Numerics -> RF Classifier
        # 3. Pipeline_GBM: Scaler on Numerics -> GBM Classifier
        # Wait, if I only feed numerics to RF, it will fail on Text-only datasets (Emirhan).
        # So RF and GBM must ALSO see the text (vectorized).
        
        for c in ds['features_num']:
            if c in df.columns:
                X[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
            else:
                X[c] = 0.0

        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # --- Define Preprocessors ---
        
        # NLP Preprocessor: Only looks at 'text_blob'
        # Handles case where text_blob is empty string? Tfidf might complain if all empty.
        # If dataset is purely numeric (Atakan), text_blob is empty. Tfidf will error or return empty matrix.
        # Safe strategy: If dataset has NO text features, use Dummy transformer or skip text part.
        
        has_text = len(ds['features_text']) > 0
        has_num = len(ds['features_num']) > 0
        
        transformers_nlp = []
        if has_text:
            transformers_nlp.append(('txt', TfidfVectorizer(max_features=500), 'text_blob'))
        
        # If no text, NLP model might be weak/useless, but we train it anyway (or skip?)
        # For numeric datasets, "NLP Model" makes no sense.
        # But the User wants "3 Models".
        # Let's define the 3 models as:
        # 1. "Text Expert" (RandomForest on Tfidf) -> If no text, falls back to numerics or 0.
        # 2. "Numeric Expert" (RandomForest on Num) -> If no num, falls back to text length?
        # 3. "Hybrid GBM" (GBM on Both) -> The arbitrator.
        
        # Better Plan:
        # Common Preprocessor: Vectorize Text + Scale Num
        # Then 3 Classifiers.
        
        transformers_common = []
        if has_text:
            transformers_common.append(('txt', TfidfVectorizer(max_features=500), 'text_blob'))
        if has_num:
            transformers_common.append(('num', SimpleImputer(strategy='constant', fill_value=0), ds['features_num']))
            
        if not transformers_common:
            return f"Skipped {ds['name']}: No features defined"
            
        preprocessor = ColumnTransformer(transformers_common, remainder='drop')
        
        # Pipeline 1: Random Forest (The Generalist)
        pipe_rf = Pipeline([('prep', preprocessor), ('clf', RandomForestClassifier(n_estimators=100))])
        
        # Pipeline 2: NLP Expert (Uses RF but maybe different hyperparams or just relies on the Tfidf part heavily)
        # Actually let's strictly vary the ALGORITHMS as requested.
        # User Plan: Model A (RF), Model B (NLP - implied technique), Model C (GBM).
        # Let's stick effectively to:
        # 1. RF (RandomForest)
        # 2. SVC or LinearModel (often used for NLP) -> Let's use LogisticRegression for variety? Or another RF?
        # Let's use 'GradientBoosting' as requested for C.
        # For B (NLP), if we use RF on Tfidf, it's fine.
        
        pipe_gbm = Pipeline([('prep', preprocessor), ('clf', GradientBoostingClassifier(n_estimators=100))])
        
        # For Diversity, Model 3 could be ExtraTrees or SVC.
        # Let's use ExtraTreesClassifier as "Model Output Diversity".
        from sklearn.ensemble import ExtraTreesClassifier
        pipe_et = Pipeline([('prep', preprocessor), ('clf', ExtraTreesClassifier(n_estimators=100))])
        
        results = ""
        
        # Train 1: RF
        pipe_rf.fit(X_train, y_train)
        score_rf = pipe_rf.score(X_test, y_test)
        joblib.dump(pipe_rf, os.path.join(MODELS_DIR, f"{ds['name']}_RF.joblib"))
        
        # Train 2: GBM
        pipe_gbm.fit(X_train, y_train)
        score_gbm = pipe_gbm.score(X_test, y_test)
        joblib.dump(pipe_gbm, os.path.join(MODELS_DIR, f"{ds['name']}_GBM.joblib"))
        
        # Train 3: ET (Extra Trees)
        pipe_et.fit(X_train, y_train)
        score_et = pipe_et.score(X_test, y_test)
        joblib.dump(pipe_et, os.path.join(MODELS_DIR, f"{ds['name']}_ET.joblib"))
        
        results = f"RF: {score_rf:.2%} | GBM: {score_gbm:.2%} | ET: {score_et:.2%}"
        return results

    except Exception as e:
        return f"Error {ds['name']}: {e}"

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("ENSEMBLE TRAINING REPORT\n========================\n")
    for ds in DATASETS:
        res = train_ensemble_for_dataset(ds)
        f.write(f"{ds['name']}: {res}\n")
        print(f"Trained {ds['name']}: {res}")

print("Ensemble Training Complete.")
