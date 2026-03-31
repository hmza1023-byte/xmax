from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secret123"

# قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# رفع الصور
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# حماية من التخمين
login_attempts = {}

def is_blocked(ip):
    return login_attempts.get(ip, 0) >= 5

# جدول المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    image = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# تسجيل دخول
@app.route("/", methods=["GET", "POST"])
def login():
    ip = request.remote_addr

    if is_blocked(ip):
        return "🚫 تم حظرك مؤقتاً"

    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user"] = user.username
            session["admin"] = user.is_admin
            login_attempts[ip] = 0
            return redirect("/dashboard")
        else:
            login_attempts[ip] = login_attempts.get(ip, 0) + 1
            return "❌ خطأ"

    return render_template("login.html")

# تسجيل حساب
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        file = request.files["image"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        is_admin = False
        if User.query.count() == 0:
            is_admin = True

        user = User(username=username, password=password, image=filename, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")

# داشبورد
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        user = User.query.filter_by(username=session["user"]).first()
        return render_template("dashboard.html", user=user)
    return redirect("/")

# لوحة الادمن
@app.route("/admin")
def admin():
    if "admin" in session and session["admin"]:
        users = User.query.all()
        return render_template("admin.html", users=users)
    return "🚫 ممنوع"

# API
@app.route("/api/users")
def api_users():
    users = User.query.all()
    return jsonify([{"username": u.username} for u in users])

# خروج
@app.route("/logout")
def logout

import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
