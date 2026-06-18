"""
auth.py - Kimlik Doğrulama Rotaları

Kullanıcı girişi, çıkışı ve oturum yönetimi.
RBAC (Rol Bazlı Erişim Kontrolü) desteği.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for
from backend.models import authenticate_user, log_system_event

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Oturum doğrulama dekoratörü."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api'):
                from flask import jsonify
                return jsonify({"error": "Unauthorized"}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfası ve kimlik doğrulaması."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = authenticate_user(username, password)
        if user:
            session['logged_in'] = True
            session['role'] = user['role']
            session['username'] = user['username']

            # Giriş olayını kaydet
            log_system_event('login', {'role': user['role']}, user['username'])

            return redirect('/dashboard')

        return "Kimlik Doğrulaması Başarısız! <a href='/login'>Geri Dön</a>", 401

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Kullanıcı çıkışı ve oturum temizleme."""
    username = session.get('username', 'unknown')
    log_system_event('logout', None, username)
    session.clear()
    return redirect('/login')
