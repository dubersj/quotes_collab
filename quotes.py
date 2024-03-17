from flask import Flask, render_template, request, redirect, session, url_for
from mongita import MongitaClientDisk
from bson import ObjectId
import json
import jwt

app = Flask(__name__)
app.secret_key = 'quotes_application'


def login_required(route):
    def inner(*args, **kwargs):
        if not session.get("token"):
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return inner


def generate_token(user):
    return jwt.encode(user, "quotes_application", algorithm="HS256")


# create Mongita client connection
client = MongitaClientDisk()

# open quotes database
quotes_db = client.quotes_db


@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
@login_required
def get_quotes():
    quotes_collection = quotes_db.quotes_collection
    data = list(quotes_collection.find({}))
    for item in data:
        #del item["_id"]
        item["_id"] = str(item["_id"])
        item["object"] = ObjectId(item["_id"])
    return render_template("quotes.html", data=data)


@app.route("/delete", methods=["GET"])
@app.route("/delete/<id>", methods=["GET"])
def get_delete(id=None):
    if id:
        quotes_collection = quotes_db.quotes_collection
        data = list(quotes_collection.find({"_id":ObjectId(id)}))
        quotes_collection.delete_one({"_id":ObjectId(id)})
    return redirect("/quotes")

@app.route("/edit", methods=["GET"])
@app.route("/edit/<id>", methods=["GET"])
def get_edit(id=None):
    if id:
        quotes_collection = quotes_db.quotes_collection
        data = quotes_collection.find_one({"_id":ObjectId(id)})
        print(len(data["author"]))
        if len(data["author"])>0 and len(data["quote"]) > 0:
            print("here")
            return render_template("edit.html", data=data)
        return render_template("form.html", data=data)
    else: return render_template("form.html")


@app.route("/update", methods=["POST"])
def update_quote():
    quotes_collection = quotes_db.quotes_collection
    data = request.get_data()
    print(json.loads(data))
    quotes_collection.update_one({"_id":ObjectId(json.loads(data)["_id"])},{"$set":json.loads(data)})
    return redirect("/quotes")

@app.route("/create", methods=["POST"])
def get_create():
    quotes_collection = quotes_db.quotes_collection
    data = request.get_data()
    
    print(json.loads(data))
    quotes_collection.insert_one(json.loads(data))
    return redirect("/quotes")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        userscollection = quotes_db.users_collection
        email = request.form.get("email")
        password = request.form.get("password")
        token = generate_token({"email": email})
        #check if the user is already in the database
        data = userscollection.find_one({"email": email})
        if data:
            return render_template("signup.html", error="User already exists")
        userscollection.insert_one({"email": email, "password": password, "token": token})
        session["token"] = token
        return redirect("/quotes")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userscollection = quotes_db.users_collection
        email = request.form.get("email")
        password = request.form.get("password")
        data = userscollection.find_one({"email": email, "password": password})
        if data:
            session["token"] = data["token"]
            return redirect("/quotes")
        else:
            return render_template("login.html", error="Invalid Credentials")
    return render_template("login.html", error=None)


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("token", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
