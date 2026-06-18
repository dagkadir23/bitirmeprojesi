"""
config.py - SecureVision AI Yapılandırma Dosyası
"""

import os

# Proje kök dizini (bitirme/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Veritabanı
DATABASE_PATH = os.path.join(PROJECT_ROOT, "database", "securevision.db")

# Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "securevision-ai-2026-secret-key")

# Frontend yolları
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, "frontend", "templates")
STATIC_FOLDER = os.path.join(PROJECT_ROOT, "frontend", "static")

# AI Modülü
AI_MODULE_PATH = os.path.join(PROJECT_ROOT, "ai_module")
YOLO_MODEL_PATH = os.path.join(AI_MODULE_PATH, "yolov8n.pt")

# Harici API - NIST NVD (National Vulnerability Database)
# Güvenlik kamerası sistemleriyle ilgili bilinen güvenlik açıklarını sorgular
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = os.environ.get("NVD_API_KEY", "")  # Opsiyonel, rate limit artırır
NVD_CACHE_SECONDS = 600  # 10 dakika önbellek
NVD_SEARCH_KEYWORDS = ["surveillance camera", "YOLO", "OpenCV", "adversarial attack"]

# Figures
FIGURES_DIR = os.path.join(PROJECT_ROOT, "frontend", "static", "figures")
