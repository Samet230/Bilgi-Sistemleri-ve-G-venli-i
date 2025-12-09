import asyncio
import websockets
import json
import can
from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result
from ocpp.v201.enums import RegistrationStatusType

# CAN Konfigürasyonu
CAN_BUS = 'vcan0'
# CAN Arayüzüne bağlan
can_bus = can.interface.Bus(CAN_BUS, bustype='socketcan')

# OCPP -> CAN Mapping (Saldırı analizi için kritik ID'ler)
# RemoteStopTransaction'ı temsil eden CAN ID: 0x201
CAN_MAP = {
    'RemoteStartTransaction': 0x200,
    'RemoteStopTransaction': 0x201, 
    'SetChargingProfile': 0x210
}

class ChargePoint(cp):
    @on('BootNotification')
    def on_boot_notification(self, reason, **kwargs):
        # CP Agent başarılı bir şekilde bağlandığında CSMS'e yanıt gönderir
        print(f"[{self.id}] BootNotification alındı. Durum: {reason}")
        return call_result.BootNotification(
            current_time='2025-11-09T01:30:00Z',
            interval=300,
            status=RegistrationStatusType.accepted
        )

    @on('RemoteStopTransaction')
    async def on_remote_stop_transaction(self, transaction_id, **kwargs):
        # *KRİTİK: OCPP komutunu al ve CAN'e çevir*
        can_id = CAN_MAP['RemoteStopTransaction']
        # Transaction ID'nin son 1 byte'ını CAN verisi olarak kullan (Basit örnek)
        data = [transaction_id & 0xFF] 
        # CAN mesajını oluştur
        message = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
        
        try:
            # CAN ağına (vcan0) gönder
            can_bus.send(message)
            print(f"[{self.id}] CAN GÖNDERİLDİ: RemoteStop (ID: {hex(can_id)}, Data: {data})")
        except Exception as e:
            print(f"[{self.id}] CAN HATA: {e}")

        # CSMS'e başarılı yanıtı gönder
        return call_result.RemoteStopTransaction(
            status='Accepted'
        )

async def start_cp(cp_id):
    # CSMS'in WebSocket adresi
    uri = f'ws://localhost:9000/{cp_id}' 
    
    while True:
        try:
            # CSMS'e (Sunucuya) bağlan
            async with websockets.connect(uri, subprotocols=['ocpp2.0.1']) as ws:
                cp = ChargePoint(cp_id, ws)
                await cp.start()
        except websockets.exceptions.ConnectionClosedOK:
            print(f"[{cp_id}] Bağlantı kapatıldı. Tekrar bağlanılıyor...")
            await asyncio.sleep(5)
        except ConnectionRefusedError:
            print(f"[{cp_id}] CSMS kapalı. Tekrar deneniyor...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[{cp_id}] Beklenmedik Hata: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(start_cp('CP001'))
