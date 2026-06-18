# SecureVision AI — Sistem Mimarisi

## Genel Bakış

SecureVision AI, beş temel katmandan oluşan çok katmanlı bir güvenlik mimarisi üzerine inşa edilmiştir. Her katman belirli bir güvenlik fonksiyonunu yerine getirerek uçtan uca koruma sağlar.

## Mimari Diyagram

```
                    ┌──────────────────────────┐
                    │     KULLANICI ARAYÜZÜ    │
                    │   (frontend/templates/)   │
                    │  Landing · Login · Dash   │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │     BACKEND (Flask)       │
                    │   (backend/app.py)        │
                    │                           │
                    │  ┌─────┐ ┌─────┐ ┌─────┐ │
                    │  │auth │ │ api │ │cyber│ │
                    │  └──┬──┘ └──┬──┘ └──┬──┘ │
                    │     │      │       │     │
                    │  ┌──▼──────▼───────▼──┐  │
                    │  │  external_api.py    │  │
                    │  │  (NVD CVE API)      │  │
                    │  └────────────────────┘  │
                    └─────┬──────────┬─────────┘
                          │          │
              ┌───────────▼──┐  ┌───▼───────────┐
              │  AI MODÜLÜ   │  │  VERİTABANI   │
              │ (ai_module/) │  │ (database/)    │
              │              │  │                │
              │ ┌──────────┐ │  │ ┌────────────┐│
              │ │ YOLOv8   │ │  │ │  SQLite DB ││
              │ │ Detector │ │  │ │            ││
              │ └──────────┘ │  │ │ · users    ││
              │ ┌──────────┐ │  │ │ · logs     ││
              │ │Autoencdr │ │  │ │ · reports  ││
              │ │ Anomaly  │ │  │ │ · events   ││
              │ └──────────┘ │  │ │ · cve_cache││
              │ ┌──────────┐ │  │ └────────────┘│
              │ │CyberSec  │ │  └───────────────┘
              │ │ Attack/  │ │
              │ │ Defense  │ │
              │ └──────────┘ │
              │ ┌──────────┐ │
              │ │ Camera   │ │
              │ │ WebCam   │ │
              │ └──────────┘ │
              └──────────────┘
```

## Katman Detayları

### Katman 1: Veri Toplama (camera.py)
- Thread tabanlı kare yakalama
- Frame-skipping ile CPU optimizasyonu
- 640x480 çözünürlük stabilizasyonu

### Katman 2: Nesne Tespiti (detector.py)
- YOLOv8-Nano modeli
- Yalnızca insan sınıfı tespiti (classes=[0])
- Bounding box ve güven skoru çıktısı

### Katman 3: Anomali Analizi (autoencoder.py)
- Convolutional Autoencoder (Encoder → Decoder)
- Yeniden Yapılandırma Hatası (MSE) bazlı anomali skorlaması
- Yakınlık ve düşme tespiti ek risk faktörleri

### Katman 4: Siber Güvenlik (cybersecurity.py)
- **Saldırı**: Yüksek frekanslı grid paraziti ile CNN filtrelerini bozan adversarial perturbation
- **Savunma**: Median Blur → Gaussian Blur → Sharpening filtre dizisi
- **Log Güvenliği**: SHA-256 kriptografik hash ile veri bütünlüğü

### Katman 5: Raporlama ve Erişim Kontrolü
- RBAC ile Yönetici/Operatör rol ayrımı
- SQLite veritabanında kalıcı depolama
- JSON/PDF formatında vaka dışa aktarımı

## Veri Akışı

```
Kamera → Frame → [Saldırı?] → [Savunma?] → YOLOv8 → İnsan Tespiti
                                                        ↓
                                              Bounding Box Kırpma
                                                        ↓
                                              Autoencoder Skoru
                                                        ↓
                                              Anomali Kararı (MSE > θ)
                                                        ↓
                                    ┌───────────────────┴────────────────┐
                                    ↓                                    ↓
                              SHA-256 Hash                          Ekrana Çizim
                              ile Loglama                          (Bounding Box)
                                    ↓
                              SQLite DB'ye
                              Kaydetme
```

## Harici API Entegrasyonu

- **API**: NIST NVD CVE API (services.nvd.nist.gov)
- **Amaç**: Sistem bileşenleri ile ilişkili siber güvenlik tehditlerinin/açıklarının izlenmesi
- **Önbellek**: 10 dakika (DB + bellek içi)
- **Fallback**: API erişilemezse demo/fallback CVE listesi gösterilir
