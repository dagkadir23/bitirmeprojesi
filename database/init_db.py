"""
init_db.py - SecureVision AI Veritabanı Başlatma Scripti

Bu script, SQLite veritabanını oluşturur ve varsayılan kullanıcıları ekler.
Kullanım: python database/init_db.py
"""

import sqlite3
import os
import hashlib

# Proje kök dizinini belirle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "securevision.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def hash_password(password):
    """Basit SHA-256 tabanlı şifre hashleme (demo amaçlı)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_database():
    """Veritabanını oluşturur ve varsayılan verileri ekler."""
    print("=" * 50)
    print("  SecureVision AI - Veritabanı Başlatılıyor")
    print("=" * 50)

    # Mevcut veritabanını kontrol et
    db_exists = os.path.exists(DB_PATH)
    if db_exists:
        print(f"\n  [BİLGİ] Mevcut veritabanı bulundu: {DB_PATH}")
        print("  [BİLGİ] Tablolar varsa atlanacak (IF NOT EXISTS)")

    # Veritabanı bağlantısı
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Şema dosyasını oku ve çalıştır
    print("\n  [1/3] Şema uygulanıyor...")
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("  [OK] Tablolar oluşturuldu.")

    # Varsayılan kullanıcıları ekle (yoksa)
    print("\n  [2/3] Varsayılan kullanıcılar ekleniyor...")
    default_users = [
        ("admin", hash_password("123"), "admin"),
        ("operator", hash_password("123"), "operator"),
    ]

    for username, pw_hash, role in default_users:
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, pw_hash, role)
            )
            print(f"  [OK] Kullanıcı eklendi: {username} (rol: {role})")
        except sqlite3.IntegrityError:
            print(f"  [ATLANDI] Kullanıcı zaten mevcut: {username}")

    # Başlangıç sistem olayı
    print("\n  [3/3] Başlangıç olayı kaydediliyor...")
    cursor.execute(
        "INSERT INTO system_events (event_type, event_data) VALUES (?, ?)",
        ("db_init", '{"message": "Veritabanı başarıyla başlatıldı"}')
    )

    conn.commit()
    conn.close()

    print(f"\n  Veritabanı hazır: {DB_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    init_database()
