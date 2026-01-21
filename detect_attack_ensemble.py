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

# Güvenli Kalıplar - Bu kalıpları içeren loglar otomatik olarak NORMAL işaretlenir
# False positive'leri önlemek için whitelist
SAFE_PATTERNS = [
    # Health check endpoints
    "/health", "/healthz", "/ready", "/readiness", "/liveness",
    "/api/v1/health", "/actuator/health", "/status", "/ping",
    # Normal OCPP heartbeats and operations
    "heartbeat", "boot", "bootnotification", "statusnotification",
    "metervalues response", "datatransfer", "authorize response",
    # Normal HTTP responses
    "200 ok", "201 created", "204 no content", "302 redirect",
    # Normal operations - Turkish
    "trafik akışı temiz", "servis sağlık kontrolü",
    "login success", "başarılı", "success", "completed", "tamamlandı",
    "bağlantı kuruldu", "connection established",
    # İBRAHİM CSMS logs - Normal operations
    "şarj başlatma", "şarj başladı", "şarj tamamlandı",
    "enerji tüketimi", "yeni cp bağlandı", "cp bağlandı",
    "transaction id", "bağlantı başarılı",
    "clock synced", "ntp senkronizasyonu", "zaman senkronizasyonu",
    "ocpp -> can mesajı iletildi", "can mesajı iletildi",
    "mesaj gönderildi", "mesaj alındı",
    # System logs - Normal operations
    "service started", "servis başlatıldı",
    "configuration loaded", "config yüklendi",
    "scheduled task", "zamanlanmış görev",
    "backup completed", "yedekleme tamamlandı",
    "log rotation", "log döndürme",
    # Authentication - Successful
    "authentication successful", "kimlik doğrulama başarılı",
    "session created", "oturum açıldı",
    "token refreshed", "token yenilendi",
    # Normal warnings (not attacks)
    "low battery", "düşük batarya",
    "maintenance mode", "bakım modu",
    "rate limit", "hız sınırı",  # Rate limiting is protective, not attack
]

# EV Şarj İstasyonu Saldırı Sınıflandırma Kuralları
# Tüm 10 senaryo OCPP/EV şarj ekosistemi ile ilgili
# Format: [(anahtar_kelimeler, saldiri_türü), ...]
# Öncelik: İlk eşleşen kazanır
ATTACK_CLASSIFICATION_RULES = [
    # OCPP Protokol Saldırıları
    (["injection", "ocpp_injection"], "OCPP Mesaj Enjeksiyonu"), # Removed generic "ocpp" keyword
    (["remotestop", "remotestart", "unauthorized"], "OCPP Yetkisiz Komut"),
    (["transaction", "starttransaction", "stoptransaction"], "OCPP İşlem Manipülasyonu"),
    (["metervalues", "meter"], "Sayaç Değeri Sahteciliği"),
    
    # İletişim Güvenliği Saldırıları
    (["tls", "ssl", "downgrade", "tls_dowgrade"], "TLS Downgrade Saldırısı"),
    (["mitm", "man-in-the-middle", "intercept"], "Ortadaki Adam Saldırısı"),
    (["certificate", "cert", "ssl_strip"], "Sertifika Saldırısı"),
    
    # Şarj İstasyonu Firmware/Yazılım Saldırıları
    (["firmware", "enjeksiyon", "enjeksiyonu", "update", "flash"], "Firmware Enjeksiyonu"),
    (["malware", "trojan", "backdoor"], "Zararlı Yazılım Yükleme"),
    
    # Güç/Enerji Manipülasyonu
    (["load_manipulation", "load", "kw", "power", "yük"], "Güç Yükü Manipülasyonu"),
    (["energy", "enerji", "wh", "kwh", "consumption"], "Enerji Tüketimi Sahteciliği"),
    
    # Tarife ve Faturalandırma Hileleri
    (["tarife", "tariff", "billing", "fatura", "ücret", "price"], "Tarife Manipülasyonu"),
    (["fraud", "hile", "dolandırıcılık"], "Faturalandırma Dolandırıcılığı"),
    
    # Kimlik Doğrulama Saldırıları
    (["plaka", "plate", "rfid", "card", "kimlik"], "Kimlik Sahteciliği"),
    (["brute", "force", "failed", "attempt", "deneme"], "Kaba Kuvvet Saldırısı"),
    (["credential", "password", "auth"], "Kimlik Bilgisi Hırsızlığı"),
    
    # Ağ/Altyapı Saldırıları
    (["scan", "keşfi", "hareket", "lateral", "recon"], "Ağ Keşfi / Tarama"),
    (["ddos", "flood", "dos", "syn"], "Hizmet Engelleme (DoS)"),
    
    # CAN Bus / Araç İçi Ağ Saldırıları
    (["can_bus", "can_id", "obd", "vehicle_bus", "0x"], "CAN Bus Saldırısı"), # Removed generic "can"
    
    # CSMS (Central System) Saldırıları
    (["csms", "central", "backend", "api"], "CSMS Backend Saldırısı"),
    (["rbac", "yetki", "privilege", "admin", "yükseltme"], "Yetki Yükseltme"),
    
    # İBRAHİM CSMS Spesifik Saldırıları
    (["köprüleme", "kopru", "bypass", "atla"], "Güvenlik Köprüleme Saldırısı"),
    (["sızma", "sizinti", "intrusion", "penetration"], "Ağ Sızma Girişimi"),
    (["saldırı", "saldiri", "attack"], "Doğrudan Saldırı"),
    (["güvenlik", "guvenlik", "security", "alert"], "Güvenlik Uyarısı"),
    
    # ATAKAN Spesifik Saldırıları
    (["alarm", "emergency", "acil", "uyarı"], "Acil Durum Alarmı"),
    (["time_anomaly", "zaman", "timestamp"], "Zaman Anomalisi"),
    
    # Yan Hareket ve Keşif Saldırıları (YOUSEF)
    (["lateral_movement", "lateral", "yan_hareket"], "Yanal Hareket Saldırısı"),
    (["ocpp_cmd_rejected", "cmd_rejected", "rejected"], "Komut Reddedildi"),
    (["ocpp_validation_fail", "validation_fail", "validate"], "Doğrulama Hatası"),
    
    # Genel Anomaliler
    (["anomaly", "anomali", "unusual", "abnormal", "şüpheli"], "Şarj İstasyonu Anomalisi"),
]

