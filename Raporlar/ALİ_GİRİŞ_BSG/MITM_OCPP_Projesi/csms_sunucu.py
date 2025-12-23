import asyncio
import websockets
import json

# Sunucunun dinleyeceği port (Şifresiz iletişim için 8080 kullanıldı)
PORT = 8080

async def csms_handler(websocket, path):
    """Her yeni EVSE bağlantısını yönetir."""
    print(f"[BAGLANDI] Yeni EVSE baglandi: {path}")

    try:
        async for message in websocket:
            # Gelen mesajı JSON formatında ayrıştır (OCPP mesajı beklenir)
            try:
                request = json.loads(message)
                
                print(f"[{path}] GELEN MESAJ:")
                print(request) # Mesaj içeriğini ekrana yazar

                # Yanıt olarak basit bir onay mesajı gönder
                response_message = json.dumps([3, request[1], {}])
                await websocket.send(response_message)
            
            except json.JSONDecodeError:
                print(f"[{path}] Gecersiz JSON: {message}")

    except websockets.exceptions.ConnectionClosed:
        print(f"[{path}] Baglanti kesildi.")
    finally:
        print(f"[{path}] Baglanti sonlandi.")

async def start_csms():
    """Ana sunucuyu başlatır ve sürekli dinlemede kalır."""
    print(f"--- Merkezi Sistem Sunucusu (CSMS) baslatiliyor... ---")
    async with websockets.serve(csms_handler, "0.0.0.0", PORT):
        print(f"CSMS, ws://0.0.0.0:{PORT} adresinde dinlemede.")
        await asyncio.Future() # Sunucunun durmamasını sağlar

if __name__ == "__main__":
    asyncio.run(start_csms())