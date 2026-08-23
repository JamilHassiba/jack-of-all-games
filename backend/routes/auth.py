"""Authentication routes: landing page, register, login, logout."""

import sqlite3

from flask import Blueprint, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import db
from registry import rooms

bp = Blueprint("auth", __name__)


@bp.route('/')
def home_page():
    # session.clear()                               # temporarily used for conn_test
    server_ip = request.host_url.rstrip("/")

    # player = session.get("player_obj")
    # if not player:
    #     return render_template("index.html")
    # else:
    #     redirect("/room")

    if "user_id" not in session:
        return redirect("/login")
    
    room_id = session.get("room")
    if room_id and room_id in rooms:
        return redirect("/room")
    else:
        session.pop("room", None)
        session.pop("player_index", None)
        session.pop("player_obj", None)
    return render_template("index.html", username=session.get("username"))

@bp.route("/register", methods=["GET", "POST"])
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
        
        return "", 200
    
    return render_template("register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    
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

@bp.route("/logout")
def logout():
    # clear session data on logout
    session.clear()
    return redirect("/login")

