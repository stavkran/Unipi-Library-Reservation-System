import flask as fk
import pymongo as pm
import re
from datetime import date
from pymongo import MongoClient
import json

#User blueprint
user = fk.Blueprint("user", __name__, static_folder="static", template_folder="templates")

#Connect to mongodb
client = MongoClient("mongodb://mongodb:27017/")
db = client["UnipiLibrary"]
usersDb = db["users"]
booksDb = db["books"]
reservedDb = db["reservedbooks"]

# User's home page which also shows all the unreserved books.
@user.route("/")
@user.route("/userAvailableFlights", methods=["GET"])
def userHomePage():
    all_flights = booksDb.find({"ticketsleftnum": {"$gt": 0}})
    return fk.render_template("availableFlights.html", flights = all_flights)
    
# Book a flight
@user.route("/")
@user.route("/bookFlight", methods=["GET","POST"])
def bookFlight():
    if fk.request.method == "GET":
        # Get the user's information from the user JSON file
        with open("users.json", "r") as users_file:
            users_data = json.load(users_file)
        
        # Find the user based on their email (assuming email is used as a unique identifier)
        signed_in_user = next((user for user in users_data if user["email"] == fk.session["email"]), None)
        
        if signed_in_user:
            return fk.render_template("bookFlight.html", user=signed_in_user)
        else:
            fk.flash("User not found!")
            return fk.redirect(fk.url_for("user.bookFlight"))
    else:
        #request values
        flightid = fk.request.form["flightid"]
        firstname = fk.request.form["firstname"]
        surname = fk.request.form["surname"]
        passportid = fk.request.form["passportid"]
        dateofbirth = fk.request.form["dateofbirth"]
        email = fk.request.form["email"]
        tickettype = fk.request.form["tickettype"]

        # bookedflights = {"email":fk.session["email"], "firstnamebooker": firstname, "surnamebooker": surname, "passportidbooker": paassportid, "dateofbirthbooker": dateofbirth, "emailbooker": email, "tickettypebooker": tickettype}
        # bookedflightsDb.insert_one(bookedflights)
        # fk.flash("Flight booked Successfully!")
        # return fk.redirect(fk.url_for("user.userHomePage"))

        with open("flights.json", "r") as flights_file:
            flights_data = json.load(flights_file)

        # Find the flight based on the _id
        matching_flights = [flight for flight in flights_data if flight["_id"] == flightid]
        if matching_flights:
            matched_flight = matching_flights[0]
            booked_flight = {
                "_id": matched_flight["_id"],
                "airportoforigin": matched_flight["airportoforigin"],
                "airportfinaldest": matched_flight["airportfinaldest"],
                "date": matched_flight["date"],
                "firstname": firstname,
                "surname": surname,
                "passportid": passportid,
                "dateofbirth": dateofbirth,
                "email": email,
                "tickettype": tickettype
            }

            with open("bookedflights.json", "r") as booked_flights_file:
                    booked_flights = json.load(booked_flights_file)

            booked_flights.append(booked_flight)

            with open("bookedflights.json", "w") as booked_flights_file:
                json.dump(booked_flights, booked_flights_file, indent=4)

            matched_flight["ticketsleftnum"] -= 1
            if tickettype == "economy":
                matched_flight["econticketsleftnum"] -= 1
            elif tickettype == "business":
                matched_flight["busticketsleftnum"] -= 1

            with open("flights.json", "w") as flights_file:
                json.dump(flights_data, flights_file, indent=4)

            fk.flash("Flight booked successfully!")
            return fk.redirect(fk.url_for("user.userHomePage"))
        else:
            fk.flash("Flight not found!")
            return fk.redirect(fk.url_for("user.userHomePage"))
        
# Search via Airport Of Origin and Airport Of Destination
@user.route("/search")
@user.route("/searchViaOriginDest", methods=["GET", "POST"])
def searchViaOriginDest():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaOriginDest.html")
    else:
        airportoforigin = fk.request.form["airportoforigin"]
        airportfinaldest = fk.request.form["airportfinaldest"]
        results = flightsDb.find({
            "$and":[ 
                {"airportoforigin": airportoforigin}, 
                {"airportfinaldest": airportfinaldest},
                {"ticketsleftnum": {"$gt": 0}} 
            ]
        })
        if results is None:
            fk.flash("No flights found.")
            return fk.redirect(fk.url_for("user.searchViaOriginDest"))
        else:
            return fk.render_template("userSearchViaOriginDest.html", flights=results)
        
# Search via Airport Of Origin and Airport Of Destination and Date
@user.route("/search")
@user.route("/searchViaOriginDestDate", methods=["GET", "POST"])
def searchViaOriginDestDate():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaOriginDestDate.html")
    else:
        airportoforigin = fk.request.form["airportoforigin"]
        airportfinaldest = fk.request.form["airportfinaldest"]
        date = fk.request.form["date"]
        results = flightsDb.find({
            "$and":[ 
                {"airportoforigin": airportoforigin}, 
                {"airportfinaldest": airportfinaldest},
                {"date": date},
                {"ticketsleftnum": {"$gt": 0}} 
            ]
        })
        if results is None:
            fk.flash("No flights found.")
            return fk.redirect(fk.url_for("user.searchViaOriginDestDate"))
        else:
            return fk.render_template("userSearchViaOriginDestDate.html", flights=results)
        
# Search via Date
@user.route("/search")
@user.route("/searchViaDate", methods=["GET", "POST"])
def searchViaDate():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaDate.html")
    else:
        date = fk.request.form["date"]
        # Make a variable to catch all reuslts similar to title in case of wrong spelling.
        # like_airportoforigin = re.compile(f"[{airportoforigin}]")
        results = flightsDb.find({
            "$and":[ 
                {"date": date},
                {"ticketsleftnum": {"$gt": 0}} 
            ]
        })
        if results is None:
            fk.flash("No flights found.")
            return fk.redirect(fk.url_for("user.searchViaDate"))
        else:
            return fk.render_template("userSearchViaDate.html", flights=results)

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

