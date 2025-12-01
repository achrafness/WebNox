"""
XSS Reflected Lab - Vulnerable Search Application
Flag: FLAG{xss_r3fl3ct3d_b4s1c}

This is a simpler XSS lab where you need to find the flag hidden in the page.
The search query is reflected without sanitization.
"""
from flask import Flask, request, render_template_string, jsonify
import os

app = Flask(__name__)

# The secret flag
FLAG = os.environ.get('LAB_FLAG', 'FLAG{xss_r3fl3ct3d_b4s1c}')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Product Search - XSS Reflected Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1 { text-align: center; margin-bottom: 30px; color: #0d6efd; }
        
        .search-box {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .search-box h2 { color: #333; margin-bottom: 20px; }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
        }
        input[type="text"]:focus { border-color: #0d6efd; outline: none; }
        button {
            background: #0d6efd;
            color: #fff;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover { background: #0b5ed7; }
        
        .results {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            color: #333;
            margin-bottom: 20px;
        }
        .results h3 { margin-bottom: 15px; color: #333; }
        .product {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .product .price { color: #198754; font-weight: bold; }
        
        .hint-box {
            background: rgba(13, 110, 253, 0.1);
            border: 1px solid rgba(13, 110, 253, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .hint-box h4 { color: #0d6efd; margin-bottom: 10px; }
        .hint-box ul { margin-left: 20px; margin-top: 10px; }
        .hint-box li { margin-bottom: 8px; }
        .hint-box code { 
            background: rgba(0,0,0,0.2); 
            padding: 2px 6px; 
            border-radius: 4px;
            font-size: 13px;
        }
        
        .examples {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .examples h5 { color: #ffc107; margin-bottom: 10px; }
        .examples code {
            display: block;
            background: rgba(0,0,0,0.2);
            padding: 8px;
            border-radius: 4px;
            margin-top: 5px;
            word-break: break-all;
        }
        
        /* Hidden flag element for the challenge */
        #secret-flag { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Product Search</h1>
        
        <div class="search-box">
            <h2>Search Products</h2>
            <form method="GET" action="/search">
                <input type="text" name="q" placeholder="Search for products..." value="{{ query }}">
                <button type="submit">Search</button>
            </form>
        </div>
        
        {% if query %}
        <div class="results">
            <h3>Search results for: {{ query | safe }}</h3>
            {% if products %}
                {% for product in products %}
                <div class="product">
                    <span><strong>{{ product.name }}</strong></span>
                    <span class="price">${{ product.price }}</span>
                </div>
                {% endfor %}
            {% else %}
                <p>No products found matching "<em>{{ query | safe }}</em>"</p>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="hint-box">
            <h4>🎯 Lab Objective</h4>
            <p>Find and exploit the reflected XSS vulnerability to discover the hidden flag on this page.</p>
            
            <ul>
                <li>Your search query is <strong>reflected without sanitization</strong></li>
                <li>The flag is hidden somewhere in the page's HTML</li>
                <li>Use JavaScript to extract the hidden flag</li>
                <li>Check hidden elements, data attributes, or the DOM</li>
            </ul>
            
            <div class="examples">
                <h5>💡 Example Payloads to Try:</h5>
                <code>&lt;script&gt;alert(1)&lt;/script&gt;</code>
                <code>&lt;script&gt;alert(document.getElementById('secret-flag').innerHTML)&lt;/script&gt;</code>
                <code>&lt;img src=x onerror="alert(document.body.innerHTML)"&gt;</code>
            </div>
        </div>
        
        <!-- Hidden flag for XSS challenge -->
        <div id="secret-flag" data-flag="{{ flag }}">{{ flag }}</div>
    </div>
</body>
</html>
'''

PRODUCTS = [
    {'name': 'Laptop Pro 15', 'price': '999.99'},
    {'name': 'Wireless Mouse', 'price': '29.99'},
    {'name': 'Mechanical Keyboard', 'price': '149.99'},
    {'name': 'USB-C Hub', 'price': '49.99'},
    {'name': '4K Monitor', 'price': '399.99'},
    {'name': 'Webcam HD', 'price': '79.99'},
    {'name': 'Headphones Pro', 'price': '199.99'},
]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, query='', products=None, flag=FLAG)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # VULNERABLE: No sanitization of user input
    # The query is reflected directly in the page using | safe filter
    
    if query:
        # Simple search (case-insensitive)
        results = [p for p in PRODUCTS if query.lower() in p['name'].lower()]
    else:
        results = []
    
    return render_template_string(HTML_TEMPLATE, query=query, products=results, flag=FLAG)


@app.route('/flag')
def get_flag():
    """API endpoint to verify flag capture"""
    return jsonify({'flag': FLAG})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
