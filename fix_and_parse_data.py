import pandas as pd
import re
import os

BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

# ===============================================
# 1. FIX İBRAHİM LABELS
# ===============================================
IBRAHIM_FILE = os.path.join(BASE_PATH, r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv")

def fix_ibrahim_labels():
    print("İbrahim düzeltiliyor...")
    df = pd.read_csv(IBRAHIM_FILE)
    
    original_attack_count = df['label'].sum()
    
    # Fix: If source is 'SALDIRGAN' or event_type contains 'Sald', set label to 1
    mask = (
        (df['source'].str.contains('SALDIRGAN', case=False, na=False)) |
        (df['event_type'].str.contains('Sald', case=False, na=False))
    )
    df.loc[mask, 'label'] = 1
    
    new_attack_count = df['label'].sum()
    
    df.to_csv(IBRAHIM_FILE, index=False)
    print(f"  Düzeltildi: {original_attack_count} -> {new_attack_count} saldırı kaydı")

# ===============================================
# 2. PARSE ALI'S LOGS TO CSV
# ===============================================
ALI_LOG_FILE = os.path.join(BASE_PATH, r"Raporlar\ALİ_GİRİŞ_BSG\1000 log kayıtları.txt")
ALI_CSV_FILE = os.path.join(BASE_PATH, r"Raporlar\ALİ_GİRİŞ_BSG\ali_logs_parsed.csv")

def parse_ali_logs():
    print("Ali logları CSV'ye dönüştürülüyor...")
    
    # Log format: [TIMESTAMP] [STATUS] [JSON_ARRAY]
    # Example: [2025-12-23 10:45:00] [NORMAL] [2, "0", "Heartbeat", {}]
    
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(NORMAL|ANOMALY)\] \[\d+, "(\d+)", "(\w+)", (\{.*?\})\]'
    
    rows = []
    with open(ALI_LOG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = re.findall(pattern, content)
    
    for match in matches:
        timestamp, status, message_id, action, payload = match
        label = 1 if status == "ANOMALY" else 0
        
        # Extract transactionId if present
        transaction_id = ""
        if "transactionId" in payload:
            tid_match = re.search(r'"transactionId":\s*(\d+)', payload)
            if tid_match:
                transaction_id = tid_match.group(1)
        
        rows.append({
            "timestamp": timestamp,
            "status": status,
            "message_id": message_id,
            "action": action,
            "transaction_id": transaction_id,
            "label": label
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(ALI_CSV_FILE, index=False)
    
    normal_count = len(df[df['label'] == 0])
    attack_count = len(df[df['label'] == 1])
    print(f"  Dönüştürüldü: {len(df)} kayıt ({normal_count} Normal, {attack_count} Anomaly)")
    print(f"  Dosya: {ALI_CSV_FILE}")

if __name__ == "__main__":
    fix_ibrahim_labels()
    parse_ali_logs()
    print("\nTüm düzeltmeler tamamlandı!")
