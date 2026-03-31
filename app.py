from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    balance = db.Column(db.Float, default=1000)
    btc = db.Column(db.Float, default=0)
    eth = db.Column(db.Float, default=0)

# العمليات
class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    coin = db.Column(db.String(10))
    amount = db.Column(db.Float)
    type = db.Column(db.String(10))

# اسعار حقيقية
def get_prices():
    try:
        data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd").json()
        return {
            "btc": data["bitcoin"]["usd"],
            "eth": data["ethereum"]["usd"]
        }
    except:
        return {"btc": 30000, "eth": 2000}

# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("index.html")

# تسجيل
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        user = User(username=request.form["username"],
                    password=request.form["password"])
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

# دخول
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            session["user"] = user.username
            return redirect("/dashboard")

    return render_template("login.html")

# داشبورد
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(username=session["user"]).first()
    trades = Trade.query.filter_by(username=user.username).all()
    prices = get_prices()

    return render_template("dashboard.html",
                           user=user,
                           prices=prices,
                           trades=trades)

# تداول
@app.route("/trade", methods=["POST"])
def trade():
    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(username=session["user"]).first()

    coin = request.form["coin"]
    amount = float(request.form["amount"])
    action = request.form["action"]

    prices = get_prices()
    price = prices[coin]

    if action == "buy":
        cost = amount * price
        if user.balance >= cost:
            user.balance -= cost
            setattr(user, coin, getattr(user, coin) + amount)

    elif action == "sell":
        if getattr(user, coin) >= amount:
            user.balance += amount * price
            setattr(user, coin, getattr(user, coin) - amount)

    db.session.add(Trade(username=user.username, coin=coin, amount=amount, type=action))
    db.session.commit()

    return redirect("/dashboard")

# 👑 ادمن
@app.route("/admin")
def admin():
    if "user" not in session or session["user"] != "admin":
        return "🚫 ممنوع"

    users = User.query.all()
    total = sum([u.balance for u in users])

    return render_template("admin.html", users=users, total=total)

# إضافة رصيد
@app.route("/add_balance", methods=["POST"])
def add_balance():
    if "user" not in session or session["user"] != "admin":
        return "🚫"

    user = User.query.filter_by(username=request.form["username"]).first()
    if user:
        user.balance += float(request.form["amount"])
        db.session.commit()

    return redirect("/admin")

# حذف
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session or session["user"] != "admin":
        return "🚫"

    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect("/admin")

# خروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

with app.app_context():
    db.create_all()

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
