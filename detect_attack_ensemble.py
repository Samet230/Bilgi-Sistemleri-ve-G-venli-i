import joblib
import pandas as pd
import numpy as np
import os
import sys
import json
import warnings
from datetime import datetime

# Suppress sklearn warnings about feature names (since we construct DF dynamically)
warnings.filterwarnings("ignore")

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
MODELS_DIR = os.path.join(BASE_PATH, "models_ensemble")

# Standardized Feature Schema for Reconstruction
DATASET_CONFIGS = {
    "YOUSEF": {"features_text": ["event_type", "attack_type"], "features_num": ["time_delta_ms", "blocked"]},
    "SAMET": {"features_text": ["detail"], "features_num": []},
    "EMİRHAN": {"features_text": ["message"], "features_num": []},
    "ATAKAN": {"features_text": [], "features_num": ["load_kw"]},
    "İBRAHİM": {"features_text": ["detail"], "features_num": []},
    "SUZAN": {"features_text": ["ocpp_message"], "features_num": ["price_eur_kwh", "energy_kwh", "power_kw"]},
    "İREM": {"features_text": [], "features_num": ["length", "protocol_ip", "protocol_tcp", "protocol_udp", "protocol_can", "can_id_anomaly"]},
    "MİRAÇ": {"features_text": ["input_name", "input_plate", "reason"], "features_num": ["energy_kwh", "duration_min", "avg_power_kw"]},
    "EMİRHNT": {"features_text": ["Durum"], "features_num": ["Tuketim_kWh", "UygulananTarife", "OlmasiGerekenTarife"]},
    "ALİ": {"features_text": ["action", "status"], "features_num": []},
}

class EnsembleDetector:
    def __init__(self, dataset_name):
        self.name = dataset_name.upper()
        self.config = DATASET_CONFIGS.get(self.name)
        if not self.config:
            raise ValueError(f"Unknown dataset: {dataset_name}")
            
        # Load Models
        self.models = {}
        for algo in ["RF", "GBM", "ET"]:
            path = os.path.join(MODELS_DIR, f"{self.name}_{algo}.joblib")
            if os.path.exists(path):
                self.models[algo] = joblib.load(path)
            else:
                print(f"Warning: Model {algo} not found at {path}")
        
        if not self.models:
            raise RuntimeError("No models loaded! Train models first.")

    def preprocess(self, log_dict):
        """Converts raw log dictionary to Ensembler-ready DataFrame."""
        df = pd.DataFrame([log_dict])
        X = pd.DataFrame()
        
        # Text Construction
        text_cols = self.config['features_text']
        if text_cols:
            valid_cols = [c for c in text_cols if c in df.columns]
            if valid_cols:
                X['text_blob'] = df[valid_cols].astype(str).fillna('').agg(' '.join, axis=1)
            else:
                X['text_blob'] = ""
        else:
             X['text_blob'] = ""

        # Numeric Construction
        num_cols = self.config['features_num']
        for c in num_cols:
            if c in df.columns:
                X[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0).astype(float)
            else:
                X[c] = 0.0
                
        return X

    def detect(self, log_dict):
        """Analyzes a log using the Council of Models."""
        X = self.preprocess(log_dict)
        
        votes = []
        confidences = []
        details = []
        
        for algo, model in self.models.items():
            # Soft Voting if available
            try:
                # Predict Probability
                proba = model.predict_proba(X)[0] # [prob_normal, prob_attack]
                confidence = proba[1] # Probability of Attack
                
                # Decision
                # Using 0.5 as model's own threshold, but we record actual confidence
                prediction = 1 if confidence > 0.5 else 0
                
                votes.append(prediction)
                # If prediction is 0 (Normal), confidence of Attack is low, so confidence of Normal is 1-p.
                # But for voting, let's track "Attack Score".
                confidences.append(confidence)
                details.append(f"{algo}: {'🔴 SALDIRI' if prediction else '🟢 NORMAL'} (%{confidence:.1%})")
                
            except Exception as e:
                details.append(f"{algo}: Error ({e})")
        
        # --- The Council Decision (Majority Voting 2/3) ---
        attack_votes = sum(votes)
        total_models = len(self.models)
        avg_confidence = np.mean(confidences)
        
        # Find the model with highest confidence for documentation
        max_conf_idx = np.argmax(confidences)
        model_names = list(self.models.keys())
        winning_model = model_names[max_conf_idx] if model_names else "UNKNOWN"
        highest_confidence = confidences[max_conf_idx] if confidences else 0.0
        
        if attack_votes >= 2:
            status_label = "SALDIRI"
            final_confidence = highest_confidence  # Use the highest model's confidence
            is_attack = True
        elif attack_votes == 1:
            status_label = "ŞÜPHELİ (Zayıf Sinyal)"
            final_confidence = max(confidences)
            is_attack = True
        else:
            status_label = "NORMAL"
            final_confidence = 1 - avg_confidence
            is_attack = False

        return {
            "dataset": self.name,
            "final_decision": status_label,
            "confidence_score": final_confidence,
            "attack_detected": is_attack,
            "winning_model": winning_model,
            "council_votes": details
        }

# --- Demo Usage ---
if __name__ == "__main__":
    print("Initializing Ensemble Detectors...")
    
    # Example 1: Emirhan (Text Attack)
    detector_emirhan = EnsembleDetector("EMİRHAN")
    # A real attack example "SQL Injection"
    test_log_1 = {"message": "Dışarıdan SQL Injection Denemesi Algılandı", "rule_id": "101"} # rule_id should be ignored
    result_1 = detector_emirhan.detect(test_log_1)
    
    # Example 2: Atakan (Numeric Attack)
    detector_atakan = EnsembleDetector("ATAKAN")
    # A real normal example
    test_log_2 = {"load_kw": 3.5}
    result_2 = detector_atakan.detect(test_log_2)
    
    # Example 3: Suzan (Numeric Attack)
    detector_suzan = EnsembleDetector("SUZAN")
    # Attack: High Price
    test_log_3 = {"ocpp_message": "MeterValues", "price_eur_kwh": 55.0}
    result_3 = detector_suzan.detect(test_log_3)

    print("\n" + "="*50)
    print(f"LOG 1 (Emirhan - SQL): {result_1['final_decision']} (Güven: {result_1['confidence_score']:.1%})")
    print(f"Kazanan: {result_1['winning_model']}")
    print("Konsey:", " | ".join(result_1['council_votes']))
    
    print("\n" + "="*50)
    print(f"LOG 2 (Atakan - Normal): {result_2['final_decision']} (Güven: {result_2['confidence_score']:.1%})")
    print(f"Kazanan: {result_2['winning_model']}")
    print("Konsey:", " | ".join(result_2['council_votes']))

    print("\n" + "="*50)
    print(f"LOG 3 (Suzan - Fiyat): {result_3['final_decision']} (Güven: {result_3['confidence_score']:.1%})")
    print(f"Kazanan: {result_3['winning_model']}")
    print("Konsey:", " | ".join(result_3['council_votes']))
    print("="*50 + "\n")
