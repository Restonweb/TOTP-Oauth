from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'testappsecret123'

# 配置统一认证系统信息
AUTH_SERVER = 'http://localhost:5000' # 请替换为实际的统一认证系统地址
APP_ID = 'RX48E'  # 请替换为从统一认证系统后台获取的实际App ID

@app.route('/')
def home():
    # 检查是否已认证
    if 'authenticated' in session and 'token' in session:
        # 验证token是否有效
        import requests
        verify_url = f"{AUTH_SERVER}/auth/verify"
        response = requests.post(verify_url, json={
            'app_id': 'test-app',
            'token': session['token']
        })
        
        if response.json().get('valid'):
            return render_template('protected.html')
        
    # 无效或过期的session
    session.clear()
    return render_template('index.html')

@app.route('/protected')
def protected():
    if 'authenticated' in session and 'token' in session:
        # 验证token是否有效
        response = requests.post(
            f'{AUTH_SERVER}/auth/verify',
            json={
                'app_id': APP_ID,
                'token': session['token']
            }
        )
        
        if response.status_code == 200 and response.json().get('valid'):
            return render_template('protected.html')
    
    # 无效或过期的session
    session.clear()
    return redirect(f'{AUTH_SERVER}/auth/auth/{APP_ID}')

@app.route('/auth-callback')
def auth_callback():
    # 从统一认证系统获取token
    token = request.args.get('token')
    
    if not token:
        return redirect(url_for('home'))
    
    # 验证token
    response = requests.post(
        f'{AUTH_SERVER}/auth/verify',
        json={
            'app_id': APP_ID,
            'token': token
        }
    )
    
    if response.status_code == 200 and response.json().get('valid'):
        session['authenticated'] = True
        session['token'] = token
        return redirect(url_for('protected'))
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
