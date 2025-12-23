import pandas as pd
import os
import sys
from sklearn.metrics import accuracy_score
from detect_attack_ensemble import EnsembleDetector

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
TEST_DATA_DIR = os.path.join(BASE_PATH, "test_data")
OUTPUT_FILE = os.path.join(TEST_DATA_DIR, "ensemble_final_report.txt")

# List of all datasets to test
TEST_FILES = [
    {"file": "test_YOUSEF.csv", "model_name": "YOUSEF", "target": "label"},
    {"file": "test_SAMET.csv", "model_name": "SAMET", "target": "label"},
    {"file": "test_EMİRHAN.csv", "model_name": "EMİRHAN", "target": "label"},
    {"file": "test_ATAKAN.csv", "model_name": "ATAKAN", "target": "label"},
    {"file": "test_İBRAHİM.csv", "model_name": "İBRAHİM", "target": "label"},
    {"file": "test_SUZAN.csv", "model_name": "SUZAN", "target": "label"},
    {"file": "test_İREM.csv", "model_name": "İREM", "target": "label"},
    {"file": "test_MİRAÇ.csv", "model_name": "MİRAÇ", "target": "label"},
    {"file": "test_EMİRHNT.csv", "model_name": "EMİRHNT", "target": "label"},
    {"file": "test_ALİ.csv", "model_name": "ALİ", "target": "label"},
]

def run_tests():
    report_lines = []
    report_lines.append("🛡️ ENSEMBLE SYSTEM: FINAL COMPREHENSIVE TEST & DEBUG REPORT")
    report_lines.append("=" * 60)
    report_lines.append("Ideally achieving 100% accuracy due to 'Voting Mechanism'.\n")
    
    overall_passed = 0
    total_datasets = 0
    
    for item in TEST_FILES:
        name = item['model_name']
        file_path = os.path.join(TEST_DATA_DIR, item['file'])
        
        report_lines.append(f"🧪 TESTING ANOMALY: {name}")
        report_lines.append("-" * 30)
        
        if not os.path.exists(file_path):
             report_lines.append("  -> ❌ Test Data Not Found. Skipped.\n")
             continue
             
        try:
            # Load Detector
            detector = EnsembleDetector(name)
            
            # Load Test Data
            df = pd.read_csv(file_path)
            y_true = df[item['target']]
            
            y_pred = []
            debug_logs = []
            
            # Process row by row to simulate real-time and capture logic
            for idx, row in df.iterrows():
                log_dict = row.to_dict()
                result = detector.detect(log_dict)
                
                # Map based on the detector's own internal flag
                pred_label = 1 if result['attack_detected'] else 0
                
                y_pred.append(pred_label)
                
                # Capture debug info if it was an ACTUAL Attack or Predicted Attack
                # To keep report concise, only show 1 Normal and 1 Attack example detailed
                actual_label = row[item['target']]
                should_log = False
                prefix = ""
                
                if actual_label == 1 and pred_label == 1:
                    prefix = "✅ TP (Caught Attack)"
                    if "TP_SHOWN" not in debug_logs: should_log = True; debug_logs.append("TP_SHOWN")
                elif actual_label == 1 and pred_label == 0:
                    prefix = "❌ FN (Missed Attack)"
                    should_log = True # Always log errors
                elif actual_label == 0 and pred_label == 1:
                    prefix = "⚠️ FP (False Alarm)"
                    should_log = True
                
                if should_log:
                    votes_str = " | ".join(result['council_votes'])
                    report_lines.append(f"  [{prefix}] Log #{idx}")
                    report_lines.append(f"    -> Council: {votes_str}")
                    report_lines.append(f"    -> Final: {result['final_decision']} (Conf: {result['confidence_score']:.1%})")

            # Calc Metrics
            acc = accuracy_score(y_true, y_pred)
            
            report_lines.append(f"\n  -> Accuracy: {acc:.2%}")
            if acc == 1.0:
                report_lines.append("  -> RESULT: PERFECT 🚀")
                overall_passed += 1
            elif acc > 0.9:
                 report_lines.append("  -> RESULT: EXCELLENT ✅")
                 overall_passed += 1
            else:
                 report_lines.append("  -> RESULT: NEEDS ATTENTION ⚠️")
            
            total_datasets += 1
            report_lines.append("\n")

        except Exception as e:
            report_lines.append(f"  -> CRITICAL ERROR: {e}\n")

    # Final Summary
    report_lines.append("=" * 60)
    report_lines.append(f"SUMMARY: {overall_passed}/{total_datasets} Datasets Passed with High Accuracy.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        print(f"Test Complete. Report saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_tests()
