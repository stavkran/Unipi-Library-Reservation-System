from flask import Flask, redirect, url_for, render_template
import json
import flask as fk
from pymongo import MongoClient

#Import pymethods from other files
from pymethods.user import user
from pymethods.auth import auth
from pymethods.admin import admin

#insert collection to db
def insert(collection, document):
    match = collection.find_one(document)

    if not match:
        collection.insert_one(document)

#Insert json to collection
def insert_json(path, collection):
    data = None

    try:
        with open(path, "r") as file:
            data = json.load(file)
    except Exception:
        print(f"Failed to read the file and/or parse json for the {collection} we want to insert to the database")
        return

    for document in data:
        insert(collection, document)


#Connect to mongodb
client = MongoClient("mongodb://mongodb:27017/")
db = client["UnipiLibrary"]
usersDb = db["users"]
booksDb = db["books"]
reservedbooksDb = db["reservedbooks"]

app = Flask(__name__)
app.secret_key = "UnipiLibrarySecretKey"


#Blueprints
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(admin, url_prefix="/admin")


# Home.
@app.route("/home", methods=["GET"])
def index():
    return "<h2>Welcome to UnipiLibrary</h2>"

# Redirect to signIn.
@app.route("/")
@app.route("/signIn")
def goToSignIn():
    return redirect(fk.url_for("auth.signIn"))


if __name__ == "__main__":
    if not "UnipiLibrary" in db.list_collection_names():
        insert_json("books.json", booksDb)
        insert_json("users.json", usersDb)
        insert_json("reservedbooks.json", reservedbooksDb)

    app.run(debug=True, host='0.0.0.0', port=5000)