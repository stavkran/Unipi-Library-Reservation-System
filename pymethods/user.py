import flask as fk
import pymongo as pm
import re
from datetime import date
from pymongo import MongoClient
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, redirect, url_for, session, flash

#User blueprint
user = fk.Blueprint("user", __name__, static_folder="static", template_folder="templates")

#Connect to mongodb
client = MongoClient("mongodb://mongodb:27017/")
db = client["UnipiLibrary"]
usersDb = db["users"]
booksDb = db["books"]
reservedbooksDb = db["reservedbooks"]

# User's home page which also shows all the unreserved books.
@user.route("/")
@user.route("/userAvailableFlights", methods=["GET"])
def userHomePage():
    # Get all books from the database
    all_books = list(db.booksDb.find())

    #Get all the reserved books from the database
    reserved_books = list(db.reservedbooksDb.find())

    # Create a set of reserved ISBNs for faster lookup
    reserved_isbns = set(book["isbn"] for book in reserved_books)

    # Create an empty list to hold unreserved books
    unreserved_books = []

    for book in all_books:
         if book["isbn"] not in reserved_isbns:
            unreserved_books.append(book)

    return fk.render_template("userAvailableBooks.html", unreserved_books=unreserved_books)
   
# Reserve a book
@user.route("/")
@user.route("/reserveBook", methods=["GET","POST"])
def reserveBook():
    if fk.request.method == "GET":
        # Get the user's information from the user JSON file
        with open("users.json", "r") as users_file:
            users_data = json.load(users_file)
        
        # Find the user based on their email (assuming email is used as a unique identifier)
        signed_in_user = next((user for user in users_data if user["email"] == fk.session["email"]), None)
        
        if signed_in_user:
            return fk.render_template("userReserveBook.html", user=signed_in_user)
        else:
            fk.flash("User not found!")
            return fk.redirect(fk.url_for("user.reserveBook"))
    else:
        #request values
        isbn = fk.request.form["isbn"]  # Assuming the user provides the unique ISBN code
        firstname = fk.request.form["firstname"]
        surname = fk.request.form["surname"]
        email = fk.request.form["email"]
        mobile = fk.request.form["mobile"]

        # Check if the book with the given ISBN exists
        matched_book = db.booksDb.find_one({"isbn": isbn})

        # for book in all_books:
        #     if book["_id"] != bookid:
        #         flash(f"The ")

        if matched_book:
             # Calculate the reservation expiration date (7 days from now)
            reservation_duration = matched_book["reservationdays"]  # Number of days for the reservation
            
            # Calculate the reservation expiration date based on the reservation duration
            reservation_expiration = datetime.now() + timedelta(days=reservation_duration)

            reserved_book = {
                "_id": matched_book["_id"],
                "title": matched_book["title"],  # Replace with the appropriate field name
                "firstname": firstname,
                "surname": surname,
                "email": email,
                "email": email,
                "reservation_expiration": reservation_expiration.strftime("%Y-%m-%d")  # Format as "YYYY-MM-DD"
            }

            # Insert the reserved book into the reservedbooksDb collection
            db.reservedbooksDb.insert_one(reserved_book)
             
            # Return a success message or redirect to a success page
            return fk.redirect(fk.url_for("user.reserveBook"))
    
        else:
            # Book with the given ISBN doesn't exist
            fk.flash(f"The book with the ISBN '{isbn}' doesn't exist. Please insert a different ISBN.")
            return fk.redirect(fk.url_for("user.reserveBook"))


# Search via Title
@user.route("/search")
@user.route("/searchViaTitle", methods=["GET", "POST"])
def searchViaTitle():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaTitle.html")
    else:
        title = fk.request.form["title"]
        bookresults = db.booksDb.find({"title": title})
        if bookresults:
            reservedBook = db.reservedbooksDb.find_one({"title": title})

            if reservedBook is None:
                return fk.render_template("userSearchViaTitle.html", book=bookresults)
        if bookresults is None:
            fk.flash("No book registrations found in the system.")
            return fk.redirect(fk.url_for("user.searchViaTitle"))
        else:
            return fk.render_template("userSearchViaTitle.html", book=bookresults)


