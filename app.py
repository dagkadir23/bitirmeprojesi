from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for, send_file
import cv2
import time
import os
import json
import hashlib
import psutil
from fpdf import FPDF
from core.camera import WebCamera
from core.detector import HumanDetector
from core.autoencoder import AnomalyDetector
from core.cybersecurity import CyberSecurityDefense
from core.tracker import AnomalyTracker
from core.utils import draw_anomaly_box

app = Flask(__name__)
app.secret_key = os.urandom(24)

try:
    camera = WebCamera(camera_index=0, frame_skip=2)
except Exception as e:
    print(f"Kamera Hatası: {e}")
    camera = None

detector = HumanDetector(model_name="yolov8n.pt")
anomaly_detector = AnomalyDetector(threshold=0.20)
cyber_defense = CyberSecurityDefense(apply_blur=True)
tracker = AnomalyTracker(timeout=3.0)

system_state = {
    "is_attack_active": False,
    "is_defense_active": True,
    "log_integrity_status": "Bütünlük Doğrulandı"
}
stats = {"fps": 0, "last_anomaly": "Yok", "total_anomalies": 0, "current_status": "Güvenli"}
logs = []

def generate_frames():
    global stats, logs, system_state
    prev_time = time.time()
    
    while True:
        if camera is None:
            import numpy as np
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "KAMERA DONANIMI BULUNAMADI", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(1)
            continue
            
        ret, process_this_frame, frame = camera.get_frame()
        if not ret or frame is None: 
            import numpy as np
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "GORUNTU ALINAMIYOR (IZIN HATASI)", (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
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
                if crop.size == 0: continue
                
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
                    if len(logs) > 30: logs.pop() 
                
                draw_anomaly_box(frame, box, score, is_anomaly=is_anomaly)

            tracker.update(frame_anomaly_found, highest_score, best_behavior)
            stats["current_status"] = "Risk Tespit Edildi" if frame_anomaly_found else "Güvenli"

        # Uyarı Metinleri
        if system_state["is_attack_active"]: cv2.putText(frame, "ADVERSARIAL PERTURBATION: AKTIF", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        if system_state["is_defense_active"]: cv2.putText(frame, "SAVUNMA FILTRESI: AKTIF", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# --- ROUTES & RBAC ---
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api'): return jsonify({"error": "Unauthorized"}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/figures/<path:filename>')
def serve_figure(filename):
    figures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
    return send_file(os.path.join(figures_dir, filename), mimetype='image/png')

@app.route('/dashboard')
@login_required
def index():
    return render_template('index.html', role=session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if password == '123':
            session['logged_in'] = True
            session['role'] = 'admin' if username.lower() == 'admin' else 'operator'
            return redirect('/dashboard')
        return "Kimlik Doğrulaması Başarısız! <a href='/login'>Geri Dön</a>", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
@login_required
def api_stats():
    # Analitik Metrik Simülasyonu
    cpu = psutil.cpu_percent()
    is_compromised = system_state["is_attack_active"] and not system_state["is_defense_active"]
    metrics = {
        "accuracy": 45.2 if is_compromised else 94.8,
        "f1_score": 0.38 if is_compromised else 0.92,
        "false_alarm_rate": "Yüksek (Saldırı)" if is_compromised else "%2.4",
        "cpu_usage": f"%{cpu}",
        "processing_time": f"{round(1000/max(1, stats['fps']), 1)} ms"
    }
    return jsonify({
        "stats": stats, 
        "logs": [{"time": l["time"], "message": l["message"], "hash": l["hash"][:15]+"..."} for l in logs[:5]],
        "state": system_state,
        "metrics": metrics
    })

# --- CYBER CONTROL ENDPOINTS ---
@app.route('/api/toggle_attack', methods=['POST'])
@login_required
def toggle_attack():
    if session.get('role') != 'admin': return jsonify({"error": "Yetkisiz İşlem"}), 403
    system_state["is_attack_active"] = not system_state["is_attack_active"]
    return jsonify({"state": system_state["is_attack_active"]})

@app.route('/api/toggle_defense', methods=['POST'])
@login_required
def toggle_defense():
    if session.get('role') != 'admin': return jsonify({"error": "Yetkisiz İşlem"}), 403
    system_state["is_defense_active"] = not system_state["is_defense_active"]
    return jsonify({"state": system_state["is_defense_active"]})

@app.route('/api/verify_logs', methods=['POST'])
@login_required
def verify_logs():
    corrupted = sum(1 for log in logs if not cyber_defense.verify_log_hash(log["raw_data"], log["hash"]))
    system_state["log_integrity_status"] = f"Bütünlük Doğrulaması Başarısız! ({corrupted} Tahribat)" if corrupted else "Bütünlük Doğrulandı"
    return jsonify({"status": system_state["log_integrity_status"]})

@app.route('/api/poison_log', methods=['POST'])
@login_required
def poison_log():
    if session.get('role') != 'admin': return jsonify({"error": "Yetkisiz İşlem"}), 403
    if len(logs) == 0:
        fk_data = {"box": [0,0,50,50], "score": 0.35, "time": time.time(), "type": "Test"}
        logs.insert(0, {"time": time.strftime('%H:%M:%S'), "message": "Normal Davranış (0.35)", "raw_data": fk_data, "hash": cyber_defense.generate_log_hash(fk_data)})
    logs[0]["raw_data"]["score"] = 99.99
    logs[0]["message"] = "LOG MANİPÜLASYONU TESPİT EDİLDİ"
    return jsonify({"success": True})

# --- REPORT EXPORTS ---
@app.route('/api/reports')
@login_required
def get_reports():
    rep = []
    # Tarih filtresine yönelik arayüze data dönüyoruz
    for r in tracker.get_all_reports():
        hashed_id = hashlib.sha256(str(r).encode('utf-8')).hexdigest()[:10]
        rep.append({
            "id": r["id"],
            "behavior": r.get("behavior_type", "Bilinmeyen"),
            "start": time.strftime('%H:%M:%S', time.localtime(r["start_time"])),
            "date": time.strftime('%Y-%m-%d', time.localtime(r["start_time"])),
            "duration": round(r["duration"], 1),
            "max_score": round(r["max_score"], 2),
            "hash": hashed_id
        })
    return jsonify({"reports": rep})

@app.route('/download_reports/<format>')
@login_required
def download_reports(format):
    reports = tracker.get_all_reports()
    if format == 'json':
        file_path = os.path.join(os.getcwd(), 'vaka_raporu.json')
        with open(file_path, 'w', encoding='utf-8') as f: json.dump(reports, f, indent=4, ensure_ascii=False)
        return send_file(file_path, as_attachment=True)
    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Siber Guvenlik Vaka Raporu", ln=True, align='C')
        pdf.ln(10)
        for r in reports:
            st = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r["start_time"]))
            bh = str(r.get("behavior_type", "N/A")).replace('ı', 'i').replace('ş', 's').replace('ğ', 'g').replace('ç', 'c').replace('ö', 'o').replace('ü', 'u').replace('İ', 'I').replace('Ş', 'S').replace('Ğ', 'G').replace('Ç', 'C').replace('Ö', 'O').replace('Ü', 'U') # FPDF ASCII issue bypass
            pdf.cell(200, 10, txt=f"ID: {r['id']} | Zaman: {st}", ln=True)
            pdf.cell(200, 10, txt=f"Davranis: {bh} | Sure: {round(r['duration'],1)} sn | Skor: {round(r['max_score'],2)}", ln=True)
            pdf.ln(5)
        file_path = os.path.join(os.getcwd(), 'vaka_raporu.pdf')
        pdf.output(file_path)
        return send_file(file_path, as_attachment=True)
    return "Invalid format", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
