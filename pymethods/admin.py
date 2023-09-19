import flask as fk
import pymongo as pm
import re
from datetime import date
from pymongo import MongoClient
import json

#Admin Blueprint
admin = fk.Blueprint("admin", __name__, static_folder="static", template_folder="templates")

#Connect to mongodb
client = MongoClient("mongodb://mongodb:27017/")
db = client["UnipiLibrary"]
usersDb = db["users"]
booksDb = db["books"]
reservedbooksDb = db["reservedbooks"]

#Admin Home Page
@admin.route("/")
@admin.route("/adminHome", methods=["GET"])
def adminHome():
    all_books = list(booksDb.find({}))
    return fk.render_template("adminHomePage.html", books = all_books)

# Import Book
@admin.route("/")
@admin.route("/importBook", methods=["GET","POST"])
def importBook():
    if fk.request.method == "GET":
        return fk.render_template("adminImportBook.html")
    else:
        # Check if book already exists in the system.
        title = fk.request.form["title"]
        author = fk.request.form["author"]
        publicationdate = fk.request.form["publicationdate"]
        isbn = fk.request.form["isbn"]
        summary = fk.request.form["summary"]
        pagesnum = int(fk.request.form["pagesnum"])
        reservationdays = int(fk.request.form["reservationdays"])
        print(type(reservationdays))
        existing_book = booksDb.find_one({
            "isbn": isbn
        })
        if (existing_book is None):
            # If no book exists, create the new book registration and return to home page
            new_book = {"title": title, "author": author, "publicationdate": publicationdate, "isbn": isbn, "summary": summary,"pagesnum": pagesnum, "reservationdays": reservationdays}
            booksDb.insert_one(new_book)
            fk.flash("New book registration successfully imported!")
            return fk.redirect(fk.url_for("admin.adminHome"))
        else:
            fk.flash("Book already exists in the System.")
            return fk.redirect(fk.url_for("admin.importBook"))
        
#Update Book Reservation Days
@admin.route("/")
@admin.route("/updateResDays", methods=["GET","POST"])
def updateResDays():
    if fk.request.method == "GET":
        return fk.render_template("adminUpdateResDays.html")
    else:
        # Check if book registration exists.
        isbn = fk.request.form["isbn"]
        reservationdays = fk.request.form["reservationdays"]
        bookexists = booksDb.find_one({
            "isbn": isbn
        })
        if (bookexists is None):
            fk.flash("This book registration does not exist.")
            return fk.redirect(fk.url_for("admin.updateResDays"))
        else:
            # Update the reservation days of the book registration.
            booksDb.update_one({"isbn": isbn}, {"$set": {"reservationdays": reservationdays}})
            fk.flash("Reservation days of the book updated successfully!")
            return fk.redirect(fk.url_for("admin.adminHome"))
    
# Delete book registration
@admin.route("/")
@admin.route("/deleteBook", methods=["GET", "POST"])
def deleteFlight():
    if fk.request.method == "GET":
        return fk.render_template("adminDeleteBook.html")
    else:
        # Check if book registration exists.
        isbn = fk.request.form["isbn"]
        bookexists =booksDb.find_one({"isbn": isbn})
        reservationexeists = reservedbooksDb.find_one({"isbn": isbn})

        if (bookexists):
            # Check if the book is reserved by any user.
            if reservationexeists is None:
                # Delete the book registration from the system
                booksDb.delete_one({"isbn": isbn})
                fk.flash("Book registration deleted successfully!")
                return fk.redirect(fk.url_for("admin.adminHome"))
            else:
                fk.flash("Book registration cannot be deleted as it is reserved by a user.")
                return fk.redirect(fk.url_for("admin.deleteBook"))
        else:
            fk.flash("Book Registrtation does not exist.")
            return fk.redirect(fk.url_for("admin.deleteBook"))
        
# Search via Title
@admin.route("/search")
@admin.route("/searchViaTitle", methods=["GET", "POST"])
def searchViaTitle():
    if fk.request.method == "GET":
        return fk.render_template("adminSearchViaTitle.html")
    else:
        title = fk.request.form["title"]
        bookresults = db.booksDb.find({"title": title})
        if bookresults:
            reservedBook = db.reservedbooksDb.find_one({"title": title})

            if reservedBook is None:
                return fk.render_template("adminSearchViaTitle.html", book=bookresults)
        if bookresults is None:
            fk.flash("No book registrations found in the system.")
            return fk.redirect(fk.url_for("admin.searchViaTitle"))
        else:
            return fk.render_template("adminSearchViaTitle.html", book=bookresults)

# Search via Author      
@admin.route("/search")
@admin.route("/searchViaAuthor", methods=["GET", "POST"])
def searchViaAuthor():
    if fk.request.method == "GET":
        return fk.render_template("adminSearchViaAuthor.html")
    else:
        author = fk.request.form["author"]
        bookresults = db.booksDb.find({"author": author})
        if bookresults:
            reservedBook = db.reservedbooksDb.find_one({"author": author})

            if reservedBook is None:
                return fk.render_template("adminSearchViaAuthor.html", book=bookresults)
        if bookresults is None:
            fk.flash("No book registrations found in the system.")
            return fk.redirect(fk.url_for("admin.searchViaAuthor"))
        else:
            return fk.render_template("adminSearchViaAuthor.html", book=bookresults)
        
# Search via ISBN      
@admin.route("/search")
@admin.route("/searchViaISBN", methods=["GET", "POST"])
def searchViaISBN():
    if fk.request.method == "GET":
        return fk.render_template("adminSearchViaISBN.html")
    else:
        isbn = fk.request.form["isbn"]
        bookresults = db.booksDb.find({"isbn": isbn})
        if bookresults:
            reservedBook = db.reservedbooksDb.find_one({"isbn": isbn})

            if reservedBook is None:
                return fk.render_template("adminSearchViaISBN.html", book=bookresults)
        if bookresults is None:
            fk.flash("No book registrations found in the system.")
            return fk.redirect(fk.url_for("admin.searchViaISBN"))
        else:
            return fk.render_template("adminSearchViaISBN.html", book=bookresults)

#Show all book details
@admin.route("/")
@admin.route("/showBookDetails", methods=["GET", "POST"])
def showDetails():
    # Get all books from the database
    books = list(db.booksDb.find())

    # Create an empty list to hold the book details
    book_details = []

    for book in books:
        book_detail = {
            "title": book["title"],
            "author": book["author"],
            "publicationdate": book["publicationdate"],
            "isbn": book["isbn"],
            "summary": book["summary"],
            "pagesnum": book["pagesnum"],
            "reservationdays": book["reservationdays"],
            "reserved_by": None
        }
    
        # Check if the book is reserved
        reserved_book = db.reservedbooksDb.find_one({"title": book["title"]})
        if reserved_book:
            user = reserved_book["user"]
            book_detail["reserved_by"] = {
                "firstname": user["firstname"],
                "surname": user["surname"],
                "email": user["email"],
                "mobile": user["mobile"]
            }

        book_details.append(book_detail)

    return fk.render_template("adminBookDetails.html", book_details=book_details)

