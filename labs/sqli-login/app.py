"""
SQL Injection Login Bypass Lab
Flag: FLAG{sql1_l0g1n_byp4ss}
"""
from flask import Flask, request, render_template_string, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

FLAG = os.environ.get('LAB_FLAG', 'FLAG{sql1_l0g1n_byp4ss}')

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

HTML_LOGIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Portal - SQL Injection Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
        }
        .container { width: 100%; max-width: 450px; padding: 20px; }
        .login-box {
            background: #fff;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        }
        .login-box h1 { 
            color: #333; 
            text-align: center; 
            margin-bottom: 10px;
            font-size: 28px;
        }
        .login-box .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            color: #333;
            font-weight: 500;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus { border-color: #0d6efd; outline: none; }
        button {
            width: 100%;
            background: linear-gradient(135deg, #0d6efd, #0b5ed7);
            color: #fff;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        .error {
            background: #ffe6e6;
            border: 1px solid #dc3545;
            color: #dc3545;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .hint {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
        }
        .hint code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
        }
        .debug {
            background: #1e1e1e;
            color: #4ec9b0;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h1>🔐 Admin Portal</h1>
            <p class="subtitle">Secure Authentication System v2.1</p>
            
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            
            {% if query %}
            <div class="debug">
                <strong>DEBUG (SQL Query):</strong><br>
                {{ query }}
            </div>
            {% endif %}
        </div>
        
        <div class="hint">
            <strong>💡 Lab Objective:</strong> Bypass the login to access the admin account.
            <br><br>
            <strong>Hints:</strong>
            <ul style="margin-top: 10px; margin-left: 20px;">
                <li>The login query is vulnerable to SQL injection</li>
                <li>Try using <code>' OR '1'='1</code></li>
                <li>Comments in SQL: <code>--</code> or <code>#</code></li>
                <li>Admin username is: <code>admin</code></li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

HTML_DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - SQL Injection Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .header h1 { color: #0d6efd; }
        .logout-btn {
            background: #dc3545;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
        }
        .card {
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            color: #333;
            margin-bottom: 20px;
        }
        .card h2 { color: #0d6efd; margin-bottom: 20px; }
        .success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 18px;
        }
        .flag {
            background: #1e1e1e;
            color: #4ec9b0;
            padding: 20px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 20px;
            text-align: center;
            margin-top: 20px;
            letter-spacing: 2px;
        }
        .user-info {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 10px;
        }
        .user-info dt { font-weight: bold; color: #666; }
        .user-info dd { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Admin Dashboard</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <div class="card">
            <h2>Welcome, {{ user.username }}!</h2>
            <div class="success">
                ✅ You have successfully bypassed the authentication!
            </div>
            
            <div class="flag">
                🚩 {{ user.secret_note }}
            </div>
        </div>
        
        <div class="card">
            <h2>User Information</h2>
            <dl class="user-info">
                <dt>User ID:</dt>
                <dd>{{ user.id }}</dd>
                <dt>Username:</dt>
                <dd>{{ user.username }}</dd>
                <dt>Role:</dt>
                <dd>{{ user.role }}</dd>
            </dl>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template_string(HTML_LOGIN, error=None, query=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # VULNERABLE: SQL Injection in login query
    # Direct string concatenation allows injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            return render_template_string(HTML_LOGIN, error='Invalid credentials!', query=query)
    except Exception as e:
        return render_template_string(HTML_LOGIN, error=f'Database error: {str(e)}', query=query)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return redirect('/logout')
    
    return render_template_string(HTML_DASHBOARD, user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/flag')
def get_flag():
    return {'flag': FLAG}

if __name__ == '__main__':
    # Ensure database exists
    if not os.path.exists('users.db'):
        from init_db import init_db
        init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