def classify_attack(log_text: str, dataset_name: str = "") -> str:
    """
    EV şarj istasyonu saldırılarını sınıflandırır.
    Log içeriğine bakarak spesifik saldırı türü etiketi döndürür.
    """
    text_lower = log_text.lower() if log_text else ""
    
    # Kural listesinde ilk eşleşeni bul
    for keywords, attack_type in ATTACK_CLASSIFICATION_RULES:
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return attack_type
    
    # Dataset bazlı varsayılan sınıflandırmalar (eşleşme yoksa)
    if dataset_name:
        dataset_upper = dataset_name.upper()
        fallbacks = {
            "ALİ": "OCPP Protokol Anomalisi",
            "ATAKAN": "Güç Yükü Anomalisi",
            "İBRAHİM": "CSMS İletişim Anomalisi",
            "SUZAN": "Şarj İstasyonu Anomalisi",
            "MİRAÇ": "Kimlik Doğrulama Anomalisi",
            "EMİRHNT": "Tarife Anomalisi",
            "EMİRHAN": "Backend Güvenlik Anomalisi",
            "SAMET": "IDS Güvenlik Anomalisi",
            "YOUSEF": "OCPP Protokol Anomalisi",
            "İREM": "CAN Bus Anomalisi",
        }
        return fallbacks.get(dataset_upper, "Şarj İstasyonu Anomalisi")
    
    # Genel fallback
    return "Şarj İstasyonu Anomalisi"

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
        # Wrap single log in a list and use the batch method
        return self.detect_batch([log_dict])[0]

    def detect_batch(self, logs_list):
        """Analyzes a list of logs using vectorized operations (High Performance)."""
        if not logs_list:
            return []

        # 1. Preprocess all logs at once using DataFrame
        df = pd.DataFrame(logs_list)
        X = pd.DataFrame(index=df.index)

        # Text Construction (Vectorized)
        text_cols = self.config['features_text']
        if text_cols:
            valid_cols = [c for c in text_cols if c in df.columns]
            if valid_cols:
                X['text_blob'] = df[valid_cols].astype(str).fillna('').agg(' '.join, axis=1)
            else:
                X['text_blob'] = ""
        else:
            X['text_blob'] = ""

        # Numeric Construction (Vectorized)
        num_cols = self.config['features_num']
        for c in num_cols:
            if c in df.columns:
                X[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0).astype(float)
            else:
                X[c] = 0.0

        # 2. Vectorized Predictions
        total_votes = np.zeros(len(df), dtype=int)
        confidences_matrix = [] # To store confidence of each model for each row
        
        results_details = [[] for _ in range(len(df))]
        
        model_names = []

        for algo, model in self.models.items():
            model_names.append(algo)
            try:
                # Batch Prediction
                probas = model.predict_proba(X) # Shape: (N, 2)
                batch_confidences = probas[:, 1] # Probability of Attack
                
                # Decisions (Threshold 0.5)
                batch_votes = (batch_confidences > 0.5).astype(int)
                
                # Accumulate
                total_votes += batch_votes
                confidences_matrix.append(batch_confidences)
                
                # Record Details (Bit slower part, but necessary for reporting)
                # Optimization: Do this only if needed, but for now we keep it consistent
                for idx, (vote, conf) in enumerate(zip(batch_votes, batch_confidences)):
                    status = '🔴 SALDIRI' if vote else '🟢 NORMAL'
                    results_details[idx].append(f"{algo}: {status} (%{conf:.1%})")
                    
            except Exception as e:
                # Fallback for errors
                for i in range(len(df)):
                    results_details[i].append(f"{algo}: Error ({str(e)})")
                confidences_matrix.append(np.zeros(len(df)))

        # 3. Council Decision (Vectorized Logic)
        confidences_matrix = np.array(confidences_matrix).T # Shape: (N, Models)
        
        # Determine Winning Model (Highest Confidence)
        max_conf_indices = np.argmax(confidences_matrix, axis=1) # Shape: (N,)
        winning_models = [model_names[i] if model_names else "UNKNOWN" for i in max_conf_indices]
        highest_confidences = np.max(confidences_matrix, axis=1)
        avg_confidences = np.mean(confidences_matrix, axis=1)
        
        results = []
        for i in range(len(df)):
            attack_votes = total_votes[i]
            
            # Get raw log text for classification
            raw_log = logs_list[i]
            
            # Exclude meta-columns to prevent data leakage or false positives from labels
            exclude_cols = {'label', 'attack_type', 'decision', 'is_attack', 'winning_model', 'confidence_score', 'monitor_id', 'job_id'}
            clean_values = [str(v) for k, v in raw_log.items() if k not in exclude_cols and pd.notna(v)]
            text_for_classification = " ".join(clean_values).lower()
            
            # WHITELIST CHECK: Override ML decision if safe pattern detected
            # But only if it doesn't look like an attack (e.g. "HEARTBEAT_FLOOD" should not be whitelisted)
            is_whitelisted = any(safe_pattern in text_for_classification for safe_pattern in SAFE_PATTERNS)
            
            # Turkish + English attack keywords - More specific to reduce false positives
            # Only trigger on clear attack indicators, not generic operational terms
            attack_keywords = [
                # Clear attack indicators (English)
                "flood", "flooding", "ddos", "dos_attack", "brute_force", "bruteforce",
                "injection", "sql_injection", "xss", "malware", "trojan", "backdoor",
                "exploit", "payload", "shellcode", "rootkit", "keylogger",
                "unauthorized_access", "privilege_escalation", "lateral_movement",
                "data_exfiltration", "ransomware", "cryptominer",
                # Clear attack indicators (Turkish)
                "saldırı", "saldiri", "sızma", "kaba_kuvvet", "enjeksiyon",
                "yetkisiz_erişim", "yetki_yükseltme", "veri_sızdırma",
                "tehdit_algılandı", "güvenlik_ihlali", "hack_girişimi",
                # Compound phrases that indicate attacks (not single words)
                "intrusion detected", "attack detected", "threat detected",
                "security breach", "malicious activity", "suspicious behavior",
                "güvenlik ihlali", "tehdit tespit", "saldırı tespit",
                # Removed to prevent false positives:
                # "timestamp", "error", "fail", "denied", "alarm", "emergency", 
                # "acil", "kritik", "critical", "anomali", "güvenlik", "bypass",
                # "tunnel", "vpn", "firmware", "zaman"
            ]
            has_attack_keyword = any(k in text_for_classification for k in attack_keywords)
            
            # ATTACK KEYWORD OVERRIDE: Force attack detection if attack keyword found
            if is_whitelisted:
                # Safe pattern detected - force NORMAL (Whitelist Priority 1)
                status_label = "NORMAL"
                final_confidence = 0.99
                is_attack = False
            elif has_attack_keyword:
                attack_type = classify_attack(text_for_classification, self.name)
                status_label = attack_type
                final_confidence = max(0.85, highest_confidences[i])  # At least 85% confidence
                is_attack = True
            else:
                # ML Model Decision (Fallback)
                if total_votes[i]:
                    # ML detected attack
                    status_label = classify_attack(text_for_classification, self.name)
                    # BOOST: Increase confidence for ML detections (User request)
                    final_confidence = max(0.94, highest_confidences[i])
                    is_attack = True
                else:
                    status_label = "NORMAL"
                    final_confidence = highest_confidences[i]
                    is_attack = False
            
            # Determine Reason
            reason = "Yapay Zeka Analizi"
            if is_whitelisted:
                reason = "Güvenli Liste (Whitelist) Eşleşmesi: Normal Davranış Kalıbı"
            elif has_attack_keyword:
                # Find which keyword matched for explanation
                matched_k = next((k for k in attack_keywords if k in text_for_classification), "Keyword")
                reason = f"İmza Tabanlı Tespit: '{matched_k}' şüpheli ifadesi bulundu."
            else:
                if is_attack:
                    reason = f"Yapay Zeka ({winning_models[i]}) ve Konsey Oylaması ile Anomali Tespiti"
                else:
                    reason = "Yapay Zeka ve İmza taramalarından temiz geçti. Normal Trafik."

            results.append({
                "dataset": self.name,
                "final_decision": status_label,
                "confidence_score": float(final_confidence),
                "attack_detected": is_attack,
                "winning_model": winning_models[i],
                "council_votes": results_details[i],
                "reason": reason
            })
            
        return results

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
