import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
import db
import config
import items
import users
import re
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    print("tarkastus toimii")
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
        abort(403)
    location = request.form["location"]
    if len(location) == 0:
        abort(403)
    availability = request.form["available"]
    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,4}$", price):
        abort(403)
    description = request.form["description"]
    user_id = session["user_id"]

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                abort(403)
            if value not in all_classes[title]:
                abort(403)
            classes.append((title, value))
    items.add_item(makeandmodel, location, availability, price, description, user_id, classes)

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
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    makeandmodel = request.form["make_and_model"]
    if len(makeandmodel) > 50 or len(makeandmodel) == 0:
        abort(403)
    
    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                abort(403)
            if value not in all_classes[title]:
                abort(403)
            classes.append((title, value))

    location = request.form["location"]
    if len(location) == 0:
        abort(403)
    availability = request.form["available"]
    price = request.form["price"]
    if not re.search("^[1-9][0-9]{0,4}$", price):
        abort(403)

    description = request.form["description"]

    items.update_item(item_id, makeandmodel, location, availability, price, description, classes)

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
        else:
            return redirect("/item/" + str(item_id))

@app.route("/new_reservation", methods=["POST"])
def new_reservation():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    user_id = session["user_id"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    if start_date > end_date:
        return "Virhe: Loppupäivä ei voi olla ennen aloituspäivää.", 400

    if items.check_reservations(item_id, start_date, end_date):
        return "Virhe: Valitsemallasi ajanjaksolla on jo olemassaoleva varaus"

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
        abort(403)
    password1 = request.form["password1"]
    if len(password1) == 0:
        abort(403)
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return redirect("/registered")

@app.route("/registered")
def registered():
    return render_template("registration_successful.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = users.check_login(username, password)

        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")