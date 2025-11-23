import asyncio
from datetime import datetime, timezone
import random

import websockets

from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.datatypes import MeterValue, SampledValue
from ocpp.v16.enums import (
    RegistrationStatus,
    ChargePointStatus,
    ChargePointErrorCode,
    Measurand,
    UnitOfMeasure,
)

# SteVe adresi ve CP ID
STEV_URL = "ws://localhost:8180/steve/websocket/CentralSystemService/CP-TEST-01"
CP_ID = "CP-TEST-01"


class ChargePoint(Cp):
    async def send_boot_notification(self):
        print(f"SteVe'ye bağlanılıyor: {STEV_URL}")
        print("BootNotification gönderiliyor...")

        req = call.BootNotification(
            charge_point_model="PythonSim-1",
            charge_point_vendor="LeventCorp",
        )

        # ocpp kütüphanesi JSON'u kendi üretip gönderiyor
        res = await self.call(req)

        print(f"BootNotification cevabı: {res}")
        # Örn: BootNotification(current_time='...', interval=14400, status=<RegistrationStatus.accepted: 'Accepted'>)
        return res

    async def heartbeat_loop(self, interval: int):
        print(f"Heartbeat döngüsü başlatılıyor... (interval = {interval} sn)")
        while True:
            req = call.Heartbeat()
            res = await self.call(req)
            try:
                current_time = getattr(res, "current_time", None)
                print(f"Heartbeat cevabı (currentTime): {current_time}")
            except Exception:
                print(f"Heartbeat cevabı: {res}")
            await asyncio.sleep(interval)

    async def send_status_notification(self, connector_id: int, status: ChargePointStatus):
        req = call.StatusNotification(
            connector_id=connector_id,
            error_code=ChargePointErrorCode.no_error,
            status=status,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        print(f"StatusNotification gönderiliyor: connector={connector_id}, status={status}")
        await self.call(req)

    async def send_meter_values(self, connector_id: int, transaction_id: int, energy_wh: int):
        meter_value = MeterValue(
            timestamp=datetime.now(timezone.utc).isoformat(),
            sampled_value=[
                SampledValue(
                    value=str(energy_wh),
                    measurand=Measurand.energy_active_import_register,
                    unit=UnitOfMeasure.wh,
                )
            ],
        )

        req = call.MeterValues(
            connector_id=connector_id,
            transaction_id=transaction_id,
            meter_value=[meter_value],
        )

        print(f"MeterValues gönderiliyor: tx={transaction_id}, energy_wh={energy_wh}")
        await self.call(req)

    async def run_transaction_scenario(self):
        """
        ⚡ Authorize → StartTransaction → MeterValues → StopTransaction
        basit bir 'gerçek şarj' senaryosu.
        """
        connector_id = 1
        id_tag = "TESTTAG1234"

        print("\n=== StatusNotification(Available) ===")
        await self.send_status_notification(
            connector_id=connector_id,
            status=ChargePointStatus.available,
        )

        print("\n=== Authorize ===")
        auth_req = call.Authorize(id_tag=id_tag)
        auth_res = await self.call(auth_req)
        print(f"Authorize cevabı: {auth_res}")

        print("\n=== StatusNotification(Preparing) ===")
        await self.send_status_notification(
            connector_id=connector_id,
            status=ChargePointStatus.preparing,
        )

        print("\n=== StartTransaction ===")
        start_req = call.StartTransaction(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        start_res = await self.call(start_req)
        print(f"StartTransaction cevabı: {start_res}")

        # response.transaction_id alanını yakalamaya çalış
        transaction_id = getattr(start_res, "transaction_id", None)
        if transaction_id is None:
            # SteVe bazen 1 vs. dönecektir, bulamazsak 1 diyip devam edelim
            transaction_id = 1

        print("\n=== StatusNotification(Charging) ===")
        await self.send_status_notification(
            connector_id=connector_id,
            status=ChargePointStatus.charging,
        )

        print("\n=== MeterValues (simüle enerji akışı) ===")
        energy = 0
        for _ in range(5):
            step = random.randint(100, 300)  # Wh artış
            energy += step
            await self.send_meter_values(
                connector_id=connector_id,
                transaction_id=transaction_id,
                energy_wh=energy,
            )
            await asyncio.sleep(2)

        print("\n=== StatusNotification(Finishing) ===")
        await self.send_status_notification(
            connector_id=connector_id,
            status=ChargePointStatus.finishing,
        )

        print("\n=== StopTransaction ===")
        stop_req = call.StopTransaction(
            transaction_id=transaction_id,
            meter_stop=energy,
            timestamp=datetime.now(timezone.utc).isoformat(),
            id_tag=id_tag,
        )
        stop_res = await self.call(stop_req)
        print(f"StopTransaction cevabı: {stop_res}")

        print("\n=== StatusNotification(Available) ===")
        await self.send_status_notification(
            connector_id=connector_id,
            status=ChargePointStatus.available,
        )

        print("\nŞarj senaryosu tamamlandı.\n")


async def main():
    async with websockets.connect(
        STEV_URL,
        subprotocols=["ocpp1.6"],
    ) as ws:
        cp = ChargePoint(CP_ID, ws)

        # 1) cp.start() → gelen mesajları dinler
        # 2) cp_flow()  → BootNotification + Heartbeat + Transaction senaryosu
        async def cp_flow():
            boot_res = await cp.send_boot_notification()

            # BootNotification.conf içindeki interval alanını al
            interval = getattr(boot_res, "interval", 60) or 60

            # Heartbeat loop'u arka planda çalışsın
            asyncio.create_task(cp.heartbeat_loop(interval))

            # Küçük bir bekleme
            await asyncio.sleep(2)

            # Şarj senaryosunu çalıştır
            await cp.run_transaction_scenario()

        await asyncio.gather(
            cp.start(),  # ocpp kütüphanesinin mesaj router'ı
            cp_flow(),
        )


if __name__ == "__main__":
    asyncio.run(main())
