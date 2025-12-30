#!/usr/bin/env python3
"""
Anomi Esnek Ajan - Kendi Test Senaryolarınız İçin
=================================================
Bu ajan iki modda çalışabilir:

1. DOSYA MODU: Belirttiğiniz bir log dosyasını izler.
   python agent.py --file /path/to/your/test_output.log

2. STDIN MODU: Test scriptinizin çıktısını doğrudan alır (pipe).
   python test_charging_anomaly.py | python agent.py

Her iki durumda da veriler anında Canlı İzleme ekranına yansır.
"""

import requests
import time
import sys
import platform
import argparse
import os

# ==========================================
# AYARLAR - Windows IP Adresinizi Buraya Yazın
# ==========================================
TARGET_URL = "http://192.168.198.1:5050/api/ingest"
HOSTNAME = platform.node()

def send_log(line):
    """Logu backend'e gönderir."""
    if not line or not line.strip():
        return
    
    line = line.strip()
    
    try:
        payload = {
            "log": line,
            "source": HOSTNAME,
            "timestamp": time.time()
        }
        resp = requests.post(TARGET_URL, json=payload, timeout=2)
        
        # Kısa çıktı
        status = "🟢" if resp.status_code == 201 else f"🔴 [{resp.status_code}]"
        print(f"{status} {line[:70]}...")
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Bağlantı Hatası! Windows'a ulaşılamıyor.")
    except Exception as e:
        print(f"❌ Hata: {e}")

def follow_file(filepath):
    """Dosyayı tail -f gibi izler."""
    print(f"📂 Dosya izleniyor: {filepath}")
    
    with open(filepath, 'r') as f:
        # Dosya sonuna git
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.1)

def read_stdin():
    """STDIN'den satır satır okur."""
    print("📥 STDIN bekleniyor... (Test scriptinizi pipe edin)")
    
    for line in sys.stdin:
        yield line

def main():
    parser = argparse.ArgumentParser(description="Anomi Esnek Ajan")
    parser.add_argument('--file', '-f', type=str, help="İzlenecek log dosyası yolu")
    args = parser.parse_args()

    print("\n" + "="*50)
    print("🔌 Anomi Esnek Ajan Başlatıldı")
    print(f"📡 Hedef: {TARGET_URL}")
    print(f"💻 Host: {HOSTNAME}")
    print("="*50 + "\n")

    try:
        if args.file:
            # Dosya Modu
            if not os.path.exists(args.file):
                print(f"❌ Dosya bulunamadı: {args.file}")
                sys.exit(1)
            
            for line in follow_file(args.file):
                send_log(line)
        else:
            # STDIN Modu
            for line in read_stdin():
                send_log(line)
                
    except KeyboardInterrupt:
        print("\n🛑 Ajan durduruldu.")

if __name__ == "__main__":
    main()
