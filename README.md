# Inventory Management System

A modern, full-featured Inventory Management System built with Flask and MySQL. This application provides role-based access control for owners and customers, enabling efficient product management, billing, and sales tracking.

## 🚀 Features

### Owner Features
- **Dashboard**: Centralized control panel for all operations
- **Product Management**: Add, view, and delete products with images
- **Inventory Tracking**: Monitor stock levels and product details
- **Sales History**: View comprehensive sales reports and analytics
- **Export Sales**: Download sales data as CSV files
- **Product Images**: Upload and manage product images

### Customer Features
- **Product Browsing**: View all available products
- **Billing System**: Generate bills for purchases
- **Real-time Stock**: See current inventory availability

### Shared Features
- **Secure Authentication**: Role-based login system
- **Responsive Design**: Modern, mobile-friendly UI
- **Image Management**: Product image uploads and display

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.7+**
- **MySQL 8.0+**
- **pip** (Python package manager)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/harshal5478/ims.git
cd ims  # Note: Repository name is 'ims' but project is 'Inventory Management System'
```

### 2. Install Python Dependencies
```bash
pip install flask mysql-connector-python werkzeug pandas scikit-learn numpy
```

Or create a `requirements.txt` file:
```
Flask==3.0.0
mysql-connector-python==8.2.0
Werkzeug==3.0.1
pandas==2.1.4
scikit-learn==1.3.2
numpy==1.26.2
```

Then install:
```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. Make sure MySQL is running on your system
2. Update database credentials in `app.py` (lines 25-30) if needed:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "your_password",
       "database": "inventory_db",
   }
   ```

3. Run the SQL script to create database and tables:
   ```bash
   mysql -u root -p < quary.sql
   ```
   
   Or manually execute the SQL commands from `quary.sql` in MySQL Workbench/command line.

### 4. Create Upload Directory
The application will automatically create the `static/uploads/` directory for product images.

## 🏃 Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. The application will redirect you to the login page.

## 🔐 Default Login Credentials

### Owner Account
- **Username**: `owner`
- **Password**: `owner123`
- **Access**: Full system access (add products, view sales, manage inventory)

### Customer Account
- **Username**: `customer`
- **Password**: `cust123`
- **Access**: View products and generate bills

⚠️ **Important**: Change these default credentials in production!

## 📁 Project Structure

```
aiml_inventory_app/
│
├── app.py                 # Main Flask application
├── quary.sql              # Database schema and initial data
├── task.py                # ML utilities (demand forecasting, exports)
├── README.md              # This file
│
├── static/
│   ├── style.css          # Global stylesheet
│   └── uploads/           # Product images storage
│
└── templates/
    ├── base.html          # Base template with navigation
    ├── login.html         # Login page
    ├── owner_dashboard.html    # Owner dashboard
    ├── customer_dashboard.html # Customer dashboard
    ├── add_product.html        # Add product form
    ├── index.html              # Product listing
    ├── billing.html            # Billing form
    ├── bill_generated.html     # Generated bill display
    ├── sales_history.html      # Sales reports
    └── inventory.html          # Inventory details
```

## 🔧 Configuration

### Environment Variables (Optional)
You can set these environment variables instead of hardcoding:
- `DB_HOST`: Database host (default: localhost)
- `DB_USER`: Database user (default: root)
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name (default: inventory_db)
- `FLASK_SECRET_KEY`: Flask secret key for sessions

### Database Configuration
Edit `DB_CONFIG` in `app.py` to match your MySQL setup.

## 📖 Usage Guide

### For Owners

1. **Login** with owner credentials
2. **Add Products**: 
   - Click "Add Product" from dashboard
   - Fill in product details (name, category, price, quantity)
   - Upload product image (optional)
   - Submit form
3. **View Products**: Click "View Products" to see all items
4. **Manage Inventory**: Check inventory levels and stock
5. **View Sales**: Access sales history and analytics
6. **Export Data**: Download sales data as CSV

### For Customers

1. **Login** with customer credentials
2. **Browse Products**: View all available products with prices
3. **Generate Bill**: 
   - Select a product
   - Enter quantity
   - Generate bill with automatic stock update

## 🧪 Additional Features

### ML/AI Features (task.py)
- **Sales Export**: Export sales data to CSV
- **Demand Forecasting**: Predict future demand using Linear Regression
- **Top Products**: Get recommendations for best-selling products

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL is running
   - Check credentials in `app.py`
   - Ensure database `inventory_db` exists

2. **Table Not Found**
   - Run `quary.sql` script again
   - Check if all tables are created

3. **Image Upload Issues**
   - Ensure `static/uploads/` directory exists
   - Check file permissions
   - Verify image file formats

4. **Port Already in Use**
   - Change port in `app.py`: `app.run(debug=True, port=5001)`

## 🔒 Security Notes

- Change default credentials before deploying
- Use environment variables for sensitive data
- Implement proper password hashing in production
- Enable HTTPS for production deployment
- Validate and sanitize all user inputs

## 🚀 Production Deployment

For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn, uWSGI)
3. Configure a reverse proxy (Nginx)
4. Use environment variables for secrets
5. Implement proper password hashing
6. Enable SSL/HTTPS

## 📝 License

This project is open source and available for educational purposes.

## 👤 Author

**Harshal**
- GitHub: [@harshal5478](https://github.com/harshal5478)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/harshal5478/ims/issues).

## 📧 Support

For support, open an issue on GitHub or contact the repository owner.

---

**Made by using Cursor**

