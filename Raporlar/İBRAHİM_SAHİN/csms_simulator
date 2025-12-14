# -*- coding: utf-8 -*-
import asyncio
import logging
import websockets
from datetime import datetime, timezone
import traceback

from ocpp.routing import on
from ocpp.v201 import ChargePoint as CP
from ocpp.v201 import call_result, call
from ocpp.v201.enums import RegistrationStatusEnumType

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


# ==============================
# Central System (CSMS) Sınıfı
# ==============================
class CentralSystem(CP):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.boot_completed = False
        self.transaction_id_counter = 100 # İşlem ID sayacı

    # ⭐ YENİ METOT: SÜREKLİ İŞLEM DÖNGÜSÜ
    async def transaction_cycle_loop(self):
        """Sürekli olarak RemoteStartTransaction ve RemoteStopTransaction komutlarını gönderen döngü."""
        while True:
            # İşlem ID'sini artır
            self.transaction_id_counter += 1
            current_tx_id = str(self.transaction_id_counter)

            logging.info("=" * 60)
            logging.info(f"[CSMS DÖNGÜ] 🎯 İşlem Başlatılıyor (ID: {current_tx_id})...")

            try:
                # 1. Başlatma İsteği Gönder (RemoteStartTransaction)
                start_request = call.RequestStartTransaction(
                    remote_start_id=self.transaction_id_counter,
                    id_token={"id_token": "ABC123", "type": "ISO14443"},
                    evse_id=1
                )

                # Timeout kaldırıldı, asyncio.wait_for ile süre yönetimi
                start_response = await asyncio.wait_for(self.call(start_request), timeout=35.0)

                logging.info(f"[CSMS DÖNGÜ] CP Yanıtı (Start): {start_response.status}")

                if start_response.status == 'Accepted':
                    # 2. Şarj Etme Süresi Simülasyonu (Veri Akışı)
                    logging.info("[CSMS DÖNGÜ] Şarj başladı, 5 saniye veri akışı bekleniyor...")
                    await asyncio.sleep(5)

                    # 3. Durdurma İsteği Gönder (RequestStopTransaction)
                    logging.info(f"[CSMS DÖNGÜ] İşlem Durduruluyor (ID: {current_tx_id})...")
                    stop_request = call.RequestStopTransaction(
                        transaction_id=current_tx_id
                    )
                    # Timeout kaldırıldı, asyncio.wait_for ile süre yönetimi
                    stop_response = await asyncio.wait_for(self.call(stop_request), timeout=10.0)
                    logging.info(f"[CSMS DÖNGÜ] CP Yanıtı (Stop): {stop_response.status}")

                else:
                    logging.warning("[CSMS DÖNGÜ] Başlatma Reddedildi. 3 saniye bekleniyor.")
                    await asyncio.sleep(3)


            except asyncio.TimeoutError:
                logging.error("[CSMS DÖNGÜ] ❌ İşlem Timeout! Sonraki işleme geçiliyor.")
                await asyncio.sleep(2)
            except Exception as e:
                # Traceback burada işlenir
                logging.error(f"[CSMS DÖNGÜ] Genel Hata: {e}. 5 saniye bekleniyor.")
                logging.error(traceback.format_exc())
                await asyncio.sleep(5)

            logging.info("==========================================")
            await asyncio.sleep(2) # İşlemler arası kısa bekleme


    # ⭐ YENİ METOT: BootNotification'dan hemen sonra döngüyü başlatan sarmalayıcı
    async def send_remote_start_delayed(self):
        """Boot cevabı gönderildikten sonra sürekli işlem döngüsünü başlatır."""
        try:
            await asyncio.sleep(1.0) # CP'ye tam oturması için 1 saniye bekleme
            asyncio.create_task(self.transaction_cycle_loop())
        except Exception as e:
            logging.error(f"[CSMS] send_remote_start_delayed hatası: {e}")
            logging.error(traceback.format_exc())

    @on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        """BootNotification handler - sürekli döngüyü başlatır."""
        try:
            logging.info("=" * 60)
            logging.info(f"[CSMS] 🎯 BootNotification ALINDI!")

            model = charging_station.get("model", "Unknown")
            vendor = charging_station.get("vendor_name", "Unknown")

            logging.info(f"[CSMS] Yeni CP bağlandı -> Model: {model}, Vendor: {vendor}")

            # Yanıt oluştur (Zaman düzeltmesi içerir)
            response = call_result.BootNotification(
                current_time=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
                interval=10,
                status=RegistrationStatusEnumType.accepted,
            )

            self.boot_completed = True

            # KRİTİK DEĞİŞİKLİK: Sürekli döngüyü arka planda başlat
            asyncio.create_task(self.send_remote_start_delayed())

            return response

        except Exception as e:
            logging.error(f"[CSMS] BootNotification hatası: {e}")
            logging.error(traceback.format_exc())
            raise

    @on('MeterValues')
    async def on_meter_values(self, evse_id, meter_value, **kwargs):
        """MeterValues handler"""
        try:
            logging.info("=" * 60)
            logging.info("[CSMS] 📊 MeterValues ALINDI!")

            # Meter değerlerini detaylı loglama
            for meter in meter_value:
                timestamp = meter.get("timestamp")
                for sample in meter.get("sampled_value", []):
                    value = sample.get("value")
                    logging.info(f"  📊 Meter okuma: {value} Wh @ {timestamp}")

            logging.info("=" * 60)

            return call_result.MeterValues()

        except Exception as e:
            logging.error(f"[CSMS] MeterValues hatası: {e}")
            logging.error(traceback.format_exc())
            raise

    @on('StatusNotification')
    async def on_status_notification(self, timestamp, connector_status, evse_id, connector_id, **kwargs):
        """StatusNotification handler"""
        try:
            logging.info(f"[CSMS] StatusNotification -> EVSE {evse_id}, Connector {connector_id}, Status: {connector_status}")
            return call_result.StatusNotification()
        except Exception as e:
            logging.error(f"[CSMS] StatusNotification hatası: {e}")
            logging.error(traceback.format_exc())
            raise


# ==============================
# WebSocket Sunucusu
# ==============================
async def on_connect(websocket):
    """WebSocket handler"""
    try:
        # Path'i websocket objesinden al
        path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
        charge_point_id = path.strip('/')

        logging.info(f"[CSMS] 🔌 Yeni bağlantı: {charge_point_id}")

        cs = CentralSystem(charge_point_id, websocket)
        await cs.start()

    except websockets.exceptions.ConnectionClosed:
        logging.info(f"[CSMS] Bağlantı kesildi")
    except Exception as e:
        logging.error(f"[CSMS] on_connect hatası: {e}")
        logging.error(traceback.format_exc())


async def main():
    async def handler(websocket):
        await on_connect(websocket)

    server = await websockets.serve(
        handler,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp2.0.1"],
        ping_interval=20,
        ping_timeout=20
    )

    print("=" * 60)
    print("🚀 CSMS SIMULATOR BAŞLATILDI")
    print("=" * 60)
    logging.info("[CSMS] 🚀 Sunucu başlatıldı -> ws://0.0.0.0:9000 (OCPP 2.0.1)")
    logging.info("[CSMS] Bağlantı bekleniyor...")
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n")
        logging.info("[CSMS] Sunucu kapatıldı.")


