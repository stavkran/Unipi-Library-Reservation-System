import flask as fk
import pymongo as pm
import re
from datetime import date
from pymongo import MongoClient
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from itertools import chain
from datetime import datetime, timedelta
from bson import ObjectId

#User blueprint
user = fk.Blueprint("user", __name__, static_folder="static", template_folder="templates")

#Connect to mongodb
client = MongoClient("mongodb://mongodb:27017/")
db = client["UnipiLibrary"]
usersDb = db["users"]
booksDb = db["books"]
reservedbooksDb = db["reservedbooks"]

@user.route("/")
@user.route("/userHomePage", methods=["GET"])
def userHomePage():
    if fk.request.method == "GET":
        return fk.render_template("userHomepage.html")
    else:
        return fk.redirect(fk.url_for("user.userHomePage"))

# User's home page which also shows all the unreserved books.
@user.route("/")
@user.route("/userAvailableBooks", methods=["GET"])
def userAvailableBooks():
    # Get all books from the database
    all_books = list(booksDb.find())

    # Get all the reserved books from the database
    reserved_books = list(reservedbooksDb.find())

    # Create a set of reserved ISBNs for faster lookup
    reserved_isbns = set(book["isbn"] for book in reserved_books)

    # Create an empty list to hold available books
    available_books = []

    for book in all_books:
        if book["isbn"] not in reserved_isbns:
            available_books.append(book)

    return render_template("userAvailableBooks.html", available_books=available_books)

# Reserve a book
@user.route("/")
@user.route("/reserveBook", methods=["GET","POST"])
def reserveBook():
    user = usersDb.find_one({"email": session["email"]})
    if request.method == "GET":
        if session.get("email"):
            user = usersDb.find_one({"email": session["email"]})
            if user:
                user_data = {
                    "firstname": user.get("firstname"),
                    "surname": user.get("surname"),
                    "email": user.get("email")
                }
                return render_template("userReserveBook.html", user=user_data)
            else:
                flash("User not found.", "error")
                return redirect(url_for("auth.signIn"))
        else:
            flash("You must be logged in to reserve a book.", "error")
            return redirect(url_for("auth.signIn"))
    else:
        if not session.get("email"):
            flash("You must be logged in to reserve a book.", "error")
            return redirect(url_for("auth.signIn"))

        # Get the ISBN of the book to be reserved from the form
        isbn = request.form.get("isbn")
        mobile = request.form.get("mobile")

        # Check if the book with the given ISBN exists
        book = booksDb.find_one({"isbn": isbn})

        if not book:
            flash("The book with the provided ISBN does not exist.", "error")
            return redirect(request.referrer)

        # Check if the book is already reserved
        existing_reservation = reservedbooksDb.find_one({"isbn": isbn})

        if existing_reservation:
            flash("This book is already reserved by another user.", "error")
            return redirect(request.referrer)

        # Calculate the reservation end date based on the 'reservationdays' field
        reservation_days = int(book.get("reservationdays", 14))  # Default to 14 days if 'reservationdays' is not specified
        reservation_end_date = datetime.now() + timedelta(days=reservation_days)

        # Create a reservation document and save it to the 'reservedbooks' collection
        reservation = {
            "title": book["title"],
            "author": book["author"],
            "isbn": book["isbn"],
            "user": {
                "firstname": user["firstname"],  
                "surname": user["surname"],      
                "email": user["email"],          
                "mobile": mobile       
            },
            "reservation": {
                "reservationdate": datetime.now().strftime('%Y-%m-%d'),
                "returndate": reservation_end_date.strftime('%Y-%m-%d')
            }
        }
        reservedbooksDb.insert_one(reservation)

        flash(f"The book '{book['title']}' has been successfully reserved.", "success")

        # Check if the reservation date is approaching the return date
        today = datetime.now()
        notification_threshold = timedelta(days=reservation_days - 1)  # Notify 1 day before the return date
        if reservation_end_date - today <= notification_threshold:
            flash(f"The book with the title '{book['title']}' you've reserved needs to be returned soon. "
                f"If you don't return it by {reservation_end_date.strftime('%Y-%m-%d')}, a fine will be charged.", "warning")

        return redirect(request.referrer)
    

# See Your Reservation
@user.route("/")
@user.route("/userReservations", methods=["GET"])
def userReservations():
    if not session.get("email"):
        flash("You must be logged in to view your reservations.", "error")
        return redirect(url_for("auth.signIn"))

    # Get the user's email
    user_email = session["email"]

    users_reservations = list(reservedbooksDb.find({}))
    print(users_reservations)

    user_reservations = list(reservedbooksDb.find({"user.email": user_email}))

    print(user_reservations)

    # Calculate days remaining for each reservation
    for reservation in user_reservations:
        returndate = datetime.strptime(reservation['reservation']['returndate'], '%Y-%m-%d')
        today = datetime.now()
        days_remaining = (returndate - today).days
        reservation['days_remaining'] = days_remaining

    return render_template("userReservations.html", user_reservations=user_reservations, is_book_return_soon=is_book_return_soon)

