import requests
import json
import os
import time

# Configuration
API_URL = "http://localhost:5050/api/analyze/upload"
TEST_FILE = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv"

def run_demo():
    print(f"🚀 Demo Başlatılıyor...")
    print(f"📡 API Hedefi: {API_URL}")
    print(f"📂 Test Dosyası: {TEST_FILE}")
    
    if not os.path.exists(TEST_FILE):
        print("❌ Hata: Test dosyası bulunamadı!")
        return

    try:
        # Prepare the upload
        files = {'file': open(TEST_FILE, 'rb')}
        
        print("\n⏳ Dosya yükleniyor ve analiz ediliyor (Ensemble AI)...")
        start_time = time.time()
        
        response = requests.post(API_URL, files=files)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ BAŞARILI! Analiz Sonuçları:")
            print("="*50)
            print(f"⏱️ Süre: {duration:.2f} saniye")
            print(f"🆔 Job ID: {result.get('job_id')}")
            
            stats = result.get('results', {})
            print(f"🤖 Kullanılan Model: {stats.get('model_used', 'Bilinmiyor')}")
            print(f"📊 Toplam Kayıt: {stats.get('total_records')}")
            print(f"🔴 Tespit Edilen Saldırı: {stats.get('attacks_detected')}")
            print(f"🟢 Normal Trafik: {stats.get('normal_traffic')}")
            print("="*50)
            print("\n💡 Not: Bu sonuçlar backend veritabanına kaydedildi.")
        else:
            print(f"\n❌ HATA: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Bağlantı Hatası: {e}")
        print("Backend sunucusunun çalıştığından emin olun (port 5050).")

if __name__ == "__main__":
    run_demo()
