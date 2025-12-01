"""
Initialize the SQLite database for SQL Injection lab
"""
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            secret_note TEXT
        )
    ''')
    
    # Insert sample users
    users = [
        ('admin', 'super_secret_admin_password_2024!', 'admin', 'FLAG{sql1_l0g1n_byp4ss}'),
        ('john', 'john123', 'user', 'Nothing special here'),
        ('alice', 'alice456', 'user', 'Just a regular user'),
        ('bob', 'bob789', 'user', 'No secrets to see'),
    ]
    
    for user in users:
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role, secret_note) VALUES (?, ?, ?, ?)',
                user
            )
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
