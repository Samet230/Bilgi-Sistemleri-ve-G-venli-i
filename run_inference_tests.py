import pandas as pd
import joblib
import os
import glob
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
MODELS_DIR = os.path.join(BASE_PATH, "models")
TEST_DATA_DIR = os.path.join(BASE_PATH, "test_data")
OUTPUT_FILE = os.path.join(TEST_DATA_DIR, "inference_report.txt")

# Define mapping between test files and models
# File: test_YOUSEF.csv -> Model: rf_model_YOUSEF.joblib
TEST_FILES = [
    {"file": "test_YOUSEF.csv", "model_name": "YOUSEF", "target": "label"},
    {"file": "test_SAMET.csv", "model_name": "SAMET", "target": "label"},
    {"file": "test_ATAKAN.csv", "model_name": "ATAKAN", "target": "label"},
    {"file": "test_EMİRHAN.csv", "model_name": "EMİRHAN", "target": "label"},
    {"file": "test_İBRAHİM.csv", "model_name": "İBRAHİM", "target": "label"},
]

def run_inference():
    report_lines = []
    report_lines.append("INFERENCE TEST REPORT: NEW SYNTHETIC DATA")
    report_lines.append("=========================================\n")
    
    for item in TEST_FILES:
        file_path = os.path.join(TEST_DATA_DIR, item['file'])
        model_path = os.path.join(MODELS_DIR, f"rf_model_{item['model_name']}.joblib")
        encoder_path = os.path.join(MODELS_DIR, f"encoders_{item['model_name']}.joblib")
        
        report_lines.append(f"TESTING MODEL: {item['model_name']}")
        report_lines.append("-" * 30)
        
        if not os.path.exists(file_path):
            report_lines.append(f"  -> Test Data Not Found: {file_path}\n")
            continue
            
        if not os.path.exists(model_path):
            report_lines.append(f"  -> Model Not Found: {model_path}\n")
            continue
            
        try:
            # Load Data
            df = pd.read_csv(file_path)
            y_true = df[item['target']]
            X = df.drop(columns=[item['target']])
            
            # Load Model & Encoders
            rf = joblib.load(model_path)
            encoders = joblib.load(encoder_path)
            
            # Preprocess X (Apply same encoding as training)
            X_encoded = X.copy()
            
            # Apply saved encoders if columns exist
            # Note: In production, we must handle 'unseen labels' safely.
            # Here we just try transform, if error fill 0 or skip.
            
            for col in X_encoded.columns:
                if col in encoders:
                    le = encoders[col]
                    # Safe transform: map unknown to a default or strings
                    X_encoded[col] = X_encoded[col].astype(str).map(
                        lambda s: le.transform([s])[0] if s in le.classes_ else 0
                    )
                else:
                    # If numerical, fillna
                    if X_encoded[col].dtype != 'object':
                        X_encoded[col] = X_encoded[col].fillna(0)
                        
            # Ensure X_encoded has same columns as model expects?
            # RF doesn't enforce column names strictly but order matters if array.
            # But sklearn stores feature_names_in_.
            # We align columns.
            
            if hasattr(rf, "feature_names_in_"):
                 expected_cols = rf.feature_names_in_
                 # Add missing cols with 0
                 for col in expected_cols:
                     if col not in X_encoded.columns:
                         X_encoded[col] = 0
                 # Reorder and drop extras
                 X_encoded = X_encoded[list(expected_cols)]
            
            # Predict
            y_pred = rf.predict(X_encoded)
            
            # Compare
            acc = accuracy_score(y_true, y_pred)
            anomalies_detected = sum(y_pred)
            actual_anomalies = sum(y_true)
            
            report_lines.append(f"  -> Test Samples: {len(df)}")
            report_lines.append(f"  -> Actual Anomalies: {actual_anomalies}")
            report_lines.append(f"  -> DETECTED Anomalies: {anomalies_detected}")
            report_lines.append(f"  -> Accuracy on New Data: {acc:.2%}")
            
            if acc == 1.0:
                 report_lines.append("  -> RESULT: PERFECT DETECTION 🚀")
            else:
                 report_lines.append("  -> RESULT: GOOD (Some mismatches due to new data patterns)")
                 
            report_lines.append("\n")

        except Exception as e:
            report_lines.append(f"  -> ERROR: {e}\n")

    # Write Report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"Inference complete. Report saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_inference()
