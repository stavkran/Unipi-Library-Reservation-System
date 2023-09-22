# unipiLibrary

Υπηρεσία ψηφιακής πύλης της δανειστικής βιβλιοθήκης του Πανεπιστημίου Πειραιώς-Unipi Library

## Περιεχόμενα
* [Σύστημα](#Το-σύστημα)
* [Βάση](#Η-βάση)
* [Εγκατάσταση και εκτέλεση](#Εγκατάσταση-και-εκτέλεση)
* [Λειτουργίες Συστήματος](#Λειτουργίες-Συστήματος)
  * [Authentication](#Authentication)
  * [User](#User)
  * [Administrator](#Administrator)

## Το σύστημα
Το πληροφοριακό σύστημα, το οποίο παρέχει την υπηρεσία unpiLibrary, αποτελείται από 2 container.
Στο ένα περιέχεται η βάση δεδομένων (mongoDb), ενώ στο άλλο η υπηρεσία. Η υλοποίηση των services αυτών γίνεται με python, χρησιμοποιώντας εργαλεία flask και pymongo για την υλοποίηση της web-εφαρμογής και της επικοινωνίας με τη βάση αντίστοιχα. Για τη δημιουργία των interfaces χρησιμοποιήθηκε HTML και CSS.

## Database
Χρησιμοποιούνται 3 collections σε μια βάση MongoDb με την εξής δομή:
* Το πρώτο collection ονομάζεται users και περιέχει όλες τις πληροφορίες ενός χρήστη.

users:

| firstname    | surname    | email       | mobile      | password    | dateofbirth     | category   | 
| ----------- | ----------- | ----------- | ----------- | ----------- | --------------- | ---------- |
| string      | string      | string      | string      | string      | Date            | string     | 


* To δεύτερο collection ονομάζεται books και περιέχει όλα τα βιβλία που είναι καταχωρημένα στο σύστημα της βιβλιοθήκης.

books:

| title    | author   | publicationdate       | isbn     | summary | pagesnum | reservationdays |
| -------- | -------- | --------------------- | -------- | ------- | -------- | --------------- | 
| string   | string   | string                | string   | string  | int      | int             |

* To τρίτο collection ονομάζεται reservedbooks και περιέχει όλα τις κρατήσεις βιβλίων που έχουν γίνει και είναι καταχωρημένες στο σύστημα.

reservedbooks:

| Title            | Author         | ISBN             | User                                   | Reservation                        |
|------------------|----------------|------------------|----------------------------------------|------------------------------------|
| string           | string         | string           | object                                 | object                             |

*Τα user και reservation έχουν τα στοιχεία του χρήστη που έχει δανειστεί το βιβλίο και της ημερομηνίας κράτησης και επιστροφής αντιστοίχως.

user:

| User                                   |
|----------------------------------------|
| firstname | surname | email   | mobile | 
|-----------|---- ----|---------|--------|
| string    | string  | string  | string |
 
 *Κατα την εκτέλεση δημιουργείται ο λογαριασμός ενός διαχειριστή με στοιχεία firstname: Admin, surname: User, email: admin@email.com, password: admin, dateofbirth: 2001-07-13, countryoforigin: Greece, passportid: e19074 και category: admin. Επίσης δημιουργείτε ο λογαριασμός ενός απλού χρήστη με στοιχεία firstname: Vincent, surname: Peters, email: vin@email.com, password: 12345, dateofbirth: 2000-04-27, countryoforigin: Denmark, passportid: e18080 και category: user.*

## Εγκατάσταση και εκτέλεση

Η εγκατάσταση και εκτέλεση του συστήματος γίνεται με τα παρακάτω βήματα*:

1. Clone αυτού του repository τοπικά.
2. Εκτέλεση της παρακάτω εντολής στο local directory που αποθηκεύτηκε το repository:

```bash
sudo docker-compose up --build
```
 *Βασική προϋπόθεση να υπάρχει εγκατεστημένη έκδοση docker*

## Λειτουργίες Συστήματος

##  Authentication

### SignIn Page
Η σελίδα σύνδεσης είναι η πρώτη σελίδα που θα εμφανιστεί σε κάθε χρήστη μόλις συνδεθεί στη διεύθυνση '[0.0.0.0:5000](http://127.0.0.1:5000/)'.
Σε αυτή τη σελίδα ένας ήδη καταχωρημένος χρήστης μπορεί να κάνει εισαγωγή στην εφαρμογή εισάγωντας το email του και password.
Σε περίπτωση που κάποιος νέος χρήστης δεν έχει λογαριασμό του, μπορεί να μεταβεί στην 'SignUp' σελίδα για να δημιουργήσει νέο λογαριασμό.

<img src="./DigitalAirlinesimgs/signInPage.png" width="512">

### SignUp Page
Στη σελίδα εγγραφής ο χρήστης μπορεί να δημιουργήσει έναν νέο λογαριασμό για να μπορέσει να εισέλθει στην εφαρμογή.
Δε μπορεί να δημιουργήσει λογαριασμό με email ή passportid που είναι ήδη κατωχηρωμένα στο σύστημα.

<img src="./DigitalAirlinesimgs/signUpPage.png" width="512">
<img src="./DigitalAirlinesimgs/signUpNewUserPage.png" width="512">

## User
### Homepage
Ένας εγγεγραμμένος χρήστης αφού εισάγει επιτυχώς τα στοιχεία του και εισέλθει στην υπηρεσία θα μεταφερθεί αυτόματα στην κύρια σελίδα στην οποία μπορεί να δει όλες τις διαθέσιμες πτήσεις που υπάρχουν καταχωρημένες στο σύστημα.
Μέσω του Navigation Bar μπορεί να περιηγηθεί στις λειτουργίες που παρέχει η υπηρεσία.

<img src="./DigitalAirlinesimgs/userHomePage.png" width="512">

### Κράτηση Πτήσης
Σε αυτή τη σελίδα ο χρήστης μπορεί να κάνει κράτηση εισητηρίου σε μια πτήση εισάγοντας το μοναδικό κωδικό της πτήσης που επιθυμεί καθώς και τον τύπο του εισιτηρίου *economy/business*.

*(Τα προσωπικά του στοιχεία που απαιτούνται για την κράτηση, παίρνονται αυτόματα από τον λογαριασμό του χρήστη και δεν έχει δικαίωμα να τα επεξεργαστεί)*

<img src="./DigitalAirlinesimgs/userBookFlightPage.png" width="512">

### Ακύρωση Κράτησης
Σε αυτή τη σελίδα ο χρήστης μπορεί να ακυρώση μία κράτηση που έχει κάνει εισάγωντας το μοναδικό κωδικό της κράτησης.
*Στο κάτω μέρος της οθόνης εμφανίζονται οι κρατήσεις του χρήστη ώστε να μπορεί να βρει το μοναδικό κωδικό αυτής που επιθυμεί.*

<img src="./DigitalAirlinesimgs/userCancelFlightPage.png" width="512">

### Εμφάνιση Κρατήσεων Χρήστη
Σε αυτή τη σελίδα εμφανίζονται όλες οι κρατήσεις που έχει κάνει ο συγκεκριμένος χρήστης.

<img src="./DigitalAirlinesimgs/userBookedFlightsPage.png" width="512">

### Διαγραφή λογαριασμού
Ο χρήστης μπορείνα διαγράψει το λογαριασμό του. Ωστόσο οποιαδήποτε κράτηση έχει κάνει θα παραμείνει στο σύστημα.
Έπειτα ο χρήστης θα μεταφέρεται στη σελίδα εγγραφής σε περίπτωση που θέλει να δημιουργήσει νέο λογαριασμό.

<img src="./DigitalAirlinesimgs/userDeleteAccountPage.png" width="512">

### Αναζήτηση σημείωσης μέσω Αεροδρομίου Προέλευσης και Προρισμού 
Ο χρήστης να κάνει αναζήτηση μιας πτήσης βάση του Αεροδρομίου Προέλευσης και Προορισμού.

<img src="./DigitalAirlinesimgs/userSearchOriginDestPageNoResults.png" width="512">
<img src="./DigitalAirlinesimgs/userSearchOriginDestPageResults.png" width="512">

### Αναζήτηση σημείωσης μέσω Αεροδρομίου Προέλευσης και Προρισμού και ημερομηνίας αναχώρησης. 
Ο χρήστης να κάνει αναζήτηση μιας πτήσης βάση του Αεροδρομίου Προέλευσης και Προορισμού και της ημερομηνίας αναχώρησης.

<img src="./DigitalAirlinesimgs/userSearchOriginDestDatePage.png" width="512">

### Αναζήτηση σημείωσης μέσω ημερομηνίας αναχώρησης. 
Ο χρήστης να κάνει αναζήτηση μιας πτήσης βάση ημερομηνίας αναχώρησης.

<img src="./DigitalAirlinesimgs/userSearchDatePage.png" width="512">

## Administrator

### Home page
Αν κάποιος εισέλθει στο σύστημα ως διαχειριστής μεταφέρεται στο αντίστοιχο Homepage.
Μέσω του Navigation Bar μπορεί να περιηγηθεί στις λειτουργίες που παρέχει η υπηρεσία.

<img src="./DigitalAirlinesimgs/adminHomePage.png" width="512">


### Δημιουργία Πτήσης
Σε αυτή τη σελίδα ο χρήστης μπορεί να δημιουργήσει μια πτήση εισάγοντας τα παρακάτω στοιχεία:
Airport Of Origin, Airport Of Destination, Date (of Departure), Economy Tickets Number, Business Tickets Number, Economy Tickets Price, Business Tickets Price.

<img src="./DigitalAirlinesimgs/adminCreateFlight.png" width="512">

Για κάθε νέα πτήση δημιουργείται αυτόματα από το mongo ένα _id.
*(Το ίδιο ισχύει και κάθε φορά που γίνεται κράτηση από έναν απλό χρήστη)*

### Ενημέρωση τιμών εισιτηρίων 
Σε αυτή τη σελίδα ο διαχειριστής μπορεί να ανανεώνει τις τιμές των εισιτηρίων μιας πτήσης. Για να βρει τη πτήση που επιθυμεί θα συμπληρώσει τα παρακάτω στοιχεία: 
Airport Of Origin, Airport Of Destination, Date (Of Departure). Έπειτα θα συμπληρώσει τις νέες τιμές των εισιτηρίων. Ύστερα αν αυτή η πτήση βρεθεί στο σύστημα, θα ανανεωθούν οι τιμές των εισιτηρίων.

<img src="./DigitalAirlinesimgs/adminUpdateTicketPricesPage.png" width="512">

### Διαγραφή Πτήσης
Ένας διαχειριστής μπορεί να διαγράφει κάποια πτήση, πληκτρολογώντας το μοναδικό κωδικό της. Απαραίτητη προϋπόθεση είναι να μην έχει γίνει καμοία κράτηση για αυτή τη πτήση, αλλιώς η διαγραφή της δεν είναι δυνατή. 

<img src="./DigitalAirlinesimgs/adminDeleteFlightPage.png" width="512">

### Αναζήτηση σημείωσης μέσω Αεροδρομίου Προέλευσης και Προρισμού 
Ο χρήστης να κάνει αναζήτηση μιας πτήσης βάση του Αεροδρομίου Προέλευσης και Προορισμού.

<img src="./DigitalAirlinesimgs/UserSearchFlightDropdown.png" width="512">
<img src="./DigitalAirlinesimgs/userSearchOriginDestPageNoResults.png" width="512">
<img src="./DigitalAirlinesimgs/userSearchOriginDestPageResults.png" width="512">

### Αναζήτηση σημείωσης μέσω Αεροδρομίου Προέλευσης και Προρισμού και ημερομηνίας αναχώρησης. 
Ο χρήστης να κάνει αναζήτηση μιας πτήσης βάση του Αεροδρομίου Προέλευσης και Προορισμού και της ημερομηνίας αναχώρησης.

<img src="./DigitalAirlinesimgs/userSearchOriginDestDatePage.png" width="512">

### Αναζήτηση σημείωσης μέσω ημερομηνίας αναχώρησης. 
Ο χρήστης να κάνει αναζήτηση μιας πτήσης βάση ημερομηνίας αναχώρησης.

<img src="./DigitalAirlinesimgs/userSearchDatePage.png" width="512">

### Πληροφορίες Πτήσης
Αν ο χρήστης επιθυμεί να δει τις πληροφορίες μίας πτήσης, τότε σε αυτή τη σελίδα, θα εισάγει το μοναδικό κωδικό της πτήσης που επιθυμεί.

<img src="./DigitalAirlinesimgs/adminFlightDetailsByIDPage.png" width="512">
