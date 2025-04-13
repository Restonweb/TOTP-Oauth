from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Application, AdminUser
from extensions import db
import pyotp
import qrcode
import io
import base64
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('用户名或密码错误', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('请填写所有字段')
            return redirect(url_for('admin.change_password'))
            
        if new_password != confirm_password:
            flash('新密码不匹配')
            return redirect(url_for('admin.change_password'))
            
        user = AdminUser.query.get(current_user.id)
        if not user.check_password(current_password):
            flash('当前密码错误', 'error')
            return redirect(url_for('admin.change_password'))
            
        try:
            user.set_password(new_password)
            db.session.commit()
            flash('密码修改成功', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('密码修改失败: ' + str(e), 'error')
            return redirect(url_for('admin.change_password'))
    
    return render_template('admin/change_password.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    apps = Application.query.order_by(Application.created_at.desc()).all()
    return render_template('admin/dashboard.html', apps=apps)

@admin_bp.route('/app/delete/<string:app_id>', methods=['POST'])
@login_required
def delete_app(app_id):
    app = Application.query.get_or_404(app_id)
    db.session.delete(app)
    db.session.commit()
    flash('应用已删除')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/app/reset_secret/<string:app_id>', methods=['POST'])
@login_required
def reset_secret(app_id):
    app = Application.query.get_or_404(app_id)
    new_secret = pyotp.random_base32()
    app.secret_key = new_secret
    db.session.commit()
    
    # 生成新的QR码
    totp_uri = app.generate_totp_uri()
    img = qrcode.make(totp_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('admin/app_created.html', 
                        app=app,
                        qr_code=qr_code,
                        secret_key=new_secret)

@admin_bp.route('/app/create', methods=['GET', 'POST'])
@login_required
def create_app():
    if request.method == 'POST':
        name = request.form.get('name')
        redirect_uri = request.form.get('redirect_uri')
        
        if not name or not redirect_uri:
            flash('请填写所有字段')
            return redirect(url_for('admin.create_app'))
            
        secret_key = pyotp.random_base32()
        # 生成5位随机字母数字组合的app_id
        import random
        import string
        app_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        app = Application(id=app_id, name=name, secret_key=secret_key, redirect_uri=redirect_uri)
        db.session.add(app)
        db.session.commit()
        
        # 生成QR码
        totp_uri = app.generate_totp_uri()
        img = qrcode.make(totp_uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        return render_template('admin/app_created.html', 
                            app=app, 
                            qr_code=qr_code,
                            secret_key=secret_key)
    
    return render_template('admin/create_app.html')
