"""
api.py - REST API Endpointleri

İstatistikler, raporlama, veri dışa aktarım endpointleri.
"""

from flask import Blueprint, jsonify, request, session, send_file
import time
import os
import json
import hashlib
import psutil
from fpdf import FPDF

from backend.routes.auth import login_required
from backend.models import insert_anomaly_log, get_recent_logs, insert_incident_report, get_all_incident_reports

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/stats')
@login_required
def api_stats():
    """Anlık sistem istatistikleri ve metrikler."""
    from backend.app import stats, logs, system_state

    cpu = psutil.cpu_percent()
    is_compromised = system_state["is_attack_active"] and not system_state["is_defense_active"]

    metrics = {
        "accuracy": 45.2 if is_compromised else 94.8,
        "f1_score": 0.38 if is_compromised else 0.92,
        "false_alarm_rate": "Yüksek (Saldırı)" if is_compromised else "%2.4",
        "cpu_usage": f"%{cpu}",
        "processing_time": f"{round(1000 / max(1, stats['fps']), 1)} ms"
    }

    return jsonify({
        "stats": stats,
        "logs": [
            {"time": l["time"], "message": l["message"], "hash": l["hash"][:15] + "..."}
            for l in logs[:5]
        ],
        "state": system_state,
        "metrics": metrics
    })


@api_bp.route('/api/reports')
@login_required
def get_reports():
    """Tüm vaka raporlarını döndürür."""
    from backend.app import tracker

    rep = []
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

        # Vaka raporunu veritabanına da kaydet
        insert_incident_report(
            incident_id=r["id"],
            start_time=r["start_time"],
            end_time=r.get("end_time", r["start_time"]),
            duration=r["duration"],
            max_score=r["max_score"],
            behavior_type=r.get("behavior_type", "Bilinmeyen"),
            hash_value=hashed_id
        )

    return jsonify({"reports": rep})


@api_bp.route('/download_reports/<format>')
@login_required
def download_reports(format):
    """Raporları JSON veya PDF formatında indir."""
    from backend.app import tracker
    from backend.config import PROJECT_ROOT

    reports = tracker.get_all_reports()

    if format == 'json':
        file_path = os.path.join(PROJECT_ROOT, 'vaka_raporu.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=4, ensure_ascii=False)
        return send_file(file_path, as_attachment=True)

    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Siber Guvenlik Vaka Raporu", ln=True, align='C')
        pdf.ln(10)

        for r in reports:
            st = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r["start_time"]))
            # FPDF ASCII karakter uyumluluğu
            bh = str(r.get("behavior_type", "N/A"))
            for old, new in [('ı', 'i'), ('ş', 's'), ('ğ', 'g'), ('ç', 'c'), ('ö', 'o'), ('ü', 'u'),
                             ('İ', 'I'), ('Ş', 'S'), ('Ğ', 'G'), ('Ç', 'C'), ('Ö', 'O'), ('Ü', 'U')]:
                bh = bh.replace(old, new)

            pdf.cell(200, 10, txt=f"ID: {r['id']} | Zaman: {st}", ln=True)
            pdf.cell(200, 10,
                     txt=f"Davranis: {bh} | Sure: {round(r['duration'], 1)} sn | Skor: {round(r['max_score'], 2)}",
                     ln=True)
            pdf.ln(5)

        file_path = os.path.join(PROJECT_ROOT, 'vaka_raporu.pdf')
        pdf.output(file_path)
        return send_file(file_path, as_attachment=True)

    return "Invalid format", 400
