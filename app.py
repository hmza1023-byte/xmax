from flask import Flask, render_template, request, redirect, session, jsonify
import os

app = Flask(__name__)
app.secret_key = "secret123"

# الصفحة الرئيسية
@app.route("/")
def home():
    return "App is working 🚀"

# تسجيل دخول بسيط
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect("/admin")
        else:
            return "❌ خطأ في تسجيل الدخول"

    return '''
    <form method="post">
        <input name="username" placeholder="username">
        <input name="password" placeholder="password" type="password">
        <button type="submit">Login</button>
    </form>
    '''

# صفحة الادمن
@app.route("/admin")
def admin():
    if "admin" in session:
        return "👑 Admin Page"
    return "❌ Access Denied"

# API
@app.route("/api/users")
def api_users():
    return jsonify([
        {"username": "admin"},
        {"username": "user1"}
    ])

# تسجيل خروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# تشغيل السيرفر (مهم جدا)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
