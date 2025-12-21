import asyncio
import websockets
import datetime

async def handle_connection(websocket):
    # 'path' parametresi yeni sürümlerde websocket nesnesinin içindedir, 
    # ayrı argüman olarak gelmez.
    print(f"[SUNUCU] Yeni bir Şarj İstasyonu bağlandı!")
    try:
        async for message in websocket:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] İstasyondan Mesaj: {message}")
            
            # Senaryo: Eğer istasyon 'Authorize' onayı isterse cevap ver
            if "Authorize" in message:
                await websocket.send("CSMS: Yetkilendirme Başarılı. Şarj Başlayabilir.")
            elif "MeterValues" in message:
                # Enerji tüketim verisi geldiğinde onayla
                await websocket.send("CSMS: Veri Alındı.")
                
    except websockets.exceptions.ConnectionClosed:
        print("[SUNUCU] İstasyon bağlantısı koptu.")

async def main():
    # Modern başlatma yöntemi: Context Manager kullanımı
    print("=== CSMS YÖNETİM SUNUCUSU BAŞLATILDI (Port: 9000) ===")
    print("İstasyonların bağlanması bekleniyor...")
    
    async with websockets.serve(handle_connection, "localhost", 9000):
        # Sunucuyu sonsuza kadar açık tut
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSunucu kapatıldı.")
