"""
CSRF Password Change Lab
Flag: FLAG{csrf_p4ssw0rd_ch4ng3}
"""
from flask import Flask, request, render_template_string, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

FLAG = os.environ.get('LAB_FLAG', 'FLAG{csrf_p4ssw0rd_ch4ng3}')

# Simulated users database
users = {
    'admin': {'password': 'admin123', 'email': 'admin@bank.com'},
    'victim': {'password': 'victim123', 'email': 'victim@bank.com'},
    'attacker': {'password': 'attacker123', 'email': 'attacker@evil.com'}
}

# Track password changes for the challenge
password_change_log = []

HTML_LOGIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>SecureBank - CSRF Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { max-width: 400px; width: 100%; padding: 20px; }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        }
        h1 { color: #0d6efd; text-align: center; margin-bottom: 10px; }
        .subtitle { color: #666; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus { border-color: #0d6efd; outline: none; }
        button {
            width: 100%;
            background: #0d6efd;
            color: white;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #0b5ed7; }
        .error { background: #ffe6e6; color: #dc3545; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .hint {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            color: white;
            font-size: 14px;
        }
        .accounts {
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .accounts h4 { margin-bottom: 10px; color: #0d6efd; }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h1>🏦 SecureBank</h1>
            <p class="subtitle">Online Banking Portal</p>
            
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            
            <div class="accounts">
                <h4>Test Accounts:</h4>
                <strong>Victim:</strong> victim / victim123<br>
                <strong>Attacker:</strong> attacker / attacker123
            </div>
            
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
        <div class="hint">
            <strong>💡 Lab Objective:</strong> Craft a CSRF attack to change the victim's password without their knowledge.
            <br><br>
            <strong>Scenario:</strong>
            <ol style="margin-top: 10px; margin-left: 20px;">
                <li>Login as 'victim' to see the password change form</li>
                <li>Notice there's no CSRF protection</li>
                <li>Use the /attacker-page to create a malicious page</li>
                <li>The victim bot visits your page every minute</li>
            </ol>
        </div>
    </div>
</body>
</html>
'''

HTML_DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - SecureBank</title>
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
        .logout { background: #dc3545; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; }
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            color: #333;
            margin-bottom: 20px;
        }
        .card h2 { color: #0d6efd; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            background: #0d6efd;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .warning {
            background: #fff3cd;
            border: 2px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .code-box {
            background: #1e1e1e;
            color: #4ec9b0;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            overflow-x: auto;
            margin-top: 15px;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .nav-tabs a {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }
        .nav-tabs a.active { background: #0d6efd; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 SecureBank Dashboard</h1>
            <a href="/logout" class="logout">Logout</a>
        </div>
        
        <div class="nav-tabs">
            <a href="/dashboard" class="active">Account</a>
            <a href="/attacker-page">Attacker Tools</a>
            <a href="/logs">Change Logs</a>
        </div>
        
        {% if success %}
        <div class="success">{{ success }}</div>
        {% endif %}
        
        <div class="card">
            <h2>Welcome, {{ username }}!</h2>
            <p>Account Balance: <strong>$10,000.00</strong></p>
        </div>
        
        <div class="card">
            <h2>🔐 Change Password</h2>
            
            <div class="warning">
                ⚠️ <strong>Vulnerability Notice:</strong> This form has no CSRF protection! 
                A malicious website could trick you into changing your password.
            </div>
            
            <!-- VULNERABLE: No CSRF token! -->
            <form method="POST" action="/change-password">
                <div class="form-group">
                    <label>New Password</label>
                    <input type="password" name="new_password" required>
                </div>
                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" name="confirm_password" required>
                </div>
                <button type="submit">Change Password</button>
            </form>
            
            <div class="code-box">
                <strong>Form HTML (for attackers):</strong><br><br>
                &lt;form method="POST" action="http://localhost:PORT/change-password"&gt;<br>
                &nbsp;&nbsp;&lt;input type="hidden" name="new_password" value="hacked123"&gt;<br>
                &nbsp;&nbsp;&lt;input type="hidden" name="confirm_password" value="hacked123"&gt;<br>
                &nbsp;&nbsp;&lt;input type="submit" value="Click for free money!"&gt;<br>
                &lt;/form&gt;
            </div>
        </div>
    </div>
</body>
</html>
'''

HTML_ATTACKER = '''
<!DOCTYPE html>
<html>
<head>
    <title>Attacker Tools - CSRF Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header { margin-bottom: 30px; }
        .header h1 { color: #dc3545; }
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            color: #333;
            margin-bottom: 20px;
        }
        .card h2 { color: #dc3545; margin-bottom: 20px; }
        textarea {
            width: 100%;
            height: 200px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
        }
        button {
            background: #dc3545;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
        }
        .preview {
            border: 2px dashed #ddd;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
            min-height: 100px;
        }
        .success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 20px;
            border-radius: 8px;
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
            margin-top: 15px;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .nav-tabs a {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }
        .nav-tabs a.active { background: #dc3545; }
        .instructions { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .instructions ol { margin-left: 20px; }
        .instructions li { margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>😈 Attacker Tools</h1>
        </div>
        
        <div class="nav-tabs">
            <a href="/dashboard">Account</a>
            <a href="/attacker-page" class="active">Attacker Tools</a>
            <a href="/logs">Change Logs</a>
        </div>
        
        {% if csrf_success %}
        <div class="card">
            <div class="success">
                🎉 CSRF Attack Successful! The victim's password was changed!
            </div>
            <div class="flag">🚩 {{ flag }}</div>
        </div>
        {% endif %}
        
        <div class="card">
            <h2>Create Malicious Page</h2>
            
            <div class="instructions">
                <strong>Instructions:</strong>
                <ol>
                    <li>Create a malicious HTML page with a hidden form</li>
                    <li>The form should auto-submit to /change-password</li>
                    <li>Host your page at /evil-page</li>
                    <li>The victim bot will visit your page</li>
                    <li>If successful, the victim's password will be changed!</li>
                </ol>
            </div>
            
            <form method="POST" action="/create-evil-page">
                <label><strong>Your Malicious HTML:</strong></label>
                <textarea name="html_content" placeholder="<html>
<body>
<h1>You won a prize! Click below!</h1>
<form id='csrf-form' method='POST' action='/change-password'>
    <input type='hidden' name='new_password' value='pwned123'>
    <input type='hidden' name='confirm_password' value='pwned123'>
</form>
<script>document.getElementById('csrf-form').submit();</script>
</body>
</html>">{{ evil_html if evil_html else "" }}</textarea>
                <button type="submit">Deploy Evil Page</button>
            </form>
            
            {% if evil_page_url %}
            <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px;">
                <strong>✅ Evil page deployed at:</strong> <a href="{{ evil_page_url }}" target="_blank">{{ evil_page_url }}</a>
                <br><br>
                <button onclick="simulateVictim()">🤖 Simulate Victim Visit</button>
            </div>
            {% endif %}
        </div>
    </div>
    
    <script>
        function simulateVictim() {
            fetch('/simulate-victim')
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
    </script>
</body>
</html>
'''

HTML_LOGS = '''
<!DOCTYPE html>
<html>
<head>
    <title>Password Change Logs</title>
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
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            color: #333;
        }
        .card h2 { color: #0d6efd; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .csrf-tag { background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .nav-tabs a {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }
        .nav-tabs a.active { background: #0d6efd; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-tabs">
            <a href="/dashboard">Account</a>
            <a href="/attacker-page">Attacker Tools</a>
            <a href="/logs" class="active">Change Logs</a>
        </div>
        
        <div class="card">
            <h2>📋 Password Change History</h2>
            <table>
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Time</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>{{ log.user }}</td>
                        <td>{{ log.time }}</td>
                        <td>
                            {% if log.csrf %}
                            <span class="csrf-tag">CSRF ATTACK!</span>
                            {% else %}
                            Normal
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="3" style="text-align: center; color: #666;">No password changes yet</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

# Store for evil page content
evil_page_content = None
csrf_attack_success = False

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template_string(HTML_LOGIN, error=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect('/dashboard')
    
    return render_template_string(HTML_LOGIN, error='Invalid credentials')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    
    success = request.args.get('success')
    return render_template_string(HTML_DASHBOARD, username=session['username'], success=success)

@app.route('/change-password', methods=['POST'])
def change_password():
    global csrf_attack_success
    
    # Get username from session or referer-based detection
    username = session.get('username')
    
    # For CSRF simulation: if no session but request came from evil page
    referer = request.headers.get('Referer', '')
    is_csrf = 'evil-page' in referer or 'username' not in session
    
    if not username:
        # Simulate victim session for CSRF demo
        username = 'victim'
    
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        return redirect('/dashboard?error=passwords_dont_match')
    
    # Change password
    if username in users:
        users[username]['password'] = new_password
        
        import datetime
        password_change_log.append({
            'user': username,
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'csrf': is_csrf
        })
        
        if is_csrf and username == 'victim':
            csrf_attack_success = True
    
    if 'username' in session:
        return redirect('/dashboard?success=Password changed successfully!')
    else:
        return "Password changed!", 200

@app.route('/attacker-page')
def attacker_page():
    if 'username' not in session:
        return redirect('/')
    
    return render_template_string(
        HTML_ATTACKER, 
        evil_page_url='/evil-page' if evil_page_content else None,
        evil_html=evil_page_content,
        csrf_success=csrf_attack_success,
        flag=FLAG
    )

@app.route('/create-evil-page', methods=['POST'])
def create_evil_page():
    global evil_page_content
    evil_page_content = request.form.get('html_content', '')
    return redirect('/attacker-page')

@app.route('/evil-page')
def evil_page():
    if evil_page_content:
        return evil_page_content
    return "No evil page created yet", 404

@app.route('/simulate-victim')
def simulate_victim():
    """Simulate victim visiting the evil page"""
    global csrf_attack_success
    
    if evil_page_content and 'change-password' in evil_page_content:
        # Simulate the CSRF attack
        import re
        # Extract password from hidden field
        match = re.search(r'name=["\']new_password["\'].*?value=["\']([^"\']+)["\']', evil_page_content)
        if match:
            new_password = match.group(1)
            users['victim']['password'] = new_password
            csrf_attack_success = True
            
            import datetime
            password_change_log.append({
                'user': 'victim',
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'csrf': True
            })
            
            return {'success': True, 'message': 'CSRF Attack successful! Victim password changed!'}
    
    return {'success': False, 'message': 'Attack failed. Check your malicious HTML.'}

@app.route('/logs')
def logs():
    if 'username' not in session:
        return redirect('/')
    return render_template_string(HTML_LOGS, logs=password_change_log)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/flag')
def get_flag():
    return {'flag': FLAG}

@app.route('/reset')
def reset():
    global csrf_attack_success, evil_page_content, password_change_log, users
    csrf_attack_success = False
    evil_page_content = None
    password_change_log = []
    users = {
        'admin': {'password': 'admin123', 'email': 'admin@bank.com'},
        'victim': {'password': 'victim123', 'email': 'victim@bank.com'},
        'attacker': {'password': 'attacker123', 'email': 'attacker@evil.com'}
    }
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
