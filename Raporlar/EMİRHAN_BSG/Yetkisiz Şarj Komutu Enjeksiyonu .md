Yetkisiz Şarj Komutu Enjeksiyonu 


Hazırlayan:Emirhan Aydemir
Öğrenci No: 230542031
Ders: Bilgi Sistemleri Güvenliği 


1. Giriş ve Amaç

Bu rapor, elektrikli araçların (EV) şarj sistemlerinde meydana gelebilecek güvenlik açıklarını incelemek amacıyla hazırlanmıştır. Özellikle 'Yetkisiz Şarj Komutu Enjeksiyonu' adı verilen saldırı türü ele alınarak, bu saldırının olası etkileri ve önlenmesi için alınabilecek teknik önlemler değerlendirilmiştir.

2. Sistemin Temel Yapısı ve Çalışma Prensibi

Elektrikli araçlar, şarj istasyonları (EVSE) ile OCPP veya ISO 15118 gibi protokoller üzerinden haberleşir. Bu iletişimde şarj başlatma (StartCharging) ve durdurma (StopCharging) gibi komutlar kullanılır. Aşağıdaki şekil sistem mimarisini basitleştirilmiş olarak göstermektedir.
[Şekil 1: EV - EVSE - Backend Sistem Mimarisi (şema eklenecektir)]

3. Anomalinin Tanımlanması

Yetkisiz Şarj Komutu Enjeksiyonu, saldırganın sahte mesajlar göndererek şarj sürecini bozduğu bir saldırı türüdür. Aşağıdaki diyagram, saldırı akışının genel yapısını göstermektedir.
[Şekil 2: Saldırı Akışı Diyagramı (MITM - Injection - Impact)]

4. Tehdit Modeli ve Saldırı Senaryosu

Saldırgan Tipi	Erişim Türü	Amaç	Örnek Senaryo
Fiziksel	Servis Portu	Cihaz Manipülasyonu	Kasanın açılıp porttan komut gönderilmesi
Ağ Tabanlı	Wi-Fi / LAN	Komut Enjeksiyonu	MITM ile OCPP mesajı değiştirme
Uzaktan	Backend	DoS / Sabotaj	CSMS açığı ile çoklu istasyon hedefleme

5. Zafiyetin Teknik Nedenleri

Bu saldırılar aşağıdaki teknik eksikliklerden kaynaklanır:
- Sertifika doğrulama eksikliği
- TLS yanlış yapılandırması
- Komut imzalama yokluğu
- Güvensiz debug portlar
- Zayıf loglama ve denetim sistemleri

6. Risk Değerlendirmesi ve Etki Analizi

Aşağıdaki tablo olasılık ve etki düzeylerine göre risk sınıflandırmasını göstermektedir:

Risk Türü	Olasılık	Etki
Yetkisiz Faturalandırma	Yüksek	Yüksek
Erken Şarj Kesilmesi	Orta	Yüksek
Veri Manipülasyonu	Düşük	Orta

7. Anomali Tespiti Yaklaşımı

Aşağıdaki tablo IDS/ML model performanslarını göstermektedir:

Model	Doğruluk (%)	Precision	Recall
Random Forest	98.4	97.8	98.0
KNN	96.5	95.1	95.9
MLP	97.2	96.3	96.8

8. Çözüm ve Önleme Yöntemleri

Donanım Düzeyi:
- Port izolasyonu
- Güvenli çip kullanımı (TPM)

Yazılım Düzeyi:
- Mesaj imzalama, nonce kontrolü
- Rate‑limiting

Ağ Düzeyi:
- Mutual TLS, sertifika yenileme
- Şifreli iletişim

Operasyonel Düzey:
- IDS log izleme
- Olay müdahale planlarının uygulanması

9. Olay Müdahale Planı

Bir saldırı tespit edildiğinde izlenecek temel adımlar aşağıdaki gibidir:
1. Etkilenen sistemin ağdan izole edilmesi
2. Günlük kayıtlarının (log) incelenmesi
3. Sertifika ve anahtarların iptali
4. Adli bilişim incelemesi yapılması
5. Sistemlerin güvenli şekilde yeniden devreye alınması
[Şekil 3: Olay Müdahale Süreci (İzolasyon → İnceleme → Kurtarma)]

10. Sonuç ve Değerlendirme

Yetkisiz şarj komutu enjeksiyonu, hem kullanıcı hem de altyapı güvenliği açısından ciddi risk taşır. Çok katmanlı savunma yaklaşımlarıyla (donanım, yazılım, ağ, operasyonel) bu tehdit azaltılabilir. Yapay zekâ destekli güvenlik sistemleri gelecekte proaktif koruma sağlayacaktır.

11. SWOT Analizi – Yetkisiz Şarj Komutu Enjeksiyonu Güvenliği


Güçlü Yönler (Strengths)	Zayıf Yönler (Weaknesses)
• Gelişmiş şifreleme protokollerinin (TLS, Mutual-Auth) uygulanabilirliği	• Sertifika yönetimi ve kimlik doğrulama maliyeti yüksek
• Makine öğrenimi tabanlı IDS sistemlerinin erken tespit başarısı	• Donanım izolasyonunun tüm istasyonlarda standart olmaması
• Güçlü protokol temeli (OCPP 2.0.1, ISO 15118)	• Günlük (log) analizlerinin çoğu işletmede eksik olması
• Güvenlik testlerinin (fuzzing, red-team) yapılabilirliği	• OTA güncellemelerinin yetersiz kontrol edilmesi


Fırsatlar (Opportunities)	Tehditler (Threats)
• Uluslararası güvenlik standartlarının (SAE J3061 vb.) yaygınlaşması	• Saldırganların artan siber araç yetkinliği
• Elektrikli araç altyapısının hızla gelişmesi → Güvenlik bilincinin artması	• Tedarik zincirinde güvenlik açıklarının zincirleme etkisi
• IDS sistemlerinin bulut tabanlı entegrasyonu	• Fiziksel portlara erişimle doğrudan saldırı riski
• Üniversite–sanayi iş birliğiyle siber güvenlik Ar-Ge’si	• Eski (legacy) şarj istasyonlarında yazılım güncellemelerinin uygulanmaması


12. Kaynakça

Open Charge Alliance. (2022). OCPP 2.0.1 specification. Open Charge Alliance. https://www.openchargealliance.org/
International Organization for Standardization. (2014). ISO 15118-2: Road vehicles — Vehicle-to-grid communication interface — Part 2: Network and application protocol requirements. ISO.
International Electrotechnical Commission. (2014). IEC 61851-24: Electric vehicle conductive charging system — Digital communication between a DC EV charging station and an electric vehicle for control of DC charging. IEC.
IEEE Dataport. (2024). CIC-EVSE 2024 dataset. IEEE Dataport.
Society of Automotive Engineers. (2016). SAE J3061: Cybersecurity guidebook for cyber-physical vehicle systems. SAE International.
European Network for Cyber Security (ENCS). (2023). EV charging infrastructure cybersecurity: Threat landscape and mitigation strategies. ENCS Publications.
Aydemir, E. (2025). Yetkisiz şarj komutu enjeksiyonu için SWOT analizi – Güçlü, zayıf yönler, fırsatlar ve tehditler değerlendirmesi. Elazığ: Fırat Üniversitesi, Yazılım Mühendisliği Bölümü.


