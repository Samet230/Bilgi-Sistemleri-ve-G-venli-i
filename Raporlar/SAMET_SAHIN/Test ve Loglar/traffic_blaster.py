import can
import time
import random

# Ayarlar
INTERFACE = 'vcan0'
ATTACK_RATIO = 0.3 # %30 Saldırı, %70 Normal

bus = can.Bus(channel=INTERFACE, interface='socketcan')

print("--- TRAFİK JENERATÖRÜ: 1000 LOG HEDEFİ BAŞLATILDI ---")
print("İpucu: Loglar 1000 olana kadar kapatma.")

try:
    while True:
        if random.random() < ATTACK_RATIO:
            # Saldırı Tipleri (Dokümanlara Göre)
            choice = random.choice(['firmware', 'pivot', 'tls'])
            if choice == 'firmware':
                msg = can.Message(arbitration_id=0x9FF, data=[0xDE, 0xAD, 0xBE, 0xEF, 0, 0, 0, 0])
            elif choice == 'pivot':
                msg = can.Message(arbitration_id=random.randint(0x001, 0x0FF), data=[1,1,1,1,1,1,1,1])
            else: # TLS Downgrade / Bozuk Paket
                msg = can.Message(arbitration_id=0x300, dlc=4, data=[0xAA, 0xBB, 0xCC, 0xDD])
        else:
            # Normal Trafik
            msg = can.Message(arbitration_id=0x300, data=[random.randint(0,255) for _ in range(8)])
        
        bus.send(msg)
        time.sleep(0.05) # 50ms bekleme (Saniyede 20 mesaj - İdeal hız)
except KeyboardInterrupt:
    print("Durduruldu.")
