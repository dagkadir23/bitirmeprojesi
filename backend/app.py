"""
app.py - SecureVision AI Backend Ana Uygulaması

Flask tabanlı backend uygulaması. Blueprint mimari yapısı ile modüler tasarım.
Bileşenler:
- Kimlik doğrulama (RBAC)
- REST API endpointleri
- Siber güvenlik kontrolleri
- Harici API entegrasyonu (NIST NVD CVE API)
- Gerçek zamanlı kamera akışı
"""

from flask import Flask, render_template, Response, send_file, session
import cv2
import time
import os
import sys
import numpy as np

# Proje kök dizinini Python path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.config import (
    SECRET_KEY, TEMPLATE_FOLDER, STATIC_FOLDER,
    FIGURES_DIR, YOLO_MODEL_PATH
)

# ==========================================
# FLASK UYGULAMA OLUŞTURMA
# ==========================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_FOLDER,
    static_folder=STATIC_FOLDER,
    static_url_path='/static'
)
app.secret_key = SECRET_KEY

# ==========================================
# BLUEPRINT KAYITLARI
# ==========================================

from backend.routes.auth import auth_bp
from backend.routes.api import api_bp
from backend.routes.cyber import cyber_bp
from backend.routes.external_api import external_api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(cyber_bp)
app.register_blueprint(external_api_bp)

# ==========================================
# AI MODÜLÜ BAŞLATMA
# ==========================================

from ai_module.camera import WebCamera
from ai_module.detector import HumanDetector
from ai_module.autoencoder import AnomalyDetector
from ai_module.cybersecurity import CyberSecurityDefense
from ai_module.tracker import AnomalyTracker
from ai_module.utils import draw_anomaly_box

try:
    camera = WebCamera(camera_index=0, frame_skip=2)
except Exception as e:
    print(f"Kamera Hatası: {e}")
    camera = None

detector = HumanDetector(model_name=YOLO_MODEL_PATH)
anomaly_detector = AnomalyDetector(threshold=0.20)
cyber_defense = CyberSecurityDefense(apply_blur=True)
tracker = AnomalyTracker(timeout=3.0)

# ==========================================
# GLOBAL DURUM DEĞİŞKENLERİ
# ==========================================

system_state = {
    "is_attack_active": False,
    "is_defense_active": True,
    "log_integrity_status": "Bütünlük Doğrulandı"
}

stats = {
    "fps": 0,
    "last_anomaly": "Yok",
    "total_anomalies": 0,
    "current_status": "Güvenli"
}

logs = []

# ==========================================
# KAMERA GÖRÜNTÜ AKIŞI
# ==========================================

def generate_frames():
    """Kameradan gerçek zamanlı görüntü akışı üretir."""
    global stats, logs, system_state
    prev_time = time.time()

    while True:
        if camera is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "KAMERA DONANIMI BULUNAMADI", (50, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(1)
            continue

        ret, process_this_frame, frame = camera.get_frame()
        if not ret or frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "GORUNTU ALINAMIYOR (IZIN HATASI)", (30, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.5)
            continue

        current_time = time.time()
        fps = 1 / (current_time - prev_time + 0.001)
        prev_time = current_time
        stats["fps"] = round(fps, 1)

        # SİBER SALDIRI (Adversarial Perturbation Simülasyonu)
        if system_state["is_attack_active"]:
            frame = cyber_defense.apply_attack(frame)

        # SİBER SAVUNMA (Ön-Filtre)
        if system_state["is_defense_active"]:
            frame = cyber_defense.apply_defense(frame)

        if process_this_frame:
            humans = detector.detect(frame)
            frame_anomaly_found = False
            highest_score = 0
            best_behavior = "Normal Davranış"

            for human in humans:
                box = human["box"]
                crop = frame[box[1]:box[3], box[0]:box[2]]
                if crop.size == 0:
                    continue

                is_attack_unmitigated = system_state["is_attack_active"] and not system_state["is_defense_active"]
                score, behavior = anomaly_detector.compute_anomaly_score(crop, is_attacked=is_attack_unmitigated)
                is_anomaly = anomaly_detector.is_anomaly(score)

                if score > highest_score:
                    highest_score = score
                    best_behavior = behavior

                if is_anomaly:
                    frame_anomaly_found = True
                    stats["total_anomalies"] += 1
                    stats["last_anomaly"] = f"Skor: {score:.2f}"

                    log_data = {"box": box, "score": score, "time": time.time(), "type": behavior}
                    log_hash = cyber_defense.generate_log_hash(log_data)

                    logs.insert(0, {
                        "time": time.strftime('%H:%M:%S'),
                        "message": f"{behavior} ({score:.2f})",
                        "raw_data": log_data,
                        "hash": log_hash
                    })
                    if len(logs) > 30:
                        logs.pop()

                    # Veritabanına da kaydet
                    try:
                        from backend.models import insert_anomaly_log
                        insert_anomaly_log(
                            message=f"{behavior} ({score:.2f})",
                            anomaly_score=score,
                            behavior_type=behavior,
                            bbox_data=box,
                            hash_value=log_hash
                        )
                    except Exception:
                        pass  # DB hatası akışı durdurmasın

                draw_anomaly_box(frame, box, score, is_anomaly=is_anomaly)

            tracker.update(frame_anomaly_found, highest_score, best_behavior)
            stats["current_status"] = "Risk Tespit Edildi" if frame_anomaly_found else "Güvenli"

        # Uyarı Metinleri
        if system_state["is_attack_active"]:
            cv2.putText(frame, "ADVERSARIAL PERTURBATION: AKTIF", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        if system_state["is_defense_active"]:
            cv2.putText(frame, "SAVUNMA FILTRESI: AKTIF", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


# ==========================================
# ANA ROTALAR
# ==========================================

@app.route('/')
def landing():
    """Proje tanıtım sayfası."""
    return render_template('landing.html')


@app.route('/dashboard')
def index():
    """Ana kontrol paneli (login gerekli)."""
    from backend.routes.auth import login_required
    if not session.get('logged_in'):
        return app.redirect('/login')
    return render_template('dashboard.html', role=session.get('role'))


@app.route('/video_feed')
def video_feed():
    """Gerçek zamanlı kamera akışı."""
    if not session.get('logged_in'):
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 401
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/figures/<path:filename>')
def serve_figure(filename):
    """Grafik görsellerini serve eder."""
    return send_file(os.path.join(FIGURES_DIR, filename), mimetype='image/png')


# ==========================================
# UYGULAMA BAŞLATMA
# ==========================================

def create_app():
    """Uygulama factory fonksiyonu."""
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
