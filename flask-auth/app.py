from flask import Flask
from flask_migrate import Migrate
from extensions import db, login_manager
import os
from werkzeug.security import generate_password_hash

app = Flask(__name__)
migrate = Migrate(app, db)
login_manager.init_app(app)
login_manager.login_view = 'admin.login'

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return db.session.get(AdminUser, int(user_id))
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 初始化默认管理员
def init_admin():
    from models import AdminUser
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(
            username='admin',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created. Username: admin, Password: admin123')

# 注册蓝图
from routes.auth import auth_bp
from routes.admin import admin_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_admin()
    app.run(host='0.0.0.0', port=5000, debug=True)
