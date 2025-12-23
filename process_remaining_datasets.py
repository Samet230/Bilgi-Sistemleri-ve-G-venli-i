"""
Samet ve Emirhan BSG Log İşleme Scripti
Bu script:
1. SAMET_SAHIN klasöründeki ids_guvenlik_logu.txt dosyasını regex ile parse eder.
2. EMİRHAN_BSG klasöründeki logs_5000.json dosyasını okur ve CSV formatına dönüştürür.
Her iki çıktı da ML eğitimi için hazır formatta (etiketli CSV) kaydedilir.
"""

import pandas as pd
import re
import json
import os

# --- Konfigürasyon ---
SAMET_INPUT_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_logu.txt"
SAMET_OUTPUT_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv"

EMIRHAN_INPUT_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\EMİRHAN_BSG\LOG\logs_5000.json"
EMIRHAN_OUTPUT_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv"

def process_samet_logs():
    print(f"İşleniyor: {SAMET_INPUT_PATH}")
    
    # Regex Paternleri
    # Örnek: [2025-12-20 23:10:59] [SALDIRI] UYARI: Yan Hareket / Ağ Keşfi | Aksiyon: Bloklandı | ID: 0xcc
    log_pattern = re.compile(r'^\[(.*?)\] \[(.*?)\] (.*?) \| (.*?) \| ID: (.*?)$')
    
    records = []
    
    try:
        with open(SAMET_INPUT_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                match = log_pattern.match(line)
                if match:
                    timestamp = match.group(1)
                    level = match.group(2) # NORMAL veya SALDIRI
                    message_part = match.group(3)
                    action_part = match.group(4) # Durum: OK veya Aksiyon: Bloklandı
                    id_val = match.group(5)
                    
                    # Detayları ayrıştır
                    if level == 'SALDIRI':
                        # Mesaj: "UYARI: Yan Hareket / Ağ Keşfi" -> Tip: UYARI, Detay: Yan Hareket...
                        if ": " in message_part:
                            severity, detail = message_part.split(": ", 1)
                        else:
                            severity, detail = "UNKNOWN", message_part
                            
                        # Aksiyon
                        action = action_part.replace("Aksiyon: ", "")
                        label = 1
                    else:
                        severity = "INFO"
                        detail = message_part
                        action = action_part.replace("Durum: ", "")
                        label = 0
                    
                    records.append({
                        'timestamp': timestamp,
                        'level': level,
                        'severity': severity,
                        'detail': detail,
                        'action': action,
                        'id': id_val,
                        'label': label
                    })
                    
        df = pd.DataFrame(records)
        df.to_csv(SAMET_OUTPUT_PATH, index=False, encoding='utf-8')
        print(f"✅ Samet logs processed. Total: {len(df)}, Anomalies: {df['label'].sum()}")
        print(f"Output: {SAMET_OUTPUT_PATH}\n")
        
    except Exception as e:
        print(f"❌ Error processing Samet logs: {e}")

def process_emirhan_logs():
    print(f"İşleniyor: {EMIRHAN_INPUT_PATH}")
    
    try:
        with open(EMIRHAN_INPUT_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # JSON yapısını düzleştir (flatten)
        # Eğer liste değilse listeye çevir
        if isinstance(data, dict):
            data = [data]
            
        processed_data = []
        for entry in data:
            # Temel alanları al
            # JSON yapısı: timestamp, label, severity, stage, event, action, rule_id, ...
            flat_entry = {
                'timestamp': entry.get('timestamp'),
                'level': entry.get('label'), # Orijinal JSON'da 'label': SALDIRI/NORMAL
                'severity': entry.get('severity'),
                'message': entry.get('event'), # 'event' alanı mesaj içeriği
                'action': entry.get('action'),
                'stage': entry.get('stage'),
                'rule_id': entry.get('rule_id'),
                'source_ip': entry.get('network', {}).get('src_ip'),
                'source_port': entry.get('network', {}).get('src_port'),
                'dest_ip': entry.get('network', {}).get('dst_ip'),
                'dest_port': entry.get('network', {}).get('dst_port'),
                'http_method': entry.get('http', {}).get('method'),
                'http_path': entry.get('http', {}).get('path'),
                'http_status': entry.get('http', {}).get('status'),
                'ocp_namespace': entry.get('ocp', {}).get('namespace'),
                'ocp_pod': entry.get('ocp', {}).get('pod')
            }
            
            # Label belirle (ML için 0/1)
            # Orijinal 'label' alanı zaten 'SALDIRI' veya 'NORMAL'
            if entry.get('label') == 'SALDIRI':
                flat_entry['label'] = 1
            else:
                flat_entry['label'] = 0
                
            processed_data.append(flat_entry)
            
        df = pd.DataFrame(processed_data)
        df.to_csv(EMIRHAN_OUTPUT_PATH, index=False, encoding='utf-8')
        print(f"✅ Emirhan logs processed. Total: {len(df)}, Anomalies: {df['label'].sum()}")
        print(f"Output: {EMIRHAN_OUTPUT_PATH}\n")
        
    except Exception as e:
        print(f"❌ Error processing Emirhan logs: {e}")

if __name__ == "__main__":
    process_samet_logs()
    process_emirhan_logs()
