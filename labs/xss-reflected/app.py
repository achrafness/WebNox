"""
XSS Reflected Lab - Vulnerable Search Application
Flag: FLAG{xss_r3fl3ct3d_b4s1c}
"""
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# The secret flag
FLAG = os.environ.get('LAB_FLAG', 'FLAG{xss_r3fl3ct3d_b4s1c}')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Product Search - XSS Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
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
        }
        .results h3 { margin-bottom: 15px; color: #333; }
        .product {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .alert {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .hint {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
        }
        /* Hidden flag element */
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
                    <strong>{{ product.name }}</strong> - ${{ product.price }}
                </div>
                {% endfor %}
            {% else %}
                <p>No products found matching your search.</p>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="hint">
            <strong>💡 Lab Objective:</strong> Find and exploit the XSS vulnerability to discover the hidden flag.
            <br><br>
            <strong>Hint:</strong> The search results reflect your input. Can you inject JavaScript?
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
]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, query='', products=None, flag=FLAG)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # Vulnerable: No sanitization of user input
    # The query is reflected directly in the page
    
    if query:
        # Simple search (case-insensitive)
        results = [p for p in PRODUCTS if query.lower() in p['name'].lower()]
    else:
        results = []
    
    return render_template_string(HTML_TEMPLATE, query=query, products=results, flag=FLAG)

@app.route('/flag')
def get_flag():
    """API endpoint to verify flag capture"""
    return {'flag': FLAG}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
