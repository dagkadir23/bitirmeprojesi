# SecureVision AI — Akıllı Güvenlik Kamerası Sistemi

**Adversarial Dayanıklılık ve Siber Savunma Platformu**

Fırat Üniversitesi · Teknoloji Fakültesi · Yazılım Mühendisliği  
Lisans Bitirme Projesi — 2026

---

## 📋 Proje Tanımı

Bu proje, yapay zeka tabanlı güvenlik kamerası sistemlerinin **adversarial perturbation** saldırılarına karşı savunmasızlığını ele almaktadır. YOLOv8 nesne tespiti ve Convolutional Autoencoder anomali analizi üzerine inşa edilmiş çok katmanlı bir siber savunma mimarisi sunulmaktadır.

### Temel Özellikler

- 🎯 **Gerçek Zamanlı İnsan Tespiti** — YOLOv8-Nano ile kamera görüntüsünde anlık insan algılama
- 🧠 **Anomali Tespiti** — Convolutional Autoencoder ile davranış anomalisi skorlaması
- 🛡️ **Adversarial Savunma** — Median Blur + Gaussian + Sharpening filtre zinciri
- 🔐 **SHA-256 Log Bütünlüğü** — Kriptografik hash ile olay kaydı mühürleme
- 👤 **RBAC Erişim Kontrolü** — Yönetici ve Operatör rol ayrımı
- 🛡️ **Harici API Entegrasyonu** — NIST NVD CVE API ile siber tehdit istihbaratı izleme
- 📊 **Kurumsal Raporlama** — JSON/PDF formatında vaka dışa aktarımı

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    KULLANICI ARAYÜZÜ                        │
│              HTML5 / CSS3 / JavaScript                       │
│         Landing Page | Login | Dashboard                     │
├─────────────────────────────────────────────────────────────┤
│                     BACKEND (Flask)                          │
│   REST API | RBAC | Blueprint Mimarisi | Oturum Yönetimi    │
├──────────────┬──────────────────┬────────────────────────────┤
│  AI MODÜLÜ   │   VERİTABANI     │    HARİCİ API             │
│  YOLOv8      │   SQLite         │    NIST NVD CVE API       │
│  Autoencoder │   Kullanıcılar   │    Tehdit Analizi         │
│  CyberSec    │   Loglar         │                            │
│  Tracker     │   Raporlar       │                            │
└──────────────┴──────────────────┴────────────────────────────┘
```

---

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknolojiler |
|--------|-------------|
| **Arayüz** | HTML5, CSS3, JavaScript, TailwindCSS, Font Awesome |
| **Backend** | Python 3.10+, Flask, Blueprint Mimarisi, REST API |
| **Yapay Zeka** | YOLOv8 (Ultralytics), PyTorch, Convolutional Autoencoder |
| **Görüntü İşleme** | OpenCV, NumPy |
| **Veritabanı** | SQLite3 |
| **Harici API** | NIST NVD CVE API |
| **Güvenlik** | SHA-256 Hash, RBAC, Oturum Yönetimi |
| **Raporlama** | FPDF, JSON |

---

## 📁 Proje Dizin Yapısı

```
bitirme/
├── frontend/                    # Arayüz Katmanı
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/dashboard.js, landing.js
│   │   └── figures/             # Grafik görselleri
│   └── templates/
│       ├── landing.html
│       ├── login.html
│       └── dashboard.html
│
├── backend/                     # Backend Katmanı
│   ├── app.py                   # Flask ana uygulama
│   ├── config.py                # Konfigürasyon
│   ├── models.py                # Veritabanı modelleri
│   ├── routes/
│   │   ├── auth.py              # Kimlik doğrulama
│   │   ├── api.py               # REST API
│   │   ├── cyber.py             # Siber güvenlik
│   │   └── external_api.py      # Harici API (Threat Intelligence)
│   └── requirements.txt
│
├── ai_module/                   # Yapay Zeka Bileşeni
│   ├── autoencoder.py           # Convolutional Autoencoder
│   ├── detector.py              # YOLOv8 insan tespiti
│   ├── cybersecurity.py         # Adversarial saldırı/savunma
│   ├── tracker.py               # Olay takipçisi
│   ├── camera.py                # Kamera yönetimi
│   ├── utils.py                 # Yardımcı fonksiyonlar
│   └── yolov8n.pt               # Model ağırlıkları
│
├── database/                    # Veritabanı Katmanı
│   ├── schema.sql               # SQL şeması
│   ├── init_db.py               # Veritabanı başlatma
│   └── securevision.db          # SQLite veritabanı (runtime)
│
├── docs/                        # Dokümantasyon
│   └── system_architecture.md
│
├── evaluate.py                  # Performans değerlendirme
├── generate_figures.py          # Grafik üretimi
├── run.py                       # Ana başlatma scripti
└── README.md                    # Bu dosya
```

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.10 veya üzeri
- Web kamerası (opsiyonel, yoksa demo modu çalışır)

### Kurulum

```bash
# 1. Projeyi klonlayın
git clone https://github.com/kullanici/securevision-ai.git
cd securevision-ai

# 2. Bağımlılıkları yükleyin
pip install -r backend/requirements.txt

# 3. Sistemi başlatın (veritabanı otomatik oluşturulur)
python run.py
```

### Harici API Yapılandırması (Opsiyonel)

NIST NVD API anahtarını ayarlamak için (NIST API key isteğe bağlıdır, ancak rate limit sınırını artırır):

```bash
# Windows
set NVD_API_KEY=your_api_key_here

# Linux/Mac
export NVD_API_KEY=your_api_key_here
```

> **Not:** API key olmadan da sistem otomatik olarak demo/fallback tehdit istihbaratı verileri ve sınırlı istek hızıyla sorunsuz çalışır.

---

## 🖥️ Demo Açıklaması

### Kullanıcı Rolleri

| Rol | Kullanıcı Adı | Şifre | Yetkiler |
|-----|--------------|-------|----------|
| **Yönetici** | admin | 123 | Tüm kontroller (saldırı, savunma, manipülasyon) |
| **Operatör** | operator | 123 | Salt izleme (dashboard görüntüleme) |

### Demo Senaryosu

1. **Giriş**: `http://localhost:5000` adresine gidin → "Sisteme Giriş" butonuna tıklayın
2. **Dashboard**: Canlı kamera akışını ve metrikleri izleyin
3. **Adversarial Saldırı**: "Adversarial Perturbation" butonuyla saldırı başlatın
4. **Savunma**: "Savunma Filtresi" ile modelin tekrar çalışmasını sağlayın
5. **Log Bütünlüğü**: "Manipüle Et" ve "Check" butonları ile veri zehirleme testi yapın
6. **Tehdit İstihbaratı**: Sağ paneldeki widget'ta güncel siber güvenlik açıklarını (CVE) görüntüleyin
7. **Raporlama**: Alt bölümde vakaları filtreleyin ve JSON/PDF olarak indirin

---

## 📊 Deneysel Sonuçlar

| Senaryo | Doğruluk | F1-Skor | Yanlış Alarm |
|---------|----------|---------|-------------|
| Normal Koşullar | %97.0 | 0.952 | %4.0 |
| Saldırı Altında | %44.8 | 0.496 | %74.9 |
| Savunma Aktif | %96.0 | 0.938 | %5.7 |

---

## 📄 Lisans

Bu proje Fırat Üniversitesi Teknoloji Fakültesi Yazılım Mühendisliği Bölümü lisans bitirme projesi kapsamında geliştirilmiştir.
