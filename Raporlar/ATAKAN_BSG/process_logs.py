"""
ATAKAN_BSG Log Parsing ve Mock Data Generation Script
Bu script execution_logs.txt dosyasını parse eder ve ML eğitimine uygun CSV oluşturur.
Anomali: Yük değeri > 10 kW (Normal: 3.6 kW, Saldırı: 11.2 kW)
"""
import pandas as pd
import re
import random
from datetime import datetime, timedelta
import os

def parse_atakan_logs():
    """Atakan'ın log dosyasını parse et ve CSV'ye dönüştür"""
    
    inputFile = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\execution_logs.txt"
    outputFile = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\parsed_logs.csv"
    
    # Regex patterns
    meterValuePattern = r'\[(\w+)\] MeterValues: \{.*?"value": "(\d+\.?\d*)".*?"unit": "(\w+)"'
    timestampPattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    levelPattern = r' - (\w+) - '
    
    records = []
    
    with open(inputFile, 'r', encoding='utf-8') as file:
        for lineNumber, line in enumerate(file, 1):
            # Timestamp çıkar
            timestampMatch = re.search(timestampPattern, line)
            logTimestamp = timestampMatch.group(1) if timestampMatch else None
            
            # Log level çıkar
            levelMatch = re.search(levelPattern, line)
            logLevel = levelMatch.group(1) if levelMatch else "INFO"
            
            # MeterValues mesajlarını bul
            meterMatch = re.search(meterValuePattern, line)
            if meterMatch:
                source = meterMatch.group(1)
                loadValue = float(meterMatch.group(2))
                unit = meterMatch.group(3)
                
                # Anomali tespiti: > 10 kW ise saldırı
                isAnomaly = 1 if loadValue > 10.0 else 0
                attackType = "LOAD_MANIPULATION" if isAnomaly else "NULL"
                
                record = {
                    'timestamp': logTimestamp,
                    'source': source,
                    'event_type': 'MeterValues',
                    'load_kw': loadValue,
                    'unit': unit,
                    'log_level': logLevel,
                    'attack_type': attackType,
                    'label': isAnomaly
                }
                records.append(record)
            
            # ALARM mesajlarını bul
            elif 'ALARM' in line or 'ACİL DURUM' in line:
                record = {
                    'timestamp': logTimestamp,
                    'source': 'MERKEZ' if 'ALARM' in line else 'SCADA',
                    'event_type': 'ALARM' if 'ALARM' in line else 'EMERGENCY',
                    'load_kw': None,
                    'unit': None,
                    'log_level': 'WARNING' if 'ALARM' in line else 'ERROR',
                    'attack_type': 'LOAD_MANIPULATION',
                    'label': 1
                }
                records.append(record)
    
    # DataFrame oluştur
    dataFrame = pd.DataFrame(records)
    dataFrame.to_csv(outputFile, index=False, encoding='utf-8')
    
    # İstatistikler
    totalRows = len(dataFrame)
    anomalyCount = dataFrame['label'].sum()
    normalCount = totalRows - anomalyCount
    
    print(f"Parse edilen toplam kayıt: {totalRows}")
    print(f"Normal kayıt (label=0): {normalCount}")
    print(f"Anomali kayıt (label=1): {anomalyCount}")
    print(f"Dosya kaydedildi: {outputFile}")
    
    return dataFrame


def generate_atakan_mock_data():
    """Atakan'ın veri setini genişletmek için mock data üret"""
    
    outputFile = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv"
    
    random.seed(42)
    
    TOTAL_ROWS = 1000
    ANOMALY_RATIO = 0.12  # %12 anomali
    
    # Normal yük değerleri: 3.0 - 7.2 kW arası
    # Saldırı yük değerleri: 10.5 - 15.0 kW arası (eşik: 10.0 kW)
    
    startDate = datetime(2025, 12, 22, 8, 0, 0)
    
    mockData = []
    
    for i in range(TOTAL_ROWS):
        currentTimestamp = startDate + timedelta(minutes=random.randint(1, 5) * (i + 1))
        
        isAnomaly = random.random() < ANOMALY_RATIO
        
        if isAnomaly:
            # Saldırı senaryosu: Yüksek yük değeri
            loadValue = round(random.uniform(10.5, 15.0), 1)
            source = random.choice(["SALDIRGAN", "İSTASYON"])  # Saldırgan veya compromised istasyon
            attackType = "LOAD_MANIPULATION"
            logLevel = "WARNING"
        else:
            # Normal senaryo
            loadValue = round(random.uniform(3.0, 7.2), 1)
            source = "İSTASYON"
            attackType = "NULL"
            logLevel = "INFO"
        
        record = {
            'timestamp': currentTimestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'source': source,
            'event_type': 'MeterValues',
            'load_kw': loadValue,
            'unit': 'kW',
            'log_level': logLevel,
            'attack_type': attackType,
            'label': 1 if isAnomaly else 0
        }
        
        mockData.append(record)
    
    # DataFrame oluştur ve kaydet
    dataFrame = pd.DataFrame(mockData)
    dataFrame.to_csv(outputFile, index=False, encoding='utf-8')
    
    # İstatistikler
    totalRows = len(dataFrame)
    anomalyCount = dataFrame['label'].sum()
    normalCount = totalRows - anomalyCount
    
    print(f"\nÜretilen toplam satır: {totalRows}")
    print(f"Normal kayıt (label=0): {normalCount}")
    print(f"Anomali kayıt (label=1): {anomalyCount}")
    print(f"Anomali oranı: {(anomalyCount/totalRows)*100:.2f}%")
    print(f"Dosya kaydedildi: {outputFile}")
    
    return dataFrame


if __name__ == "__main__":
    print("=" * 60)
    print("ATAKAN_BSG Log İşleme")
    print("=" * 60)
    
    print("\n1. Mevcut log dosyasını parse ediyorum...")
    parse_atakan_logs()
    
    print("\n2. Mock data üretiyorum...")
    generate_atakan_mock_data()
    
    print("\n" + "=" * 60)
    print("İşlem tamamlandı!")
    print("=" * 60)
