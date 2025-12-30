#!/usr/bin/env python3
"""
LogIz Canlı İzleme Client - SAMET IDS Test Ortamı İçin
======================================================
Bu script, Ubuntu'daki IDS loglarını LogIz sunucusuna gerçek zamanlı gönderir.

Kullanım:
1. LogIz backend sunucusunu başlatın (Windows/Ubuntu'da python app.py)
2. Bu scripti Ubuntu'da çalıştırın
3. Dashboard'dan "Canlı İzleme" sekmesini açın
"""

import requests
import time
import os

# ==================== AYARLAR ====================
# LogIz sunucusunun IP adresi (değiştirin)
# Eğer aynı makinede: http://localhost:5050
# Eğer farklı makinede: http://192.168.1.X:5050
LOGIZ_SERVER = os.getenv('LOGIZ_SERVER', 'http://localhost:5050')

# Kaynak adı (dashboard'da görünecek)
SOURCE_NAME = 'SAMET_IDS_UBUNTU'

# Gönderim aralığı (saniye)
SEND_INTERVAL = 0.5
# ==================================================


def send_log(log_line: str):
    """Tek bir log satırını LogIz'e gönderir."""
    try:
        response = requests.post(
            f'{LOGIZ_SERVER}/api/ingest',
            json={
                'log': log_line,
                'source': SOURCE_NAME,
                'timestamp': time.time()
            },
            timeout=5
        )
        if response.status_code in [200, 201]:
            result = response.json()
            analysis = result.get('analysis', 'N/A')
            print(f"✅ Gönderildi: {log_line[:50]}... -> {analysis}")
            return True
        else:
            print(f"❌ Hata ({response.status_code}): {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"🔌 Bağlantı hatası: {e}")
        return False


def watch_log_file(file_path: str):
    """Log dosyasını izler ve yeni satırları gerçek zamanlı gönderir."""
    print(f"📂 Log dosyası izleniyor: {file_path}")
    print(f"🌐 LogIz Sunucusu: {LOGIZ_SERVER}")
    print("=" * 50)
    
    with open(file_path, 'r') as f:
        # Dosyanın sonuna git (sadece yeni satırları al)
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                line = line.strip()
                if line:  # Boş satırları atla
                    send_log(line)
            else:
                time.sleep(SEND_INTERVAL)


def watch_can_bus():
    """CAN Bus mesajlarını izler (vcan0) - live_ids_detector.py entegrasyonu."""
    try:
        import can
        bus = can.Bus(channel='vcan0', interface='socketcan')
        print("🚗 CAN Bus (vcan0) izleniyor...")
        print(f"🌐 LogIz Sunucusu: {LOGIZ_SERVER}")
        print("=" * 50)
        
        for msg in bus:
            log_line = f"CAN ID: 0x{msg.arbitration_id:03X} | Data: {msg.data.hex()}"
            send_log(log_line)
            
    except ImportError:
        print("❌ python-can kütüphanesi yüklü değil. 'pip install python-can' ile yükleyin.")
    except Exception as e:
        print(f"❌ CAN Bus hatası: {e}")


if __name__ == '__main__':
    import sys
    
    print("=" * 50)
    print("   LogIz Canlı İzleme Client v1.0")
    print("   SAMET IDS Ubuntu Test Ortamı")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nKullanım:")
        print("  1. Log dosyası izleme:")
        print("     python logiz_live_client.py /path/to/ids_guvenlik_logu.txt")
        print("")
        print("  2. CAN Bus izleme:")
        print("     python logiz_live_client.py --can")
        print("")
        print("Ortam Değişkenleri:")
        print("  LOGIZ_SERVER=http://192.168.1.X:5050")
        sys.exit(1)
    
    if sys.argv[1] == '--can':
        watch_can_bus()
    else:
        log_file = sys.argv[1]
        if not os.path.exists(log_file):
            print(f"❌ Dosya bulunamadı: {log_file}")
            sys.exit(1)
        watch_log_file(log_file)
