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

# cursor = conn.cursor()   #FIX: ye remove kiya (global cursor unnecessary)
conn.autocommit = True

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    # print(products)   #FIX: remove kiya (production me useless)

    return render_template("products.html", products=products)


@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=%s",(id,))
    product = cursor.fetchone()
    cursor.close()

    #FIX: product None check add kiya
    if not product:
        return "Product not found"

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

    return redirect(url_for("products"))


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


@app.route("/update_quantity/<int:id>/<string:action>")
def update_quantity(id, action):

    cart = session.get("cart", [])

    for item in cart:
        if item["id"] == id:
            if action == "increase":
                item["quantity"] += 1
            elif action == "decrease":
                if item["quantity"] > 1:
                    item["quantity"] -= 1

    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/remove_item/<int:id>")
def remove_item(id):

    cart = session.get("cart", [])

    cart = [item for item in cart if item["id"] != id]

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/place_order", methods=["POST"])
def place_order():

    cursor = conn.cursor()

    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]

    cart_items = session.get("cart", [])

    #FIX: empty cart check add kiya
    if not cart_items:
        return "Cart is empty"

    total = 0
    for item in cart_items:
        total += int(item["price"]) * int(item["quantity"])


    query = "INSERT INTO orders (name,phone,address,total) VALUES (%s,%s,%s,%s)"
    cursor.execute(query,(name,phone,address,total))
    conn.commit()
    cursor.close()

    session.pop("cart",None)

    return render_template("success.html")

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()

    return render_template("admin.html", products=products)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    description = request.form["description"]
    image = request.form["image"]

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name,price,description,image_url) VALUES (%s,%s,%s,%s)",
        (name, price, description, image)
    )
    conn.commit()
    cursor.close()

    return redirect("/admin")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # simple hardcoded login (baad me DB se bhi kar sakte hain)
        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


@app.route("/delete_product/<int:id>")
def delete_product(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    cursor.close()

    return redirect("/admin")

app.run(debug=True)  #UPDATED: live karte time debug=False kar dena