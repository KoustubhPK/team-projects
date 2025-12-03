from flask import Flask, jsonify, request, redirect, render_template, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = 'secret-key'
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

jwt = JWTManager(app)


@app.route('/')
def home():
    return render_template("/auth/login.html")   # show login page


@app.route('/login', methods=['POST'])
def login():
    user_name = request.form.get("user_name")
    password = request.form.get("password")

    # ALWAYS compare with string
    if user_name == "test" and password == "12345":
        token = create_access_token(identity=user_name)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "token": token
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        })

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()

    return jsonify({
        "status": "success",
        "message": "Profile fetched successfully",
        "user": current_user
    })

@app.route('/profile_page')
def profile_page():
    return render_template("auth/profile.html")

if __name__ == "__main__":
    app.run(debug=True)

