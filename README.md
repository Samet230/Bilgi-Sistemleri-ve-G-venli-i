# BilgiSistemGuvenligi-ekip10 🔐

Elektrikli Araç Şarj Altyapısı (EV Charging Infrastructure) için **Siber Güvenlik Anomali Tespit Sistemi**.

## 🚀 Proje Özeti

Bu proje, elektrikli araç şarj istasyonları ve ağ altyapısındaki **siber güvenlik açıklarını** tespit etmek için geliştirilmiş bir yapay zeka destekli izleme ve analiz sistemidir.

### Ana Bileşenler:
- **LogIz Ensemble**: 3 farklı AI modelinin oy çokluğuyla tehdit tespiti yapan akıllı sistem
- **Canlı İzleme**: Harici sunuculardan gelen logları gerçek zamanlı analiz eden dashboard
- **Esnek Ajan**: Kendi test senaryolarınızı (şarj anomalisi, zaman kayması vb.) canlı olarak görselleştirme

## 📂 Klasör Yapısı

| Klasör | Açıklama |
|--------|----------|
| `logiz-ensemble-standalone/` | Ana uygulama (Frontend + Backend) |
| `Raporlar/` | Takım üyelerinin bireysel anomali raporları |
| `models_ensemble/` | Eğitilmiş Ensemble AI modelleri |
| `test_data/` | Test veri setleri |

## 🛠️ Kurulum ve Çalıştırma

### Backend (Python Flask)
```bash
cd logiz-ensemble-standalone/backend
pip install -r requirements.txt
python app.py
```

### Frontend (Next.js)
```bash
cd logiz-ensemble-standalone/frontend
npm install
npm run dev
```

### Canlı İzleme için Ajan (Linux)
```bash
# flexible_agent.py dosyasını Linux sunucunuza kopyalayın
# IP adresini düzenleyin
sudo python3 flexible_agent.py --file /var/log/auth.log
# Veya kendi test scriptinizi pipe edin:
python3 test_anomaly.py | python3 flexible_agent.py
```

## 👥 Takım Üyeleri ve Senaryolar

| Üye | Anomali Senaryosu |
|-----|-------------------|
| YOUSEF | OCPP & Network Attack Vectors |
| SUZAN | Energy Consumption & Price Manipulation |
| İREM | Network Traffic & CAN Bus Anomalies |
| MİRAÇ | Charging Station Registration & Auth |
| EMİRHAN | Kubernetes/OCP Security Incidents |
| SAMET | IDS/IPS Security Logs (Kritik Altyapı) |
| EMİRHNT | Time Shift & Billing Anomaly |
| İBRAHİM | System Time Manipulation |
| ATAKAN | Load Data Manipulation |

## 📋 Proje Aşamaları

- [x] Kişisel dosyalar ve ön araştırma
- [x] Makale seçimi ve SWOT analizi
- [x] Anomali senaryolarının belirlenmesi
- [x] Simülasyon ortamının kurulması
- [x] AI modellerinin eğitilmesi (Ensemble Suite)
- [x] LogIz Dashboard ve Canlı İzleme sistemi
- [ ] Final video ve sunum

---

**NOT:** Anomali konusu: Elektrikli araçlar ve şarj noktaları arasında oluşabilecek siber açıklık.  
**NOT:** Orijinal README yedek olarak `README_ORIGINAL.md` dosyasında saklanmaktadır.
