import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    owned_stocks_db1 = db.execute(
        "SELECT symbol FROM data WHERE user_id = ? GROUP BY symbol", session["user_id"]
    )
    for stock1 in range(len(owned_stocks_db1)):
        current_price = lookup(owned_stocks_db1[stock1]["symbol"])["price"]
        db.execute(
            "UPDATE data SET current_price = ? WHERE user_id = ? AND symbol = ?",
            current_price,
            session["user_id"],
            owned_stocks_db1[stock1]["symbol"],
        )

    owned_stocks_db = db.execute(
        "SELECT symbol, SUM(shares) AS shares, current_price FROM data WHERE user_id = ? GROUP BY symbol",
        session["user_id"],
    )
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash_db[0]["cash"]
    owned_stocks_price = 0
    for stock in range(len(owned_stocks_db)):
        owned_stocks_price += lookup(owned_stocks_db[stock]["symbol"])["price"] * int(
            owned_stocks_db[stock]["shares"]
        )

    grand_tot = cash + owned_stocks_price
    db.execute(
        "UPDATE users SET grand_total = ? WHERE id = ?", grand_tot, session["user_id"]
    )

    return render_template(
        "portofilio.html",
        owned_stocks=owned_stocks_db,
        cash1=cash,
        grand_tot1=grand_tot,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure symbol was valid
        if lookup(request.form.get("symbol").upper()) == None:
            return apology("Symbol doesn't exist", 400)

        # Ensure number of shares was valid
        if not int(request.form.get("shares")) > 0:
            return apology("Invalid number of shares", 400)

        price = lookup(request.form.get("symbol").upper())["price"]
        amount_db = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        amount = amount_db[0]["cash"]

        # Ensure if the user can afford the stock
        if int(request.form.get("shares")) * price > amount:
            return apology("Can't afford the number of shares demanded", 400)

        id = session["user_id"]
        username_db = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        username = username_db[0]["username"]
        shares = request.form.get("shares")
        symbol = request.form.get("symbol").upper()
        time = datetime.datetime.now()
        tot_transaction = int(request.form.get("shares")) * price
        cash = amount - tot_transaction

        db.execute(
            "INSERT INTO data (user_id, username, shares, symbol, price, total_transaction, time) VALUES(?, ?, ?, ?, ?, ?, ?)",
            id,
            username,
            shares,
            symbol,
            price,
            tot_transaction,
            time,
        )

        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
        flash("Bought!")

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    owned_stocks_db = db.execute(
        "SELECT symbol, shares, price, time FROM data WHERE user_id = ?",
        session["user_id"],
    )
    history1 = len(owned_stocks_db)
    return render_template(
        "history.html", owned_stocks=owned_stocks_db, history=history1
    )

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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure symbol was valid
        if lookup(request.form.get("symbol").upper()) == None:
            return apology("Symbol doesn't exist", 400)

        # direct user to Quoted result
        stock1 = lookup(request.form.get("symbol").upper())
        return render_template("quoteresult.html", stock=stock1)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was given
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password was confirmed
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("password not confirmed", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 0:
            return apology("invalid username and/or password", 400)

        # Add the user into the database
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        rows1 = db.execute(
            "SELECT id FROM users WHERE username = ?", request.form.get("username")
        )

        # Remember which user has logged in
        session["user_id"] = rows1[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registration.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("gsymbol"):
            return apology("must provide symbol", 403)

        # Ensure symbol was valid
        if lookup(request.form.get("gsymbol").upper()) == None:
            return apology("Symbol doesn't exist", 403)

        # Ensure shares was valid
        if int(request.form.get("shares")) <= 0:
            return apology("Shares not valid", 403)

        shares = db.execute(
            "SELECT SUM(shares) AS shares FROM data WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            session["user_id"],
            request.form.get("gsymbol").upper(),
        )
        # Ensure number of shares was valid
        if int(request.form.get("shares")) > shares[0]["shares"]:
            return apology("Unavailable number of shares", 403)

        price = lookup(request.form.get("gsymbol").upper())["price"]
        amount_db = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        amount = amount_db[0]["cash"]

        id = session["user_id"]
        username_db = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        username = username_db[0]["username"]
        shares = -int(request.form.get("shares"))
        symbol = request.form.get("gsymbol").upper()
        time = datetime.datetime.now()
        tot_transaction = int(request.form.get("shares")) * price
        cash = amount + tot_transaction

        db.execute(
            "INSERT INTO data (user_id, username, shares, symbol, price, total_transaction, time) VALUES(?, ?, ?, ?, ?, ?, ?)",
            id,
            username,
            shares,
            symbol,
            price,
            tot_transaction,
            time,
        )

        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        flash("Sold!")

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        owned_stocks_db = db.execute(
            "SELECT symbol, SUM(shares) AS shares FROM data WHERE user_id = ? GROUP BY symbol",
            session["user_id"],
        )
        return render_template("sell.html", owned_stocks=owned_stocks_db)
