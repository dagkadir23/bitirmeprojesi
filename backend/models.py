"""
models.py - SecureVision AI Veritabanı Modelleri (SQLite + sqlite3)

Bu modül, veritabanı CRUD işlemlerini yöneten yardımcı fonksiyonları içerir.
"""

import sqlite3
import hashlib
import json
import time
import os
from backend.config import DATABASE_PATH


def get_db_connection():
    """Veritabanı bağlantısı döndürür."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Dict benzeri erişim
    return conn


def hash_password(password):
    """SHA-256 ile şifre hashleme."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ==========================================
# KULLANICI İŞLEMLERİ
# ==========================================

def authenticate_user(username, password):
    """
    Kullanıcı adı ve şifre ile kimlik doğrulaması yapar.
    Başarılı ise kullanıcı dict'i, başarısız ise None döner.
    """
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()

    if user:
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    return None


def get_all_users():
    """Tüm kullanıcıları döndürür."""
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, role, created_at FROM users").fetchall()
    conn.close()
    return [dict(u) for u in users]


# ==========================================
# ANOMALİ LOG İŞLEMLERİ
# ==========================================

def insert_anomaly_log(message, anomaly_score, behavior_type, bbox_data, hash_value):
    """Yeni anomali log kaydı ekler."""
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO anomaly_logs (message, anomaly_score, behavior_type, bbox_data, hash_value)
           VALUES (?, ?, ?, ?, ?)""",
        (message, anomaly_score, behavior_type, json.dumps(bbox_data), hash_value)
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit=30):
    """En son anomali loglarını döndürür."""
    conn = get_db_connection()
    logs = conn.execute(
        "SELECT * FROM anomaly_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(l) for l in logs]


# ==========================================
# VAKA RAPORU İŞLEMLERİ
# ==========================================

def insert_incident_report(incident_id, start_time, end_time, duration, max_score, behavior_type, hash_value):
    """Tamamlanmış vaka raporunu veritabanına kaydeder."""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO incident_reports 
               (incident_id, start_time, end_time, duration, max_score, behavior_type, hash_value)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (incident_id, start_time, end_time, duration, max_score, behavior_type, hash_value)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Aynı incident_id zaten varsa atla
    finally:
        conn.close()


def get_all_incident_reports():
    """Tüm vaka raporlarını döndürür."""
    conn = get_db_connection()
    reports = conn.execute(
        "SELECT * FROM incident_reports ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in reports]


# ==========================================
# SİSTEM OLAY KAYDI
# ==========================================

def log_system_event(event_type, event_data=None, username=None):
    """Sistem olayı kaydeder."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO system_events (event_type, event_data, username) VALUES (?, ?, ?)",
        (event_type, json.dumps(event_data) if event_data else None, username)
    )
    conn.commit()
    conn.close()


# ==========================================
# CVE ÖNBELLEĞİ (TEHDİT İSTİHBARATI)
# ==========================================

def cache_cve_data(cve_id, source, published_date, description, cvss_score, severity, keyword):
    """CVE güvenlik açığı verisini önbelleğe kaydeder."""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO cve_cache (cve_id, source, published_date, description, cvss_score, severity, keyword)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cve_id, source, published_date, description, cvss_score, severity, keyword)
        )
        conn.commit()
    except Exception as e:
        print(f"[CVE Kayıt Hatası] {e}")
    finally:
        conn.close()


def get_cached_cves(max_age_seconds=600):
    """Önbellekteki en güncel CVE verilerini döndürür (max_age_seconds içinde)."""
    conn = get_db_connection()
    result = conn.execute(
        """SELECT * FROM cve_cache 
           WHERE fetched_at >= datetime('now', ?) 
           ORDER BY cvss_score DESC, published_date DESC""",
        (f'-{max_age_seconds} seconds',)
    ).fetchall()
    conn.close()
    return [dict(r) for r in result]


def clear_cve_cache():
    """Önbellekteki CVE verilerini temizler."""
    conn = get_db_connection()
    conn.execute("DELETE FROM cve_cache")
    conn.commit()
    conn.close()
