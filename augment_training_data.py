import pandas as pd
import random
import os
from datetime import datetime, timedelta

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

# 1. SAMET AUGMENTATION
SAMET_FILE = os.path.join(BASE_PATH, r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv")

def augment_samet():
    if not os.path.exists(SAMET_FILE):
        print(f"File not found: {SAMET_FILE}")
        return

    df = pd.read_csv(SAMET_FILE)
    print(f"Samet Original Size: {len(df)}")
    
    # New Normal Messages to teach variety
    new_messages = [
        "Standart sistem kontrolü",
        "Rutin Veri Akışı",
        "Bağlantı Kontrolü Başarılı",
        "Sunucu Yanıtı OK",
        "Ağ Trafiği Stabil",
        "Kullanıcı Oturumu Açıldı",
        "Ping Yanıtı Alındı",
        "Veri Tabanı Bağlantısı Normal",
        "Sistem Sağlık Taraması Temiz",
        "Normal Operasyon"
    ]
    
    new_rows = []
    base_time = datetime.now()
    
    for i in range(500): # Add 500 diverse normal logs
        msg = random.choice(new_messages)
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "level": "NORMAL",
            "severity": "INFO",
            "detail": msg,
            "action": "OK",
            "id": "0x301", # Dummy ID
            "label": 0
        })
        
    df_new = pd.DataFrame(new_rows)
    df_augmented = pd.concat([df, df_new], ignore_index=True)
    
    df_augmented.to_csv(SAMET_FILE, index=False)
    print(f"Samet Augmented Size: {len(df_augmented)}")

# 2. SUZAN AUGMENTATION
SUZAN_FILE = os.path.join(BASE_PATH, r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv")

def augment_suzan():
    if not os.path.exists(SUZAN_FILE):
        return

    df = pd.read_csv(SUZAN_FILE)
    print(f"Suzan Original Size: {len(df)}")
    
    # Add Normal "MeterValues" with prices slightly higher than 0.3 but less than attack(2.0)
    # Range 0.3 - 0.7 to teach that 0.5 is OK.
    
    new_rows = []
    base_time = datetime.now()
    
    for i in range(500): 
        price = random.uniform(0.3, 0.7)
        new_rows.append({
            "timestamp": (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "station_id": f"CP-{random.randint(1,10):02d}",
            "connector_id": 1,
            "ocpp_message": "MeterValues", # Teach that this message can be normal
            "status": "Charging",
            "price_eur_kwh": round(price, 4),
            "energy_kwh": round(random.uniform(5, 20), 3),
            "power_kw": round(random.uniform(10, 22), 2),
            "reason": "normal",
            "label": 0
        })
        
    df_new = pd.DataFrame(new_rows)
    df_augmented = pd.concat([df, df_new], ignore_index=True)
    
    df_augmented.to_csv(SUZAN_FILE, index=False)
    print(f"Suzan Augmented Size: {len(df_augmented)}")

if __name__ == "__main__":
    augment_samet()
    augment_suzan()
