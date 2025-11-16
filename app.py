from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    Response,
)
import mysql.connector
import os
from werkzeug.utils import secure_filename
from functools import wraps
from uuid import uuid4
import csv
import io


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "h@rsh5478"),
    "database": os.environ.get("DB_NAME", "inventory_db"),
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def fetch_one(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def execute(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()


def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("You are not authorized to access that page.", "danger")
                return redirect(url_for("home"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def save_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    filename = f"{uuid4().hex}_{secure_filename(file_storage.filename)}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return filename


def delete_image(filename):
    if not filename:
        return
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = fetch_one("SELECT * FROM users WHERE username = %s", (username,))

        if not user:
            flash("Username not found.", "danger")
            return redirect(url_for("login"))

        if password != user["password"]:
            flash("Password is incorrect.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user["user_id"]
        session["role"] = user["role"]
        flash("Welcome back!", "success")

        return redirect(
            url_for("owner_dashboard" if user["role"] == "owner" else "customer_dashboard")
        )

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/")
@login_required()
def home():
    products = fetch_all("SELECT * FROM products ORDER BY product_id DESC")
    return render_template("index.html", products=products)


@app.route("/owner")
@login_required("owner")
def owner_dashboard():
    return render_template("owner_dashboard.html")


@app.route("/customer")
@login_required("customer")
def customer_dashboard():
    return render_template("customer_dashboard.html")


@app.route("/add-product", methods=["GET", "POST"])
@login_required("owner")
def add_product():
    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form["price"]
        quantity = request.form["quantity"]

        image_name = save_image(request.files.get("image"))

        execute(
            """
            INSERT INTO products (name, category, description, price, quantity, image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (name, category, description, price, quantity, image_name),
        )

        flash("Product added successfully.", "success")
        return redirect(url_for("home"))

    return render_template("add_product.html")


@app.route("/delete-product/<int:product_id>", methods=["POST"])
@login_required("owner")
def delete_product(product_id):
    product = fetch_one("SELECT image FROM products WHERE product_id = %s", (product_id,))
    execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    if product and product.get("image"):
        delete_image(product["image"])
    flash("Product removed.", "info")
    return redirect(url_for("home"))


@app.route("/inventory")
@login_required("owner")
def inventory():
    items = fetch_all("SELECT * FROM products ORDER BY name ASC")
    return render_template("inventory.html", inventory=items)


@app.route("/billing", methods=["GET", "POST"])
@login_required("customer")
def billing():
    products = fetch_all("SELECT * FROM products ORDER BY name ASC")

    if request.method == "POST":
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])

        product = fetch_one("SELECT * FROM products WHERE product_id = %s", (product_id,))

        if not product:
            flash("Product not found.", "danger")
            return redirect(url_for("billing"))

        if quantity <= 0:
            flash("Quantity must be at least 1.", "warning")
            return redirect(url_for("billing"))

        if quantity > product["quantity"]:
            flash(f"Only {product['quantity']} items available.", "warning")
            return redirect(url_for("billing"))

        total = float(product["price"]) * quantity

        execute(
            "UPDATE products SET quantity = quantity - %s WHERE product_id = %s",
            (quantity, product_id),
        )
        execute(
            "INSERT INTO sales (product_id, quantity_sold, total_price) VALUES (%s, %s, %s)",
            (product_id, quantity, total),
        )

        product["quantity"] -= quantity

        return render_template("bill_generated.html", product=product, qty=quantity, total=total)

    return render_template("billing.html", products=products)


@app.route("/sales-history")
@login_required("owner")
def sales_history():
    sales = fetch_all(
        """
        SELECT s.sale_id, p.name AS product_name, s.quantity_sold, s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        ORDER BY s.sale_date DESC
    """
    )
    return render_template("sales_history.html", sales=sales)


@app.route("/export-sales")
@login_required("owner")
def export_sales():
    sales = fetch_all(
        """
        SELECT s.sale_id, p.name AS product_name, s.quantity_sold, s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        ORDER BY s.sale_date DESC
    """
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sale ID", "Product", "Quantity", "Total Price", "Sale Date"])
    for sale in sales:
        writer.writerow(
            [
                sale["sale_id"],
                sale["product_name"],
                sale["quantity_sold"],
                sale["total_price"],
                sale["sale_date"],
            ]
        )

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sales_history.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
