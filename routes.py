from flask import Flask,session, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
import uuid
import requests


app = Flask(__name__)
app.secret_key = 'sincostan'

# Konfigurasi folder upload
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Fungsi koneksi ke database
def get_db_connection():
    conn = sqlite3.connect('Trendify.db')
    conn.row_factory = sqlite3.Row
    return conn

# Midtrans Keys
SERVER_KEY = "SB-Mid-server-cR69-qEA1FYdey-5kR2Zz5Gp"
CLIENT_KEY = "SB-Mid-client-UDCOjDw5ZzD_6smy"


# ================= HOME =================
@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC LIMIT 10').fetchall()
    conn.close()
    return render_template('home_page.html', products=products)

# ============== FORM UPLOAD =============
@app.route('/upload')
def upload_form():
    return render_template('upload_page.html')

# ============== SIMPAN PRODUK ============
@app.route('/add', methods=['POST'])
def add_product():
    title = request.form['title']
    artist = request.form['artist']
    description = request.form['description']
    price = request.form['price']

    image = request.files['image']
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
    else:
        filename = ""

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO products (title, artist, description, price, image_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, artist, description, price, filename))
    conn.commit()
    conn.close()

    return redirect('/dashboard/all')

# ============== ALL PRODUCTS ============
@app.route('/allproducts')
def all_products():
    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()

        all_products = [{
            'id': p['id'],
            'title': p['title'],
            'description': p['description'],
            'price': p['price'],
            'artist': p['artist'],
            'image_path': p['image_path']
        } for p in products]

        return render_template('all_products.html', all_products=all_products)
    except Exception as e:
        return f"Gagal load all products: {str(e)}"


@app.route('/api/products')
def get_products():
    conn = sqlite3.connect('Trendify.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        products.append({
            'id': row['id'],
            'title': row['title'],
            'artist': row['artist'],
            'price': row['price'],
            'description': row['description'],
            'image_path': row['image_path'],
        })

    return jsonify(products)

