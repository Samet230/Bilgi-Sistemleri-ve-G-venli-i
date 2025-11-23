⚡ Python OCPP 1.6 Charge Point Simülatörü

Bu proje; Python kullanarak SteVe OCPP 1.6 Sunucusuna bağlanan bir elektrikli araç şarj istasyonu (Charge Point) simülasyonudur. Simülasyon, gerçek bir EV şarj istasyonunun gönderdiği tüm kritik mesaj akışlarını birebir uygular:

BootNotification

Heartbeat

StatusNotification

Authorize

StartTransaction

MeterValues

StopTransaction

Projede ayrıca kritik bir güvenlik açığı tespit edilmiş, saldırı (PoC) gerçekleştirilmiş ve gerekli önlemler raporlanmıştır.

📌 1. Amaç

Elektrikli araç şarj istasyonlarının OCPP protokolü üzerinden SteVe sunucusuna nasıl bağlandığını tamamen otomatik, gerçekçi, protokole sadık ve güvenlik odaklı bir şekilde simüle etmek. Bu senaryo, bir EV şarj oturumunun başından sonuna kadar gerçekleşen tüm olayları açık şekilde göstermektedir.

📌 2. Sistem Mimarisi

Python Script (ChargePoint) → WebSocket (OCPP 1.6) → SteVe OCPP Back-End Server

Simülatör, SteVe’ye şu endpoint üzerinden bağlanır:
ws://localhost:8180/steve/websocket/CentralSystemService/CP-TEST-01

📌 3. Kurulum

Gerekli paketleri yükleyin:
pip install ocpp websockets

Simülatörü çalıştırın:
python cp_sim.py

📌 4. Gerçek Şarj Senaryosu Akışı

Aşağıdaki adımlar gerçek bir istasyonun davranışlarını birebir simüle eder:

BootNotification
İstasyon kendisini tanıtır. SteVe kabul ederse bağlantı resmileşir.

Heartbeat
SteVe’nin belirlediği interval süresine göre düzenli "hayattayım" mesajı gönderilir.

StatusNotification
İstasyonun durumu sırasıyla: Available → Preparing → Charging → Finishing → Available olarak bildirilir.

Authorize
Gönderilen idTag SteVe tarafından doğrulanır. Tanımlı değilse Invalid / Blocked döner.

StartTransaction
Yeni bir transaction_id oluşur ve şarj oturumu resmen başlar.

MeterValues
Sayaç (Wh) değeri artarak gönderilir. Bu gerçek bir EV’nin enerji tüketimini simüle eder.

StopTransaction
Oturum sonlandırılır. Tüm işlem SteVe loglarına kaydedilir.

📌 5. Güvenlik Açığı: Yetkisiz Kart ile Şarj Başlatılması

Açık şu şekilde keşfedildi:

Authorize = Invalid olmasına rağmen SteVe StartTransaction'ı kabul ediyor.
Bu durum yetkisiz kullanıcıların şarj başlatabilmesi anlamına gelir.

Bu açık sayesinde saldırgan:

Kayıtsız idTag ile işlem başlatabilir

Enerji hırsızlığı yapabilir

Log kayıtlarını manipüle edebilir

Sistemin doğruluk ve güvenilirliğini bozabilir

📌 6. Saldırı Senaryosu (PoC)

Saldırı çıktısı:

Authorize cevabı: status = Invalid
StartTransaction cevabı: transaction_id = 1 (kabul edildi!)

Yani:

Authorize reddediliyor → Ama şarj yine de başlatılıyor.

Daha sonra saldırgan enerji akışını simüle eden MeterValues gönderiyor. StopTransaction cevabı “Blocked” gelse bile enerji çoktan tüketilmiş oluyor.

📌 7. Açığın Etkileri

Enerji hırsızlığı

Şirkete maddi zarar

Doğru kullanıcı tespiti yapılamaması

Transaction loglarının sahte görünmesi

Hukuki risk

OCPP 1.6 kimlik doğrulamasının atlatılabilmesi

📌 8. Saldırı Nasıl Yapıldı?

Kayıtsız idTag gönderildi

SteVe bu idTag için “Invalid” döndürdü

Buna rağmen StartTransaction gönderildi ve kabul edildi

Saldırgan MeterValues ile enerji çekiyormuş gibi veri gönderdi

StopTransaction ile oturum kapandı ama enerji çoktan tüketilmişti

📌 9. Çözüm: Açığı Nasıl Kapatırız?

Script tarafında yetkilendirme kontrolü eklenmeli:
Eğer idTag “Accepted” değilse işlem başlamamalı.

SteVe tarafında Strict Authorization Mode aktif edilmeli:
Authorization Required = true
Allow StartTransaction without Authorization = false
Local Pre-Authorize = false

StartTransaction sırasında idTag tekrar doğrulanmalı.

Şifreli bağlantı (TLS / WSS) zorunlu hale getirilmeli:
ws:// yerine wss:// kullanılmalı.

IP whitelist uygulanmalı.

📌 10. Sonuç

Bu proje ile:

OCPP 1.6 mesaj akışı tamamen simüle edildi

SteVe sunucusuyla tam entegrasyon sağlandı

Yetkisiz şarj başlatma açığı keşfedildi

Açık PoC ile doğrulandı

Gerekli tüm güvenlik önlemleri raporlandı