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
        result = booksDb.count_documents({"title": title})

        if result == 0:
            fk.flash(f"There is no book with the title: {title}")
            return fk.redirect(fk.url_for("admin.searchViaTitle"))
        else:
            books = booksDb.find({"title": title})
            return fk.render_template("adminSearchViaTitle.html", books=books, is_book_reserved=is_book_reserved)

# Search via Author      
@admin.route("/search")
@admin.route("/searchViaAuthor", methods=["GET", "POST"])
def searchViaAuthor():
    if fk.request.method == "GET":
        return fk.render_template("adminSearchViaAuthor.html")
    else:
        author = fk.request.form["author"]
        result = booksDb.count_documents({"author": author})

        if result == 0:
            fk.flash(f"There is no book by the author: {author}")
            return fk.redirect(fk.url_for("admin.searchViaTitle"))
        else:
            books = booksDb.find({"author": author})
            return fk.render_template("adminSearchViaAuthor.html", books=books, is_book_reserved=is_book_reserved)
        
def is_book_reserved(title):
    reserved_book = reservedbooksDb.find_one({"title": title})
    return reserved_book is not None
        
# Search via ISBN      
@admin.route("/search")
@admin.route("/searchViaISBN", methods=["GET", "POST"])
def searchViaISBN():
    if fk.request.method == "GET":
        return fk.render_template("adminSearchViaISBN.html")
    else:
        isbn = fk.request.form["isbn"]
        result = booksDb.count_documents({"isbn": isbn})

        if result == 0:
            fk.flash(f"There is no book with the isbn code: {isbn}")
            return fk.redirect(fk.url_for("admin.searchViaISBN"))
        else:
            books = booksDb.find({"isbn": isbn})
            return fk.render_template("adminSearchViaISBN.html", books=books, is_book_reserved=is_book_reserved)
        

@admin.route("/search")
@admin.route("/searchViaDate", methods=["GET", "POST"])
def searchViaDate():
    if fk.request.method == "GET":
        return fk.render_template("adminSearchViaDate.html")
    else:
        publicationdate = fk.request.form["publicationdate"]
        result = booksDb.count_documents({"publicationdate": publicationdate})

        if result == 0:
            fk.flash(f"There is no book published on that date: {publicationdate}")
            return fk.redirect(fk.url_for("admin.searchViaDate"))
        else:
            books = booksDb.find({"publicationdate": publicationdate})
            return fk.render_template("adminSearchViaDate.html", books=books, is_book_reserved=is_book_reserved)

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

