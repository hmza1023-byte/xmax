from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# جدول المستخدمين
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("index.html")

# تسجيل
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "المستخدم موجود"

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

# تسجيل دخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            session["user"] = user.username
            if user.username == "admin":
                session["admin"] = True
            return redirect("/dashboard")

        return "خطأ في البيانات"

    return render_template("login.html")

# لوحة التحكم
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"])

# أدمن
@app.route("/admin")
def admin():
    if "admin" in session:
        users = User.query.all()
        return render_template("admin.html", users=users)
    return "🚫 ليس لديك صلاحية"

# تسجيل خروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# تشغيل
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
