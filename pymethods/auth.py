import flask as fk
import pymongo as pm
from pymongo import MongoClient

#Authentication Blueprint
auth = fk.Blueprint("auth", __name__, static_folder="static", template_folder="templates")

#Connect to mongodb
client = MongoClient("mongodb://mongodb:27017/")
db = client["UnipiLibrary"]
usersDb = db["users"]
booksDb = db["books"]
reservedbooksDb = db["reservedbooks"]
#Sign Up.
@auth.route("/signUp", methods=["GET", "POST"])
def signUp():
    if fk.request.method == "GET":
        return fk.render_template("signUp.html")
    else:
        firstname = fk.request.form["firstname"]
        surname = fk.request.form["surname"]
        email = fk.request.form["email"]
        password = fk.request.form["password"]
        dateofbirth = fk.request.form["dateofbirth"]

        # Check if email exists.
        exists_email = usersDb.find_one({"email":email})
        
        if (exists_email is None):
            new_user = {"firstname": firstname, "surname": surname, "email": email, "password": password, "dateofbirth": dateofbirth,"category": "user"}
            usersDb.insert_one(new_user)
            return fk.redirect(fk.url_for("auth.signIn"))
        else:
            fk.flash("This email has already been registered!")
            return fk.redirect(fk.url_for("auth.signUp"))


# Sign In.
@auth.route("/")
@auth.route("/signIn", methods=["GET","POST"])
def signIn():
    if fk.request.method == "GET":
        return fk.render_template("signIn.html")
    else:
        email = fk.request.form["email"]
        password = fk.request.form["password"]
        user = usersDb.find_one({"email":email})
        if user is None:
            fk.flash("Invalid e-mail")
            return fk.redirect(fk.url_for("auth.signIn"))
        elif user["password"] == password:

            # Assign session variable
            fk.session["email"] = user["email"]

            # Log In according to property
            if user["category"] == "admin":
                fk.flash(f"Successfully logged in as { email }")
                return fk.redirect(fk.url_for("admin.adminHome"))
            else:
                fk.flash(f"Successfully logged in as { email }")
                return fk.redirect(fk.url_for("user.userHomePage"))
        else:
            fk.flash("Invalid Password")
            return fk.redirect(fk.url_for("auth.signIn"))


# Sign out.
@auth.route("/signOut")
def signOut():
    fk.session.pop("email", None)
    return fk.redirect(fk.url_for("auth.signIn"))

