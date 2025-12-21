import can
import time
from sklearn.ensemble import IsolationForest
from collections import deque
from datetime import datetime
import random # Normal logları biraz azaltmak için (isteğe bağlı)

# --- AYARLAR ---
data_buffer = deque(maxlen=300)
model = IsolationForest(contamination=0.05, random_state=42)
LOG_FILE = "ids_guvenlik_logu.txt"
counter = 0 

try:
    bus = can.Bus(channel='vcan0', interface='socketcan')
    print("--- DEDEKTİF (VERİ TOPLAMA MODU): NORMAL + SALDIRI ---")
except OSError:
    print("HATA: vcan0 arayüzü bulunamadı!")
    exit(1)

try:
    while True:
        msg = bus.recv()
        if msg is None: continue
        
        counter += 1
        features = [[msg.arbitration_id, msg.dlc]]
        
        # Modeli eğit
        if len(data_buffer) >= 50 and counter % 50 == 0:
            model.fit(list(data_buffer))

        # --- TESPİT MANTIĞI ---
        threat = None
        log_type = "NORMAL" # Varsayılan durum
        hour = datetime.now().hour

        # Saldırı Kontrolleri
        if msg.arbitration_id == 0x9FF:
            threat = "KRITIK: Firmware Enjeksiyonu"
        elif msg.arbitration_id < 0x100:
            threat = "UYARI: Yan Hareket / Ağ Keşfi"
        elif hour in [2, 3, 4]: 
            threat = "ANOMALI: Zaman Bazlı Yetkisiz Erişim"
        elif msg.dlc != 8:
            threat = "TEHDIT: TLS Downgrade / Fuzzing"

        # LOGLAMA KARARI
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if threat:
            # SALDIRI VARSA: Kesinlikle kaydet ve ekrana bas
            log_type = "SALDIRI"
            log_msg = f"[{ts}] [{log_type}] {threat} | Aksiyon: Bloklandı | ID: {hex(msg.arbitration_id)}\n"
            print(f"\033[91m{log_msg.strip()}\033[0m") # Kırmızı Yazı
            
            with open(LOG_FILE, "a") as f:
                f.write(log_msg)
        
        else:
            # NORMAL VERİ: Veri seti dengesi için kaydet
            # Disk şişmesin diye her normal paketi değil, %50'sini kaydedelim (Opsiyonel)
            # Ama tam eğitim için hepsini açıyoruz:
            log_msg = f"[{ts}] [NORMAL] Trafik Akışı Temiz | Durum: OK | ID: {hex(msg.arbitration_id)}\n"
            # Ekrana basma (Terminal kirlenmesin), sadece dosyaya yaz
            
            with open(LOG_FILE, "a") as f:
                f.write(log_msg)

        data_buffer.append(features[0])

except KeyboardInterrupt:
    print("\nVeri Toplama Durduruldu.")
finally:
    bus.shutdown()
