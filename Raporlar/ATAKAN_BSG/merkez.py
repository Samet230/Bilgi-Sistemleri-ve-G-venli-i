import asyncio
import logging
from datetime import datetime
from websockets import serve
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.routing import on

# Logları görelim
logging.basicConfig(level=logging.INFO)

class MerkeziSistem(cp):
    # İstasyon bağlandığında çalışır
    @on('BootNotification')
    async def on_boot_notification(self, **kwargs):
        # kwargs: Gelen tüm parametreleri kabul et (Hata çıkmasını engeller)
        print(f"\n[MERKEZ] İstasyon Bağlantı İsteği Gönderdi.")
        
        # Kesinlikle çalışan cevap formatı
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )

    # Veri geldiğinde çalışır
    @on('MeterValues')
    async def on_meter_values(self, meter_value, **kwargs):
        print(f"[MERKEZ] Veri Paketi Alındı.")
        
        # Gelen veriyi güvenli şekilde okuyalım
        for value in meter_value:
            try:
                # Veri formatı bazen obje bazen sözlük olabilir, ikisini de deneyelim
                if hasattr(value, 'sampled_value'):
                    sample = value.sampled_value[0]
                else:
                    sample = value['sampled_value'][0]

                if hasattr(sample, 'value'):
                    okunan_deger = sample.value
                else:
                    okunan_deger = sample['value']
                
                print(f"[MERKEZ] Okunan Güç: {okunan_deger} kW")

                # ANOMALİ KONTROLÜ (Senin projenin kalbi burası)
                if float(okunan_deger) > 10.0:
                    print("\n🚨 🚨 🚨 ALARM! AŞIRI YÜK TESPİT EDİLDİ! 🚨 🚨 🚨")
                    print("!!! Sisteme Müdahale Ediliyor... !!!\n")

            except Exception as e:
                print(f"[HATA] Veri okunamadı: {e}")

        return call_result.MeterValues()

# İstasyon bağlandığında bu fonksiyon çalışır
async def on_connect(websocket):
    try:
        requested_protocols = websocket.request_headers.get("Sec-WebSocket-Protocol")
        print(f"[MERKEZ] Yeni Bağlantı Geldi. Protokol: {requested_protocols}")
    except:
        pass

    # İstasyonun ID'sini 'CP_1' olarak varsayalım
    charge_point_id = "CP_1"
    cp_instance = MerkeziSistem(charge_point_id, websocket)

    try:
        # İletişimi başlat
        await cp_instance.start()
    except Exception as e:
        print(f"[MERKEZ] Bağlantı koptu veya hata oluştu: {e}")

async def main():
    # Sunucuyu başlatırken 'ocpp1.6' protokolünü kabul ettiğimizi belirtiyoruz!
    # BU KISIM ÇOK ÖNEMLİ, HATAYI ÇÖZEN KISIM BURASI:
    server = await serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6'] 
    )
    
    print("------------------------------------------------")
    print(" MERKEZİ YÖNETİM SİSTEMİ (CSMS) BAŞLATILDI")
    print(" İstasyon bekleniyor...")
    print("------------------------------------------------")
    await server.wait_closed()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Sistem kapatıldı.")