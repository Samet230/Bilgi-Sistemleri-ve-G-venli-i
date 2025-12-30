# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import sys
import json

sys.path.insert(0, r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i")
from detect_attack_ensemble import EnsembleDetector

BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

def test_ibrahim_json():
    csv_path = os.path.join(BASE_PATH, "Raporlar", "İBRAHİM_SAHİN", "output_labeled.csv")
    
    if not os.path.exists(csv_path):
        print("File not found")
        return

    df = pd.read_csv(csv_path)
    
    # Test ALL logs
    logs = df.to_dict(orient="records")
    
    detector = EnsembleDetector("İBRAHİM")
    results = detector.detect_batch(logs)
    
    y_true = df["label"].values
    y_pred = [1 if r["attack_detected"] else 0 for r in results]
    
    analysis = {
        "total_logs": len(df),
        "errors": [],
        "low_confidence": []
    }
    
    for i, (t, p, r, log) in enumerate(zip(y_true, y_pred, results, logs)):
        conf = float(r['confidence_score'])
        log_content = str(log.get("detail", log.get("message", "")))[:200]
        
        # Error?
        if t != p:
            analysis["errors"].append({
                "index": i,
                "log": log_content,
                "true": int(t),
                "pred": int(p),
                "conf": conf,
                "decision": r['final_decision']
            })
            
        # Low Confidence? (Looking for ~64%)
        if 0.60 <= conf <= 0.70:
            analysis["low_confidence"].append({
                "index": i,
                "log": log_content,
                "true": int(t),
                "pred": int(p),
                "conf": conf
            })
            
    # Save JSON
    with open("ibrahim_analysis_v5.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
        
    print(f"Done. Found {len(analysis['errors'])} errors and {len(analysis['low_confidence'])} low confidence logs.")

if __name__ == "__main__":
    test_ibrahim_json()
