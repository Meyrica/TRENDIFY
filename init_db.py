import sqlite3

# Koneksi ke SQLite
conn = sqlite3.connect('Trendify.db')
cursor = conn.cursor()


cursor.execute('DROP TABLE IF EXISTS users')

# TABEL PRODUCTS
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    price REAL,
    artist TEXT,
    image_path TEXT
)
''')

# TABEL COMMENTS
cursor.execute('''
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    comment TEXT,
    name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

# TABEL USERS
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                                                                                  
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# ✅ Cek apakah admin sudah ada
cursor.execute("SELECT * FROM users WHERE email = ?", ('info.sincostan@gmail.com',))
admin_exists = cursor.fetchone()

if not admin_exists:
    cursor.execute('''
    INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)
    ''', ('Admin Trendify', 'info.sincostan@gmail.com', 'sincostan', 'admin'))
    print("✅ Admin berhasil ditambahkan!")
else:
    print("ℹ️  Admin sudah ada, tidak ditambahkan lagi.")

# Simpan dan tutup koneksi
conn.commit()
conn.close()

print("✅ Database dan semua tabel berhasil dibuat!")