def is_book_return_soon(return_date):
    # Convert the return_date string to a datetime object
    return_date_obj = datetime.strptime(return_date, '%Y-%m-%d')

    # Calculate the difference between the return date and the current date
    time_difference = return_date_obj - datetime.now()

    # Check if the time difference is less than or equal to 1 day
    return time_difference <= timedelta(days=1)
    
# See All Registered Books
@user.route("/search")
@user.route("/userSeeAllBooks", methods=["GET"])
def userSeeAllBooks():
    # Get all books from the database
    books = list(booksDb.find())

    return render_template("userSeeAllBooks.html", books=books, is_book_reserved=is_book_reserved)

# Search via Title
@user.route("/search")
@user.route("/searchViaTitle", methods=["GET", "POST"])
def searchViaTitle():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaTitle.html")
    else:
        title = request.form["title"]
        result = booksDb.count_documents({"title": title})

        if result == 0:
            flash(f"There is no book with the title: {title}")
            return redirect(url_for("user.searchViaTitle"))
        else:
            books = booksDb.find({"title": title})
            return render_template("userSearchViaTitle.html", books=books, is_book_reserved=is_book_reserved)


# Search via Author      
@user.route("/search")
@user.route("/searchViaAuthor", methods=["GET", "POST"])
def searchViaAuthor():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaAuthor.html")
    else:
        author = fk.request.form["author"]
        result = booksDb.count_documents({"author": author})

        if result == 0:
            fk.flash(f"There is no book by the author: {author}")
            return fk.redirect(fk.url_for("user.searchViaAuthor"))
        else:
            books = booksDb.find({"author": author})
            return fk.render_template("userSearchViaAuthor.html", books=books, is_book_reserved=is_book_reserved)
        
def is_book_reserved(title):
    reserved_book = reservedbooksDb.find_one({"title": title})
    return reserved_book is not None
        

# Search via ISBN      
@user.route("/search")
@user.route("/searchViaISBN", methods=["GET", "POST"])
def searchViaISBN():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaISBN.html")
    else:
        isbn = fk.request.form["isbn"]
        result = booksDb.count_documents({"isbn": isbn})

        if result == 0:
            fk.flash(f"There is no book with the isbn code: {isbn}")
            return fk.redirect(fk.url_for("user.searchViaISBN"))
        else:
            books = booksDb.find({"isbn": isbn})
            return fk.render_template("userSearchViaISBN.html", books=books, is_book_reserved=is_book_reserved)
        

# Search via Date      
@user.route("/search")
@user.route("/searchViaDate", methods=["GET", "POST"])
def searchViaDate():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaDate.html")
    else:
        publicationdate = fk.request.form["publicationdate"]
        result = booksDb.count_documents({"publicationdate": publicationdate})

        if result == 0:
            fk.flash(f"There is no book published on that date: {publicationdate}")
            return fk.redirect(fk.url_for("user.searchViaDate"))
        else:
            books = booksDb.find({"publicationdate": publicationdate})
            return fk.render_template("userSearchViaDate.html", books=books, is_book_reserved=is_book_reserved)

# show book details (via ISBN)

# unreserve book 
@user.route("/")
@user.route("/unreserveBook", methods=["GET","POST"])
def unreserveBook():
    if fk.request.method == "GET":
        return fk.render_template("userUnreservedBook.html")
    else:
        if not session.get("email"):
            flash("You must be logged in to cancel a reservation.", "error")
            return redirect(url_for("auth.signIn"))

        # Get the reservation ID from the form
        reservation_id = request.form.get("reservedbook")

        # Check if the reservation exists
        existing_reservation = reservedbooksDb.find_one({"_id": ObjectId(reservation_id)})

        if not existing_reservation:
            flash("Reservation not found. Please check the reservation ID.", "error")
            return redirect(request.referrer)

        # Check if the user is authorized to cancel this reservation
        if existing_reservation["user"]["email"] != session["email"]:
            flash("You are not authorized to cancel this reservation.", "error")
            return redirect(request.referrer)

        # Delete the reservation
        reservedbooksDb.delete_one({"_id": ObjectId(reservation_id)})

        flash("Reservation canceled successfully.", "success")
        return redirect(request.referrer)


        


# Delete account.
@user.route("/")
@user.route("/deleteAccount", methods=["GET","POST"])
def deleteAccount():
    if fk.request.method == "GET":
        return fk.render_template("userDeleteAccount.html")
    else:
        email = fk.request.form["email"]
        if email == fk.session["email"]:
            usersDb.delete_one({"email": email})
            fk.flash("Account successfully deleted!")
            return fk.redirect(fk.url_for("auth.signUp"))
        else:
            fk.flash("Invalid username")
            return fk.redirect(fk.url_for("user.userDeleteAccount"))

