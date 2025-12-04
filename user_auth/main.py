
from datetime import timedelta
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify, redirect, flash, make_response, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request

app = Flask(__name__)
app.secret_key = "yoursecret"

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # True if using HTTPS
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017')
db = client['test_flask_db']
user_table = db['auth_table']

# Frontend Routes
@app.route('/')
def home():
    return redirect('/login_page')

@app.route('/register_page')
def register_page():
    try:
        verify_jwt_in_request(optional=True)
        user = get_jwt_identity()
        if user:
            return redirect('/profile_page')
    except:
        pass

    return render_template('auth/register.html')

@app.route('/login_page')
def login_page():
    try:
        verify_jwt_in_request(optional=True)
        user = get_jwt_identity()
        if user:
            return redirect('/profile_page')
    except:
        pass

    return render_template('auth/login.html')

@app.route('/profile_page')
@jwt_required()
def profile_page():
    user_id = get_jwt_identity()
    user = user_table.find_one({'_id': ObjectId(user_id)})
    if not user:
        return "User not found", 404
    login_success = request.args.get("login") == "success"
    return render_template('auth/profile.html', username=user['username'], email=user['email'], login_success=login_success)

@app.route('/logout')
def logout():
    response = make_response(redirect('/login_page'))
    unset_jwt_cookies(response)
    return response

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if user_table.find_one({'email': email}):
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_id = user_table.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password
    }).inserted_id

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Find user
    user = user_table.find_one({'email': email})
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    # Validate password
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Create JWT token
    access_token = create_access_token(identity=str(user['_id']))

    # Store username/email in session for navbar
    session['username'] = user.get('username') or user.get('email')

    # Create response object
    response = jsonify({'message': 'Login successful'})

    # Set token in secure cookie
    set_access_cookies(response, access_token)

    # Flash success message (will show only once on profile page)
    flash("Login successful!", "success")

    return response, 200

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = user_table.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'username': user['username'],
        'email': user['email']
    }), 200

@app.context_processor
def inject_user():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            user = user_table.find_one({"_id": ObjectId(user_id)})
            if user:
                return {"current_user": user}
    except:
        pass
    return {"current_user": None}

if __name__ == '__main__':
    app.run(debug=True)
