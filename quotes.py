from flask import Flask, render_template, request,redirect
from mongita import MongitaClientDisk
from bson import ObjectId
import json
app = Flask(__name__)

# create Mongita client connection
client = MongitaClientDisk()

# open quotes database
quotes_db = client.quotes_db

@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
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
    return render_template("quotes.html", data=data)

@app.route("/edit", methods=["GET"])
@app.route("/edit/<id>", methods=["GET"])
def get_edit(id=None):
    if id:
        quotes_collection = quotes_db.quotes_collection
        data = quotes_collection.find_one({"_id":ObjectId(id)})
    return render_template("form.html")



@app.route("/create", methods=["POST"])
def get_create():
    quotes_collection = quotes_db.quotes_collection
    data = request.get_data()
    
    print(json.loads(data))
    quotes_collection.insert_one(json.loads(data))
    return redirect("/quotes")
# adding /edit /edit/id
# if form not filled correctly redirect back to edit
# adding /create get/post