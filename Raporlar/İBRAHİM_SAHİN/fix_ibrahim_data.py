"""
İbrahim Şahin Veri Seti Düzeltme Script'i
Bu script output.csv dosyasını okur ve label sütunu ekler.
- Durum = "CRITICAL" veya Olay Tipi = "GÜVENLİK" ise label = 1
- Diğer durumlarda label = 0
"""
import pandas as pd
import os

def process_ibrahim_data():
    # Dosya yolu
    input_file = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\İBRAHİM_SAHİN\output.csv"
    output_file = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\İBRAHİM_SAHİN\output_labeled.csv"
    
    # CSV dosyasını oku
    dataFrame = pd.read_csv(input_file, encoding='utf-8-sig')
    
    # Sütun isimlerini İngilizce'ye çevir
    columnMapping = {
        'Zaman Damgası': 'timestamp',
        'Kaynak (Terminal)': 'source',
        'Olay Tipi': 'event_type',
        'Detay/Değer': 'detail',
        'Durum': 'status'
    }
    dataFrame.rename(columns=columnMapping, inplace=True)
    
    # Label sütunu ekle
    # status = "CRITICAL" veya event_type = "GÜVENLİK" ise anomali (1)
    dataFrame['label'] = dataFrame.apply(
        lambda row: 1 if row['status'] == 'CRITICAL' or row['event_type'] == 'GÜVENLİK' else 0,
        axis=1
    )
    
    # attack_type sütunu ekle
    dataFrame['attack_type'] = dataFrame.apply(
        lambda row: 'TIME_ANOMALY' if row['label'] == 1 else 'NULL',
        axis=1
    )
    
    # Sonuçları kaydet
    dataFrame.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # İstatistikleri yazdır
    totalRows = len(dataFrame)
    anomalyCount = dataFrame['label'].sum()
    normalCount = totalRows - anomalyCount
    
    print(f"İşlenen toplam satır: {totalRows}")
    print(f"Normal kayıt (label=0): {normalCount}")
    print(f"Anomali kayıt (label=1): {anomalyCount}")
    print(f"Dosya kaydedildi: {output_file}")
    
    return dataFrame

if __name__ == "__main__":
    process_ibrahim_data()
