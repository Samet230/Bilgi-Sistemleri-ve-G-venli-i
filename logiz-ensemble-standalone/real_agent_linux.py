
import requests
import time
import sys
import platform
import os
import subprocess
import select

# ==========================================
# AYARLAR
# ==========================================
# Windows bilgisayarınızın IP adresini buraya yazın
# Hata alırsanız: http://192.168.198.1:5050/api/ingest deneyin
TARGET_URL = "http://192.168.198.1:5050/api/ingest"  
HOSTNAME = platform.node()

# İzlenecek Log Dosyaları (Linux için)
LOG_FILES = [
    "/var/log/auth.log",
    "/var/log/syslog",
    "/var/log/messages"  # CentOS/RHEL için
]

def get_valid_log_file():
    """Sistemde mevcut olan ilk log dosyasını bulur."""
    for log_file in LOG_FILES:
        if os.path.exists(log_file):
            return log_file
    return None

def follow(filename):
    """'tail -f' benzeri dosya takip fonksiyonu"""
    try:
        f = subprocess.Popen(['tail', '-F', '-n', '0', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        while True:
            if p.poll(1):
                line = f.stdout.readline()
                if line:
                    yield line.decode('utf-8', errors='replace').strip()
            time.sleep(0.1)
    except Exception as e:
        print(f"Hata (Tail): {e}")

def send_log(line):
    if not line: return
    
    try:
        payload = {
            "log": line,
            "source": HOSTNAME,
            "timestamp": time.time()
        }
        # Timeout kısa tutulur ki log akışı tıkanmasın
        resp = requests.post(TARGET_URL, json=payload, timeout=2)
        
        status_icon = "🟢" if resp.status_code == 201 else f"🔴 [{resp.status_code}]"
        # Sadece hata veya saldırı varsa veya verbose istenirse yazdırılabilir
        # Şimdilik her gönderimi yazalım ama kısa olsun
        print(f"{status_icon} {line[:80]}...")
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Bağlantı Hatası! Windows'a ulaşılamıyor.")
    except Exception as e:
        print(f"❌ Gönderim Hatası: {e}")

def main():
    print("\n" + "="*50)
    print(f"🛡️  LogIz GERÇEK Ajan Başlatıldı (Real-Time)")
    print(f"📡 Hedef: {TARGET_URL}")
    print(f"💻 Host: {HOSTNAME}")
    print("="*50 + "\n")

    target_log = get_valid_log_file()
    if not target_log:
        print("❌ HATA: İzlenecek uygun log dosyası (/var/log/auth.log vb.) bulunamadı!")
        print("   -> Linux tabanlı bir sistemde olduğunuza emin olun.")
        sys.exit(1)

    print(f"📂 İzleniyor: {target_log}")
    print("Log akışı bekleniyor... (Sistemde bir aktivite yapmayı deneyin)\n")

    try:
        # Permission check
        if not os.access(target_log, os.R_OK):
            print(f"🚫 UYARI: {target_log} dosyasına okuma izniniz yok.")
            print("   -> 'sudo python3 agent.py' komutuyla çalıştırmayı deneyin.")
            sys.exit(1)

        for line in follow(target_log):
            send_log(line)
            
    except KeyboardInterrupt:
        print("\n🛑 Ajan durduruldu.")

if __name__ == "__main__":
    main()
