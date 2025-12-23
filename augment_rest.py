import pandas as pd
import random
import os
from datetime import datetime, timedelta

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

# 1. YOUSEF AUGMENTATION
YOUSEF_FILE = os.path.join(BASE_PATH, r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv")

def augment_yousef():
    if not os.path.exists(YOUSEF_FILE): return
    df = pd.read_csv(YOUSEF_FILE)
    print(f"Yousef Original Size: {len(df)}")
    
    # Yousef issue: 'Faulted' is attack. 'Available' is normal.
    # Needs more diverse 'Normal' states (Preparing, Charging, SuspendedEV) without attack tags.
    
    new_rows = []
    base_time = datetime.now()
    possible_statuses = ["Available", "Preparing", "Charging", "SuspendedEV", "Finishing"]
    possible_messages = ["Heartbeat", "MeterValues", "StatusNotification", "BootNotification", "Authorize"]
    
    for i in range(500):
        status = random.choice(possible_statuses)
        msg = random.choice(possible_messages)
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "station_id": f"CS-{random.randint(100,200)}",
            "status": status,
            "ocpp_message": msg,
            "label": 0, # Normal
            # Dummy fillers for other columns if they exist
            "connector_id": 1,
            "time_delta_ms": random.randint(100, 5000),
            "attack_type": "None",
            "event_type": "Normal"
        })
        
    df_new = pd.DataFrame(new_rows)
    # Align columns
    for col in df.columns:
        if col not in df_new.columns:
            df_new[col] = 0
            
    df_augmented = pd.concat([df, df_new[df.columns]], ignore_index=True)
    
    # --- ATTACK AUGMENTATION (Balancing) ---
    attack_rows = []
    attacks = ["PRICE_SPIKE", "LATERAL_MOVEMENT", "TLS_DOWGRADE_DETECTED", "REMOTE_ACCESS"]
    for i in range(200):
        status = "Faulted"
        msg = random.choice(possible_messages)
        new_row = {
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "station_id": f"CS-ATTACK-{random.randint(1,50)}",
            "status": status,
            "ocpp_message": msg,
            "label": 1, # Attack
            "connector_id": 1,
            "time_delta_ms": random.randint(100, 5000),
            "attack_type": random.choice(attacks),
            "event_type": "Security"
        }
        attack_rows.append(new_row)
    
    df_attacks = pd.DataFrame(attack_rows)
    # Ensure cols align
    for col in df.columns:
        if col not in df_attacks.columns:
            df_attacks[col] = 0
            
    df_final = pd.concat([df_augmented, df_attacks[df.columns]], ignore_index=True)
    df_final.to_csv(YOUSEF_FILE, index=False)
    print(f"Yousef Augmented Size: {len(df_final)} (Balanced)")

# 2. ATAKAN AUGMENTATION
ATAKAN_FILE = os.path.join(BASE_PATH, r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv")

def augment_atakan():
    if not os.path.exists(ATAKAN_FILE): return
    df = pd.read_csv(ATAKAN_FILE)
    print(f"Atakan Original Size: {len(df)}")
    
    new_rows = []
    base_time = datetime.now()
    
    # Normals
    for i in range(500):
        load = round(random.uniform(0.1, 10.9), 2)
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "load_kw": load,
            "label": 0,
            "attack_type": "Normal",
            "event_type": "LoadReading",
            "source": "Grid"
        })
        
    # --- ATTACK AUGMENTATION ---
    for i in range(200):
        load = round(random.uniform(11.1, 20.0), 2) # High load
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "load_kw": load,
            "label": 1,
            "attack_type": "LOAD_MANIPULATION",
            "event_type": "LoadReading",
            "source": "Grid"
        })
        
    df_new = pd.DataFrame(new_rows)
    for col in df.columns:
        if col not in df_new.columns:
            df_new[col] = "0"
            
    df_augmented = pd.concat([df, df_new[df.columns]], ignore_index=True)
    df_augmented.to_csv(ATAKAN_FILE, index=False)
    print(f"Atakan Augmented Size: {len(df_augmented)} (Balanced)")

# 3. MİRAÇ AUGMENTATION
MIRAC_FILE = os.path.join(BASE_PATH, r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv")

def augment_mirac():
    if not os.path.exists(MIRAC_FILE): return
    df = pd.read_csv(MIRAC_FILE)
    print(f"Miraç Original Size: {len(df)}")
    
    names = ["Ali", "Veli", "Ayse", "Fatma", "John", "Doe", "TestUser", "Admin", "User1", "Guest"]
    plates = ["34AB123", "06CD456", "35EF789", "01GH012", "55KL345"]
    reasons = ["Basarili", "Onaylandi", "Giris Yapildi", "Kayit OK"]
    
    new_rows = []
    base_time = datetime.now()
    
    # Normals
    for i in range(500):
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "input_name": random.choice(names),
            "input_plate": random.choice(plates),
            "reason": random.choice(reasons),
            "label": 0,
            "energy_kwh": 0, "duration_min": 0, "avg_power_kw": 0
        })
        
    # --- ATTACK AUGMENTATION ---
    for i in range(200):
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "input_name": f"Attacker_{i}",
            "input_plate": "FAKE_PLATE",
            "reason": "YANLIS_PLAKA",
            "label": 1,
            "energy_kwh": 0, "duration_min": 0, "avg_power_kw": 0
        })
        
    df_new = pd.DataFrame(new_rows)
    for col in df.columns:
        if col not in df_new.columns:
            df_new[col] = 0
            
    df_augmented = pd.concat([df, df_new[df.columns]], ignore_index=True)
    df_augmented.to_csv(MIRAC_FILE, index=False)
    print(f"Miraç Augmented Size: {len(df_augmented)} (Balanced)")

if __name__ == "__main__":
    augment_yousef()
    augment_atakan()
    augment_mirac()
