from flask import Flask, render_template, session, redirect, url_for, request
import psycopg2

app = Flask(__name__)
app.secret_key = "secret"

# Database connection
conn = psycopg2.connect(
    host="dpg-d6qgdn15pdvs73b9rd40-a.oregon-postgres.render.com",
    database="flourmill",
    user="flouruser",
    password="IgzNLTYVXB6PohifqAO1KGwZBS8YxWbK",
    port="5432",
    sslmode="require"
)


cursor = conn.cursor()


conn.autocommit = True


@app.route("/products")
def products():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    print(products)

    return render_template("products.html", products=products)


@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=%s",(id,))
    product = cursor.fetchone()
    cursor.close()

    item = {
        "id": product[0],
        "name": product[1],
        "price": product[2],
        "image": product[4],
        "quantity": 1
    }

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(item)
    session.modified = True

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():

    cart_items = session.get("cart", [])

    total = 0
    for item in cart_items:
        total += int(item["price"]) * int(item["quantity"])

    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/checkout")
def checkout():

    cart_items = session.get("cart", [])

    total = 0
    for item in cart_items:
        total += int(item["price"]) * int(item["quantity"])

    return render_template("checkout.html", total=total)


@app.route("/place_order", methods=["POST"])
def place_order():

    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]

    cart_items = session.get("cart", [])

    total = 0
    for item in cart_items:
        total += int(item["price"]) * int(item["quantity"])
        cursor = conn.cursor()

    query = "INSERT INTO orders (name,phone,address,total) VALUES (%s,%s,%s,%s)"
    cursor.execute(query,(name,phone,address,total))
    conn.commit()
    cursor.close()

    session.pop("cart",None)

    return "Order Placed Successfully"

@app.route("/admin")
def admin():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.close()

    return render_template("admin.html", orders=orders)


app.run(debug=True)