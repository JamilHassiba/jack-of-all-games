from flask import Flask, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "jack_of_all_games_secret_key"
# need a secret key for the session retained data

def db():
    # best way to operate on db with sqlite
    conn = sqlite3.connect("../users.db")
    conn.row_factory = sqlite3.Row
    return conn

with db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # creates user table if it doesnt exist

@app.route('/')
def home_page():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # password validation (can add more strict requirements later)
        if len(username) < 3 or len(password) < 8:
            return "Username or password is invalid length", 400
        
        #generate hash and register to DB
        pw_hash = generate_password_hash(password)
        try:
            with db() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pw_hash)
                )
        
        # except if user exists alredy
        except sqlite3.IntegrityError:
            return "User already exists", 400
        
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/client")
    
    if request.method == "POST": 
        username = request.form["username"]
        password = request.form["password"]

        # get user and hash from db
        with db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            # if user doesnt exist or wrong password
            if not user or not check_password_hash(user["password_hash"], password):
                return "Invalid username or password", 401
            
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        # retain info for session and redirect to game
        return "", 200
    
    return render_template("login.html")

@app.route("/client")
def client():
    # if user not logged in go to login page
    if "user_id" not in session:
        return redirect("/login")
    
    return render_template("client.html")

@app.route("/logout")
def logout():
    # clear session data on logout
    session.clear()
    return redirect("/login")

if __name__ == '__main__': 
    app.run(debug=True)