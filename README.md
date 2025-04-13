# 统一认证系统 (TOTPA)

基于Python Flask实现的简单TOTP(基于时间的一次性密码)统一认证系统样例，为多个应用提供集中式认证服务。

## 功能特性

- ✅ 基于时间的一次性密码(TOTP)认证
- ✅ 多应用统一认证管理
- ✅ TOTP密钥管理
- ✅ 可配置回调URL
- ✅ 管理界面

## 技术栈

- **后端**: Python Flask
- **数据库**: SQLite (开发环境)
- **前端**: Bootstrap 5 + Jinja2模板
- **认证**: PyOTP实现TOTP算法
- **安全**: Flask-Login会话管理

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 初始化数据库
```bash
flask db init
flask db migrate
flask db upgrade
```

### 运行开发服务器
```bash
python app.py
```

## 接入示例 (test-app)

test-app 是一个演示如何接入统一认证系统的示例应用。

1. 配置步骤:
```python
# 在test-app/app.py中配置认证系统URL
AUTH_SERVER = "http://localhost:5000"
APP_ID = "your_app_id"  # 从管理后台获取
```

2. 保护路由示例:
```python
@app.route('/protected')
def protected():
    token = request.args.get('token')
    if not verify_token(token):  # 验证token
        return redirect(f"{AUTH_SERVER}/auth/init?app_id={APP_ID}")
    return render_template('protected.html')
```

3. Token验证方法:
```python
def verify_token(token):
    if not token:
        return False
    response = requests.post(
        f"{AUTH_SERVER}/auth/verify",
        json={"token": token, "app_id": APP_ID}
    )
    return response.status_code == 200
```

完整示例代码请查看 `test-app/` 目录。

## 系统架构

```
flask-auth/
├── app.py                # 应用入口
├── extensions.py         # Flask扩展初始化
├── models.py             # 数据模型
├── requirements.txt      # 依赖列表
├── routes/               # 路由
│   ├── admin.py          # 管理后台路由
│   └── auth.py           # 认证路由
└── templates/            # 模板文件
    ├── admin/            # 管理后台模板
    └── auth/             # 认证页面模板
```

## 管理员账号

默认管理员账号:
- 用户名: `admin`
- 密码: `admin123` (首次登录后请修改)

## 部署说明

1. 生产环境建议:
   - 使用PostgreSQL/MySQL替代SQLite
   - 配置HTTPS加密
   - 设置强密码策略

2. 环境变量配置:
   ```
   export FLASK_SECRET_KEY=your-secret-key
   export FLASK_ENV=production
   ```
