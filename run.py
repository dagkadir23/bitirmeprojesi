"""
run.py - SecureVision AI Başlatma Scripti

Tek komutla sistemi başlatır:
1. Veritabanını kontrol eder/oluşturur
2. Flask uygulamasını başlatır

Kullanım: python run.py
"""

import os
import sys

# Proje kök dizinini Python path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def ensure_database():
    """Veritabanı yoksa oluşturur."""
    db_path = os.path.join(PROJECT_ROOT, "database", "securevision.db")

    if not os.path.exists(db_path):
        print("[BİLGİ] Veritabanı bulunamadı, oluşturuluyor...")
        from database.init_db import init_database
        init_database()
        print("[OK] Veritabanı hazır.\n")
    else:
        print(f"[OK] Veritabanı mevcut: {db_path}")


def main():
    print("=" * 60)
    print("  SecureVision AI - Akıllı Güvenlik Kamerası Sistemi")
    print("  Adversarial Dayanıklılık ve Siber Savunma Platformu")
    print("=" * 60)
    print()

    # 1. Veritabanı kontrolü
    ensure_database()

    # 2. Flask uygulamasını başlat
    print("\n[BİLGİ] Flask sunucusu başlatılıyor...")
    print("[BİLGİ] Tarayıcıda açın: http://localhost:5000")
    print("[BİLGİ] Durdurmak için Ctrl+C\n")

    from backend.app import app
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)


if __name__ == '__main__':
    main()
