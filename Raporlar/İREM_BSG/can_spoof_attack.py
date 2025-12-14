import can
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Saldırının Hedefi: vcan0
CAN_BUS = 'vcan0'

# Anormal/Sahte CAN ID'si (Modelin anomali olarak etiketleyeceği ID)
SPOOFED_CAN_ID = 0x7FF 

def send_spoofed_can():
    try:
        bus = can.interface.Bus(CAN_BUS, bustype='socketcan')
        logging.info("==============================================")
        logging.info("🚨 ANOMALİ B BAŞLADI: CAN ID Sahteciliği Saldırısı 🚨")
        logging.info(f"Sahte ID: {hex(SPOOFED_CAN_ID)} gönderiliyor.")

        # Sahte CAN mesajını oluştur (4 byte rastgele veri ile)
        message = can.Message(
            arbitration_id=SPOOFED_CAN_ID, 
            data=[0xAA, 0xBB, 0xCC, 0xDD], 
            is_extended_id=False
        )

        # Mesajı 5 kez gönderme
        for i in range(5):
            bus.send(message)
            logging.warning(f"  [{i+1}/5] Gönderildi: vcan0 {hex(SPOOFED_CAN_ID)} [4] AABBCCDD")
            time.sleep(0.1)

        logging.info("==============================================")
        logging.info("✅ ANOMALİ B TAMAMLANDI. Sahte CAN trafiği oluştu.")

    except Exception as e:
        logging.error(f"CAN HATA: {e}")

if __name__ == '__main__':
    send_spoofed_can()
