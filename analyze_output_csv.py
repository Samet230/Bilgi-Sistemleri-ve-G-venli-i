import pandas as pd
import json
import os
import sys
from detect_attack_ensemble import EnsembleDetector

# Config
DATA_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\İBRAHİM_SAHİN\output.csv"
MODEL_PATH = "best_ensemble_model.pkl"

def analyze_output():
    print(f"Loading data from {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Rename columns to standard English names for consistency
    column_mapping = {
        "Zaman Damgası": "timestamp",
        "Kaynak (Terminal)": "source",
        "Olay Tipi": "event_type",
        "Detay/Değer": "detail",
        "Durum": "status"
    }
    df = df.rename(columns=column_mapping)
    
    print(f"Total logs: {len(df)}")
    
    # Check if 'label' exists, if not assume unknown (just detection)
    if 'label' not in df.columns:
        df['label'] = -1

    # Initialize Detector
    detector = EnsembleDetector("İBRAHİM")
    
    # Prepare logs list
    logs = df.to_dict(orient="records")
    
    print("Running detection logic...")
    # Run detection
    results = detector.detect_batch(logs)
    
    # Analyze Results
    attack_count = 0
    attack_types = {}
    attacks = []
    
    for i, res in enumerate(results):
        decision = res.get('final_decision', 'UNKNOWN')
        confidence = res.get('confidence_score', 0.0)
        is_attack = decision != "NORMAL"
        
        if is_attack:
            attack_count += 1
            attack_types[decision] = attack_types.get(decision, 0) + 1
            attacks.append({
                "index": i,
                "log": str(logs[i]),
                "decision": decision,
                "confidence": confidence
            })

    # Report
    print("\n" + "="*50)
    print(f"ANALYSIS REPORT FOR: {os.path.basename(DATA_PATH)}")
    print("="*50)
    print(f"Total Logs Analyzed: {len(df)}")
    print(f"Total Attacks Detected: {attack_count}")
    print("-" * 30)
    print("Attack Distribution:")
    for atype, count in attack_types.items():
        print(f"  - {atype}: {count}")
    print("-" * 30)
    
    # Show first 5 attacks
    if attacks:
        print("\nSample Attacks (First 5):")
        for att in attacks[:5]:
            print(f"Row {att['index']}: {att['decision']} (%{att['confidence']*100:.1f})")
            # Print log nicely
            log_dict = eval(att['log'])
            print(f"  Content: {log_dict.get('event_type')} - {log_dict.get('detail')} - {log_dict.get('status')}")
            print("-" * 20)
    else:
        print("\nNo attacks detected.")

    # Save to JSON
    report = {
        "total_logs": len(df),
        "total_attacks": attack_count,
        "attack_types": attack_types,
        "sample_attacks": [ {k: str(v) for k,v in a.items()} for a in attacks[:50] ] # Save first 50 attacks
    }
    with open("analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    analyze_output()
