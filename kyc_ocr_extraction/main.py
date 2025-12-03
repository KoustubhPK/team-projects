import os, shutil
from pymongo import MongoClient
from ocr import ExtractPanData, ExtractAadhaarData
from flask import Flask, jsonify, render_template, request, redirect, flash, url_for, session

client = MongoClient('mongodb://localhost:27017')

db = client['test_flask_db']
user_table = db['user_table']

app = Flask(__name__)
app.secret_key = "abcd@123"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # POST request: validate login
    user_name = request.form.get("user_name")
    password = request.form.get("password")

    if not user_name or not password:
        flash("Please enter both email and password", "danger")
        return redirect(url_for("login"))

    # Fetch user
    user = user_table.find_one({"user_name": user_name})

    if user is None:
        flash("User not found! Please register first.", "danger")
        return redirect(url_for("login"))

    # Validate password
    if user["password"] != password:
        flash("Incorrect password!", "danger")
        return redirect(url_for("login"))

    # Login success → save session
    session["username"] = user["user_name"]
    session["email"] = user["email_id"]
    session["logged_in"] = True

    flash("Login successful!", "success")
    return redirect(url_for("home"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        email_id = request.form.get('email_id')
        contact_number = request.form.get('contact_number')
        dob = request.form.get('dob')

        # Check user existence
        response = user_table.find_one({
            "email_id": email_id,
            "contact_number": contact_number
        })

        if not response:
            user_table.insert_one({
                "email_id": email_id,
                "contact_number": contact_number,
                "user_name": user_name,
                "password": password,
                "dob": dob
            })

            return render_template("login.html", message="User registered successfully")

        else:
            return render_template("register.html", message="User Already Exists")

    return render_template('register.html')

@app.route('/aadhaar-data', methods=['GET', 'POST'])
def aadhaar_data():

    # GET:  just load empty page
    if request.method == "GET":
        return render_template("aadhaar-data.html", result=None)

    # POST: process extraction
    file = request.files.get('image_file')

    if not file:
        flash("Please upload an image", "danger")
        return redirect(url_for("dashboard"))

    # Save temporarily
    folder_name = "static/ocr"
    os.makedirs(folder_name, exist_ok=True)

    file_path = os.path.join(folder_name, file.filename)
    file.save(file_path)

    obj = ExtractAadhaarData(file_path, preprocess=True).get_aadhaar()
    
    result = {
        'aadhaar_number': obj[0],
        'dob': obj[1],
        'gender': obj[2],
    }
    os.remove(file_path)
    shutil.rmtree(r'result')

    return render_template("aadhaar-data.html", result=result)

@app.route('/pan-data', methods=['GET', 'POST'])
def pan_data():

    # GET:  just load empty page
    if request.method == "GET":
        return render_template("pan-data.html", result=None)

    # POST: process extraction
    file = request.files.get('image_file')

    if not file:
        flash("Please upload an image", "danger")
        return redirect(url_for("dashboard"))

    # Save temporarily
    folder_name = "static/ocr"
    os.makedirs(folder_name, exist_ok=True)

    file_path = os.path.join(folder_name, file.filename)
    file.save(file_path)

    obj = ExtractPanData(file_path, preprocess=True).get_pan()
    
    result = {
        'pan_number': obj[0],
        'dob': obj[1]
    }

    os.remove(file_path)
    shutil.rmtree(r'result')

    return render_template("pan-data.html", result=result)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)