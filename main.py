import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
from hashlib import sha256,blake2b
import json
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database='slotBooking'
)
db = mydb.cursor(dictionary=True,buffered=  True)
headers = {
    'Access-Control-Allow-Origin': '*'
}
app = Flask(__name__)
# run_with_ngrok(app)
CORS(app, resources={r"/*": {"origins": "*"}})



@app.route('/', methods=['POST', "GET"])
def home():
    return jsonify({'status': 200, 'message': "SWAGAT H AAPKA SHREEMATI CHIRAG MAHODAYA"})



@app.route('/addCampaign', methods=['POST'])
def addCampaign():
    data = request.get_json()
    users = data['users']
    slots = data['slots']
    with open('data.json', 'r') as f:
        inf = json.load(f)
        if inf["campaign"]:
            return jsonify({"message": "Campaign already exists.\n Please Reset it before updating new data", 'status': 201})
    
    for user in users:
        # try:
        #     db.execute("select * from users where email=%s", (user["email"],))
        #     if db.fetchone():
        #         continue
        #         return jsonify({"message": "User with email:"+user["email"]+" already exists", 'status': 201})
        #     db.execute("INSERT INTO users (name,email,mobile,rollnumber,branch,year) VALUES (%s,%s)",
        #             (user["name"],user["email"], user["mobile"],user["rollnumber"],user["branch"],user["year"]))
        # except:
        #     return jsonify({"message": "Issue adding the User with email:"+user["email"], 'status': 201})
        db.execute("select * from users where email=%s", (user["email"],))
        if db.fetchone():
            continue
            return jsonify({"message": "User with email:"+user["email"]+" already exists", 'status': 201})
        db.execute("INSERT INTO users (name,email,mobile,rollnumber,branch,year) VALUES (%s,%s)",
                (user["name"],user["email"], user["mobile"],user["rollnumber"],user["branch"],user["year"]))
        mydb.commit()

    for slot in slots:
        try:
            db.execute("INSERT INTO slots (startTime,endTime,available) VALUES (%s,%s)",
                   (slot["startTime"], slot["endTime"], slot["available"]))
        except:
            return jsonify({"message": "Issue adding the Slot with at time:"+slot["startTime"], 'status': 201})
        mydb.commit()
    with open('data.json', 'w') as f:
        f.write(jsonify({"campaign": True}))
    
    return jsonify({"data": user["uid"], 'status': 200})

@app.route('/initiateCampaign', methods=['POST'])
def initiateCampaign():
    return jsonify({"data": "Left to be completed", 'status': 200})


@app.route('/resetCampaign', methods=['POST'])
def resetCampaign():

    data = request.get_json()

    if data["password"] == "Manan_technosurge_slots_2023":
        db.execute("DELETE FROM users")
        
        db.execute("DELETE FROM slots")
        db.execute("DELETE FROM bookings")
        mydb.commit()
        
        with open('data.json', 'w') as f:
            json.dump({"campaign": False}, f)
        return jsonify({"data": "Campaign Reset", 'status': 200})
    
    return jsonify({"data": "Its a Deja Vu!!!", 'status': 404})


@app.route('/getAllUsers', methods=['GET'])
def getAllUsers():
    
    db.execute("SELECT * FROM users")
    users = db.fetchall()
    if not(users):
        return jsonify({'status': 201, 'message': "Table is empty or doesn't exist"})
    return jsonify({'status': 200, 'data': users})

@app.route('/getAllSlots', methods=['GET'])
def getAllSlots():
    db.execute("SELECT * FROM slots")
    slots = db.fetchall()
    if not(slots):
        return jsonify({'status': 201, 'message': "Table is empty or doesn't exist"})
    return jsonify({'status': 200, 'data': slots})


@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data['email']
    db.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = db.fetchone()
    if not(user):
        return jsonify({'status': 201, 'message': "User doesn't exist"})
    else:
        if db["bookStatus"]:
            return jsonify({'status': 201, 'message': "User already verified"})
        #generate hash
        hsh = blake2b(sha256(sha256((email+"Manan2023").encode('utf-8')).hexdigest().encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()

        # db.execute("update users set hash=%s where email=%s", (hsh, email))
        db.execute("update users set hash=%s where email=%s", (hsh, email))
        mydb.commit()

        #send mail to the user

        return jsonify({'status': 200, 'message': "User verified","hash":hsh})  
    
@app.route('/bookSlot', methods=['POST'])
def bookSlot():
    data = request.get_json()
    hsh,slotid = data['hash'],data['slotid']
    db.execute("SELECT id FROM users WHERE hash=%s", (hsh))
    userid = db.fetchone()
    if userid:
        db.execute("SELECT * FROM slots WHERE id=%s", (slotid))
        slot = db.fetchone()
        if slot:
            if slot['available'] == 0:
                return jsonify({'status': 201, 'message': "Slot not available"})
            else:
                db.execute("INSERT INTO bookings (userid,slotid) VALUES (%s,%s)", (userid,slotid))
                db.execute("UPDATE slots SET available=available-1 WHERE id=%s", (slotid))
                mydb.commit()
                db.execute("UPDATE users SET bookStatus=1 WHERE id=%s", (userid))
                return jsonify({'status': 200, 'message': "Slot booked"})
        else:
            return jsonify({'status': 201, 'message': "Slot doesn't exist"})
    else:
        return jsonify({'status': 202, 'message': "User doesn't exist"})
    

@app.route('/checkBooking', methods=['POST'])
def checkBooking():
    data = request.get_json()
    hsh = data['hash']
    db.execute("SELECT id FROM users WHERE hash=%s", (hsh))
    userid = db.fetchone()
    if userid:
        db.execute("SELECT * FROM bookings WHERE userid=%s", (userid))
        booking = db.fetchone()
        if booking:
            return jsonify({'status': 201, 'message': "Slot already booked!"})
        else:
            return jsonify({'status': 200, 'message': "Slot not booked"})
    else:
        return jsonify({'status': 202, 'message': "User doesn't exist"})



app.run(debug=True)