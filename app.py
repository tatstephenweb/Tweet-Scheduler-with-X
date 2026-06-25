from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import json, os, fitz
import re
from groq import Groq
from dotenv import load_dotenv
from db_helpers import create_user, verify_user, get_db_connection
import mysql.connector
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = "app_secret_key"


#congig mail
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mail = Mail(app)
serializer = URLSafeTimedSerializer('app_secret_key')


# ── Routes __
@app.route("/")
def load():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("auth-page-1.html")

@app.route("/create-account")
def create_account():
    return render_template("signup.html")

@app.route("/dashboard")
def result():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    
    user = {
        'email': session["email"],
        'username':session['user_name']
    }
    return render_template("dashboard.html",user=user)

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/check-email")
def check_email():
    return render_template("verify-email.html")

@app.route("/reset-password/<token>", methods=["GET","POST"])
def reset_password(token):
    errors = []
    try:
        email = serializer.loads(token, salt='password-reset', max_age=900)
    except SignatureExpired:
        errors.append("Reset Link has expired")
    except BadSignature:
        errors.append("Tempered token")
    
    return render_template("reset-password.html")

saved = []
@app.route("/verify", methods=["GET", "POST"])
def verify():
    errors = []
    if request.method == "POST":
        email = request.form.get("email")

        saved.append(email)
        errors.append(f"If {email} exists, a verification link will be sent. Check your email")

    #generate token with the user's email
    token = serializer.dumps(email, salt='password-reset')

    reset_url = f"http://localhost:5000/reset-password/{token}"

    msg = Message("Reset your Password", recipients=[email])        
    msg.html = f"""
        <h2>Passowrd reset link</h2>
        <p>Click the link below to reset your password</p>
        <a href="{reset_url}">Reset Passoword</a>
        <p>This link expires in 15 minutes</p>
    """

    mail.send(msg)

    return render_template("forgot-password.html", errors = errors)

        #check if email is in database

        #else append to error and display to user.



@app.route("/register-user", methods=["GET", "POST"])
def register_user():
    errors = []

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = (request.form.get("password") or "").strip()

        if len(password) < 8:
            errors.append("Password must be 8 or more characters")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            errors.append("This email already has an account")

        if not errors:
            try:
                session["email"] = email
                session["name"] = name
                session["password"] = password

                #generate token with the user's email
                #token = serializer.dumps(email, salt='verify-new-user')

                # Encode all 3 values in the token
                token = serializer.dumps(
                    {"email": email, "name": name, "password": password},
                    salt='verify-new-user'
                )

                verify_url = f"http://localhost:5000/verify-new-user/{token}"  # pass token in URL

                msg = Message("Signup verification Link", recipients=[email])        
                msg.html = f"""
                    <h2>Verify your Email</h2>
                    <p>Click the link below to verify your email and register you.</p>
                    <a href="{verify_url}">Verify email</a>
                    <p>This link expires in 15 minutes</p>
                """

                mail.send(msg)
               # return redirect(url_for("login"))

                return redirect(url_for("check_email"))
            
            #except mysql.connector.IntegrityError:
            except (mysql.connector.IntegrityError, Exception) as e:
                errors.append("An error occured")
            
    
    return render_template("signup.html", errors = errors)

@app.route("/verify-new-user/<token>", methods=["GET","POST"])
def verify_new_user(token):
    errors = []
    try:
        #email = serializer.loads(token, salt='password-reset', max_age=900)
        data = serializer.loads(token, salt='verify-new-user', max_age=900)

        name = data["name"]
        email = data["email"]
        password = data["password"]

        create_user(name, email, password)

        return redirect(url_for("login"))
    
    except SignatureExpired:
        errors.append("Reset Link has expired")
    except BadSignature:
        errors.append("Tempered token")

    return render_template("signup.html", errors = errors)


@app.route("/new-password", methods=["GET","POST"])
def new_password():
    g_email = saved[-1]
    errors =[]
    if request.method == "POST":
        email = g_email
        new_pass = request.form["password"]

        if len(new_pass) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not errors:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)

                query = ("SELECT * FROM users where email = %s")
                cursor.execute(query, (email,))
                user = cursor.fetchone()


                if user:
                    new_hash_pass = generate_password_hash(new_pass)
                    
                    query = "UPDATE users SET password_hash = %s WHERE email = %s"
                    cursor.execute(query, (new_hash_pass, email))

                    conn.commit()

                    cursor.close()
                    conn.close()
                    return redirect(url_for("login"))
                else:
                    errors.append("This email does not have an account. Please sign up")
                    return render_template("reset-password.html", errors = errors)

            except mysql.connector.IntegrityError:
                errors.append("This email does not exist")

    return render_template("reset-password.html", errors = errors)

@app.route("/login-user", methods=["GET", "POST"])
def login_user():
    errors = []
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print("hello")
        user = verify_user(email, password)
        print(user)

        if user:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["user_name"] = user["name"]
            print(session["user_id"])
            print(session["email"])

            return redirect(url_for("result"))
        else:
            errors.append("Invalid email or password")
            print(errors)
    
    #return redirect(url_for("login"))
    return render_template("auth-page-1.html", errors = errors)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)