import pandas as pd
import mysql.connector
from sklearn.linear_model import LinearRegression
import numpy as np
import csv

# Connect to MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # 🔁 Replace with your actual username
        password="h@rsh5478",  # 🔁 Replace with your actual password
        database="inventory_db"
    )

# 1️⃣ Export sales data to CSV
def export_sales_to_csv(file_path='sales_data.csv'):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT product_id, quantity, total_price, sale_time FROM sales")
    rows = cursor.fetchall()

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Product ID', 'Quantity', 'Total Price', 'Sale Time'])
        writer.writerows(rows)

    db.close()
    print(f"✅ Sales data exported to {file_path}")

# 2️⃣ Demand forecasting (Linear Regression)
def forecast_demand(product_id, future_days=7):
    db = connect_db()
    query = """
    SELECT DAY(sale_time), quantity FROM sales
    WHERE product_id = %s
    ORDER BY sale_time ASC
    """
    df = pd.read_sql(query, db, params=(product_id,))
    db.close()

    if df.empty:
        return "❌ No sales data available for this product."

    X = df.iloc[:, 0].values.reshape(-1, 1)  # Days
    y = df['quantity'].values  # Quantities

    model = LinearRegression()
    model.fit(X, y)

    future_days_array = np.array(range(1, future_days + 1)).reshape(-1, 1)
    predictions = model.predict(future_days_array)

    forecast = list(zip(range(1, future_days + 1), predictions.round(2)))
    return forecast

# 3️⃣ Recommend top selling products
def recommend_top_products(limit=5):
    db = connect_db()
    cursor = db.cursor()
    query = """
    SELECT p.name, SUM(s.quantity) as total_sold
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY s.product_id
    ORDER BY total_sold DESC
    LIMIT %s
    """
    cursor.execute(query, (limit,))
    recommendations = cursor.fetchall()
    db.close()
    return recommendations
