import asyncio
import logging
from websockets import connect
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call

logging.basicConfig(level=logging.INFO)

class SarjIstasyonu(cp):
    async def boot_ol(self):
        # Merkeze bağlanma isteği
        request = call.BootNotification(
            charge_point_model="Model-X",
            charge_point_vendor="Tesla-Similator"
        )
        response = await self.call(request)
        if response.status == 'Accepted':
            print("[İSTASYON] ✅ Merkez bağlantıyı kabul etti. Sistem hazır.")

    async def veri_gonder(self, guc_degeri):
        # Güç verisi gönderme
        request = call.MeterValues(
            connector_id=1,
            meter_value=[{
                "timestamp": "2023-12-14T10:00:00Z",
                "sampled_value": [{"value": str(guc_degeri), "unit": "kW"}]
            }]
        )
        await self.call(request)
        print(f"[İSTASYON] 📤 Gönderilen Tüketim: {guc_degeri} kW")

async def main():
    # Merkeze bağlanırken protokolü belirtiyoruz
    async with connect(
        'ws://localhost:9000/CP_1',
        subprotocols=['ocpp1.6']
    ) as ws:
        istasyon = SarjIstasyonu('CP_1', ws)
        await asyncio.gather(istasyon.start(), istasyon_senaryosu(istasyon))

async def istasyon_senaryosu(istasyon):
    # 1. Bağlan
    await istasyon.boot_ol()
    await asyncio.sleep(2)

    # 2. NORMAL veri gönder (3.6 kW)
    print("[İSTASYON] Normal şarj işlemi simüle ediliyor...")
    await istasyon.veri_gonder(3.6)
    
    # Program hemen kapanmasın diye bekle
    await asyncio.sleep(5)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("İstasyon kapatıldı.")