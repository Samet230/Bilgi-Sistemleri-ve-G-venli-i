# Elektrikli Araç Şarj İstasyonu (OCPP) Yük Verisi Manipülasyonu Simülasyonu

[cite_start]Bu proje, Elektrikli Araç (EV) şarj istasyonlarında görülebilecek siber güvenlik zafiyetlerini, özellikle **Yük Verisi Manipülasyonu Anomalisi**'ni [cite: 1, 15] simüle etmek amacıyla geliştirilmiştir.

Python ve `ocpp` kütüphanesi kullanılarak bir **Merkezi Yönetim Sistemi (CSMS)** ve bir **Şarj İstasyonu (CP)** sanal ortamda oluşturulmuş; araya giren bir **Saldırgan (Attacker)** senaryosu ile sisteme sahte enerji tüketim verileri enjekte edilmiştir.

## 📂 Proje İçeriği

* **`merkez.py`**: OCPP 1.6 protokolü ile çalışan, istasyonları dinleyen ve anomali (aşırı yük) durumunda alarm veren sunucu kodu.
* **`istasyon.py`**: Merkeze bağlanan ve normal şarj verisi (3.6 kW) gönderen temiz istasyon simülatörü.
* [cite_start]**`saldirgan.py`**: Sisteme yetkisiz erişim sağlayan ve manipüle edilmiş yüksek yük verisi (11.2 kW) gönderen saldırı aracı[cite: 23, 24].

## 🚀 Kurulum ve Çalıştırma

Bu projeyi kendi bilgisayarınızda test etmek için aşağıdaki adımları izleyin:

1.  **Gereksinimleri Yükleyin:**
    ```bash
    pip install ocpp websockets asyncio
    ```

2.  **Sistemi Başlatın (Sırasıyla):**
    * Terminal 1: `python3 merkez.py` (Sunucuyu ayağa kaldırır)
    * Terminal 2: `python3 istasyon.py` (Normal veri akışını gösterir)
    * Terminal 3: `python3 saldirgan.py` (Saldırıyı gerçekleştirir)

## 📊 SWOT Analizi

Bu projenin ve ele alınan anomalinin (Yük Manipülasyonu) güçlü, zayıf yönleri ile fırsat ve tehditleri aşağıda analiz edilmiştir:

### 💪 Güçlü Yönler (Strengths)
* [cite_start]**Gerçek Zamanlı İzleme:** Geliştirilen `merkez.py` modülü, `MeterValues` mesajlarını anlık olarak izleyerek belirlenen eşik değerin (10 kW) üzerindeki verilerde anında alarm üretmektedir[cite: 38].
* [cite_start]**Standart Protokol Kullanımı:** Proje, endüstri standardı olan **OCPP 1.6** protokolü üzerine kurgulanmıştır, bu da gerçek dünya senaryolarına uygunluk sağlar[cite: 155].
* [cite_start]**Uygulanabilirlik:** Python tabanlı yapısı sayesinde, karmaşık donanımlara ihtiyaç duymadan "Yük Verisi Manipülasyonu" anomalisi başarılı bir şekilde simüle edilmiştir[cite: 15, 87].

### 📉 Zayıf Yönler (Weaknesses)
* [cite_start]**Fiziksel Test Eksikliği:** Çalışma tamamen yazılımsal simülasyon ortamında gerçekleştirilmiştir; fiziksel bir şarj ünitesi veya araç üzerinde test yapılmamıştır[cite: 56, 58].
* **Temel Şifreleme:** Simülasyon ortamı olduğu için `ws://` (WebSocket) kullanılmıştır. [cite_start]Gerçek dünyada `wss://` (TLS/SSL) kullanılmadığında MITM saldırılarına karşı savunmasızdır[cite: 109, 472].
* [cite_start]**Manuel Firmware Yönetimi:** İstasyon tarafındaki zafiyetlerin (eski firmware vb.) simülasyonu kod içerisine manuel olarak yerleştirilmiştir[cite: 20, 39].

### 🌟 Fırsatlar (Opportunities)
* [cite_start]**Yapay Zeka Entegrasyonu:** `merkez.py` içerisindeki kural tabanlı (if > 10) tespit mekanizması, gelecekte Makine Öğrenmesi (AI) ile güçlendirilerek daha karmaşık anomalileri tespit edebilir[cite: 12, 40].
* [cite_start]**Blokzincir ile Güvenlik:** Veri bütünlüğünü sağlamak ve "inkar edilememezlik" (non-repudiation) ilkesini güçlendirmek için log kayıtlarının Blokzincir üzerinde tutulması sağlanabilir[cite: 1082, 1083].
* [cite_start]**Ulusal Güvenlik Çerçevesi:** Bu tip simülasyonlar, ulusal enerji şebekesi (Smart Grid) güvenliği için sertifikasyon süreçlerine temel oluşturabilir[cite: 40].

### ⚠️ Tehditler (Threats)
* [cite_start]**Şebeke Dengesinde Bozulma:** Gerçek bir senaryoda, bu tür manipüle edilmiş veriler trafolarda aşırı ısınmaya ve bölgesel elektrik kesintilerine yol açabilir[cite: 32, 34].
* [cite_start]**Fiziksel Sabotaj:** Saldırganların istasyona fiziksel erişim sağlayarak donanım tabanlı manipülasyon yapma riski, sadece yazılımla engellenemez[cite: 41, 58].
* [cite_start]**MITM (Ortadaki Adam) Saldırıları:** Ağ trafiğinin şifrelenmediği veya sertifika doğrulamalarının zayıf olduğu durumlarda, saldırganlar iletişimi tamamen ele geçirebilir[cite: 10, 41].

## 📸 Ekran Görüntüleri (Kanıtlar)

### 1. Sistem Başlatıldı
![Sistem Başlatıldı](1_Sistem_Baslatildi.png)

### 2. Normal Durum
![Normal Durum](2_Normal_Durum.png)
![Normal Durum](3_Normal_Durum.png)

### 3. Alarm Kanıtı
![Saldırı Anı](4_Saldiri_Ani.png)

### 4. Saldırı Anı
![Alarm Kanıtı](5_Alarm_Kaniti.png)
