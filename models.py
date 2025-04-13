from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
from flask_login import UserMixin

class Application(db.Model):
    id = db.Column(db.String(5), primary_key=True)  # 5位随机字符串作为app_id
    name = db.Column(db.String(80), unique=True, nullable=False)
    secret_key = db.Column(db.String(32), nullable=False)
    redirect_uri = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tokens = db.Column(db.Text, default='{}')  # 存储token和过期时间(JSON格式)

    def generate_totp_uri(self):
        return pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=self.name,
            issuer_name="TOTP统一认证系统"
        )

class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