# # ============================ DETAIL PRODUK AND MIDTRANS ============================
# Midtrans API Key
SERVER_KEY = "SB-Mid-server-cR69-qEA1FYdey-5kR2Zz5Gp"
CLIENT_KEY = "SB-Mid-client-UDCOjDw5ZzD_6smy"

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    try:
        role = session.get('role', 'user')
        from_page = 'dashboard' if role == 'admin' else 'all'

        conn = sqlite3.connect('Trendify.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            return f"Produk ID {product_id} tidak ditemukan", 404

        cursor.execute("SELECT name, comment, created_at FROM comments WHERE product_id = ? ORDER BY created_at DESC", (product_id,))
        comments = cursor.fetchall()
        conn.close()

        return render_template('detail_page.html', product=product, comments=comments, from_page=from_page, client_key=CLIENT_KEY)

    except Exception as e:
        return f"Gagal mengambil detail produk: {str(e)}", 500
# ====================== PAYMENT PAGE ======================
@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        product_id = data.get('product_id')

        conn = sqlite3.connect('Trendify.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'Produk tidak ditemukan'}), 404

        order_id = f"ORDER-{str(uuid.uuid4())}"
        gross_amount = int(row['price'])

        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": gross_amount
            },
            "credit_card": {
                "secure": True
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        auth = (SERVER_KEY, '')

        response = requests.post(
            "https://app.sandbox.midtrans.com/snap/v1/transactions",
            json=payload,
            headers=headers,
            auth=auth
        )

        return jsonify(response.json())

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================ KOMENTAR ============================
@app.route('/product/<int:product_id>/comment', methods=['POST'])
def add_comment(product_id):
    try:
        name = request.form.get('name')
        comment = request.form.get('comment')

        if not name or not comment:
            return redirect(url_for('product_detail', product_id=product_id))

        conn = sqlite3.connect('Trendify.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO comments (product_id, name, comment, created_at) VALUES (?, ?, ?, datetime('now'))",
            (product_id, name, comment)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('product_detail', product_id=product_id))

    except Exception as e:
        return f"❌ Error saat tambah komentar: {str(e)}"
    
# ============================ EDIT PRODUK ============================
@app.route('/edit/<int:product_id>', methods=['GET'])
def edit_page(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if not product:
        return f"Produk dengan ID {product_id} tidak ditemukan", 404

    return render_template('edit_page.html', product=product)

# ============================ UPDATE PRODUK ============================
@app.route('/edit/<int:product_id>', methods=['POST'])
def update_product(product_id):
    title = request.form['title']
    artist = request.form['artist']
    description = request.form['description']
    price = request.form['price']

    image = request.files.get('image')
    conn = get_db_connection()

    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        conn.execute('''
            UPDATE products SET title = ?, artist = ?, description = ?, price = ?, image_path = ?
            WHERE id = ?
        ''', (title, artist, description, price, filename, product_id))
    else:
        conn.execute('''
            UPDATE products SET title = ?, artist = ?, description = ?, price = ?
            WHERE id = ?
        ''', (title, artist, description, price, product_id))

    conn.commit()
    conn.close()

    return redirect(url_for('product_detail', product_id=product_id))

# ============================ HAPUS PRODUK ============================
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    # Response untuk JavaScript
    return jsonify({'status': 'success'})

# ================= GUIDE PAGE =================
@app.route('/Guide')
def guide():
    return render_template('guide_page.html')


#=======================================================================================================================

# ================= HALAMAN LOGIN =================
@app.route('/login')
def login_page():
    return render_template('login_page.html')

# ================= API LOGIN =================
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email').lower()
    password = data.get('password')

    # Hardcoded admin login
    if email == 'info.sincostan@gmail.com' and password == 'sincostan':
        session['email'] = email
        session['role'] = 'admin'
        return jsonify({'status': 'success', 'role': 'admin'})

    # Hardcoded user login
    elif email == 'user@gmail.com' and password == 'user123':
        session['email'] = email
        session['role'] = 'user'
        return jsonify({'status': 'success', 'role': 'user'})

    # Jika tidak cocok
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect email or password'}) 


# ================= HALAMAN DASHBOARD ADMIN =================
@app.route('/dashboard')
def dashboard_admin():
    conn = sqlite3.connect('Trendify.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Hitung total produk
    cursor.execute("SELECT COUNT(*) AS total FROM products")
    total_products = cursor.fetchone()['total']

    # Hitung total user (role-nya 'user' saja, bukan admin)
    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()['total']

    conn.close()

    return render_template('dashboard.html', total_products=total_products, total_users=total_users)


# ================= HALAMAN SEMUA PRODUK ADMIN =================
@app.route('/dashboard/all')
def dashboard_all():
    return render_template('dashboard_all.html')

# ================= API GET ALL PRODUCTS =================
@app.route('/api/products')
def get_all_products_api():
    conn = sqlite3.connect('Trendify.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    products = [{
        'id': row['id'],
        'title': row['title'],
        'artist': row['artist'],
        'price': row['price'],
        'description': row['description'],
        'image_path': row['image_path'],
    } for row in rows]

    return jsonify(products)

# ================= LOGOUT ADMIN =================
@app.route('/logout')
def logout():
    role = session.get('role')  # cek sebelum session dihapus
    session.clear()

    if role == 'admin':
        return redirect(url_for('login_page'))  # misal /login untuk admin
    else:
        return redirect(url_for('index'))  # ke home_page.html


# ================= DASHBOARD COMMENT ADMIN =================
@app.route('/dashboard/comment')
def dashboard_comment():
    conn = sqlite3.connect('Trendify.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT comments.id, comments.name, comments.comment, comments.created_at, products.title
        FROM comments
        JOIN products ON comments.product_id = products.id
        ORDER BY comments.created_at DESC
    ''')
    comments = cursor.fetchall()
    conn.close()

    return render_template('dashboard_comment.html', comments=comments)

# ================= DELETE COMMENT =================
@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    conn = sqlite3.connect('Trendify.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard_comment'))