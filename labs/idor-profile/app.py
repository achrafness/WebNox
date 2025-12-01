"""
IDOR Profile Access Lab
Flag: FLAG{1d0r_pr0f1l3_4cc3ss}
"""
from flask import Flask, request, render_template_string, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

FLAG = os.environ.get('LAB_FLAG', 'FLAG{1d0r_pr0f1l3_4cc3ss}')

# Simulated user database
USERS = {
    1: {
        'id': 1,
        'username': 'admin',
        'email': 'admin@company.com',
        'role': 'Administrator',
        'private_notes': f'🚩 Secret Admin Flag: {FLAG}',
        'salary': '$150,000',
        'ssn': '***-**-1234'
    },
    2: {
        'id': 2,
        'username': 'john_doe',
        'email': 'john@company.com',
        'role': 'Developer',
        'private_notes': 'Working on the new feature',
        'salary': '$85,000',
        'ssn': '***-**-5678'
    },
    3: {
        'id': 3,
        'username': 'jane_smith',
        'email': 'jane@company.com',
        'role': 'Designer',
        'private_notes': 'Design review scheduled for Friday',
        'salary': '$75,000',
        'ssn': '***-**-9012'
    },
    100: {
        'id': 100,
        'username': 'guest',
        'email': 'guest@company.com',
        'role': 'Guest',
        'private_notes': 'This is your test account. Try accessing other profiles!',
        'salary': 'N/A',
        'ssn': 'N/A'
    }
}

HTML_LOGIN = '''
<!DOCTYPE html>
<html>
<head>
    <title>Employee Portal - IDOR Lab</title>
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
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
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
        .hint {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            color: white;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h1>👤 Employee Portal</h1>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Select Account:</label>
                    <select name="user_id">
                        <option value="100">Guest Account (ID: 100)</option>
                        <option value="2">John Doe (ID: 2)</option>
                        <option value="3">Jane Smith (ID: 3)</option>
                    </select>
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
        <div class="hint">
            <strong>💡 Lab Objective:</strong> Access the admin's private profile (ID: 1) to find the flag.
            <br><br>
            <strong>Hint:</strong> After logging in, check the URL structure. Can you manipulate the profile ID?
        </div>
    </div>
</body>
</html>
'''

HTML_PROFILE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Profile - {{ user.username }}</title>
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
        .nav-links a {
            color: white;
            text-decoration: none;
            margin-left: 20px;
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.2); }
        .nav-links a.logout { background: #dc3545; }
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
            color: #333;
            margin-bottom: 20px;
        }
        .card h2 { color: #0d6efd; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .profile-grid {
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 15px;
        }
        .profile-grid dt { font-weight: bold; color: #666; }
        .profile-grid dd { color: #333; }
        .private-section {
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .private-section h3 { color: #856404; margin-bottom: 10px; }
        .flag {
            background: #1e1e1e;
            color: #4ec9b0;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 16px;
            margin-top: 10px;
        }
        .url-hint {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 14px;
        }
        .warning {
            background: #dc3545;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👤 Employee Profile</h1>
            <div class="nav-links">
                <a href="/profile?id={{ session_user_id }}">My Profile</a>
                <a href="/logout" class="logout">Logout</a>
            </div>
        </div>
        
        {% if user.id != session_user_id %}
        <div class="warning">
            ⚠️ <strong>IDOR Vulnerability!</strong> You are viewing someone else's profile! 
            (Your ID: {{ session_user_id }}, Viewing ID: {{ user.id }})
        </div>
        {% endif %}
        
        <div class="card">
            <h2>Profile Information</h2>
            <dl class="profile-grid">
                <dt>User ID:</dt>
                <dd>{{ user.id }}</dd>
                <dt>Username:</dt>
                <dd>{{ user.username }}</dd>
                <dt>Email:</dt>
                <dd>{{ user.email }}</dd>
                <dt>Role:</dt>
                <dd>{{ user.role }}</dd>
                <dt>Salary:</dt>
                <dd>{{ user.salary }}</dd>
                <dt>SSN:</dt>
                <dd>{{ user.ssn }}</dd>
            </dl>
            
            <div class="private-section">
                <h3>🔒 Private Notes</h3>
                <div class="flag">{{ user.private_notes }}</div>
            </div>
        </div>
        
        <div class="url-hint">
            <strong>Current URL:</strong> /profile?id={{ user.id }}
            <br><br>
            💡 <em>Try changing the ID parameter to access other profiles...</em>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(f'/profile?id={session["user_id"]}')
    return render_template_string(HTML_LOGIN)

@app.route('/login', methods=['POST'])
def login():
    user_id = int(request.form.get('user_id', 100))
    if user_id in USERS:
        session['user_id'] = user_id
        return redirect(f'/profile?id={user_id}')
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/')
    
    # VULNERABLE: No authorization check!
    # The application only checks if user is logged in, not if they own the profile
    profile_id = request.args.get('id', session['user_id'])
    
    try:
        profile_id = int(profile_id)
    except ValueError:
        profile_id = session['user_id']
    
    user = USERS.get(profile_id)
    if not user:
        return "User not found", 404
    
    return render_template_string(
        HTML_PROFILE, 
        user=user, 
        session_user_id=session['user_id']
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/flag')
def get_flag():
    return {'flag': FLAG}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
