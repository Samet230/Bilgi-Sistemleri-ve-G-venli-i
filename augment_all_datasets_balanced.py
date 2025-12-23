import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

def augment_dataset(name, path, attack_patterns, normal_patterns, count=1000):
    """Augmented with 1:1 ratio for balance."""
    full_path = os.path.join(BASE_PATH, path)
    if not os.path.exists(full_path):
        print(f"Skipped {name}: {full_path} not found")
        return

    df = pd.read_csv(full_path)
    print(f"Augmenting {name} (Current: {len(df)})")
    
    new_rows = []
    half = count // 2
    
    # 1. Add ATTACKS
    for _ in range(half):
        pattern = random.choice(attack_patterns)
        row = pattern.copy()
        row['label'] = 1
        new_rows.append(row)

    # 2. Add HARD NORMALS
    for _ in range(half):
        pattern = random.choice(normal_patterns)
        row = pattern.copy()
        row['label'] = 0
        new_rows.append(row)

    df_new = pd.DataFrame(new_rows)
    # Standardize column existence
    for col in df.columns:
        if col not in df_new.columns:
            if df[col].dtype in [np.float64, np.int64]: df_new[col] = 0
            else: df_new[col] = "normal"
            
    df_final = pd.concat([df, df_new], ignore_index=True)
    df_final.to_csv(full_path, index=False)
    print(f"Done {name}. Final size: {len(df_final)}")

def run_balanced_augmentation():
    # 1. SAMET
    augment_dataset("SAMET", r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv", [
        {"level": "SALDIRI", "detail": "Brute Force attempt - multiple failed login", "action": "Bloklandı"},
        {"level": "SALDIRI", "detail": "Reverse Shell detected on port 4444", "action": "Bloklandı"},
        {"level": "SALDIRI", "detail": "Data Exfiltration: large encrypted zip upload", "action": "Bloklandı"}
    ], [
        {"level": "NORMAL", "detail": "User authenticated successfully", "action": "OK"},
        {"level": "NORMAL", "detail": "Daily system backup started", "action": "OK"},
        {"level": "NORMAL", "detail": "NTP time sync completed", "action": "OK"}
    ])

    # 2. EMİRHAN
    augment_dataset("EMİRHAN", r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv", [
        {"message": "SQLi: ' OR '1'='1"},
        {"message": "XSS: <script>"},
        {"message": "Log4Shell: ${jndi:"}
    ], [
        {"message": "GET /api/public/search?q=test"},
        {"message": "POST /login HTTP/1.1 200"},
        {"message": "Static content served: logo.png"}
    ])

    # 3. İBRAHİM
    augment_dataset("İBRAHİM", r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv", [
        {"attack_type": "TIME_ANOMALY", "detail": "Zaman Kayması > 1 saat", "status": "CRITICAL"},
        {"attack_type": "TIME_ANOMALY", "detail": "Clock reset to 1970", "status": "CRITICAL"}
    ], [
        {"attack_type": "NULL", "detail": "Sync Success", "status": "Normal"},
        {"attack_type": "NULL", "detail": "Minor drift corrected: 0.1s", "status": "Normal"}
    ])

    # 4. MİRAÇ
    augment_dataset("MİRAÇ", r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv", [
        {"reason": "REUSED_PLATE", "input_plate": "06XXX01"},
        {"reason": "SQL_INJECTION", "input_plate": "'; DROP"}
    ], [
        {"reason": "Basarili", "input_plate": "34ABC12"},
        {"reason": "Basarili", "input_plate": "06DEF56"}
    ])

    # 5. ALİ
    augment_dataset("ALİ", r"Raporlar\ALİ_GİRİŞ_BSG\ali_logs_parsed.csv", [
        {"action": "RemoteStopTransaction", "status": "FORCE_STOP"},
        {"action": "UnlockConnector", "status": "UNAUTHORIZED"}
    ], [
        {"action": "Heartbeat", "status": "NORMAL"},
        {"action": "MeterValues", "status": "NORMAL"},
        {"action": "BootNotification", "status": "NORMAL"}
    ])

if __name__ == "__main__":
    # We overwrite the previous imbalanced augmentation by reading the files again
    # Note: These files are already larger now, we are adding another 1000 records.
    # Total size will be ~2500-3000 which is good for training stability.
    run_balanced_augmentation()
    print("\n✅ Balanced Mass Augmentation Complete.")
