from flask import Flask, render_template, request, redirect, session, flash
import pandas as pd
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ali_sabea_secret_key"

EXCEL_FILE = "Book1.xlsx"
DEFAULT_PASSWORD = "12345678"
DB_FILE = "users.db"


# ===== قاعدة البيانات =====
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            emp_no TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            changed INTEGER NOT NULL
        )
    """)
    return conn


# ===== قراءة الإكسل =====
def load_excel():
    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.columns.astype(str).str.strip()
    return df


# ===== تسجيل الدخول =====
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emp_no = request.form.get("emp_no", "").strip()
        password = request.form.get("password", "")

        df = load_excel()

        if emp_no not in df["الرقم الوظيفي"].astype(str).values:
            flash("لم ترد الأضبارة")
            return redirect("/")

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT password, changed FROM users WHERE emp_no=?", (emp_no,))
        user = cur.fetchone()

        # أول دخول
        if user is None:
            if password != DEFAULT_PASSWORD:
                flash("كلمة المرور غير صحيحة")
                return redirect("/")

            cur.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (emp_no, generate_password_hash(DEFAULT_PASSWORD), 0)
            )
            db.commit()
            session["emp_no"] = emp_no
            return redirect("/change-password")

        # دخول طبيعي
        if not check_password_hash(user[0], password):
            flash("كلمة المرور غير صحيحة")
            return redirect("/")

        session["emp_no"] = emp_no
        if user[1] == 0:
            return redirect("/change-password")

        return redirect("/dashboard")

    return render_template("login.html")


# ===== تغيير كلمة المرور =====
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "emp_no" not in session:
        return redirect("/")

    if request.method == "POST":
        new_pass = request.form.get("new_password", "")

        if len(new_pass) < 6:
            flash("كلمة المرور يجب أن تكون 6 أحرف على الأقل")
            return redirect("/change-password")

        db = get_db()
        db.execute(
            "UPDATE users SET password=?, changed=1 WHERE emp_no=?",
            (generate_password_hash(new_pass), session["emp_no"])
        )
        db.commit()
        return redirect("/dashboard")

    return render_template("change_password.html")


# ===== لوحة الموظف =====
@app.route("/dashboard")
def dashboard():
    if "emp_no" not in session:
        return redirect("/")

    df = load_excel()
    row = df[df["الرقم الوظيفي"].astype(str) == session["emp_no"]]

    if row.empty:
        return "لم ترد الأضبارة"

    return render_template("dashboard.html", row=row.iloc[0])


# ===== خروج =====
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
