from flask import Blueprint, request, redirect, url_for, jsonify
from models import Application
from extensions import db
import pyotp
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/verify', methods=['POST'])
def verify_totp():
    # 处理TOTP验证请求
    if request.form.get('code'):
        app_id = request.form.get('app_id')
        code = request.form.get('code')
        
        if not app_id or not code:
            from flask import render_template
            return render_template('error.html',
                                error_message='缺少必要参数',
                                app_id=app_id), 400

        app = Application.query.get(app_id)
        if not app:
            return jsonify({'error': '无效的应用ID'}), 404

        totp = pyotp.TOTP(app.secret_key)
        if not totp.verify(code, valid_window=1):
            from flask import render_template
            return render_template('error.html',
                                error_message='验证码无效',
                                app_id=app_id), 401

        # 生成访问令牌(有效期15分钟)
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        import json
        tokens = json.loads(app.tokens or '{}')
        tokens[token] = expires_at.isoformat()
        try:
            app.tokens = json.dumps(tokens)
            db.session.add(app)
            db.session.commit()
            print(f"Stored token: {token}, expires_at: {expires_at.isoformat()}")
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500
        
        # 构建回调URL并重定向
        callback_url = f"{app.redirect_uri}?token={token}"
        return redirect(callback_url)
    
    # 处理token验证请求
    elif request.json and request.json.get('token'):
        app_id = request.json.get('app_id')
        token = request.json.get('token')
        
        if not app_id or not token:
            return jsonify({'error': '缺少必要参数'}), 400

        app = Application.query.get(app_id)
        if not app:
            return jsonify({'error': '无效的应用ID'}), 404

        db.session.refresh(app)  # 确保获取最新数据
        import json
        tokens = json.loads(app.tokens or '{}')
        expires_str = tokens.get(token)
        print("expires_str:", expires_str)
        if not expires_str:
            return jsonify({'valid': False}), 401
            
        expires_at = datetime.fromisoformat(expires_str)
        print("expires_at:", expires_at)
        if datetime.utcnow() > expires_at:
            return jsonify({'valid': False}), 401
            
        return jsonify({'valid': True})
    
    return jsonify({'error': '无效的请求'}), 400

@auth_bp.route('/auth/<app_id>')
def auth_redirect(app_id):
    app = Application.query.get(app_id)
    if not app:
        return "无效的应用ID", 404
    return redirect(url_for('auth.totp_form', app_id=app_id))

@auth_bp.route('/totp/<app_id>')
def totp_form(app_id):
    from flask import render_template
    return render_template('totp_form.html', app_id=app_id)
