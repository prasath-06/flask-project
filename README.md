# Flask Warehouse Management System

This is a Flask-based web application for managing products, locations, and product movements in a warehouse. The application allows users to add products, assign locations, move products between locations, and generate reports.

---

## Features

- **Add Products**: Add new products with unique IDs, names, and quantities.
- **Assign Locations**: Assign products to specific locations in the warehouse.
- **Move Products**: Move products between locations while tracking quantities.
- **View Locations**: View all products and their assigned locations.
- **Edit Locations**: Update the location of a product.
- **View Navigation**: Track product movements between locations.
- **Reports**: Generate reports based on product locations.

---

## Prerequisites

- Python 3.x
- PostgreSQL
- Flask
- Flask-SQLAlchemy

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prasath-06/flask-project.git
   cd flaskwarehouse
2. pip install -r requirements.txt
   
3. flask db init
flask db migrate -m "Initial migration"
flask db upgrade

4.python app.py

5.http://127.0.0.1:5000/

flaskwarehouse/
│
├──                   # Main application file
├── requirements.txt        # Python dependencies
├── static/
│   └── style.css           # CSS for styling
├── templates/
│   ├── index.html          # Home page
│   ├── location.html       # Assign locations to products
│   ├── view_locations.html # View all locations
│   ├── product_movement.html # Move products between locations
│   ├── view_navigation.html # View product movements
│   ├── report.html         # Generate reports
│   ├── edit_product.html   # Edit product details
│   ├── edit_location.html  # Edit location details
│   └── edit_navigation.html # Edit navigation details
└── README.md               # Project documentation
