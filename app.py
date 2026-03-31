from flask import Flask, render_template, request, redirect, session, jsonify
import os

app = Flask(__name__)
app.secret_key = "secret123"

# الصفحة الرئيسية ✅
@app.route("/")
def home():
    return render_template("dashboard.html")

# تسجيل دخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["admin"] = True
        return redirect("/admin")
    return render_template("login.html")

# تسجيل حساب
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# لوحة الأدمن
@app.route("/admin")
def admin():
    if "admin" in session:
        users = [{"username": "test1"}, {"username": "test2"}]
        return render_template("admin.html", users=users)
    return "❌ ممنوع"

# API
@app.route("/api/users")
def api_users():
    users = [{"username": "test1"}, {"username": "test2"}]
    return jsonify(users)

# تسجيل خروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# تشغيل السيرفر (مهم لـ Render)
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
