import os, hashlib,re

from flask import Flask, session
from flask_session import Session
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Make sure password and confirm password are same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirm password must be same", 403)

        user = request.form.get("username")
        passw = request.form.get("password")
        h = generate_password_hash(passw)
        # return redirect("/")
        # Inserting the values into db
        # db.execute("insert into users (?, ?)", (*request.form.get("username"),*request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES (:user, :hash)", {"user": user, "hash": h})
        db.commit()
        # Returning to login page
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",{"username": request.form.get("username")}).fetchone()
        # Ensure username exists and password is correct
        if not check_password_hash(rows[2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        if not request.form.get("search"):
            return apology("Enter something to search",404)

        search = request.form.get("search")
        tempRows = db.execute("SELECT * FROM books").fetchall()
        rows = []
        r=[]
        i=0
        ids = []
        for tempRow in tempRows:
            for row in tempRow:
                row = str(row)
                temp = tempRow[0]
                if search in row:
                    ids.append(temp)

        for id in ids:
            r = db.execute("SELECT isbn, title, author, releaseyear FROM books where book_id = :id", {"id":id}).fetchall()
            for t in r:
                rows.append(t)

        if not rows:
            return render_template("index.html", number = 0)

        return render_template("index.html", number = 1,rows=rows)

    else:
        return render_template("index.html")



# @app.route("/search/<int:search_id>")
# def flight(search_id):
    
@app.route("/book/<int:row_id>")
def search(row_id):
    return render_template("index.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)