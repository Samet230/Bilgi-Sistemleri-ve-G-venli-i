# 🔐 Anomi AI - EV Charging Infrastructure Security

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Elektrikli Araç Şarj Altyapısı için Yapay Zeka Destekli Siber Güvenlik Anomali Tespit Sistemi**

[🚀 Kurulum](#-kurulum) • [📊 Özellikler](#-özellikler) • [👥 Ekip](#-ekip) • [📖 Dokümantasyon](#-dokümantasyon)

</div>

---

## 📖 Proje Hakkında

**Anomi AI**, elektrikli araç (EV) şarj istasyonları ve OCPP (Open Charge Point Protocol) altyapısındaki siber güvenlik tehditlerini tespit etmek için geliştirilmiş kapsamlı bir sistemdir.

### 🎯 Tespit Edilen Anomali Türleri

| # | Anomali | Açıklama |
|---|---------|----------|
| 1 | OCPP Mesaj Enjeksiyonu | Yetkisiz şarj komutları |
| 2 | TLS Downgrade Saldırıları | Şifreleme zayıflatma |
| 3 | Tarife Manipülasyonu | Fiyat/faturalandırma hileleri |
| 4 | Yük Verisi Manipülasyonu | Enerji tüketim sahteciliği |
| 5 | CAN Bus Saldırıları | Araç içi ağ anomalileri |
| 6 | CSMS Backend Saldırıları | Merkezi sistem güvenliği |
| 7 | Kimlik Doğrulama Atakları | Plaka/RFID sahteciliği |
| 8 | IDS/IPS Güvenlik Olayları | Ağ sızma girişimleri |
| 9 | Zaman Manipülasyonu | Sistem saati saldırıları |
| 10 | RemoteStop Saldırıları | OCPP komut enjeksiyonu |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                      ANOMI AI SİSTEMİ                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Random    │    │   Gradient  │    │    Extra    │     │
│  │   Forest    │    │   Boosting  │    │    Trees    │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            ▼                                │
│                   ┌─────────────────┐                       │
│                   │ ENSEMBLE VOTING │                       │
│                   │   (Oy Çokluğu)  │                       │
│                   └────────┬────────┘                       │
│                            ▼                                │
│         ┌─────────────────────────────────────┐             │
│         │         KARAR: NORMAL / SALDIRI     │             │
│         │         Güven Skoru: %XX.X          │             │
│         └─────────────────────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Proje Yapısı

```
Bilgi-Sistemleri-ve-Güvenliği/
│
├── 📁 logiz-ensemble-standalone/      # Ana Web Uygulaması
│   ├── 📁 backend/                    # Flask API (Python)
│   │   ├── app.py                     # Ana sunucu
│   │   └── requirements.txt           # Python bağımlılıkları
│   └── 📁 frontend/                   # Next.js Dashboard
│       ├── app/                       # React bileşenleri
│       └── package.json               # Node bağımlılıkları
│
├── 📁 models_ensemble/                # Eğitilmiş AI Modelleri
│   ├── SAMET_RF.joblib               # Random Forest modeli
│   ├── SAMET_GBM.joblib              # Gradient Boosting modeli
│   └── SAMET_ET.joblib               # Extra Trees modeli
│
├── 📁 models_can_bus/                 # CAN Bus Anomali Modeli
│   └── can_bus_detector.joblib       # Araç içi ağ tespiti
│
├── 📁 Raporlar/                       # Ekip Üyesi Raporları
│   ├── SAMET_SAHIN/                  # IDS Güvenlik Senaryosu
│   ├── EMİRHAN_BSG/                  # OCPP Enjeksiyon
│   ├── YOUSEF_BSG/                   # TLS Saldırıları
│   └── ...                           # Diğer üyeler
│
├── 📁 scripts/                        # Yardımcı Scriptler
│   ├── training/                     # Model eğitim scriptleri
│   ├── analysis/                     # Analiz araçları
│   └── utils/                        # Yardımcı araçlar
│
├── detect_attack_ensemble.py          # Ana Tespit Modülü
└── README.md                          # Bu dosya
```

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.10+
- Node.js 18+
- pip ve npm

### Backend Kurulumu

```bash
# Repoyu klonla
git clone https://github.com/Samet230/Bilgi-Sistemleri-ve-G-venli-i.git
cd Bilgi-Sistemleri-ve-G-venli-i

# Backend dizinine git
cd logiz-ensemble-standalone/backend

# Sanal ortam oluştur (önerilen)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu başlat
python app.py
```

Backend `http://localhost:5050` adresinde çalışacak.

### Frontend Kurulumu

```bash
# Yeni terminal aç
cd logiz-ensemble-standalone/frontend

# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev
```

Frontend `http://localhost:3000` adresinde çalışacak.

---

## 📊 Özellikler

### 1. 🎛️ Dashboard
- Gerçek zamanlı tehdit izleme
- Görsel istatistikler ve grafikler
- Saldırı türü dağılımı

### 2. 📤 Dosya Analizi
- CSV/JSON log dosyası yükleme
- Toplu anomali tespiti
- Detaylı rapor çıktısı

### 3. ⚡ Hızlı Analiz
- Tek log satırı analizi
- Anlık sonuç

### 4. 📡 Canlı İzleme
- SSH üzerinden uzak sunucu izleme
- Gerçek zamanlı log akışı
- Agent tabanlı veri toplama

---

## 🔧 API Kullanımı

### Tekli Log Analizi

```bash
curl -X POST http://localhost:5050/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"log": "Failed SSH login attempt from 192.168.1.100", "dataset_type": "SAMET"}'
```

### Yanıt Örneği

```json
{
  "attack_detected": true,
  "final_decision": "Kaba Kuvvet Saldırısı",
  "confidence_score": 0.94,
  "winning_model": "RF",
  "council_votes": ["RF: SALDIRI", "GBM: SALDIRI", "ET: NORMAL"]
}
```

---

## 👥 Ekip

| Üye | Senaryo |
|-----|---------|
| **Samet Şahin** (Scrum Master) | IDS/IPS Güvenlik Logları (LogIz) |
| Emirhan Aydemir | Yetkisiz Şarj Komutu Enjeksiyonu |
| İrem Tüfekçi | CAN Bus Anomalisi |
| İbrahim Şahin | CSMS Backend Anomalisi |
| Emirhan Turan | Zaman/Tarife Manipülasyonu |
| Miraç Polat | Plaka/Kimlik Doğrulama |
| Suzan Battal | Tarife Manipülasyonu |
| Atakan Akyol | Yük Verisi Manipülasyonu |
| Yousef Taljibini | TLS Downgrade Saldırıları |
| Ali Giriş | OCPP RemoteStop Saldırısı |

---

## 📈 Model Performansı

| Dataset | Accuracy | Precision | Recall | F1 Score |
|---------|----------|-----------|--------|----------|
| SAMET (IDS) | 99.2% | 98.5% | 99.1% | 98.8% |
| CAN Bus | 99.9% | 99.9% | 100% | 99.9% |
| OCPP | 97.8% | 96.2% | 98.4% | 97.3% |

---

## 📋 Proje Durumu

- [x] Anomali senaryolarının belirlenmesi
- [x] Veri setlerinin toplanması ve etiketlenmesi
- [x] AI modellerinin eğitilmesi (Ensemble + CAN Bus)
- [x] LogIz Web Dashboard geliştirmesi
- [x] Canlı izleme sistemi
- [x] False positive optimizasyonu
- [ ] Final sunum ve video

---

## 📄 Lisans

Bu proje **Bandırma Onyedi Eylül Üniversitesi - Bilgi Sistemleri ve Güvenliği** dersi kapsamında geliştirilmiştir.

---

<div align="center">

**© 2026 Anomi AI Team - Ekip 10**

</div>
