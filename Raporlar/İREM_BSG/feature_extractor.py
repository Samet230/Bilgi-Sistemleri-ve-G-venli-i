import pandas as pd
import numpy as np
import os

# CAN import hatasını çözmek için 'CAN' dışarıda tutulur ve contrib'dan alınır
# Eğer bu satır hata verirse (bazı scapy versiyonlarında), altındaki yoruma alınmış satır denenir.
try:
    from scapy.all import rdpcap, IP, TCP, UDP
    from scapy.contrib.cansocket import CAN
except ImportError:
    # Alternatif içe aktarma yöntemi (Bazı eski scapy versiyonları için)
    from scapy.all import rdpcap, IP, TCP, UDP
    CAN = None # CAN'i bulamazsa geçersiz kıl

# ===============================================================
# 1. Öznitelik Çıkarma Fonksiyonu
# ===============================================================

def extract_features(pcap_file, label):
    """Pcap dosyasını okur ve makine öğrenimi için öznitelikleri çıkarır."""

    # Dosya yoksa kontrol et
    if not os.path.exists(pcap_file):
        print(f"Hata: '{pcap_file}' dosyası bulunamadı.")
        return None

    # Dosya okuma ve hata yönetimi
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        print(f"Hata: {pcap_file} okunamadı: {e}")
        return None

    data = []
    start_time = packets[0].time if packets else 0

    for packet in packets:
        features = {
            'timestamp': float(packet.time - start_time),
            'length': len(packet),
            'protocol_ip': 0,
            'protocol_tcp': 0,
            'protocol_udp': 0,
            'protocol_can': 0,
            'protocol_other': 0,
            'can_id_anomaly': 0, 
            'label': label
        }

        # Protokol Kontrolleri
        if IP in packet:
            features['protocol_ip'] = 1
            if TCP in packet:
                features['protocol_tcp'] = 1
            elif UDP in packet:
                features['protocol_udp'] = 1

        # CAN Protokolü Kontrolü (Sadece CAN başarıyla içe aktarılabildiyse çalışır)
        if CAN is not None:
            if CAN in packet:
                features['protocol_can'] = 1

                # CAN ID Anomalisini Belirleme (Saldırı ID'si 0x7FF)
                try:
                    # Eğer CAN paketinin ID'si 0x7FF ise, anomali etiketlenir.
                    if packet[CAN].id == 0x7FF: 
                        features['can_id_anomaly'] = 1
                except:
                    pass 

        # Diğer Protokoller
        if not features['protocol_ip'] and not features['protocol_can']:
             features['protocol_other'] = 1

        data.append(features)

    return pd.DataFrame(data)

# ===============================================================
# 2. Veri Çıkarımını Çalıştırma ve Birleştirme
# ===============================================================

# Dosya Adları ve Etiketler
file_list = [
    ('normal_traffic.pcap', 'normal'),
    ('attack_traffic_pivot.pcap', 'pivot'),
    ('attack_traffic_can.pcap', 'can_spoof')
]

all_data = []

for file_name, label in file_list:
    print(f"[{label.upper()}]: '{file_name}' dosyasından öznitelikler çıkarılıyor...")
    df = extract_features(file_name, label)
    if df is not None and not df.empty:
        all_data.append(df)
        print(f"  -> {len(df)} paket başarıyla eklendi.")
    else:
        print(f"  -> {file_name} dosyası boş veya bulunamadı.")

# Tüm DataFrame'leri birleştir
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    # Sonuçları Kaydetme
    output_file = 'network_traffic_features.csv'
    final_df.to_csv(output_file, index=False)
    print("---------------------------------------------")
    print(f"✅ TÜM VERİ ÇIKARIMI TAMAMLANDI.")
    print(f"Toplam {len(final_df)} paket, '{output_file}' dosyasına kaydedildi.")
    print("---------------------------------------------")
else:
    print("Hata: Hiçbir veri dosyası yüklenemedi. Çıkarım başarısız.")
