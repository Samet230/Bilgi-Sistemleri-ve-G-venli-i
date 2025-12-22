# 📄 Veri Seti Açıklaması

## Veri Seti Genel Bakış
Bu veri seti, **şarj istasyonu sistemleri** ve **ağ / güvenlik izleme kaynaklarından** toplanan logların birleştirilmiş ve temizlenmiş hâlini içerir.  
Veri seti hem **normal sistem olaylarını** hem de **saldırı / anomali senaryolarını** kapsar ve **Makine Öğrenmesi (ML)** çalışmalarında kullanılmak üzere hazırlanmıştır.

Tüm kategorik değerler tutarlılık sağlamak amacıyla **BÜYÜK HARFE (UPPERCASE)** dönüştürülmüştür.

---

## 📊 Sütun Açıklamaları

### `event_type`
Sistemde gerçekleşen olayın türünü belirtir.

**Olası değerler:**
- `CONNECTION` – Sistemler arasında bağlantı kurulması  
- `START_CHARGING` – Şarj işleminin başlatılması  
- `ENERGY_USAGE` – Enerji tüketimi / sayaç bilgisi  
- `OTHER` – Yukarıdakilere uymayan diğer olaylar  

---

### `status`
Olayın gerçekleştiği andaki sistem veya işlem durumunu gösterir.

**Olası değerler:**
- `INFO` – Bilgilendirme mesajı  
- `SUCCESS` – İşlem başarıyla tamamlandı  
- `WARNING` – Şüpheli veya olağandışı durum  
- `OK` – Normal çalışma durumu  
- `CHARGING` – Şarj işlemi devam ediyor  
- `PREPARING` – Şarj için hazırlanıyor  
- `AVAILABLE` – İstasyon veya konnektör müsait  
- `SUSPENDEDEV` – Şarj, araç tarafından askıya alındı  
- `FAULTED` – Sistem veya donanım hatası  
- `BLOCKED` – Güvenlik nedeniyle işlem engellendi  

---

### `attack_type`
Tespit edilen saldırı veya anomali türünü belirtir.

**Olası değerler:**
- `NULL` – Saldırı yok (normal davranış)  
- `LATERAL_MOVEMENT` – Yan hareket / ağ keşfi  
- `PRICE_SPIKE` – Ani ve anormal fiyat artışı  
- `FREQUENT_IRREGULAR_CHANGE` – Sık ve düzensiz değişiklikler  
- `SPOOFED_METER_VALUES` – Sahte / değiştirilmiş sayaç değerleri  
- `NEGATIVE_PRICE` – Geçersiz negatif fiyat  
- `PRICE_DROP` – Ani ve anormal fiyat düşüşü  
- `TLS_DOWGRADE_DETECTED` – TLS downgrade saldırısı tespit edildi  
- `OCPP_INJECTION_ATTEMPT` – Yetkisiz OCPP mesaj enjeksiyonu  
- `OCPP_CMD_REJECTED` – OCPP komutu güvenlik nedeniyle reddedildi  
- `OCPP_VALIDATION_FAIL` – OCPP mesaj doğrulaması başarısız  

---

## 📝 Notlar
- `attack_type = NULL` → **Normal davranış**  
- Veri seti, makine öğrenmesi modelleri için **standartlaştırılmış ve temizlenmiştir**  
- Kullanım alanları:
  - Normal / saldırı sınıflandırması  
  - Saldırı türü tahmini  
  - Anomali tespiti  

---

### `label`
Bu sütun, ilgili kaydın **makine öğrenmesi açısından sınıf etiketini** belirtir.  
Model eğitimi sırasında, bir olayın **normal mi yoksa saldırı/anomali mi** olduğunu ayırt etmek için kullanılır.

**Olası değerler:**
- `0` → **Normal (Benign)**  
  - Sistem beklenen şekilde çalışmaktadır  
  - Herhangi bir saldırı veya anomali tespit edilmemiştir  
  - Genellikle `attack_type = NULL` durumuna karşılık gelir  

- `1` → **Saldırı / Anomali (Malicious)**  
  - Güvenlik ihlali, şüpheli davranış veya anomali tespit edilmiştir  
  - TLS saldırıları, OCPP enjeksiyonları, fiyat manipülasyonları vb. durumları kapsar  

---

### 📌 Önemli Notlar
- `label` sütunu, **hedef değişken (target variable)** olarak kullanılır  
- Denetimli öğrenme (Supervised Learning) senaryoları için uygundur  
- `label = 1` olan tüm kayıtlar, **en az bir anomali veya saldırı türü** içermektedir  

---

### 🎯 Kullanım Amacı
Bu etiketleme sayesinde:
- Normal ve saldırı trafiği ayrıştırılabilir  
- Saldırı tespit modelleri eğitilebilir  
- Gerçek zamanlı anomali algılama sistemleri geliştirilebilir  


## ✅ Makine Öğrenmesi İçin Hazır
Bu veri seti; özellik çıkarımı, encoding ve model eğitimi için doğrudan kullanılabilir durumdadır.
