from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from werkzeug.utils import secure_filename

# ✅ Initialize Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Configure Upload Folder
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # create folder if not exists


# ✅ Initialize App
app = Flask(__name__)
app.secret_key = "supersecretkey"   # session key

# ✅ MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="h@rsh5478",
    database="inventory_db"
)
cursor = db.cursor(dictionary=True)

# 🟢 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()  # remove spaces
        password = request.form['password'].strip()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        print("DEBUG → Username entered:", username)
        print("DEBUG → User fetched from DB:", user)

        if not user:
            return "❌ Username not found in DB"

        if password == user['password']:
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            return redirect(url_for('owner_dashboard' if user['role'] == 'owner' else 'customer_dashboard'))
        else:
            return "❌ Password is wrong"

    return render_template('login.html')



# 🟢 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 🟢 Owner Dashboard
@app.route('/owner')
def owner_dashboard():
    if 'role' not in session or session['role'] != 'owner':
        return redirect(url_for('login'))
    return render_template('owner_dashboard.html')

# 🟢 Customer Dashboard
@app.route('/customer')
def customer_dashboard():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    return render_template('customer_dashboard.html')

# 🟢 View Products (both roles)
@app.route('/')
def home():
    if 'user_id' not in session:   # if user not logged in
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('index.html', products=products)

# 🟢 Add Product (Owner only)
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if 'role' not in session or session['role'] != 'owner':
        return "❌ Access denied"

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']

        # ✅ Handle image upload safely
        image_name = None
        if 'image' in request.files:  # check if file field exists
            image_file = request.files['image']
            if image_file and image_file.filename != '':
                image_name = secure_filename(image_file.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
                image_file.save(save_path)

        # ✅ Insert into database
        cursor.execute(
            "INSERT INTO products (name, category, description, price, quantity, image) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, category, description, price, quantity, image_name)
        )
        db.commit()

        return redirect(url_for('owner_dashboard'))

    return render_template('add_product.html')


@app.route('/delete-product/<int:product_id>')
def delete_product(product_id):
    if 'role' not in session or session['role'] != 'owner':
        return "❌ Access denied"

    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    db.commit()
    return redirect(url_for('home'))


# 🟢 Billing (Customer)
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    if request.method == 'POST':
        pid = request.form['product_id']
        qty = int(request.form['quantity'])

        cursor.execute("SELECT * FROM products WHERE product_id = %s", (pid,))
        product = cursor.fetchone()

        if not product:
            return "❌ Product not found"
        if qty > product['quantity']:
            return f"❌ Only {product['quantity']} available"

        total = float(product['price']) * qty

        # Update stock
        cursor.execute("UPDATE products SET quantity = quantity - %s WHERE product_id=%s", (qty, pid))

        # Record sale
        cursor.execute("INSERT INTO sales (product_id, quantity_sold, total_price) VALUES (%s, %s, %s)",
                       (pid, qty, total))
        db.commit()

        return render_template('bill_generated.html', product=product, qty=qty, total=total)

    # GET request → show billing form
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('billing.html', products=products)
     
# 🟢 Owner: View Sales History
@app.route('/sales-history')
def sales_history():
    if 'role' not in session or session['role'] != 'owner':
        return redirect(url_for('login'))

    cursor.execute("""
        SELECT s.sale_id, p.name AS product_name, s.quantity_sold, s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        ORDER BY s.sale_date DESC
    """)
    sales = cursor.fetchall()
    return render_template('sales_history.html', sales=sales)

if __name__ == '__main__':
    app.run(debug=True)
