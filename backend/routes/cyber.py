"""
cyber.py - Siber Güvenlik Kontrol Endpointleri

Adversarial saldırı/savunma toggle, log bütünlüğü doğrulama,
veri zehirleme simülasyonu endpointleri.
"""

from flask import Blueprint, jsonify, session, request
import time

from backend.routes.auth import login_required
from backend.models import log_system_event

cyber_bp = Blueprint('cyber', __name__)


@cyber_bp.route('/api/toggle_attack', methods=['POST'])
@login_required
def toggle_attack():
    """Adversarial saldırı simülasyonunu aç/kapat (Yalnızca Admin)."""
    if session.get('role') != 'admin':
        return jsonify({"error": "Yetkisiz İşlem"}), 403

    from backend.app import system_state
    system_state["is_attack_active"] = not system_state["is_attack_active"]

    log_system_event('attack_toggle',
                     {"active": system_state["is_attack_active"]},
                     session.get('username'))

    return jsonify({"state": system_state["is_attack_active"]})


@cyber_bp.route('/api/toggle_defense', methods=['POST'])
@login_required
def toggle_defense():
    """Savunma filtresini aç/kapat (Yalnızca Admin)."""
    if session.get('role') != 'admin':
        return jsonify({"error": "Yetkisiz İşlem"}), 403

    from backend.app import system_state
    system_state["is_defense_active"] = not system_state["is_defense_active"]

    log_system_event('defense_toggle',
                     {"active": system_state["is_defense_active"]},
                     session.get('username'))

    return jsonify({"state": system_state["is_defense_active"]})


@cyber_bp.route('/api/verify_logs', methods=['POST'])
@login_required
def verify_logs():
    """Log kayıtlarının SHA-256 bütünlüğünü doğrular."""
    from backend.app import logs, system_state, cyber_defense

    corrupted = sum(
        1 for log in logs
        if not cyber_defense.verify_log_hash(log["raw_data"], log["hash"])
    )

    if corrupted:
        system_state["log_integrity_status"] = f"Bütünlük Doğrulaması Başarısız! ({corrupted} Tahribat)"
    else:
        system_state["log_integrity_status"] = "Bütünlük Doğrulandı"

    log_system_event('log_verify',
                     {"corrupted_count": corrupted},
                     session.get('username'))

    return jsonify({"status": system_state["log_integrity_status"]})


@cyber_bp.route('/api/poison_log', methods=['POST'])
@login_required
def poison_log():
    """Veri zehirleme (poisoning) saldırısı simülasyonu (Yalnızca Admin)."""
    if session.get('role') != 'admin':
        return jsonify({"error": "Yetkisiz İşlem"}), 403

    from backend.app import logs, cyber_defense

    if len(logs) == 0:
        fk_data = {"box": [0, 0, 50, 50], "score": 0.35, "time": time.time(), "type": "Test"}
        logs.insert(0, {
            "time": time.strftime('%H:%M:%S'),
            "message": "Normal Davranış (0.35)",
            "raw_data": fk_data,
            "hash": cyber_defense.generate_log_hash(fk_data)
        })

    logs[0]["raw_data"]["score"] = 99.99
    logs[0]["message"] = "LOG MANİPÜLASYONU TESPİT EDİLDİ"

    log_system_event('log_poison', None, session.get('username'))

    return jsonify({"success": True})
