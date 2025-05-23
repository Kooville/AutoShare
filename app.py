import sqlite3
import re
import secrets
from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session, flash
import db
import config
import items
import users


app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    items = users.get_items(user_id)
    return render_template("show_user.html", user=user, items=items)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("find_item.html", query=query, results=results)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    classes = items.get_classes(item_id)
    reservations = items.get_item_reservations(item_id)
    return render_template("show_item.html", item=item, classes=classes, reservations=reservations)

@app.route("/add_image/<int:item_id>", methods=["GET", "POST"])
def add_image(item_id):
    require_login()

    item = items.get_item(item_id)
    if not item or item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("add_image.html", item=item)

    if request.method == "POST":
        check_csrf()
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("VIRHE: Lähettämäsi tiedosto ei ole jpg-tiedosto")
            return redirect("/add_image/" + str(item_id))

        image = file.read()
        if len(image) > 100 * 1024:
            flash("VIRHE: Lähettämäsi tiedosto on liian suuri")
            return redirect("/add_image/" + str(item_id))

        items.update_image(item_id, image)
        return redirect("/item/" + str(item_id))

@app.route("/remove_image/<int:item_id>", methods=["GET", "POST"])
def remove_image(item_id):
    require_login()

    item = items.get_item(item_id)
    if not item or item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_image.html", item=item)

    if request.method == "POST":
        check_csrf()

        items.update_image(item_id, None)

        return redirect("/item/" + str(item_id))

@app.route("/image/<int:item_id>")
def show_image(item_id):
    image = items.get_image(item_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/new_item")
def new_item():
    require_login()
    classes = items.get_all_classes()
    return render_template("new_item.html", classes=classes)

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    check_csrf()

    makeandmodel = request.form["make_and_model"]
    if len(makeandmodel) > 50 or len(makeandmodel) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/new_item/")

    location = request.form["location"]
    if len(location) > 50 or len(location) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/new_item/")

    availability_start = request.form["availability_start"]
    availability_end = request.form["availability_end"]
    if len(availability_start) == 0 or len(availability_end) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/new_item/")

    if availability_end < availability_start:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/new_item/")

    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,4}$", price) or len(price) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/new_item/")

    description = request.form["description"]
    user_id = session["user_id"]

    all_classes = items.get_all_classes()

    classes = []

    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                flash("VIRHE: Virheellinen syöte")
                return redirect("/new_item/")
            if value not in all_classes[title]:
                flash("VIRHE: Virheellinen syöte")
                return redirect("/new_item/")
            classes.append((title, value))
    items.add_item(makeandmodel, location, availability_start, 
                   availability_end, price, description, user_id, classes)

    return redirect("/")

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    all_classes = items.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in items.get_classes(item_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_item.html", item=item, classes=classes, all_classes=all_classes)

@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    item = items.get_item(item_id)

    if not item:
        flash("VIRHE: Ajoneuvoa ei löydy")
        return redirect("/edit_item/" + str(item_id))

    if item["user_id"] != session["user_id"]:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/edit_item/" + str(item_id))

    makeandmodel = request.form["make_and_model"]

    if len(makeandmodel) > 50 or len(makeandmodel) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/edit_item/" + str(item_id))

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                flash("VIRHE: Virheellinen syöte")
                return redirect("/edit_item/" + str(item_id))

            if value not in all_classes[title]:
                flash("VIRHE: Virheellinen syöte")
                return redirect("/edit_item/" + str(item_id))

            classes.append((title, value))

    location = request.form["location"]
    if len(location) > 50 or len(location) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/edit_item/" + str(item_id))

    availability_start = request.form["availability_start"]
    availability_end = request.form["availability_end"]

    if len(availability_start) == 0 or len(availability_end) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/edit_item/" + str(item_id))

    if availability_end < availability_start:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/edit_item/" + str(item_id))

    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,4}$", price) or len(location) == 0:
        flash("VIRHE: Virheellinen syöte")
        return redirect("/edit_item/" + str(item_id))

    description = request.form["description"]

    items.update_item(item_id, makeandmodel, location, availability_start,
                      availability_end, price, description, classes)

    return redirect("/item/" + str(item_id))

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_item.html", item=item)
    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            items.remove_item(item_id)
            return redirect("/")
        return redirect("/item/" + str(item_id))

@app.route("/new_reservation", methods=["POST"])
def new_reservation():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    user_id = session["user_id"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    item = items.get_item(item_id)

    availability_start = item["availability_start"]
    availability_end = item["availability_end"]

    if start_date < availability_start or end_date > availability_end:
        flash("VIRHE: Kohde ei ole saatavilla valitsemanasi aikana.")
        return redirect("item/" + str(item_id))

    if start_date > end_date:
        flash("VIRHE: Loppupäivä ei voi olla ennen aloituspäivää.")
        return redirect("item/" + str(item_id))

    if items.check_reservations(item_id, start_date, end_date):
        flash("Virhe: Valitsemallasi ajanjaksolla on jo olemassaoleva varaus")
        return redirect("item/" + str(item_id))

    items.reserve_item(item_id, user_id, start_date, end_date)
    return redirect("item/" + str(item_id))

@app.route("/remove_reservation/<int:res_id>", methods=["GET", "POST"])
def remove_reservation(res_id):
    require_login()
    reservation = db.query("SELECT * FROM reservations WHERE id = ?", [res_id])

    if not reservation:
        return "Varausta ei löytynyt.", 404

    if reservation[0]["user_id"] != session["user_id"]:
        return "Ei oikeuksia poistaa tätä varausta.", 403

    if request.method == "POST":
        check_csrf()
        items.remove_reservation(res_id)
        return redirect("/item/" + str(reservation[0]["item_id"]))

    return render_template("remove_reservation.html", reservation=reservation[0])

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    if len(username) == 0 or len(username) > 50:
        flash("VIRHE: Käyttäjätunnuksen pituus ei voi olla 0")
        return redirect("/register")
    password1 = request.form["password1"]
    if len(password1) == 0:
        flash("VIRHE: Salasanan pituus ei voi olla 0")
        return redirect("/register")
    password2 = request.form["password2"]
    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return redirect("/register")
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        return redirect("/register")

    return redirect("/registered")

@app.route("/registered")
def registered():
    return render_template("registration_successful.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", next_page=request.referrer)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]

        user_id = users.check_login(username, password)

        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(next_page)
        else:
            flash("VIRHE: Väärä tunnus tai salasana")
            return render_template("login.html", next_page=next_page)

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    del session["csrf_token"]

    return redirect("/")
