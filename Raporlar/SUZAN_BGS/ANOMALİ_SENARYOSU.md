# ⚠ Anomali Senaryosu – Enerji Fiyatlandırma Güvenliği (OCPP)

## Rapor: Senaryo — Fiyatlandırma Parametrelerinin Sık ve Aralıklı Değişimi ile Hatalı Faturalama
**Senaryo Başlığı:**  
Dinamik Tarife Değişimi → Fiyat Tutarsızlığı → Hatalı Faturalama ve Energy Fraud Riski

---

## 🧾 Özet

Bu senaryoda, elektrikli araç şarj altyapısında enerji fiyatlandırma parametreleri  
(**birim fiyat, zaman dilimi, güç bazlı ücretlendirme, kampanya ve vergi bileşenleri**)  
kısa süreler içinde ve düzensiz aralıklarla değiştirilir.

Bu değişiklikler; teknik hata, yanlış yapılandırma veya kötü niyetli müdahale sonucu  
ortaya çıkarak **fiyat tutarsızlığı**, **hatalı faturalama** ve  
**kullanıcı güven kaybı** ile sonuçlanan kritik bir anomali oluşturur.

---

## 1️⃣ Başlangıç Durumu

- Şarj istasyonu (CS), merkezi sistem (CSMS) ile OCPP üzerinden haberleşmektedir.
- Fiyatlandırma:
  - Zaman dilimi
  - Güç seviyesi
  - İstasyon bazlı tarifeler
  üzerinden dinamik olarak belirlenir.
- Normal koşullarda:
  - Fiyat parametreleri oturum başlamadan önce belirlenir
  - Oturum süresince sabit kalması beklenir

---

## 2️⃣ Anomali Oluşumu

- CSMS tarafında:
  - Tarife parametreleri kısa aralıklarla güncellenir.
- Güncellemeler:
  - Düzensiz zamanlarda
  - Farklı istasyonlara farklı gecikmelerle
  iletilir.

Bu durumda:
- Aynı şarj oturumu sırasında birden fazla fiyat uygulanabilir.
- İstasyon ile CSMS arasında **senkronizasyon bozulur**.

---

## 3️⃣ Anomali Akışı / Sömürü

- Aktif bir şarj oturumu devam ederken:
  - Birim fiyat değiştirilir.
- Kısa süre sonra:
  - Zaman dilimi tarifesi güncellenir.
- Ardından:
  - Kampanya veya vergi bileşeni eklenir ya da kaldırılır.

**Sonuçlar:**
- Kullanıcıya gösterilen fiyat ile
- Faturalandırılan tutar arasında fark oluşur.
- Aynı kullanıcı için:
  - ücretsiz şarj
  - fazla ücretlendirme
  - çift faturalama
  senaryoları ortaya çıkabilir.

---

## 4️⃣ Algılama Mantığı (Detection Logic)

Aşağıdaki göstergeler anomali sinyali olarak değerlendirilir:

- Belirli bir zaman penceresinde fiyat parametresi değişim sayısı eşik değeri aşıyor mu?
- Aktif şarj oturumu sırasında fiyat değişimi yapılmış mı?
- Aynı oturum için birden fazla tarife versiyonu kullanılmış mı?
- CSMS hesaplaması ile şarj istasyonu raporları uyumsuz mu?
- `MeterValues` ile faturalandırma çıktıları tutarlı mı?

---

## 5️⃣ Karar ve Tepki Mekanizması

Anomali tespit edildiğinde sistem aşağıdaki aksiyonları alır:

1. Aktif şarj oturumu için **fiyat kilitleme (price lock)** uygulanır.
2. İlgili tarife versiyonu oturum sonuna kadar sabitlenir.
3. Anomali alarmı üretilir ve loglanır.
4. Şüpheli oturumlar için:
   - Faturalama geçici olarak askıya alınır
   - Manuel doğrulama süreci başlatılır

---

## 6️⃣ Log Örneği

```text
2025-11-05T14:22:10Z | StationID: ST-104 | event=PRICE_UPDATE
param=unit_price | old=2.45 | new=3.90 | anomaly=FREQUENT_CHANGE


2025-11-05T14:22:40Z | StationID: ST-104 | event=PRICE_LOCK_APPLIED
session_id=TX-88921 | tariff_version=v3.2 | action=LOCKED
