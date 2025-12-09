import socket
import random
import time
import logging

# Anomali Raporunuzdaki Keşif Parametrelerini Simüle Eder
# Varsayılan olarak 192.168.1.x ağını tarıyoruz
TARGET_BASE = "192.168.1."
SCAN_PORT = 80  # Hedefteki popüler bir portu (Web Sunucusu) simüle et
SCAN_COUNT = 8  # Kurumsal ağdaki 8 farklı IP'ye tarama girişimini simüle eder [cite: 18]

# Anormal ağ davranışı için logging ayarı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_pivot_scan():
    logging.info("==========================================================")
    logging.info("🚨 ANOMALİ BAŞLADI: Şarj İstasyonu Kökenli Pivot Keşfi 🚨")
    logging.info("==========================================================")
    logging.info("Amaç: İstasyonu, yerel ağdaki cihazları tarayan bir Pivot noktasına çevirmek.")
    
    # Yerel ağdaki rastgele hedeflere tarama başlatmayı simüle et
    for i in range(SCAN_COUNT):
        # Rastgele bir IP adresi oluştur (2 ile 254 arası)
        target_ip = TARGET_BASE + str(random.randint(2, 254))
        
        # Soket oluştur (T1046: Network Service Scanning tekniği ile eşleşir [cite: 31])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5) # Hızlı taramayı simüle etmek için kısa timeout
        
        start_time = time.time()
        
        # Hedefe bağlantı kurmayı dene (Anormal Giden Bağlantı Sayısı [cite: 18])
        result = sock.connect_ex((target_ip, SCAN_PORT))
        
        if result == 0:
            logging.warning(f"  [{i+1}/{SCAN_COUNT}] Keşif Başarılı: Açık Port Tespiti -> {target_ip}:{SCAN_PORT}")
        else:
            logging.info(f"  [{i+1}/{SCAN_COUNT}] Tarama Girişimi: Hedef {target_ip}:{SCAN_PORT} -> Kapalı (Geçen Süre: {time.time() - start_time:.3f}s)")
        
        sock.close()
        time.sleep(0.3) # Ağdaki bağlantı yükünü sürekli kılmayı simüle et (CPU/Bellek Yükü Anomali Tespiti [cite: 20])
        
    logging.info("==========================================================")
    logging.info("✅ ANOMALİ TAMAMLANDI. Anormal Pivot Ağ Aktivitesi Sona Erdi.")
    logging.info("==========================================================")

if __name__ == '__main__':
    run_pivot_scan()
