-- ============================================================
-- SecureVision AI - Veritabanı Şeması
-- Akıllı Güvenlik Kamerası Sistemi
-- ============================================================

-- Kullanıcı tablosu (RBAC - Rol Bazlı Erişim Kontrolü)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'operator' CHECK(role IN ('admin', 'operator')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomali log tablosu (SHA-256 hash mühürlü)
CREATE TABLE IF NOT EXISTS anomaly_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    anomaly_score REAL NOT NULL,
    behavior_type TEXT,
    bbox_data TEXT,           -- JSON formatında bounding box koordinatları
    hash_value TEXT NOT NULL,  -- SHA-256 kriptografik hash
    is_manipulated INTEGER DEFAULT 0
);

-- Vaka (Incident) raporları tablosu
CREATE TABLE IF NOT EXISTS incident_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL UNIQUE,  -- UUID kısa referans
    start_time REAL NOT NULL,
    end_time REAL,
    duration REAL DEFAULT 0.0,
    max_score REAL DEFAULT 0.0,
    behavior_type TEXT DEFAULT 'Bilinmeyen',
    hash_value TEXT            -- Adli bütünlük hash değeri
);

-- Sistem olay günlüğü
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,   -- 'login', 'logout', 'attack_toggle', 'defense_toggle', 'log_verify', vb.
    event_data TEXT,            -- JSON formatında ek veri
    username TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CVE önbellek tablosu (Harici API verisi)
CREATE TABLE IF NOT EXISTS cve_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cve_id TEXT NOT NULL UNIQUE,
    source TEXT,
    published_date TEXT,
    description TEXT,
    cvss_score REAL,
    severity TEXT,
    keyword TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
