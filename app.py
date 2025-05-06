from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), unique=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False, default=0)
    location_name = db.Column(db.String(100), nullable=True)
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)  # Changed to Integer
    location_name = db.Column(db.String(100), nullable=False)
class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False) 
    created_at = db.Column(db.DateTime, default=db.func.now())

@app.route('/')
def product1():
    edit_id = request.args.get('edit_id')
    product = Product.query.get(edit_id) if edit_id else None
    return render_template('index.html', products=Product.query.all(), product=product)

@app.route('/add_or_update_product', methods=['POST'])
def add_or_update_product():
    product_id = request.form.get('product_id')
    product_name = request.form.get('product_name').strip()
    product_quantity = int(request.form.get('product_quantity'))
    product_id_hidden = request.form.get('id')

    if product_quantity <= 0:
        return render_template('index.html', products=Product.query.all(), product=None, message="Product quantity must be greater than 0!")

    existing_product = Product.query.filter_by(product_name=product_name).first()
    if existing_product:
        existing_product.product_quantity = product_quantity
        db.session.commit()
        return redirect(url_for('product1'))

    if product_id_hidden:
        product = Product.query.get(product_id_hidden)
        if product:
            product.product_id = product_id
            product.product_name = product_name
            product.product_quantity = product_quantity
    else:
        new_product = Product(
            product_id=product_id,
            product_name=product_name,
            product_quantity=product_quantity
        )
        db.session.add(new_product)

    db.session.commit()
    return redirect(url_for('product1'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.product_id = request.form['product_id']
        product.product_name = request.form['product_name']
        product.product_quantity = request.form['product_quantity']
        db.session.commit()
        return redirect(url_for('product1'))
    return render_template('edit_product.html', product=product)

@app.route('/view_products')
def view_products():
    return render_template('view_products.html', products=Product.query.all())

@app.route('/location', methods=['GET'])
def location():
    # Fetch all products to display in the dropdown
    products = Product.query.all()
    return render_template('location.html', products=products)
@app.route('/add_location', methods=['POST'])
def add_location():
    product_id = request.form.get('product_id')
    location_name = request.form.get('location_name')

    product = Product.query.get(product_id)
    if product:
        product.location_name = location_name
        db.session.commit()

        existing_location = db.session.query(Location).filter_by(product_id=product_id, location_name=location_name).first()
        if not existing_location:
            new_location = Location(product_id=product_id, location_name=location_name)
            db.session.add(new_location)
            db.session.commit()

    return redirect(url_for('view_location'))

@app.route('/view_locations')
def view_locations():
    # Join Product and Location tables to fetch product details along with location
    locations = db.session.query(
        Location.product_id,
        Product.product_name,
        Location.location_name,
        Location.id.label("location_id")  # Add Location ID for editing
    ).join(Product, Product.product_id == Location.product_id).all()

    return render_template('view_locations.html', locations=locations)

@app.route('/edit_location/<int:id>', methods=['GET', 'POST'])
def edit_location(id):
    location = Location.query.get_or_404(id)
    if request.method == 'POST':
        location.location_name = request.form.get('location_name')
        db.session.commit()
        return redirect(url_for('view_locations'))
    return render_template('edit_location.html', location=location)

@app.route('/productmovement', methods=['GET', 'POST'])
def product_movement():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')
        quantity = int(request.form.get('quantity'))

        # Fetch the product from the specific from_location in the Location table
        location_entry = Location.query.filter_by(product_id=product_id, location_name=from_location).first()
        if location_entry:
            # Validate quantity in the from_location
            if location_entry.product_quantity < quantity:
                return render_template(
                    'product_movement.html',
                    products=Product.query.all(),
                    locations=Location.query.filter_by(product_id=product_id).all(),
                    message="Insufficient quantity in the selected location!"
                )

            # Insert the movement into the movements table
            new_movement = Movement(
                product_id=product_id,
                product_name=Product.query.filter_by(product_id=product_id).first().product_name,
                from_location=from_location,
                to_location=to_location,
                quantity=quantity
            )
            db.session.add(new_movement)
            db.session.commit()

            # Reduce the product's quantity in the from_location
            location_entry.product_quantity -= quantity
            db.session.commit()

            # Check if the product already exists in the to_location
            to_location_entry = Location.query.filter_by(product_id=product_id, location_name=to_location).first()
            if to_location_entry:
                # Update the quantity in the to_location
                to_location_entry.product_quantity += quantity
            else:
                # Create a new location entry for the to_location
                new_location = Location(
                    product_id=product_id,
                    location_name=to_location,
                    product_quantity=quantity
                )
                db.session.add(new_location)
            db.session.commit()

        return redirect(url_for('product_movement'))

    products = Product.query.all()
    locations = Location.query.all()
    return render_template('product_movement.html', products=products, locations=locations)

@app.route('/view_navigation')
def view_navigation():
    movements = Movement.query.all()
    return render_template('view_navigation.html', movements=movements)

@app.route('/edit_navigation/<int:id>', methods=['GET', 'POST'])
def edit_navigation(id):
    movement = Movement.query.get_or_404(id)
    if request.method == 'POST':
        movement.to_location = request.form.get('to_location')
        db.session.commit()
        return redirect(url_for('view_navigation'))
    return render_template('edit_navigation.html', movement=movement)

@app.route('/report', methods=['GET', 'POST'])
def report():
    products = []
    selected_location = None

    if request.method == 'POST':
        selected_location = request.form.get('location_name')  # Get the selected location
        # Fetch products assigned to the selected location (to_location)
        products = Product.query.filter_by(location_name=selected_location).all()

    # Predefined locations
    locations = ["Coimbatore", "Erode", "Tiruppur"]

    return render_template('report.html', products=products, locations=locations, selected_location=selected_location)

if __name__ == '__main__':
    app.run(debug=True)
