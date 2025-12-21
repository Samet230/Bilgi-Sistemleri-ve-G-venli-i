import asyncio
import websockets
import can
import random
import json

# --- AYARLAR ---
SERVER_URI = "ws://localhost:9000"
CAN_INTERFACE = 'vcan0'
STATION_ID = "TR-EV-4523" 

# CAN Bus Başlatma (Hata verirse programı durdurma, uyar)
try:
    bus = can.Bus(channel=CAN_INTERFACE, interface='socketcan')
except OSError:
    print(f"HATA: '{CAN_INTERFACE}' bulunamadı. Lütfen 'sudo ip link add...' komutlarını uygulayın.")
    exit(1)

async def simulate_station():
    while True: # Sonsuz döngü: Bağlantı kopsa da tekrar dene
        try:
            print(f"[İSTASYON] Sunucuya bağlanılıyor ({SERVER_URI})...")
            # ping_interval=None ve ping_timeout=None: Bağlantıyı asla zaman aşımına uğratma
            async with websockets.connect(SERVER_URI, ping_interval=None, ping_timeout=None) as websocket:
                print(f"[İSTASYON] Bağlantı Başarılı!")
                
                await websocket.send(f"BootNotification: {STATION_ID} Aktif")
                
                while True:
                    # --- NORMAL DAVRANIŞ ---
                    current = round(random.uniform(15.0, 16.5), 2)
                    
                    # WebSocket Hatası Olursa Yakala
                    try:
                        msg = json.dumps({"Action": "MeterValues", "Station": STATION_ID, "Current": current})
                        await websocket.send(msg)
                    except websockets.exceptions.ConnectionClosed:
                        print("[HATA] Mesaj gönderilirken sunucu bağlantısı koptu!")
                        break # İç döngüden çık, tekrar bağlanmayı dene

                    # CAN Mesajı Gönder
                    can_msg = can.Message(arbitration_id=0x300, data=[int(current), 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
                    bus.send(can_msg)
                    print(f"[NORMAL] Akım: {current}A | CAN Frame gönderildi.")

                    # --- SALDIRI SENARYOSU ---
                    if random.random() < 0.2:
                        print("\n>>> [SALDIRI] ANOMALİ BAŞLATILIYOR! (TR-EV-4523) <<<")
                        
                        try:
                            # A) Sunucuya saldırı
                            for _ in range(5):
                                await websocket.send("StartTransaction: TR-EV-4523 (Yetkisiz Deneme)")
                        except websockets.exceptions.ConnectionClosed:
                             print("[SALDIRI] Saldırı sırasında sunucu düştü! Devam ediliyor...")
                             break

                        # B) CAN Hattına Saldırı
                        for _ in range(10):
                            attack_frame = can.Message(arbitration_id=0x9FF, data=[0xFF, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
                            bus.send(attack_frame)
                            await asyncio.sleep(0.05) 
                            
                        print(">>> [SALDIRI] Zararlı CAN paketleri enjekte edildi.\n")

                    await asyncio.sleep(2)
        
        except (OSError, websockets.exceptions.InvalidURI, websockets.exceptions.ConnectionClosedError):
            print("[SİSTEM] Sunucuya ulaşılamıyor. 3 saniye içinde tekrar denenecek...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(simulate_station())
    except KeyboardInterrupt:
        print("Simülasyon durduruldu.")
        bus.shutdown()
