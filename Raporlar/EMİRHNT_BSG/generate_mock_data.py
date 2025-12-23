"""
EMİRHNT Veri Seti Mock Veri Üretme Script'i
Bu script mevcut 21 satırlık veriyi analiz eder ve 
benzer yapıda 1000+ satırlık mock veri üretir.
Anomali oranı: %10-15
"""
import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_emirhnt_mock_data():
    # Dosya yolları
    inputFile = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\EMİRHNT_BSG\logs.txt"
    outputFile = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\EMİRHNT_BSG\logs_expanded.csv"
    
    # Seed for reproducibility
    random.seed(42)
    
    # Parametreler
    TOTAL_ROWS = 1000
    ANOMALY_RATIO = 0.12  # %12 anomali
    
    # Station ID listesi
    stationIdList = [f"ST-{str(i).zfill(3)}" for i in range(1, 100)]
    
    # User ID listesi
    userIdList = [f"U-{str(i).zfill(3)}" for i in range(100, 400)]
    
    # Tarife saatleri
    GUNDUZ_START = 6
    GUNDUZ_END = 22
    
    # Başlangıç tarihi
    startDate = datetime(2025, 11, 10, 8, 0, 0)
    
    mockData = []
    logIdCounter = 1001
    
    for i in range(TOTAL_ROWS):
        # Timestamp oluştur
        currentTimestamp = startDate + timedelta(minutes=random.randint(5, 30) * (i + 1))
        serverTime = currentTimestamp.strftime("%H:%M:%S")
        dateStr = currentTimestamp.strftime("%Y-%m-%d")
        
        # Normal veya anomali karar ver
        isAnomaly = random.random() < ANOMALY_RATIO
        
        if isAnomaly:
            # Anomali senaryosu: Zaman kayması
            # ServerTime gündüz ama LocalTime gece (veya tam tersi)
            serverHour = currentTimestamp.hour
            
            # Saati 12 saat kaydır (gündüz -> gece veya gece -> gündüz)
            shiftedHour = (serverHour + 12) % 24
            localTime = f"{str(shiftedHour).zfill(2)}:{currentTimestamp.strftime('%M:%S')}"
            
            # Tarife tutarsızlığı
            if GUNDUZ_START <= serverHour < GUNDUZ_END:
                uygulananTarife = "GECE"
                olmasiGerekenTarife = "GUNDUZ"
            else:
                uygulananTarife = "GUNDUZ"
                olmasiGerekenTarife = "GECE"
                
            durum = "ANOMALI_ZAMAN_KAYMASI"
            
            # Anomali'de tüketim genelde normal dışı
            tuketimKwh = round(random.uniform(25, 60), 1)
        else:
            # Normal senaryo
            localTime = serverTime
            serverHour = currentTimestamp.hour
            
            if GUNDUZ_START <= serverHour < GUNDUZ_END:
                uygulananTarife = "GUNDUZ"
                olmasiGerekenTarife = "GUNDUZ"
            else:
                uygulananTarife = "GECE"
                olmasiGerekenTarife = "GECE"
                
            durum = "Normal"
            tuketimKwh = round(random.uniform(4, 22), 1)
        
        # Kayıt oluştur
        record = {
            'LogID': logIdCounter,
            'Tarih': dateStr,
            'ServerTime': serverTime,
            'LocalTime': localTime,
            'StationID': random.choice(stationIdList),
            'UserID': random.choice(userIdList),
            'Tuketim_kWh': tuketimKwh,
            'UygulananTarife': uygulananTarife,
            'OlmasiGerekenTarife': olmasiGerekenTarife,
            'Durum': durum,
            'label': 1 if isAnomaly else 0
        }
        
        mockData.append(record)
        logIdCounter += 1
    
    # DataFrame oluştur ve kaydet
    dataFrame = pd.DataFrame(mockData)
    dataFrame.to_csv(outputFile, index=False, encoding='utf-8')
    
    # İstatistikleri yazdır
    totalRows = len(dataFrame)
    anomalyCount = dataFrame['label'].sum()
    normalCount = totalRows - anomalyCount
    
    print(f"Üretilen toplam satır: {totalRows}")
    print(f"Normal kayıt (label=0): {normalCount}")
    print(f"Anomali kayıt (label=1): {anomalyCount}")
    print(f"Anomali oranı: {(anomalyCount/totalRows)*100:.2f}%")
    print(f"Dosya kaydedildi: {outputFile}")
    
    return dataFrame

if __name__ == "__main__":
    generate_emirhnt_mock_data()
