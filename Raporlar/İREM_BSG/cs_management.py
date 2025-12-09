import asyncio
import websockets
import logging
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result
from ocpp.v201 import call
from ocpp.v201.enums import Action

logging.basicConfig(level=logging.INFO)
charge_points = {}

async def on_connect(websocket, path):
    """ CP Agent bağlandığında çalışır. """
    charge_point_id = path.strip('/')
    
    # OCPP Alt Protokolünü kontrol et
    if 'ocpp2.0.1' not in websocket.request_headers.get('Sec-WebSocket-Protocol', ''):
        logging.error(f"CP {charge_point_id} hatalı protokol ile bağlandı.")
        return

    cp_instance = cp(charge_point_id, websocket)
    charge_points[charge_point_id] = cp_instance
    logging.info(f"CP {charge_point_id} bağlandı.")
    
    try:
        await cp_instance.start()
    except Exception as e:
        logging.error(f"CP {charge_point_id} ile iletişim hatası: {e}")
    finally:
        del charge_points[charge_point_id]
        logging.info(f"CP {charge_point_id} bağlantısı kesildi.")

async def send_remote_stop(cp_id, transaction_id):
    """ Belirli bir CP'ye RemoteStop komutu gönderir. """
    if cp_id not in charge_points:
        logging.warning(f"CP {cp_id} bulunamadı.")
        return

    cp_instance = charge_points[cp_id]
    
    request = call.RemoteStopTransaction(
        transaction_id=transaction_id
    )
    
    logging.info(f"CSMS GÖNDERİYOR: RemoteStopTransaction (CP: {cp_id})")
    try:
        response = await cp_instance.call(request)
        logging.info(f"CP'den yanıt: {response.status}")
    except Exception as e:
        logging.error(f"RemoteStop gönderme hatası: {e}")

async def main():
    # CSMS Sunucusunu başlat (Port: 9000)
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0.1']
    )
    logging.info("CSMS Sunucusu başlatıldı. Port: 9000")
    
    # Bir saniye bekleyip RemoteStop komutunu gönder (CP001'e)
    await asyncio.sleep(2)
    await send_remote_stop('CP001', 12345)
    
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