# Search via Author      
@user.route("/search")
@user.route("/searchViaAuthor", methods=["GET", "POST"])
def searchViaAuthor():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaAuthor.html")
    else:
        author = fk.request.form["author"]
        bookresults = db.booksDb.find({"author": author})
        if bookresults:
            reservedBook = db.reservedbooksDb.find_one({"author": author})

            if reservedBook is None:
                return fk.render_template("userSearchViaAuthor.html", book=bookresults)
        if bookresults is None:
            fk.flash("No book registrations found in the system.")
            return fk.redirect(fk.url_for("user.searchViaAuthor"))
        else:
            return fk.render_template("userSearchViaAuthor.html", book=bookresults)
        

# Search via ISBN      
@user.route("/search")
@user.route("/searchViaISBN", methods=["GET", "POST"])
def searchViaISBN():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaISBN.html")
    else:
        isbn = fk.request.form["isbn"]
        bookresults = db.booksDb.find({"isbn": isbn})
        if bookresults:
            reservedBook = db.reservedbooksDb.find_one({"isbn": isbn})

            if reservedBook is None:
                return fk.render_template("userSearchViaISBN.html", book=bookresults)
        if bookresults is None:
            fk.flash("No book registrations found in the system.")
            return fk.redirect(fk.url_for("user.searchViaISBN"))
        else:
            return fk.render_template("userSearchViaISBN.html", book=bookresults)


# Unbook flight
@user.route("/")
@user.route("/unbookFlight", methods=["GET","POST"])
def deleteFlight():
    if fk.request.method == "GET":
        with open("bookedflights.json", "r") as booked_flights_file:
            booked_flights_data = json.load(booked_flights_file)

        # Filter booked flights based on the user's email
        user_booked_flights = [flight for flight in booked_flights_data if flight["email"] == fk.session["email"]]
        
        return fk.render_template("unbookFlight.html", bookedFlights=user_booked_flights)
    else:
        flightid = fk.request.form["flightid"]
        with open("bookedflights.json", "r") as booked_flights_file:
            booked_flights_data = json.load(booked_flights_file)
        
        # Find the booked flight to unbook
        flight_to_unbook = next((flight for flight in booked_flights_data if flight["_id"] == flightid), None)
        if flight_to_unbook:
            with open("bookedflights.json", "w") as booked_flights_file:
                # Remove the flight from the booked flights data
                booked_flights_data.remove(flight_to_unbook)
                json.dump(booked_flights_data, booked_flights_file, indent=4)
            
            with open("flights.json", "r") as flights_file:
                flights_data = json.load(flights_file)

            # Find the corresponding flight in the flights data
            matching_flight = next((flight for flight in flights_data if flight["_id"] == flight_to_unbook["_id"]), None)
            if matching_flight:
                matching_flight["ticketsleftnum"] += 1
                if flight_to_unbook["tickettype"] == "economy":
                    matching_flight["econticketsleftnum"] += 1
                elif flight_to_unbook["tickettype"] == "business":
                    matching_flight["busticketsleftnum"] += 1
                
                with open("flights.json", "w") as flights_file:
                    json.dump(flights_data, flights_file, indent=4)
                
                fk.flash("Flight successfully unbooked!")
            else:
                fk.flash("Flight not found!")
        else:
            fk.flash("There is no flight with such ID.")
        
        return fk.redirect(fk.url_for("user.userHomePage"))

#bookedFlight
@user.route("/")
@user.route("/bookedFlights", methods=["GET","POST"])
def userHPage():
    if fk.request.method == "GET":
        allBookedFlights = bookedflightsDb.find({"email":fk.session["email"]})
        return fk.render_template("userBookedFlights.html", userEmail = fk.session["email"], bookedflights = allBookedFlights)
    else:
        allBookedFlights = bookedflightsDb.find({"email":fk.session["email"]})
        return fk.render_template("userBookedFlights.html", userEmail = fk.session["email"], bookedflights = allBookedFlights)

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

