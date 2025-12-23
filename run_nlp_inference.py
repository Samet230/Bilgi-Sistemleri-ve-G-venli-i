import pandas as pd
import joblib
import os
import glob
from sklearn.metrics import accuracy_score

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
MODELS_DIR = os.path.join(BASE_PATH, "models")
TEST_DATA_DIR = os.path.join(BASE_PATH, "test_data")
OUTPUT_FILE = os.path.join(TEST_DATA_DIR, "inference_report_nlp.txt")

# Configuration to reconstruct 'text_blob' for inference
DATASET_CONFIGS = {
    "YOUSEF": {"features_text": ["ocpp_message"], "features_num": ["time_delta_ms"]},
    "SAMET": {"features_text": ["detail"], "features_num": []},
    "EMİRHAN": {"features_text": ["message"], "features_num": []},
    "ATAKAN": {"features_text": [], "features_num": ["load_kw"]},
    "İBRAHİM": {"features_text": ["detail"], "features_num": []},
    "SUZAN": {"features_text": ["ocpp_message"], "features_num": ["price_eur_kwh", "energy_kwh", "power_kw"]},
    "İREM": {"features_text": [], "features_num": ["length", "protocol_ip", "protocol_tcp", "protocol_udp", "protocol_can", "can_id_anomaly"]},
    "MİRAÇ": {"features_text": ["input_name", "input_plate", "reason"], "features_num": ["energy_kwh", "duration_min", "avg_power_kw"]},
    "EMİRHNT": {"features_text": ["Durum"], "features_num": ["Tuketim_kWh", "UygulananTarife", "OlmasiGerekenTarife"]},
}

TEST_FILES = [
    {"file": "test_YOUSEF.csv", "model_name": "YOUSEF", "target": "label"},
    {"file": "test_SAMET.csv", "model_name": "SAMET", "target": "label"},
    {"file": "test_ATAKAN.csv", "model_name": "ATAKAN", "target": "label"},
    {"file": "test_EMİRHAN.csv", "model_name": "EMİRHAN", "target": "label"},
    {"file": "test_İBRAHİM.csv", "model_name": "İBRAHİM", "target": "label"},
    {"file": "test_SUZAN.csv", "model_name": "SUZAN", "target": "label"},
    {"file": "test_İREM.csv", "model_name": "İREM", "target": "label"},
    {"file": "test_MİRAÇ.csv", "model_name": "MİRAÇ", "target": "label"},
    {"file": "test_EMİRHNT.csv", "model_name": "EMİRHNT", "target": "label"},
]

def run_nlp_inference():
    report_lines = []
    report_lines.append("INFERENCE TEST REPORT: ROBUST NLP MODELS")
    report_lines.append("========================================\n")
    
    for item in TEST_FILES:
        name = item['model_name']
        file_path = os.path.join(TEST_DATA_DIR, item['file'])
        model_path = os.path.join(MODELS_DIR, f"nlp_model_{name}.joblib")
        
        report_lines.append(f"TESTING NLP MODEL: {name}")
        report_lines.append("-" * 30)
        
        if not os.path.exists(file_path):
            report_lines.append(f"  -> Test Data Not Found\n")
            continue
        if not os.path.exists(model_path):
            report_lines.append(f"  -> Model Not Found\n")
            continue
            
        try:
            df = pd.read_csv(file_path)
            y_true = df[item['target']]
            
            # Reconstruct Features (X) same as training logic
            # This logic must align with 'train_nlp_models.py'
            cfg = DATASET_CONFIGS.get(name, {})
            text_cols = cfg.get("features_text", [])
            num_cols = cfg.get("features_num", [])
            
            X = pd.DataFrame()
            
            # Text Construction
            if text_cols:
                 valid_cols = [c for c in text_cols if c in df.columns]
                 if valid_cols:
                     X['text_blob'] = df[valid_cols].astype(str).fillna('').agg(' '.join, axis=1)
                 else:
                     X['text_blob'] = ""
                     # If test data is missing source columns entirely, empty string.
                     
            # Numeric Construction
            for c in num_cols:
                if c in df.columns:
                    X[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0).astype(float)
                else:
                    X[c] = 0.0
            
            # Load Pipeline
            pipeline = joblib.load(model_path)
            
            # Predict
            y_pred = pipeline.predict(X)
            
            acc = accuracy_score(y_true, y_pred)
            anomalies_detected = sum(y_pred)
            actual_anomalies = sum(y_true)
            
            report_lines.append(f"  -> Samples: {len(df)}")
            report_lines.append(f"  -> Actual Anomalies: {actual_anomalies}")
            report_lines.append(f"  -> DETECTED Anomalies: {anomalies_detected}")
            report_lines.append(f"  -> Accuracy: {acc:.2%}")
            
            if acc == 1.0:
                 report_lines.append("  -> RESULT: PERFECT DETECTION 🚀")
            else:
                 if acc > 0.8:
                     report_lines.append("  -> RESULT: SIGNIFICANT IMPROVEMENT ✅")
                 else:
                     report_lines.append("  -> RESULT: STILL NEEDS TUNING ⚠️")
            report_lines.append("\n")

        except Exception as e:
            report_lines.append(f"  -> ERROR: {e}\n")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        print(f"Inference complete. Report: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_nlp_inference()
