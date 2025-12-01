"""
XSS Stored Lab - Vulnerable Comment System
Flag: FLAG{st0r3d_xss_p3rs1st3nt}
"""
from flask import Flask, request, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# The secret flag (stored in admin's session/cookie simulation)
FLAG = os.environ.get('LAB_FLAG', 'FLAG{st0r3d_xss_p3rs1st3nt}')

# In-memory storage for comments
comments = [
    {'author': 'Admin', 'content': 'Welcome to our blog! Feel free to leave comments.'},
    {'author': 'User123', 'content': 'Great article, thanks for sharing!'},
]

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
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        h1 { text-align: center; margin-bottom: 10px; color: #0d6efd; }
        .subtitle { text-align: center; color: #aaa; margin-bottom: 30px; }
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
        .comment .author { font-weight: bold; color: #0d6efd; margin-bottom: 5px; }
        .comment .content { color: #333; }
        .comment-form { margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; }
        .comment-form h4 { margin-bottom: 15px; }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        input:focus, textarea:focus { border-color: #0d6efd; outline: none; }
        button {
            background: #0d6efd;
            color: #fff;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { background: #0b5ed7; }
        .hint {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
        }
        .admin-info {
            background: #dc3545;
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
    <script>
        // Simulated admin session with flag in cookie
        document.cookie = "admin_session={{ flag }}; path=/";
    </script>
</head>
<body>
    <div class="container">
        <h1>📝 Tech Blog</h1>
        <p class="subtitle">Latest in Technology & Security</p>
        
        <div class="admin-info">
            🔐 <strong>Admin Note:</strong> The admin bot visits this page every minute to check comments. 
            The admin's session contains sensitive information...
        </div>
        
        <div class="blog-post">
            <h2>Understanding Web Security</h2>
            <p>Web security is crucial in today's connected world. Applications must protect against various attacks including XSS, SQL Injection, and CSRF.</p>
            <p>Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users. There are three main types: Reflected, Stored, and DOM-based XSS.</p>
            <p>Always sanitize user input and encode output to prevent these attacks!</p>
        </div>
        
        <div class="comments-section">
            <h3>💬 Comments ({{ comments|length }})</h3>
            
            {% for comment in comments %}
            <div class="comment">
                <div class="author">{{ comment.author }}</div>
                <div class="content">{{ comment.content | safe }}</div>
            </div>
            {% endfor %}
            
            <div class="comment-form">
                <h4>Leave a Comment</h4>
                <form method="POST" action="/comment">
                    <input type="text" name="author" placeholder="Your name" required>
                    <textarea name="content" rows="4" placeholder="Your comment..." required></textarea>
                    <button type="submit">Post Comment</button>
                </form>
            </div>
        </div>
        
        <div class="hint">
            <strong>💡 Lab Objective:</strong> Inject a stored XSS payload that steals the admin's session cookie.
            <br><br>
            <strong>Hints:</strong>
            <ul style="margin-top: 10px; margin-left: 20px;">
                <li>Comments are stored and displayed to all users</li>
                <li>The admin bot visits this page regularly</li>
                <li>The flag is stored in document.cookie</li>
                <li>Try: &lt;script&gt;alert(document.cookie)&lt;/script&gt;</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, comments=comments, flag=FLAG)

@app.route('/comment', methods=['POST'])
def add_comment():
    author = request.form.get('author', 'Anonymous')
    content = request.form.get('content', '')
    
    # Vulnerable: No sanitization of comment content
    # XSS payload will be stored and executed for all visitors
    if author and content:
        comments.append({'author': author, 'content': content})
    
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    """Reset comments to default"""
    global comments
    comments = [
        {'author': 'Admin', 'content': 'Welcome to our blog! Feel free to leave comments.'},
        {'author': 'User123', 'content': 'Great article, thanks for sharing!'},
    ]
    return redirect(url_for('index'))

@app.route('/flag')
def get_flag():
    """API endpoint to verify flag capture"""
    return {'flag': FLAG}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
